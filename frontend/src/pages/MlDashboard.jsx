import { useApi } from '../useApi.js';
import { useStaggerIn } from '../anim.js';
import { StatCard } from '../components.jsx';

export default function MlDashboard() {
  const { data, error, loading } = useApi('/predictions/');
  const ref = useStaggerIn([loading]);
  if (loading) return <p className="p-3">Loading…</p>;
  if (error) return <p className="text-danger">{error}</p>;
  const rows = data.results ?? data;
  const high = rows.filter((p) => p.risk_level === 'high').length;
  const medium = rows.filter((p) => p.risk_level === 'medium').length;

  return (
    <div ref={ref}>
      <div className="row g-3 mb-4">
        <div className="col-md-4"><StatCard label="Total Predictions" value={rows.length} icon="bi-robot" color="primary" /></div>
        <div className="col-md-4"><StatCard label="High Risk" value={high} icon="bi-exclamation-octagon-fill" color="danger" /></div>
        <div className="col-md-4"><StatCard label="Medium Risk" value={medium} icon="bi-exclamation-triangle-fill" color="warning" /></div>
      </div>

      <div className="chart-container">
        <h6 className="fw-bold mb-3"><i className="bi bi-cpu me-2"></i>Predictions</h6>
        {rows.length ? (
          <div className="table-responsive"><table className="table table-hover">
            <thead className="table-light"><tr><th>Student</th><th>Type</th><th>Risk</th><th>Confidence</th></tr></thead>
            <tbody>{rows.map((p) => (
              <tr key={p.id}>
                <td>{p.student_name}</td><td>{p.prediction_type}</td>
                <td><span className={`badge bg-${p.risk_level === 'high' ? 'danger' : p.risk_level === 'low' ? 'success' : 'warning'}`}>{p.risk_level || '—'}</span></td>
                <td>{p.confidence?.toFixed?.(2) ?? '—'}</td>
              </tr>
            ))}</tbody>
          </table></div>
        ) : <p className="text-muted text-center py-4">No predictions yet. Run <code>python manage.py reset_predictions --train</code>.</p>}
      </div>
    </div>
  );
}
