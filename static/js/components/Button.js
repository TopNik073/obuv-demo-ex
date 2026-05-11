/**
 * @param {string} label
 * @param {{ variant?: 'primary' | 'ghost' | 'danger', type?: string, className?: string, onClick?: () => void }} [opts]
 */
export function createButton(label, opts = {}) {
  const { variant = 'primary', type = 'button', className = '', onClick } = opts;
  const el = document.createElement('button');
  el.type = type;
  el.className = `ui-btn ui-btn--${variant} ${className}`.trim();
  el.textContent = label;
  if (onClick) el.addEventListener('click', onClick);
  return el;
}
