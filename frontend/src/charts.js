// Register the Chart.js pieces used by the dashboards once, app-wide.
import {
  Chart, CategoryScale, LinearScale, RadialLinearScale,
  PointElement, LineElement, BarElement, ArcElement,
  Filler, Tooltip, Legend,
} from 'chart.js';

Chart.register(
  CategoryScale, LinearScale, RadialLinearScale,
  PointElement, LineElement, BarElement, ArcElement,
  Filler, Tooltip, Legend,
);
