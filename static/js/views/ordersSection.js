import { api } from '../api.js';
import { listState } from '../state.js';
import { escapeHtml } from '../utils/html.js';
import { formatRub } from '../utils/format.js';
import { orderStatusLabel } from '../utils/roles.js';
import { createPaginationBar } from '../components/PaginationBar.js';
import { createModal } from '../components/Modal.js';
import { createTextField } from '../components/TextField.js';
import { createSelect } from '../components/Select.js';
import { createButton } from '../components/Button.js';
import { createIconButton } from '../components/IconButton.js';
import { confirmDanger } from '../components/ConfirmDialog.js';
import { attachTableColumnResize } from '../utils/tableColumnResize.js';
import { createOrderSortMenu } from '../utils/orderSortMenu.js';

function formatDt(iso) {
  try {
    return new Date(iso).toLocaleString('ru-RU');
  } catch {
    return String(iso);
  }
}

/** @param {{ surname?: string, name?: string, lastname?: string, username: string }} u */
function formatRuUser(u) {
  const parts = [u.surname, u.name, u.lastname].filter(Boolean);
  return parts.length ? parts.join(' ') : u.username;
}

/** @param {string} q */
async function searchUsers(q) {
  const qs = new URLSearchParams({ page: '1', page_size: '40' });
  if (q) qs.set('q', q);
  return api(`/api/v1/users?${qs}`);
}

/** @param {string} q */
async function searchProducts(q) {
  const qs = new URLSearchParams({ page: '1', page_size: '40' });
  if (q) qs.set('q', q);
  return api(`/api/v1/products?${qs}`);
}

/**
 * @param {string} labelText
 * @param {string} [initialCustomerId]
 */
function createUserSearchField(labelText, initialCustomerId) {
  const wrap = document.createElement('div');
  wrap.className = 'ui-picker';
  const lab = document.createElement('label');
  lab.className = 'ui-field__label';
  lab.textContent = labelText;
  const search = document.createElement('input');
  search.type = 'search';
  search.className = 'ui-field__input';
  search.placeholder = 'Логин или ФИО';
  search.autocomplete = 'off';
  const hidden = document.createElement('input');
  hidden.type = 'hidden';
  const list = document.createElement('ul');
  list.className = 'ui-picker__list hidden';
  wrap.append(lab, search, hidden, list);

  async function bootstrap() {
    if (!initialCustomerId) return;
    try {
      const u = await api(`/api/v1/users/${initialCustomerId}`);
      hidden.value = String(u.id);
      search.value = formatRuUser(u);
    } catch {
      hidden.value = String(initialCustomerId);
      search.value = `${String(initialCustomerId).slice(0, 8)}…`;
    }
  }
  void bootstrap();

  let deb;
  search.addEventListener('input', () => {
    clearTimeout(deb);
    deb = setTimeout(async () => {
      const q = search.value.trim();
      if (!q) {
        list.classList.add('hidden');
        return;
      }
      try {
        const rows = await searchUsers(q);
        list.replaceChildren();
        for (const u of rows) {
          const li = document.createElement('li');
          li.className = 'ui-picker__item';
          li.textContent = `${formatRuUser(u)} (${u.username})`;
          li.addEventListener('mousedown', (e) => {
            e.preventDefault();
            hidden.value = String(u.id);
            search.value = formatRuUser(u);
            list.classList.add('hidden');
          });
          list.appendChild(li);
        }
        list.classList.toggle('hidden', rows.length === 0);
      } catch {
        list.classList.add('hidden');
      }
    }, 300);
  });

  search.addEventListener('blur', () => {
    setTimeout(() => list.classList.add('hidden'), 200);
  });

  return {
    root: wrap,
    getCustomerId: () => hidden.value.trim(),
  };
}

/**
 * @param {string} [initialPid]
 * @param {string | number} [initialQty]
 */
