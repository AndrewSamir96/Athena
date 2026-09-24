from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ChatMessage(Base):
	__tablename__ = "chat_messages"

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
	role: Mapped[str] = mapped_column(String(20), nullable=False)
	content: Mapped[str] = mapped_column(Text, nullable=False)
	citations: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=text("now()"), nullable=False
	)

	user: Mapped["User"] = relationship(back_populates="messages")
