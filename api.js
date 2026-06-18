const API_BASE = 'http://localhost:5000/api';

const API = {
  getToken: () => localStorage.getItem('kul_token'),
  getUser:  () => { try { return JSON.parse(localStorage.getItem('kul_user')); } catch { return null; } },
  setSession: (token, user) => {
    localStorage.setItem('kul_token', token);
    localStorage.setItem('kul_user', JSON.stringify(user));
  },
  clearSession: () => {
    localStorage.removeItem('kul_token');
    localStorage.removeItem('kul_user');
  },
  headers: () => {
    const t = localStorage.getItem('kul_token');
    return { 'Content-Type': 'application/json', ...(t ? { Authorization: `Bearer ${t}` } : {}) };
  },
  async request(method, url, body) {
    try {
      const opts = { method, headers: this.headers() };
      if (body) opts.body = JSON.stringify(body);
      const r = await fetch(API_BASE + url, opts);
      if (r.status === 401) { window.location.href = 'login.html'; return {}; }
      return await r.json();
    } catch (e) { return { error: 'Network error — is Flask running on port 5000?' }; }
  },
  get:  (url)       => API.request('GET',    url),
  post: (url, data) => API.request('POST',   url, data),
  put:  (url, data) => API.request('PUT',    url, data),
  del:  (url)       => API.request('DELETE', url),

  guard(requiredRole) {
    const u = this.getUser(), t = this.getToken();
    if (!u || !t) { window.location.href = 'login.html'; return null; }
    if (requiredRole === 'staff' && u.role !== 'admin' && u.role !== 'librarian') {
      window.location.href = 'member.html'; return null;
    }
    return u;
  },

  toast(msg, type = 'info') {
    let box = document.getElementById('__toastBox');
    if (!box) {
      box = document.createElement('div');
      box.id = '__toastBox';
      box.style.cssText = 'position:fixed;bottom:28px;left:50%;transform:translateX(-50%);z-index:99999;display:flex;flex-direction:column;gap:8px;pointer-events:none;min-width:280px;text-align:center';
      document.body.appendChild(box);
    }
    const colors = { success: '#16a34a', error: '#dc2626', info: '#1a1a1a', warn: '#d97706' };
    const t = document.createElement('div');
    t.style.cssText = `background:${colors[type]||colors.info};color:#fff;padding:13px 24px;border-radius:12px;font-size:13px;font-family:'DM Sans',sans-serif;box-shadow:0 8px 24px rgba(0,0,0,.2);animation:slideUp .3s both;pointer-events:auto;font-weight:500;`;
    t.textContent = msg; box.appendChild(t);
    setTimeout(() => { t.style.transition = 'opacity .3s,transform .3s'; t.style.opacity = '0'; t.style.transform = 'translateY(8px)'; setTimeout(() => t.remove(), 350); }, 3000);
  }
};
