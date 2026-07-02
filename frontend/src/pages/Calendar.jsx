import { useApi } from '../useApi.js';

const COLORS = { class: 'primary', exam: 'danger', meeting: 'info', assignment: 'warning' };

export default function Calendar() {
  const { data, error, loading } = useApi('/events/');
  if (loading) return <p>Loading…</p>;
  if (error) return <p className="text-danger">{error}</p>;
  const events = data.results ?? data;

  return (
    <div className="chart-container">
      <h6 className="fw-bold mb-3"><i className="bi bi-calendar3 me-2"></i>Upcoming Events</h6>
      {events.length ? events.map((e) => (
        <div key={e.id} className="d-flex justify-content-between align-items-center border-bottom py-2">
          <div>
            <span className={`badge bg-${COLORS[e.event_type] || 'secondary'} me-2`}>{e.event_type}</span>
            <strong>{e.title}</strong>
            {e.location && <span className="text-muted small ms-2"><i className="bi bi-geo-alt"></i> {e.location}</span>}
          </div>
          <small className="text-muted">{new Date(e.start_datetime).toLocaleString()}</small>
        </div>
      )) : <p className="text-muted text-center py-4">No events scheduled.</p>}
    </div>
  );
}
