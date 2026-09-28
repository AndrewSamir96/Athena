from app.models import NoteChunk
from openai import OpenAI

from app.schemas.chat import Citation

client = OpenAI()


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model='text-embedding-3-small',
        input=texts,
    )
    return [data.embedding for data in response.data]


def build_prompt(question: str, chunks: list[NoteChunk]) -> str:
    sources = "\n\n".join(
        f'[Source {i + 1}: "{chunk.note.title}", chunk {chunk.chunk_index}]\n{chunk.content}'
        for i, chunk in enumerate(chunks)
    )
    return (
        f"{sources}\n\n"
        f"Answer the question using only the sources above. Cite the source number "
        f"after each claim. If the sources don't contain the answer, say so explicitly.\n\n"
        f"Question: {question}"
    )


def generate_answer(
    question: str, chunks: list[NoteChunk]
) -> tuple[str, list[Citation]]:
    prompt = build_prompt(question, chunks)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = "".join(block.text for block in response.content if block.type == "text")

    citations = [
        Citation(note_id=chunk.note_id, chunk_id=chunk.id, title=chunk.note.title)
        for chunk in chunks
    ]
    return answer, citations
