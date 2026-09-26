import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';

export default function UploadPage() {
  const navigate = useNavigate();
  const inputRef = useRef(null);

  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  function handleFiles(fileList) {
    const picked = fileList[0];
    if (picked) setFile(picked);
  }

  async function handleUpload() {
    if (!file) return;
    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      await client.post('/notes/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      navigate('/notes');
    } catch {
      setError('Upload failed. Try again.');
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="content">
      <div className="section-header">
        <h2>Upload a note</h2>
      </div>

      {error && <div className="form-error">{error}</div>}

      <div
        className={`dropzone ${dragging ? 'dragging' : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
      >
        <div>Drop a PDF or text file here, or click to browse</div>
        <div className="dropzone-hint">PDF, TXT, or MD — one file at a time</div>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.txt,.md"
          hidden
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      {file && (
        <div className="selected-file">
          <span>{file.name}</span>
          <button className="link-button" onClick={() => setFile(null)}>
            Remove
          </button>
        </div>
      )}

      <div style={{ marginTop: 20 }}>
        <button className="btn-primary" onClick={handleUpload} disabled={!file || uploading}>
          {uploading ? 'Uploading…' : 'Upload'}
        </button>
      </div>
    </div>
  );
}
