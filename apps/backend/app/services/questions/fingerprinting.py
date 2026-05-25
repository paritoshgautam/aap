import hashlib
import re


class StructuralFingerprinter:
    number_pattern = re.compile(r"\b\d+(\.\d+)?\b")
    whitespace_pattern = re.compile(r"\s+")
    punctuation_pattern = re.compile(r"[^a-z0-9\s_\[\]]")

    def canonicalize(self, stem: str) -> str:
        value = stem.lower().strip()
        value = self.number_pattern.sub("[number]", value)
        value = self.punctuation_pattern.sub(" ", value)
        value = self.whitespace_pattern.sub(" ", value)
        return value.strip()

    def fingerprint(self, stem: str, answer: dict) -> str:
        answer_key = ""
        if isinstance(answer, dict):
            answer_key = str(answer.get("correct_option") or answer.get("value") or answer.get("summary") or "")
        payload = f"{self.canonicalize(stem)}::{answer_key.lower().strip()}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
