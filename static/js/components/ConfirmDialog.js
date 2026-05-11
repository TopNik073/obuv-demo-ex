import { createButton } from './Button.js';
import { createModal } from './Modal.js';

/**
 * @param {{ title: string, message: string, confirmLabel?: string }} cfg
 * @returns {Promise<boolean>}
 */
export function confirmDanger(cfg) {
  return new Promise((resolve) => {
    const confirmLabel = cfg.confirmLabel || 'Удалить';

    let backdropRef = null;

    function cleanup() {
      if (backdropRef?.parentNode) backdropRef.parentNode.removeChild(backdropRef);
    }

    const modal = createModal({
      title: cfg.title,
      onClose: () => {
        cleanup();
        resolve(false);
      },
    });
    backdropRef = modal.backdrop;

    const msg = document.createElement('p');
    msg.textContent = cfg.message;

    const actions = document.createElement('div');
    actions.className = 'ui-modal__actions';

    const cancel = createButton('Отмена', {
      variant: 'ghost',
      onClick: () => {
        modal.close();
        cleanup();
        resolve(false);
      },
    });

    const ok = createButton(confirmLabel, {
      variant: 'danger',
      onClick: () => {
        modal.close();
        cleanup();
        resolve(true);
      },
    });

    actions.append(cancel, ok);

    const wrap = document.createElement('div');
    wrap.append(msg, actions);

    modal.setBody(wrap);
    document.body.appendChild(modal.backdrop);
    modal.open();
  });
}
