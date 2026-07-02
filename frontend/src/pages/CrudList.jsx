import { useState } from 'react';
import { useApi } from '../useApi.js';
import { useFadeIn } from '../anim.js';
import { GradeBadge } from '../components.jsx';

// Generic read-only list matching the old *_list.html tables, now with a live
// filter box and animated entrance.
export default function CrudList({ endpoint, columns }) {
  const { data, error, loading } = useApi(endpoint);
  const [q, setQ] = useState('');
  const ref = useFadeIn();
  if (loading) return <p className="p-3">Loading…</p>;
  if (error) return <p className="text-danger">{error}</p>;
  const all = data.results ?? data;
  const rows = q
    ? all.filter((r) => columns.some(([k]) => String(r[k] ?? '').toLowerCase().includes(q.toLowerCase())))
    : all;

  return (
    <div className="chart-container" ref={ref}>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <span className="badge bg-primary bg-opacity-10 text-primary">{rows.length} records</span>
        <input className="form-control form-control-sm" style={{ maxWidth: 240 }}
          placeholder="Filter…" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      {rows.length ? (
        <div className="table-responsive">
          <table className="table table-hover align-middle">
            <thead className="table-light">
              <tr>{columns.map(([, label]) => <th key={label}>{label}</th>)}</tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  {columns.map(([key]) => (
                    <td key={key}>
                      {key === 'grade' ? <GradeBadge grade={row[key]} /> : String(row[key] ?? '—')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : <p className="text-muted text-center py-4">No records found.</p>}
    </div>
  );
}
