"""
File validation service for uploaded CVs and portfolios.
Validates file types, sizes, and performs basic security checks.
"""
from fastapi import UploadFile
from typing import Dict
import magic
from pathlib import Path

from app.config import settings


class FileValidator:
    """Validates uploaded files for security and compatibility."""
    
    def __init__(self):
        self.allowed_extensions = settings.allowed_extensions_list
        self.max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    
    async def validate_file(self, file: UploadFile) -> Dict[str, any]:
        """
        Validate an uploaded file.
        
        Returns:
            Dict with 'valid' (bool) and 'error' (str) if invalid
        """
        # Check filename extension
        file_ext = Path(file.filename).suffix.lower().lstrip('.')
        if file_ext not in self.allowed_extensions:
            return {
                "valid": False,
                "error": f"File extension '.{file_ext}' not allowed. Allowed: {', '.join(self.allowed_extensions)}"
            }
        
        # Read file for validation (will reset after)
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Check file size
        file_size = len(content)
        if file_size > self.max_size_bytes:
            return {
                "valid": False,
                "error": f"File size {file_size/1024/1024:.2f}MB exceeds maximum {settings.MAX_FILE_SIZE_MB}MB"
            }
        
        # Check for empty files
        if file_size == 0:
            return {
                "valid": False,
                "error": "File is empty"
            }
        
        # MIME type validation
        try:
            mime_type = magic.from_buffer(content, mime=True)
            
            # Define allowed MIME types
            allowed_mimes = {
                'pdf': ['application/pdf'],
                'jpg': ['image/jpeg'],
                'jpeg': ['image/jpeg'],
                'png': ['image/png'],
                'tiff': ['image/tiff'],
                'doc': ['application/msword'],
                'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            }
            
            if file_ext in allowed_mimes:
                if mime_type not in allowed_mimes[file_ext]:
                    return {
                        "valid": False,
                        "error": f"File content doesn't match extension. Expected {allowed_mimes[file_ext]}, got {mime_type}"
                    }
        except Exception as e:
            # If magic fails, just log and continue (optional check)
            print(f"MIME type check failed: {e}")
        
        # Basic malware check - check for suspicious patterns
        # In production, integrate with ClamAV or similar
        suspicious_signatures = [
            b'<script',
            b'javascript:',
            b'eval(',
        ]
        
        content_lower = content.lower()
        for sig in suspicious_signatures:
            if sig in content_lower:
                return {
                    "valid": False,
                    "error": "File contains suspicious content"
                }
        
        return {"valid": True, "error": None}
