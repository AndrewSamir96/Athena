from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
	__tablename__ = "users"

	id: Mapped[UUID] = mapped_column(
		PostgreSQLUUID(as_uuid=True),
		primary_key=True,
		server_default=text("gen_random_uuid()"),
	)
	email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
	hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=text("now()"), nullable=False
	)

	notes: Mapped[list["Note"]] = relationship(
		back_populates="user", cascade="all, delete-orphan"
	)
	messages: Mapped[list["ChatMessage"]] = relationship(
		back_populates="user", cascade="all, delete-orphan"
	)
