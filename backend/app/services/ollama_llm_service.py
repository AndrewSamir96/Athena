import ollama
from app.models import NoteChunk
from app.schemas.chat import Citation

client = ollama.Client(host="http://localhost:11434")


def embed_texts(texts: list[str]) -> list[list[float]]:
    print(f"[llm.embed_texts] count={len(texts)}")
    response = client.embed(
        model="embeddinggemma",
        input=texts,
    )
    embeddings = response.embeddings
    print(f"[llm.embed_texts] received={len(embeddings)}")
    return embeddings


def build_prompt(question: str, chunks: list[NoteChunk]) -> str:
    print(f"[llm.build_prompt] question_length={len(question)} chunks={len(chunks)}")

    sources = "\n\n".join(
        f'[Source {i + 1}: "{chunk.note.title}", chunk {chunk.chunk_index}]\n'
        f"{chunk.content}"
        for i, chunk in enumerate(chunks)
    )
    # Old prompt template:
    # Instructions:
    # 	- Return ONLY the final answer.
    # 	- Do NOT output your reasoning or thinking process.
    # 	- Do NOT analyze the sources step by step.
    # 	- Be concise and directly answer the question.
    # 	- Cite the relevant source number after each factual claim.
    # 	- If the answer cannot be found in the sources, say: "The provided sources do not contain the answer."

    prompt = f"""
	You are a question-answering assistant.

	Use ONLY the sources provided below to answer the question.

	{sources}

	Rules:
	1. Find the answer directly in the sources.
	2. Prefer an explicit statement over calculating or inferring an answer.
	3. Do not perform calculations if the source already provides the requested value.
	4. Do not invent or modify numbers from the sources.
	5. Give only the final answer.
	6. Cite the source number after the answer.
	7. If the answer is not explicitly present in the sources, say that it is not found.
	8. Do not add any markdown formatting to the answer.

	Question:
	{question}

	Final answer:
	"""

    print(f"[llm.build_prompt] prompt_length={len(prompt)}")
    return prompt


def generate_answer(
    question: str, chunks: list[NoteChunk]
) -> tuple[str, list[Citation]]:
    print(f"[llm.generate_answer] question_length={len(question)} chunks={len(chunks)}")

    prompt = build_prompt(question, chunks)

    response = client.chat(
        model="qwen3.5:0.8b",
        messages=[{"role": "user", "content": prompt}],
        think=False,
    )
    answer = response.message.content
    print("content:", repr(response.message.content))
    print("thinking:", repr(response.message.thinking))
    citations = [
        Citation(note_id=chunk.note_id, chunk_id=chunk.id, title=chunk.note.title)
        for chunk in chunks
    ]
    print(
        f"[llm.generate_answer] answer_length={len(answer)} citations={len(citations)}"
    )
    print(f"[llm.generate_answer] LLM ANSWER IS {answer}")
    return answer, citations
