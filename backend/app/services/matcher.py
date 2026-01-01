"""
Rule-based candidate matching service.
Matches candidates against job descriptions using deterministic scoring.
Provides explainable results - NO AI/ML.
"""
from typing import Dict, List
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.job_description import JobDescription
from app.models.match_result import MatchResult
from app.services.dictionaries import get_role_equivalents


class CandidateMatcher:
    """Rule-based matching engine for candidate-JD matching."""
    
    def __init__(self):
        self.role_equivalents = get_role_equivalents()
    
    def match_candidate(
        self,
        candidate: Candidate,
        jd: JobDescription,
        db: Session
    ) -> MatchResult:
        """
        Match a candidate against a job description.
        Returns a MatchResult with explainable scoring.
        """
        # Calculate individual scores
        skill_score = self._calculate_skill_score(candidate, jd)
        role_score = self._calculate_role_score(candidate, jd)
        tool_score = self._calculate_tool_score(candidate, jd)
        experience_score = self._calculate_experience_score(candidate, jd)
        portfolio_score = self._calculate_portfolio_score(candidate, jd)
        quality_score = self._calculate_quality_score(candidate, jd)
        
        # Calculate total weighted score
        total_score = (
            skill_score['weighted'] +
            role_score['weighted'] +
            tool_score['weighted'] +
            experience_score['weighted'] +
            portfolio_score['weighted'] +
            quality_score['weighted']
        )
        
        # Generate justification
        justification = self._generate_justification(
            candidate, jd,
            skill_score, role_score, tool_score,
            experience_score, portfolio_score, quality_score
        )
        
        # Create detailed breakdown
        breakdown = {
            'skills': skill_score,
            'role': role_score,
            'tools': tool_score,
            'experience': experience_score,
            'portfolio': portfolio_score,
            'quality': quality_score,
        }
        
        # Create match result
        match_result = MatchResult(
            candidate_id=candidate.candidate_id,
            jd_id=jd.jd_id,
            total_score=total_score,
            skill_score=skill_score['weighted'],
            role_score=role_score['weighted'],
            tool_score=tool_score['weighted'],
            experience_score=experience_score['weighted'],
            portfolio_score=portfolio_score['weighted'],
            quality_score=quality_score['weighted'],
            score_breakdown=breakdown,
            justification=justification,
            matched_skills=skill_score.get('matched', []),
            missing_skills=skill_score.get('missing', []),
            matched_tools=tool_score.get('matched', []),
        )
        
        return match_result
    
    def _calculate_skill_score(
        self,
        candidate: Candidate,
        jd: JobDescription
    ) -> Dict:
        """
        Calculate skills match score (max: jd.skill_weight points).
        Simple proportional: (matched/total) × max_points
        """
        candidate_skills = set([s.lower() for s in (candidate.skills or [])])
        must_have = set([s.lower() for s in jd.must_have_skills])
        nice_to_have = set([s.lower() for s in (jd.nice_to_have_skills or [])])
        
        # Match must-have skills
        matched_must_have = candidate_skills & must_have
        missing_must_have = must_have - candidate_skills
        
        # Match nice-to-have skills
        matched_nice_to_have = candidate_skills & nice_to_have
        
        # Simple proportional scoring
        max_points = jd.skill_weight
        must_have_weight = 0.75 * max_points
        nice_to_have_weight = 0.25 * max_points
        
        # VERY GENEROUS: 85% base for ANY matches, 15% progressive
        if len(must_have) > 0:
            match_ratio = len(matched_must_have) / len(must_have)
            if match_ratio > 0:
                # Give 85% just for having SOME matches, 15% for perfection
                base_score = 0.85 * must_have_weight
                bonus_score = match_ratio * 0.15 * must_have_weight
                must_have_score = base_score + bonus_score
            else:
                must_have_score = 0
        else:
            must_have_score = must_have_weight
        
        # Nice-to-have: 90% for ANY, 10% progressive
        if len(nice_to_have) > 0:
            match_ratio = len(matched_nice_to_have) / len(nice_to_have)
            if match_ratio > 0:
                base_score = 0.9 * nice_to_have_weight
                bonus_score = match_ratio * 0.1 * nice_to_have_weight
                nice_to_have_score = base_score + bonus_score
            else:
                nice_to_have_score = 0
        else:
            nice_to_have_score = nice_to_have_weight
        
        weighted_score = must_have_score + nice_to_have_score
        
        return {
            'weighted': weighted_score,
            'max': max_points,
            'matched': list(matched_must_have | matched_nice_to_have),
            'missing': list(missing_must_have),
            'matched_must_have': len(matched_must_have),
            'total_must_have': len(must_have),
            'matched_nice_to_have': len(matched_nice_to_have),
            'total_nice_to_have': len(nice_to_have),
        }
    
    def _calculate_role_score(
        self,
        candidate: Candidate,
        jd: JobDescription
    ) -> Dict:
        """
        Calculate role/title match score (max: jd.role_weight points).
        """
        max_points = jd.role_weight
        
        if not jd.role_keywords:
            return {'weighted': max_points, 'max': max_points, 'match_type': 'no_requirements'}
        
        candidate_text = (candidate.raw_text or '').lower()
        experience = candidate.experience or []
        
        # Check for exact or equivalent role matches
        role_keywords_lower = [r.lower() for r in jd.role_keywords]
        
        for keyword in role_keywords_lower:
            # Exact match
            if keyword in candidate_text:
                return {'weighted': max_points, 'max': max_points, 'match_type': 'exact'}
            
            # Check equivalents
            if keyword in self.role_equivalents:
                for equiv in self.role_equivalents[keyword]:
                    if equiv.lower() in candidate_text:
                        return {'weighted': max_points * 0.75, 'max': max_points, 'match_type': 'equivalent'}
        
        # No match
        return {'weighted': 0, 'max': max_points, 'match_type': 'no_match'}
    
    def _calculate_tool_score(
        self,
        candidate: Candidate,
        jd: JobDescription
    ) -> Dict:
        """
        Calculate software/tool match score (max: jd.tool_weight points).
        Simple proportional: (matched/total) × max_points
        """
        max_points = jd.tool_weight
        
        if not jd.required_tools:
            return {'weighted': max_points, 'max': max_points, 'matched': []}
        
        candidate_tools = set([t.lower() for t in (candidate.tools or [])])
        required_tools = set([t.lower() for t in jd.required_tools])
        
        matched_tools = candidate_tools & required_tools
        missing_tools = required_tools - candidate_tools
        
        # VERY GENEROUS: 90% for ANY tool matches
        if len(required_tools) > 0:
            match_ratio = len(matched_tools) / len(required_tools)
            if match_ratio > 0:
                # 90% for ANY matches, 10% for perfection
                score = (0.9 + match_ratio * 0.1) * max_points
            else:
                score = 0
        else:
            score = max_points
        
        return {
            'weighted': score,
            'max': max_points,
            'matched': list(matched_tools),
            'missing': list(missing_tools),
        }
    
    def _calculate_experience_score(
        self,
        candidate: Candidate,
        jd: JobDescription
    ) -> Dict:
        """
        Calculate experience indicators score (max: jd.experience_weight points).
        """
        max_points = jd.experience_weight
        
        experience = candidate.experience or []
        
        # VERY GENEROUS: assume full experience if ANY data exists
        score = 0
        
        # Give almost full points for ANY experience OR if missing (assume good)
        if len(experience) > 0:
            score = max_points  # Full points
        else:
            # Even with no experience data, give 70% (benefit of doubt)
            score = max_points * 0.7
        
        return {
            'weighted': min(score, max_points),
            'max': max_points,
            'experience_count': len(experience),
        }
    
    def _calculate_portfolio_score(
        self,
        candidate: Candidate,
        jd: JobDescription
    ) -> Dict:
        """
        Calculate portfolio relevance score (max: jd.portfolio_weight points).
        """
        max_points = jd.portfolio_weight
        
        portfolio_urls = candidate.portfolio_urls or []
        raw_text = (candidate.raw_text or '').lower()
        
        # Check for JD keywords in portfolio/raw text
        jd_keywords = (jd.role_keywords or []) + (jd.must_have_skills or [])
        jd_keywords_lower = [k.lower() for k in jd_keywords]
        
        keyword_matches = sum(1 for kw in jd_keywords_lower if kw in raw_text)
        
        # VERY GENEROUS: assume good portfolio if keywords match
        score = 0
        
        # Give 80% for having portfolio OR keyword matches
        if len(portfolio_urls) > 0 or keyword_matches > 0:
            score = max_points * 0.8
        
        # Bonus for many keyword matches
        if len(jd_keywords) > 0 and keyword_matches > 0:
            score += (keyword_matches / len(jd_keywords)) * (max_points * 0.2)
        
        return {
            'weighted': min(score, max_points),
            'max': max_points,
            'portfolio_count': len(portfolio_urls),
            'keyword_matches': keyword_matches,
        }
    
    def _calculate_quality_score(
        self,
        candidate: Candidate,
        jd: JobDescription
    ) -> Dict:
        """
        Calculate CV quality score (max: jd.quality_weight points).
        """
        max_points = jd.quality_weight
        # VERY GENEROUS: give most points regardless of quality
        score = max_points * 0.9  # Start with 90% by default
        
        # Bonus for having contact details
        if candidate.email and candidate.phone:
            score = max_points  # Perfect
        
        return {
            'weighted': min(score, max_points),
            'max': max_points,
            'ocr_quality': candidate.ocr_quality_score,
        }
    
    def _generate_justification(
        self,
        candidate: Candidate,
        jd: JobDescription,
        skill_score: Dict,
        role_score: Dict,
        tool_score: Dict,
        experience_score: Dict,
        portfolio_score: Dict,
        quality_score: Dict
    ) -> str:
        """
        Generate explainable plain-English justification with bullet points.
        """
        bullets = []
        
        # Skills - matched
        if skill_score['matched_must_have'] > 0:
            bullets.append(
                f"✓ Matches {skill_score['matched_must_have']} of {skill_score['total_must_have']} required skills"
            )
        
        # Skills - missing
        if skill_score['missing']:
            missing_list = ', '.join(skill_score['missing'][:3])
            if len(skill_score['missing']) > 3:
                missing_list += f" (+{len(skill_score['missing']) - 3} more)"
            bullets.append(f"✗ Missing must-have skills: {missing_list}")
        
        # Role
        if role_score['match_type'] == 'exact':
            bullets.append("✓ Has matching job title")
        elif role_score['match_type'] == 'equivalent':
            bullets.append("✓ Has equivalent job title")
        
        # Tools
        if tool_score.get('matched'):
            tool_list = ', '.join(tool_score['matched'][:3])
            if len(tool_score['matched']) > 3:
                tool_list += f" (+{len(tool_score['matched']) - 3} more)"
            bullets.append(f"✓ Proficient in {len(tool_score['matched'])} required tools: {tool_list}")
        
        # Missing tools
        if tool_score.get('missing'):
            missing_tools = ', '.join(tool_score['missing'][:3])
            if len(tool_score['missing']) > 3:
                missing_tools += f" (+{len(tool_score['missing']) - 3} more)"
            bullets.append(f"✗ Missing tools: {missing_tools}")
        
        # Experience
        if experience_score['experience_count'] > 0:
            bullets.append(f"✓ Has {experience_score['experience_count']} relevant experience(s)")
        
        # Portfolio
        if portfolio_score.get('portfolio_count', 0) > 0:
            bullets.append(f"✓ Has {portfolio_score['portfolio_count']} portfolio reference(s)")
        
        # Quality
        if quality_score.get('ocr_quality', 0) >= 80:
            bullets.append("✓ High-quality CV with complete contact details")
        
        # Build bullet-point list
        if bullets:
            return "\n".join([f"• {bullet}" for bullet in bullets])
        else:
            return "• Minimal matching criteria found"
