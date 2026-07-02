import { useApi } from '../useApi.js';

const ICONS = { email: 'bi-envelope', sms: 'bi-chat-dots', whatsapp: 'bi-whatsapp' };

export default function Notifications() {
  const { data, error, loading } = useApi('/notifications/');
  if (loading) return <p>Loading…</p>;
  if (error) return <p className="text-danger">{error}</p>;
  const rows = data.results ?? data;

  return (
    <div className="chart-container">
      <h6 className="fw-bold mb-3"><i className="bi bi-bell me-2"></i>Notifications</h6>
      {rows.length ? rows.map((n) => (
        <div key={n.id} className="d-flex justify-content-between align-items-start border-bottom py-2">
          <div>
            <i className={`bi ${ICONS[n.notification_type] || 'bi-bell'} me-2 text-primary`}></i>
            <strong>{n.title}</strong>
            <div className="text-muted small">{n.message}</div>
          </div>
          <span className={`badge bg-${n.status === 'sent' ? 'success' : n.status === 'failed' ? 'danger' : 'secondary'}`}>{n.status}</span>
        </div>
      )) : <p className="text-muted text-center py-4">No notifications.</p>}
    </div>
  );
}
