import re
from typing import Dict, Tuple

# Canonical section -> variants seen in real resumes
SECTION_HEADINGS = {
    "summary":        ["summary", "professional summary", "career summary", "profile",
                       "about me", "objective", "career objective"],
    "skills":         ["skills", "technical skills", "key skills", "core competencies",
                       "technical expertise", "technologies", "tech stack", "skill set"],
    "experience":     ["experience", "work experience", "professional experience",
                       "employment history", "work history", "career history", "employment"],
    "projects":       ["projects", "academic projects", "personal projects",
                       "key projects", "project experience"],
    "education":      ["education", "academic background", "academic qualifications",
                       "educational qualification", "qualifications"],
    "certifications": ["certifications", "certification", "courses", "training",
                       "licenses and certifications"],
    "achievements":   ["achievements", "awards", "accomplishments", "honors",
                       "publications", "extracurricular"],
}

def match_heading(line: str) -> str | None:
    line = line.strip().strip(":").strip("-").strip()

    # headings are short; a long line is body text
    if len(line.split()) > 5 or len(line) < 3:
        return None

    for section, variants in SECTION_HEADINGS.items():
        for v in variants:
            if line == v or line.startswith(v):
                return section

    return None

def split_into_sections(text: str) -> Tuple[Dict[str, str], bool]:
    """
    Splits resume clean text into section blocks.
    Returns (sections_dict, used_fallback)
    """
    sections = {}
    current = "header"  # name / contact sits above the first heading
    buffer = []

    for line in text.split("\n"):
        heading = match_heading(line)
        if heading:
            if buffer:
                sections[current] = sections.get(current, "") + "\n" + "\n".join(buffer)
            current = heading
            buffer = []
        else:
            if line.strip():
                buffer.append(line.strip())

    if buffer:
        sections[current] = sections.get(current, "") + "\n" + "\n".join(buffer)

    sections = {k: v.strip() for k, v in sections.items() if v.strip()}

    # FALLBACK: no real headings found -> treat the whole resume as one block
    real = [k for k in sections if k != "header"]
    if len(real) < 2:
        return {"full_text": text.strip()}, True

    return sections, False


# Canonical JD section -> variants
JD_HEADING_MAP = {
    "role":             ["job title", "title", "role", "position", "designation",
                         "about the role", "role overview", "job summary",
                         "about the job", "overview"],
    "required_skills":  ["required skills", "requirements", "must have", "must haves",
                         "required qualifications", "skills required", "key skills",
                         "technical skills", "what we are looking for", "who you are",
                         "essential skills", "mandatory skills", "technical requirements"],
    "preferred_skills": ["preferred skills", "nice to have", "good to have", "bonus",
                         "preferred qualifications", "desirable", "plus points",
                         "added advantage"],
    "responsibilities": ["responsibilities", "key responsibilities", "what you will do",
                         "what you'll do", "duties", "job description", "your role",
                         "day to day"],
    "experience":       ["experience", "experience required", "work experience",
                         "years of experience", "eligibility"],
    "education":        ["education", "qualification", "qualifications",
                         "educational qualification", "academic requirements"],
    "company":          ["about us", "about the company", "who we are", "company overview"],
    "benefits":         ["benefits", "what we offer", "perks", "compensation", "salary"],
}

DROP_SECTIONS = ["company", "benefits"]

def clean_heading_candidate(line: str) -> str:
    """Strip markdown decoration: ## heading ##, **bold**, trailing colon."""
    s = line.strip()
    s = s.strip("#").strip()
    s = s.replace("*", "").replace("_", "")
    s = s.strip("-").strip("=").strip()
    s = s.strip(":").strip()
    return s.lower().strip()

def lookup_section(candidate: str) -> str | None:
    if len(candidate) < 3 or len(candidate.split()) > 6:
        return None

    for section, variants in JD_HEADING_MAP.items():
        for v in variants:
            if candidate == v or candidate.startswith(v):
                return section

    return None

def match_jd_heading(line: str) -> Tuple[str | None, str]:
    """
    Returns (section, inline_content).
    Handles 'experience: 2+ years' by returning ('experience', '2+ years').
    """
    raw = line.strip()

    if not raw or set(raw) <= set("-=_#* "):
        return None, ""

    head, sep, rest = raw.partition(":")

    if sep:
        section = lookup_section(clean_heading_candidate(head))
        if section:
            return section, rest.strip()

    section = lookup_section(clean_heading_candidate(raw))
    if section:
        return section, ""

    return None, ""

def split_jd_into_sections(text: str) -> Tuple[Dict[str, str], bool]:
    """
    Splits job description clean text into section blocks.
    Returns (sections_dict, used_fallback)
    """
    sections = {}
    current = "role"
    buffer = []

    def flush():
        if buffer:
            sections[current] = (sections.get(current, "") + "\n" + "\n".join(buffer)).strip()

    for line in text.split("\n"):
        section, inline = match_jd_heading(line)
        if section:
            flush()
            current = section
            buffer = [inline] if inline else []
        else:
            if line.strip() and not set(line.strip()) <= set("-=_#* "):
                buffer.append(line.strip())

    flush()

    sections = {k: v.strip() for k, v in sections.items() if v.strip()}

    for noise in DROP_SECTIONS:
        sections.pop(noise, None)

    if len([k for k in sections if k != "role"]) < 1:
        return {"full_text": text.strip()}, True

    return sections, False
