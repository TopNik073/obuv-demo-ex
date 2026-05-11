const ROLE_RU = {
  guest: 'Гость',
  client: 'Клиент',
  manager: 'Менеджер',
  admin: 'Администратор',
};

/** @param {string} role */
export function roleLabel(role) {
  return ROLE_RU[role] ?? role;
}

export const ORDER_STATUS_RU = {
  pending: 'Ожидает',
  confirmed: 'Подтверждён',
  cancelled: 'Отменён',
};

/** @param {string} status */
export function orderStatusLabel(status) {
  return ORDER_STATUS_RU[status] ?? status;
}
