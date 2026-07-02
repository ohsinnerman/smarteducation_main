import { useState } from 'react';
import { useApi } from '../useApi.js';
import { useFadeIn } from '../anim.js';
import { GradeBadge } from '../components.jsx';

// Mirrors student_list.html: searchable card+table of students.
export default function Students() {
  const [q, setQ] = useState('');
  const ref = useFadeIn();
  const { data, error, loading } = useApi('/students/');
  if (loading) return <p className="p-3">Loading…</p>;
  if (error) return <p className="text-danger">{error}</p>;
  const rows = (data.results ?? data).filter(
    (s) => s.name.toLowerCase().includes(q.toLowerCase())
      || (s.roll_number || '').toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div className="chart-container" ref={ref}>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h6 className="fw-bold mb-0"><i className="bi bi-people me-2"></i>Students</h6>
        <input className="form-control form-control-sm" style={{ maxWidth: 240 }}
          placeholder="Search name or roll no…" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      <div className="table-responsive">
        <table className="table table-hover">
          <thead className="table-light">
            <tr><th>Name</th><th>Roll No</th><th>Program</th><th>Year</th><th>Attendance</th><th>Marks</th><th>Grade</th></tr>
          </thead>
          <tbody>
            {rows.map((s) => (
              <tr key={s.id}>
                <td>{s.name}</td><td>{s.roll_number}</td><td>{s.program}</td><td>{s.year ?? '—'}</td>
                <td>{s.attendance}%</td><td>{s.marks}</td><td><GradeBadge grade={s.grade} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rows.length === 0 && <p className="text-muted text-center py-3">No students match.</p>}
    </div>
  );
}
