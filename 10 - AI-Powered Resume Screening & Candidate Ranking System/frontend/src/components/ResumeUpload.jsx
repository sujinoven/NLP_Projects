import React, { useRef, useState } from 'react';
import { UploadCloud, File, X, Trash2 } from 'lucide-react';

export default function ResumeUpload({ resumes, setResumes }) {
  const fileInputRef = useRef(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFilesAdded = (newFiles) => {
    const validFiles = Array.from(newFiles).filter((file) => {
      const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
      return ['.pdf', '.docx', '.txt'].includes(ext);
    });

    setResumes((prev) => {
      const existingNames = new Set(prev.map((f) => f.name));
      const filtered = validFiles.filter((f) => !existingNames.has(f.name));
      return [...prev, ...filtered];
    });
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files) {
      handleFilesAdded(e.dataTransfer.files);
    }
  };

  const removeFile = (index) => {
    setResumes((prev) => prev.filter((_, i) => i !== index));
  };

  const clearAll = () => {
    setResumes([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Resumes</h2>
        <span className="card-badge">
          {resumes.length} {resumes.length === 1 ? 'file' : 'files'} selected
        </span>
      </div>

      <div
        className={`dropzone ${isDragOver ? 'active' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        tabIndex={0}
        role="button"
        aria-label="Drag and drop resumes or click to choose files"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
      >
        <UploadCloud style={{ width: 28, height: 28, margin: '0 auto 8px', color: '#2563eb' }} />
        <p className="dropzone-text">Drag & drop candidate resumes here</p>
        <p className="dropzone-hint">Accepts multiple .pdf, .docx, or .txt files</p>

        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            fileInputRef.current?.click();
          }}
          className="btn btn-secondary"
          style={{ padding: '6px 14px', fontSize: '0.8125rem', marginTop: '4px' }}
        >
          Choose files
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt"
          onChange={(e) => e.target.files && handleFilesAdded(e.target.files)}
          style={{ display: 'none' }}
        />
      </div>

      {resumes.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyBetween: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#334155' }}>
              Selected Resumes ({resumes.length})
            </span>
            {resumes.length > 1 && (
              <button
                type="button"
                onClick={clearAll}
                className="btn-text-danger"
                style={{ marginLeft: 'auto' }}
              >
                Clear all
              </button>
            )}
          </div>

          <div className="file-list">
            {resumes.map((file, idx) => (
              <div key={`${file.name}-${idx}`} className="file-item">
                <div className="file-info">
                  <File style={{ width: 15, height: 15, color: '#64748b', flexShrink: 0 }} />
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">({(file.size / 1024).toFixed(1)} KB)</span>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(idx)}
                  className="btn-remove"
                  aria-label={`Remove file ${file.name}`}
                  title="Remove resume"
                >
                  <X style={{ width: 15, height: 15 }} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
