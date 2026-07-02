import { useApi } from '../useApi.js';

export default function LearningPath() {
  const { data, error, loading } = useApi('/learning-paths/');
  if (loading) return <p>Loading…</p>;
  if (error) return <p className="text-danger">{error}</p>;
  const paths = data.results ?? data;

  return (
    <div>
      {paths.length ? paths.map((p) => (
        <div key={p.id} className="chart-container mb-3">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <h6 className="fw-bold mb-0"><i className="bi bi-book-half me-2"></i>{p.subject_name}</h6>
            <span className="badge bg-primary">{p.recommended_study_hours} hrs/week</span>
          </div>
          <p className="text-muted small mb-2"><strong>Weak topics:</strong> {p.weak_topics}</p>
          {p.resources?.length > 0 && (
            <div className="row g-2">
              {p.resources.map((r) => (
                <div key={r.id} className="col-md-4">
                  <a href={r.url} target="_blank" rel="noreferrer" className="d-block border rounded p-2 text-decoration-none">
                    <span className="badge bg-secondary mb-1">{r.resource_type}</span>
                    <div className="small fw-bold">{r.title}</div>
                    <div className="text-muted small">{r.provider}</div>
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      )) : <div className="chart-container"><p className="text-muted text-center py-4">No learning paths yet.</p></div>}
    </div>
  );
}
