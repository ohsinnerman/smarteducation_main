import { Doughnut } from 'react-chartjs-2';
import { useApi } from '../useApi.js';
import { useStaggerIn } from '../anim.js';
import { StatCard, ChartCard } from '../components.jsx';
import { doughnutOpts } from '../chartOpts.js';

export default function TeacherDashboard() {
  const { data, error, loading } = useApi('/dashboard/teacher/');
  const ref = useStaggerIn([loading]);
  if (loading) return <p className="p-3">Loading…</p>;
  if (error) return <p className="text-danger">{error}</p>;

  const high = data.at_risk.filter((p) => p.risk_level === 'high').length;
  const medium = data.at_risk.length - high;

  return (
    <div ref={ref}>
      <div className="row g-3 mb-4">
        <div className="col-md-4"><StatCard label="Active Students" value={data.total_students} icon="bi-people-fill" color="primary" /></div>
        <div className="col-md-4"><StatCard label="My Courses" value={data.courses.length} icon="bi-book-fill" color="success" /></div>
        <div className="col-md-4"><StatCard label="At-Risk Flagged" value={data.at_risk.length} icon="bi-exclamation-triangle-fill" color="danger" /></div>
      </div>

      <div className="row g-3">
        <div className="col-xl-4">
          <ChartCard title="Risk Breakdown" icon="bi-pie-chart">
            <div style={{ height: 220 }}>
              <Doughnut data={{ labels: ['High', 'Medium'], datasets: [{ data: [high || 0, medium || 0], backgroundColor: ['#dc3545', '#ffc107'], borderWidth: 0 }] }} options={doughnutOpts()} />
            </div>
          </ChartCard>
        </div>
        <div className="col-xl-8">
          <ChartCard title="My Courses" icon="bi-book">
            {data.courses.length ? (
              <ul className="list-group list-group-flush">
                {data.courses.map((c) => (
                  <li key={c.id} className="list-group-item px-2 d-flex justify-content-between">
                    <span><strong>{c.code}</strong> — {c.name}</span>
                    <i className="bi bi-chevron-right text-muted"></i>
                  </li>
                ))}
              </ul>
            ) : <p className="text-muted">No courses assigned.</p>}
          </ChartCard>
        </div>
      </div>

      <div className="row g-3 mt-1">
        <div className="col-12">
          <ChartCard title="At-Risk Students" icon="bi-exclamation-triangle text-danger">
            {data.at_risk.length ? (
              <div className="table-responsive"><table className="table table-sm table-hover">
                <thead><tr><th>Student</th><th>Type</th><th>Risk</th></tr></thead>
                <tbody>{data.at_risk.map((p) => (
                  <tr key={p.id}><td>{p.student_name}</td><td>{p.prediction_type}</td>
                    <td><span className={`badge bg-${p.risk_level === 'high' ? 'danger' : 'warning'}`}>{p.risk_level}</span></td></tr>
                ))}</tbody>
              </table></div>
            ) : <p className="text-muted">None flagged.</p>}
          </ChartCard>
        </div>
      </div>
    </div>
  );
}
