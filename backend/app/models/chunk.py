from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from app.database import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
	from app.models.note import Note


class NoteChunk(Base):
	__tablename__ = "note_chunks"

	id: Mapped[UUID] = mapped_column(
		PostgreSQLUUID(as_uuid=True),
		primary_key=True,
		server_default=text("gen_random_uuid()"),
	)
	note_id: Mapped[UUID] = mapped_column(
		PostgreSQLUUID(as_uuid=True),
		ForeignKey("notes.id", ondelete="CASCADE"),
		nullable=False,
	)
	chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
	content: Mapped[str] = mapped_column(Text, nullable=False)
	embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)

	note: Mapped["Note"] = relationship(back_populates="chunks")
