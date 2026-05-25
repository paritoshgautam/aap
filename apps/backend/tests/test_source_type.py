from app.services.ingestion.source_type import detect_source_type


def test_detect_source_type_from_filename() -> None:
    assert detect_source_type("IB Chemistry Formula Sheet.pdf", "") == "formula_sheet"
    assert detect_source_type("physics-syllabus.docx", "") == "syllabus"
    assert detect_source_type("Stoichiometry Slides.pdf", "") == "slides"


def test_detect_source_type_defaults_to_review_notes() -> None:
    assert detect_source_type("chapter-1.pdf", "Atomic structure summary and revision notes") == "review_notes"
