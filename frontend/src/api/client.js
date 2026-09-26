import axios from 'axios';

const client = axios.create({
  baseURL: 'http://localhost:8000',
});

// Attach the current token to every outgoing request. The token itself
// lives in AuthContext's state — client.js just reads it via a setter
// so this file never has to import React.
let currentToken = null;

export function setAuthToken(token) {
  currentToken = token;
}

client.interceptors.request.use((config) => {
  if (currentToken) {
    config.headers.Authorization = `Bearer ${currentToken}`;
  }
  return config;
});

// If the backend ever returns 401 (expired/invalid token), clear it so
// ProtectedRoute redirects to /login on the next render instead of the
// app quietly failing every request.
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      setAuthToken(null);
      localStorage.removeItem('token');
    }
    return Promise.reject(error);
  }
);

export default client;
