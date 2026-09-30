import os
import fitz
import pytesseract
from PIL import Image

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from normal PDFs first. If a page has little/no text,
    render the page and run Tesseract OCR on it.
    """
    document = fitz.open(pdf_path)
    pages = []

    for page in document:
        text = page.get_text("text").strip()

        if len(text) < 30:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(image)

        pages.append(text.strip())

    document.close()
    return "\n\n".join(p for p in pages if p)
