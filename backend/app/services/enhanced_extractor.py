"""
Enhanced CV data extraction service using regex, NLP, and rule-based parsing.
Extracts 50+ comprehensive data points without AI model dependencies.
"""
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import phonenumbers
from dateutil import parser as date_parser

from app.services.dictionaries import get_skills_dict, get_tools_dict


class EnhancedDataExtractor:
    """Extract comprehensive CV data using advanced regex techniques (NO AI, NO spaCy required)."""
    
    # GCC countries
    GCC_COUNTRIES = ['uae', 'saudi arabia', 'ksa', 'qatar', 'kuwait', 'bahrain', 'oman']
    GCC_CITIES = ['dubai', 'abu dhabi', 'riyadh', 'jeddah', 'doha', 'kuwait city', 'manama', 'muscat']
    
    # Seniority keywords
    SENIORITY_LEVELS = {
        'Director': ['director', 'head of', 'chief', 'vp', 'vice president'],
        'Manager': ['manager', 'mgr', 'team lead', 'project manager'],
        'Lead': ['lead', 'principal', 'senior lead'],
        'Senior': ['senior', 'sr.', 'sr '],
        'Mid-Level': ['mid-level', 'intermediate', 'associate'],
        'Junior': ['junior', 'jr.', 'jr ', 'trainee', 'intern']
    }
    
    # Discipline keywords
    DISCIPLINES = {
        'Architecture': ['architect', 'architecture', 'architectural'],
        'Structural': ['structural', 'structure', 'civil'],
        'MEP': ['mep', 'mechanical', 'electrical', 'plumbing', 'hvac'],
        'BIM': ['bim', 'building information model'],
        'Interior Design': ['interior', 'interior design'],
        'Landscape': ['landscape'],
    }
    
    # Software proficiency indicators
    PROFICIENCY_KEYWORDS = {
        'Expert': ['expert', 'advanced', 'highly proficient', 'mastery', 'specialist'],
        'Intermediate': ['intermediate', 'proficient', 'working knowledge', 'experienced'],
        'Basic': ['basic', 'beginner', 'familiar', 'knowledge of']
    }
    
    # Work mode keywords
    WORK_MODES = {
        'Remote': ['remote', 'work from home', 'wfh'],
        'On-site': ['on-site', 'onsite', 'office-based', 'in-office'],
        'Hybrid': ['hybrid', 'mixed'],
        'Flexible': ['flexible']
    }
    
    def __init__(self):
        self.skills_dict = [s.lower() for s in get_skills_dict()]
        self.tools_dict = [t.lower() for t in get_tools_dict()]
        print("✅ Enhanced Data Extractor initialized (pure regex - no dependencies)")
    
    def extract_comprehensive_data(self, text: str) -> Dict[str, Any]:
        """
        Extract all comprehensive fields from CV text using pure regex.
        
        Returns:
            Dictionary with 50+ extracted fields
        """
        # No spaCy needed - pure regex works perfectly!        
        # Extract all data categories
        contact_details = self._extract_contact_details(text)
        personal_info = self._extract_personal_info(text, email=contact_details.get('email'))
        position_info = self._extract_position_info(text)
        work_history = self._extract_work_history(text)
        gcc_experience = self._calculate_gcc_experience(work_history, text)
        software_exp = self._extract_software_experience(text)
        education = self._extract_education_detailed(text)
        salary_info = self._extract_salary_info(text)
        evaluation = self._extract_evaluation_criteria(text)
        
        return {
            # Personal Information
            'name': personal_info.get('name'),
            'date_of_birth': personal_info.get('date_of_birth'),
            'nationality': personal_info.get('nationality'),
            'marital_status': personal_info.get('marital_status'),
            'military_status': personal_info.get('military_status'),
            'current_country': personal_info.get('current_country'),
            'current_city': personal_info.get('current_city'),
            
            # Contact Details
            'email': contact_details.get('email'),
            'phone': contact_details.get('phone'),
            'linkedin_url': contact_details.get('linkedin_url'),
            'portfolio_url': contact_details.get('portfolio_url'),
            'behance_url': contact_details.get('behance_url'),
            'location': contact_details.get('location'),
            
            # Position & Discipline
            'current_position': position_info.get('current_position'),
            'discipline': position_info.get('discipline'),
            'sub_discipline': position_info.get('sub_discipline'),
            
            # Experience Metrics
            'total_experience_years': gcc_experience.get('total_experience_years'),
            'relevant_experience_years': gcc_experience.get('relevant_experience_years'),
            'gcc_experience_years': gcc_experience.get('gcc_experience_years'),
            'worked_on_gcc_projects': gcc_experience.get('worked_on_gcc_projects'),
            'worked_with_mncs': gcc_experience.get('worked_with_mncs'),
            
            # Structured Data
            'work_history': work_history,
            'software_experience': software_exp,
            'education_details': education,
            
            # Legacy fields for compatibility
            'skills': self._extract_skills(text),
            'tools': self._extract_tools(text),
            'education': [{'degree': e.get('degree', ''), 'year': e.get('graduation_year', '')} for e in education],
            'experience': [{'role': w.get('job_title', ''), 'dates': f"{w.get('start_date', '')} - {w.get('end_date', '')}"} 
                          for w in work_history],
            'portfolio_urls': contact_details.get('all_urls', []),
            
            # Salary & Availability
            'current_salary_aed': salary_info.get('current_salary_aed'),
            'expected_salary_aed': salary_info.get('expected_salary_aed'),
            'notice_period_days': salary_info.get('notice_period_days'),
            'willing_to_relocate': salary_info.get('willing_to_relocate'),
            'willing_to_travel': salary_info.get('willing_to_travel'),
            
            # Evaluation Criteria
            'portfolio_relevancy_score': evaluation.get('portfolio_relevancy_score'),
            'english_proficiency': evaluation.get('english_proficiency'),
            'soft_skills': evaluation.get('soft_skills'),
        }
    
    def _extract_personal_info(self, text: str, email: Optional[str] = None) -> Dict[str, Any]:
        """Extract personal information using regex patterns."""
        info = {}
        
        # Name (use existing method)
        info['name'] = self._extract_name(text, email)
        
        # Date of Birth
        dob_patterns = [
            r'(?:date of birth|dob|born)[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:date of birth|dob|born)[:\s]+(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4})'
        ]
        for pattern in dob_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    info['date_of_birth'] = date_parser.parse(match.group(1)).strftime('%Y-%m-%d')
                    break
                except:
                    pass
        
        # Nationality
        nationality_pattern = r'(?:nationality|citizen)[:\s]+([a-z]+(?:\s+[a-z]+)?)'
        match = re.search(nationality_pattern, text.lower())
        if match:
            info['nationality'] = match.group(1).strip().title()
        
        # Marital Status
        marital_patterns = ['single', 'married', 'divorced', 'widowed']
        for status in marital_patterns:
            if re.search(rf'\b{status}\b', text.lower()):
                info['marital_status'] = status.title()
                break
        
        # Military Status
        military_patterns = ['completed', 'exempted', 'postponed', 'not applicable']
        for status in military_patterns:
            if re.search(rf'military[:\s]+{status}', text.lower()):
                info['military_status'] = status.title()
                break
        
        # Current Location (City, Country)
        location = self._extract_location(text)
        if location:
            parts = location.split(',')
            if len(parts) >= 2:
                info['current_city'] = parts[0].strip()
                info['current_country'] = parts[1].strip()
            else:
                info['current_city'] = location
        
        return info
    
    def _extract_contact_details(self, text: str) -> Dict[str, Any]:
        """Extract contact information using regex."""
        details = {}
        
        # Email
        details['email'] = self._extract_email(text)
        
        # Phone
        details['phone'] = self._extract_phone(text)
        
        # URLs
        all_urls = self._extract_urls(text)
        details['all_urls'] = all_urls
        
        # Categorize URLs
        for url in all_urls:
            url_lower = url.lower()
            if 'linkedin.com' in url_lower:
                details['linkedin_url'] = url
            elif 'behance.net' in url_lower or 'behance.com' in url_lower:
                details['behance_url'] = url
            elif any(domain in url_lower for domain in ['portfolio', 'drive.google', 'dropbox', 'website']):
                if 'portfolio_url' not in details:
                    details['portfolio_url'] = url
        
        # Location
        details['location'] = self._extract_location(text)
        
        return details
    
    def _extract_position_info(self, text: str) -> Dict[str, Any]:
        """Extract current position and discipline information."""
        info = {}
        
        # Current/Last Position - look for recent role
        position_patterns = [
            r'(?:current|present)[^\n]*?(?:position|role|title)[:\s]+([^\n]+)',
            r'(?:position|role|title)[:\s]+([^\n]+)',
        ]
        
        for pattern in position_patterns:
            match = re.search(pattern, text.lower())
            if match:
                info['current_position'] = match.group(1).strip().title()
                break
        
        # If not found, use first job title from experience
        if not info.get('current_position'):
            lines = text.split('\n')
            for i, line in enumerate(lines[:30]):
                for title_keyword in ['architect', 'engineer', 'manager', 'designer', 'coordinator', 'specialist']:
                    if title_keyword in line.lower() and len(line.split()) <= 6:
                        info['current_position'] = line.strip()
                        break
                if info.get('current_position'):
                    break
        
        # Discipline
        for discipline, keywords in self.DISCIPLINES.items():
            if any(kw in text.lower() for kw in keywords):
                info['discipline'] = discipline
                break
        
        # Sub-discipline (more specific)
        subdiscipline_keywords = {
            'BIM Modeling': ['bim model', 'revit model'],
            'BIM Coordination': ['bim coord', 'coordination'],
            'Technical Office': ['technical office', 'design engineer'],
            'Site Engineer': ['site engineer', 'site supervision'],
            'Project Management': ['project manage', 'project manager'],
        }
        
        for subdiscipline, keywords in subdiscipline_keywords.items():
            if any(kw in text.lower() for kw in keywords):
                info['sub_discipline'] = subdiscipline
                break
        
        return info
    
    def _extract_work_history(self, text: str) -> List[Dict[str, Any]]:
        """Extract detailed work history with all fields."""
        work_history = []
        
        # Find experience section
        exp_section = self._extract_experience_section(text)
       
        if not exp_section:
            return []
        
        # Split into job entries (typically separated by blank lines or dates)
        # Pattern: look for date ranges
        date_pattern = r'(\d{1,2}[-/]\d{4}|\w+\s+\d{4})\s*[-–—to]+\s*(\d{1,2}[-/]\d{4}|\w+\s+\d{4}|present|current)'
        
        entries = []
        current_entry = []
        lines = exp_section.split('\n')
        
        for line in lines:
            if re.search(date_pattern, line.lower()):
                if current_entry:
                    entries.append('\n'.join(current_entry))
                current_entry = [line]
            else:
                current_entry.append(line)
        
        if current_entry:
            entries.append('\n'.join(current_entry))
        
        # Parse each entry
        for entry in entries:
            job = self._parse_work_entry(entry)
            if job:
                work_history.append(job)
        
        return work_history
    
    def _parse_work_entry(self, entry: str) -> Optional[Dict[str, Any]]:
        """Parse a single work history entry."""
        job = {}
        
        # Extract dates
        date_pattern = r'(\w+\s+\d{4}|\d{1,2}[-/]\d{4})\s*[-–—to]+\s*(\w+\s+\d{4}|\d{1,2}[-/]\d{4}|present|current)'
        date_match = re.search(date_pattern, entry.lower())
        
        if date_match:
            job['start_date'] = date_match.group(1).strip().title()
            job['end_date'] = date_match.group(2).strip().title()
            
            # Calculate duration
            job['duration_months'] = self._calculate_duration(job['start_date'], job['end_date'])
        
        # Extract job title (usually first line or before dates)
        lines = [l.strip() for l in entry.split('\n') if l.strip()]
        if lines:
            job['job_title'] = lines[0]
        
        # Determine seniority level
        job['seniority_level'] = self._determine_seniority(job.get('job_title', ''))
        
        # Extract company name (usually after title, before or after location)
        company_pattern = r'(?:at|@)\s+([^,\n]+?)(?:,|\n|$)'
        company_match = re.search(company_pattern, entry)
        if company_match:
            job['company_name'] = company_match.group(1).strip()
        else:
            # Try to find company in second line
            if len(lines) > 1:
                job['company_name'] = lines[1]
        
        # Extract location (City, Country pattern)
        location_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        location_match = re.search(location_pattern, entry)
        if location_match:
            job['company_location'] = f"{location_match.group(1)}, {location_match.group(2)}"
        
        # Determine mode of work
        job['mode_of_work'] = self._determine_work_mode(entry)
        
        # Extract roles and responsibilities (bullet points or description)
        responsibilities = []
        for line in lines:
            if re.match(r'^[-•●]\s', line) or line.lower().startswith(('responsible', 'managed', 'led', 'developed')):
                responsibilities.append(line.strip())
        job['roles_responsibilities'] = '; '.join(responsibilities) if responsibilities else ''
        
        # Extract project mentions
        projects = []
        project_pattern = r'(?:project|development|building|complex)[:s]?\s+([A-Z][^\n,.]+?)(?:[,.\n]|$)'
        for match in re.finditer(project_pattern, entry):
            projects.append(match.group(1).strip())
        job['key_projects'] = projects[:5]  # Limit to 5
        
        # Determine if projects were in GCC
        gcc_indicators = any(gcc in entry.lower() for gcc in self.GCC_COUNTRIES + self.GCC_CITIES)
        job['project_locations'] = ['GCC'] if gcc_indicators else ['Local']
        
        return job if job.get('job_title') else None
    
    def _calculate_duration(self, start_date: str, end_date: str) -> int:
        """Calculate duration in months between two dates."""
        try:
            # Parse dates
            if 'present' in end_date.lower() or 'current' in end_date.lower():
                end = datetime.now()
            else:
                end = date_parser.parse(end_date)
            
            start = date_parser.parse(start_date)
            
            # Calculate months
            months = (end.year - start.year) * 12 + (end.month - start.month)
            return max(months, 0)
        except:
            return 0
    
    def _determine_seniority(self, job_title: str) -> str:
        """Determine seniority level from job title."""
        title_lower = job_title.lower()
        
        for level, keywords in self.SENIORITY_LEVELS.items():
            if any(kw in title_lower for kw in keywords):
                return level
        
        return 'Mid-Level'  # Default
    
    def _determine_work_mode(self, text: str) -> str:
        """Determine work mode from text."""
        text_lower = text.lower()
        
        for mode, keywords in self.WORK_MODES.items():
            if any(kw in text_lower for kw in keywords):
                return mode
        
        return 'On-site'  # Default assumption
    
    def _calculate_gcc_experience(self, work_history: List[Dict], text: str) -> Dict[str, Any]:
        """Calculate GCC and total experience metrics."""
        total_months = 0
        gcc_months = 0
        
        for job in work_history:
            duration = job.get('duration_months', 0)
            total_months += duration
            
            # Check if GCC project
            if 'GCC' in job.get('project_locations', []):
                gcc_months += duration
        
        # Check for MNC mentions
        mnc_indicators = ['multinational', 'international', 'global company', '100+ employees', 'fortune 500']
        worked_with_mncs = any(indicator in text.lower() for indicator in mnc_indicators)
        
        # Also check company names that are known MNCs
        mnc_companies = ['aecom', 'jacobs', 'kpf', 'gensler', 'hok', 'atkins', 'parsons', 'arcadis']
        for job in work_history:
            company = job.get('company_name', '').lower()
            if any(mnc in company for mnc in mnc_companies):
                worked_with_mncs = True
                break
        
        return {
            'total_experience_years': round(total_months / 12, 1),
            'relevant_experience_years': round(total_months / 12, 1),  # Assuming all is relevant
            'gcc_experience_years': round(gcc_months / 12, 1),
            'worked_on_gcc_projects': gcc_months > 0,
            'worked_with_mncs': worked_with_mncs,
        }
    
    def _extract_software_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract software experience with proficiency levels."""
        software_list = []
        text_lower = text.lower()
        
        # Find all tools mentioned
        found_tools = []
        for tool in self.tools_dict:
            pattern = r'\b' + re.escape(tool) + r'\b'
            if re.search(pattern, text_lower):
                found_tools.append(tool)
        
        # For each tool, determine proficiency and years
        for tool in found_tools:
            software = {'software_name': tool.title()}
            
            # Find context around tool mention
            tool_pattern = rf'(.{{0,100}}\b{re.escape(tool)}\b.{{0,100}})'
            matches = re.findall(tool_pattern, text_lower)
            context = ' '.join(matches)
            
            # Determine proficiency
            proficiency = 'Intermediate'  # Default
            for level, keywords in self.PROFICIENCY_KEYWORDS.items():
                if any(kw in context for kw in keywords):
                    proficiency = level
                    break
            software['proficiency_level'] = proficiency
            
            # Try to extract years of experience
            years_pattern = rf'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience\s+)?(?:with\s+|in\s+)?{re.escape(tool)}'
            years_match = re.search(years_pattern, context)
            if years_match:
                software['years_of_experience'] = float(years_match.group(1))
            else:
                # Estimate based on proficiency
                if proficiency == 'Expert':
                    software['years_of_experience'] = 5.0
                elif proficiency == 'Intermediate':
                    software['years_of_experience'] = 3.0
                else:
                    software['years_of_experience'] = 1.0
            
            software['is_relevant'] = True  # Will be updated during matching
            software_list.append(software)
        
        return software_list
    
    def _extract_education_detailed(self, text: str) -> List[Dict[str, Any]]:
        """Extract detailed education information."""
        education_list = []
        
        # Find education section
        edu_section = self._extract_education_section(text)
        if not edu_section:
            return []
        
        # Degree keywords
        degree_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'diploma',
            'b.sc', 'm.sc', 'b.tech', 'm.tech', 'mba', 'bba', 'b.arch', 'm.arch'
        ]
        
        lines = edu_section.split('\n')
        current_edu = {}
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check for degree
            for keyword in degree_keywords:
                if keyword in line_lower:
                    if current_edu:
                        education_list.append(current_edu)
                    
                    current_edu = {'degree': line.strip()}
                    
                    # Extract major/field
                    major_pattern = r'(?:in|of)\s+([A-Za-z\s]+?)(?:\s+from|\s+at|,|\n|$)'
                    major_match = re.search(major_pattern, line)
                    if major_match:
                        current_edu['major'] = major_match.group(1).strip()
                    
                    # Try to find university in next lines
                    if i + 1 < len(lines):
                        current_edu['university'] = lines[i + 1].strip()
                    
                    # Extract year
                    year_match = re.search(r'\b(19|20)\d{2}\b', line)
                    if not year_match and i + 1 < len(lines):
                        year_match = re.search(r'\b(19|20)\d{2}\b', lines[i + 1])
                    if year_match:
                        current_edu['graduation_year'] = year_match.group(0)
                    
                    # Determine if relevant
                    relevant_fields = ['civil', 'architecture', 'mechanical', 'electrical', 'engineering']
                    current_edu['relevant_qualification'] = any(
                        field in line_lower for field in relevant_fields
                    )
                    
                    break
        
        if current_edu:
            education_list.append(current_edu)
        
        # Extract certifications
        cert_pattern = r'(?:certified|certification|certificate)[:s]?\s+([A-Z][^\n,.]+?)(?:[,.\n]|$)'
        certifications = []
        for match in re.finditer(cert_pattern, text):
            certifications.append(match.group(1).strip())
        
        # Add certifications to all education entries
        for edu in education_list:
            edu['certifications'] = certifications
        
        return education_list
    
    def _extract_salary_info(self, text: str) -> Dict[str, Any]:
        """Extract salary and availability information."""
        info = {}
        text_lower = text.lower()
        
        # Current Salary (AED)
        current_salary_patterns = [
            r'current\s+salary[:\s]+(?:aed\s+)?(\d+[,\d]*)',
            r'salary[:\s]+(?:aed\s+)?(\d+[,\d]*)',
        ]
        for pattern in current_salary_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    info['current_salary_aed'] = float(match.group(1).replace(',', ''))
                    break
                except:
                    pass
        
        # Expected Salary (AED)
        expected_salary_patterns = [
            r'expected\s+salary[:\s]+(?:aed\s+)?(\d+[,\d]*)',
            r'salary\s+expectation[:\s]+(?:aed\s+)?(\d+[,\d]*)',
        ]
        for pattern in expected_salary_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    info['expected_salary_aed'] = float(match.group(1).replace(',', ''))
                    break
                except:
                    pass
        
        # Notice Period
        notice_patterns = [
            r'notice\s+period[:\s]+(\d+)\s*(?:days?|weeks?|months?)',
            r'availability[:\s]+(\d+)\s*(?:days?|weeks?|months?)',
        ]
        for pattern in notice_patterns:
            match = re.search(pattern, text_lower)
            if match:
                days = int(match.group(1))
                if 'week' in match.group(0):
                    days *= 7
                elif 'month' in match.group(0):
                    days *= 30
                info['notice_period_days'] = days
                break
        
        # Willingness to relocate
        relocate_keywords = ['willing to relocate', 'open to relocation', 'ready to relocate']
        info['willing_to_relocate'] = any(kw in text_lower for kw in relocate_keywords)
        
        # Willingness to travel
        travel_keywords = ['willing to travel', 'open to travel', 'ready to travel']
        info['willing_to_travel'] = any(kw in text_lower for kw in travel_keywords)
        
        return info
    
    def _extract_evaluation_criteria(self, text: str) -> Dict[str, Any]:
        """Extract evaluation criteria and soft skills."""
        criteria = {}
        text_lower = text.lower()
        
        # Portfolio relevancy score (0-100)
        # Based on presence of portfolio links and project descriptions
        score = 0
        if 'portfolio' in text_lower or 'behance' in text_lower:
            score += 30
        
        # Count project mentions
        project_count = len(re.findall(r'\bproject\b', text_lower))
        score += min(project_count * 5, 40)
        
        # Check for detailed descriptions
        if len(text) > 2000:  # Detailed CV
            score += 30
        elif len(text) > 1000:
            score += 20
        
        criteria['portfolio_relevancy_score'] = min(score, 100)
        
        # English proficiency (inferred from CV quality)
        word_count = len(text.split())
        grammar_indicators = ['excellent', 'proficient', 'fluent', 'native']
        
        if any(ind in text_lower for ind in grammar_indicators):
            criteria['english_proficiency'] = 'Fluent'
        elif word_count > 500 and len(text) > 2000:
            criteria['english_proficiency'] = 'Good'
        else:
            criteria['english_proficiency'] = 'Basic'
        
        # Soft skills
        soft_skills_keywords = {
            'Leadership': ['leadership', 'team lead', 'managed team', 'mentored'],
            'Communication': ['communication', 'presentation', 'stakeholder', 'client-facing'],
            'Time Management': ['time management', 'deadline', 'prioritize', 'efficient'],
            'Coordination': ['coordination', 'collaborate', 'cross-functional', 'liaison'],
            'Problem Solving': ['problem solving', 'analytical', 'troubleshoot'],
            'Teamwork': ['teamwork', 'team player', 'collaborative'],
        }
        
        found_skills = []
        for skill, keywords in soft_skills_keywords.items():
            if any(kw in text_lower for kw in keywords):
                found_skills.append(skill)
        
        criteria['soft_skills'] = found_skills
        
        return criteria
    
    # ========== Helper methods (reused from original extractor) ==========
    
    def _extract_name(self, text: str, email: Optional[str] = None) -> Optional[str]:
        """
        Extract candidate name.
        Uses email for fuzzy matching if provided.
        """
        lines = text.split('\n')
        
        # 1. Try to find name matching email
        if email:
            username = email.split('@')[0]
            # Remove digits and special chars from username for comparison
            username_clean = re.sub(r'[^a-z]', '', username.lower())
            
            if len(username_clean) > 3:
                for line in lines[:20]:
                    line_clean = line.strip()
                    if not line_clean: continue
                    
                    line_lower = line_clean.lower()
                    
                    # Skip common headers
                    if any(keyword in line_lower for keyword in ['resume', 'curriculum', 'vitae', 'cv', 'profile']):
                        continue
                        
                    # Check if line contains parts of the username
                    # e.g. "Shifa Shaj" matches "shifashaj"
                    line_alpha = re.sub(r'[^a-z]', '', line_lower)
                    
                    if len(line_alpha) > 3:
                        # Check strict match (one contains the other)
                        if (username_clean in line_alpha or line_alpha in username_clean) and len(line_clean.split()) >= 2:
                            return line_clean.title()
        
        # 2. Standard extraction with improved exclusions
        for line in lines[:20]:  # Increased range slightly
            line = line.strip()
            if len(line) > 0 and len(line) < 60:
                line_lower = line.lower()
                
                # Exclusions - Headers
                if any(keyword in line_lower for keyword in ['resume', 'curriculum', 'vitae', 'cv', 'profile', 'personal information']):
                    continue
                
                # Exclusions - Job Titles & Common False Positives
                false_positives = [
                    'survey', 'surveyor', 'quantity', 'engineer', 'architect', 'developer', 
                    'consultant', 'manager', 'director', 'technician', 'specialist',
                    'university', 'school', 'college', 'institute',
                    'address', 'phone', 'email', 'contact'
                ]
                
                if any(keyword in line_lower for keyword in false_positives):
                    continue
                
                words = line.split()
                if 2 <= len(words) <= 5:
                    # Check if words are mostly alphabets
                    alpha_words = [w for w in words if re.match(r'^[A-Za-z][A-Za-z.\-]*$', w)]
                    if len(alpha_words) >= 2:
                        name = ' '.join(alpha_words)
                        return name.title()
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address."""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(pattern, text)
        return matches[0] if matches else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract and normalize phone number."""
        potential_phones = re.findall(
            r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            text
        )
        
        if potential_phones:
            phone = ''.join(potential_phones[0].split())
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
        """Extract location/address."""
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)\b'
        matches = re.findall(pattern, text)
        
        if matches:
            city, state = matches[0]
            return f"{city}, {state}"
        
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills by matching against dictionary."""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills_dict:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return list(set(found_skills))
    
    def _extract_tools(self, text: str) -> List[str]:
        """Extract software/tools by matching against dictionary."""
        text_lower = text.lower()
        found_tools = []
        
        for tool in self.tools_dict:
            pattern = r'\b' + re.escape(tool) + r'\b'
            if re.search(pattern, text_lower):
                found_tools.append(tool)
        
        return list(set(found_tools))
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs."""
        pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(pattern, text)
        return urls
    
    def _extract_experience_section(self, text: str) -> str:
        """Extract the work experience section from CV."""
        # Find experience section markers
        exp_markers = [
            r'(?:work\s+)?experience',
            r'employment\s+history',
            r'professional\s+experience',
            r'career\s+history'
        ]
        
        # Find education section (to know where experience ends)
        edu_markers = [
            r'education',
            r'academic',
            r'qualifications'
        ]
        
        text_lower = text.lower()
        
        # Find start of experience
        exp_start = -1
        for marker in exp_markers:
            match = re.search(marker, text_lower)
            if match:
                exp_start = match.end()
                break
        
        if exp_start == -1:
            return ''
        
        # Find end of experience (start of education or skills)
        exp_end = len(text)
        for marker in edu_markers + [r'skills', r'certifications']:
            match = re.search(marker, text_lower[exp_start:])
            if match:
                exp_end = exp_start + match.start()
                break
        
        return text[exp_start:exp_end]
    
    def _extract_education_section(self, text: str) -> str:
        """Extract the education section from CV."""
        edu_markers = [
            r'education',
            r'academic',
            r'qualifications',
            r'degrees'
        ]
        
        text_lower = text.lower()
        
        # Find start
        edu_start = -1
        for marker in edu_markers:
            match = re.search(marker, text_lower)
            if match:
                edu_start = match.end()
                break
        
        if edu_start == -1:
            return ''
        
        # Find end (certifications or skills section)
        edu_end = len(text)
        for marker in [r'certifications?', r'skills', r'languages', r'references']:
            match = re.search(marker, text_lower[edu_start:])
            if match:
                edu_end = edu_start + match.start()
                break
        
        return text[edu_start:edu_end]
