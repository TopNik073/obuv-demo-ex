import { createIconButton } from '../components/IconButton.js';

/**
 * @param {{ getSort: () => string, getSortDesc: () => boolean, setSort: (s: string) => void, setSortDesc: (d: boolean) => void, onApply: () => void }} api
 */
export function createOrderSortMenu(api) {
  const wrap = document.createElement('div');
  wrap.className = 'ui-sort-menu';

  const panel = document.createElement('div');
  panel.className = 'ui-sort-menu__panel hidden';
  panel.setAttribute('role', 'menu');

  const title = document.createElement('div');
  title.className = 'ui-sort-menu__title';
  title.textContent = 'Сортировка';

  const sortLab = document.createElement('label');
  sortLab.className = 'ui-field__label';
  sortLab.htmlFor = 'order-sort-field-pop';
  sortLab.textContent = 'Поле';

  const sortSel = document.createElement('select');
  sortSel.id = 'order-sort-field-pop';
  sortSel.className = 'ui-select-native';
  sortSel.innerHTML = `
    <option value="">По дате (новые сверху)</option>
    <option value="created_at">Дата создания</option>
    <option value="total_amount">Сумма</option>
    <option value="status">Статус</option>
    <option value="customer">Клиент (логин)</option>
  `;

  const descLab = document.createElement('label');
  descLab.className = 'ui-sort-menu__check';
  const descCb = document.createElement('input');
  descCb.type = 'checkbox';
  const descSpan = document.createElement('span');
  descSpan.textContent = 'По убыванию';
  descLab.append(descCb, descSpan);

  function syncFromState() {
    sortSel.value = api.getSort();
    descCb.checked = api.getSortDesc();
  }

  function apply() {
    api.setSort(sortSel.value);
    api.setSortDesc(descCb.checked);
    panel.classList.add('hidden');
    api.onApply();
  }

  sortSel.addEventListener('change', apply);
  descCb.addEventListener('change', apply);

  panel.append(title, sortLab, sortSel, descLab);

  const btn = createIconButton({
    icon: 'more',
    ariaLabel: 'Сортировка списка заказов',
    variant: 'ghost',
    className: 'ui-sort-menu__trigger',
    onClick: (ev) => {
      ev.stopPropagation();
      syncFromState();
      panel.classList.toggle('hidden');
    },
  });

  function close() {
    panel.classList.add('hidden');
  }

  /** @param {MouseEvent} ev */
  function onDoc(ev) {
    if (!wrap.contains(/** @type {Node} */ (ev.target))) close();
  }

  document.addEventListener('click', onDoc);
  panel.addEventListener('click', (ev) => ev.stopPropagation());

  wrap.append(btn, panel);

  return {
    root: wrap,
    destroy: () => document.removeEventListener('click', onDoc),
  };
}
