import os

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from docx import Document
except ImportError:
    Document = None

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract raw text from PDF file using PyMuPDF."""
    if fitz is None:
        raise ImportError("PyMuPDF (fitz) is not installed. Run 'pip install PyMuPDF'")
    doc = fitz.open(pdf_path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages)

def extract_text_from_docx(docx_path: str) -> str:
    """Extract raw text from DOCX paragraphs and tables."""
    if Document is None:
        raise ImportError("python-docx is not installed. Run 'pip install python-docx'")
    document = Document(docx_path)
    parts = []
    for para in document.paragraphs:
        if para.text:
            parts.append(para.text)
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text:
                    parts.append(cell.text)
    return "\n".join(parts)

def extract_text_from_txt(txt_path: str) -> str:
    """Extract text from TXT file with utf-8 fallback."""
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def extract_text(file_path: str, filename: str = "") -> tuple[str, bool]:
    """
    Extract text based on file extension.
    Returns (extracted_text, is_scanned_pdf_warning)
    """
    ext = os.path.splitext(file_path)[1].lower() if not filename else os.path.splitext(filename)[1].lower()
    text = ""
    
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        text = extract_text_from_docx(file_path)
    elif ext in [".txt", ".md"]:
        text = extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: '{ext}'. Supported formats: .pdf, .docx, .txt")

    # Detect empty/scanned document
    words = len(text.strip().split())
    ocr_warning = False
    if words < 10 and ext == ".pdf":
        ocr_warning = True
        
    return text, ocr_warning
