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

PROJECT_KEYWORDS = [
    "project", "hotel", "residence", "residential", "tower", "building",
    "villa", "hospital", "mall", "airport", "stadium", "bridge", "highway",
    "commercial", "infrastructure", "development", "construction",
    "g+", "b+", "storey", "story", "sqm", "sq.m", "phase"
]

SITE_LOCATION_KEYWORDS = [
    "riyadh", "dubai", "abu dhabi", "doha", "jeddah", "mecca", "medina",
    "sharjah", "muscat", "manama", "kuwait", "gcc", "saudi", "uae", "qatar",
    "oman", "bahrain", "ksa", "usa", "uk", "india", "location", "site"
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

            "projects": self._extract_projects(lines),
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
            "description": []
        }

        header = block[0]

        # Case 1: Mixed format: "Job Title | Company"
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

        # Description only (projects are now extracted separately)
        for line in block:
            if re.search(DATE_PATTERN, line):
                continue
            if line in (job["job_title"], job["company"]):
                continue

            if len(line.split()) >= 6:
                job["description"].append(line)

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
    # PROJECTS (STRUCTURED EXTRACTION)
    # ------------------------------------------------
    def _extract_projects(self, lines):
        """
        Extract structured project information:
        - Project name
        - Site name (location)
        - Role (position in the project)
        - Responsibilities
        - Project duration (start and end dates)
        """
        projects = []
        project_blocks = []
        current_block = []
        in_project_section = False

        # Find project section and group related lines
        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Detect project section headers
            if re.match(r"^\s*(project[s]?|key project[s]?|major project[s]?)\s*[:;]?\s*$", line_lower):
                in_project_section = True
                if current_block:
                    project_blocks.append(current_block)
                    current_block = []
                continue

            # Detect end of project section
            if in_project_section and re.match(r"^\s*(certification[s]?|education|skill[s]?|training|software|technical skills?)\s*[:;]?\s*$", line_lower):
                in_project_section = False
                if current_block:
                    project_blocks.append(current_block)
                    current_block = []
                continue

            # Detect individual project start - be more strict
            starts_with_number = re.match(r"^\s*\d+[\.)]\s+", line)  # "1. Project name" or "1) Project name"

            # Project name pattern: "NAME — Type, Location" or "NAME | Location"
            looks_like_project_header = bool(re.search(r"[A-Z][A-Z\s&]+\s*[—\-|]\s*", line))

            # Has strong project indicators (building type + location)
            has_building_type = any(k in line_lower for k in ["hotel", "tower", "building", "residence", "mall", "airport", "hospital", "villa", "stadium", "bridge"])
            has_location = any(k in line_lower for k in ["riyadh", "dubai", "abu dhabi", "doha", "jeddah", "usa", "uae", "gcc", "ksa"])
            is_strong_project = has_building_type and (has_location or looks_like_project_header)

            # Check if this is a new project start
            is_project_start = starts_with_number or (in_project_section and is_strong_project)

            if in_project_section:
                if is_project_start and current_block and len(current_block) > 0:
                    # Save previous project block and start new one
                    project_blocks.append(current_block)
                    current_block = [line]
                else:
                    # Continue adding to current project block
                    current_block.append(line)
            elif is_strong_project and not in_project_section:
                # Found a standalone project outside of project section
                if current_block:
                    project_blocks.append(current_block)
                current_block = [line]

        # Don't forget the last block
        if current_block:
            project_blocks.append(current_block)

        # Parse each project block
        for block in project_blocks:
            if not block:
                continue

            project = self._parse_project_block(block)

            # Only add if we extracted meaningful data and it passes validation
            if self._is_valid_project(project):
                projects.append(project)

        return projects

    def _is_valid_project(self, project):
        """
        Validate that a project has meaningful data before including it.
        """
        # Must have a project name
        if not project.get("project_name"):
            return False

        # Project name must be reasonable length (not too short, not too long)
        name = project["project_name"]
        word_count = len(name.split())
        if word_count < 2 or word_count > 25:
            return False

        # Filter out common false positives
        name_lower = name.lower()
        false_positives = [
            "bachelor", "master", "education", "certification", "skill",
            "experience", "work history", "professional", "summary",
            "microsoft", "adobe", "autodesk", "software", "tools",
            "supporting sustainable", "cms college", "graduated"
        ]
        if any(fp in name_lower for fp in false_positives):
            return False

        # Should have at least one of: site_name, role, duration, or responsibilities
        has_meaningful_data = (
            project.get("site_name") or
            project.get("role") or
            project.get("duration_start") or
            len(project.get("responsibilities", [])) > 0
        )

        return has_meaningful_data

    def _parse_project_block(self, block):
        """
        Parse a single project block to extract structured fields.
        """
        project = {
            "project_name": None,
            "site_name": None,
            "role": None,
            "responsibilities": [],
            "duration_start": None,
            "duration_end": None
        }

        # Extract project name (usually first line with specific patterns)
        for line in block[:3]:
            line_lower = line.lower()

            # Remove numbering if present (1. , 1) , etc.)
            cleaned_line = re.sub(r"^\s*\d+[\.)]\s+", "", line).strip()

            # Pattern 1: "PROJECT NAME — Type, Location" (most common)
            name_match = re.search(r"^([A-Z][A-Z\s&\-]+)\s*[—\-|]\s*", cleaned_line)
            if name_match:
                project["project_name"] = name_match.group(1).strip()
                break

            # Pattern 2: "Project: Name" or "Project Name: Description"
            if "project" in line_lower and ":" in line:
                project_match = re.search(r"project\s*:?\s*(.+?)(?:\s*[—\-|]\s*|$)", cleaned_line, re.IGNORECASE)
                if project_match:
                    potential_name = project_match.group(1).strip()
                    if 2 <= len(potential_name.split()) <= 15:
                        project["project_name"] = potential_name
                        break

            # Pattern 3: Line with building type keyword (hotel, tower, etc.)
            building_keywords = ["hotel", "tower", "building", "residence", "mall", "airport", "hospital", "villa", "stadium", "bridge"]
            if any(k in line_lower for k in building_keywords):
                # Check if it looks like a proper title (has capital letters, reasonable length)
                if re.search(r"[A-Z]{2,}", cleaned_line) and 3 <= len(cleaned_line.split()) <= 20:
                    project["project_name"] = cleaned_line
                    break

        # If no project name found yet, use first line if it looks reasonable
        if not project["project_name"] and block:
            cleaned_first = re.sub(r"^\s*\d+[\.)]\s+", "", block[0]).strip()
            # Only use if it's not too long and has some capital letters
            if 3 <= len(cleaned_first.split()) <= 15 and re.search(r"[A-Z]", cleaned_first):
                project["project_name"] = cleaned_first

        # Extract site/location name
        for line in block:
            line_lower = line.lower()

            # Pattern 1: "Location: City" or "Site: City"
            location_match = re.search(r"(?:location|site)\s*:?\s*([^\n]+)", line, re.IGNORECASE)
            if location_match:
                project["site_name"] = location_match.group(1).strip()
                break

            # Pattern 2: Extract location from project header line "NAME — Type, Location"
            if "—" in line or " - " in line:
                # Try to extract location after the last comma or dash
                location_pattern = r",\s*([^,\n]+(?:\([^)]+\))?)\s*$"
                loc_match = re.search(location_pattern, line)
                if loc_match:
                    potential_location = loc_match.group(1).strip()
                    # Check if it contains known location keywords
                    if any(lk in potential_location.lower() for lk in SITE_LOCATION_KEYWORDS):
                        project["site_name"] = potential_location
                        break

            # Pattern 3: Look for known location keywords with better context extraction
            for loc_keyword in SITE_LOCATION_KEYWORDS:
                if loc_keyword in line_lower:
                    # Extract location with surrounding context (including parentheses)
                    # Match patterns like "Dubai, UAE" or "Riyadh (GCC)" or "Abu Dhabi, UAE"
                    loc_pattern = rf"([A-Za-z\s]+(?:,\s*)?{loc_keyword}[^,\n]*(?:\([^)]+\))?)"
                    loc_match = re.search(loc_pattern, line, re.IGNORECASE)
                    if loc_match:
                        project["site_name"] = loc_match.group(1).strip()
                        break

            if project["site_name"]:
                break

        # Extract role in project
        for line in block:
            line_lower = line.lower()

            # Pattern 1: "Role: Position" or "Position: Engineer"
            role_match = re.search(r"(?:role|position)\s*:?\s*([^,|\n]+)", line, re.IGNORECASE)
            if role_match:
                potential_role = role_match.group(1).strip()
                # Validate it looks like a role (not too long)
                if 2 <= len(potential_role.split()) <= 7:
                    project["role"] = potential_role
                    break

            # Pattern 2: Line that's just a role (like "BIM Modeler" or "Lead Engineer")
            if any(r in line_lower for r in ROLE_KEYWORDS):
                if 2 <= len(line.split()) <= 7:  # Reasonable length for a role
                    # Make sure it's not a description line
                    if not re.match(r"^\s*[-•*e]\s", line) and not line_lower.startswith(("developed", "managed", "created", "performed", "produced")):
                        potential_role = line.strip()
                        # Don't include company names or project names as roles
                        if not any(k in line_lower for k in COMPANY_KEYWORDS) and not any(b in line_lower for b in ["hotel", "tower", "building", "mall"]):
                            project["role"] = potential_role
                            break

        # If no explicit role found, try to infer from responsibility text
        if not project.get("role"):
            # Look for phrases like "as BIM Coordinator" or "worked as Engineer"
            for line in block:
                as_match = re.search(r"(?:as|role of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})", line)
                if as_match:
                    potential_role = as_match.group(1).strip()
                    if any(r in potential_role.lower() for r in ROLE_KEYWORDS):
                        project["role"] = potential_role
                        break

        # Extract duration (start and end dates)
        for line in block:
            # Pattern 1: Standard date range (Jan 2020 - Dec 2021)
            date_match = re.search(DATE_PATTERN, line)
            if date_match:
                project["duration_start"] = date_match.group(1)
                project["duration_end"] = date_match.group(3)
                break

            # Pattern 2: Year range (2020-2021 or 2020 - 2021)
            year_range = re.search(r"\b(20\d{2})\s*[-–—]\s*(20\d{2}|present|current)\b", line, re.IGNORECASE)
            if year_range:
                project["duration_start"] = year_range.group(1)
                project["duration_end"] = year_range.group(2)
                break

            # Pattern 3: "Duration: ..." explicit label
            duration_match = re.search(r"duration\s*:?\s*([^\n]+)", line, re.IGNORECASE)
            if duration_match:
                duration_text = duration_match.group(1).strip()
                # Try to parse the duration text
                year_match = re.search(r"(20\d{2})(?:\s*[-–—]\s*(20\d{2}|present|current))?", duration_text, re.IGNORECASE)
                if year_match:
                    project["duration_start"] = year_match.group(1)
                    project["duration_end"] = year_match.group(2) if year_match.group(2) else None
                    break

        # If no duration found, try to find a single year mention (fallback)
        if not project.get("duration_start"):
            for line in block[:5]:  # Check first 5 lines only
                single_year = re.search(r"\b(20\d{2})\b", line)
                if single_year:
                    project["duration_start"] = single_year.group(1)
                    break

        # Extract responsibilities (bullet points or descriptive lines)
        responsibility_keywords = ["responsible", "developed", "managed", "coordinated", "designed",
                                  "created", "implemented", "executed", "delivered", "led", "performed"]

        for line in block:
            line_lower = line.lower()

            # Remove different bullet point types (-, •, *, e, numbers)
            cleaned_line = re.sub(r"^\s*[-•*]\s*", "", line).strip()
            cleaned_line = re.sub(r"^\s*e\s+", "", cleaned_line).strip()  # Remove "e " bullets
            cleaned_line = re.sub(r"^\s*\d+[\.)]\s+", "", cleaned_line).strip()  # Remove numbered bullets

            # Skip the project header line (it shouldn't be in responsibilities)
            if project["project_name"] and project["project_name"] in line:
                continue

            # Skip lines already used for other fields
            if line == project["site_name"] or line == project["role"]:
                continue

            # Skip date lines
            if re.search(DATE_PATTERN, line):
                continue

            # Skip location-only lines
            building_keywords = ["hotel", "tower", "building", "residence", "mall", "airport"]
            if any(bk in line_lower for bk in building_keywords) and len(line.split()) < 8:
                continue

            # Add if it's a responsibility (contains action verbs or is detailed)
            if (any(kw in line_lower for kw in responsibility_keywords) or
                len(cleaned_line.split()) >= 8):  # Detailed description
                project["responsibilities"].append(cleaned_line)

        return project

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
