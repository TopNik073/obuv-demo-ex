const ACCESS_KEY = 'obuv_access_token';
const REFRESH_KEY = 'obuv_refresh_token';

/** localStorage сохраняет сессию после перезапуска приложения (тот же origin). */
const store = localStorage;

function migrateSessionToLocal() {
  try {
    if (!store.getItem(ACCESS_KEY) && sessionStorage.getItem(ACCESS_KEY)) {
      store.setItem(ACCESS_KEY, sessionStorage.getItem(ACCESS_KEY));
      const rt = sessionStorage.getItem(REFRESH_KEY);
      if (rt) store.setItem(REFRESH_KEY, rt);
      sessionStorage.removeItem(ACCESS_KEY);
      sessionStorage.removeItem(REFRESH_KEY);
    }
  } catch {
    /* ignore */
  }
}

migrateSessionToLocal();

export function getAccessToken() {
  return store.getItem(ACCESS_KEY);
}

export function getRefreshToken() {
  return store.getItem(REFRESH_KEY);
}

export function setTokens(access, refresh) {
  if (access) store.setItem(ACCESS_KEY, access);
  else store.removeItem(ACCESS_KEY);
  if (refresh) store.setItem(REFRESH_KEY, refresh);
  else store.removeItem(REFRESH_KEY);
}

export function clearTokens() {
  setTokens(null, null);
}

async function refreshAccessToken() {
  const rt = getRefreshToken();
  if (!rt) throw new Error('Нет refresh-токена');
  const res = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: rt }),
  });
  const text = await res.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }
  if (!res.ok) {
    const detail = data && data.detail != null ? String(data.detail) : res.statusText;
    throw new Error(detail || `HTTP ${res.status}`);
  }
  setTokens(data.access_token, data.refresh_token);
}

/**
 * @param {string} path
 * @param {RequestInit} [options]
 * @param {boolean} [isRetry]
 */
export async function api(path, options = {}, isRetry = false) {
  const headers = { ...(options.headers || {}) };
  const token = getAccessToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body != null && !headers['Content-Type']) {
    const isForm = typeof FormData !== 'undefined' && options.body instanceof FormData;
    if (!isForm) headers['Content-Type'] = 'application/json';
  }
  const res = await fetch(path, {
    cache: 'no-store',
    ...options,
    headers,
  });
  if (res.status === 401 && !isRetry && getRefreshToken() && !path.endsWith('/auth/refresh')) {
    try {
      await refreshAccessToken();
      return api(path, options, true);
    } catch {
      clearTokens();
    }
  }
  const text = await res.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }
  if (!res.ok) {
    const detail =
      data && data.detail != null
        ? Array.isArray(data.detail)
          ? data.detail.map((d) => d.msg).join(', ')
          : String(data.detail)
        : res.statusText;
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return data;
}
