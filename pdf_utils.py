import pypdf
import logging
from typing import Optional

def extract_text_from_pdf(pdf_file) -> Optional[str]:
    try:
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page_num, page in enumerate(reader.pages, 1):
            try:
                page_text = page.extract_text() or ""
                text += f"\n=== Page {page_num} ===\n{page_text}"
            except Exception as e:
                logging.error(f"Error extracting text from page {page_num}: {e}")
                continue
        return text.strip() if text else None
    except Exception as e:
        logging.error(f"Error processing PDF: {e}")
        raise Exception("Failed to process PDF. Please ensure the file is not corrupted.")