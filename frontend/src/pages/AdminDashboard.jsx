import { useState } from 'react';
import { Line, Bar, Doughnut, Radar } from 'react-chartjs-2';
import { useApi } from '../useApi.js';
import { useStaggerIn } from '../anim.js';
import { StatCard, GradeBadge, ChartCard, Segmented } from '../components.jsx';
import { NAVY, PALETTE, barOpts, doughnutOpts, radarOpts, lineOpts, areaGradient } from '../chartOpts.js';

export default function AdminDashboard() {
  const { data, error, loading } = useApi('/dashboard/admin/');
  const [subjectView, setSubjectView] = useState('radar');
  const ref = useStaggerIn([loading]);
  if (loading) return <p className="p-3">Loading…</p>;
  if (error) return <p className="text-danger">{error}</p>;
  const c = data.charts;

  const subjectData = {
    labels: c.subject_labels,
    datasets: [{
      label: 'Avg Marks', data: c.subject_values,
      borderColor: NAVY, backgroundColor: subjectView === 'radar' ? 'rgba(0,31,143,0.15)' : PALETTE,
      borderRadius: 6, pointBackgroundColor: NAVY,
    }],
  };

  return (
    <div ref={ref}>
      <div className="d-flex justify-content-between align-items-center mb-4" data-anim>
        <div>
          <p className="text-muted mb-1">Consolidated analytics for attendance, GPA, performance, and courses.</p>
          <h5 className="fw-bold">Admin Reporting</h5>
        </div>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-xl-3 col-md-6"><StatCard label="Total Students" value={data.total_students} icon="bi-people-fill" color="primary" /></div>
        <div className="col-xl-3 col-md-6"><StatCard label="Total Teachers" value={data.total_teachers} icon="bi-person-workspace" color="success" /></div>
        <div className="col-xl-3 col-md-6"><StatCard label="Avg Attendance" value={data.avg_attendance} suffix="%" icon="bi-calendar-check-fill" color="info" /></div>
        <div className="col-xl-3 col-md-6"><StatCard label="Avg Marks" value={data.avg_marks} icon="bi-graph-up-arrow" color="warning" /></div>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-xl-8">
          <ChartCard title="Grade Distribution" icon="bi-bar-chart">
            <div style={{ height: 260 }}>
              <Bar data={{ labels: c.grade_labels, datasets: [{ label: 'Students', data: c.grade_values, backgroundColor: PALETTE, borderRadius: 8 }] }} options={barOpts()} />
            </div>
          </ChartCard>
        </div>
        <div className="col-xl-4">
          <ChartCard title="Attendance Distribution" icon="bi-pie-chart">
            <div style={{ height: 260 }}>
              <Doughnut data={{ labels: c.attendance_labels, datasets: [{ data: c.attendance_values, backgroundColor: ['#dc3545', '#ffc107', '#0dcaf0', '#198754'], borderWidth: 0 }] }} options={doughnutOpts()} />
            </div>
          </ChartCard>
        </div>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-xl-6">
          <ChartCard title="Subject-wise Performance" icon="bi-activity"
            actions={<Segmented value={subjectView} onChange={setSubjectView}
              options={[{ value: 'radar', label: 'Radar' }, { value: 'bar', label: 'Bar' }]} />}>
            <div style={{ height: 280 }}>
              {subjectView === 'radar'
                ? <Radar data={subjectData} options={radarOpts()} />
                : <Bar data={subjectData} options={barOpts({ indexAxis: 'y' })} />}
            </div>
          </ChartCard>
        </div>
        <div className="col-xl-6">
          <ChartCard title="At-Risk Students" icon="bi-exclamation-triangle text-danger">
            {data.at_risk_students.length ? (
              <div className="table-responsive"><table className="table table-sm table-hover">
                <thead><tr><th>Student</th><th>Risk Level</th><th>Confidence</th></tr></thead>
                <tbody>{data.at_risk_students.map((p) => (
                  <tr key={p.id}><td>{p.student_name}</td>
                    <td><span className={`badge bg-${p.risk_level === 'high' ? 'danger' : p.risk_level === 'low' ? 'success' : 'warning'}`}>{p.risk_level || 'medium'}</span></td>
                    <td>{p.confidence?.toFixed?.(2) ?? '—'}</td></tr>
                ))}</tbody>
              </table></div>
            ) : <p className="text-muted">No at-risk students detected. Run <code>reset_predictions --train</code>.</p>}
          </ChartCard>
        </div>
      </div>

      <div className="row g-3">
        <div className="col-xl-8">
          <ChartCard title="Recent Results" icon="bi-clock-history">
            {data.recent_results.length ? (
              <div className="table-responsive"><table className="table table-sm table-hover">
                <thead><tr><th>Student</th><th>Exam</th><th>Marks</th><th>Grade</th></tr></thead>
                <tbody>{data.recent_results.map((r) => (
                  <tr key={r.id}><td>{r.student_name}</td><td>{r.exam_name}</td><td>{r.marks_obtained}</td><td><GradeBadge grade={r.grade} /></td></tr>
                ))}</tbody>
              </table></div>
            ) : <p className="text-muted">No results recorded yet.</p>}
          </ChartCard>
        </div>
        <div className="col-xl-4">
          <div className="stat-card text-center mb-3" data-anim>
            <h6 className="fw-bold mb-3"><i className="bi bi-star me-2"></i>Feedback Rating</h6>
            <h2 className="fw-bold text-warning mb-0">{data.avg_rating} <small className="text-muted fs-6">/ 5</small></h2>
            <div className="mt-1">{[1, 2, 3, 4, 5].map((n) => (
              <i key={n} className={`bi ${n <= Math.round(data.avg_rating) ? 'bi-star-fill' : 'bi-star'} text-warning`}></i>
            ))}</div>
            <p className="text-muted small mt-2 mb-0">{data.total_feedback} total feedbacks</p>
          </div>
          <div className="stat-card text-center" data-anim>
            <h6 className="fw-bold mb-3"><i className="bi bi-book me-2"></i>Total Courses</h6>
            <h2 className="fw-bold text-primary mb-0">{data.total_courses}</h2>
          </div>
        </div>
      </div>
    </div>
  );
}
