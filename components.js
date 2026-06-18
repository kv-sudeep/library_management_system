// ── Shared Components for Kishkinda University Library ────────────

const KUL = {

  // ── Sidebar HTML ─────────────────────────────────────────────
  sidebar(user, activePage) {
    const ini = (user.full_name||user.username||'U').split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase();
    const role = user.role;
    const isStaff = role==='admin'||role==='librarian';

    const adminNav = [
      { section:t('main'), links:[
        {href:'dashboard.html',icon:'🏠',label:t('dashboard')},
        {href:'books.html',icon:'📚',label:t('booksCatalogue')},
      ]},
      { section:t('circulation'), links:[
        {href:'issue.html',icon:'➕',label:t('issueBook')},
        {href:'transactions.html',icon:'📋',label:t('transactions')},
        {href:'qr-scan.html',icon:'📷',label:t('qrScanner')},
        {href:'overdue.html',icon:'⚠️',label:t('overdueBooks')},
      ]},
      { section:t('management'), links:[
        {href:'users.html',icon:'👥',label:t('users')},
        {href:'categories.html',icon:'🏷️',label:t('categories')},
      ]},
      { section:t('intelligence'), links:[
        {href:'analytics.html',icon:'📊',label:t('analytics')},
        {href:'audit.html',icon:'🔐',label:t('auditLogs')},
      ]},
    ];

    const memberNav = [
      { section:t('library'), links:[
        {href:'member.html',icon:'🏠',label:t('home')},
        {href:'books.html',icon:'📚',label:t('books')},
      ]},
      { section:t('myLibrary'), links:[
        {href:'mybooks.html',icon:'📖',label:t('myBooks')},
        {href:'reservations.html',icon:'🔖',label:t('reservations')},
        {href:'wishlist.html',icon:'❤️',label:t('wishlist')},
      ]},
      { section:t('account'), links:[
        {href:'profile.html',icon:'👤',label:t('profile')},
      ]},
    ];

    const navGroups = isStaff ? adminNav : memberNav;
    const navHTML = navGroups.map(g=>`
      <div class="nav-section">${g.section}</div>
      ${g.links.map(l=>{
        const active = window.location.pathname.endsWith(l.href) || window.location.href.includes(l.href);
        return `<a href="${l.href}" class="nav-link${active?' active':''}"><span class="ni">${l.icon}</span>${l.label}</a>`;
      }).join('')}
    `).join('');

    return `
      <div class="sidebar" id="sidebar">
        <div class="sb-brand">
          <div class="sb-logo">📚</div>
          <div>
            <div class="sb-name">Kishkinda University</div>
            <div class="sb-sub">Library Portal</div>
          </div>
        </div>
        <div class="sb-nav">${navHTML}</div>
        <div class="sb-foot">
          <div class="av">${ini}</div>
          <div>
            <div class="av-name">${user.full_name||user.username}</div>
            <div class="av-role">${user.role}</div>
          </div>
          <button class="btn-logout" onclick="API.clearSession();window.location.href='login.html'" title="Sign Out">⏻</button>
        </div>
      </div>`;
  },

  // ── Topbar HTML ───────────────────────────────────────────────
  topbar(title, user) {
    const ini = (user.full_name||user.username||'U')[0].toUpperCase();
    return `
      <div class="topbar">
        <div class="tb-left">
          <button class="hamburger" onclick="KUL.toggleSidebar()" aria-label="Menu">
            <span></span><span></span><span></span>
          </button>
          <span class="page-ttl">${title}</span>
        </div>
        <div class="tb-right">
          <div class="notif-wrap" id="notifWrap">
            <button class="notif-btn" onclick="KUL.toggleNotif()" id="notifBtn">
              🔔<span class="notif-badge" id="notifBadge" style="display:none">0</span>
            </button>
            <div class="notif-drop" id="notifDrop" style="display:none">
              <div class="notif-head">${t('notifications')} <button class="btn btn-ghost btn-xs" onclick="KUL.markNotifRead()">${t('markRead')}</button></div>
              <div id="notifList"><div style="padding:20px;text-align:center;color:var(--muted);font-size:13px">${t('loading')}</div></div>
            </div>
          </div>
          <div style="display:flex;gap:4px;align-items:center">
            ${['en','hi','kn'].map(l=>{
              const labels={en:'EN',hi:'हिं',kn:'ಕನ್ನಡ'};
              const active=(localStorage.getItem('kul_lang')||'en')===l;
              return `<button onclick="setLang('${l}')" style="background:${active?'#1a1a1a':'rgba(255,255,255,.06)'};color:${active?'#fff':'var(--muted)'};border:1px solid ${active?'#1a1a1a':'rgba(0,0,0,.1)'};padding:4px 9px;border-radius:6px;font-size:11px;font-weight:600;cursor:pointer;transition:all .15s">${labels[l]}</button>`;
            }).join('')}
          </div>
          <a href="profile.html" class="btn btn-ghost btn-sm">👤 ${user.full_name?.split(' ')[0]||user.username}</a>
          <button class="btn btn-ghost btn-sm" onclick="API.clearSession();window.location.href='login.html'">${t('signOut')}</button>
        </div>
      </div>`;
  },

  // ── Chatbot HTML ──────────────────────────────────────────────
  chatbot() {
    return `
      <div class="chatbot">
        <div class="cw" id="chatWin" style="display:none">
          <div class="ch"><h4>📚 Library Assistant</h4><p>Kishkinda University Library</p></div>
          <div class="cm" id="chatMsgs">
            <div class="msg mb">Hello! I can help with borrowing, fines, reservations, or finding books. What do you need?</div>
          </div>
          <div class="ci">
            <input id="chatInp" placeholder="Ask me anything…" onkeydown="if(event.key==='Enter')KUL.sendChat()"/>
            <button onclick="KUL.sendChat()">Send</button>
          </div>
        </div>
        <button class="cf" id="chatFab" onclick="KUL.toggleChat()">💬</button>
      </div>`;
  },

  // ── Status Badge ──────────────────────────────────────────────
  badge(status) {
    const cls = {issued:'sb-issued',returned:'sb-returned',overdue:'sb-overdue',pending:'sb-pending',fulfilled:'sb-fulfilled',cancelled:'sb-cancelled'};
    return `<span class="sb-badge ${cls[status]||'sb-pending'}">${status}</span>`;
  },

  // ── Stars ─────────────────────────────────────────────────────
  stars(r=0) {
    r = Math.round(r);
    return `<span class="stars">${Array.from({length:5},(_,i)=>`<span class="${i<r?'star-on':'star-off'}">★</span>`).join('')}</span>`;
  },

  // ── Format Date ───────────────────────────────────────────────
  date(d) { const loc = (typeof currentLocale==='function')?currentLocale():'en-IN'; return d ? new Date(d).toLocaleDateString(loc,{day:'2-digit',month:'short',year:'numeric'}) : '—'; },

  // ── Toggle Sidebar ────────────────────────────────────────────
  toggleSidebar() {
    const sb = document.getElementById('sidebar');
    const main = document.getElementById('mainWrap');
    sb.classList.toggle('hide');
    if(main) main.classList.toggle('full');
  },

  // ── Notifications ─────────────────────────────────────────────
  async loadNotifications() {
    const data = await API.get('/transactions/notifications');
    const notifs = Array.isArray(data) ? data : [];
    const unread = notifs.filter(n=>!n.is_read).length;
    const badge = document.getElementById('notifBadge');
    if(badge){ badge.textContent = unread; badge.style.display = unread>0?'flex':'none'; }
    const list = document.getElementById('notifList');
    if(!list) return;
    list.innerHTML = notifs.length===0
      ? '<div style="padding:24px;text-align:center;color:var(--muted);font-size:13px">No notifications</div>'
      : notifs.slice(0,7).map(n=>`
          <div class="notif-item">
            <div class="notif-t">${n.title}</div>
            <div class="notif-m">${n.message}</div>
            <div class="notif-d">${KUL.date(n.created_at)}</div>
          </div>`).join('');
  },

  async markNotifRead() {
    await API.post('/transactions/notifications/read',{});
    const badge = document.getElementById('notifBadge');
    if(badge) badge.style.display='none';
  },

  toggleNotif() {
    const d = document.getElementById('notifDrop');
    d.style.display = d.style.display==='none' ? 'block' : 'none';
  },

  // ── Chat ──────────────────────────────────────────────────────
  toggleChat() {
    const w = document.getElementById('chatWin');
    const f = document.getElementById('chatFab');
    const open = w.style.display==='none';
    w.style.display = open ? 'block' : 'none';
    f.textContent = open ? '✕' : '💬';
  },
  sendChat() {
    const inp = document.getElementById('chatInp');
    const q = inp.value.trim(); if(!q) return;
    const box = document.getElementById('chatMsgs');
    box.innerHTML += `<div class="msg mu">${q}</div>`;
    inp.value = '';
    const qa = {
      'borrow':'To borrow: Browse Books → click a book → press "Borrow Book". Default loan = 14 days.',
      'return':'Go to My Books → Currently Borrowed → click "Return" next to the book.',
      'fine':'Fines are ₹2/day for overdue books. You can see them in My Books → Fines.',
      'reserve':"Click any unavailable book → 'Reserve'. You'll be notified when it's ready (7-day hold).",
      'renew':'Renewals must be processed by a librarian at the desk.',
      'hour':'Library hours: Mon–Fri 8am–8pm, Sat 9am–6pm, Sunday closed.',
      'lost':'For a lost book, please speak to a librarian. Replacement fees apply.',
      'recommend':'Visit the Home page for personalized recommendations based on your reading history!',
      'help':'I can help with: borrowing, returning, fines, reservations, recommendations, library hours, and lost books.',
    };
    const lower = q.toLowerCase();
    const match = Object.entries(qa).find(([k])=>lower.includes(k));
    setTimeout(()=>{
      box.innerHTML += `<div class="msg mb">${match?match[1]:`I'm not sure about that. Type "help" for what I can assist with, or speak to a librarian.`}</div>`;
      box.scrollTop = box.scrollHeight;
    }, 450);
    box.scrollTop = box.scrollHeight;
  },

  // ── Close dropdowns on outside click ─────────────────────────
  initOutsideClick() {
    document.addEventListener('click', e => {
      const nw = document.getElementById('notifWrap');
      const nd = document.getElementById('notifDrop');
      if(nw && nd && !nw.contains(e.target)) nd.style.display='none';
    });
  },

  // ── Loader / Empty ────────────────────────────────────────────
  loader() { return `<div class="ldr"><div class="spin"></div><p>Loading…</p></div>`; },
  empty(icon='📭', title='Nothing here yet', desc='') {
    return `<div class="empty"><span class="ei">${icon}</span><h3>${title}</h3>${desc?`<p>${desc}</p>`:''}</div>`;
  },

  // ── Chart defaults (Chart.js) ─────────────────────────────────
  chartDefaults() {
    if(typeof Chart === 'undefined') return;
    Chart.defaults.font.family = "'DM Sans', sans-serif";
    Chart.defaults.color = '#6b6b6b';
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(20,20,20,0.92)';
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    Chart.defaults.plugins.tooltip.titleFont = { size:12, weight:'600' };
    Chart.defaults.plugins.tooltip.bodyFont = { size:11 };
  },

  baseChart() {
    return { responsive:true, maintainAspectRatio:false, plugins:{ legend:{display:false} } };
  },

  COLORS: ['#1a1a1a','#3d3d3d','#606060','#838383','#a6a6a6','#c9a84c','#d4b460','#ccc'],
  GOLD: '#c9a84c',
};
