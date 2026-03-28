/**
 * FoodCourt API Client
 * Shared across customer.html, vendor.html, admin.html
 * Base URL points to Flask running on localhost:5000
 */

const API_BASE = '/api';

// ── Token Storage ────────────────────────────────────────
const Auth = {
  getToken:   ()      => localStorage.getItem('fc_token'),
  setToken:   (t)     => localStorage.setItem('fc_token', t),
  getUser:    ()      => JSON.parse(localStorage.getItem('fc_user') || 'null'),
  setUser:    (u)     => localStorage.setItem('fc_user', JSON.stringify(u)),
  clear:      ()      => { localStorage.removeItem('fc_token'); localStorage.removeItem('fc_user'); },
  isLoggedIn: ()      => !!localStorage.getItem('fc_token'),
};

// ── Core fetch wrapper ───────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = Auth.getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

// ── Auth ─────────────────────────────────────────────────
const AuthAPI = {
  async login(email, password) {
    const data = await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    Auth.setToken(data.token);
    Auth.setUser(data.user);
    return data;
  },

  async register(name, email, password, phone = '') {
    const data = await apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password, phone })
    });
    Auth.setToken(data.token);
    Auth.setUser(data.user);
    return data;
  },

  async logout() {
    try { await apiFetch('/auth/logout', { method: 'POST' }); } catch {}
    Auth.clear();
    window.location.href = 'login.html';
  }
};

// ── Menu ─────────────────────────────────────────────────
const MenuAPI = {
  getVendors:  ()          => apiFetch('/menu/vendors'),
  getItems:    (vendorId)  => apiFetch(vendorId ? `/menu/items?vendor_id=${vendorId}` : '/menu/items'),
  getItem:     (itemId)    => apiFetch(`/menu/items/${itemId}`),
};

// ── Orders ───────────────────────────────────────────────
const OrdersAPI = {
  place:      (items)   => apiFetch('/orders/place', { method: 'POST', body: JSON.stringify({ items }) }),
  myOrders:   ()        => apiFetch('/orders/my'),
  getOrder:   (id)      => apiFetch(`/orders/${id}`),
  byToken:    (token)   => apiFetch(`/orders/token/${token}`),
  cancel:     (id)      => apiFetch(`/orders/${id}/cancel`, { method: 'POST' }),
};

// ── Vendor ───────────────────────────────────────────────
const VendorAPI = {
  orders:           (status) => apiFetch(status ? `/vendor/orders?status=${status}` : '/vendor/orders'),
  updateItemStatus: (itemId, status) => apiFetch(`/vendor/orders/${itemId}/status`, {
    method: 'POST', body: JSON.stringify({ status })
  }),
  menu:             ()       => apiFetch('/vendor/menu'),
  addItem:          (data)   => apiFetch('/vendor/menu', { method: 'POST', body: JSON.stringify(data) }),
  updateItem:       (id, d)  => apiFetch(`/vendor/menu/${id}`, { method: 'PUT', body: JSON.stringify(d) }),
  deleteItem:       (id)     => apiFetch(`/vendor/menu/${id}`, { method: 'DELETE' }),
  stats:            ()       => apiFetch('/vendor/stats'),
  toggle:           ()       => apiFetch('/vendor/toggle', { method: 'POST' }),
};

// ── Admin ────────────────────────────────────────────────
const AdminAPI = {
  stats:        () => apiFetch('/admin/stats'),
  weekly:       () => apiFetch('/admin/revenue/weekly'),
  vendors:      () => apiFetch('/admin/vendors'),
  bestsellers:  () => apiFetch('/admin/bestsellers'),
  queue:        () => apiFetch('/admin/queue'),
  alerts:       () => apiFetch('/admin/alerts'),
  updateVendor: (id, data) => apiFetch(`/admin/vendors/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
};

// ── UI Helpers ───────────────────────────────────────────
function showToast(msg, type = 'success') {
  const el = document.createElement('div');
  el.style.cssText = `
    position:fixed;bottom:24px;right:24px;z-index:9999;
    padding:.75rem 1.5rem;border-radius:10px;font-family:sans-serif;font-size:.9rem;
    font-weight:600;color:#fff;box-shadow:0 8px 24px rgba(0,0,0,.3);
    background:${type === 'error' ? '#e74c3c' : type === 'warn' ? '#f39c12' : '#27ae60'};
    animation:slideIn .3s ease;
  `;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function requireAuth(allowedRoles = []) {
  if (!Auth.isLoggedIn()) {
    window.location.href = 'login.html';
    return null;
  }
  const user = Auth.getUser();
  if (allowedRoles.length && !allowedRoles.includes(user.role)) {
    showToast('Access denied for your role', 'error');
    setTimeout(() => window.location.href = 'login.html', 1500);
    return null;
  }
  return user;
}
