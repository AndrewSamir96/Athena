import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function AppLayout() {
  const { logout } = useAuth();

  return (
    <div className="page">
      <header className="topbar">
        <span className="topbar-brand">Notes</span>
        <nav className="topbar-nav">
          <NavLink to="/notes" className={({ isActive }) => (isActive ? 'active' : '')}>
            Your notes
          </NavLink>
          <NavLink to="/notes/upload" className={({ isActive }) => (isActive ? 'active' : '')}>
            Upload
          </NavLink>
          <button className="link-button" onClick={logout}>
            Log out
          </button>
        </nav>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
