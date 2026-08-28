import io
from pypdf import PdfReader
import docx

def parse_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        extracted_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_text.append(text)
        return "\n".join(extracted_text).strip()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""

def parse_docx(file_bytes: bytes) -> str:
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        extracted_text = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(extracted_text).strip()
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
        return ""

def extract_document_text(filename: str, file_bytes: bytes) -> str:
    lower_filename = filename.lower()
    text = ""
    if lower_filename.endswith(".pdf"):
        text = parse_pdf(file_bytes)
    elif lower_filename.endswith(".docx"):
        text = parse_docx(file_bytes)
    elif lower_filename.endswith(".txt"):
        text = file_bytes.decode("utf-8", errors="ignore").strip()
    
    if not text:
        # Fallback to UTF-8 decoding if direct format parsing returned empty string
        try:
            text = file_bytes.decode("utf-8", errors="ignore").strip()
        except Exception:
            text = ""
            
    return text
