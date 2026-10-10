import React from 'react';
import { Loader2, Play } from 'lucide-react';

export default function ScreeningControls({ topK, setTopK, onScreen, loading, disabled, error }) {
  return (
    <div style={{ marginBottom: '32px' }}>
      {error && (
        <div className="error-banner" role="alert">
          <span>{error}</span>
        </div>
      )}

      <div className="controls-card">
        <div className="controls-left">
          <label htmlFor="shortlist-size-input" className="form-label" style={{ marginBottom: 0 }}>
            Shortlist size:
          </label>
          <input
            id="shortlist-size-input"
            type="number"
            min={1}
            max={100}
            value={topK}
            onChange={(e) => {
              const val = parseInt(e.target.value, 10);
              setTopK(isNaN(val) || val < 1 ? 1 : val);
            }}
            className="form-input"
            style={{ width: '80px', textAlign: 'center' }}
            disabled={loading}
          />
        </div>

        <button
          type="button"
          onClick={onScreen}
          disabled={disabled || loading}
          className="btn btn-primary"
          style={{ width: '100%', maxWidth: '220px' }}
        >
          {loading ? (
            <>
              <Loader2 className="spinner" style={{ width: 16, height: 16 }} />
              Screening resumes...
            </>
          ) : (
            <>
              <Play style={{ width: 16, height: 16, fill: 'currentColor' }} />
              Screen resumes
            </>
          )}
        </button>
      </div>
    </div>
  );
}
