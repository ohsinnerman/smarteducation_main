// Shared presentational bits matching base.html's stat-card / badge patterns,
// now with GSAP count-up and interactive hover accents.
import { useCountUp } from './anim.js';

// A stat tile whose numeric value animates up on mount.
export function StatCard({ label, value, icon, color = 'primary', suffix = '' }) {
  const numeric = typeof value === 'number' || /^[\d.]+$/.test(String(value));
  const animated = useCountUp(numeric ? parseFloat(value) : 0);
  const shown = numeric
    ? (Number.isInteger(parseFloat(value)) ? Math.round(animated) : animated.toFixed(1))
    : value;
  return (
    <div className={`stat-card stat-accent-${color}`} data-anim>
      <div className="d-flex justify-content-between align-items-center">
        <div>
          <p className="text-muted mb-1 small">{label}</p>
          <h3 className="mb-0 fw-bold">{shown}{suffix}</h3>
        </div>
        <div className={`stat-icon bg-${color} bg-opacity-10 text-${color}`}>
          <i className={`bi ${icon}`}></i>
        </div>
      </div>
    </div>
  );
}

export function GradeBadge({ grade }) {
  const g = grade || '';
  let color = 'danger';
  if (['A+', 'A'].includes(g)) color = 'success';
  else if (['B+', 'B'].includes(g)) color = 'primary';
  else if (['C+', 'C'].includes(g)) color = 'warning';
  return <span className={`badge bg-${color}`}>{g || '—'}</span>;
}

export function ChartCard({ title, icon, children, actions }) {
  return (
    <div className="chart-container" data-anim>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h6 className="fw-bold mb-0"><i className={`bi ${icon} me-2`}></i>{title}</h6>
        {actions}
      </div>
      {children}
    </div>
  );
}

// Small segmented toggle used to switch chart views.
export function Segmented({ options, value, onChange }) {
  return (
    <div className="btn-group btn-group-sm" role="group">
      {options.map((opt) => (
        <button key={opt.value} type="button"
          className={`btn ${value === opt.value ? 'btn-primary' : 'btn-outline-primary'}`}
          onClick={() => onChange(opt.value)}>
          {opt.label}
        </button>
      ))}
    </div>
  );
}
