import { useApi } from '../useApi.js';

export default function PtmScheduler() {
  const { data, error, loading } = useApi('/ptm/');
  if (loading) return <p>Loading…</p>;
  if (error) return <p className="text-danger">{error}</p>;
  const meetings = data.results ?? data;

  return (
    <div className="chart-container">
      <h6 className="fw-bold mb-3"><i className="bi bi-calendar2-check me-2"></i>Advising Meetings</h6>
      {meetings.length ? (
        <div className="table-responsive"><table className="table table-hover">
          <thead className="table-light"><tr><th>Student</th><th>Parent</th><th>Teacher</th><th>Date</th><th>Status</th><th>Agenda</th></tr></thead>
          <tbody>{meetings.map((m) => (
            <tr key={m.id}>
              <td>{m.student_name}</td><td>{m.parent_name}</td><td>{m.teacher_name}</td>
              <td>{new Date(m.meeting_date).toLocaleString()}</td>
              <td><span className={`badge bg-${m.status === 'scheduled' ? 'primary' : m.status === 'completed' ? 'success' : 'secondary'}`}>{m.status}</span></td>
              <td className="text-muted small">{m.agenda}</td>
            </tr>
          ))}</tbody>
        </table></div>
      ) : <p className="text-muted text-center py-4">No meetings scheduled.</p>}
    </div>
  );
}
