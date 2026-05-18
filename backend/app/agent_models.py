"""
Agent intelligence tables.
These extend the existing Document/Chunk/SearchSession schema.
DO NOT modify existing tables.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    String, Text, DateTime, Float, Boolean, Integer,
    Index, JSON, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from backend.app.database import Base
from backend.app.config import get_settings

EMBED_DIM = get_settings().embed_dim


# ── LAYER 1: Step-Level Traces ─────────────────────────────────────
class AgentTrace(Base):
    """Every single action the agent takes, stored as searchable vector."""
    __tablename__ = "agent_traces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[str] = mapped_column(String(128), index=True)
    task_id: Mapped[str] = mapped_column(String(128), index=True)
    step_number: Mapped[int] = mapped_column(Integer)

    # What the agent did
    action: Mapped[str] = mapped_column(String(100))
    action_args: Mapped[dict] = mapped_column(JSONB, default=dict)
    result: Mapped[str | None] = mapped_column(Text)
    result_summary: Mapped[str | None] = mapped_column(Text)  # compressed result

    # Agent's internal state
    reasoning: Mapped[str | None] = mapped_column(Text)    # thought before action
    confidence: Mapped[float | None] = mapped_column(Float) # stated 0.0–1.0
    model_used: Mapped[str] = mapped_column(String(64))

    # Metrics
    latency_ms: Mapped[float | None] = mapped_column(Float)
    token_count: Mapped[int | None] = mapped_column(Integer)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_msg: Mapped[str | None] = mapped_column(Text)

    # Evaluation (filled by ProcessEvaluator after the fact)
    step_score: Mapped[float | None] = mapped_column(Float)  # 0.0–1.0
    failure_pattern: Mapped[str | None] = mapped_column(String(64))

    # Semantic embedding of (reasoning + action + result) for self-search
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index(
            "ix_traces_embedding",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_ops={"embedding": "vector_cosine_ops"},
            postgresql_with={"lists": "50"},
        ),
    )


# ── Task-Level Outcomes ────────────────────────────────────────────
class TaskOutcome(Base):
    """One record per completed agent task run."""
    __tablename__ = "task_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[str] = mapped_column(String(128), index=True)
    task_description: Mapped[str] = mapped_column(Text)
    task_category: Mapped[str] = mapped_column(String(64), index=True)  # see TASK_CATEGORIES

    total_steps: Mapped[int] = mapped_column(Integer)
    final_success: Mapped[bool] = mapped_column(Boolean)
    quality_score: Mapped[float | None] = mapped_column(Float)  # 0.0–1.0
    dominant_failure: Mapped[str | None] = mapped_column(String(64))
    model_used: Mapped[str] = mapped_column(String(64))
    focus_mode: Mapped[str] = mapped_column(String(32), default="research")

    # Embedding of task description — for capability map lookups
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    traces_json: Mapped[list] = mapped_column(JSON, default=list)  # compressed trace IDs
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ── LAYER 3: Failure Memory ─────────────────────────────────────────
class FailureLesson(Base):
    """Structured lessons extracted from failed or suboptimal tasks."""
    __tablename__ = "failure_lessons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    situation_type: Mapped[str] = mapped_column(String(128))      # "multi-hop research"
    trigger_pattern: Mapped[str] = mapped_column(Text)            # what to match on
    what_failed: Mapped[str] = mapped_column(Text)
    why_it_failed: Mapped[str] = mapped_column(Text)
    better_approach: Mapped[str] = mapped_column(Text)
    example_task: Mapped[str | None] = mapped_column(Text)        # concrete example

    confidence: Mapped[float] = mapped_column(Float, default=0.5) # 0.0–1.0
    validated_count: Mapped[int] = mapped_column(Integer, default=0)  # times lesson helped
    failed_count: Mapped[int] = mapped_column(Integer, default=0)     # times lesson was wrong
    times_retrieved: Mapped[int] = mapped_column(Integer, default=0)

    # Embed trigger_pattern for similarity search
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def reliability_score(self) -> float:
        """Wilson score confidence interval lower bound."""
        n = self.validated_count + self.failed_count
        if n == 0:
            return self.confidence
        p = self.validated_count / n
        z = 1.645  # 90% confidence
        return (p + z*z/(2*n) - z * (p*(1-p)/n + z*z/(4*n*n))**0.5) / (1 + z*z/n)


# ── LAYER 5a: Capability Map ────────────────────────────────────────
class CapabilityRecord(Base):
    """Agent's self-knowledge of performance by task category."""
    __tablename__ = "capability_map"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_category: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_quality: Mapped[float] = mapped_column(Float, default=0.0)
    avg_steps: Mapped[float] = mapped_column(Float, default=0.0)
    most_common_failure: Mapped[str | None] = mapped_column(String(64))
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @property
    def success_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.success_count / self.total_attempts

    @property
    def is_weak(self) -> bool:
        return self.total_attempts >= 3 and self.avg_quality < 0.6


# ── LAYER 5b: Strategy Library ──────────────────────────────────────
class Strategy(Base):
    """Learned task-solving playbooks. Grows over time."""
    __tablename__ = "strategy_library"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trigger_description: Mapped[str] = mapped_column(Text)   # when to apply
    strategy_text: Mapped[str] = mapped_column(Text)         # the actual playbook
    source: Mapped[str] = mapped_column(String(32))          # "agent" | "human" | "evolved"
    success_rate: Mapped[float] = mapped_column(Float, default=0.5)
    sample_size: Mapped[int] = mapped_column(Integer, default=1)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)  # human approved?

    # Embed trigger for retrieval
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── PHASE 4: Digital Twin ───────────────────────────────────────────
class UserCorrection(Base):
    """Every time you override or correct the agent. Training signal."""
    __tablename__ = "user_corrections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[str] = mapped_column(String(128), index=True)
    situation: Mapped[str] = mapped_column(Text)
    agent_approach: Mapped[str] = mapped_column(Text)
    your_approach: Mapped[str] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text)
    domain: Mapped[str] = mapped_column(String(64), default="general")
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PersonalKnowledgeNode(Base):
    """Your personal knowledge graph — topics and their relationships."""
    __tablename__ = "personal_knowledge"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    concept: Mapped[str] = mapped_column(String(256), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    related_concepts: Mapped[list] = mapped_column(JSON, default=list)
    research_count: Mapped[int] = mapped_column(Integer, default=1)  # times you've researched this
    your_notes: Mapped[str | None] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    last_accessed: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
