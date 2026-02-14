"""
ATS PARSER V7.0 — Gemini-First Architecture

Rule-based (regex) handles ONLY contact info (99% reliable):
  - email, phone, linkedin, portfolio_urls

Gemini AI handles EVERYTHING else (95%+ reliable):
  - name, summary, position, discipline
  - experience, education, projects
  - certifications, skills

No complex merge logic. No conflicts. Maximum accuracy.
"""

import logging
import re
from typing import Dict, Any

from app.services.dictionaries import get_skills_dict, get_tools_dict

logger = logging.getLogger(__name__)


class ATSParser:

    def __init__(self, skills_dict=None, tools_dict=None, use_ai=True):
        self.skills_dict = [s.lower() for s in (skills_dict or get_skills_dict())]
        self.tools_dict = [t.lower() for t in (tools_dict or get_tools_dict())]
        self._ai_parser = None
        self._use_ai = use_ai

    @property
    def ai_parser(self):
        """Lazy-load GeminiParser to avoid import issues at module level."""
        if self._ai_parser is None and self._use_ai:
            try:
                from app.services.gemini_parser import GeminiParser
                self._ai_parser = GeminiParser()
            except Exception as e:
                logger.warning(f"Failed to initialize GeminiParser: {e}")
                self._ai_parser = None
        return self._ai_parser

    # ------------------------------------------------
    # ENTRY POINT
    # ------------------------------------------------
    def parse(self, text: str) -> Dict[str, Any]:

        # STEP 1: Regex extraction — contacts only (always reliable)
        contacts = {
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "linkedin": self._extract_linkedin(text),
            "portfolio_urls": self._extract_urls(text),
        }

        # STEP 2: Regex extraction — tools (dictionary match, always reliable)
        tools = self._extract_tools(text)

        # STEP 3: Gemini extraction — everything else
        ai_result = None
        if self._use_ai and self.ai_parser and self.ai_parser.enabled:
            try:
                ai_result = self.ai_parser.extract_sections(text)
                logger.info("Gemini extraction completed successfully")
            except Exception as e:
                logger.error(f"Gemini extraction failed: {e}")

        # STEP 4: Build final result
        if ai_result:
            result = self._build_from_gemini(ai_result, contacts, tools, text)
        else:
            # Fallback: rule-based only (when Gemini is unavailable)
            logger.warning("Using rule-based fallback (Gemini unavailable)")
            result = self._build_fallback(contacts, tools, text)

        # STEP 5: Confidence score
        from app.services.gemini_parser import calculate_confidence
        confidence = calculate_confidence(result)

        result["confidence_score"] = confidence
        result["status"] = "success" if confidence >= 60 else "low_confidence"
        result["ai_enhanced"] = ai_result is not None

        return result

    # ------------------------------------------------
    # BUILD FROM GEMINI (primary path)
    # ------------------------------------------------
    def _build_from_gemini(self, ai: Dict, contacts: Dict, tools: list, text: str) -> Dict[str, Any]:
        """
        Use Gemini output directly for all non-contact fields.
        Contacts come from regex. Tools come from dictionary match.
        Skills = union of Gemini skills + dictionary-matched skills.
        """
        # Union Gemini skills with dictionary-matched skills for completeness
        ai_skills = set(s.lower() for s in (ai.get("skills") or []))
        dict_skills = set(s for s in self.skills_dict if re.search(rf"\b{re.escape(s)}\b", text.lower()))
        combined_skills = list(ai_skills | dict_skills)

        return {
            # Contacts — regex first, Gemini fallback
            "email": contacts["email"] or ai.get("email"),
            "phone": contacts["phone"] or ai.get("phone"),
            "linkedin": contacts["linkedin"] or ai.get("linkedin"),
            "portfolio_urls": contacts["portfolio_urls"],

            # Everything else — from Gemini (95%+ reliable)
            "name": ai.get("name"),
            "summary": ai.get("summary"),
            "position": ai.get("position"),
            "discipline": ai.get("discipline") or self._detect_discipline_fallback(text),
            "experience": ai.get("experience") or [],
            "education": ai.get("education") or [],
            "projects": ai.get("projects") or [],
            "certifications": ai.get("certifications") or [],
            "languages": ai.get("languages") or [],
            "skills": combined_skills,
            "tools": tools,
        }

    # ------------------------------------------------
    # FALLBACK (rule-based only, when Gemini is down)
    # ------------------------------------------------
    def _build_fallback(self, contacts: Dict, tools: list, text: str) -> Dict[str, Any]:
        """Minimal rule-based extraction when Gemini is unavailable."""
        lines = self._clean_lines(text.split("\n"))
        dict_skills = list(set(s for s in self.skills_dict if re.search(rf"\b{re.escape(s)}\b", text.lower())))

        return {
            "email": contacts["email"],
            "phone": contacts["phone"],
            "linkedin": contacts["linkedin"],
            "portfolio_urls": contacts["portfolio_urls"],
            "name": self._extract_name_fallback(lines),
            "summary": None,
            "position": None,
            "discipline": self._detect_discipline_fallback(text),
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "languages": [],
            "skills": dict_skills,
            "tools": tools,
        }

    # ------------------------------------------------
    # REGEX CONTACT EXTRACTORS (always used)
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
        # Try full URL first
        m = re.search(r"https?://[^\s]*linkedin\.com[^\s]*", text)
        if m:
            return m.group(0)
        # Try without protocol (linkedin.com/in/username)
        m = re.search(r"(?:www\.)?linkedin\.com/in/[^\s,;)\"']+", text, re.IGNORECASE)
        if m:
            return "https://" + m.group(0)
        return None

    def _extract_urls(self, text):
        return re.findall(r"https?://[^\s<>\"']+", text)

    # ------------------------------------------------
    # DICTIONARY-BASED TOOL EXTRACTION (always used)
    # ------------------------------------------------
    def _extract_tools(self, text):
        tl = text.lower()
        return list({t for t in self.tools_dict if re.search(rf"\b{re.escape(t)}\b", tl)})

    # ------------------------------------------------
    # MINIMAL FALLBACKS (only when Gemini is down)
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

    def _extract_name_fallback(self, lines):
        """Simple name extraction — only used when Gemini is unavailable."""
        role_keywords = [
            "engineer", "designer", "manager", "modeler", "technician",
            "coordinator", "specialist", "architect", "draftsman", "supervisor",
            "developer", "analyst", "consultant", "civil", "senior", "junior",
            "lead", "bim", "cad", "drafter",
        ]
        for line in lines[:8]:
            low = line.lower()
            if any(x in low for x in ["email", "phone", "linkedin", "skill", "about"]):
                continue
            if any(rk in low for rk in role_keywords):
                continue
            words = line.split()
            if 2 <= len(words) <= 4 and words[0][0].isupper():
                return line
        return None

    def _detect_discipline_fallback(self, text):
        """Simple discipline detection — used as fallback when Gemini doesn't provide one."""
        disciplines = {
            "Civil Engineering": ["civil", "structural", "construction"],
            "BIM": ["bim", "revit", "navisworks"],
            "Architecture": ["architect", "architecture"],
            "Mechanical Engineering": ["mechanical", "hvac", "piping"],
            "Electrical Engineering": ["electrical", "power", "wiring"],
        }
        tl = text.lower()
        for d, keys in disciplines.items():
            if any(k in tl for k in keys):
                return d
        return None


# ---------------------------------------------------------
# WRAPPERS
# ---------------------------------------------------------
def parse_cv(text: str, use_ai: bool = True) -> Dict[str, Any]:
    """Parse CV with Gemini AI (default) or rule-based fallback."""
    parser = ATSParser(use_ai=use_ai)
    return parser.parse(text)


def parse_cv_rule_only(text: str) -> Dict[str, Any]:
    """Parse CV using rule-based extraction only (no AI)."""
    parser = ATSParser(use_ai=False)
    return parser.parse(text)
