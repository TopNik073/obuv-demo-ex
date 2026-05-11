/**
 * @param {{ name: string, label: string, options: { value: string, label: string }[], value?: string, required?: boolean }} cfg
 */
export function createSelect(cfg) {
  const wrap = document.createElement('label');
  wrap.className = 'ui-field';
  const span = document.createElement('span');
  span.className = 'ui-field__label';
  span.textContent = cfg.label;
  const sel = document.createElement('select');
  sel.className = 'ui-field__select';
  sel.name = cfg.name;
  sel.autocomplete = 'off';
  if (cfg.required) sel.required = true;
  for (const o of cfg.options) {
    const opt = document.createElement('option');
    opt.value = o.value;
    opt.textContent = o.label;
    sel.appendChild(opt);
  }
  if (cfg.value != null) sel.value = cfg.value;
  wrap.appendChild(span);
  wrap.appendChild(sel);
  return { root: wrap, input: sel };
}
