from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from app.database import Base
from sqlalchemy import DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
	from app.models.chunk import NoteChunk
	from app.models.user import User


class Note(Base):
	__tablename__ = "notes"

	id: Mapped[UUID] = mapped_column(
		PostgreSQLUUID(as_uuid=True),
		primary_key=True,
		server_default=text("gen_random_uuid()"),
	)
	user_id: Mapped[UUID] = mapped_column(
		PostgreSQLUUID(as_uuid=True),
		ForeignKey("users.id", ondelete="CASCADE"),
		nullable=False,
	)
	title: Mapped[str] = mapped_column(String(255), nullable=False)
	status: Mapped[str] = mapped_column(String(20), nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=text("now()"), nullable=False
	)

	user: Mapped["User"] = relationship(back_populates="notes")
	chunks: Mapped[list["NoteChunk"]] = relationship(
		back_populates="note", cascade="all, delete-orphan"
	)
