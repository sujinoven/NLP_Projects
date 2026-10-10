import React from 'react';
import { Download, AlertTriangle, Info } from 'lucide-react';

export default function ResultsTable({ results, onSelectCandidate }) {
  if (!results) return null;

  const { shortlist = [], unscored_resumes = [], file_errors = [], total_resumes_processed = 0 } = results;

  const downloadCSV = () => {
    if (!shortlist || shortlist.length === 0) return;

    const headers = ["Rank", "Candidate Name", "File Name", "Relative Score", "Raw Score", "Email", "Phone", "LinkedIn", "GitHub"];
    const rows = shortlist.map((c) => [
      c.rank,
      `"${c.candidate_name || 'N/A'}"`,
      `"${c.file_name}"`,
      c.fit_score !== null ? c.fit_score : "N/A",
      c.raw_score !== null ? c.raw_score.toFixed(4) : "N/A",
      `"${c.contact?.email || ''}"`,
      `"${c.contact?.phone || ''}"`,
      `"${c.contact?.linkedin || ''}"`,
      `"${c.contact?.github || ''}"`
    ]);

    const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `resume_screening_results_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="results-card">
      <div className="results-header">
        <div>
          <h2 className="card-title">Screening Results</h2>
          <p className="app-subtitle" style={{ fontSize: '0.8125rem', marginTop: '2px' }}>
            Screened {total_resumes_processed} {total_resumes_processed === 1 ? 'resume' : 'resumes'}. Showing top {shortlist.length} candidate matches.
          </p>
        </div>

        <button
          type="button"
          onClick={downloadCSV}
          className="btn btn-secondary"
          style={{ padding: '8px 14px', fontSize: '0.8125rem' }}
          disabled={shortlist.length === 0}
        >
          <Download style={{ width: 15, height: 15 }} />
          Download CSV
        </button>
      </div>

      {shortlist.length > 0 ? (
        <div className="table-container">
          <table className="clean-table">
            <thead>
              <tr>
                <th style={{ width: '80px' }}>Rank</th>
                <th>Candidate / Filename</th>
                <th>
                  <div>Relative score</div>
                  <div className="subtext-note" style={{ fontWeight: 400, fontSize: '0.75rem', color: '#64748b' }}>
                    Relative scores compare candidates within this upload.
                  </div>
                </th>
                <th style={{ textAlignment: 'right', width: '120px' }}>View details</th>
              </tr>
            </thead>
            <tbody>
              {shortlist.map((candidate) => (
                <tr key={candidate.file_name}>
                  <td>
                    <span className={`rank-badge ${candidate.rank <= 3 ? 'top-rank' : ''}`}>
                      {candidate.rank}
                    </span>
                  </td>
                  <td>
                    <div style={{ fontWeight: 600, color: '#0f172a' }}>
                      {candidate.candidate_name || candidate.file_name}
                    </div>
                    {candidate.candidate_name && (
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        {candidate.file_name}
                      </div>
                    )}
                  </td>
                  <td>
                    <div className="score-container">
                      <div className="score-bar-track">
                        <div
                          className="score-bar-fill"
                          style={{ width: `${candidate.fit_score ?? 0}%` }}
                        />
                      </div>
                      <span className="score-value">
                        {candidate.fit_score !== null && candidate.fit_score !== undefined
                          ? `${candidate.fit_score}%`
                          : 'N/A'}
                      </span>
                    </div>
                  </td>
                  <td>
                    <button
                      type="button"
                      onClick={() => onSelectCandidate(candidate)}
                      className="btn btn-secondary"
                      style={{ padding: '6px 12px', fontSize: '0.75rem' }}
                    >
                      View details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ padding: '24px', textAlign: 'center', color: '#64748b', fontSize: '0.875rem' }}>
          No candidates met the shortlist scoring criteria.
        </div>
      )}

      {/* Unscored or Failed Files Section */}
      {(unscored_resumes.length > 0 || file_errors.length > 0) && (
        <div className="unscored-card">
          <div className="unscored-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertTriangle style={{ width: 16, height: 16 }} />
            Unscored or Failed Files ({unscored_resumes.length + file_errors.length})
          </div>

          {unscored_resumes.map((u) => (
            <div key={u.file_name} className="unscored-item">
              <span style={{ fontWeight: 500 }}>{u.file_name}</span>
              <span style={{ color: '#b45309' }}>
                {u.unscored_reason || 'Unable to calculate similarity score'}
              </span>
            </div>
          ))}

          {file_errors.map((e) => (
            <div key={e.file_name} className="unscored-item" style={{ borderColor: '#fecaca' }}>
              <span style={{ fontWeight: 500 }}>{e.file_name}</span>
              <span style={{ color: '#dc2626' }}>{e.error}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