function createProductLineRow(initialPid, initialQty) {
  const row = document.createElement('div');
  row.className = 'ui-order-line';
  const prodWrap = document.createElement('div');
  prodWrap.className = 'ui-picker';
  const lab = document.createElement('label');
  lab.className = 'ui-field__label';
  lab.textContent = 'Товар';
  const search = document.createElement('input');
  search.type = 'search';
  search.className = 'ui-field__input';
  search.placeholder = 'Название товара';
  search.autocomplete = 'off';
  const hidden = document.createElement('input');
  hidden.type = 'hidden';
  const list = document.createElement('ul');
  list.className = 'ui-picker__list hidden';
  prodWrap.append(lab, search, hidden, list);

  const qf = createTextField({
    name: 'quantity',
    label: 'Кол-во',
    type: 'number',
    value: String(initialQty != null ? initialQty : 1),
    required: true,
  });
  qf.input.min = '1';

  const rm = createButton('Убрать', {
    variant: 'ghost',
    className: 'ui-btn--small',
    onClick: () => row.remove(),
  });

  row.append(prodWrap, qf.root, rm);

  void (async () => {
    if (!initialPid) return;
    try {
      const pr = await api(`/api/v1/products/${initialPid}`);
      hidden.value = String(pr.id);
      search.value = pr.name;
    } catch {
      hidden.value = String(initialPid);
      search.value = `${String(initialPid).slice(0, 8)}…`;
    }
  })();

  let deb;
  search.addEventListener('input', () => {
    clearTimeout(deb);
    deb = setTimeout(async () => {
      const q = search.value.trim();
      if (!q) {
        list.classList.add('hidden');
        return;
      }
      try {
        const rows = await searchProducts(q);
        list.replaceChildren();
        for (const p of rows) {
          const li = document.createElement('li');
          li.className = 'ui-picker__item';
          li.textContent = `${p.name} · ${formatRub(p.price)}`;
          li.addEventListener('mousedown', (e) => {
            e.preventDefault();
            hidden.value = String(p.id);
            search.value = p.name;
            list.classList.add('hidden');
          });
          list.appendChild(li);
        }
        list.classList.toggle('hidden', rows.length === 0);
      } catch {
        list.classList.add('hidden');
      }
    }, 300);
  });

  search.addEventListener('blur', () => {
    setTimeout(() => list.classList.add('hidden'), 200);
  });

  /** @type {HTMLElement} */
  const rowEl = row;
  rowEl._getOrderLine = () => ({
    product_id: hidden.value.trim(),
    quantity: Number(qf.input.value || 1),
  });

  return { row };
}

/**
 * @param {HTMLElement} host
 * @param {{ id: string, role: string }} me
 */
