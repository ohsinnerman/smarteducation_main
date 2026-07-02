// Shared Chart.js styling so all graphs look consistent and animate nicely.
export const NAVY = '#001f8f';
export const PALETTE = ['#001f8f', '#0033cc', '#0dcaf0', '#198754', '#ffc107', '#dc3545', '#6f42c1', '#fd7e14'];

const baseAnim = { duration: 900, easing: 'easeOutQuart' };

export function lineOpts(extra = {}) {
  return {
    responsive: true, maintainAspectRatio: false,
    animation: baseAnim,
    interaction: { mode: 'index', intersect: false },
    plugins: { legend: { display: false }, tooltip: { padding: 10, cornerRadius: 8 } },
    scales: { y: { beginAtZero: true, grid: { color: '#eef1f8' } }, x: { grid: { display: false } } },
    ...extra,
  };
}

export function barOpts(extra = {}) {
  return {
    responsive: true, maintainAspectRatio: false,
    animation: { ...baseAnim, delay: (ctx) => ctx.dataIndex * 40 },
    plugins: { legend: { display: false }, tooltip: { padding: 10, cornerRadius: 8 } },
    scales: { y: { beginAtZero: true, grid: { color: '#eef1f8' } }, x: { grid: { display: false } } },
    ...extra,
  };
}

export function doughnutOpts(extra = {}) {
  return {
    responsive: true, maintainAspectRatio: false,
    animation: { animateRotate: true, animateScale: true, duration: 900 },
    cutout: '62%',
    plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, padding: 14 } } },
    ...extra,
  };
}

export function radarOpts(extra = {}) {
  return {
    responsive: true, maintainAspectRatio: false,
    animation: baseAnim,
    plugins: { legend: { display: false } },
    scales: { r: { beginAtZero: true, max: 100, grid: { color: '#e6eaf5' }, pointLabels: { font: { size: 11 } } } },
    ...extra,
  };
}

// Build a soft vertical gradient for filled line/area charts.
export function areaGradient(ctx, color = NAVY) {
  const c = ctx.chart.ctx;
  const g = c.createLinearGradient(0, 0, 0, ctx.chart.height || 200);
  g.addColorStop(0, 'rgba(0,31,143,0.28)');
  g.addColorStop(1, 'rgba(0,31,143,0.01)');
  return g;
}
