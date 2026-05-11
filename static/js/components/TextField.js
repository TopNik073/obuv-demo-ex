/**
 * @param {{ name: string, label: string, type?: string, value?: string, required?: boolean, readonly?: boolean, autocomplete?: string }} cfg
 */
export function createTextField(cfg) {
  const wrap = document.createElement('label');
  wrap.className = 'ui-field';
  const span = document.createElement('span');
  span.className = 'ui-field__label';
  span.textContent = cfg.label;
  const input = document.createElement('input');
  input.className = 'ui-field__input';
  input.name = cfg.name;
  input.type = cfg.type || 'text';
  input.autocomplete = cfg.autocomplete ?? 'off';
  if (cfg.value != null) input.value = cfg.value;
  if (cfg.required) input.required = true;
  if (cfg.readonly) input.readOnly = true;
  wrap.appendChild(span);
  wrap.appendChild(input);
  return { root: wrap, input };
}

/**
 * @param {{ name: string, label: string, value?: string, required?: boolean, autocomplete?: string }} cfg
 */
export function createTextArea(cfg) {
  const wrap = document.createElement('label');
  wrap.className = 'ui-field';
  const span = document.createElement('span');
  span.className = 'ui-field__label';
  span.textContent = cfg.label;
  const ta = document.createElement('textarea');
  ta.className = 'ui-field__textarea';
  ta.name = cfg.name;
  ta.autocomplete = cfg.autocomplete ?? 'off';
  if (cfg.value != null) ta.value = cfg.value;
  if (cfg.required) ta.required = true;
  wrap.appendChild(span);
  wrap.appendChild(ta);
  return { root: wrap, input: ta };
}
