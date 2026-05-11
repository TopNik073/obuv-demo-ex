import { api } from '../api.js';
import { listState } from '../state.js';
import { escapeHtml } from '../utils/html.js';
import { createPaginationBar } from '../components/PaginationBar.js';
import { createModal } from '../components/Modal.js';
import { createTextField } from '../components/TextField.js';
import { createSelect } from '../components/Select.js';
import { createButton } from '../components/Button.js';
import { createIconButton } from '../components/IconButton.js';
import { confirmDanger } from '../components/ConfirmDialog.js';
import { attachTableColumnResize } from '../utils/tableColumnResize.js';
import { createUserSortMenu } from '../utils/userSortMenu.js';
import { roleLabel } from '../utils/roles.js';

const ROLE_OPTIONS = [
  { value: 'client', label: 'Клиент' },
  { value: 'manager', label: 'Менеджер' },
  { value: 'admin', label: 'Администратор' },
];

/**
 * @param {HTMLElement} host
 * @param {{ id: string }} me
 */
export function mountUsersSection(host, me) {
  host.replaceChildren();

  const section = document.createElement('div');
  section.className = 'ui-section';

  const err = document.createElement('div');
  err.className = 'ui-err hidden';

  const toolbar = document.createElement('div');
  toolbar.className = 'ui-toolbar';
  const grow = document.createElement('div');
  grow.className = 'ui-toolbar__grow';
  const { root: qRoot, input: qInput } = createTextField({
    name: 'q',
    label: 'Поиск (логин, имя, фамилия, отчество)',
  });
  qInput.placeholder = 'Запрос';
  grow.appendChild(qRoot);
  toolbar.appendChild(grow);

  const roleFilter = createSelect({
    name: 'role_filter',
    label: 'Роль',
    value: listState.users.role || '',
    options: [
      { value: '', label: 'Все роли' },
      ...ROLE_OPTIONS,
    ],
  });

  const sortMenu = createUserSortMenu({
    getSort: () => listState.users.sort || '',
    getSortDesc: () => Boolean(listState.users.sortDesc),
    setSort: (s) => {
      listState.users.sort = s;
      listState.users.page = 1;
    },
    setSortDesc: (d) => {
      listState.users.sortDesc = d;
      listState.users.page = 1;
    },
    onApply: () => load(),
  });

  const end = document.createElement('div');
  end.className = 'ui-toolbar__end';
  end.appendChild(roleFilter.root);
  end.appendChild(
    createButton('Добавить пользователя', {
      variant: 'primary',
      onClick: () => openUserModal('Новый пользователь', null),
    }),
  );
  end.appendChild(sortMenu.root);
  toolbar.appendChild(end);

  const pag = createPaginationBar({
    onPageChange: (p) => {
      listState.users.page = p;
      load();
    },
    onPageSizeChange: (s) => {
      listState.users.page = 1;
      listState.users.pageSize = s;
      load();
    },
  });

  const panel = document.createElement('div');
  panel.className = 'ui-panel';

  const tableWrap = document.createElement('div');
  tableWrap.className = 'ui-table-wrap';
  const table = document.createElement('table');
  table.className = 'ui-table';
  table.innerHTML =
    '<thead><tr><th>Логин</th><th>Имя</th><th>Роль</th><th>Создан</th><th class="ui-table__actions-col"><span class="ui-sr-only">Действия</span></th></tr></thead>';
  const tbody = document.createElement('tbody');
  table.appendChild(tbody);
  tableWrap.appendChild(table);
  panel.appendChild(tableWrap);

  const dock = document.createElement('div');
  dock.className = 'ui-pagination-dock';
  dock.appendChild(pag.root);

  section.append(err, toolbar, panel, dock);
  host.appendChild(section);

  let userModal = null;
  function getUserModal() {
    if (!userModal) {
      userModal = createModal({ title: 'Пользователь' });
      section.appendChild(userModal.backdrop);
    }
    return userModal;
  }

  function buildUserForm(u) {
    const username = createTextField({
      name: 'username',
      label: 'Логин',
      value: u?.username || '',
      required: true,
    });
    const password = createTextField({
      name: 'password',
      label: u ? 'Новый пароль (оставьте пустым, чтобы не менять)' : 'Пароль (≥ 6 символов)',
      type: 'password',
      required: !u,
    });
    if (!u) password.input.minLength = 6;
    const name = createTextField({ name: 'name', label: 'Имя', value: u?.name || '' });
    const surname = createTextField({ name: 'surname', label: 'Фамилия', value: u?.surname || '' });
    const lastname = createTextField({ name: 'lastname', label: 'Отчество', value: u?.lastname || '' });
    const role = createSelect({
      name: 'role',
      label: 'Роль',
      value: u?.role || 'client',
      options: ROLE_OPTIONS,
      required: true,
    });
    const wrap = document.createElement('div');
    wrap.append(username.root, password.root, name.root, surname.root, lastname.root, role.root);
    return {
      root: wrap,
      getData: () => {
        const pwd = password.input.value;
        const body = {
          username: username.input.value.trim(),
          name: name.input.value || '',
          surname: surname.input.value || '',
          lastname: lastname.input.value || '',
          role: role.input.value,
        };
        if (pwd) body.password = pwd;
        return body;
      },
    };
  }

  function openUserModal(title, u) {
    const userModal = getUserModal();
    userModal.close();
    const { root, getData } = buildUserForm(u);
    const actions = document.createElement('div');
    actions.className = 'ui-modal__actions';
    const cancel = createButton('Отмена', {
      variant: 'ghost',
      onClick: () => userModal.close(),
    });
    const save = createButton('Сохранить', {
      variant: 'primary',
      onClick: async () => {
        try {
          const data = getData();
          if (!u && (!data.password || data.password.length < 6)) {
            alert('Пароль не короче 6 символов');
            return;
          }
          if (u) {
            const patch = {};
            if (data.username) patch.username = data.username;
            if (data.password) patch.password = data.password;
            patch.name = data.name;
            patch.surname = data.surname;
            patch.lastname = data.lastname;
            patch.role = data.role;
            await api(`/api/v1/users/${u.id}`, { method: 'PATCH', body: JSON.stringify(patch) });
          } else {
            if (!data.password) {
              alert('Укажите пароль');
              return;
            }
            await api('/api/v1/users', { method: 'POST', body: JSON.stringify(data) });
          }
          await load();
          userModal.close();
        } catch (e) {
          alert(e.message);
        }
      },
    });
    actions.append(cancel, save);
    const wrap = document.createElement('div');
    wrap.append(root, actions);
    const titleEl = userModal.backdrop.querySelector('.ui-modal__title');
    if (titleEl) titleEl.textContent = title;
    userModal.setBody(wrap);
    userModal.open();
  }

  async function load() {
    err.classList.add('hidden');
    try {
      const qs = new URLSearchParams();
      qs.set('page', String(listState.users.page));
      qs.set('page_size', String(listState.users.pageSize));
      if (qInput.value.trim()) qs.set('q', qInput.value.trim());
      if (listState.users.role) qs.set('role', listState.users.role);
      if (listState.users.sort) {
        qs.set('sort', listState.users.sort);
        qs.set('sort_desc', listState.users.sortDesc ? 'true' : 'false');
      }
      qs.set('_ts', String(Date.now()));
      const rows = await api(`/api/v1/users?${qs}`);
      pag.setState({
        page: listState.users.page,
        pageSize: listState.users.pageSize,
        rowCount: rows.length,
      });
      tbody.replaceChildren();
      for (const u of rows) {
        const full = [u.surname, u.name, u.lastname].filter(Boolean).join(' ');
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${escapeHtml(u.username)}</td>
          <td>${escapeHtml(full || '—')}</td>
          <td>${escapeHtml(roleLabel(u.role))}</td>
          <td>${escapeHtml(u.created_at ? new Date(u.created_at).toLocaleString('ru-RU') : '—')}</td>
        `;
        const td = document.createElement('td');
        td.className = 'ui-table__actions';
        const inner = document.createElement('div');
        inner.className = 'ui-table__actions-inner';
        inner.appendChild(
          createIconButton({
            icon: 'edit',
            ariaLabel: 'Изменить',
            variant: 'ghost',
            onClick: () => openUserModal('Изменить пользователя', u),
          }),
        );
        inner.appendChild(
          createIconButton({
            icon: 'delete',
            ariaLabel: 'Удалить',
            variant: 'danger',
            onClick: async () => {
              if (u.id === me.id) {
                alert('Нельзя удалить собственную учётную запись');
                return;
              }
              const ok = await confirmDanger({
                title: 'Удалить пользователя',
                message:
                  'Пользователь и все его заказы будут удалены. Это действие необратимо. Продолжить?',
              });
              if (!ok) return;
              await api(`/api/v1/users/${u.id}`, { method: 'DELETE' });
              await load();
            },
          }),
        );
        td.appendChild(inner);
        tr.appendChild(td);
        tbody.appendChild(tr);
      }
      requestAnimationFrame(() => {
        attachTableColumnResize(table, { storageKey: 'obuv_cols_users_v3', fixedLastWidth: 90 });
      });
    } catch (e) {
      err.textContent = e.message;
      err.classList.remove('hidden');
    }
  }

  let t;
  qInput.addEventListener('input', () => {
    clearTimeout(t);
    t = setTimeout(() => {
      listState.users.page = 1;
      load();
    }, 400);
  });

  roleFilter.input.addEventListener('change', () => {
    listState.users.role = roleFilter.input.value;
    listState.users.page = 1;
    load();
  });

  load();
}
