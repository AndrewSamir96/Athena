import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useTheme } from '../theme/ThemeContext';

export default function AppShell() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="sidebar-brand">Athena</div>

        <nav className="sidebar-nav">
          <NavLink
            to="/notes"
            className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
          >
            <span className="sidebar-dot" />
            Your notes
          </NavLink>
          <NavLink
            to="/notes/upload"
            className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
          >
            <span className="sidebar-dot" />
            Upload
          </NavLink>
          <NavLink
            to="/chat"
            className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
          >
            <span className="sidebar-dot" />
            Chat
          </NavLink>
        </nav>

        <div className="sidebar-spacer" />

        <div className="sidebar-foot">
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === 'light' ? '🌙 Dark mode' : '☀️ Light mode'}
          </button>
          <div className="sidebar-user">
            <span>{user?.email ?? 'Signed in'}</span>
            <button onClick={logout}>Log out</button>
          </div>
        </div>
      </aside>

      <div className="main">
        <Outlet />
      </div>
    </div>
  );
}
