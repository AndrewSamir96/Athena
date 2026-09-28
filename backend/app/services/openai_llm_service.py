from app.models import NoteChunk
from app.schemas.chat import Citation
from openai import OpenAI

client = OpenAI()


def embed_texts(texts: list[str]) -> list[list[float]]:
    print(f"[llm.embed_texts] count={len(texts)}")
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    embeddings = [data.embedding for data in response.data]
    print(f"[llm.embed_texts] received={len(embeddings)}")
    return embeddings


def build_prompt(question: str, chunks: list[NoteChunk]) -> str:
    print(f"[llm.build_prompt] question_length={len(question)} chunks={len(chunks)}")
    sources = "\n\n".join(
        f'[Source {i + 1}: "{chunk.note.title}", chunk {chunk.chunk_index}]\n{chunk.content}'
        for i, chunk in enumerate(chunks)
    )
    prompt = (
        f"{sources}\n\n"
        f"Answer the question using only the sources above. Cite the source number "
        f"after each claim. If the sources don't contain the answer, say so explicitly.\n\n"
        f"Question: {question}"
    )
    print(f"[llm.build_prompt] prompt_length={len(prompt)}")
    return prompt


def generate_answer(
    question: str, chunks: list[NoteChunk]
) -> tuple[str, list[Citation]]:
    print(f"[llm.generate_answer] question_length={len(question)} chunks={len(chunks)}")
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
    print(
        f"[llm.generate_answer] answer_length={len(answer)} citations={len(citations)}"
    )
    return answer, citations
