import { createIconButton } from '../components/IconButton.js';

/**
 * Меню сортировки (⋯): панель с полем и направлением.
 * @param {{ getSort: () => string, getSortDesc: () => boolean, setSort: (s: string) => void, setSortDesc: (d: boolean) => void, onApply: () => void }} api
 */
export function createProductSortMenu(api) {
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
  sortLab.htmlFor = 'product-sort-field-pop';
  sortLab.textContent = 'Поле';

  const sortSel = document.createElement('select');
  sortSel.id = 'product-sort-field-pop';
  sortSel.className = 'ui-select-native';
  sortSel.innerHTML = `
    <option value="">По умолчанию</option>
    <option value="name">Название</option>
    <option value="price">Цена</option>
    <option value="quantity">Остаток</option>
    <option value="category">Категория</option>
    <option value="discount_percent">Скидка %</option>
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
    ariaLabel: 'Сортировка списка',
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
