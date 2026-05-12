import { api } from '../api.js';
import { listState } from '../state.js';
import { formatRub } from '../utils/format.js';
import { createPaginationBar } from '../components/PaginationBar.js';
import { createModal } from '../components/Modal.js';
import { createTextField, createTextArea } from '../components/TextField.js';
import { createButton } from '../components/Button.js';
import { createIconButton } from '../components/IconButton.js';
import { confirmDanger } from '../components/ConfirmDialog.js';
import { attachTableColumnResize } from '../utils/tableColumnResize.js';
import { createProductSortMenu } from '../utils/productSortMenu.js';

const PLACEHOLDER_IMG = '/static/picture.png';

/**
 * @param {HTMLElement} host
 * @param {{ id: string, role: string }} me
 */
export function mountProductsSection(host, me) {
  host.replaceChildren();

  const section = document.createElement('div');
  section.className = 'ui-section';

  const err = document.createElement('div');
  err.className = 'ui-err hidden';

  const toolbar = document.createElement('div');
  toolbar.className = 'ui-toolbar';
  const grow = document.createElement('div');
  grow.className = 'ui-toolbar__grow';

  /** @type {HTMLInputElement | null} */
  let searchInput = null;
  if (me.role === 'manager' || me.role === 'admin') {
    const { root, input } = createTextField({
      name: 'q',
      label: 'Поиск (название, категория, производитель, поставщик, цена, скидка %)',
    });
    input.placeholder = 'Запрос';
    grow.appendChild(root);
    searchInput = input;
  }
  toolbar.appendChild(grow);

  if (me.role === 'manager' || me.role === 'admin') {
    const sortMenu = createProductSortMenu({
      getSort: () => listState.products.sort || '',
      getSortDesc: () => Boolean(listState.products.sortDesc),
      setSort: (s) => {
        listState.products.sort = s;
        listState.products.page = 1;
      },
      setSortDesc: (d) => {
        listState.products.sortDesc = d;
        listState.products.page = 1;
      },
      onApply: () => load(),
    });

    const end = document.createElement('div');
    end.className = 'ui-toolbar__end';
    if (me.role === 'admin') {
      const fileIn = document.createElement('input');
      fileIn.type = 'file';
      fileIn.accept = '.csv,text/csv';
      fileIn.className = 'hidden';
      fileIn.addEventListener('change', async () => {
        const f = fileIn.files?.[0];
        fileIn.value = '';
        if (!f) return;
        const fd = new FormData();
        fd.append('file', f);
        try {
          const res = await api('/api/v1/products/import', { method: 'POST', body: fd });
          alert(`Импортировано строк: ${res.created}`);
          await load();
        } catch (e) {
          alert(e.message);
        }
      });
      end.appendChild(
        createButton('Импорт CSV', {
          variant: 'ghost',
          onClick: () => fileIn.click(),
        }),
      );
      end.appendChild(fileIn);
      end.appendChild(
        createButton('Добавить', {
          variant: 'primary',
          onClick: () => {
            openModal(
              'Новый товар',
              () => buildProductForm(null),
              async (data) => {
                await api('/api/v1/products', { method: 'POST', body: JSON.stringify(data) });
              },
            );
          },
        }),
      );
    }
    end.appendChild(sortMenu.root);
    toolbar.appendChild(end);
  }

  const pag = createPaginationBar({
    onPageChange: (p) => {
      listState.products.page = p;
      load();
    },
    onPageSizeChange: (s) => {
      listState.products.page = 1;
      listState.products.pageSize = s;
      load();
    },
  });

  const panel = document.createElement('div');
  panel.className = 'ui-panel';

  const tableWrap = document.createElement('div');
  tableWrap.className = 'ui-table-wrap';
  const table = document.createElement('table');
  table.className = 'ui-table';
  const thead = document.createElement('thead');
  const htr = document.createElement('tr');
  const baseHeaders = [
    'Фото',
    'Наименование',
    'Категория',
    'Описание',
    'Производитель',
    'Поставщик',
    'Цена',
    'Ед. изм.',
    'Остаток',
    'Скидка %',
  ];
  for (const label of baseHeaders) {
    const th = document.createElement('th');
    th.textContent = label;
    htr.appendChild(th);
  }
  if (me.role === 'admin') {
    const tha = document.createElement('th');
    tha.className = 'ui-table__actions-col';
    const sr = document.createElement('span');
    sr.className = 'ui-sr-only';
    sr.textContent = 'Действия';
    tha.appendChild(sr);
    htr.appendChild(tha);
  }
  thead.appendChild(htr);
  table.appendChild(thead);
  const tbody = document.createElement('tbody');
  table.appendChild(tbody);
  tableWrap.appendChild(table);
  panel.appendChild(tableWrap);

  const dock = document.createElement('div');
  dock.className = 'ui-pagination-dock';
  dock.appendChild(pag.root);

  section.append(err, toolbar, panel, dock);
  host.appendChild(section);

  let productModal = null;
  function getProductModal() {
    if (!productModal) {
      productModal = createModal({ title: 'Товар' });
      section.appendChild(productModal.backdrop);
    }
    return productModal;
  }

  function openModal(title, bodyFactory, onSave) {
    const productModal = getProductModal();
    productModal.close();
    const { root, getData } = bodyFactory();
    const actions = document.createElement('div');
    actions.className = 'ui-modal__actions';
    const cancel = createButton('Отмена', {
      variant: 'ghost',
      onClick: () => {
        productModal.close();
      },
    });
    const save = createButton('Сохранить', {
      variant: 'primary',
      onClick: async () => {
        try {
          await onSave(getData());
          await load();
          productModal.close();
        } catch (e) {
          alert(e.message);
        }
      },
    });
    actions.append(cancel, save);
    const wrap = document.createElement('div');
    wrap.append(root, actions);
    const titleEl = productModal.backdrop.querySelector('.ui-modal__title');
    if (titleEl) titleEl.textContent = title;
    productModal.setBody(wrap);
    productModal.open();
  }

  function buildProductForm(p) {
    const n = createTextField({
      name: 'name',
      label: 'Наименование',
      value: p?.name || '',
      required: true,
    });
    const d = createTextArea({
      name: 'description',
      label: 'Описание',
      value: p?.description || '',
    });
    const cat = createTextField({
      name: 'category',
      label: 'Категория',
      value: p?.category || '',
    });
    const man = createTextField({
      name: 'manufacturer',
      label: 'Производитель',
      value: p?.manufacturer || '',
    });
    const sup = createTextField({
      name: 'supplier',
      label: 'Поставщик',
      value: p?.supplier || '',
    });
    const unit = createTextField({
      name: 'unit',
      label: 'Ед. изм.',
      value: p?.unit || '',
    });
    const img = createTextField({
      name: 'image_url',
      label: 'URL изображения',
      value: p?.image_url || '',
    });
    const basePrice = createTextField({
      name: 'base_price',
      label: 'Базовая цена',
      type: 'number',
      value: p?.base_price != null ? String(p.base_price) : '',
    });
    basePrice.input.step = '0.01';
    basePrice.input.min = '0';
    const disc = createTextField({
      name: 'discount_percent',
      label: 'Скидка, %',
      type: 'number',
      value: p != null ? String(p.discount_percent ?? 0) : '0',
      required: true,
    });
    disc.input.step = '1';
    disc.input.min = '0';
    disc.input.max = '100';
    const price = createTextField({
      name: 'price',
      label: 'Цена продажи',
      type: 'number',
      value: p != null ? String(p.price) : '',
      required: true,
    });
    price.input.step = '0.01';
    price.input.min = '0';
    const qty = createTextField({
      name: 'quantity',
      label: 'Количество на складе',
      type: 'number',
      value: p != null ? String(p.quantity) : '0',
      required: true,
    });
    qty.input.step = '1';
    qty.input.min = '0';

    let syncGuard = false;
    const round2 = (v) => Math.round(v * 100) / 100;

    /** @param {HTMLInputElement} inp */
    function parseMoney(inp) {
      const t = inp.value.trim().replace(',', '.');
      if (t === '') return null;
      const n = Number(t);
      return Number.isFinite(n) ? n : null;
    }

    function baseOk() {
      const b = parseMoney(basePrice.input);
      return b != null && b > 0;
    }

    function syncPriceFromDiscount() {
      if (syncGuard || !baseOk()) return;
      const b = parseMoney(basePrice.input);
      const d = Math.min(100, Math.max(0, Number(disc.input.value || 0)));
      if (b == null || b <= 0) return;
      syncGuard = true;
      price.input.value = String(round2(b * (1 - d / 100)));
      syncGuard = false;
    }

    function syncDiscountFromPrice() {
      if (syncGuard || !baseOk()) return;
      const b = parseMoney(basePrice.input);
      const pr = parseMoney(price.input);
      if (b == null || b <= 0 || pr == null || pr < 0) return;
      let d = (1 - pr / b) * 100;
      d = Math.min(100, Math.max(0, Math.round(d)));
      syncGuard = true;
      disc.input.value = String(d);
      syncGuard = false;
    }

    function onBaseInput() {
      if (syncGuard) return;
      if (baseOk()) syncPriceFromDiscount();
    }

    basePrice.input.addEventListener('input', onBaseInput);
    disc.input.addEventListener('input', syncPriceFromDiscount);
    price.input.addEventListener('input', syncDiscountFromPrice);

    const wrap = document.createElement('div');
    wrap.append(
      n.root,
      d.root,
      cat.root,
      man.root,
      sup.root,
      unit.root,
      img.root,
      basePrice.root,
      disc.root,
      price.root,
      qty.root,
    );
    return {
      root: wrap,
      getData: () => {
        const baseRaw = basePrice.input.value.trim();
        const discount_percent = Number(disc.input.value || 0);
        return {
          name: n.input.value,
          description: d.input.value || null,
          category: cat.input.value.trim() || null,
          manufacturer: man.input.value.trim() || null,
          supplier: sup.input.value.trim() || null,
          unit: unit.input.value.trim() || null,
          image_url: img.input.value.trim() || null,
          base_price: baseRaw === '' ? null : baseRaw,
          price: price.input.value,
          discount_percent,
          quantity: Number(qty.input.value || 0),
        };
      },
    };
  }

  function appendPriceCell(td, p) {
    const bp = p.base_price != null ? Number(p.base_price) : null;
    const pr = Number(p.price);
    if (bp != null && !Number.isNaN(bp) && !Number.isNaN(pr) && bp > pr) {
      const old = document.createElement('span');
      old.className = 'ui-price--old';
      old.textContent = formatRub(p.base_price);
      const neu = document.createElement('span');
      neu.className = 'ui-price--new';
      neu.textContent = formatRub(p.price);
      td.append(old, document.createTextNode(' '), neu);
    } else {
      td.textContent = formatRub(p.price);
    }
  }

  function appendThumb(td, p) {
    td.classList.add('ui-table__cell--thumb');
    const img = document.createElement('img');
    img.className = 'ui-product-thumb';
    img.alt = '';
    img.decoding = 'sync';
    img.loading = 'eager';
    const u = (p.image_url || '').trim();
    const applySrc = (url) => {
      img.src = url;
    };
    if (u.startsWith('http://') || u.startsWith('https://')) {
      img.referrerPolicy = 'no-referrer';
      applySrc(u);
    } else {
      applySrc(PLACEHOLDER_IMG);
    }
    img.addEventListener('error', () => {
      if (img.dataset.fallback === '1') return;
      img.dataset.fallback = '1';
      img.removeAttribute('referrerpolicy');
      applySrc(PLACEHOLDER_IMG);
    });
    td.appendChild(img);
  }

  async function load() {
    err.classList.add('hidden');
    try {
      const qs = new URLSearchParams();
      qs.set('page', String(listState.products.page));
      qs.set('page_size', String(listState.products.pageSize));
      if (searchInput && searchInput.value.trim()) qs.set('q', searchInput.value.trim());
      if (listState.products.sort) {
        qs.set('sort', listState.products.sort);
        qs.set('sort_desc', listState.products.sortDesc ? 'true' : 'false');
      }
      qs.set('_ts', String(Date.now()));
      const rows = await api(`/api/v1/products?${qs}`);
      pag.setState({
        page: listState.products.page,
        pageSize: listState.products.pageSize,
        rowCount: rows.length,
      });
      tbody.replaceChildren();
      for (const p of rows) {
        const tr = document.createElement('tr');
        const rawQty = Number(p.quantity);
        const qty = Number.isFinite(rawQty) ? Math.trunc(rawQty) : null;
        const rawDisc = Number(p.discount_percent ?? 0);
        const disc = Number.isFinite(rawDisc) ? rawDisc : 0;
        if (qty === 0) {
          tr.classList.add('ui-row--out-stock');
          tr.title = 'Нет на складе';
        } else if (disc > 15) {
          tr.classList.add('ui-row--discount-high');
          tr.title = 'Скидка более 15%';
        }

        const td0 = document.createElement('td');
        appendThumb(td0, p);
        tr.appendChild(td0);

        for (const text of [
          p.name,
          p.category || '—',
          p.description || '—',
          p.manufacturer || '—',
          p.supplier || '—',
        ]) {
          const td = document.createElement('td');
          td.textContent = text;
          tr.appendChild(td);
        }

        const tdPrice = document.createElement('td');
        appendPriceCell(tdPrice, p);
        tr.appendChild(tdPrice);

        const tdUnit = document.createElement('td');
        tdUnit.textContent = p.unit || '—';
        tr.appendChild(tdUnit);

        const tdQty = document.createElement('td');
        tdQty.textContent = String(p.quantity);
        tr.appendChild(tdQty);

        const tdDisc = document.createElement('td');
        tdDisc.textContent = `${disc}%`;
        tr.appendChild(tdDisc);

        if (me.role === 'admin') {
          const td = document.createElement('td');
          td.className = 'ui-table__actions';
          const inner = document.createElement('div');
          inner.className = 'ui-table__actions-inner';
          inner.appendChild(
            createIconButton({
              icon: 'edit',
              ariaLabel: 'Изменить',
              variant: 'ghost',
              onClick: () => {
                openModal(
                  'Изменить товар',
                  () => buildProductForm(p),
                  async (data) => {
                    await api(`/api/v1/products/${p.id}`, {
                      method: 'PATCH',
                      body: JSON.stringify(data),
                    });
                  },
                );
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
                  title: 'Удалить товар',
                  message:
                    'Товар будет удалён. Связанные позиции в заказах будут сняты, суммы заказов пересчитаны. Продолжить?',
                });
                if (!ok) return;
                await api(`/api/v1/products/${p.id}`, { method: 'DELETE' });
                await load();
              },
            }),
          );
          td.appendChild(inner);
          tr.appendChild(td);
        }
        tbody.appendChild(tr);
      }
      requestAnimationFrame(() => {
        if (me.role === 'admin') {
          attachTableColumnResize(table, { storageKey: 'obuv_cols_products_v2', fixedLastWidth: 90 });
        }
      });
    } catch (e) {
      err.textContent = e.message;
      err.classList.remove('hidden');
    }
  }

  if (searchInput) {
    let t;
    searchInput.addEventListener('input', () => {
      clearTimeout(t);
      t = setTimeout(() => {
        listState.products.page = 1;
        load();
      }, 400);
    });
  }

  load();
}
