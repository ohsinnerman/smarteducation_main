// Single configurable base URL — never hardcode the backend anywhere else.
const BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!BASE_URL) {
  // Fail loud in dev instead of silently calling the wrong origin.
  console.error('VITE_API_BASE_URL is not set. Copy .env.example to .env.');
}

const ACCESS = 'se_access';
const REFRESH = 'se_refresh';

export const tokens = {
  get access() { return localStorage.getItem(ACCESS); },
  get refresh() { return localStorage.getItem(REFRESH); },
  set({ access, refresh }) {
    if (access) localStorage.setItem(ACCESS, access);
    if (refresh) localStorage.setItem(REFRESH, refresh);
  },
  clear() { localStorage.removeItem(ACCESS); localStorage.removeItem(REFRESH); },
};

async function refreshAccess() {
  if (!tokens.refresh) return false;
  const res = await fetch(`${BASE_URL}/auth/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: tokens.refresh }),
  });
  if (!res.ok) return false;
  const data = await res.json();
  tokens.set({ access: data.access });
  return true;
}

export async function login(username, password) {
  const res = await fetch(`${BASE_URL}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error('Invalid credentials');
  const data = await res.json();
  tokens.set({ access: data.access, refresh: data.refresh });
  return data;
}

export function logout() { tokens.clear(); }

// Authenticated fetch with one automatic refresh-retry on 401.
export async function apiFetch(path, options = {}, _retry = true) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (tokens.access) headers.Authorization = `Bearer ${tokens.access}`;

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (res.status === 401 && _retry && (await refreshAccess())) {
    return apiFetch(path, options, false);
  }
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`API ${res.status}: ${text}`);
  }
  if (res.status === 204) return null;
  return res.json();
}
