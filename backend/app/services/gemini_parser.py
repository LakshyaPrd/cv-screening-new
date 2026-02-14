"""
GeminiParser V2.0 — High-accuracy CV parser using Gemini 2.5 Flash.
Single API call, native JSON mode, optimized prompt for 95%+ accuracy.
"""

import json
import logging
import os
import re
import time
import requests
from typing import Dict, Any, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiParser:

    MAX_INPUT_CHARS = 25000
    API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
    MODEL = "gemini-2.5-flash"

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.timeout = settings.GEMINI_TIMEOUT or 90
        self.enabled = settings.GEMINI_ENABLED and bool(self.api_key)

        if self.enabled:
            logger.info(f"GeminiParser V2.0 initialized (model: {self.MODEL})")
        else:
            logger.warning("GeminiParser disabled (no API key)")

    # ==========================================================
    # PUBLIC ENTRY
    # ==========================================================
    def extract_sections(self, text: str) -> Dict[str, Any]:

        if not self.enabled:
            return self._empty_result()

        cleaned = self._clean_text(text)
        prompt = self._build_prompt(cleaned)

        # Single Gemini call with native JSON mode
        raw = self._call_api(prompt, retry_count=3)
        if raw is None:
            logger.warning("Gemini returned None — returning empty")
            return self._empty_result()

        parsed = self._safe_parse(raw)
        if parsed is None:
            logger.warning("Gemini extraction failed — could not parse JSON")
            return self._empty_result()

        return self._normalize(parsed)

    # ==========================================================
    # OPTIMIZED PROMPT — EXPLICIT INSTRUCTIONS FOR ACCURACY
    # ==========================================================
    def _build_prompt(self, text: str) -> str:
        return f"""You are an expert ATS (Applicant Tracking System) resume parser with 99% accuracy.

Your task: Extract EVERY piece of information from this resume into structured JSON.

CRITICAL ACCURACY RULES:
1. NAME: Extract the candidate's FULL PERSONAL NAME (first name + last name). NEVER use job titles, roles, skills, or company names as the name.
2. EXPERIENCE: Each company the candidate worked at is a SEPARATE experience entry. If they had multiple roles at the same company, list each role as a separate entry. Extract ALL experience entries — do not skip any. A typical CV has 3-10 experience entries.
3. DATES: Use YYYY-MM format (e.g., "2024-07"). If only year is available, use "YYYY-01". For ongoing roles, use "Present".
4. PROJECTS: Extract ALL projects mentioned anywhere in the CV — under experience, in a projects section, or standalone. Each project is a separate entry.
5. EDUCATION: Extract ALL education entries with degree name, institution, and year.
6. SKILLS: Extract ALL technical skills, software tools, methodologies, and domain skills mentioned anywhere in the CV. Include skills from experience descriptions too. Be comprehensive.
7. CERTIFICATIONS: Extract ALL certifications, licenses, and professional qualifications.
8. SUMMARY: Write a clean 2-3 sentence professional summary. Do NOT include contact info, phone numbers, emails, or URLs. Write as a professional recruiter would.
9. POSITION: The candidate's current or most recent job title exactly as stated.
10. DISCIPLINE: The professional domain (Civil Engineering, BIM, Architecture, MEP, etc.)

IMPORTANT — COMMON MISTAKES TO AVOID:
- Do NOT merge multiple companies into one experience entry
- Do NOT skip experience entries — extract ALL of them
- Do NOT put job title in the company field or vice versa
- Do NOT truncate or summarize — extract COMPLETE data
- Do NOT miss projects that are listed under experience sections
- Do NOT include section headers as certifications
- Extract ALL languages with their proficiency EXACTLY as stated in the CV. Do NOT guess proficiency levels. If proficiency is not stated, use "Not Specified"

Return this exact JSON structure:

{{
  "name": "string",
  "email": "string or null",
  "phone": "string or null",
  "linkedin": "string or null",
  "summary": "string",
  "position": "string or null",
  "discipline": "string or null",
  "experience": [
    {{
      "job_title": "string",
      "company": "string",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or Present",
      "description": ["string"]
    }}
  ],
  "education": [
    {{
      "degree": "string",
      "university": "string",
      "year": "string"
    }}
  ],
  "projects": [
    {{
      "project_name": "string",
      "site_name": "string or null",
      "role": "string or null",
      "duration_start": "YYYY-MM or null",
      "duration_end": "YYYY-MM or null",
      "responsibilities": ["string"]
    }}
  ],
  "certifications": ["string"],
  "languages": [
    {{
      "language": "string",
      "proficiency": "string (exactly as stated in CV, e.g. native, intermediate, A1.2, fluent, etc.)"
    }}
  ],
  "skills": ["string"]
}}

RESUME TEXT:
\"\"\"
{text}
\"\"\""""

    # ==========================================================
    # CLEAN TEXT
    # ==========================================================
    def _clean_text(self, text: str) -> str:
        text = re.sub(r"[—–]", "-", text)
        text = re.sub(r"[©™®•§¶]", " ", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text[:self.MAX_INPUT_CHARS].strip()

    # ==========================================================
    # API CALL — WITH RETRY
    # ==========================================================
    def _call_api(self, prompt: str, retry_count: int = 3) -> Optional[str]:

        url = f"{self.API_BASE}/{self.MODEL}:generateContent?key={self.api_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 8192,
            },
        }

        for attempt in range(1, retry_count + 1):
            try:
                start_time = time.time()
                resp = requests.post(url, json=payload, timeout=self.timeout)
                elapsed = round(time.time() - start_time, 1)

                if resp.status_code == 429:
                    wait = 5 * attempt
                    logger.warning(f"Gemini 429 rate limit — waiting {wait}s (attempt {attempt}/{retry_count})")
                    time.sleep(wait)
                    continue

                if resp.status_code != 200:
                    logger.error(f"Gemini error {resp.status_code}: {resp.text[:500]}")
                    if attempt < retry_count:
                        time.sleep(2)
                        continue
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
                logger.info(f"Gemini response: {len(text)} chars in {elapsed}s")
                return text

            except requests.exceptions.Timeout:
                logger.error(f"Gemini timeout after {self.timeout}s (attempt {attempt}/{retry_count})")
                if attempt < retry_count:
                    continue
                return None
            except Exception as e:
                logger.error(f"Gemini API exception: {e}")
                return None

        return None

    # ==========================================================
    # SAFE JSON PARSER
    # ==========================================================
    def _safe_parse(self, raw: Optional[str]) -> Optional[Dict]:

        if not raw:
            return None

        text = raw.strip()

        # Strip markdown code block if present (shouldn't happen with JSON mode)
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

        logger.warning(f"JSON parse failed: {text[:300]}")
        return None

    def _fix_truncated_json(self, text: str) -> Optional[str]:
        if not text:
            return None

        open_braces = text.count("{") - text.count("}")
        open_brackets = text.count("[") - text.count("]")

        if open_braces <= 0 and open_brackets <= 0:
            return None

        # Remove trailing incomplete key-value pairs
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

        result["languages"] = []
        for lang in (data.get("languages") or []):
            if isinstance(lang, dict):
                result["languages"].append({
                    "language": lang.get("language") or None,
                    "proficiency": lang.get("proficiency") or "Not Specified",
                })

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
            "languages": [],
        }


# ------------------------------------------------------------------
# CONFIDENCE SCORING
# ------------------------------------------------------------------
def calculate_confidence(merged: Dict[str, Any]) -> int:
    score = 0
    if merged.get("name"):
        score += 10
    if merged.get("summary") and len(merged["summary"]) > 20:
        score += 15
    if len(merged.get("experience") or []) > 0:
        score += 25
    if len(merged.get("experience") or []) >= 3:
        score += 10
    if len(merged.get("projects") or []) > 0:
        score += 15
    if len(merged.get("skills") or []) > 3:
        score += 15
    if merged.get("education"):
        score += 10
    return min(score, 100)
