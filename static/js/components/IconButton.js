/** Lucide-style pencil */
const ICON_EDIT =
  '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>';

/** Lucide-style trash */
const ICON_DELETE =
  '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>';

/** More horizontal (⋯) */
const ICON_MORE =
  '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>';

/**
 * @param {{ icon: 'edit' | 'delete' | 'more', ariaLabel: string, variant?: 'ghost' | 'danger', className?: string, onClick?: (ev: MouseEvent) => void }} cfg
 */
export function createIconButton(cfg) {
  const variant = cfg.variant ?? 'ghost';
  const el = document.createElement('button');
  el.type = 'button';
  el.className = `ui-btn ui-btn--icon ui-btn--${variant} ${cfg.className || ''}`.trim();
  el.setAttribute('aria-label', cfg.ariaLabel);
  const html =
    cfg.icon === 'delete' ? ICON_DELETE : cfg.icon === 'more' ? ICON_MORE : ICON_EDIT;
  el.innerHTML = html;
  if (cfg.onClick) el.addEventListener('click', cfg.onClick);
  return el;
}
