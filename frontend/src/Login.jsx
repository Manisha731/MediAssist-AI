import { useState } from 'react';

function Login({ onLoginSuccess, notice, onSwitch }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Invalid email or password');
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      onLoginSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h1>Log in</h1>
      <p className="lead">Welcome back. Log in to analyze a medical report.</p>
      <div aria-live="polite">
        {notice && <p className="success-banner banner-in">{notice}</p>}
      </div>
      <form className="form" onSubmit={handleLogin}>
        <fieldset className="fieldset" disabled={loading}>
          <div className="form-group">
            <label className="label" htmlFor="login-email">Email</label>
            <input
              id="login-email"
              className="input"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label className="label" htmlFor="login-password">Password</label>
            <input
              id="login-password"
              className="input"
              type="password"
              autoComplete="current-password"
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
          {loading ? 'Logging in…' : 'Log in'}
        </button>
      </form>
      <p className="switch-line">
        Need an account?{' '}
        <button type="button" className="button-link" onClick={onSwitch}>Sign up</button>
      </p>
    </div>
  );
}

export default Login;
