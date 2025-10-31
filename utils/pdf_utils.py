import fitz  # PyMuPDF

def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF file."""
    try:
        text = ""
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text()
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")
        
        return text
    
    except fitz.FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    except fitz.FileDataError:
        raise ValueError(f"Invalid or corrupted PDF file: {file_path}")
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")