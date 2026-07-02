import { useApi } from '../useApi.js';
import { useStaggerIn } from '../anim.js';
import { StatCard, ChartCard } from '../components.jsx';

export default function ParentDashboard() {
  const { data, error, loading } = useApi('/dashboard/parent/');
  const ref = useStaggerIn([loading]);
  if (loading) return <p className="p-3">Loading…</p>;
  if (error) return <p className="text-danger">{error}</p>;

  const avgAtt = data.children.length
    ? (data.children.reduce((a, s) => a + (s.attendance || 0), 0) / data.children.length).toFixed(1) : 0;

  return (
    <div ref={ref}>
      <div className="row g-3 mb-4">
        <div className="col-md-4"><StatCard label="My Children" value={data.children.length} icon="bi-people-fill" color="primary" /></div>
        <div className="col-md-4"><StatCard label="Avg Attendance" value={avgAtt} suffix="%" icon="bi-calendar-check-fill" color="info" /></div>
        <div className="col-md-4"><StatCard label="Meetings" value={data.meetings.length} icon="bi-calendar2-check-fill" color="success" /></div>
      </div>

      <ChartCard title="My Children" icon="bi-people">
        {data.children.length ? (
          <div className="table-responsive"><table className="table table-hover">
            <thead className="table-light"><tr><th>Name</th><th>Attendance</th><th>Marks</th><th>CGPA</th></tr></thead>
            <tbody>{data.children.map((s) => (
              <tr key={s.id}><td>{s.name}</td><td>{s.attendance}%</td><td>{s.marks}</td><td>{s.cgpa}</td></tr>
            ))}</tbody>
          </table></div>
        ) : <p className="text-muted">No linked children.</p>}
      </ChartCard>

      <div className="row g-3 mt-1">
        <div className="col-xl-6">
          <ChartCard title="Advising Meetings" icon="bi-calendar2-check">
            {data.meetings.length ? data.meetings.map((m) => (
              <div key={m.id} className="d-flex justify-content-between border-bottom py-2">
                <div>{m.student_name} with {m.teacher_name}<br /><small className="text-muted">{new Date(m.meeting_date).toLocaleString()}</small></div>
                <span className={`badge bg-${m.status === 'scheduled' ? 'primary' : m.status === 'completed' ? 'success' : 'secondary'}`}>{m.status}</span>
              </div>
            )) : <p className="text-muted">No meetings scheduled.</p>}
          </ChartCard>
        </div>
        <div className="col-xl-6">
          <ChartCard title="Progress Reports" icon="bi-file-earmark-text">
            {data.progress_reports.length ? data.progress_reports.map((r) => (
              <div key={r.id} className="border-bottom py-2">
                <strong>{r.student_name}</strong> — {r.report_type} ({r.report_date})<br />
                <small className="text-muted">Attendance {r.attendance_pct}% · Avg {r.avg_marks}</small>
              </div>
            )) : <p className="text-muted">No progress reports.</p>}
          </ChartCard>
        </div>
      </div>
    </div>
  );
}
