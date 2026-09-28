import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { ThemeProvider } from './theme/ThemeContext';
import ProtectedRoute from './auth/ProtectedRoute';
import LoginPage from './auth/LoginPage';
import RegisterPage from './auth/RegisterPage';
import AppShell from './components/AppShell';
import NotesListPage from './notes/NotesListPage';
import UploadPage from './notes/UploadPage';
import ChatPage from './chat/ChatPage';

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Everything under here requires a token — ProtectedRoute redirects
                to /login otherwise. AppShell then adds the sidebar. */}
            <Route element={<ProtectedRoute />}>
              <Route element={<AppShell />}>
                <Route path="/notes" element={<NotesListPage />} />
                <Route path="/notes/upload" element={<UploadPage />} />
                <Route path="/chat" element={<ChatPage />} />
              </Route>
            </Route>

            <Route path="*" element={<Navigate to="/notes" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
