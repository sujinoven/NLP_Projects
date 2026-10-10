import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any

SECTION_MAP = {
    "required_skills":  ["skills", "experience", "projects"],
    "experience":       ["experience", "summary"],
    "responsibilities": ["experience", "projects"],
    "preferred_skills": ["skills", "projects", "experience"],
}

TOP_EVIDENCE = 3

def compare_section(
    jd_vecs_sec: np.ndarray,
    jd_chunks_sec: List[str],
    res_vecs: Dict[str, np.ndarray],
    res_chunks: Dict[str, List[str]],
    targets: List[str]
) -> Tuple[Optional[float], List[Dict[str, Any]]]:
    """
    Max-pool each JD chunk against target resume section chunks, then average (mean-of-max).
    Returns (section_score, evidence_list)
    """
    # If resume used fallback -> only full_text block exists
    if "full_text" in res_vecs:
        targets = ["full_text"]

    mats, texts, srcs = [], [], []

    for t in targets:
        if t in res_vecs and len(res_vecs[t]) > 0:
            mats.append(res_vecs[t])
            texts.extend(res_chunks[t])
            srcs.extend([t] * len(res_chunks[t]))

    if not mats or len(jd_vecs_sec) == 0:
        return None, []

    R = np.vstack(mats)
    sim = jd_vecs_sec @ R.T  # (n_jd_chunks, n_resume_chunks)

    best_idx = sim.argmax(axis=1)
    best_val = sim.max(axis=1)

    score = float(best_val.mean())

    evidence = []
    for i in range(len(best_val)):
        j = int(best_idx[i])
        evidence.append({
            "jd_chunk":       jd_chunks_sec[i],
            "resume_chunk":   texts[j],
            "resume_section": srcs[j],
            "sim":            round(float(best_val[i]), 4),
        })

    evidence.sort(key=lambda e: e["sim"], reverse=True)
    return score, evidence[:TOP_EVIDENCE]

def calculate_raw_score(scores: Dict[str, Optional[float]]) -> Optional[float]:
    """
    Calculate equal-weight average of available non-missing section scores.
    """
    valid_scores = [s for s in scores.values() if s is not None and not np.isnan(s)]
    return sum(valid_scores) / len(valid_scores) if valid_scores else None

def compute_relative_scores(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Computes min-max relative fit_score across the pool of candidate resumes.
    Resumes with no raw_score are marked as unscored.
    """
    scored_candidates = [c for c in candidates if c.get("raw_score") is not None]
    unscored_candidates = [c for c in candidates if c.get("raw_score") is None]

    if not scored_candidates:
        for c in unscored_candidates:
            c["fit_score"] = None
            c["unscored"] = True
            c["unscored_reason"] = "No valid section similarity scores could be calculated."
        return candidates

    raw_scores = [c["raw_score"] for c in scored_candidates]
    min_score, max_score = min(raw_scores), max(raw_scores)

    for c in scored_candidates:
        c["unscored"] = False
        c["unscored_reason"] = None
        if max_score - min_score < 1e-6:
            c["fit_score"] = 50.0
        else:
            c["fit_score"] = round(((c["raw_score"] - min_score) / (max_score - min_score)) * 100, 1)

    for c in unscored_candidates:
        c["fit_score"] = None
        c["unscored"] = True
        c["unscored_reason"] = "No valid section similarity scores could be calculated."

    return candidates