export function mountOrdersSection(host, me) {
  host.replaceChildren();

  const section = document.createElement('div');
  section.className = 'ui-section';

  const err = document.createElement('div');
  err.className = 'ui-err hidden';

  const toolbar = document.createElement('div');
  toolbar.className = 'ui-toolbar';
  const grow = document.createElement('div');
  grow.className = 'ui-toolbar__grow';
  const { root: qRoot, input: searchInput } = createTextField({
    name: 'orders_q',
    label: 'Поиск (клиент, сумма, статус, № заказа)',
  });
  searchInput.placeholder = 'Запрос';
  searchInput.value = listState.orders.q || '';
  grow.appendChild(qRoot);

  const sortMenu = createOrderSortMenu({
    getSort: () => listState.orders.sort || '',
    getSortDesc: () => Boolean(listState.orders.sortDesc),
    setSort: (s) => {
      listState.orders.sort = s;
      listState.orders.page = 1;
    },
    setSortDesc: (d) => {
      listState.orders.sortDesc = d;
      listState.orders.page = 1;
    },
    onApply: () => load(),
  });

  const end = document.createElement('div');
  end.className = 'ui-toolbar__end';
  if (me.role === 'admin') {
    end.appendChild(
      createButton('Добавить заказ', {
        variant: 'primary',
        onClick: () => {
          void openOrderModal('Новый заказ', null, async (data) => {
            await api('/api/v1/orders', { method: 'POST', body: JSON.stringify(data) });
          });
        },
      }),
    );
  }
  end.appendChild(sortMenu.root);
  toolbar.append(grow, end);

  const pag = createPaginationBar({
    onPageChange: (p) => {
      listState.orders.page = p;
      load();
    },
    onPageSizeChange: (s) => {
      listState.orders.page = 1;
      listState.orders.pageSize = s;
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
    '<thead><tr><th>Статус</th><th>Клиент</th><th>Сумма</th><th>Создан</th><th>Позиции</th><th class="ui-table__actions-col"><span class="ui-sr-only">Действия</span></th></tr></thead>';
  const tbody = document.createElement('tbody');
  table.appendChild(tbody);
  tableWrap.appendChild(table);
  panel.appendChild(tableWrap);

  const dock = document.createElement('div');
  dock.className = 'ui-pagination-dock';
  dock.appendChild(pag.root);

  section.append(err, toolbar, panel, dock);
  host.appendChild(section);

  let orderModal = null;
  function getOrderModal() {
    if (!orderModal) {
      orderModal = createModal({ title: 'Заказ', wide: true });
      section.appendChild(orderModal.backdrop);
    }
    return orderModal;
  }

  async function buildOrderForm(existing) {
    const custField = createUserSearchField('Клиент', existing?.customer_id);
    const linesHost = document.createElement('div');
    linesHost.className = 'ui-order-lines';
    const addLine = createButton('Добавить позицию', {
      variant: 'ghost',
      onClick: () => {
        linesHost.appendChild(createProductLineRow('', 1).row);
      },
    });

    if (existing?.items?.length) {
      for (const it of existing.items) {
        linesHost.appendChild(createProductLineRow(String(it.product_id), String(it.quantity)).row);
      }
    } else {
      linesHost.appendChild(createProductLineRow('', 1).row);
    }

    let statusSel = null;
    if (existing) {
      statusSel = createSelect({
        name: 'status',
        label: 'Статус',
        value: existing.status,
        options: [
          { value: 'pending', label: 'Ожидает' },
          { value: 'confirmed', label: 'Подтверждён' },
          { value: 'cancelled', label: 'Отменён' },
        ],
      });
    }

    const wrap = document.createElement('div');
    wrap.appendChild(custField.root);
    if (statusSel) wrap.appendChild(statusSel.root);
    wrap.appendChild(linesHost);
    wrap.appendChild(addLine);

    return {
      root: wrap,
      getData: () => {
        const items = [];
        for (const row of linesHost.querySelectorAll('.ui-order-line')) {
          const fn = /** @type {{ _getOrderLine?: () => { product_id: string, quantity: number } }} */ (row)
            ._getOrderLine;
          if (typeof fn === 'function') {
            const line = fn();
            if (line.product_id) items.push(line);
          }
        }
        const base = { customer_id: custField.getCustomerId(), items };
        if (statusSel) base.status = statusSel.input.value;
        return base;
      },
    };
  }

  async function openOrderModal(title, existing, onSave) {
    const modal = getOrderModal();
    modal.close();
    const { root, getData } = await buildOrderForm(existing);
    const actions = document.createElement('div');
    actions.className = 'ui-modal__actions';
    const cancel = createButton('Отмена', {
      variant: 'ghost',
      onClick: () => modal.close(),
    });
    const save = createButton('Сохранить', {
      variant: 'primary',
      onClick: async () => {
        try {
          const data = getData();
          if (!data.customer_id) {
            alert('Выберите клиента: введите запрос и выберите строку из списка');
            return;
          }
          if (!data.items?.length) {
            alert('Добавьте позиции: для каждой строки выберите товар из списка');
            return;
          }
          await onSave(data);
          await load();
          modal.close();
        } catch (e) {
          alert(e.message);
        }
      },
    });
    actions.append(cancel, save);
    const wrap = document.createElement('div');
    wrap.append(root, actions);
    const titleEl = modal.backdrop.querySelector('.ui-modal__title');
    if (titleEl) titleEl.textContent = title;
    modal.setBody(wrap);
    modal.open();
  }

  async function load() {
    err.classList.add('hidden');
    try {
      const qs = new URLSearchParams();
      qs.set('page', String(listState.orders.page));
      qs.set('page_size', String(listState.orders.pageSize));
      if (searchInput.value.trim()) qs.set('q', searchInput.value.trim());
      if (listState.orders.sort) {
        qs.set('sort', listState.orders.sort);
        qs.set('sort_desc', listState.orders.sortDesc ? 'true' : 'false');
      }
      qs.set('_ts', String(Date.now()));
      const rows = await api(`/api/v1/orders?${qs}`);
      pag.setState({
        page: listState.orders.page,
        pageSize: listState.orders.pageSize,
        rowCount: rows.length,
      });
      tbody.replaceChildren();
      for (const o of rows) {
        const lines = (o.items || [])
          .map((it) => {
            const label = it.product_name || `${String(it.product_id).slice(0, 8)}…`;
            return `${label} ×${it.quantity}`;
          })
          .join(', ');
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${escapeHtml(orderStatusLabel(o.status))}</td>
          <td>${escapeHtml(o.customer_label || '—')}</td>
          <td>${escapeHtml(formatRub(o.total_amount))}</td>
          <td>${escapeHtml(formatDt(o.created_at))}</td>
          <td>${escapeHtml(lines || '—')}</td>
        `;
        const td = document.createElement('td');
        td.className = 'ui-table__actions';
        if (me.role === 'admin') {
          const inner = document.createElement('div');
          inner.className = 'ui-table__actions-inner';
          inner.appendChild(
            createIconButton({
              icon: 'edit',
              ariaLabel: 'Изменить',
              variant: 'ghost',
              onClick: () => {
                void openOrderModal('Изменить заказ', o, async (data) => {
                  const body = {
                    status: data.status,
                    customer_id: data.customer_id,
                    items: data.items,
                  };
                  await api(`/api/v1/orders/${o.id}`, {
                    method: 'PATCH',
                    body: JSON.stringify(body),
                  });
                });
              },
            }),
          );
          inner.appendChild(
            createIconButton({
              icon: 'delete',
              ariaLabel: 'Удалить',
              variant: 'danger',
              onClick: async () => {
                const ok = await confirmDanger({
                  title: 'Удалить заказ',
                  message: 'Заказ будет удалён безвозвратно. Продолжить?',
                });
                if (!ok) return;
                await api(`/api/v1/orders/${o.id}`, { method: 'DELETE' });
                await load();
              },
            }),
          );
          td.appendChild(inner);
        } else {
          td.textContent = '—';
        }
        tr.appendChild(td);
        tbody.appendChild(tr);
      }
      requestAnimationFrame(() => {
        attachTableColumnResize(table, { storageKey: 'obuv_cols_orders_v3', fixedLastWidth: 90 });
      });
    } catch (e) {
      err.textContent = e.message;
      err.classList.remove('hidden');
    }
  }

  let searchDeb;
  searchInput.addEventListener('input', () => {
    clearTimeout(searchDeb);
    searchDeb = setTimeout(() => {
      listState.orders.q = searchInput.value;
      listState.orders.page = 1;
      load();
    }, 400);
  });

  load();
}
