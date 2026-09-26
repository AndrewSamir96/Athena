import { createContext, useContext, useState, useEffect } from 'react';
import client, { setAuthToken } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Starting from localStorage means a page refresh doesn't log you out.
  // Swap to plain useState(null) if you'd rather trade that convenience
  // for not persisting the token at all — see the guide's note in Phase 5.
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  // The JWT itself only carries the user id (`sub`), not the email — so we
  // keep the email the person typed to log in, purely for display in the UI.
  // A real app would add a GET /auth/me endpoint instead of trusting this.
  const [user, setUser] = useState(() => {
    const email = localStorage.getItem('email');
    return email ? { email } : null;
  });

  useEffect(() => {
    setAuthToken(token);
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
      localStorage.removeItem('email');
    }
  }, [token]);

  async function login(email, password) {
    const { data } = await client.post('/auth/login', { email, password });
    localStorage.setItem('email', email);
    setUser({ email });
    setToken(data.access_token);
  }

  async function register(email, password) {
    const { data } = await client.post('/auth/register', { email, password });
    localStorage.setItem('email', email);
    setUser({ email });
    setToken(data.access_token);
  }

  function logout() {
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ token, user, login, register, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook so every component does `const { login } = useAuth()`
// instead of importing useContext + AuthContext everywhere.
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside an AuthProvider');
  return ctx;
}
