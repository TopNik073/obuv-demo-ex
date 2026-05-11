const rubFormatter = new Intl.NumberFormat('ru-RU', {
  style: 'currency',
  currency: 'RUB',
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

/**
 * Число/строка из API → формат «10 000 ₽» (группировка и символ рубля).
 * @param {string | number} value
 */
export function formatRub(value) {
  const n = typeof value === 'string' ? Number(value.replace(',', '.')) : Number(value);
  if (Number.isNaN(n)) return String(value);
  return rubFormatter.format(n);
}
