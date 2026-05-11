/** @type {{ id: string, username: string, full_name: string, role: string } | null} */
export let currentUser = null;

/** @param {{ id: string, username: string, full_name: string, role: string } | null} u */
export function setCurrentUser(u) {
  currentUser = u;
}

export const listState = {
  products: { page: 1, pageSize: 20, sort: '', sortDesc: false },
  orders: { page: 1, pageSize: 20, sort: '', sortDesc: true, q: '' },
  users: { page: 1, pageSize: 20, role: '', sort: '', sortDesc: false },
};

/** @type {'products' | 'orders' | 'users'} */
export let activeSection = 'products';

/** @param {'products' | 'orders' | 'users'} s */
export function setActiveSection(s) {
  activeSection = s;
}
