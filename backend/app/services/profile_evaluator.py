"""
ProfileEvaluator — Recruitment Intelligence Engine.
Computes derived metrics from extracted CV data.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# GCC countries and city keywords
GCC_KEYWORDS = [
    "uae", "dubai", "abu dhabi", "sharjah", "ajman", "ras al khaimah", "fujairah",
    "saudi", "ksa", "riyadh", "jeddah", "mecca", "medina", "dammam", "neom",
    "qatar", "doha", "lusail",
    "oman", "muscat", "salalah",
    "bahrain", "manama",
    "kuwait", "kuwait city",
    "gcc",
]

# Known MNC companies in engineering/construction
MNC_COMPANIES = [
    "aecom", "wsp", "jacobs", "atkins", "snc lavalin", "snc-lavalin",
    "bechtel", "fluor", "kbr", "worley", "parsons", "arcadis", "stantec",
    "arup", "mott macdonald", "hdr", "turner", "skanska", "vinci",
    "bouygues", "samsung engineering", "hyundai engineering", "daelim",
    "larsen & toubro", "l&t", "tata", "shapoorji pallonji",
    "dar al handasah", "khatib & alami", "consolidated contractors",
    "arabtec", "al habtoor", "emaar", "nakheel", "aldar",
    "saudi binladin", "al rajhi", "al bawani",
]

# Known software/tools in engineering
KNOWN_SOFTWARE = [
    "revit", "autocad", "navisworks", "tekla", "etabs", "sap2000", "staad",
    "primavera", "ms project", "procore", "bluebeam", "sketchup",
    "civil 3d", "infraworks", "robot structural", "safe", "dynamo",
    "bim 360", "acc", "solibri", "bentley", "microstation",
    "archicad", "rhino", "grasshopper", "enscape", "lumion",
    "matlab", "python", "excel", "powerbi", "power bi",
]


class ProfileEvaluator:

    def evaluate(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all evaluations and return computed metrics."""
        experience = extracted_data.get("experience") or []
        projects = extracted_data.get("projects") or []
        skills = extracted_data.get("skills") or []
        tools = extracted_data.get("tools") or []
        summary = extracted_data.get("summary") or ""

        all_skills = list(set(s.lower() for s in skills + tools))

        total_years = self.calculate_total_experience(experience)
        gcc_years = self.calculate_gcc_experience(experience, projects)
        seniority = self.determine_seniority(total_years)
        mnc = self.detect_mnc_experience(experience)
        software_exp = self.calculate_software_experience(all_skills, experience)

        return {
            "total_experience_years": total_years,
            "gcc_experience_years": gcc_years,
            "seniority_level": seniority,
            "mnc_experience": mnc,
            "software_experience": software_exp,
        }

    # ------------------------------------------------------------------
    # 1) TOTAL EXPERIENCE
    # ------------------------------------------------------------------
    def calculate_total_experience(self, experience_list: List[Dict]) -> float:
        """Sum durations from start_date to end_date. Returns years rounded to 1 decimal."""
        total_months = 0

        for exp in experience_list:
            start = self._parse_date(exp.get("start_date"))
            end = self._parse_date(exp.get("end_date"))

            if start is None:
                continue
            if end is None:
                end = datetime.now()

            diff_months = (end.year - start.year) * 12 + (end.month - start.month)
            if diff_months > 0:
                total_months += diff_months

        return round(total_months / 12, 1)

    # ------------------------------------------------------------------
    # 2) GCC EXPERIENCE
    # ------------------------------------------------------------------
    def calculate_gcc_experience(
        self, experience_list: List[Dict], projects_list: List[Dict]
    ) -> float:
        """Count years worked in GCC region based on company/description/project locations."""
        gcc_months = 0

        for exp in experience_list:
            if self._has_gcc_reference(exp):
                start = self._parse_date(exp.get("start_date"))
                end = self._parse_date(exp.get("end_date"))
                if start is None:
                    continue
                if end is None:
                    end = datetime.now()
                diff = (end.year - start.year) * 12 + (end.month - start.month)
                if diff > 0:
                    gcc_months += diff

        # Also check projects for GCC references (add 6 months per GCC project if no dates)
        for proj in projects_list:
            text = " ".join([
                proj.get("site_name") or "",
                proj.get("project_name") or "",
                " ".join(proj.get("responsibilities") or []),
            ]).lower()
            if any(k in text for k in GCC_KEYWORDS):
                start = self._parse_date(proj.get("duration_start"))
                end = self._parse_date(proj.get("duration_end"))
                if start and end:
                    diff = (end.year - start.year) * 12 + (end.month - start.month)
                    if diff > 0:
                        gcc_months += diff

        return round(gcc_months / 12, 1)

    # ------------------------------------------------------------------
    # 3) SENIORITY LEVEL
    # ------------------------------------------------------------------
    def determine_seniority(self, total_years: float) -> str:
        if total_years < 2:
            return "Junior"
        elif total_years < 5:
            return "Mid-Level"
        elif total_years < 8:
            return "Senior"
        elif total_years < 12:
            return "Lead"
        else:
            return "Manager"

    # ------------------------------------------------------------------
    # 4) SOFTWARE EXPERIENCE
    # ------------------------------------------------------------------
    def calculate_software_experience(
        self, skills: List[str], experience_list: List[Dict]
    ) -> Dict[str, Dict[str, Any]]:
        """
        List software found in the candidate's skills.
        Years/proficiency only if explicitly stated in CV — otherwise 'Not Specified'.
        """
        software_found: Dict[str, Dict[str, Any]] = {}

        for sw in KNOWN_SOFTWARE:
            sw_lower = sw.lower()
            if not any(sw_lower in s for s in skills):
                continue

            software_found[sw] = {
                "years": "Not Specified",
                "proficiency": "Not Specified",
            }

        return software_found

    # ------------------------------------------------------------------
    # 5) MNC EXPERIENCE
    # ------------------------------------------------------------------
    def detect_mnc_experience(self, experience_list: List[Dict]) -> bool:
        for exp in experience_list:
            company = (exp.get("company") or "").lower()
            if any(mnc in company for mnc in MNC_COMPANIES):
                return True
        return False

    # ------------------------------------------------------------------
    # 6) PORTFOLIO RELEVANCY SCORE
    # ------------------------------------------------------------------
    def calculate_portfolio_score(
        self,
        experience: List[Dict],
        projects: List[Dict],
        skills: List[str],
        gcc_years: float,
        seniority: str,
    ) -> int:
        score = 0

        # Relevant domain match (+30)
        domain_keywords = [
            "civil", "structural", "architecture", "bim", "mep",
            "construction", "infrastructure", "engineering",
        ]
        all_text = " ".join(
            (exp.get("job_title") or "") + " " + " ".join(exp.get("description") or [])
            for exp in experience
        ).lower()
        if any(k in all_text for k in domain_keywords):
            score += 30

        # Relevant software match (+30)
        relevant_software = ["revit", "autocad", "navisworks", "tekla", "etabs", "primavera"]
        if any(sw in skills for sw in relevant_software):
            score += 30

        # GCC experience (+20)
        if gcc_years > 0:
            score += 20

        # Seniority level appropriate (+20)
        if seniority in ("Senior", "Lead", "Manager"):
            score += 20

        return min(score, 100)

    # ------------------------------------------------------------------
    # 7) ENGLISH PROFICIENCY
    # ------------------------------------------------------------------
    def detect_english_proficiency(self, summary: Optional[str]) -> str:
        if not summary or len(summary.strip()) < 20:
            return "Intermediate"

        words = summary.split()
        avg_word_len = sum(len(w) for w in words) / max(len(words), 1)

        # Well-structured: has enough words, decent avg word length, has punctuation
        has_punctuation = bool(re.search(r"[.,;:]", summary))
        long_enough = len(words) >= 15

        if long_enough and avg_word_len >= 4 and has_punctuation:
            return "Advanced"
        return "Intermediate"

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string into datetime. Handles YYYY-MM, YYYY, Month YYYY, Present."""
        if not date_str:
            return None

        date_str = date_str.strip()

        if date_str.lower() in ("present", "current", "now"):
            return datetime.now()

        # YYYY-MM
        match = re.match(r"^(\d{4})-(\d{1,2})$", date_str)
        if match:
            return datetime(int(match.group(1)), int(match.group(2)), 1)

        # Month YYYY (e.g., "January 2020", "Jan 2020")
        match = re.match(
            r"^(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
            r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|"
            r"Dec(?:ember)?)\s+(\d{4})$",
            date_str,
            re.IGNORECASE,
        )
        if match:
            month_map = {
                "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
            }
            month_str = match.group(1)[:3].lower()
            return datetime(int(match.group(2)), month_map.get(month_str, 1), 1)

        # Just YYYY
        match = re.match(r"^(\d{4})$", date_str)
        if match:
            return datetime(int(match.group(1)), 1, 1)

        return None

    def _has_gcc_reference(self, exp: Dict) -> bool:
        """Check if experience entry references GCC region."""
        text = " ".join([
            exp.get("company") or "",
            exp.get("job_title") or "",
            " ".join(exp.get("description") or []),
        ]).lower()
        return any(k in text for k in GCC_KEYWORDS)

    def _get_proficiency(self, years: float) -> str:
        """Kept for backward compatibility."""
        if years < 1:
            return "Basic"
        elif years < 3:
            return "Intermediate"
        else:
            return "Expert"
