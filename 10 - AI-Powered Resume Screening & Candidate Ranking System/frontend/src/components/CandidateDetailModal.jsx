import React, { useEffect } from 'react';
import { X, Mail, Phone, Globe, Code, Info } from 'lucide-react';

export default function CandidateDetailModal({ candidate, onClose }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!candidate) return null;

  const { rank, file_name, candidate_name, fit_score, raw_score, contact, section_scores, evidence } = candidate;

  // Filter non-empty contact fields
  const hasEmail = Boolean(contact?.email);
  const hasPhone = Boolean(contact?.phone);
  const hasLinkedin = Boolean(contact?.linkedin);
  const hasGithub = Boolean(contact?.github);
  const hasAnyContact = hasEmail || hasPhone || hasLinkedin || hasGithub;

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className="rank-badge top-rank" style={{ fontSize: '0.75rem', width: 'auto', padding: '2px 8px', borderRadius: '4px' }}>
                Rank #{rank}
              </span>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a' }}>
                {candidate_name || file_name}
              </h2>
            </div>
            <p style={{ fontSize: '0.8125rem', color: '#64748b' }}>File: {file_name}</p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="btn-remove"
            aria-label="Close details panel"
            style={{ padding: '6px' }}
          >
            <X style={{ width: 20, height: 20 }} />
          </button>
        </div>

        {/* Contact Information */}
        <div style={{ marginBottom: '24px' }}>
          <div className="section-label">Extracted Contact Information</div>
          {hasAnyContact ? (
            <div className="contact-grid">
              {hasEmail && (
                <div className="contact-box">
                  <div className="contact-title" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Mail style={{ width: 13, height: 13, color: '#2563eb' }} /> Email
                  </div>
                  <div className="contact-detail">{contact.email}</div>
                </div>
              )}
              {hasPhone && (
                <div className="contact-box">
                  <div className="contact-title" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Phone style={{ width: 13, height: 13, color: '#16a34a' }} /> Phone
                  </div>
                  <div className="contact-detail">{contact.phone}</div>
                </div>
              )}
              {hasLinkedin && (
                <div className="contact-box">
                  <div className="contact-title" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Globe style={{ width: 13, height: 13, color: '#2563eb' }} /> LinkedIn
                  </div>
                  <div className="contact-detail">{contact.linkedin}</div>
                </div>
              )}
              {hasGithub && (
                <div className="contact-box">
                  <div className="contact-title" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Code style={{ width: 13, height: 13, color: '#475569' }} /> GitHub
                  </div>
                  <div className="contact-detail">{contact.github}</div>
                </div>
              )}
            </div>
          ) : (
            <p style={{ fontSize: '0.8125rem', color: '#64748b', fontStyle: 'italic' }}>
              No contact information extracted from resume text.
            </p>
          )}
        </div>

        {/* Scores & Metrics */}
        <div style={{ marginBottom: '24px' }}>
          <div className="section-label">Similarity Scores & Section Breakdown</div>
          <div className="scores-grid">
            <div className="score-box">
              <span style={{ fontSize: '0.8125rem', fontWeight: 500, color: '#334155' }}>Relative Score</span>
              <span style={{ fontSize: '0.875rem', fontWeight: 700, color: '#2563eb' }}>
                {fit_score !== null && fit_score !== undefined ? `${fit_score}%` : 'N/A'}
              </span>
            </div>
            <div className="score-box">
              <span style={{ fontSize: '0.8125rem', fontWeight: 500, color: '#334155' }}>Raw Similarity</span>
              <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#0f172a' }}>
                {raw_score !== null && raw_score !== undefined ? raw_score.toFixed(4) : 'N/A'}
              </span>
            </div>
            {Object.entries(section_scores || {}).map(([sec, score]) => (
              <div key={sec} className="score-box">
                <span style={{ fontSize: '0.8125rem', fontWeight: 500, color: '#334155', textTransform: 'capitalize' }}>
                  {sec.replace('_', ' ')}
                </span>
                <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#475569' }}>
                  {score !== null && score !== undefined ? score.toFixed(4) : 'N/A'}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Matching Evidence */}
        <div style={{ marginBottom: '24px' }}>
          <div className="section-label">Matching Evidence</div>
          {evidence && Object.keys(evidence).length > 0 ? (
            Object.entries(evidence).map(([sec, items]) => (
              <div key={sec} className="evidence-group">
                <div className="evidence-header">
                  <span style={{ textTransform: 'capitalize' }}>{sec.replace('_', ' ')} Evidence</span>
                  <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 400 }}>
                    {items?.length || 0} matching {items?.length === 1 ? 'snippet' : 'snippets'}
                  </span>
                </div>
                <div className="evidence-content">
                  {items && items.length > 0 ? (
                    items.map((item, idx) => (
                      <div key={idx} className="evidence-card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.75rem', color: '#64748b' }}>
                          <span>Similarity: <strong>{item.sim?.toFixed(4)}</strong></span>
                          {item.resume_section && <span>Section: {item.resume_section}</span>}
                        </div>
                        <div style={{ marginBottom: '8px' }}>
                          <div className="evidence-label">JD Requirement Snippet:</div>
                          <div className="evidence-text evidence-text-jd">{item.jd_chunk}</div>
                        </div>
                        <div>
                          <div className="evidence-label">Matching Resume Text:</div>
                          <div className="evidence-text">{item.resume_chunk}</div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p style={{ fontSize: '0.8125rem', color: '#64748b', fontStyle: 'italic' }}>
                      No direct matching snippets found for this section.
                    </p>
                  )}
                </div>
              </div>
            ))
          ) : (
            <p style={{ fontSize: '0.8125rem', color: '#64748b', fontStyle: 'italic' }}>
              No matching evidence snippets available.
            </p>
          )}
        </div>

        {/* Mandatory Note */}
        <div className="notice-banner">
          <Info style={{ width: 16, height: 16, flexShrink: 0 }} />
          <span>Review the resume to verify qualifications.</span>
        </div>
      </div>
    </div>
  );
}
