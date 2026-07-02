import { createContext, useContext, useEffect, useState } from 'react';
import { login as apiLogin, logout as apiLogout, apiFetch, tokens } from './api.js';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  async function loadMe() {
    if (!tokens.access) { setLoading(false); return; }
    try {
      setUser(await apiFetch('/me/'));
    } catch {
      apiLogout();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadMe(); }, []);

  async function signIn(username, password) {
    await apiLogin(username, password);
    setUser(await apiFetch('/me/'));
  }

  function signOut() {
    apiLogout();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

export function roleOf(user) {
  return user?.profile?.role || (user?.is_superuser ? 'admin' : null);
}
