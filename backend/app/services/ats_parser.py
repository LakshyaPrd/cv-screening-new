"""
ATS PARSER V4.2 — GCC Civil/BIM Precision Engine (NON-AI FIXED)
Fully corrected:
✔ Summary extraction
✔ Experience parsing (job title + company + dates)
✔ Mixed-format roles (“Role | Company”)
✔ Project extraction
✔ Position detection
✔ Clean output
"""

import re
import phonenumbers
from dateutil import parser as date_parser
from typing import Dict, List, Any, Optional

from app.services.dictionaries import get_skills_dict, get_tools_dict


MONTHS = (
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "sept", "oct", "nov", "dec"
)

DATE_PATTERN = (
    r"((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{4}"
    r"|\d{4})\s*[-–—to]+\s*(Present|Current|Now|present|current|now|"
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{4}|"
    r"\d{4})"
)

ROLE_KEYWORDS = [
    "engineer", "manager", "modeler", "technician", "designer",
    "supervisor", "coordinator", "specialist", "architect", "draftsman"
]

COMPANY_KEYWORDS = [
    "llc", "ltd", "private", "pvt", "consult", "consultancy", "contracting",
    "engineering", "infrastructure", "services", "global", "solutions"
]

DISCIPLINES = {
    "Civil Engineering": ["civil", "structural", "construction"],
    "BIM": ["bim", "revit", "navisworks"],
    "Architecture": ["architect", "architecture"],
}


