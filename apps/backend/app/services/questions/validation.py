from app.models.question import QuestionType
from app.schemas.question import GeneratedQuestionItem, QuestionCandidateValidation


class QuestionValidator:
    def validate(self, candidate: GeneratedQuestionItem) -> QuestionCandidateValidation:
        checks: dict[str, bool] = {
            "has_stem": len(candidate.stem.strip()) >= 20,
            "has_answer": bool(candidate.answer),
            "has_source_reference": bool(candidate.source_references),
            "difficulty_in_range": -4.0 <= candidate.difficulty <= 4.0,
        }

        if candidate.type == QuestionType.mcq:
            choices = candidate.answer.get("choices", [])
            correct_option = candidate.answer.get("correct_option")
            checks["mcq_has_four_choices"] = isinstance(choices, list) and len(choices) == 4
            checks["mcq_has_valid_correct_option"] = correct_option in {"A", "B", "C", "D"}

        if candidate.type == QuestionType.open_ended:
            checks["has_rubric_criteria"] = bool(candidate.rubric.get("criteria"))

        passed = all(checks.values())
        confidence = round(sum(1 for value in checks.values() if value) / len(checks), 2)
        notes = None if passed else "Candidate failed one or more deterministic validation checks."
        return QuestionCandidateValidation(
            passed=passed,
            confidence=confidence,
            checks=checks,
            notes=notes,
        )
