import React, { useState } from 'react';
import Header from './components/Header';
import JobDescriptionInput from './components/JobDescriptionInput';
import ResumeUpload from './components/ResumeUpload';
import ScreeningControls from './components/ScreeningControls';
import ResultsTable from './components/ResultsTable';
import CandidateDetailModal from './components/CandidateDetailModal';
import { screenResumes } from './services/api';

export default function App() {
  const [jdText, setJdText] = useState('');
  const [jdFile, setJdFile] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  const hasJD = Boolean(jdFile) || Boolean(jdText && jdText.trim());
  const hasResumes = resumes.length > 0;
  const isSubmissionDisabled = !hasJD || !hasResumes;

  const handleScreening = async () => {
    if (!hasJD) {
      setError('Please provide a Job Description by pasting text or uploading a file.');
      return;
    }
    if (!hasResumes) {
      setError('Please upload at least one candidate resume file.');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const data = await screenResumes({
        jdText,
        jdFile,
        resumes,
        topK,
      });
      setResults(data);
    } catch (err) {
      console.error('Screening failed:', err);
      const detail = err.response?.data?.detail || err.message || 'Screening request failed. Please check backend connection and inputs.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* 1. Header */}
      <Header />

      <main>
        {/* 2. Input Area: 2 Cards side-by-side on desktop, stacked on mobile */}
        <div className="card-grid">
          <JobDescriptionInput
            jdText={jdText}
            setJdText={setJdText}
            jdFile={jdFile}
            setJdFile={setJdFile}
          />
          <ResumeUpload
            resumes={resumes}
            setResumes={setResumes}
          />
        </div>

        {/* 3. Screening Controls */}
        <ScreeningControls
          topK={topK}
          setTopK={setTopK}
          onScreen={handleScreening}
          loading={loading}
          disabled={isSubmissionDisabled}
          error={error}
        />

        {/* 4. Results Section */}
        {results && (
          <ResultsTable
            results={results}
            onSelectCandidate={(cand) => setSelectedCandidate(cand)}
          />
        )}
      </main>

      {/* 5. Candidate Details Modal / Panel */}
      {selectedCandidate && (
        <CandidateDetailModal
          candidate={selectedCandidate}
          onClose={() => setSelectedCandidate(null)}
        />
      )}
    </div>
  );
}
