import os
import shutil
import tempfile
from typing import List, Optional
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, status
from app.config import settings
from app.schemas import (
    HealthStatus,
    ScreeningResponse,
    CandidateResult,
    ContactInfo,
    EvidenceItem,
    FileError
)
from app.services.extraction import extract_text
from app.services.preprocessing import preprocess
from app.services.sections import split_into_sections, split_jd_into_sections
from app.services.embeddings import EmbeddingModelManager, embed_sections, get_device_name
from app.services.scoring import compare_section, calculate_raw_score, compute_relative_scores, SECTION_MAP
from app.services.entities import NERModelManager, extract_contact, run_ner, pick_name

router = APIRouter()

@router.get("/health", response_model=HealthStatus)
def health_check():
    emb_loaded = EmbeddingModelManager.is_loaded()
    ner_loaded = NERModelManager.is_loaded()
    device = get_device_name()

    return HealthStatus(
        status="ok",
        models_loaded=emb_loaded and ner_loaded,
        device=device,
        embedding_model=settings.EMBEDDING_MODEL,
        ner_model=settings.NER_MODEL,
        message="System ready" if (emb_loaded and ner_loaded) else "Models will be initialized on first request"
    )

@router.post("/screen", response_model=ScreeningResponse)
async def screen_resumes(
    jd_text: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
    resumes: List[UploadFile] = File(...),
    top_k: int = Form(5)
):
    # 1. Obtain JD text
    raw_jd_text = ""
    if jd_file and jd_file.filename:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(jd_file.filename)[1]) as tmp_jd:
            shutil.copyfileobj(jd_file.file, tmp_jd)
            tmp_jd_path = tmp_jd.name

        try:
            raw_jd_text, _ = extract_text(tmp_jd_path, filename=jd_file.filename)
        finally:
            if os.path.exists(tmp_jd_path):
                os.remove(tmp_jd_path)
    elif jd_text and jd_text.strip():
        raw_jd_text = jd_text.strip()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a Job Description either as pasted text or by uploading a file (.pdf, .docx, .txt)."
        )

    if not raw_jd_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job Description text could not be extracted or is empty."
        )

    # Preprocess & Split JD
    jd_clean = preprocess(raw_jd_text)
    jd_sections, jd_fallback = split_jd_into_sections(jd_clean)
    jd_chunks, jd_vecs = embed_sections(jd_sections, is_query=True)

    processed_candidates = []
    file_errors = []

    # 2. Process each resume individually
    for upload in resumes:
        if not upload.filename:
            continue

        filename = upload.filename
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_res:
            shutil.copyfileobj(upload.file, tmp_res)
            tmp_res_path = tmp_res.name

        try:
            raw_text, ocr_warning = extract_text(tmp_res_path, filename=filename)

            if not raw_text.strip():
                file_errors.append(FileError(
                    file_name=filename,
                    error="Empty text extracted. If this is a scanned PDF, OCR may be required."
                ))
                continue

            clean_text = preprocess(raw_text)
            res_sections, res_fallback = split_into_sections(clean_text)
            res_chunks, res_vecs = embed_sections(res_sections, is_query=False)

            # Compare JD sections vs Resume sections
            scores = {}
            evidences = {}

            if jd_fallback:
                # If JD has no section headers, compare full JD text against resume
                for jd_sec, jd_v in jd_vecs.items():
                    s, e = compare_section(jd_v, jd_chunks[jd_sec], res_vecs, res_chunks, ["full_text", "skills", "experience", "projects", "summary"])
                    scores[jd_sec] = s
                    evidences[jd_sec] = [EvidenceItem(**item) for item in e]
            else:
                for jd_sec, targets in SECTION_MAP.items():
                    if jd_sec not in jd_vecs:
                        continue
                    s, e = compare_section(jd_vecs[jd_sec], jd_chunks[jd_sec], res_vecs, res_chunks, targets)
                    scores[jd_sec] = s
                    evidences[jd_sec] = [EvidenceItem(**item) for item in e]

            raw_score = calculate_raw_score(scores)

            # Extract Contact & Entities from original text
            contact_dict = extract_contact(raw_text)
            ner_out = run_ner(raw_text)
            cand_name = pick_name(ner_out, raw_text)

            processed_candidates.append({
                "file_name": filename,
                "candidate_name": cand_name if cand_name else None,
                "raw_score": raw_score,
                "contact": ContactInfo(**contact_dict),
                "sections_found": list(res_sections.keys()),
                "used_fallback": res_fallback,
                "section_scores": scores,
                "evidence": evidences,
                "ner_entities": ner_out,
                "ocr_warning": ocr_warning
            })

        except Exception as exc:
            file_errors.append(FileError(
                file_name=filename,
                error=f"Processing error: {str(exc)}"
            ))
        finally:
            if os.path.exists(tmp_res_path):
                os.remove(tmp_res_path)

    # 3. Compute relative scores & rank
    all_scored = compute_relative_scores(processed_candidates)

    valid_candidates = [c for c in all_scored if c.get("raw_score") is not None]
    unscored_candidates = [c for c in all_scored if c.get("raw_score") is None]

    # Sort valid candidates descending by raw_score
    valid_candidates.sort(key=lambda x: x["raw_score"], reverse=True)

    # Assign ranks
    shortlist_results = []
    for idx, cand in enumerate(valid_candidates):
        cand_dict = cand.copy()
        cand_dict["rank"] = idx + 1
        shortlist_results.append(CandidateResult(**cand_dict))

    unscored_results = []
    for cand in unscored_candidates:
        cand_dict = cand.copy()
        cand_dict["rank"] = 0
        unscored_results.append(CandidateResult(**cand_dict))

    # Slice shortlist by top_k
    top_shortlist = shortlist_results[:top_k]

    return ScreeningResponse(
        total_resumes_processed=len(resumes),
        successful_count=len(shortlist_results),
        failed_count=len(file_errors) + len(unscored_results),
        jd_sections_detected=list(jd_sections.keys()),
        jd_used_fallback=jd_fallback,
        shortlist=top_shortlist,
        unscored_resumes=unscored_results,
        file_errors=file_errors
    )
