import { useState } from 'react';

function Signup({ onSignupSuccess, onSwitch }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Signup failed. Try a different email.');
      }

      onSignupSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h1>Create your account</h1>
      <p className="lead">Sign up to start analyzing your reports.</p>
      <form className="form" onSubmit={handleSignup}>
        <fieldset className="fieldset" disabled={loading}>
          <div className="form-group">
            <label className="label" htmlFor="signup-email">Email</label>
            <input
              id="signup-email"
              className="input"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label className="label" htmlFor="signup-password">Password</label>
            <input
              id="signup-password"
              className="input"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
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
          {loading ? 'Creating account…' : 'Sign up'}
        </button>
      </form>
      <p className="switch-line">
        Already have an account?{' '}
        <button type="button" className="button-link" onClick={onSwitch}>Log in</button>
      </p>
    </div>
  );
}

export default Signup;
