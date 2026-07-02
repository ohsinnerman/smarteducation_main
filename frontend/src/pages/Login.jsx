import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth.jsx';

export default function Login() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      await signIn(username, password);
      navigate('/');
    } catch {
      setError('Invalid username or password.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-page">
      <div className="card shadow-lg border-0" style={{ width: 400, borderRadius: 16 }}>
        <div className="card-body p-4">
          <div className="text-center mb-4">
            <i className="bi bi-mortarboard-fill text-primary" style={{ fontSize: '2.5rem' }}></i>
            <h4 className="fw-bold mt-2">SmartEdu Analytics</h4>
            <p className="text-muted small">Sign in to your account</p>
          </div>
          <form onSubmit={onSubmit}>
            <div className="mb-3">
              <label className="form-label small fw-bold">Username</label>
              <input className="form-control" value={username} autoFocus
                onChange={(e) => setUsername(e.target.value)} />
            </div>
            <div className="mb-3">
              <label className="form-label small fw-bold">Password</label>
              <input type="password" className="form-control" value={password}
                onChange={(e) => setPassword(e.target.value)} />
            </div>
            {error && <div className="alert alert-danger py-2 small">{error}</div>}
            <button className="btn btn-primary w-100" disabled={busy}>
              {busy ? 'Signing in…' : 'Sign In'}
            </button>
          </form>
          <p className="text-muted small mt-3 mb-0">
            Demo: admin_demo / admin1234 · teacher_demo / teacher1234 ·
            student_demo1 / student1234 · parent_demo / parent1234
          </p>
        </div>
      </div>
    </div>
  );
}
