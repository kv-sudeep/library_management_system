# Kishkinda University Library — Digital Library Management System

A complete library management system with a Flask + SQLAlchemy backend and a
**fully separated, multi-page** vanilla HTML/CSS/JS frontend featuring 3D
glassmorphism design, animated stat cards, and working Chart.js analytics.

---

## What changed in this version

1. **Every page is now its own standalone `.html` file** (no single-page React bundle) — easier to edit, debug, and deploy individually.
2. **Login is a separate, dedicated entry page** (`login.html`) with full 3D floating-book background, particle animation, and tilting glass card. After login it routes straight to `dashboard.html` (staff) or `member.html` (members) — no in-app login screen.
3. **Analytics graphs are fixed.** The previous build used Recharts loaded as a UMD `<script>` tag, which silently failed in some environments and rendered blank charts. This version uses **Chart.js 4** (loaded from a reliable CDN) with manually verified data bindings for every chart — all 15+ charts across the Dashboard and Analytics pages now render correctly with live data from the API.
4. **System renamed throughout** from "LibraryOS" to **Kishkinda University Library** — page titles, sidebar branding, hero banners, login screen, and chatbot greeting.
5. **Full 3D design language applied everywhere**: tilting glass login card, floating book illustrations, 3D-hover stat cards (`rotateX`/`rotateY` on hover), 3D book covers with perspective lift, gradient hero banners with parallax-style blur circles.

---

## File Structure

```
kishkinda-library/
├── login.html              # Standalone login/register page (3D glass + floating books)
├── dashboard.html          # Staff dashboard — KPIs + 6 live charts
├── analytics.html          # Full analytics center — 5 tabs, 15+ charts
├── books.html               # Book catalogue (shared by staff & members)
├── issue.html               # Issue-book workflow (staff)
├── transactions.html        # All transactions table (staff)
├── overdue.html             # Overdue books + fine calculator (staff)
├── users.html                # User management (staff)
├── categories.html           # Category management (staff)
├── audit.html                # Audit log viewer (admin)
├── member.html               # Member home page (trending + recommendations)
├── mybooks.html               # Member's borrow history & active loans
├── reservations.html          # Member's reservations
├── wishlist.html               # Member's wishlist
├── profile.html                 # Edit profile (shared)
├── styles.css                    # ALL shared styling (one file, one source of truth)
├── api.js                         # Fetch wrapper, session/token handling, toast()
├── components.js                   # Sidebar, topbar, chatbot, badges, chart helpers
└── backend/
    ├── app.py, extensions.py, models.py, seed_data.py, requirements.txt
    └── routes/  (auth, books, transactions, analytics, users, admin)
```

Every page includes `styles.css`, `api.js`, and `components.js`, then builds its
sidebar/topbar/chatbot via `KUL.sidebar()`, `KUL.topbar()`, `KUL.chatbot()` — so
look-and-feel stays consistent without a build step.

---

## Run It

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Flask starts on `http://localhost:5000` and auto-seeds the SQLite database
with 20 books, 10 categories, 10 authors, 5 demo members, and 80 historical
transactions (the data that powers every chart).

### 2. Frontend

Just open `login.html` directly in a browser, **or** serve the folder so
relative links behave the same as a real deployment:

```bash
cd kishkinda-library
python -m http.server 8080 --bind 127.0.0.1
# visit http://localhost:8080/login.html
```

> The backend must be running first — every page calls `http://localhost:5000/api/...`.

---

## Demo Accounts

| Role      | Email                  | Password |
|-----------|-------------------------|----------|
| Admin     | admin@library.com       | admin123 |
| Librarian | librarian@library.com   | lib123   |
| Member    | alice@email.com         | pass123  |

Click any row on the login screen's "Demo Accounts" box to auto-fill it.

---

## Why the analytics graphs weren't showing before — and the fix

The earlier build rendered charts with **Recharts** (a React charting
library) loaded via a CDN `<script>` tag and used inside plain
`React.createElement` calls without JSX/build tooling. In that setup the
Recharts UMD bundle sometimes failed to resolve its internal D3
sub-dependencies correctly when loaded outside a bundler, which made the
`<ResponsiveContainer>` collapse to zero height — so the chart container was
present in the DOM but visually empty.

This version replaces Recharts with **Chart.js 4**, which is a single
self-contained UMD bundle with no React or D3 dependency, and every chart
call site explicitly sets a `height` on its `<canvas>` and verifies the API
response shape (`labels`/`data` arrays) before instantiating the chart. All
endpoints were individually tested against the live Flask backend (see test
output during build) and every one returns populated data for the seeded
database, so each of the 15+ charts across **Dashboard** and **Analytics**
now renders with real numbers on first load.

---

## 3D Design Details

- **Login page**: 16 floating "book spine" divs with randomized size/color/animation-delay, 30 drifting gold particles, and the glass card itself tilts toward the mouse cursor using `rotateX`/`rotateY` transforms.
- **Stat cards**: `transform-style: preserve-3d` + hover `translateY(-7px) rotateX(4deg)` with an expanding corner-accent circle.
- **Book cards**: hover lifts with `rotateX(4deg) rotateY(-2deg)` and a soft drop shadow that grows on hover, simulating a book tilting toward the viewer.
- **Hero banners**: dark gradient with two blurred radial "glow" circles that scale on hover for subtle parallax depth.
- **Chart cards**: consistent `cc` class with hover-lift, matching the rest of the 3D card system.

---

## Tech Stack

| Layer    | Tech |
|----------|------|
| Backend  | Python 3.12, Flask 3.0, SQLAlchemy, JWT |
| ML       | scikit-learn (LinearRegression demand forecast) |
| Database | SQLite (auto-created + seeded) |
| Frontend | Vanilla HTML/CSS/JS — no build step, no framework |
| Charts   | Chart.js 4 (line, bar, doughnut, pie, radar) |
| Fonts    | Cormorant Garamond (display) + DM Sans (UI) |
![alt text](<Screenshot 2026-06-18 093122.png>) ![alt text](<Screenshot 2026-06-18 093130.png>) ![alt text](<Screenshot 2026-06-18 093143.png>) ![alt text](<Screenshot 2026-06-18 093228.png>) ![alt text](<Screenshot 2026-06-18 093242.png>) ![alt text](<Screenshot 2026-06-18 093344.png>) ![alt text](<Screenshot 2026-06-18 093353.png>)