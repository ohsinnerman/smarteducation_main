import { useAuth, roleOf } from '../auth.jsx';

export default function Profile() {
  const { user } = useAuth();
  const p = user?.profile || {};

  return (
    <div className="row">
      <div className="col-lg-6">
        <div className="chart-container">
          <div className="text-center mb-3">
            <i className="bi bi-person-circle text-primary" style={{ fontSize: '4rem' }}></i>
            <h5 className="fw-bold mt-2">{user?.username}</h5>
            <span className="badge bg-primary text-capitalize">{roleOf(user)}</span>
          </div>
          <table className="table">
            <tbody>
              <tr><th>Email</th><td>{user?.email || '—'}</td></tr>
              <tr><th>First name</th><td>{user?.first_name || '—'}</td></tr>
              <tr><th>Last name</th><td>{user?.last_name || '—'}</td></tr>
              <tr><th>Phone</th><td>{p.phone || '—'}</td></tr>
              <tr><th>Department</th><td>{p.department || '—'}</td></tr>
              <tr><th>Bio</th><td>{p.bio || '—'}</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
