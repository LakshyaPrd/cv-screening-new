"""
GeminiParser — Single-call production CV parser using Gemini 2.5 Flash.
One API call extracts all sections for speed.
"""

import json
import logging
import os
import re
import requests
from typing import Dict, Any, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiParser:

    MAX_INPUT_CHARS = 20000
    API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
    MODEL = "gemini-2.5-flash"

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.timeout = settings.GEMINI_TIMEOUT or 60
        self.enabled = settings.GEMINI_ENABLED and bool(self.api_key)

        if self.enabled:
            logger.info(f"GeminiParser initialized (model: {self.MODEL})")
        else:
            logger.warning("GeminiParser disabled (no API key)")

    # ==========================================================
    # PUBLIC ENTRY — SINGLE API CALL
    # ==========================================================
    def extract_sections(self, text: str) -> Dict[str, Any]:

        if not self.enabled:
            return self._empty_result()

        cleaned = self._clean_text(text)
        prompt = self._build_prompt(cleaned)

        # Single Gemini call for everything
        raw = self._call_api(prompt)
        if raw is None:
            logger.warning("Gemini returned None — returning empty")
            return self._empty_result()

        parsed = self._safe_parse(raw, None)
        if parsed is None:
            # Retry with correction prompt
            logger.info("JSON parse failed — retrying with correction prompt")
            correction = f"Fix this JSON and return ONLY valid JSON:\n{raw}"
            raw_retry = self._call_api(correction)
            if raw_retry:
                parsed = self._safe_parse(raw_retry, None)

        if parsed is None:
            logger.warning("Gemini extraction failed after retry")
            return self._empty_result()

        return self._normalize(parsed)

    # ==========================================================
    # SINGLE PROMPT — ALL SECTIONS AT ONCE
    # ==========================================================
    def _build_prompt(self, text: str) -> str:
        return f"""You are a professional ATS resume parser.

Extract ALL information from this resume and return ONLY valid JSON.
Do not include any explanation text before or after the JSON.

Required JSON structure:

{{
  "name": "candidate full name",
  "summary": "2 sentence professional summary",
  "position": "current or most recent job title",
  "discipline": "professional domain (e.g. Civil Engineering, BIM, Architecture, Mechanical Engineering, Electrical Engineering, Software Engineering)",
  "experience": [
    {{
      "job_title": "exact role name",
      "company": "company name only",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or Present",
      "description": ["responsibility 1", "responsibility 2"]
    }}
  ],
  "education": [
    {{
      "degree": "full degree name",
      "university": "institution name",
      "year": "YYYY"
    }}
  ],
  "projects": [
    {{
      "project_name": "exact project name",
      "site_name": "city or country",
      "role": "role in project",
      "duration_start": "YYYY-MM or null",
      "duration_end": "YYYY-MM or null",
      "responsibilities": ["task 1", "task 2"]
    }}
  ],
  "certifications": ["certification 1", "certification 2"],
  "skills": ["skill1", "skill2"]
}}

RULES:
- name must be the candidate's full personal name (first + last). Do NOT use job titles, roles, or skills as the name.
- summary must be a clean 2-sentence professional summary. Do NOT include phone numbers, emails, URLs, icons, symbols, or contact info in the summary. Write it as a recruiter would.
- position is the candidate's current or most recent job title (e.g. "Senior BIM Modeler", "Civil Engineer"). Use null if not found.
- discipline is the professional domain or field. Infer from experience and education if not stated explicitly.
- Extract ALL work experience entries with correct job_title and company.
- If job title and company are on separate lines, associate them correctly.
- Do NOT merge job title into company field.
- Extract ALL projects (construction, engineering, infrastructure, software, academic).
- certifications should list actual certification names (e.g. "Autodesk Certified Professional", "PMP"). Do NOT include section headers.
- If summary is not explicit in the resume, generate a short professional one based on the candidate's experience and skills.
- Skills should include technical skills, software, and domain skills. No duplicates.
- Use null for missing fields.
- Dates should be YYYY-MM format when possible.
- Return ONLY the JSON object, no markdown, no explanation.

Resume:
\"\"\"
{text}
\"\"\""""

    # ==========================================================
    # CLEAN TEXT
    # ==========================================================
    def _clean_text(self, text: str) -> str:
        # Normalize dashes
        text = re.sub(r"[—–]", "-", text)
        # Remove common OCR icon artifacts (©, ™, _, &, etc. used as separators)
        text = re.sub(r"[©™®•§¶]", " ", text)
        # Remove excessive whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text[:self.MAX_INPUT_CHARS].strip()

    # ==========================================================
    # API CALL
    # ==========================================================
    def _call_api(self, prompt: str) -> Optional[str]:

        url = f"{self.API_BASE}/{self.MODEL}:generateContent?key={self.api_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 4096,
            },
        }

        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)

            if resp.status_code != 200:
                logger.error(f"Gemini error {resp.status_code}: {resp.text[:500]}")
                return None

            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                logger.warning("Gemini returned no candidates")
                return None

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                logger.warning("Gemini returned no parts")
                return None

            text = parts[0].get("text", "")
            logger.info(f"Gemini response received ({len(text)} chars)")
            return text

        except requests.exceptions.Timeout:
            logger.error(f"Gemini API timeout after {self.timeout}s")
            return None
        except Exception as e:
            logger.error(f"Gemini API exception: {e}")
            return None

    # ==========================================================
    # SAFE JSON PARSER
    # ==========================================================
    def _safe_parse(self, raw: Optional[str], fallback) -> Optional[Dict]:

        if not raw:
            return fallback

        text = raw.strip()

        # Strip markdown code block (complete or truncated)
        code_block = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if code_block:
            text = code_block.group(1).strip()
        elif text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text).strip()

        # Extract JSON object
        brace = re.search(r"\{[\s\S]*\}", text)
        if brace:
            text = brace.group(0)

        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try fixing truncated JSON
        try:
            fixed = self._fix_truncated_json(text)
            if fixed:
                return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        logger.warning(f"Gemini JSON parse failed: {text[:200]}")
        return fallback

    def _fix_truncated_json(self, text: str) -> Optional[str]:
        if not text:
            return None

        open_braces = text.count("{") - text.count("}")
        open_brackets = text.count("[") - text.count("]")

        if open_braces <= 0 and open_brackets <= 0:
            return None

        text = re.sub(r",\s*$", "", text.rstrip())
        text = re.sub(r',\s*"[^"]*":\s*"?[^"}\]]*$', "", text)
        text += "]" * open_brackets
        text += "}" * open_braces

        return text

    # ==========================================================
    # NORMALIZE OUTPUT
    # ==========================================================
    def _normalize(self, data: Dict) -> Dict:
        result = {
            "name": data.get("name") or None,
            "summary": data.get("summary") or None,
            "position": data.get("position") or None,
            "discipline": data.get("discipline") or None,
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "skills": [],
        }

        for exp in (data.get("experience") or []):
            if isinstance(exp, dict):
                result["experience"].append({
                    "job_title": exp.get("job_title") or None,
                    "company": exp.get("company") or None,
                    "start_date": exp.get("start_date") or None,
                    "end_date": exp.get("end_date") or None,
                    "description": exp.get("description") or [],
                })

        for edu in (data.get("education") or []):
            if isinstance(edu, dict):
                result["education"].append({
                    "degree": edu.get("degree") or None,
                    "university": edu.get("university") or None,
                    "year": edu.get("year") or None,
                })

        for proj in (data.get("projects") or []):
            if isinstance(proj, dict):
                result["projects"].append({
                    "project_name": proj.get("project_name") or None,
                    "site_name": proj.get("site_name") or None,
                    "role": proj.get("role") or None,
                    "responsibilities": proj.get("responsibilities") or [],
                    "duration_start": proj.get("duration_start") or None,
                    "duration_end": proj.get("duration_end") or None,
                })

        raw_certs = data.get("certifications") or []
        if isinstance(raw_certs, list):
            result["certifications"] = [c for c in raw_certs if isinstance(c, str)]

        raw_skills = data.get("skills") or []
        if isinstance(raw_skills, list):
            result["skills"] = [s for s in raw_skills if isinstance(s, str)]

        return result

    # ==========================================================
    # EMPTY RESULT
    # ==========================================================
    def _empty_result(self) -> Dict[str, Any]:
        return {
            "name": None,
            "summary": None,
            "position": None,
            "discipline": None,
            "skills": [],
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
        }


# ------------------------------------------------------------------
# CONFIDENCE SCORING
# ------------------------------------------------------------------
def calculate_confidence(merged: Dict[str, Any]) -> int:
    score = 0
    if merged.get("summary"):
        score += 25
    if len(merged.get("experience") or []) > 0:
        score += 25
    if len(merged.get("projects") or []) > 0:
        score += 20
    if len(merged.get("skills") or []) > 3:
        score += 20
    if merged.get("education"):
        score += 10
    return min(score, 100)
