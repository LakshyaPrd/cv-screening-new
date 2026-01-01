"""
Data extraction service for parsing structured information from OCR text.
Uses rule-based patterns (regex) to extract candidate information.
"""
import re
from typing import Dict, List, Any, Optional
import phonenumbers

from app.services.dictionaries import get_skills_dict, get_tools_dict


class DataExtractor:
    """Extract structured data from raw OCR text using rule-based patterns."""
    
    def __init__(self):
        self.skills_dict = [s.lower() for s in get_skills_dict()]
        self.tools_dict = [t.lower() for t in get_tools_dict()]
    
    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract all candidate information from OCR text.
        
        Returns:
            Dictionary with extracted fields
        """
        return {
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'location': self._extract_location(text),
            'skills': self._extract_skills(text),
            'tools': self._extract_tools(text),
            'education': self._extract_education(text),
            'experience': self._extract_experience(text),
            'portfolio_urls': self._extract_urls(text),
        }
    
    def _extract_name(self, text: str) -> Optional[str]:
        """
        Extract candidate name.
        Enhanced to handle various text formats (UPPERCASE, lowercase, TitleCase).
        """
        lines = text.split('\n')
        for line in lines[:15]:  # Check first 15 lines
            line = line.strip()
            if len(line) > 0 and len(line) < 60:
                # Remove common noise words
                if any(keyword in line.lower() for keyword in ['resume', 'curriculum', 'vitae', 'cv', 'profile']):
                    continue
                
                # Check if it looks like a name (2-5 words, mostly alphabetic)
                words = line.split()
                if 2 <= len(words) <= 5:
                    # Check if words are mostly alphabetic (allowing for periods, hyphens)
                    alpha_words = [w for w in words if re.match(r'^[A-Za-z][A-Za-z.\-]*$', w)]
                    if len(alpha_words) >= 2:
                        # Convert to title case for consistency
                        name = ' '.join(alpha_words)
                        return name.title()
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address using regex."""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(pattern, text)
        return matches[0] if matches else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract and normalize phone number."""
        # Try to find phone numbers
        potential_phones = re.findall(
            r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            text
        )
        
        if potential_phones:
            phone = ''.join(potential_phones[0].split())
            # Try to parse and normalize
            try:
                parsed = phonenumbers.parse(phone, "US")
                if phonenumbers.is_valid_number(parsed):
                    return phonenumbers.format_number(
                        parsed,
                        phonenumbers.PhoneNumberFormat.E164
                    )
            except:
                return phone
        
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """
        Extract location/address.
        Look for patterns like "City, State" or "City, Country".
        """
        # Simple pattern for City, State/Country
        pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)\b'
        matches = re.findall(pattern, text)
        
        if matches:
            city, state = matches[0]
            return f"{city}, {state}"
        
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """
        Extract skills by matching against skills dictionary.
        """
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills_dict:
            # Use word boundary matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def _extract_tools(self, text: str) -> List[str]:
        """
        Extract software/tools by matching against tools dictionary.
        """
        text_lower = text.lower()
        found_tools = []
        
        for tool in self.tools_dict:
            pattern = r'\b' + re.escape(tool) + r'\b'
            if re.search(pattern, text_lower):
                found_tools.append(tool)
        
        return list(set(found_tools))
    
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract education information.
        Look for degree keywords and years.
        """
        education = []
        
        # Keywords
        degree_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'diploma',
            'b.sc', 'm.sc', 'b.tech', 'm.tech', 'mba', 'bba'
        ]
        
        text_lower = text.lower()
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for keyword in degree_keywords:
                if keyword in line_lower:
                    # Extract year if present in nearby lines
                    year_match = re.search(r'\b(19|20)\d{2}\b', line)
                    if not year_match and i < len(lines) - 1:
                        year_match = re.search(r'\b(19|20)\d{2}\b', lines[i + 1])
                    
                    education.append({
                        'degree': line.strip(),
                        'year': year_match.group(0) if year_match else None
                    })
                    break
        
        return education
    
    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract work experience sections.
        Look for role titles and date ranges.
        """
        experience = []
        
        # Common job title keywords
        title_keywords = [
            'architect', 'manager', 'engineer', 'designer', 'developer',
            'specialist', 'coordinator', 'consultant', 'analyst', 'lead'
        ]
        
        lines = text.split('\n')
        text_lower = text.lower()
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if line contains a title keyword
            for keyword in title_keywords:
                if keyword in line_lower:
                    # Look for date range nearby
                    date_pattern = r'\b(19|20)\d{2}\s*-\s*(19|20)\d{2}|(present|current)\b'
                    date_match = re.search(date_pattern, line.lower())
                    
                    if not date_match and i < len(lines) - 1:
                        date_match = re.search(date_pattern, lines[i + 1].lower())
                    
                    experience.append({
                        'role': line.strip(),
                        'dates': date_match.group(0) if date_match else None
                    })
                    break
        
        return experience
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs (portfolio links, LinkedIn, etc.)."""
        pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(pattern, text)
        return urls
