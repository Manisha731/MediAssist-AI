import { useEffect, useRef, useState } from 'react';

const GENERAL_DISCLAIMER =
  'This is an AI-generated summary for informational purposes only. It is not medical advice. Always consult a healthcare provider before making treatment decisions.';

const DRUG_DISCLAIMER =
  'Interaction data is not exhaustive. Do not start, stop, or change any medication without consulting your doctor or pharmacist.';

const cleanDrugNames = (text) =>
  text
    .split(',')
    .map((d) => d.trim().replace(/[.;]+$/, ''))
    .filter(Boolean)
    .join(',');

const formatElapsed = (seconds) =>
  `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;

function UploadReport() {
  const [file, setFile] = useState(null);
  const [drugNames, setDrugNames] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [usedDrugs, setUsedDrugs] = useState(false);
  const [error, setError] = useState('');
  const [elapsed, setElapsed] = useState(0);
  const resultsRef = useRef(null);

  // Elapsed-time counter: the only progress the backend lets us report honestly.
  useEffect(() => {
    if (!loading) return undefined;
    const start = Date.now();
    const id = setInterval(() => {
      setElapsed(Math.floor((Date.now() - start) / 1000));
    }, 1000);
    return () => clearInterval(id);
  }, [loading]);

  // Bring new results into view and move focus there for keyboard/screen-reader users.
  useEffect(() => {
    if (!result || !resultsRef.current) return;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    resultsRef.current.focus({ preventScroll: true });
    resultsRef.current.scrollIntoView({
      behavior: reduceMotion ? 'auto' : 'smooth',
      block: 'start',
    });
  }, [result]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    const cleaned = cleanDrugNames(drugNames);

    setElapsed(0);
    setLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(
        `http://localhost:8000/process-report?drug_names=${encodeURIComponent(cleaned)}`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error('The server could not process this report.');
      }

      const data = await response.json();
      setResult(data);
      setUsedDrugs(cleaned.length > 0);
    } catch (err) {
      if (err.message === 'Failed to fetch') {
        setError(
          'Could not get a response. The server or the AI service may be busy. Please wait a minute and try again.'
        );
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-stack">
      <div className="card">
        <h1>Upload a medical report</h1>
        <p className="lead">
          Choose a PDF and, if you like, list your medications. You will get a
          plain-language summary and explanation.
        </p>
        <form className="form" onSubmit={handleUpload}>
          <fieldset className="fieldset" disabled={loading}>
            <div className="form-group">
              <label className="label" htmlFor="report-file">Medical report (PDF)</label>
              <div className="file-field">
                <input
                  id="report-file"
                  type="file"
                  accept="application/pdf"
                  aria-describedby="report-file-name"
                  onChange={(e) => setFile(e.target.files[0] || null)}
                  required
                />
                <label htmlFor="report-file" className="button button-secondary">
                  {file ? 'Change file' : 'Choose PDF'}
                </label>
                <span
                  id="report-file-name"
                  className={file ? 'file-name file-name--chosen' : 'file-name'}
                >
                  {file ? file.name : 'No file chosen'}
                </span>
              </div>
            </div>
            <div className="form-group">
              <label className="label" htmlFor="drug-names">
                Medications <span className="optional">(optional)</span>
              </label>
              <input
                id="drug-names"
                className="input"
                type="text"
                autoComplete="off"
                aria-describedby="drug-names-help"
                placeholder="e.g. warfarin, ibuprofen"
                value={drugNames}
                onChange={(e) => setDrugNames(e.target.value)}
              />
              <span id="drug-names-help" className="helper-text">
                Separate medications with commas. We will also check them for known interactions.
              </span>
            </div>
          </fieldset>
          <div aria-live="polite">
            {error && <p className="error-banner banner-in">{error}</p>}
          </div>
          <button
            type="submit"
            className="button button-primary button-block"
            disabled={loading}
            aria-busy={loading}
          >
            {loading && <span className="spinner spinner--small" aria-hidden="true" />}
            {loading ? 'Analyzing…' : 'Upload & analyze'}
          </button>
        </form>

        {loading && (
          <div className="progress-panel banner-in">
            <p className="progress-text" role="status">
              Analyzing your report. This can take up to a minute, so please keep this page open.
            </p>
            <div className="progress-track" aria-hidden="true">
              <div className="progress-bar" />
            </div>
            <p className="progress-time" aria-hidden="true">
              Time elapsed: <span className="progress-clock">{formatElapsed(elapsed)}</span>
            </p>
          </div>
        )}
      </div>

      <div className="visually-hidden" role="status">
        {result ? 'Your results are ready.' : ''}
      </div>

      {result && (
        <section
          ref={resultsRef}
          className="results"
          tabIndex={-1}
          aria-labelledby="results-title"
        >
          <h2 id="results-title" className="results-title">Your results</h2>

          <article className="card result-card reveal">
            <h3>Summary</h3>
            <p className="result-text">{result.summary}</p>
            <p className="disclaimer disclaimer--muted">{GENERAL_DISCLAIMER}</p>
          </article>

          <article className="card result-card reveal reveal--2">
            <h3>Final explanation</h3>
            <p className="result-text">{result.final_explanation}</p>
            <p className="disclaimer disclaimer--muted">{GENERAL_DISCLAIMER}</p>
          </article>

          {usedDrugs && (
            <div className="disclaimer disclaimer--prominent reveal--now" role="note">
              <svg className="notice-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M12 3 2 21h20L12 3Z"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinejoin="round"
                />
                <path d="M12 10v5M12 17.5v.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <p>{DRUG_DISCLAIMER}</p>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default UploadReport;