/**
 * @param {{ title: string, onClose?: () => void, wide?: boolean }} cfg
 */
export function createModal(cfg) {
  const backdrop = document.createElement('div');
  backdrop.className = 'ui-modal-backdrop hidden';
  backdrop.setAttribute('role', 'dialog');
  backdrop.setAttribute('aria-modal', 'true');

  const panel = document.createElement('div');
  panel.className = cfg.wide ? 'ui-modal ui-modal--wide' : 'ui-modal';
  panel.addEventListener('click', (e) => e.stopPropagation());

  const title = document.createElement('h2');
  title.className = 'ui-modal__title';
  title.textContent = cfg.title;

  const body = document.createElement('div');
  body.className = 'ui-modal__body';

  panel.appendChild(title);
  panel.appendChild(body);
  backdrop.appendChild(panel);

  function onBackdropClick() {
    close();
    cfg.onClose?.();
  }
  backdrop.addEventListener('click', onBackdropClick);

  /** @param {KeyboardEvent} e */
  function onKey(e) {
    if (e.key === 'Escape') {
      close();
      cfg.onClose?.();
    }
  }

  function open() {
    backdrop.classList.remove('hidden');
    document.body.classList.add('ui-no-scroll');
    document.addEventListener('keydown', onKey);
  }

  function close() {
    backdrop.classList.add('hidden');
    document.body.classList.remove('ui-no-scroll');
    document.removeEventListener('keydown', onKey);
  }

  /** @param {HTMLElement} node */
  function setBody(node) {
    body.innerHTML = '';
    body.appendChild(node);
  }

  return { backdrop, open, close, setBody, body };
}
