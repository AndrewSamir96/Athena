"""Use the dimension returned by the active Ollama embedding model.

Revision ID: 0002_use_768_dimensional_embeddings
Revises: 0001_initial_schema
"""

from typing import Sequence, Union

from alembic import op
from pgvector.sqlalchemy import Vector


revision: str = "0002_embedding_dim_768"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_note_chunks_embedding_hnsw", table_name="note_chunks")
    op.alter_column(
        "note_chunks",
        "embedding",
        existing_type=Vector(dim=1536),
        type_=Vector(dim=768),
        existing_nullable=False,
        postgresql_using="embedding::vector(768)",
    )
    op.create_index(
        "ix_note_chunks_embedding_hnsw",
        "note_chunks",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_note_chunks_embedding_hnsw", table_name="note_chunks")
    op.alter_column(
        "note_chunks",
        "embedding",
        existing_type=Vector(dim=768),
        type_=Vector(dim=1536),
        existing_nullable=False,
        postgresql_using="embedding::vector(1536)",
    )
    op.create_index(
        "ix_note_chunks_embedding_hnsw",
        "note_chunks",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
