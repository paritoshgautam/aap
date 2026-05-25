import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(StrEnum):
    admin = "admin"
    teacher = "teacher"
    student = "student"


class ExamSessionStatus(StrEnum):
    active = "active"
    completed = "completed"
    abandoned = "abandoned"


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(260), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(260), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(180))


class Student(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "students"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    cohort: Mapped[str | None] = mapped_column(String(120))
    target_exam_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    profile_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class Exam(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "exams"

    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    config_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=3600)


class ExamSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "exam_sessions"

    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exams.id"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id"), nullable=False)
    status: Mapped[ExamSessionStatus] = mapped_column(
        Enum(ExamSessionStatus, name="exam_session_status"), nullable=False
    )
    ability_estimate: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False, default=0.0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    state_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    __table_args__ = (Index("ix_exam_sessions_student_status", "student_id", "status"),)


class QuestionAttempt(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "question_attempts"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_sessions.id"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id"), nullable=False)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"), nullable=False)
    response_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_correct: Mapped[bool | None] = mapped_column()
    score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    time_spent_seconds: Mapped[int | None] = mapped_column(Integer)
    flagged_for_review: Mapped[bool] = mapped_column(nullable=False, default=False)
    grading_evidence: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    __table_args__ = (
        Index("ix_question_attempts_student_question", "student_id", "question_id"),
        Index("ix_question_attempts_session", "session_id"),
    )


class StudentTopicMastery(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "student_topic_mastery"

    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id"), nullable=False)
    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id"), nullable=False)
    mastery_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    confidence: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    exposure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (Index("ix_student_topic_mastery_student", "student_id"),)


class AnalyticsSnapshot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "analytics_snapshots"

    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id"), nullable=False)
    readiness_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    projected_exam_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    weak_areas_json: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    topic_mastery_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    cognitive_skill_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    trend_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
