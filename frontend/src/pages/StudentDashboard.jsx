import { useState } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import { useApi } from '../useApi.js';
import { useStaggerIn } from '../anim.js';
import { StatCard, GradeBadge, ChartCard, Segmented } from '../components.jsx';
import { NAVY, PALETTE, lineOpts, barOpts, areaGradient } from '../chartOpts.js';

export default function StudentDashboard() {
  const { data, error, loading } = useApi('/dashboard/student/');
  const [trendType, setTrendType] = useState('area');
  const ref = useStaggerIn([loading]);
  if (loading) return <p className="p-3">Loading…</p>;
  if (error) return <p className="text-danger">{error}</p>;
  if (!data.student) {
    return (
      <div className="stat-card text-center py-5">
        <i className="bi bi-person-plus fs-1 text-muted"></i>
        <h4 className="mt-3">No Student Profile</h4>
        <p className="text-muted">Your account is not linked to a student record yet. Contact your administrator.</p>
      </div>
    );
  }
  const c = data.charts;

  const trendData = {
    labels: c.trend_labels,
    datasets: [{
      label: 'Marks', data: c.trend_values,
      borderColor: NAVY, tension: 0.4, fill: true, pointRadius: 4, pointHoverRadius: 6,
      backgroundColor: trendType === 'area' ? areaGradient : 'transparent',
    }],
  };

  return (
    <div ref={ref}>
      <div className="row g-3 mb-4">
        <div className="col-md-3"><StatCard label="My Attendance" value={data.attendance} suffix="%" icon="bi-calendar-check-fill" color="info" /></div>
        <div className="col-md-3"><StatCard label="My Marks" value={data.marks} icon="bi-graph-up-arrow" color="primary" /></div>
        <div className="col-md-3"><StatCard label="Present Days" value={data.present} icon="bi-check-circle-fill" color="success" /></div>
        <div className="col-md-3"><StatCard label="My Courses" value={data.enrollments_count} icon="bi-book-fill" color="warning" /></div>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-xl-7">
          <ChartCard title="Performance Trend" icon="bi-graph-up"
            actions={<Segmented value={trendType} onChange={setTrendType}
              options={[{ value: 'area', label: 'Area' }, { value: 'line', label: 'Line' }]} />}>
            <div style={{ height: 240 }}><Line data={trendData} options={lineOpts()} /></div>
          </ChartCard>
        </div>
        <div className="col-xl-5">
          <ChartCard title="Subject-wise Marks" icon="bi-bar-chart">
            <div style={{ height: 240 }}>
              <Bar data={{ labels: c.subject_labels, datasets: [{ data: c.subject_values, backgroundColor: PALETTE, borderRadius: 8 }] }}
                options={barOpts({ scales: { y: { beginAtZero: true, max: 100 } } })} />
            </div>
          </ChartCard>
        </div>
      </div>

      <div className="row g-3">
        <div className="col-xl-6">
          <ChartCard title="Upcoming Exams" icon="bi-calendar-event">
            {data.upcoming_exams.length ? data.upcoming_exams.map((ex) => (
              <div key={ex.id} className="d-flex justify-content-between align-items-center border-bottom py-2">
                <div><strong>{ex.name}</strong><br /><small className="text-muted">{ex.subject_name}</small></div>
                <span className="badge bg-primary">{ex.date}</span>
              </div>
            )) : <p className="text-muted">No upcoming exams.</p>}
          </ChartCard>
        </div>
        <div className="col-xl-6">
          <ChartCard title="Recent Results" icon="bi-list-check">
            {data.results.length ? (
              <div className="table-responsive"><table className="table table-sm table-hover">
                <thead><tr><th>Exam</th><th>Marks</th><th>Grade</th></tr></thead>
                <tbody>{data.results.slice(0, 10).map((r) => (
                  <tr key={r.id}><td>{r.exam_name}</td><td>{r.marks_obtained}</td><td><GradeBadge grade={r.grade} /></td></tr>
                ))}</tbody>
              </table></div>
            ) : <p className="text-muted">No results yet.</p>}
          </ChartCard>
        </div>
      </div>
    </div>
  );
}
