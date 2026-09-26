import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import client from '../api/client';

export default function NotesListPage() {
  const [notes, setNotes] = useState(null); // null = "still loading"
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    client
      .get('/notes')
      .then(({ data }) => {
        if (!cancelled) setNotes(data);
      })
      .catch(() => {
        if (!cancelled) setError('Could not load your notes.');
      });

    return () => {
      cancelled = true; // avoid setting state after the component unmounts
    };
  }, []);

  return (
    <div className="content">
      <div className="section-header">
        <h2>Your notes</h2>
      </div>

      {error && <div className="form-error">{error}</div>}

      {notes === null && !error && <p>Loading…</p>}

      {notes?.length === 0 && (
        <div className="empty-state">
          <p>No notes yet</p>
          <p>
            <Link to="/notes/upload">Upload your first note</Link> to start chatting with it.
          </p>
        </div>
      )}

      {notes?.map((note) => (
        <div className="note-row" key={note.id}>
          <div>
            <div className="note-title">{note.title}</div>
            <div className="note-meta">
              Added {new Date(note.created_at).toLocaleDateString()}
            </div>
          </div>
          <span className={`status-pill ${note.status}`}>{note.status}</span>
        </div>
      ))}
    </div>
  );
}
