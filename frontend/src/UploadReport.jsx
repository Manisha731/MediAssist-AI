import { useState } from 'react';

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

function UploadReport() {
  const [file, setFile] = useState(null);
  const [drugNames, setDrugNames] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [usedDrugs, setUsedDrugs] = useState(false);
  const [error, setError] = useState('');

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    const cleaned = cleanDrugNames(drugNames);

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
    <div>
      <h2>Upload a Medical Report</h2>
      <form onSubmit={handleUpload}>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files[0])}
          required
        />
        <input
          type="text"
          placeholder="Medications (comma-separated, e.g. warfarin,ibuprofen)"
          value={drugNames}
          onChange={(e) => setDrugNames(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing... this can take up to a minute' : 'Upload & Analyze'}
        </button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {result && (
        <div>
          <h3>Summary</h3>
          <p style={{ whiteSpace: 'pre-wrap' }}>{result.summary}</p>
          <p style={{ fontSize: '0.85em', color: '#666' }}>{GENERAL_DISCLAIMER}</p>

          <h3>Final Explanation</h3>
          <p style={{ whiteSpace: 'pre-wrap' }}>{result.final_explanation}</p>
          <p style={{ fontSize: '0.85em', color: '#666' }}>{GENERAL_DISCLAIMER}</p>
          {usedDrugs && (
            <p style={{ fontSize: '0.85em', color: '#b00020' }}>{DRUG_DISCLAIMER}</p>
          )}
        </div>
      )}
    </div>
  );
}

export default UploadReport;