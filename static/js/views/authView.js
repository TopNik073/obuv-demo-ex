import { api, setTokens } from '../api.js';
import { setCurrentUser } from '../state.js';
import { createButton } from '../components/Button.js';
import { createTextField } from '../components/TextField.js';

/**
 * @param {HTMLElement} root
 * @param {{
 *   onAuthenticated: (me: { id: string, username: string, full_name: string, role: string }) => void,
 *   onGuest?: () => void,
 * }} hooks
 */
export function mountAuthView(root, hooks) {
  root.replaceChildren();
  root.className = 'ui-auth-wrap';

  const brand = document.createElement('div');
  brand.className = 'ui-auth-brand';
  const logoImg = document.createElement('img');
  logoImg.src = '/static/logo.svg';
  logoImg.alt = 'Логотип';
  logoImg.className = 'ui-auth-logo';
  brand.appendChild(logoImg);

  const loginCard = document.createElement('div');
  loginCard.className = 'ui-card';
  const loginTitle = document.createElement('h1');
  loginTitle.className = 'ui-card__title';
  loginTitle.textContent = 'Вход';
  loginCard.appendChild(loginTitle);

  const loginForm = document.createElement('form');
  const u1 = createTextField({ name: 'username', label: 'Логин', required: true });
  u1.input.autocomplete = 'username';
  const p1 = createTextField({ name: 'password', label: 'Пароль', type: 'password', required: true });
  p1.input.autocomplete = 'current-password';
  const loginErr = document.createElement('div');
  loginErr.className = 'ui-err hidden';
  const loginSubmit = createButton('Войти', { type: 'submit', variant: 'primary' });
  loginForm.append(u1.root, p1.root, loginErr, loginSubmit);

  loginForm.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    loginErr.classList.add('hidden');
    const fd = new FormData(loginForm);
    try {
      const data = await api('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username: fd.get('username'), password: fd.get('password') }),
      });
      setTokens(data.access_token, data.refresh_token);
      const me = await api('/api/v1/auth/profile');
      setCurrentUser(me);
      hooks.onAuthenticated(me);
    } catch (e) {
      loginErr.textContent = e.message;
      loginErr.classList.remove('hidden');
    }
  });
  loginCard.appendChild(loginForm);

  const registerCard = document.createElement('div');
  registerCard.className = 'ui-card hidden';
  const regTitle = document.createElement('h1');
  regTitle.className = 'ui-card__title';
  regTitle.textContent = 'Регистрация';
  registerCard.appendChild(regTitle);

  const regForm = document.createElement('form');
  const ru = createTextField({ name: 'username', label: 'Логин', required: true });
  ru.input.autocomplete = 'username';
  const rp = createTextField({ name: 'password', label: 'Пароль (не менее 6 символов)', type: 'password', required: true });
  rp.input.minLength = 6;
  rp.input.autocomplete = 'new-password';
  const rn = createTextField({ name: 'name', label: 'Имя' });
  const rs = createTextField({ name: 'surname', label: 'Фамилия' });
  const rl = createTextField({ name: 'lastname', label: 'Отчество' });
  const regErr = document.createElement('div');
  regErr.className = 'ui-err hidden';
  const regSubmit = createButton('Зарегистрироваться', { type: 'submit', variant: 'primary' });
  regForm.append(ru.root, rp.root, rn.root, rs.root, rl.root, regErr, regSubmit);

  regForm.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    regErr.classList.add('hidden');
    const fd = new FormData(regForm);
    const pwd = String(fd.get('password') || '');
    if (pwd.length < 6) {
      regErr.textContent = 'Пароль должен быть не короче 6 символов';
      regErr.classList.remove('hidden');
      return;
    }
    try {
      const data = await api('/api/v1/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          username: fd.get('username'),
          password: pwd,
          name: fd.get('name') || '',
          surname: fd.get('surname') || '',
          lastname: fd.get('lastname') || '',
        }),
      });
      setTokens(data.access_token, data.refresh_token);
      const me = await api('/api/v1/auth/profile');
      setCurrentUser(me);
      hooks.onAuthenticated(me);
    } catch (e) {
      regErr.textContent = e.message;
      regErr.classList.remove('hidden');
    }
  });
  registerCard.appendChild(regForm);

  const toRegister = document.createElement('p');
  toRegister.className = 'ui-auth-switch';
  const linkReg = document.createElement('button');
  linkReg.type = 'button';
  linkReg.className = 'ui-link';
  linkReg.textContent = 'Зарегистрироваться';
  linkReg.addEventListener('click', () => {
    loginCard.classList.add('hidden');
    registerCard.classList.remove('hidden');
    toRegister.classList.add('hidden');
    toLogin.classList.remove('hidden');
  });
  toRegister.append(document.createTextNode('Нет аккаунта? '), linkReg);

  const toLogin = document.createElement('p');
  toLogin.className = 'ui-auth-switch hidden';
  const linkLogin = document.createElement('button');
  linkLogin.type = 'button';
  linkLogin.className = 'ui-link';
  linkLogin.textContent = 'Войти';
  linkLogin.addEventListener('click', () => {
    registerCard.classList.add('hidden');
    loginCard.classList.remove('hidden');
    toLogin.classList.add('hidden');
    toRegister.classList.remove('hidden');
  });
  toLogin.append(document.createTextNode('Уже есть аккаунт? '), linkLogin);

  const guestRow = document.createElement('div');
  guestRow.className = 'ui-auth-guest';
  if (typeof hooks.onGuest === 'function') {
    guestRow.appendChild(
      createButton('Просмотр товаров (без входа)', {
        variant: 'ghost',
        className: 'ui-auth-guest-btn',
        onClick: () => hooks.onGuest(),
      }),
    );
  }

  root.append(brand, loginCard, registerCard, toRegister, toLogin, guestRow);
}
