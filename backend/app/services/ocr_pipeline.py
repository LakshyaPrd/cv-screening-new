"""
OCR Pipeline for processing CVs and portfolios.
Handles PDF conversion, image preprocessing, OCR, and data extraction.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from sqlalchemy.orm import Session

from app.config import settings
from app.models.candidate import Candidate
from app.services.enhanced_extractor import EnhancedDataExtractor


class OCRPipeline:
    """Main OCR processing pipeline."""
    
    def __init__(self):
        self.tesseract_path = settings.TESSERACT_PATH
        self.dpi = settings.OCR_DPI
        self.languages = settings.OCR_LANGUAGES
        self.extractor = EnhancedDataExtractor()  # Use enhanced extractor
        
        # Set Tesseract path if configured
        if self.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
    
    def process_file(self, file_path: str, batch_id: str, db: Session) -> Candidate:
        """
        Process a single CV/portfolio file.
        
        Args:
            file_path: Path to the file
            batch_id: Batch ID this file belongs to
            db: Database session
        
        Returns:
            Candidate object with extracted data
        """
        file_path = Path(file_path)
        
        # Determine file type
        extension = file_path.suffix.lower()
        
        # Extract text based on file type
        try:
            raw_text = self.extract_text(file_path)
        except ValueError as e:
            # Fallback/Error handling or re-raise
            if "Unsupported file type" in str(e):
                raise ValueError(f"Unsupported file type: {extension}")
            raise e
        
    def extract_text(self, file_path: Path) -> str:
        """
        Extract raw text from a file (PDF or Image).
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text string
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return self._process_pdf(file_path)
        elif extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            return self._process_image(file_path)
        elif extension in ['.doc', '.docx']:
             # For DOC/DOCX, convert to PDF first (requires additional library)
            # Simplified: just return placeholder
            return "DOC/DOCX processing not yet implemented"
        else:
            raise ValueError(f"Unsupported file type: {extension}")
        
        # Calculate OCR quality score
        ocr_quality = self._calculate_ocr_quality(raw_text)
        
        # Extract comprehensive structured data
        extracted_data = self.extractor.extract_comprehensive_data(raw_text)
        
        # Convert boolean strings to actual booleans (for SQLite compatibility)
        def to_bool_str(val):
            if isinstance(val, bool):
                return 'true' if val else 'false'
            return val
        
        # Create candidate record with ALL comprehensive fields
        candidate = Candidate(
            batch_id=batch_id,
            
            # Contact Information
            name=extracted_data.get('name'),
            email=extracted_data.get('email'),
            phone=extracted_data.get('phone'),
            location=extracted_data.get('location'),
            
            # Personal Information
            date_of_birth=extracted_data.get('date_of_birth'),
            nationality=extracted_data.get('nationality'),
            marital_status=extracted_data.get('marital_status'),
            military_status=extracted_data.get('military_status'),
            current_country=extracted_data.get('current_country'),
            current_city=extracted_data.get('current_city'),
            
            # Extended Contact
            linkedin_url=extracted_data.get('linkedin_url'),
            portfolio_url=extracted_data.get('portfolio_url'),
            behance_url=extracted_data.get('behance_url'),
            
            # Position & Discipline
            current_position=extracted_data.get('current_position'),
            discipline=extracted_data.get('discipline'),
            sub_discipline=extracted_data.get('sub_discipline'),
            
            # Experience Metrics
            total_experience_years=extracted_data.get('total_experience_years'),
            relevant_experience_years=extracted_data.get('relevant_experience_years'),
            gcc_experience_years=extracted_data.get('gcc_experience_years'),
            worked_on_gcc_projects=to_bool_str(extracted_data.get('worked_on_gcc_projects')),
            worked_with_mncs=to_bool_str(extracted_data.get('worked_with_mncs')),
            
            # Salary & Availability
            current_salary_aed=extracted_data.get('current_salary_aed'),
            expected_salary_aed=extracted_data.get('expected_salary_aed'),
            notice_period_days=extracted_data.get('notice_period_days'),
            willing_to_relocate=to_bool_str(extracted_data.get('willing_to_relocate')),
            willing_to_travel=to_bool_str(extracted_data.get('willing_to_travel')),
            
            # Evaluation
            portfolio_relevancy_score=extracted_data.get('portfolio_relevancy_score'),
            english_proficiency=extracted_data.get('english_proficiency'),
            
            # Legacy fields (for backward compatibility)
            skills=extracted_data.get('skills', []),
            tools=extracted_data.get('tools', []),
            education=extracted_data.get('education', []),
            experience=extracted_data.get('experience', []),
            portfolio_urls=extracted_data.get('portfolio_urls', []),
            
            # Enhanced structured data
            work_history=extracted_data.get('work_history', []),
            software_experience=extracted_data.get('software_experience', []),
            education_details=extracted_data.get('education_details', []),
            soft_skills=extracted_data.get('soft_skills', []),
            
            # OCR Data
            raw_text=raw_text,
            ocr_quality_score=ocr_quality,
            cv_file_path=str(file_path),
            extraction_status="completed",
        )
        
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        return candidate
    
    def _process_pdf(self, pdf_path: Path) -> str:
        """
        Convert PDF to images and perform OCR.
        """
        try:
            # Convert PDF to images
            images = convert_from_path(
                str(pdf_path),
                dpi=self.dpi,
                poppler_path=settings.POPPLER_PATH if hasattr(settings, 'POPPLER_PATH') else None
            )
            
            # Perform OCR on each page
            full_text = []
            for i, image in enumerate(images):
                # Preprocess image
                processed_image = self._preprocess_image(image)
                
                # OCR
                page_text = pytesseract.image_to_string(
                    processed_image,
                    lang=self.languages
                )
                full_text.append(f"--- Page {i + 1} ---\n{page_text}")
            
            return "\n\n".join(full_text)
            
        except Exception as e:
            raise Exception(f"PDF OCR failed: {str(e)}")
    
    def _process_image(self, image_path: Path) -> str:
        """
        Perform OCR on an image file.
        """
        try:
            # Load image
            image = Image.open(image_path)
            
            # Preprocess
            processed_image = self._preprocess_image(image)
            
            # OCR
            text = pytesseract.image_to_string(
                processed_image,
                lang=self.languages
            )
            
            return text
            
        except Exception as e:
            raise Exception(f"Image OCR failed: {str(e)}")
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results.
        - Convert to grayscale
        - Enhance contrast
        - Deskew (simplified)
        """
        # Convert to grayscale
        image = image.convert('L')
        
        # Enhance contrast (simple approach)
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # In production, add deskew and rotation detection
        
        return image
    
    def _calculate_ocr_quality(self, text: str) -> float:
        """
        Calculate OCR quality score (0-100).
        Based on heuristics like text length, word count, etc.
        """
        if not text or len(text.strip()) == 0:
            return 0.0
        
        # Count words
        words = text.split()
        num_words = len(words)
        
        # Count alpha characters vs total
        alpha_count = sum(c.isalpha() for c in text)
        total_chars = len(text)
        alpha_ratio = alpha_count / total_chars if total_chars > 0 else 0
        
        # Heuristic score
        score = 0.0
        
        # More words = better (up to 50 points)
        score += min(num_words / 10, 50)
        
        # Higher alpha ratio = better (up to 50 points)
        score += alpha_ratio * 50
        
        return min(score, 100.0)
