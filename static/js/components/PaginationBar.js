import { createButton } from './Button.js';

/**
 * @param {{ onPageChange: (p: number) => void, onPageSizeChange: (s: number) => void }} handlers
 */
export function createPaginationBar(handlers) {
  const root = document.createElement('div');
  root.className = 'ui-pagination';

  const state = { page: 1, pageSize: 20, rowCount: 0 };

  const prev = createButton('Назад', {
    variant: 'ghost',
    className: 'ui-btn--small',
    onClick: () => {
      if (state.page > 1) handlers.onPageChange(state.page - 1);
    },
  });

  const label = document.createElement('span');
  label.className = 'ui-muted';

  const next = createButton('Вперёд', {
    variant: 'ghost',
    className: 'ui-btn--small',
    onClick: () => {
      if (state.rowCount >= state.pageSize) handlers.onPageChange(state.page + 1);
    },
  });

  const sizeLabel = document.createElement('label');
  sizeLabel.className = 'ui-muted';
  sizeLabel.append(document.createTextNode('На странице '));
  const select = document.createElement('select');
  select.className = 'ui-field__select';
  select.autocomplete = 'off';
  select.style.maxWidth = '5rem';
  for (const n of [10, 20, 50]) {
    const o = document.createElement('option');
    o.value = String(n);
    o.textContent = String(n);
    select.appendChild(o);
  }
  select.addEventListener('change', () => {
    handlers.onPageSizeChange(Number(select.value));
  });
  sizeLabel.appendChild(select);

  root.append(prev, label, next, sizeLabel);

  function redraw() {
    label.textContent = `Страница ${state.page}`;
    prev.disabled = state.page <= 1;
    next.disabled = state.rowCount < state.pageSize;
    select.value = String(state.pageSize);
  }

  /** @param {{ page: number, pageSize: number, rowCount: number }} s */
  function setState(s) {
    Object.assign(state, s);
    redraw();
  }

  redraw();

  return { root, setState };
}
