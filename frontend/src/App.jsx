import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth, roleOf } from './auth.jsx';
import Layout from './Layout.jsx';
import Login from './pages/Login.jsx';
import AdminDashboard from './pages/AdminDashboard.jsx';
import TeacherDashboard from './pages/TeacherDashboard.jsx';
import StudentDashboard from './pages/StudentDashboard.jsx';
import ParentDashboard from './pages/ParentDashboard.jsx';
import Students from './pages/Students.jsx';
import CrudList from './pages/CrudList.jsx';
import Gamification from './pages/Gamification.jsx';
import Calendar from './pages/Calendar.jsx';
import GradeForecast from './pages/GradeForecast.jsx';
import LearningPath from './pages/LearningPath.jsx';
import PtmScheduler from './pages/PtmScheduler.jsx';
import Notifications from './pages/Notifications.jsx';
import Profile from './pages/Profile.jsx';
import MlDashboard from './pages/MlDashboard.jsx';

function Home() {
  const { user } = useAuth();
  const dest = { admin: '/admin', teacher: '/teacher', student: '/student', parent: '/parent' }[roleOf(user)];
  return dest ? <Navigate to={dest} replace /> : <p>No role assigned. Contact an administrator.</p>;
}

function Protected({ children, allow, title }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="p-4">Loading…</p>;
  if (!user) return <Navigate to="/login" replace />;
  if (allow && !allow.includes(roleOf(user))) return <Navigate to="/" replace />;
  return <Layout title={title}>{children}</Layout>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Protected title="Dashboard"><Home /></Protected>} />

      <Route path="/admin" element={<Protected allow={['admin']} title="Admin Dashboard"><AdminDashboard /></Protected>} />
      <Route path="/teacher" element={<Protected allow={['teacher', 'admin']} title="Teacher Dashboard"><TeacherDashboard /></Protected>} />
      <Route path="/student" element={<Protected allow={['student', 'admin']} title="My Dashboard"><StudentDashboard /></Protected>} />
      <Route path="/parent" element={<Protected allow={['parent', 'admin']} title="Guardian Portal"><ParentDashboard /></Protected>} />

      <Route path="/students" element={<Protected title="Students"><Students /></Protected>} />
      <Route path="/courses" element={<Protected title="Courses"><CrudList endpoint="/courses/" columns={[['code', 'Code'], ['name', 'Name'], ['teacher_name', 'Teacher']]} /></Protected>} />
      <Route path="/exams" element={<Protected title="Exams"><CrudList endpoint="/exams/" columns={[['name', 'Name'], ['subject_name', 'Subject'], ['exam_type', 'Type'], ['date', 'Date'], ['total_marks', 'Total']]} /></Protected>} />
      <Route path="/results" element={<Protected title="Results"><CrudList endpoint="/results/" columns={[['student_name', 'Student'], ['exam_name', 'Exam'], ['marks_obtained', 'Marks'], ['grade', 'Grade']]} /></Protected>} />
      <Route path="/attendance" element={<Protected title="Attendance"><CrudList endpoint="/attendance/" columns={[['student_name', 'Student'], ['subject_name', 'Subject'], ['date', 'Date'], ['status', 'Status']]} /></Protected>} />
      <Route path="/feedback" element={<Protected title="Feedback"><CrudList endpoint="/feedback/" columns={[['student_name', 'Student'], ['teacher_name', 'Teacher'], ['rating', 'Rating']]} /></Protected>} />

      <Route path="/ml" element={<Protected allow={['admin']} title="AI/ML Module"><MlDashboard /></Protected>} />
      <Route path="/grade-forecast" element={<Protected allow={['student', 'parent', 'admin']} title="Academic Forecast"><GradeForecast /></Protected>} />
      <Route path="/learning-path" element={<Protected allow={['student', 'parent', 'admin']} title="Learning Path"><LearningPath /></Protected>} />
      <Route path="/gamification" element={<Protected allow={['student', 'admin']} title="Gamification Dashboard"><Gamification /></Protected>} />
      <Route path="/calendar" element={<Protected title="Calendar"><Calendar /></Protected>} />
      <Route path="/ptm-scheduler" element={<Protected allow={['parent', 'teacher', 'admin']} title="Advising Scheduler"><PtmScheduler /></Protected>} />

      <Route path="/notifications" element={<Protected title="Notifications"><Notifications /></Protected>} />
      <Route path="/profile" element={<Protected title="My Profile"><Profile /></Protected>} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
