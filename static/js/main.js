import { api, clearTokens, getAccessToken } from './api.js';
import { setCurrentUser } from './state.js';
import { mountAuthView } from './views/authView.js';
import { mountAppShell } from './views/appShell.js';

const authRoot = document.getElementById('auth-root');
const appRoot = document.getElementById('app-root');

function showLogin() {
  appRoot.classList.add('hidden');
  authRoot.classList.remove('hidden');
  mountAuthView(authRoot, { onAuthenticated: showApp, onGuest: showGuest });
}

function showGuest() {
  const me = { id: '', username: 'guest', full_name: 'Гость', role: 'guest' };
  setCurrentUser(me);
  authRoot.classList.add('hidden');
  appRoot.classList.remove('hidden');
  mountAppShell(appRoot, me, { onLogout: showLogin });
}

function showApp(me) {
  setCurrentUser(me);
  authRoot.classList.add('hidden');
  appRoot.classList.remove('hidden');
  mountAppShell(appRoot, me, { onLogout: showLogin });
}

async function boot() {
  if (!getAccessToken()) {
    showLogin();
    return;
  }
  try {
    const me = await api('/api/v1/auth/profile');
    showApp(me);
  } catch {
    clearTokens();
    showLogin();
  }
}

boot();
