from pathlib import Path

from docx import Document
from pypdf import PdfReader


class UnsupportedUploadTypeError(ValueError):
    pass


class TextExtractor:
    supported_suffixes = {".pdf", ".docx", ".txt", ".md"}

    def extract(self, path: Path, content_type: str) -> str:
        suffix = path.suffix.lower()
        if suffix == ".pdf" or content_type == "application/pdf":
            return self._extract_pdf(path)
        if suffix == ".docx":
            return self._extract_docx(path)
        if suffix in {".txt", ".md"} or content_type.startswith("text/"):
            return path.read_text(encoding="utf-8", errors="ignore")
        raise UnsupportedUploadTypeError(f"Unsupported upload type: {content_type}")

    def _extract_pdf(self, path: Path) -> str:
        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if text.strip():
            return text
        return "[OCR_REQUIRED] No extractable text found. OCR worker integration required."

    def _extract_docx(self, path: Path) -> str:
        document = Document(path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
