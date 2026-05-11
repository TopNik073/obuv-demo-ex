import { clearTokens } from '../api.js';
import { setCurrentUser } from '../state.js';
import { roleLabel } from '../utils/roles.js';
import { createButton } from '../components/Button.js';
import { mountProductsSection } from './productsSection.js';
import { mountOrdersSection } from './ordersSection.js';
import { mountUsersSection } from './usersSection.js';

/**
 * @param {HTMLElement} root
 * @param {{ id: string, username: string, full_name: string, role: string }} me
 * @param {{ onLogout: () => void }} hooks
 */
export function mountAppShell(root, me, hooks) {
  root.replaceChildren();
  root.className = 'ui-layout';

  const sidebar = document.createElement('aside');
  sidebar.className = 'ui-sidebar';
  const brand = document.createElement('div');
  brand.className = 'ui-sidebar__brand';
  const logoImg = document.createElement('img');
  logoImg.src = '/static/logo.svg';
  logoImg.alt = '';
  logoImg.className = 'ui-sidebar__logo';
  const brandTitle = document.createElement('span');
  brandTitle.className = 'ui-sidebar__title';
  brandTitle.textContent = 'Обувь — склад';
  brand.append(logoImg, brandTitle);
  const nav = document.createElement('nav');
  nav.className = 'ui-sidebar__nav';

  const content = document.createElement('div');
  content.className = 'ui-content';

  const header = document.createElement('header');
  header.className = 'ui-app-header';
  const headerSpacer = document.createElement('div');
  headerSpacer.className = 'ui-app-header__spacer';
  const userLine = document.createElement('div');
  userLine.className = 'ui-app-header__user';
  userLine.textContent =
    me.role === 'guest' ? 'Гость' : `${me.full_name || me.username} · ${roleLabel(me.role)}`;
  const logout = createButton('Выйти', {
    variant: 'ghost',
    className: 'ui-btn--header',
    onClick: () => {
      clearTokens();
      setCurrentUser(null);
      hooks.onLogout();
    },
  });
  header.append(headerSpacer, userLine, logout);

  const main = document.createElement('main');
  main.className = 'ui-main';
  const outlet = document.createElement('div');
  outlet.id = 'section-outlet';
  outlet.className = 'ui-main-outlet';
  main.appendChild(outlet);

  content.append(header, main);

  /** @type {{ tab: 'products' | 'orders' | 'users', btn: HTMLButtonElement }[]} */
  const navItems = [];

  function renderSection() {
    for (const n of navItems) {
      n.btn.classList.toggle('is-active', n.tab === active);
    }
    outlet.replaceChildren();
    if (active === 'products') mountProductsSection(outlet, me);
    else if (active === 'orders') mountOrdersSection(outlet, me);
    else if (active === 'users') mountUsersSection(outlet, me);
  }

  let active = 'products';

  function addNav(label, tab, visible) {
    if (!visible) return;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'ui-sidebar__item';
    btn.textContent = label;
    btn.addEventListener('click', () => {
      active = tab;
      renderSection();
    });
    nav.appendChild(btn);
    navItems.push({ tab, btn });
  }

  addNav('Товары', 'products', true);
  addNav('Заказы', 'orders', me.role === 'manager' || me.role === 'admin');
  addNav('Пользователи', 'users', me.role === 'admin');

  sidebar.append(brand, nav);
  root.append(sidebar, content);

  renderSection();
}
