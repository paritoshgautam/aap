"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-21
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    user_role = postgresql.ENUM(
        "admin", "teacher", "student", name="user_role", create_type=False
    )
    source_status = postgresql.ENUM(
        "uploaded", "processing", "processed", "failed", name="source_status", create_type=False
    )
    question_type = postgresql.ENUM(
        "mcq", "numeric", "open_ended", "diagram", name="question_type", create_type=False
    )
    question_status = postgresql.ENUM(
        "draft", "validating", "approved", "rejected", name="question_status", create_type=False
    )
    session_status = postgresql.ENUM(
        "active", "completed", "abandoned", name="exam_session_status", create_type=False
    )
    user_role.create(op.get_bind(), checkfirst=True)
    source_status.create(op.get_bind(), checkfirst=True)
    question_type.create(op.get_bind(), checkfirst=True)
    question_status.create(op.get_bind(), checkfirst=True)
    session_status.create(op.get_bind(), checkfirst=True)

    timestamps = [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]

    op.create_table(
        "subjects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(40), nullable=False, unique=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("curriculum", sa.String(60), nullable=False, server_default="IB"),
        *timestamps,
    )
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(260), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(260), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("full_name", sa.String(180)),
        *timestamps,
    )
    op.create_table(
        "units",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subjects.id"), nullable=False),
        sa.Column("code", sa.String(60), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("sequence", sa.Integer, nullable=False, server_default="0"),
        *timestamps,
        sa.UniqueConstraint("subject_id", "code", name="uq_units_subject_code"),
    )
    op.create_table(
        "chapters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("unit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("units.id"), nullable=False),
        sa.Column("code", sa.String(60), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("sequence", sa.Integer, nullable=False, server_default="0"),
        *timestamps,
        sa.UniqueConstraint("unit_id", "code", name="uq_chapters_unit_code"),
    )
    op.create_table(
        "students",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("cohort", sa.String(120)),
        sa.Column("target_exam_date", sa.DateTime(timezone=True)),
        sa.Column("profile_json", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        *timestamps,
    )
    op.create_table(
        "topics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chapters.id")),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("title", sa.String(220), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("difficulty_weight", sa.Numeric(4, 2), nullable=False, server_default="1.0"),
        sa.Column("ib_metadata", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("formulas", postgresql.ARRAY(sa.Text), nullable=False, server_default="{}"),
        sa.Column("misconception_tags", postgresql.ARRAY(sa.String(80)), nullable=False, server_default="{}"),
        sa.Column("mastery_threshold", sa.Numeric(4, 2), nullable=False, server_default="0.8"),
        *timestamps,
        sa.UniqueConstraint("chapter_id", "code", name="uq_topics_chapter_code"),
    )
    op.create_index("ix_topics_code", "topics", ["code"])
    op.create_table(
        "subtopics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("topics.id"), nullable=False),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("title", sa.String(220), nullable=False),
        sa.Column("description", sa.Text),
        *timestamps,
        sa.UniqueConstraint("topic_id", "code", name="uq_subtopics_topic_code"),
    )
    op.create_table(
        "learning_objectives",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("topics.id"), nullable=False),
        sa.Column("subtopic_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subtopics.id")),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("blooms_level", sa.String(40)),
        *timestamps,
        sa.UniqueConstraint("topic_id", "code", name="uq_learning_objectives_topic_code"),
    )
    op.create_table(
        "topic_prerequisites",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("topics.id"), nullable=False),
        sa.Column("prerequisite_topic_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("topics.id"), nullable=False),
        sa.UniqueConstraint("topic_id", "prerequisite_topic_id", name="uq_topic_prerequisite_relation"),
    )
    op.create_table(
        "curriculum_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subjects.id")),
        sa.Column("filename", sa.String(260), nullable=False),
        sa.Column("content_type", sa.String(120), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("status", source_status, nullable=False, server_default="uploaded"),
        sa.Column("extracted_text_hash", sa.String(128)),
        sa.Column("metadata_json", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("processed_at", sa.DateTime(timezone=True)),
        *timestamps,
    )
    op.create_table(
        "source_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_sources.id"), nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("token_estimate", sa.Integer, nullable=False),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("topics.id")),
        sa.Column("metadata_json", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        *timestamps,
        sa.UniqueConstraint("source_id", "chunk_index", name="uq_source_chunks_source_index"),
    )
    op.create_index("ix_source_chunks_source_id", "source_chunks", ["source_id"])
    op.create_table(
        "questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("topics.id"), nullable=False),
        sa.Column("subtopic_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subtopics.id")),
        sa.Column("learning_objective_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("learning_objectives.id")),
        sa.Column("type", question_type, nullable=False),
        sa.Column("status", question_status, nullable=False, server_default="draft"),
        sa.Column("stem", sa.Text, nullable=False),
        sa.Column("answer", postgresql.JSONB, nullable=False),
        sa.Column("rubric", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("blooms_level", sa.String(40)),
        sa.Column("difficulty", sa.Numeric(5, 2), nullable=False, server_default="0.0"),
        sa.Column("discrimination", sa.Numeric(5, 2), nullable=False, server_default="1.0"),
        sa.Column("source_references", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("canonical_fingerprint", sa.String(128), nullable=False, unique=True),
        sa.Column("generation_metadata", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        *timestamps,
    )
    op.create_index("ix_questions_topic_difficulty", "questions", ["topic_id", "difficulty"])
    op.create_index("ix_questions_status", "questions", ["status"])
    op.create_table(
        "question_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("embedding_model", sa.String(120), nullable=False),
        sa.Column("embedding", postgresql.JSONB, nullable=False),
        *timestamps,
        sa.UniqueConstraint("question_id", "embedding_model", name="uq_question_embedding"),
    )
    op.create_table(
        "generation_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("topics.id")),
        sa.Column("source_chunk_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("source_chunks.id")),
        sa.Column("prompt_name", sa.String(120), nullable=False),
        sa.Column("prompt_version", sa.String(40), nullable=False),
        sa.Column("model", sa.String(120), nullable=False),
        sa.Column("request_json", postgresql.JSONB, nullable=False),
        sa.Column("response_json", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(40), nullable=False),
        *timestamps,
    )
    op.create_table(
        "question_validation_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("questions.id")),
        sa.Column("checks", postgresql.JSONB, nullable=False),
        sa.Column("passed", sa.Boolean, nullable=False),
        sa.Column("confidence", sa.Numeric(5, 2), nullable=False, server_default="0.0"),
        sa.Column("notes", sa.Text),
        *timestamps,
    )
    op.create_table(
        "exams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("subjects.id"), nullable=False),
        sa.Column("title", sa.String(220), nullable=False),
        sa.Column("config_json", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("duration_seconds", sa.Integer, nullable=False, server_default="3600"),
        *timestamps,
    )
    op.create_table(
        "exam_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("exam_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("exams.id"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("status", session_status, nullable=False),
        sa.Column("ability_estimate", sa.Numeric(6, 3), nullable=False, server_default="0.0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("state_json", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        *timestamps,
    )
    op.create_index("ix_exam_sessions_student_status", "exam_sessions", ["student_id", "status"])
    op.create_table(
        "question_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("exam_sessions.id"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("response_json", postgresql.JSONB, nullable=False),
        sa.Column("is_correct", sa.Boolean),
        sa.Column("score", sa.Numeric(5, 2)),
        sa.Column("time_spent_seconds", sa.Integer),
        sa.Column("flagged_for_review", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("grading_evidence", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        *timestamps,
    )
    op.create_index("ix_question_attempts_student_question", "question_attempts", ["student_id", "question_id"])
    op.create_index("ix_question_attempts_session", "question_attempts", ["session_id"])
    op.create_table(
        "student_topic_mastery",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("topics.id"), nullable=False),
        sa.Column("mastery_score", sa.Numeric(5, 2), nullable=False, server_default="0.0"),
        sa.Column("confidence", sa.Numeric(5, 2), nullable=False, server_default="0.0"),
        sa.Column("exposure_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        *timestamps,
    )
    op.create_index("ix_student_topic_mastery_student", "student_topic_mastery", ["student_id"])
    op.create_table(
        "analytics_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("readiness_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("projected_exam_score", sa.Numeric(5, 2)),
        sa.Column("weak_areas_json", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("topic_mastery_json", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("cognitive_skill_json", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("trend_json", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        *timestamps,
    )


def downgrade() -> None:
    for table in [
        "analytics_snapshots",
        "student_topic_mastery",
        "question_attempts",
        "exam_sessions",
        "exams",
        "question_validation_logs",
        "generation_audit_logs",
        "question_embeddings",
        "questions",
        "source_chunks",
        "curriculum_sources",
        "topic_prerequisites",
        "learning_objectives",
        "subtopics",
        "topics",
        "students",
        "chapters",
        "units",
        "users",
        "subjects",
    ]:
        op.drop_table(table)
    for enum_name in [
        "exam_session_status",
        "question_status",
        "question_type",
        "source_status",
        "user_role",
    ]:
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
