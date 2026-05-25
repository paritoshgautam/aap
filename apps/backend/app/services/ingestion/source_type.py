from pathlib import Path


def detect_source_type(filename: str, text: str) -> str:
    name = Path(filename).stem.lower()
    sample = text[:4000].lower()
    combined = f"{name} {sample}"

    rules = [
        ("slides", ["slides", "slide deck", "presentation", "pptx"]),
        ("syllabus", ["syllabus", "guide", "assessment objectives", "curriculum outline"]),
        ("formula_sheet", ["formula", "data booklet", "equation", "constants", "periodic table"]),
        ("practice_guide", ["practice", "question", "markscheme", "mark scheme", "worked example"]),
        ("review_notes", ["review", "notes", "summary", "revision", "study guide"]),
    ]
    for source_type, terms in rules:
        if any(term in combined for term in terms):
            return source_type
    return "review_notes"
