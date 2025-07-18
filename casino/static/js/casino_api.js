export const TOKEN_KEY = 'casino_session_token';

export const API_BASE = '/casino/api';

export function setSessionToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}
export function getSessionToken() {
  return localStorage.getItem(TOKEN_KEY);
}
export function clearSessionToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export async function apiLogin(code) {
  const resp = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({login_code: code})
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(data.error || 'Login failed');
  return data;
}

export async function apiMe() {
  const token = getSessionToken();
  if (!token) throw new Error('No session');
  const resp = await fetch(`${API_BASE}/me`, {
    method: 'GET',
    headers: {'Authorization': `Bearer ${token}`}
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(data.error || 'Session invalid');
  return data;
}

export async function apiSpin() {
  const token = getSessionToken();
  if (!token) throw new Error('No session');
  const resp = await fetch(`${API_BASE}/spin`, {
    method: 'POST',
    headers: {
      'Content-Type':'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({})
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(data.error || 'Spin failed');
  return data;
}