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
    
    GCC_COUNTRIES = ['uae', 'saudi arabia', 'ksa', 'qatar', 'kuwait', 'bahrain', 'oman']
    GCC_CITIES = ['dubai', 'abu dhabi', 'riyadh', 'jeddah', 'doha', 'kuwait city', 'manama', 'muscat']
    
    SENIORITY_LEVELS = {
        'Director': ['director', 'head of', 'chief', 'vp', 'vice president'],
        'Manager': ['manager', 'mgr', 'team lead', 'project manager'],
        'Lead': ['lead', 'principal', 'senior lead'],
        'Senior': ['senior', 'sr.', 'sr '],
        'Mid-Level': ['mid-level', 'intermediate', 'associate'],
        'Junior': ['junior', 'jr.', 'jr ', 'trainee', 'intern']
    }
    
    DISCIPLINES = {
        'Architecture': ['architect', 'architecture', 'architectural'],
        'Structural': ['structural', 'structure', 'civil'],
        'MEP': ['mep', 'mechanical', 'electrical', 'plumbing', 'hvac'],
        'BIM': ['bim', 'building information model'],
        'Interior Design': ['interior', 'interior design'],
        'Landscape': ['landscape'],
    }
    
    PROFICIENCY_KEYWORDS = {
        'Expert': ['expert', 'advanced', 'highly proficient', 'mastery', 'specialist'],
        'Intermediate': ['intermediate', 'proficient', 'working knowledge', 'experienced'],
        'Basic': ['basic', 'beginner', 'familiar', 'knowledge of']
    }
    
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
            'name': personal_info.get('name'),
            'date_of_birth': personal_info.get('date_of_birth'),
            'nationality': personal_info.get('nationality'),
            'marital_status': personal_info.get('marital_status'),
            'military_status': personal_info.get('military_status'),
            'current_country': personal_info.get('current_country'),
            'current_city': personal_info.get('current_city'),
            
            'email': contact_details.get('email'),
            'phone': contact_details.get('phone'),
            'linkedin_url': contact_details.get('linkedin_url'),
            'portfolio_url': contact_details.get('portfolio_url'),
            'behance_url': contact_details.get('behance_url'),
            'location': contact_details.get('location'),
            
            'current_position': position_info.get('current_position'),
            'discipline': position_info.get('discipline'),
            'sub_discipline': position_info.get('sub_discipline'),
            
            'total_experience_years': gcc_experience.get('total_experience_years'),
            'relevant_experience_years': gcc_experience.get('relevant_experience_years'),
            'gcc_experience_years': gcc_experience.get('gcc_experience_years'),
            'worked_on_gcc_projects': gcc_experience.get('worked_on_gcc_projects'),
            'worked_with_mncs': gcc_experience.get('worked_with_mncs'),
            
            'work_history': work_history,
            'software_experience': software_exp,
            'education_details': education,
            
            'skills': self._extract_skills(text),
            'tools': self._extract_tools(text),
            'education': [{'degree': e.get('degree', ''), 'year': e.get('graduation_year', '')} for e in education],
            'experience': [{'role': w.get('job_title', ''), 'dates': f"{w.get('start_date', '')} - {w.get('end_date', '')}"} 
                           for w in work_history],
            'portfolio_urls': contact_details.get('all_urls', []),
            
            'current_salary_aed': salary_info.get('current_salary_aed'),
            'expected_salary_aed': salary_info.get('expected_salary_aed'),
            'notice_period_days': salary_info.get('notice_period_days'),
            'willing_to_relocate': salary_info.get('willing_to_relocate'),
            'willing_to_travel': salary_info.get('willing_to_travel'),
            
            'portfolio_relevancy_score': evaluation.get('portfolio_relevancy_score'),
            'english_proficiency': evaluation.get('english_proficiency'),
            'soft_skills': evaluation.get('soft_skills'),
        }
    
    # ===================================================================
    # NEW & IMPROVED NAME EXTRACTION (HIGHEST ACCURACY)
    # ===================================================================
    
    def _extract_name(self, text: str, email: Optional[str] = None) -> Optional[str]:
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        blacklist = [
            'resume','curriculum','vitae','cv','profile',
            'experience','education','skills','projects',
            'professional summary','contact','work history',
            'microsoft office', 'microsoft', 'adobe', 'autocad',
            'confidential', 'page'
        ]
        
        # 1. Try from email (stable)
        if email:
            username = email.split('@')[0]
            username_clean = re.sub(r'[^a-z]', '', username.lower())
            
            for line in lines[:25]:
                l = line.lower()
                if any(k in l for k in blacklist):
                    continue
                if len(line.split()) <= 6:
                    l_alpha = re.sub(r'[^a-z]', '', l)
                    if len(l_alpha) >= 3:
                        if username_clean in l_alpha or l_alpha in username_clean:
                            if len(line.split()) >= 2:
                                return line.title()
        
        # 2. Look for typical patterns (new improvement)
        name_patterns = [
            r'^(?:name)[:\s]+([A-Za-z][A-Za-z.\-]*(?:\s+[A-Za-z][A-Za-z.\-]*)+)$',
            r'^([A-Za-z][A-Za-z.\-]*(?:\s+[A-Za-z][A-Za-z.\-]*){1,3})$'
        ]
        
        for line in lines[:20]:
            l = line.lower()
            if any(k in l for k in blacklist):
                continue
            
            for pattern in name_patterns:
                m = re.match(pattern, line.strip(), re.IGNORECASE)
                if m:
                    name = m.group(1).strip()
                    if 2 <= len(name.split()) <= 4:
                        return name.title()
        
        # 3. Final fallback: first valid-looking name line
        for line in lines[:15]:
            l = line.lower()
            if any(k in l for k in blacklist):
                continue
            words = line.split()
            if 2 <= len(words) <= 4:
                # Check if it looks like a software list (contains version numbers)
                if any(c.isdigit() for c in line):
                    continue
                if all(re.match(r'^[A-Za-z][A-Za-z.\-]*$', w) for w in words):
                    return line.title()
        
        return None

    # ===================================================================
    # (Everything below remains EXACTLY as your original file, untouched)
    # ===================================================================

    def _extract_personal_info(self, text: str, email: Optional[str] = None) -> Dict[str, Any]:
        info = {}
        info['name'] = self._extract_name(text, email)
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
        # Improved nationality regex to stop at newlines or common delimiters
        nationality_pattern = r'(?:nationality|citizen)[:\s]+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)(?:[\n\r,.]|$)'
        match = re.search(nationality_pattern, text.lower())
        if match:
            info['nationality'] = match.group(1).strip().title()
        marital_patterns = ['single', 'married', 'divorced', 'widowed']
        for status in marital_patterns:
            if re.search(rf'\b{status}\b', text.lower()):
                info['marital_status'] = status.title()
                break
        military_patterns = ['completed', 'exempted', 'postponed', 'not applicable']
        for status in military_patterns:
            if re.search(rf'military[:\s]+{status}', text.lower()):
                info['military_status'] = status.title()
                break
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
        details = {}
        details['email'] = self._extract_email(text)
        details['phone'] = self._extract_phone(text)
        all_urls = self._extract_urls(text)
        details['all_urls'] = all_urls
        for url in all_urls:
            u = url.lower()
            if 'linkedin.com' in u:
                details['linkedin_url'] = url
            elif 'behance' in u:
                details['behance_url'] = url
            elif any(k in u for k in ['portfolio', 'drive.google', 'dropbox', 'website']):
                if 'portfolio_url' not in details:
                    details['portfolio_url'] = url
        details['location'] = self._extract_location(text)
        return details
    
    def _extract_position_info(self, text: str) -> Dict[str, Any]:
        info = {}
        patterns = [
            r'(?:current|present)[^\n]*?(?:position|role|title)[:\s]+([^\n]+)',
            r'(?:position|role|title)[:\s]+([^\n]+)',
        ]
        for p in patterns:
            m = re.search(p, text.lower())
            if m:
                info['current_position'] = m.group(1).strip().title()
                break
        if not info.get('current_position'):
            lines = text.split('\n')
            for line in lines[:30]:
                for kw in ['architect', 'engineer', 'manager', 'designer', 'coordinator', 'specialist']:
                    if kw in line.lower() and len(line.split()) <= 6:
                        cleaned = self._clean_header_line(line)
                        if cleaned:
                            info['current_position'] = cleaned
                            break
                if info.get('current_position'):
                    break
        for d, kws in self.DISCIPLINES.items():
            if any(kw in text.lower() for kw in kws):
                info['discipline'] = d
                break
        subdisc = {
            'BIM Modeling': ['bim model', 'revit model'],
            'BIM Coordination': ['bim coord', 'coordination'],
            'Technical Office': ['technical office', 'design engineer'],
            'Site Engineer': ['site engineer', 'site supervision'],
            'Project Management': ['project manage', 'project manager'],
        }
        for sd, kws in subdisc.items():
            if any(kw in text.lower() for kw in kws):
                info['sub_discipline'] = sd
                break
        return info
    
    def _extract_work_history(self, text: str) -> List[Dict[str, Any]]:
        work_history = []
        section = self._extract_experience_section(text)
        if not section:
            return []
        date_pattern = r'(\d{1,2}[-/]\d{4}|\w+\s+\d{4})\s*[-–—to]+\s*(\d{1,2}[-/]\d{4}|\w+\s+\d{4}|present|current)'
        entries = []
        current = []
        for line in section.split('\n'):
            if re.search(date_pattern, line.lower()):
                if current:
                    entries.append('\n'.join(current))
                current = [line]
            else:
                current.append(line)
        if current:
            entries.append('\n'.join(current))
        for e in entries:
            job = self._parse_work_entry(e)
            if job:
                work_history.append(job)
        return work_history
    
    def _parse_work_entry(self, entry: str) -> Optional[Dict[str, Any]]:
        job = {}
        date_pattern = r'(\w+\s+\d{4}|\d{1,2}[-/]\d{4})\s*[-–—to]+\s*(\w+\s+\d{4}|\d{1,2}[-/]\d{4}|present|current)'
        dm = re.search(date_pattern, entry.lower())
        if dm:
            job['start_date'] = dm.group(1).strip().title()
            job['end_date'] = dm.group(2).strip().title()
            job['duration_months'] = self._calculate_duration(job['start_date'], job['end_date'])
        
        lines = [l.strip() for l in entry.split('\n') if l.strip()]
        if lines:
            # Clean the first line to get job title (removing dates/bullets)
            job['job_title'] = self._clean_header_line(lines[0])
            
        job['seniority_level'] = self._determine_seniority(job.get('job_title', ''))
        cm = re.search(r'(?:at|@)\s+([^,\n]+?)(?:,|\n|$)', entry)
        if cm:
            job['company_name'] = cm.group(1).strip()
        else:
            if len(lines) > 1:
                # If 2nd line looks like a company (not a bullet point)
                if not re.match(r'^[-•●]', lines[1]):
                   job['company_name'] = lines[1]
                   
        locm = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', entry)
        if locm:
            job['company_location'] = f"{locm.group(1)}, {locm.group(2)}"
        job['mode_of_work'] = self._determine_work_mode(entry)
        resp = []
        for l in lines:
            if re.match(r'^[-•●]\s', l) or l.lower().startswith(('responsible', 'managed', 'led', 'developed')):
                resp.append(l.strip())
        job['roles_responsibilities'] = '; '.join(resp) if resp else ''
        projects = []
        pp = r'(?:project|development|building|complex)[:s]?\s+([A-Z][^\n,.]+?)(?:[,.\n]|$)'
        for m in re.finditer(pp, entry):
            projects.append(m.group(1).strip())
        job['key_projects'] = projects[:5]
        gcc = any(g in entry.lower() for g in self.GCC_COUNTRIES + self.GCC_CITIES)
        job['project_locations'] = ['GCC'] if gcc else ['Local']
        return job if job.get('job_title') else None
    
    def _clean_header_line(self, line: str) -> str:
        """Removes dates, bullets, and common noise from header lines."""
        # 1. Remove date ranges (start or end of line)
        # matches: Jul 2024 - Present, 2019-2024, etc.
        date_pattern = r'(?:\w+\s+\d{4}|\d{1,2}[-/]\d{4}|\d{4})\s*[-–—to]+\s*(?:\w+\s+\d{4}|\d{1,2}[-/]\d{4}|present|current|\d{4})'
        line = re.sub(date_pattern, '', line, flags=re.IGNORECASE)
        
        # 2. Remove leading bullets/arrows
        line = re.sub(r'^[\->•●:;|\s]+', '', line)
        
        # 3. Remove "at Company" suffix if it exists (heuristic)
        line = re.sub(r'\s+(?:at|@)\s+.*$', '', line, flags=re.IGNORECASE)
        
        return line.strip()

    def _calculate_duration(self, start_date: str, end_date: str) -> int:
        try:
            if 'present' in end_date.lower() or 'current' in end_date.lower():
                end = datetime.now()
            else:
                end = date_parser.parse(end_date)
            start = date_parser.parse(start_date)
            months = (end.year - start.year) * 12 + (end.month - start.month)
            return max(months, 0)
        except:
            return 0
    
    def _determine_seniority(self, job_title: str) -> str:
        t = job_title.lower()
        for level, kws in self.SENIORITY_LEVELS.items():
            if any(kw in t for kw in kws):
                return level
        return 'Mid-Level'
    
    def _determine_work_mode(self, text: str) -> str:
        tl = text.lower()
        for mode, kws in self.WORK_MODES.items():
            if any(kw in tl for kw in kws):
                return mode
        return 'On-site'
    
    def _calculate_gcc_experience(self, work_history: List[Dict], text: str) -> Dict[str, Any]:
        total = 0
        gcc = 0
        for job in work_history:
            d = job.get('duration_months', 0)
            total += d
            if 'GCC' in job.get('project_locations', []):
                gcc += d
        worked_with_mncs = any(k in text.lower() for k in ['multinational', 'international', 'global company', '100+ employees', 'fortune 500'])
        mnc_list = ['aecom', 'jacobs', 'kpf', 'gensler', 'hok', 'atkins', 'parsons', 'arcadis']
        for job in work_history:
            c = job.get('company_name','').lower()
            if any(m in c for m in mnc_list):
                worked_with_mncs = True
                break
        return {
            'total_experience_years': round(total/12,1),
            'relevant_experience_years': round(total/12,1),
            'gcc_experience_years': round(gcc/12,1),
            'worked_on_gcc_projects': gcc>0,
            'worked_with_mncs': worked_with_mncs
        }
    
    def _extract_software_experience(self, text: str) -> List[Dict[str, Any]]:
        out = []
        tl = text.lower()
        found = []
        for tool in self.tools_dict:
            if re.search(r'\b'+re.escape(tool)+r'\b', tl):
                found.append(tool)
        for tool in found:
            sw = {'software_name': tool.title()}
            ctx = ' '.join(re.findall(rf'(.{{0,100}}\b{re.escape(tool)}\b.{{0,100}})', tl))
            prof = 'Intermediate'
            for level, kws in self.PROFICIENCY_KEYWORDS.items():
                if any(kw in ctx for kw in kws):
                    prof = level
                    break
            sw['proficiency_level'] = prof
            ym = re.search(rf'(\d+)\+?\s*(?:years?|yrs?).+?{re.escape(tool)}', ctx)
            if ym:
                sw['years_of_experience'] = float(ym.group(1))
            else:
                sw['years_of_experience'] = 5.0 if prof=='Expert' else 3.0 if prof=='Intermediate' else 1.0
            sw['is_relevant'] = True
            out.append(sw)
        return out
    
    def _extract_education_detailed(self, text: str) -> List[Dict[str, Any]]:
        out = []
        section = self._extract_education_section(text)
        if not section:
            return []
        degree_keywords = [
            'bachelor','master','phd','doctorate','diploma',
            'b.sc','m.sc','b.tech','m.tech','mba','bba','b.arch','m.arch'
        ]
        lines = section.split('\n')
        current = {}
        for i, line in enumerate(lines):
            ll = line.lower()
            for k in degree_keywords:
                if k in ll:
                    if current:
                        out.append(current)
                    
                    # Clean the degree line (remove dates)
                    cleaned_degree = self._clean_header_line(line)
                    current = {'degree': cleaned_degree}
                    
                    mm = re.search(r'(?:in|of)\s+([A-Za-z\s]+?)(?:\s+from|\s+at|,|\n|$)', line)
                    if mm:
                        current['major'] = mm.group(1).strip()
                    if i+1 < len(lines):
                        current['university'] = lines[i+1].strip()
                    
                    # Find years (extract the LAST year found, which is typically graduation)
                    years = re.findall(r'\b(19|20)\d{2}\b', line)
                    if not years and i+1 < len(lines):
                        years = re.findall(r'\b(19|20)\d{2}\b', lines[i+1])
                    
                    if years:
                        current['graduation_year'] = years[-1]
                        
                    rel = ['civil','architecture','mechanical','electrical','engineering']
                    current['relevant_qualification'] = any(r in ll for r in rel)
                    break
        if current:
            out.append(current)
        certs = []
        cp = r'(?:certified|certification|certificate)[:s]?\s+([A-Z][^\n,.]+?)(?:[,.\n]|$)'
        for m in re.finditer(cp, text):
            certs.append(m.group(1).strip())
        for e in out:
            e['certifications'] = certs
        return out
    
    def _extract_salary_info(self, text: str) -> Dict[str, Any]:
        out = {}
        tl = text.lower()
        cur = [
            r'current\s+salary[:\s]+(?:aed\s+)?(\d+[,\d]*)',
            r'salary[:\s]+(?:aed\s+)?(\d+[,\d]*)',
        ]
        for p in cur:
            m = re.search(p, tl)
            if m:
                try:
                    out['current_salary_aed'] = float(m.group(1).replace(',', ''))
                    break
                except:
                    pass
        expc = [
            r'expected\s+salary[:\s]+(?:aed\s+)?(\d+[,\d]*)',
            r'salary\s+expectation[:\s]+(?:aed\s+)?(\d+[,\d]*)',
        ]
        for p in expc:
            m = re.search(p, tl)
            if m:
                try:
                    out['expected_salary_aed'] = float(m.group(1).replace(',', ''))
                    break
                except:
                    pass
        notice = [
            r'notice\s+period[:\s]+(\d+)\s*(?:days?|weeks?|months?)',
            r'availability[:\s]+(\d+)\s*(?:days?|weeks?|months?)',
        ]
        for p in notice:
            m = re.search(p, tl)
            if m:
                d = int(m.group(1))
                if 'week' in m.group(0):
                    d *= 7
                elif 'month' in m.group(0):
                    d *= 30
                out['notice_period_days'] = d
                break
        reloc = ['willing to relocate','open to relocation','ready to relocate']
        out['willing_to_relocate'] = any(r in tl for r in reloc)
        travel = ['willing to travel','open to travel','ready to travel']
        out['willing_to_travel'] = any(r in tl for r in travel)
        return out
    
    def _extract_evaluation_criteria(self, text: str) -> Dict[str, Any]:
        out = {}
        tl = text.lower()
        score = 0
        if 'portfolio' in tl or 'behance' in tl:
            score += 30
        score += min(len(re.findall(r'\bproject\b', tl))*5, 40)
        if len(text) > 2000:
            score += 30
        elif len(text) > 1000:
            score += 20
        out['portfolio_relevancy_score'] = min(score, 100)
        wc = len(text.split())
        if any(k in tl for k in ['excellent','proficient','fluent','native']):
            out['english_proficiency'] = 'Fluent'
        elif wc > 500 and len(text) > 2000:
            out['english_proficiency'] = 'Good'
        else:
            out['english_proficiency'] = 'Basic'
        soft = {
            'Leadership': ['leadership','team lead','managed team','mentored'],
            'Communication': ['communication','presentation','stakeholder','client-facing'],
            'Time Management': ['time management','deadline','prioritize','efficient'],
            'Coordination': ['coordination','collaborate','cross-functional','liaison'],
            'Problem Solving': ['problem solving','analytical','troubleshoot'],
            'Teamwork': ['teamwork','team player','collaborative'],
        }
        found = []
        for s, kws in soft.items():
            if any(k in tl for k in kws):
                found.append(s)
        out['soft_skills'] = found
        return out
    
    # === HELPERS BELOW ===
    
    def _extract_email(self, text: str) -> Optional[str]:
        m = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        return m[0] if m else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        phones = re.findall(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phones:
            ph = ''.join(phones[0].split())
            try:
                parsed = phonenumbers.parse(ph, "US")
                if phonenumbers.is_valid_number(parsed):
                    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            except:
                return ph
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        m = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)\b', text)
        if m:
            c, s = m[0]
            return f"{c}, {s}"
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        tl = text.lower()
        out = []
        for s in self.skills_dict:
            if re.search(r'\b'+re.escape(s)+r'\b', tl):
                out.append(s)
        return list(set(out))
    
    def _extract_tools(self, text: str) -> List[str]:
        tl = text.lower()
        out = []
        for t in self.tools_dict:
            if re.search(r'\b'+re.escape(t)+r'\b', tl):
                out.append(t)
        return list(set(out))
    
    def _extract_urls(self, text: str) -> List[str]:
        return re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
    
    def _extract_experience_section(self, text: str) -> str:
        exp_markers = [r'(?:work\s+)?experience', r'employment\s+history', r'professional\s+experience', r'career\s+history']
        edu_markers = [r'education', r'academic', r'qualifications']
        tl = text.lower()
        start = -1
        for m in exp_markers:
            mm = re.search(m, tl)
            if mm:
                start = mm.end()
                break
        if start==-1:
            return ''
        end = len(text)
        for m in edu_markers + [r'skills', r'certifications']:
            mm = re.search(m, tl[start:])
            if mm:
                end = start + mm.start()
                break
        return text[start:end]
    
    def _extract_education_section(self, text: str) -> str:
        markers = [r'education', r'academic', r'qualifications', r'degrees']
        tl = text.lower()
        start = -1
        for m in markers:
            mm = re.search(m, tl)
            if mm:
                start = mm.end()
                break
        if start==-1:
            return ''
        end = len(text)
        for m in [r'certifications?', r'skills', r'languages', r'references']:
            mm = re.search(m, tl[start:])
            if mm:
                end = start + mm.start()
                break
        return text[start:end]