class ATSParser:

    def __init__(self, skills_dict=None, tools_dict=None):
        self.skills_dict = [s.lower() for s in (skills_dict or get_skills_dict())]
        self.tools_dict = [t.lower() for t in (tools_dict or get_tools_dict())]

    # ------------------------------------------------
    # ENTRY POINT
    # ------------------------------------------------
    def parse(self, text: str) -> Dict[str, Any]:

        lines = self._clean_lines(text.split("\n"))

        return {
            "name": self._extract_name(lines),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "linkedin": self._extract_linkedin(text),
            "portfolio_urls": self._extract_urls(text),

            "summary": self._extract_summary(lines),
            "experience": self._extract_experience(lines),
            "education": self._extract_education(lines),

            "skills": self._extract_skills(text),
            "tools": self._extract_tools(text),

            "projects": self._extract_global_projects(lines),
            "certifications": self._extract_certifications(lines),

            "discipline": self._detect_discipline(text),
            "position": self._detect_position(lines),
        }

    # ------------------------------------------------
    # CLEANING
    # ------------------------------------------------
    def _clean_lines(self, lines):
        out = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("--- Page") or re.match(r"^Page \d+", line):
                continue
            out.append(line)
        return out

    # ------------------------------------------------
    # NAME
    # ------------------------------------------------
    def _extract_name(self, lines):
        for line in lines[:8]:
            if any(x in line.lower() for x in ["email", "phone", "linkedin"]):
                continue
            if 2 <= len(line.split()) <= 4 and line.split()[0][0].isupper():
                return line
        return None

    # ------------------------------------------------
    # CONTACTS
    # ------------------------------------------------
    def _extract_email(self, text):
        m = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        return m.group(0) if m else None

    def _extract_phone(self, text):
        matches = re.findall(r"[+\(]?\d[\d\-\s\(\)]{7,}\d", text)
        for raw in matches:
            cleaned = re.sub(r"[^\d+]", "", raw)
            if len(cleaned) >= 10:
                return cleaned
        return None

    def _extract_linkedin(self, text):
        m = re.search(r"https?://[^\s]*linkedin[^\s]*", text)
        return m.group(0) if m else None

    def _extract_urls(self, text):
        return re.findall(r"https?://[^\s<>\"']+", text)

    # ------------------------------------------------
    # SUMMARY FIXED
    # ------------------------------------------------
    def _extract_summary(self, lines):
        summary = []
        ignore = ["phone", "email", "linkedin", "dob", "india", "uae"]

        for i, line in enumerate(lines[:15]):
            if any(k in line.lower() for k in ignore):
                continue
            if len(line.split()) >= 8:
                summary.append(line)
            if len(summary) >= 3:
                break

        return " ".join(summary) if summary else None

    # ------------------------------------------------
    # EXPERIENCE FIXED
    # ------------------------------------------------
    def _extract_experience(self, lines):
        blocks = []
        current = []

        for line in lines:
            mixed_format = ("|" in line or " - " in line or " — " in line) and any(
                r in line.lower() for r in ROLE_KEYWORDS
            )

            if bool(re.search(DATE_PATTERN, line)) or mixed_format:
                if current:
                    blocks.append(current)
                current = [line]
            else:
                current.append(line)

        if current:
            blocks.append(current)

        parsed = []
        for b in blocks:
            exp = self._parse_experience_block(b)
            if exp.get("start_date"):
                parsed.append(exp)

        return parsed

    def _parse_experience_block(self, block):
        job = {
            "job_title": None,
            "company": None,
            "start_date": None,
            "end_date": None,
            "description": [],
            "projects": []
        }

        header = block[0]

        # Case 1: Mixed format: “Job Title | Company”
        if "|" in header:
            left, right = header.split("|", 1)
            job["job_title"] = left.strip()
            job["company"] = right.strip()

        # Case 2: Extract job title by keyword
        if not job["job_title"]:
            for line in block[:3]:
                low = line.lower()
                if any(r in low for r in ROLE_KEYWORDS) and len(line.split()) <= 7:
                    job["job_title"] = line.strip()
                    break

        # Case 3: Extract company by keyword
        if not job["company"]:
            for line in block[:3]:
                if any(k in line.lower() for k in COMPANY_KEYWORDS):
                    job["company"] = line.strip()
                    break

        # Extract dates
        for line in block[:3]:
            m = re.search(DATE_PATTERN, line)
            if m:
                job["start_date"] = m.group(1)
                job["end_date"] = m.group(3)

        # Description + Projects
        for line in block:
            if re.search(DATE_PATTERN, line):
                continue
            if line in (job["job_title"], job["company"]):
                continue

            if len(line.split()) >= 6:
                job["description"].append(line)

            # Consider these as projects
            if any(p in line.lower() for p in
                   ["hotel", "residence", "tower", "g+","b+",
                    "project", "usa", "gcc", "riyadh", "abu dhabi"]):
                job["projects"].append(line)

        return job

    # ------------------------------------------------
    # EDUCATION
    # ------------------------------------------------
    def _extract_education(self, lines):
        edu = []
        degree_keys = ["bachelor", "master", "b.e", "civil engineering"]

        for line in lines:
            if any(k in line.lower() for k in degree_keys):
                years = re.findall(r"(19|20)\d{2}", line)
                edu.append({
                    "degree": line.strip(),
                    "university": None,
                    "year": years[0] if years else None
                })
        return edu

    # ------------------------------------------------
    # SKILLS & TOOLS
    # ------------------------------------------------
    def _extract_skills(self, text):
        tl = text.lower()
        return list({s for s in self.skills_dict if re.search(rf"\b{s}\b", tl)})

    def _extract_tools(self, text):
        tl = text.lower()
        return list({t for t in self.tools_dict if re.search(rf"\b{t}\b", tl)})

    # ------------------------------------------------
    # PROJECTS
    # ------------------------------------------------
    def _extract_global_projects(self, lines):
        out = []
        for line in lines:
            if any(p in line.lower() for p in ["hotel", "residence", "tower", "g+", "b+"]):
                out.append(line.strip())
        return out

    # ------------------------------------------------
    # CERTIFICATIONS
    # ------------------------------------------------
    def _extract_certifications(self, lines):
        return [line.strip() for line in lines if "cert" in line.lower()]

    # ------------------------------------------------
    # DISCIPLINE
    # ------------------------------------------------
    def _detect_discipline(self, text):
        tl = text.lower()
        for d, keys in DISCIPLINES.items():
            if any(k in tl for k in keys):
                return d
        return "Civil Engineering"

    # ------------------------------------------------
    # POSITION (CURRENT ROLE)
    # ------------------------------------------------
    def _detect_position(self, lines):
        for line in lines[:20]:
            if any(r in line.lower() for r in ROLE_KEYWORDS):
                if len(line.split()) <= 7:
                    return line.strip()
        return None


# ---------------------------------------------------------
# WRAPPER
# ---------------------------------------------------------
def parse_cv(text: str) -> Dict[str, Any]:
    parser = ATSParser()
    return parser.parse(text)
