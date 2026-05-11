const MIN_DATA_COL = 56;
const DEFAULT_ACTIONS_COL = 82;
const MIN_ACTIONS_COL = 65;

/**
 * @param {HTMLTableElement} table
 * @param {{ storageKey?: string, fixedLastWidth?: number }} [opts]
 * @returns {() => void} cleanup — снять document listeners (если были)
 */
export function attachTableColumnResize(table, opts = {}) {
  if (table._resizeCleanup) {
    table._resizeCleanup();
    table._resizeCleanup = null;
  }

  const storageKey = opts.storageKey;
  const fixedLast = opts.fixedLastWidth ?? DEFAULT_ACTIONS_COL;
  const theadRow = table.querySelector('thead tr');
  if (!theadRow) return () => {};

  const ths = theadRow.querySelectorAll('th');
  const n = ths.length;
  if (n < 2) return () => {};

  table.style.tableLayout = 'fixed';

  let colgroup = table.querySelector('colgroup');
  if (colgroup) colgroup.remove();
  colgroup = document.createElement('colgroup');
  const cols = [];
  for (let i = 0; i < n; i += 1) {
    const col = document.createElement('col');
    if (i === n - 1) col.className = 'ui-table__col--actions';
    colgroup.appendChild(col);
    cols.push(col);
  }
  table.insertBefore(colgroup, table.firstChild);

  function parseStored() {
    if (!storageKey) return null;
    try {
      const raw = localStorage.getItem(storageKey);
      if (!raw) return null;
      const arr = JSON.parse(raw);
      if (!Array.isArray(arr) || arr.length !== n) return null;
      if (!arr.every((x) => typeof x === 'number' && x > 0)) return null;
      return arr;
    } catch {
      return null;
    }
  }

  function applyWidths(px) {
    for (let i = 0; i < n; i += 1) {
      cols[i].style.width = `${Math.round(px[i])}px`;
    }
    if (storageKey) localStorage.setItem(storageKey, JSON.stringify(px.map((x) => Math.round(x))));
  }

  function initialWidths() {
    const wrap = table.closest('.ui-table-wrap');
    const total = Math.max((wrap?.clientWidth ?? table.getBoundingClientRect().width) - 8, n * MIN_DATA_COL);
    const stored = parseStored();
    if (stored) return stored;
    const dataCount = n - 1;
    const rest = Math.max(total - fixedLast, dataCount * MIN_DATA_COL);
    const each = Math.floor(rest / dataCount);
    const w = [];
    for (let i = 0; i < dataCount; i += 1) w.push(each);
    w.push(fixedLast);
    return w;
  }

  function readWidths() {
    return cols.map((c) => {
      const s = c.style.width;
      if (s && s.endsWith('px')) return parseFloat(s);
      return c.getBoundingClientRect().width;
    });
  }

  let widths = initialWidths();
  applyWidths(widths);

  /** @type {(() => void) | null} */
  let removeDocListeners = null;

  function cleanupHandles() {
    table.querySelectorAll('.ui-table__col-resize-handle').forEach((h) => h.remove());
    if (removeDocListeners) {
      removeDocListeners();
      removeDocListeners = null;
    }
  }

  cleanupHandles();

  for (let i = 0; i < n - 1; i += 1) {
    const th = /** @type {HTMLElement} */ (ths[i]);
    const handle = document.createElement('div');
    handle.className = 'ui-table__col-resize-handle';
    handle.setAttribute('role', 'separator');
    handle.setAttribute('aria-orientation', 'vertical');
    handle.title = 'Изменить ширину колонки';

    handle.addEventListener('mousedown', (downEv) => {
      downEv.preventDefault();
      downEv.stopPropagation();
      const startX = downEv.clientX;
      const start = readWidths();
      const isLastPair = i === n - 2;

      function onMove(ev) {
        const dx = ev.clientX - startX;
        let a = start[i] + dx;
        let b = start[i + 1] - dx;
        const minA = MIN_DATA_COL;
        const minB = isLastPair ? MIN_ACTIONS_COL : MIN_DATA_COL;
        if (a < minA) {
          b -= minA - a;
          a = minA;
        }
        if (b < minB) {
          a -= minB - b;
          b = minB;
        }
        const next = start.slice();
        next[i] = a;
        next[i + 1] = b;
        widths = next;
        applyWidths(widths);
      }

      function onUp() {
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
        removeDocListeners = null;
      }

      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
      removeDocListeners = onUp;
    });

    th.appendChild(handle);
  }

  const cleanup = () => {
    cleanupHandles();
  };
  table._resizeCleanup = cleanup;
  return cleanup;
}
