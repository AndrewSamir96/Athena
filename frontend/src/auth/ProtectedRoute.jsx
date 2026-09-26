import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './AuthContext';

// Wraps any set of routes that need a logged-in user. Used in App.jsx as:
//   <Route element={<ProtectedRoute />}>
//     <Route path="/notes" element={<NotesListPage />} />
//   </Route>
export default function ProtectedRoute() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}
