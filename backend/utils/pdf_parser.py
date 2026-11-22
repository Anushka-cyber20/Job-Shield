"""
PDF Offer Letter Text Extractor & Document Inspector for JobShield.
Parses uploaded PDF offer letters and contracts for fraud screening.
"""

import io
from typing import Dict, Any
from pypdf import PdfReader

def extract_text_from_pdf(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Extracts text, metadata, and structural properties from an uploaded PDF.
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(reader.pages)
        full_text = []
        
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            full_text.append(page_text)
            
        combined_text = "\n".join(full_text).strip()
        metadata = reader.metadata or {}
        
        doc_info = {
            "title": str(metadata.get("/Title", "")),
            "author": str(metadata.get("/Author", "")),
            "creator": str(metadata.get("/Creator", "")),
            "producer": str(metadata.get("/Producer", "")),
            "page_count": num_pages
        }
        
        return {
            "success": True,
            "text": combined_text,
            "metadata": doc_info,
            "word_count": len(combined_text.split()),
            "character_count": len(combined_text)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "text": "",
            "metadata": {},
            "word_count": 0,
            "character_count": 0
        }
