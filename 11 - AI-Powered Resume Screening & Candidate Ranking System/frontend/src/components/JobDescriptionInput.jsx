import React, { useRef } from 'react';
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react';

export default function JobDescriptionInput({ jdText, setJdText, jdFile, setJdFile }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setJdFile(e.target.files[0]);
    }
  };

  const removeFile = () => {
    setJdFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Job Description</h2>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <label htmlFor="jd-text-input" className="form-label">
          Job Description Text
        </label>
        <textarea
          id="jd-text-input"
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
          placeholder="Paste job description requirements, role responsibilities, and required skills here..."
          className="form-textarea"
          rows={6}
          disabled={Boolean(jdFile)}
        />
      </div>

      <div>
        <label htmlFor="jd-file-input" className="form-label">
          Or Upload Job Description File
        </label>
        {!jdFile ? (
          <div
            className="dropzone"
            onClick={() => fileInputRef.current?.click()}
            tabIndex={0}
            role="button"
            aria-label="Upload Job Description file"
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                fileInputRef.current?.click();
              }
            }}
          >
            <Upload style={{ width: 20, height: 20, margin: '0 auto 8px', color: '#64748b' }} />
            <p className="dropzone-text">Click or drop file here to upload</p>
            <p className="dropzone-hint">Supports .pdf, .docx, or .txt</p>
            <input
              ref={fileInputRef}
              id="jd-file-input"
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
          </div>
        ) : (
          <div className="file-item" style={{ backgroundColor: '#eff6ff', borderColor: '#bfdbfe' }}>
            <div className="file-info">
              <FileText style={{ width: 16, height: 16, color: '#2563eb', flexShrink: 0 }} />
              <span className="file-name" style={{ color: '#1e3a8a' }}>{jdFile.name}</span>
              <span className="file-size">({(jdFile.size / 1024).toFixed(1)} KB)</span>
            </div>
            <button
              type="button"
              onClick={removeFile}
              className="btn-remove"
              aria-label="Remove uploaded job description file"
              title="Remove file"
            >
              <X style={{ width: 16, height: 16 }} />
            </button>
          </div>
        )}
      </div>

      {/* Clear indication of which input will be used */}
      {jdFile ? (
        <div className="input-indicator file-active">
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <CheckCircle style={{ width: 15, height: 15, color: '#2563eb' }} />
            Using uploaded file: <strong>{jdFile.name}</strong> (Pasted text is ignored)
          </span>
          <button
            type="button"
            onClick={removeFile}
            className="btn-text-danger"
          >
            Use pasted text
          </button>
        </div>
      ) : jdText.trim() ? (
        <div className="input-indicator text-active">
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <CheckCircle style={{ width: 15, height: 15, color: '#16a34a' }} />
            Using pasted job description text
          </span>
        </div>
      ) : (
        <div className="input-indicator empty-active">
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertCircle style={{ width: 15, height: 15, color: '#94a3b8' }} />
            Please paste text or upload a file above
          </span>
        </div>
      )}
    </div>
  );
}
