import { useEffect, useRef, useState } from 'react';
import client from '../api/client';

export default function ChatPage() {
  const [messages, setMessages] = useState([]); // { role, content, citations? }
  const [input, setInput] = useState('');
  const [asking, setAsking] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, asking]);

  async function handleSend(e) {
    e.preventDefault();
    const question = input.trim();
    if (!question || asking) return;

    setMessages((prev) => [...prev, { role: 'user', content: question }]);
    setInput('');
    setAsking(true);

    try {
      // Matches POST /chat/ask from the backend guide — swap this for an
      // EventSource call once you build the streaming version in Phase 8.
      const { data } = await client.post('/chat/ask', { question });
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.answer, citations: data.citations },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: "Something went wrong answering that — try again.", error: true },
      ]);
    } finally {
      setAsking(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSend(e);
    }
  }

  return (
    <div className="chat-page">
      <div className="chat-header">
        <h2>Chat</h2>
      </div>

      <div className="chat-scroll" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="chat-empty">
            <p>Ask your notes something</p>
            <p>Answers are grounded only in the notes you've uploaded — with sources.</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div className={`msg-row ${msg.role}`} key={i}>
            <div className="msg-group">
              <div className="msg-bubble">{msg.content}</div>
              {msg.citations?.length > 0 && (
                <div className="msg-citations">
                  {msg.citations.map((c) => (
                    <span className="citation-chip" key={c.chunk_id}>
                      {c.title}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {asking && (
          <div className="msg-row assistant thinking">
            <div className="msg-bubble">Thinking…</div>
          </div>
        )}
      </div>

      <form className="chat-composer" onSubmit={handleSend}>
        <textarea
          rows={1}
          placeholder="Ask a question about your notes…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="chat-send" type="submit" disabled={!input.trim() || asking}>
          Send
        </button>
      </form>
    </div>
  );
}
