import React, { useState } from 'react';

const API = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export default function Login({ onLoginSuccess, currentUser }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Senior Analyst');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const endpoint = isRegister ? `${API}/auth/register` : `${API}/auth/login`;
    const body = isRegister
      ? { username, email, password, role }
      : { username, password };

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Authentication failed');
      }

      localStorage.setItem('token', data.token);
      if (onLoginSuccess) {
        onLoginSuccess(data.user, data.token);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = () => {
    setUsername('analyst');
    setPassword('password123');
    setIsRegister(false);
  };

  if (currentUser) {
    return (
      <div className="login-card logged-in">
        <div className="user-avatar">👤</div>
        <h2>Welcome back, {currentUser.username}!</h2>
        <p className="muted">Role: <strong>{currentUser.role}</strong> | Email: {currentUser.email}</p>
        <div className="login-success-badge">
          ✅ Authenticated Session Active
        </div>
      </div>
    );
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="login-badge-icon">🇰🇪</div>
          <h2>{isRegister ? 'Create Analyst Account' : 'Analyst Log In'}</h2>
          <p className="subtitle">
            Access secure sentiment analytics and tension alert controls
          </p>
        </div>

        <div className="auth-tabs">
          <button
            type="button"
            className={!isRegister ? 'auth-tab active' : 'auth-tab'}
            onClick={() => { setIsRegister(false); setError(''); }}
          >
            Log In
          </button>
          <button
            type="button"
            className={isRegister ? 'auth-tab active' : 'auth-tab'}
            onClick={() => { setIsRegister(true); setError(''); }}
          >
            Register
          </button>
        </div>

        {error && <div className="auth-error-banner" role="alert">⚠️ {error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="username-input">Username</label>
            <input
              id="username-input"
              type="text"
              placeholder="e.g. analyst or john_doe"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          {isRegister && (
            <>
              <div className="form-group">
                <label htmlFor="email-input">Email Address</label>
                <input
                  id="email-input"
                  type="email"
                  placeholder="e.g. analyst@maandamanopulse.co.ke"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="role-input">Role / Title</label>
                <select
                  id="role-input"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                >
                  <option value="Senior Analyst">Senior Analyst</option>
                  <option value="Civic Researcher">Civic Researcher</option>
                  <option value="System Operator">System Operator</option>
                </select>
              </div>
            </>
          )}

          <div className="form-group">
            <label htmlFor="password-input">Password</label>
            <input
              id="password-input"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="primary-btn auth-submit-btn" disabled={loading}>
            {loading ? 'Authenticating…' : (isRegister ? 'Register Account' : 'Log In to Pulse')}
          </button>
        </form>

        {!isRegister && (
          <div className="quick-fill-option">
            <p>Demo Preset Credentials:</p>
            <button type="button" className="demo-fill-btn" onClick={handleQuickLogin}>
              ⚡ Fill Demo Credentials (analyst / password123)
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
