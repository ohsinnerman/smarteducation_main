import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth, roleOf } from './auth.jsx';

// Sidebar nav mirrors base.html exactly: same labels, icons, and role gating.
function navItems(role) {
  const items = [];
  if (role === 'admin') items.push(['/admin', 'bi-speedometer2', 'Admin Dashboard']);
  else if (role === 'teacher') items.push(['/teacher', 'bi-speedometer2', 'Teacher Dashboard']);
  else if (role === 'parent') items.push(['/parent', 'bi-speedometer2', 'Guardian Portal']);
  else items.push(['/student', 'bi-speedometer2', 'My Dashboard']);

  items.push(
    ['/students', 'bi-people', 'Students'],
    ['/courses', 'bi-book', 'Courses'],
    ['/exams', 'bi-pencil-square', 'Exams'],
    ['/results', 'bi-graph-up', 'Results'],
    ['/attendance', 'bi-calendar-check', 'Attendance'],
    ['/feedback', 'bi-star', 'Feedback'],
  );
  if (role === 'admin') items.push(['/ml', 'bi-robot', 'AI/ML Module', true]);

  items.push('divider');
  if (role === 'student' || role === 'parent') {
    items.push(
      ['/grade-forecast', 'bi-graph-up-arrow', 'Academic Forecast'],
      ['/learning-path', 'bi-book-half', 'Learning Path'],
    );
  }
  if (role === 'student') items.push(['/gamification', 'bi-trophy', 'Gamification']);
  items.push(['/calendar', 'bi-calendar3', 'Calendar']);
  if (role === 'parent' || role === 'teacher') {
    items.push(['/ptm-scheduler', 'bi-calendar2-check', 'Advising Scheduler']);
  }
  items.push('divider');
  items.push(
    ['/notifications', 'bi-bell', 'Notifications'],
    ['/profile', 'bi-person-circle', 'My Profile'],
  );
  return items;
}

export default function Layout({ title, children }) {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [show, setShow] = useState(false);
  const role = roleOf(user);

  function logout() { signOut(); navigate('/login'); }

  return (
    <>
      <div className={`sidebar${show ? ' show' : ''}`}>
        <div className="brand"><i className="bi bi-mortarboard-fill"></i> SmartEdu Analytics</div>
        <nav className="nav flex-column py-3">
          {navItems(role).map((item, i) =>
            item === 'divider'
              ? <hr key={i} className="mx-3" style={{ borderColor: 'rgba(255,255,255,0.2)' }} />
              : (
                <NavLink key={item[0]} to={item[0]}
                  className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
                  onClick={() => setShow(false)}>
                  <i className={`bi ${item[1]}`}></i> {item[2]}
                </NavLink>
              )
          )}
          <a className="nav-link" onClick={logout}><i className="bi bi-box-arrow-left"></i> Logout</a>
        </nav>
      </div>

      <div className="main-content">
        <div className="top-bar">
          <div>
            <button className="btn btn-sm btn-outline-secondary d-md-none me-2"
              onClick={() => setShow((s) => !s)}>
              <i className="bi bi-list"></i>
            </button>
            <span className="fw-bold text-primary">{title}</span>
          </div>
          <div className="d-flex align-items-center gap-3">
            <div className="position-relative">
              <NavLink to="/notifications" className="text-dark text-decoration-none">
                <i className="bi bi-bell fs-5"></i>
              </NavLink>
            </div>
            <span><i className="bi bi-person-circle fs-5 me-1"></i> {user?.username}</span>
          </div>
        </div>
        {children}
      </div>
    </>
  );
}
