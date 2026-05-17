# backend/app/models.py
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from backend.app.database import Base

EMBED_DIM = 768  # nomic-embed-text output dimension


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                                          default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(512))
    domain: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document",
                                                  cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                                          default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"))
    content: Mapped[str] = mapped_column(Text)
    embedding = mapped_column(Vector(EMBED_DIM))
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)
    document: Mapped["Document"] = relationship(back_populates="chunks")

    # Full-text search index (powers BM25 keyword retrieval)
    __table_args__ = (
        Index("ix_chunks_fts", "content",
              postgresql_using="gin",
              postgresql_ops={"content": "gin_trgm_ops"}),
    )


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                                          default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str | None] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
