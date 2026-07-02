import { useApi } from '../useApi.js';
import { useStaggerIn } from '../anim.js';
import { StatCard } from '../components.jsx';

export default function Gamification() {
  const dash = useApi('/dashboard/student/');
  const points = useApi('/points/');
  const board = useApi('/student-badges/');
  const ref = useStaggerIn([dash.loading]);
  if (dash.loading) return <p className="p-3">Loading…</p>;
  if (dash.error) return <p className="text-danger">{dash.error}</p>;
  const badges = dash.data.badges || [];
  const history = (points.data?.results ?? points.data ?? []);

  return (
    <div ref={ref}>
      <div className="row g-4 mb-4">
        <div className="col-xl-4" data-anim>
          <div className="stat-card text-center">
            <i className="bi bi-trophy text-warning fs-1 mb-2"></i>
            <h2 className="fw-bold">{dash.data.points_total}</h2>
            <p className="text-muted">Total Points</p>
          </div>
        </div>
        <div className="col-xl-8" data-anim>
          <div className="stat-card">
            <h5 className="mb-3">Your Badges</h5>
            <div className="row g-2">
              {badges.length ? badges.map((sb) => (
                <div key={sb.id} className="col-md-3 col-6">
                  <div className="badge-tile border rounded p-3 text-center" style={{ background: 'linear-gradient(135deg, #ffecb3, #ffe082)' }}>
                    <i className={`bi ${sb.badge.icon} text-warning fs-3`}></i>
                    <p className="mb-0 mt-1 small fw-bold">{sb.badge.name}</p>
                  </div>
                </div>
              )) : <div className="col-12"><p className="text-muted text-center">No badges earned yet. Keep going!</p></div>}
            </div>
          </div>
        </div>
      </div>

      <div className="row g-4">
        <div className="col-xl-6"><div className="chart-container" data-anim>
          <h5 className="mb-3"><i className="bi bi-people me-2 text-primary"></i>Badges Earned</h5>
          <div className="table-responsive"><table className="table table-hover">
            <thead className="table-light"><tr><th>#</th><th>Student</th><th>Badge</th></tr></thead>
            <tbody>{(board.data?.results ?? board.data ?? []).map((b, i) => (
              <tr key={b.id}><td>{i + 1}</td><td>{b.student_name}</td><td>{b.badge?.name}</td></tr>
            ))}</tbody>
          </table></div>
        </div></div>
        <div className="col-xl-6"><div className="chart-container" data-anim>
          <h5 className="mb-3"><i className="bi bi-clock-history me-2 text-success"></i>Points History</h5>
          {history.length ? history.map((sp) => (
            <div key={sp.id} className="d-flex justify-content-between border-bottom py-2">
              <div><i className="bi bi-check-circle-fill text-success me-2"></i> {sp.reason} <span className="text-muted small">({sp.category})</span></div>
              <div className="fw-bold text-success">+{sp.points}</div>
            </div>
          )) : <p className="text-muted text-center py-4">No points history yet.</p>}
        </div></div>
      </div>
    </div>
  );
}
