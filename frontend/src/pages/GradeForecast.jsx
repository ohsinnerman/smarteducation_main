import { useApi } from '../useApi.js';

export default function GradeForecast() {
  const { data, error, loading } = useApi('/grade-forecasts/');
  if (loading) return <p>Loading…</p>;
  if (error) return <p className="text-danger">{error}</p>;
  const rows = data.results ?? data;

  return (
    <div className="chart-container">
      <h6 className="fw-bold mb-3"><i className="bi bi-graph-up-arrow me-2"></i>Academic Forecast</h6>
      {rows.length ? (
        <div className="table-responsive"><table className="table table-hover">
          <thead className="table-light"><tr><th>Student</th><th>Subject</th><th>Predicted Marks</th><th>Confidence</th><th>Remarks</th></tr></thead>
          <tbody>{rows.map((f) => (
            <tr key={f.id}>
              <td>{f.student_name}</td><td>{f.subject_name}</td>
              <td className="fw-bold">{f.predicted_marks}</td>
              <td><span className="badge bg-info">{f.confidence_score}%</span></td>
              <td className="text-muted small">{f.remarks}</td>
            </tr>
          ))}</tbody>
        </table></div>
      ) : <p className="text-muted text-center py-4">No forecasts available.</p>}
    </div>
  );
}
