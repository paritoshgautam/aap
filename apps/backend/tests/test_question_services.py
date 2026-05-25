from app.models.question import QuestionType
from app.schemas.question import GeneratedQuestionItem
from app.services.questions.embeddings import cosine_similarity
from app.services.questions.fingerprinting import StructuralFingerprinter
from app.services.questions.validation import QuestionValidator


def test_structural_fingerprint_normalizes_numbers() -> None:
    fingerprinter = StructuralFingerprinter()
    left = fingerprinter.fingerprint("Calculate the pH of 0.10 M HCl.", {"value": "1"})
    right = fingerprinter.fingerprint("Calculate the pH of 0.20 M HCl.", {"value": "1"})

    assert left == right


def test_question_validator_rejects_invalid_mcq() -> None:
    candidate = GeneratedQuestionItem(
        type=QuestionType.mcq,
        stem="Which statement best explains equilibrium behavior?",
        answer={"choices": ["A", "B"], "correct_option": "E"},
        source_references=[{"source_chunk_id": "chunk-1"}],
        difficulty=0.0,
    )

    validation = QuestionValidator().validate(candidate)

    assert not validation.passed
    assert not validation.checks["mcq_has_four_choices"]


def test_cosine_similarity_identifies_same_direction() -> None:
    assert cosine_similarity([1, 0, 1], [1, 0, 1]) > 0.999
