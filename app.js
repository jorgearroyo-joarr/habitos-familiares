// ============================================
// HábitosFam – app.js  (v3)
// PIN login, API-driven habits, dynamic profiles,
// individual micro-habit tracking, per-profile dashboard
// ============================================

const API = window.location.origin;

// ── Session state ────────────────────────────
let session = {
    role: null,          // 'admin' | 'user' | null
    profileSlug: null,   // scoped profile for users
    token: null,
    pin: null,
};
let profiles = [];
let habitsConfig = {};  // { slug: [HabitTemplate...] }
let appSettings = {};
let state = {};         // { slug: { habits: {date: {habitId: {done, miniTasks}}}, dayLog: {} } }
let activeProfile = null;

// ── API helpers ──────────────────────────────

async function api(path, opts = {}) {
    const res = await fetch(`${API}${path}`, {
        headers: { 'Content-Type': 'application/json', ...opts.headers },
        ...opts
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

// ── Init ─────────────────────────────────────

async function init() {
    // Load settings
    try { appSettings = await api('/api/settings'); } catch (e) { appSettings = { currency_symbol: '$', app_name: 'HábitosFam' }; }

    // Update app title from settings
    const titleEl = document.getElementById('app-title');
    if (titleEl && appSettings.app_name) titleEl.textContent = appSettings.app_name;
    if (appSettings.app_name) document.title = `${appSettings.app_name} ✨`;

    // Initialize notification system
    if (Notification.permission === 'granted') {
        scheduleDailyReminder();
    }

    // Check saved session
    const saved = localStorage.getItem('habitosfam_session');
    if (saved) {
        try {
            const s = JSON.parse(saved);
            session = s;
            await loadApp();
            return;
        } catch (e) { localStorage.removeItem('habitosfam_session'); }
    }

    showLoginOverlay();
    initTheme();
}

// ── Theme Toggle ───────────────────────────────

function toggleTheme() {
    const html = document.documentElement;
    const btn = document.getElementById('theme-toggle');
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('habitosfam_theme', newTheme);
    btn.textContent = newTheme === 'light' ? '🌙' : '☀️';
}

function initTheme() {
    const savedTheme = localStorage.getItem('habitosfam_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.textContent = savedTheme === 'light' ? '🌙' : '☀️';
}

// ── Login ────────────────────────────────────

function showLoginOverlay() {
    document.getElementById('login-overlay').classList.remove('hidden');
    document.getElementById('app-container').classList.add('hidden');
    document.getElementById('login-error').textContent = '';
    const inputs = document.querySelectorAll('.pin-input');
    inputs.forEach(i => i.value = '');
    inputs[0]?.focus();
}

function setupPinInputs() {
    const inputs = document.querySelectorAll('.pin-input');
    inputs.forEach((inp, idx) => {
        inp.addEventListener('input', () => {
            if (inp.value.length === 1 && idx < inputs.length - 1) {
                inputs[idx + 1].focus();
            }
        });
        inp.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && !inp.value && idx > 0) {
                inputs[idx - 1].focus();
            }
            if (e.key === 'Enter') {
                submitLogin();
            }
        });
    });
}

async function submitLogin() {
    const inputs = document.querySelectorAll('.pin-input');
    const pin = Array.from(inputs).map(i => i.value).join('');
    if (pin.length < 4) return;

    try {
        const res = await api('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ pin })
        });
        session = {
            role: res.role,
            profileSlug: res.profile_slug,
            token: res.token,
            pin: pin,
        };
        localStorage.setItem('habitosfam_session', JSON.stringify(session));
        await loadApp();
    } catch (e) {
        document.getElementById('login-error').textContent = 'PIN inválido. Intenta de nuevo.';
        inputs.forEach(i => i.value = '');
        inputs[0]?.focus();
    }
}

function logout() {
    session = { role: null, profileSlug: null, token: null, pin: null };
    localStorage.removeItem('habitosfam_session');
    localStorage.removeItem('habitosfam_state');
    showLoginOverlay();
}

// ── Load App ─────────────────────────────────

async function loadApp() {
    document.getElementById('login-overlay').classList.add('hidden');
    document.getElementById('app-container').classList.remove('hidden');

    // Load profiles
    profiles = await api('/api/profiles');

    // Filter by role
    let visibleProfiles = profiles;
    if (session.role === 'user' && session.profileSlug) {
        visibleProfiles = profiles.filter(p => p.slug === session.profileSlug);
    }

    // Load habit config for ALL profiles (needed for family tab)
    for (const p of profiles) {
        habitsConfig[p.slug] = await api(`/api/profiles/${p.slug}/habits-config`);
    }

    // Load state from localStorage
    loadState();

    // Build dynamic tabs
    buildTabs(visibleProfiles);
    buildProfileSections(visibleProfiles);

    // Load today from API
    for (const p of visibleProfiles) {
        await loadTodayFromAPI(p.slug);
    }

    // Render first profile
    activeProfile = visibleProfiles[0]?.slug;
    if (activeProfile) {
        switchProfile(activeProfile);
    }

    updateHeaderDate();

    // Show user info
    const roleEl = document.getElementById('user-role-badge');
    if (roleEl) {
        if (session.role === 'admin') {
            roleEl.textContent = '👑 Supervisor';
            roleEl.className = 'role-badge admin';
        } else {
            const p = profiles.find(pr => pr.slug === session.profileSlug);
            roleEl.textContent = `${p?.avatar || '👤'} ${p?.name || session.profileSlug}`;
            roleEl.className = 'role-badge user';
        }
    }

    // Show/hide admin link
    const adminLink = document.getElementById('admin-panel-link');
    if (adminLink) {
        adminLink.style.display = session.role === 'admin' ? 'inline-block' : 'none';
    }
}

// ── State ────────────────────────────────────

function loadState() {
    const stored = localStorage.getItem('habitosfam_state');
    if (stored) {
        try { state = JSON.parse(stored); } catch (e) { state = {}; }
    }
    // Ensure all profiles have state
    for (const p of profiles) {
        if (!state[p.slug]) {
            state[p.slug] = { habits: {}, dayLog: {}, streak: 0, shieldUsed: false };
        }
        const todayKey = today();
        if (!state[p.slug].habits[todayKey]) {
            state[p.slug].habits[todayKey] = {};
        }
    }
}

function saveState() {
    localStorage.setItem('habitosfam_state', JSON.stringify(state));
}

function today() {
    return new Date().toISOString().split('T')[0];
}

// ── Dynamic tabs ─────────────────────────────

function buildTabs(visibleProfiles) {
    const nav = document.getElementById('tab-nav');
    nav.innerHTML = '';

    visibleProfiles.forEach((p, i) => {
        const btn = document.createElement('button');
        btn.className = `tab-btn ${p.theme}-theme ${i === 0 ? 'active' : ''}`;
        btn.id = `tab-${p.slug}`;
        btn.setAttribute('role', 'tab');
        btn.innerHTML = `<span class="tab-avatar">${p.avatar}</span><span>${p.name} <small>${p.age} años</small></span>`;
        btn.onclick = () => switchProfile(p.slug);
        nav.appendChild(btn);
    });

    // Family tab (only for admin or if multiple profiles)
    if (visibleProfiles.length > 1 || session.role === 'admin') {
        const famBtn = document.createElement('button');
        famBtn.className = 'tab-btn';
        famBtn.id = 'tab-family';
        famBtn.innerHTML = '<span class="tab-avatar">🏆</span><span>Familia</span>';
        famBtn.onclick = () => switchProfile('family');
        nav.appendChild(famBtn);
    }
}

// ── Dynamic profile sections ─────────────────

function buildProfileSections(visibleProfiles) {
    const main = document.getElementById('app-main');
    // Remove old profile sections BUT keep family section
    main.querySelectorAll('.profile-section').forEach(s => {
        if (s.id !== 'profile-family') s.remove();
    });

    // Ensure family section exists
    let famSection = document.getElementById('profile-family');
    if (!famSection) {
        famSection = document.createElement('section');
        famSection.id = 'profile-family';
        famSection.className = 'profile-section';
        famSection.dataset.profile = 'family';
        main.appendChild(famSection);
    }

    const currency = appSettings.currency_symbol || '$';

    visibleProfiles.forEach((p, i) => {
        const section = document.createElement('section');
        section.id = `profile-${p.slug}`;
        section.className = `profile-section ${i === 0 ? 'active' : ''}`;
        section.dataset.profile = p.slug;

        const themeClass = `${p.theme || p.slug}-theme`;

        section.innerHTML = `
        <div class="profile-hero ${themeClass}">
            <div class="profile-avatar">${p.avatar}</div>
            <div class="profile-info">
                <h2>${p.name}</h2>
                <p class="profile-age">${p.age} años · Nivel <span id="${p.slug}-level-label">⭐</span></p>
                <div class="streak-badge" id="${p.slug}-streak">
                    <span>🔥</span> <span id="${p.slug}-streak-days">0</span> días seguidos
                </div>
            </div>
            <div class="profile-coins">
                <div class="coin-display">
                    <span class="coin-icon">🌟</span>
                    <div>
                        <div class="coin-amount" id="${p.slug}-week-stars">0</div>
                        <div class="coin-label">estrellas esta semana</div>
                    </div>
                </div>
                <div class="coin-display">
                    <span class="coin-icon">💰</span>
                    <div>
                        <div class="coin-amount" id="${p.slug}-week-coins">${currency}0.00</div>
                        <div class="coin-label">ganados esta semana</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="daily-progress-card ${themeClass}">
            <div class="progress-header">
                <span>⚡ Progreso de hoy</span>
                <span id="${p.slug}-daily-count">0/0 hábitos</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar ${p.slug}-bar" id="${p.slug}-progress-bar" style="width:0%"></div>
            </div>
            <div class="progress-message" id="${p.slug}-progress-msg">¡Empieza tu día! 🚀</div>
        </div>

        <div class="habits-grid" id="${p.slug}-habits-grid"></div>

        <button class="complete-day-btn ${p.slug}-btn" id="${p.slug}-complete-btn" onclick="completeDay('${p.slug}')" disabled>
            ✅ ¡Completé mi día!
        </button>

        <!-- Dashboard -->
        <div class="dashboard-card" id="${p.slug}-dashboard">
            <h3>📊 Mi Dashboard</h3>
            <div class="dashboard-grid" id="${p.slug}-dashboard-grid"></div>
        </div>
        `;

        main.insertBefore(section, famSection);
    });

    // Rebuild family section with ALL profiles (not just visible)
    buildFamilySection(profiles, currency);
}

function buildFamilySection(visibleProfiles, currency) {
    const famSection = document.getElementById('profile-family');
    if (!famSection) return;

    let cardsHTML = '';
    let monthlyHTML = '';
    visibleProfiles.forEach(p => {
        cardsHTML += `
        <div class="family-card ${p.slug}-card">
            <div class="family-card-header">
                <span class="fam-avatar">${p.avatar}</span>
                <div><h3>${p.name}</h3><p>${p.age} años</p></div>
            </div>
            <div class="family-stats">
                <div class="stat-item"><span class="stat-val" id="fam-${p.slug}-streak">0</span><span class="stat-lbl">🔥 Racha</span></div>
                <div class="stat-item"><span class="stat-val" id="fam-${p.slug}-week-pct">0%</span><span class="stat-lbl">📊 Semana</span></div>
                <div class="stat-item"><span class="stat-val" id="fam-${p.slug}-earned">${currency}0</span><span class="stat-lbl">💰 Ganado</span></div>
            </div>
            <div class="week-calendar" id="fam-${p.slug}-calendar"></div>
        </div>`;

        monthlyHTML += `
        <div class="monthly-item">
            <div class="monthly-progress-ring">
                <svg viewBox="0 0 80 80">
                    <circle cx="40" cy="40" r="34" class="ring-bg" />
                    <circle cx="40" cy="40" r="34" class="ring-fill ${p.slug}-ring" id="${p.slug}-ring" stroke-dasharray="0 213" />
                </svg>
                <div class="ring-center">
                    <span class="ring-avatar">${p.avatar}</span>
                    <span class="ring-pct" id="${p.slug}-month-pct">0%</span>
                </div>
            </div>
            <p>${p.name}</p>
            <div class="monthly-reward-badge" id="${p.slug}-monthly-reward">🔒 Pendiente</div>
        </div>`;
    });

    famSection.innerHTML = `
    <div class="family-hero"><h2>🏆 Panel Familiar</h2><p>Resumen de la semana y recompensas</p></div>
    <div class="family-week-grid">${cardsHTML}</div>
    <div class="monthly-card"><h3>🎁 Recompensa Mensual</h3><div class="monthly-grid">${monthlyHTML}</div></div>
    <div class="rules-card">
        <h3>📋 Reglas del Sistema</h3>
        <div class="rules-grid">
            <div class="rule-item"><span class="rule-icon">⭐</span><div><strong>Puntos diarios</strong><p>Cada hábito = 1 estrella. Día completo = ⭐ bonus extra</p></div></div>
            <div class="rule-item"><span class="rule-icon">💰</span><div><strong>Recompensa semanal</strong><p>Escalonada por % de cumplimiento</p></div></div>
            <div class="rule-item"><span class="rule-icon">🎁</span><div><strong>Recompensa mensual</strong><p>75%+ = actividad especial</p></div></div>
            <div class="rule-item"><span class="rule-icon">🔥</span><div><strong>Racha</strong><p>7 días seguidos = +50% recompensa</p></div></div>
            <div class="rule-item"><span class="rule-icon">🛡️</span><div><strong>Escudo protector</strong><p>1 día libre por semana sin perder racha</p></div></div>
            <div class="rule-item"><span class="rule-icon">📈</span><div><strong>Progresión</strong><p>Los hábitos evolucionan cada mes</p></div></div>
        </div>
    </div>
    ${session.role === 'admin' ? `
    <div class="admin-area">
        <h4>⚙️ Administración</h4>
        <div class="admin-btns">
            <button class="admin-btn" onclick="resetWeek()">🔄 Cerrar semana</button>
            <a href="/admin" class="admin-btn" style="text-decoration:none">⚙️ Panel Admin</a>
        </div>
    </div>` : ''}
    `;
}

// ── Profile switching ────────────────────────

function switchProfile(name) {
    activeProfile = name;
    document.querySelectorAll('.profile-section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

    const section = document.getElementById(`profile-${name}`);
    const tabBtn = document.getElementById(`tab-${name}`);
    if (section) section.classList.add('active');
    if (tabBtn) tabBtn.classList.add('active');

    if (name !== 'family') {
        renderProfile(name);
        renderDashboard(name);
    } else {
        renderFamily();
    }
}

// ── Render profile ───────────────────────────

function renderProfile(slug) {
    const habits = habitsConfig[slug] || [];
    const todayKey = today();
    const todayHabits = state[slug]?.habits[todayKey] || {};
    const grid = document.getElementById(`${slug}-habits-grid`);
    if (!grid) return;

    // Save expanded state before re-rendering
    const expandedKeys = new Set();
    grid.querySelectorAll('.habit-card.expanded').forEach(card => {
        const key = card.id?.replace(`card-${slug}-`, '');
        if (key) expandedKeys.add(key);
    });

    grid.innerHTML = '';
    habits.forEach(habit => {
        if (!habit.is_active) return;
        const hState = todayHabits[habit.habit_key] || { done: false, miniTasks: {} };
        const card = createHabitCard(habit, hState, slug);
        // Restore expanded state
        if (expandedKeys.has(habit.habit_key)) {
            card.classList.add('expanded');
        }
        grid.appendChild(card);
    });

    updateDailyProgress(slug);
    updateProfileHeader(slug);
    updateCompleteButton(slug);
}

function createHabitCard(habit, hState, slug) {
    const card = document.createElement('div');
    const profile = profiles.find(p => p.slug === slug);
    const themeClass = `${profile?.theme || slug}-theme`;
    card.className = `habit-card ${themeClass}${hState.done ? ' completed' : ''}`;
    card.id = `card-${slug}-${habit.habit_key}`;

    const microHabits = habit.micro_habits || [];
    const miniTasksHTML = microHabits.filter(m => m.is_active).map((mh, i) => {
        const done = hState.miniTasks[i] || false;
        return `
        <div class="mini-task${done ? ' done' : ''}" onclick="toggleMiniTask('${slug}', '${habit.habit_key}', ${i}, event)" id="mini-${slug}-${habit.habit_key}-${i}">
            <div class="mini-task-check">${done ? '✓' : ''}</div>
            <span>${mh.description}</span>
        </div>`;
    }).join('');

    const activeMicro = microHabits.filter(m => m.is_active);
    const doneCount = activeMicro.filter((_, i) => hState.miniTasks[i]).length;

    card.innerHTML = `
    <div class="habit-icon">${habit.icon}</div>
    <div class="habit-content">
        <div class="habit-name">${habit.name}</div>
        <div class="habit-desc">${habit.description || ''}</div>
        <div class="habit-stars">⭐ ${habit.stars} estrella${habit.stars !== 1 ? 's' : ''} · ${doneCount}/${activeMicro.length} micro-hábitos</div>
        <div class="mini-tasks">${miniTasksHTML}</div>
    </div>
    <div style="display:flex;flex-direction:column;align-items:center;gap:8px">
        <div class="habit-check" id="check-${slug}-${habit.habit_key}" onclick="toggleHabit('${slug}', '${habit.habit_key}')">${hState.done ? '✓' : ''}</div>
        <div class="habit-expand" onclick="toggleExpand('${slug}','${habit.habit_key}',event)">▼</div>
    </div>
    `;

    // NO whole-card click — only the checkbox or expand arrow

    return card;
}

function toggleExpand(slug, habitKey, e) {
    e.stopPropagation();
    const card = document.getElementById(`card-${slug}-${habitKey}`);
    if (card) card.classList.toggle('expanded');
}

function toggleHabit(slug, habitKey) {
    const todayKey = today();
    if (!state[slug].habits[todayKey]) state[slug].habits[todayKey] = {};
    const habits = state[slug].habits[todayKey];
    if (!habits[habitKey]) habits[habitKey] = { done: false, miniTasks: {} };

    habits[habitKey].done = !habits[habitKey].done;

    // Auto-complete micro tasks when main toggled on
    if (habits[habitKey].done) {
        const config = (habitsConfig[slug] || []).find(h => h.habit_key === habitKey);
        const micros = (config?.micro_habits || []).filter(m => m.is_active);
        micros.forEach((_, i) => { habits[habitKey].miniTasks[i] = true; });
        playCheckSound();
    } else {
        habits[habitKey].miniTasks = {};
    }

    saveState();
    syncHabitsToAPI(slug);
    renderProfile(slug);
}

function toggleMiniTask(slug, habitKey, idx, e) {
    e.stopPropagation();
    const todayKey = today();
    if (!state[slug].habits[todayKey]) state[slug].habits[todayKey] = {};
    const habits = state[slug].habits[todayKey];
    if (!habits[habitKey]) habits[habitKey] = { done: false, miniTasks: {} };

    const wasChecked = habits[habitKey].miniTasks[idx];
    habits[habitKey].miniTasks[idx] = !wasChecked;

    // Dopamine burst on checking a micro-task
    if (!wasChecked) {
        playMicroCheckSound();
        spawnMicroSparkle(e);
    }

    // Auto-complete if all micro-tasks done
    const config = (habitsConfig[slug] || []).find(h => h.habit_key === habitKey);
    const micros = (config?.micro_habits || []).filter(m => m.is_active);
    const allDone = micros.every((_, i) => habits[habitKey].miniTasks[i]);
    if (allDone && micros.length > 0) {
        habits[habitKey].done = true;
        playCheckSound();
        // Extra dopamine: mini confetti burst for completing all micro-habits
        const rect = e.target.closest('.habit-card')?.getBoundingClientRect();
        if (rect) launchMiniConfetti(rect.left + rect.width / 2, rect.top);
    }

    saveState();
    syncHabitsToAPI(slug);
    renderProfile(slug);
}

// ── API Sync ─────────────────────────────────

async function syncHabitsToAPI(slug) {
    const todayKey = today();
    const habits = state[slug]?.habits[todayKey] || {};
    const total = (habitsConfig[slug] || []).filter(h => h.is_active).length;
    const done = Object.values(habits).filter(h => h.done).length;
    const pct = total > 0 ? done / total : 0;

    const entries = Object.entries(habits).map(([id, h]) => ({
        habit_id: id,
        done: h.done,
        mini_tasks: h.miniTasks || {}
    }));

    try {
        await api(`/api/profiles/${slug}/habits`, {
            method: 'POST',
            body: JSON.stringify({ date: todayKey, habits: entries })
        });
    } catch (e) { console.warn('API sync failed', e); }
}

async function syncCompleteDayToAPI(slug, done, total, pct) {
    try {
        await api(`/api/profiles/${slug}/complete-day`, {
            method: 'POST',
            body: JSON.stringify({ date: today(), completed_count: done, total, pct })
        });
    } catch (e) { console.warn('complete-day sync failed', e); }
}

async function loadTodayFromAPI(slug) {
    try {
        const log = await api(`/api/profiles/${slug}/today`);
        if (!log || log.id === 0) return;
        const todayKey = today();
        if (!state[slug].habits[todayKey]) state[slug].habits[todayKey] = {};
        if (log.habit_entries && log.habit_entries.length > 0) {
            log.habit_entries.forEach(entry => {
                let miniTasks = {};
                try { miniTasks = JSON.parse(entry.mini_tasks_json || '{}'); } catch (e) { }
                state[slug].habits[todayKey][entry.habit_id] = { done: entry.done, miniTasks };
            });
        }
        if (log.day_done) {
            if (!state[slug].dayLog) state[slug].dayLog = {};
            state[slug].dayLog[todayKey] = {
                completedCount: log.completed_count, total: log.total,
                pct: log.pct, dayDone: true
            };
        }
        saveState();
    } catch (e) { console.warn('loadTodayFromAPI failed', e); }
}

// ── Progress ─────────────────────────────────

function updateDailyProgress(slug) {
    const todayKey = today();
    const habits = state[slug]?.habits[todayKey] || {};
    const total = (habitsConfig[slug] || []).filter(h => h.is_active).length;
    const done = Object.values(habits).filter(h => h.done).length;
    const pct = total > 0 ? (done / total) * 100 : 0;

    const bar = document.getElementById(`${slug}-progress-bar`);
    if (bar) bar.style.width = `${pct}%`;
    const count = document.getElementById(`${slug}-daily-count`);
    if (count) count.textContent = `${done}/${total} hábitos`;

    const msgs = PROGRESS_MESSAGES[slug] || PROGRESS_MESSAGES._default;
    const msgEl = document.getElementById(`${slug}-progress-msg`);
    if (msgEl) msgEl.textContent = msgs[done] || msgs[0];
}

function updateProfileHeader(slug) {
    const streak = computeStreak(slug);
    const streakEl = document.getElementById(`${slug}-streak-days`);
    if (streakEl) streakEl.textContent = streak;
    if (state[slug]) state[slug].streak = streak;

    const weekData = computeWeekStats(slug);
    const starsEl = document.getElementById(`${slug}-week-stars`);
    if (starsEl) starsEl.textContent = weekData.stars;

    const earned = computeWeeklyEarned(slug, weekData.pct);
    const currency = appSettings.currency_symbol || '$';
    const coinsEl = document.getElementById(`${slug}-week-coins`);
    if (coinsEl) coinsEl.textContent = `${currency}${earned.toFixed(2)}`;
}

function updateCompleteButton(slug) {
    const todayKey = today();
    const habits = state[slug]?.habits[todayKey] || {};
    const total = (habitsConfig[slug] || []).filter(h => h.is_active).length;
    const done = Object.values(habits).filter(h => h.done).length;
    const pct = done / total;

    const btn = document.getElementById(`${slug}-complete-btn`);
    if (!btn) return;
    const dayLog = state[slug]?.dayLog || {};

    if (dayLog[todayKey]?.dayDone) {
        btn.disabled = false;
        btn.textContent = '✅ ¡Día completado!';
        btn.style.opacity = '0.7';
        btn.onclick = null;
    } else if (pct >= 0.5) {
        btn.disabled = false;
        btn.onclick = () => completeDay(slug);
    } else {
        btn.disabled = true;
        btn.onclick = () => completeDay(slug);
    }
}

// ── Complete day ─────────────────────────────

function completeDay(slug) {
    const todayKey = today();
    const habits = state[slug]?.habits[todayKey] || {};
    const total = (habitsConfig[slug] || []).filter(h => h.is_active).length;
    const done = Object.values(habits).filter(h => h.done).length;
    const pct = done / total;

    if (!state[slug].dayLog) state[slug].dayLog = {};
    state[slug].dayLog[todayKey] = { completedCount: done, total, pct, dayDone: true, timestamp: Date.now() };

    saveState();
    syncCompleteDayToAPI(slug, done, total, pct);

    const profile = profiles.find(p => p.slug === slug);
    let emoji, title, msg;
    if (pct === 1.0) {
        emoji = '🌟🎉'; title = '¡DÍA PERFECTO!';
        msg = `¡${profile?.name || slug} completó todos los hábitos! ⭐⭐ bonus extra.`;
        launchConfetti();
    } else if (pct >= 0.83) {
        emoji = '🔥'; title = '¡Casi perfecto!';
        msg = `${done}/${total} hábitos completados.`;
        launchConfetti(40);
    } else {
        emoji = '💪'; title = '¡Buen trabajo!';
        msg = `${done}/${total} hábitos. Mañana puedes más.`;
    }

    showModal(emoji, title, msg, '⭐'.repeat(done));
    renderProfile(slug);
}

// ── Stats ────────────────────────────────────

function computeStreak(slug) {
    const log = state[slug]?.dayLog || {};
    let streak = 0;
    let check = new Date();
    for (let i = 0; i < 365; i++) {
        const key = check.toISOString().split('T')[0];
        const entry = log[key];
        if (entry && entry.pct >= 0.5) { streak++; check.setDate(check.getDate() - 1); }
        else if (i === 0) { check.setDate(check.getDate() - 1); }
        else break;
    }
    return streak;
}

function getWeekDates() {
    const d = new Date();
    const day = d.getDay();
    const startOffset = day === 0 ? -6 : 1 - day;
    const monday = new Date(d); monday.setDate(d.getDate() + startOffset);
    const dates = [];
    for (let i = 0; i < 7; i++) { const dd = new Date(monday); dd.setDate(monday.getDate() + i); dates.push(dd.toISOString().split('T')[0]); }
    return dates;
}

function computeWeekStats(slug) {
    const weekDates = getWeekDates();
    const log = state[slug]?.dayLog || {};
    let stars = 0, completedDays = 0, totalPossible = 0;
    weekDates.forEach(d => {
        const entry = log[d];
        if (entry) {
            stars += entry.completedCount;
            if (entry.completedCount === entry.total) stars++;
            totalPossible += entry.total;
            if (entry.pct >= 0.5) completedDays++;
        }
    });
    const pct = totalPossible > 0 ? stars / (totalPossible + 7) : 0;
    return { stars, pct, completedDays, weekDates };
}

function computeWeeklyEarned(slug, weekPct) {
    const profile = profiles.find(p => p.slug === slug);
    if (!profile) return 0;
    const streak = state[slug]?.streak || 0;
    const streakBonus = streak >= (appSettings.streak_bonus_days || 7) ? (appSettings.streak_bonus_pct || 1.5) : 1.0;

    // TODO: use reward tiers from API once loaded; for now use standard thresholds
    const thresholds = [
        { min: 0.90, mult: 2.0 }, { min: 0.75, mult: 1.5 },
        { min: 0.60, mult: 1.0 }, { min: 0.40, mult: 0.5 }, { min: 0, mult: 0 }
    ];
    for (const t of thresholds) {
        if (weekPct >= t.min) return profile.weekly_reward_base * t.mult * streakBonus;
    }
    return 0;
}

// ── Dashboard ────────────────────────────────

async function renderDashboard(slug) {
    try {
        const data = await api(`/api/profiles/${slug}/dashboard`);
        const grid = document.getElementById(`${slug}-dashboard-grid`);
        if (!grid) return;

        grid.innerHTML = data.habits.map(h => `
        <div class="dashboard-habit-card">
            <div class="dash-habit-header">
                <strong>${h.habit_name}</strong>
                <span class="dash-streak">🔥 ${h.current_streak}</span>
            </div>
            <div class="dash-bar-container">
                <div class="dash-bar" style="width:${Math.round(h.pct * 100)}%"></div>
            </div>
            <div class="dash-stats">
                <span>${Math.round(h.pct * 100)}% cumplimiento</span>
                <span>${h.completed_days}/${h.total_days} días</span>
            </div>
        </div>
        `).join('');
    } catch (e) { /* dashboard not critical */ }
}

// ── Family ───────────────────────────────────

function renderFamily() {
    const currency = appSettings.currency_symbol || '$';
    // Family tab always shows ALL profiles regardless of role
    const visibleProfiles = profiles;

    visibleProfiles.forEach(p => {
        const streak = computeStreak(p.slug);
        const weekData = computeWeekStats(p.slug);
        const earned = computeWeeklyEarned(p.slug, weekData.pct);

        const streakEl = document.getElementById(`fam-${p.slug}-streak`);
        if (streakEl) streakEl.textContent = `${streak} 🔥`;
        const pctEl = document.getElementById(`fam-${p.slug}-week-pct`);
        if (pctEl) pctEl.textContent = `${Math.round(weekData.pct * 100)}%`;
        const earnedEl = document.getElementById(`fam-${p.slug}-earned`);
        if (earnedEl) earnedEl.textContent = `${currency}${earned.toFixed(0)}`;

        renderWeekCalendar(p.slug, weekData.weekDates);
        renderMonthlyRing(p);
    });
}

function renderWeekCalendar(slug, weekDates) {
    const container = document.getElementById(`fam-${slug}-calendar`);
    if (!container) return;
    const log = state[slug]?.dayLog || {};
    const todayKey = today();
    container.innerHTML = '';
    weekDates.forEach(d => {
        const entry = log[d];
        const dayName = DIAS[new Date(d + 'T12:00:00').getDay()];
        const div = document.createElement('div');
        div.className = 'cal-day';
        let emoji = '⬜';
        if (d > todayKey) { div.classList.add('future'); emoji = '·'; }
        else if (entry?.pct === 1.0) { div.classList.add('done-full'); emoji = '✅'; }
        else if (entry?.pct >= 0.5) { div.classList.add('done-partial'); emoji = '🌟'; }
        else if (d <= todayKey) { div.classList.add('done-miss'); emoji = '😴'; }
        div.innerHTML = `<span class="day-dot">${emoji}</span><span class="day-label">${dayName}</span>`;
        container.appendChild(div);
    });
}

function renderMonthlyRing(profile) {
    const slug = profile.slug;
    const now = new Date();
    const year = now.getFullYear(), month = now.getMonth();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const todayKey = today();
    const log = state[slug]?.dayLog || {};
    let completed = 0, passed = 0;
    for (let i = 1; i <= daysInMonth; i++) {
        const d = new Date(year, month, i).toISOString().split('T')[0];
        if (d <= todayKey) { passed++; if (log[d]?.pct >= 0.5) completed++; }
    }
    const pct = passed > 0 ? completed / passed : 0;
    const circumference = 2 * Math.PI * 34;
    const ring = document.getElementById(`${slug}-ring`);
    if (ring) ring.setAttribute('stroke-dasharray', `${(pct * circumference).toFixed(1)} ${circumference.toFixed(1)}`);
    const pctEl = document.getElementById(`${slug}-month-pct`);
    if (pctEl) pctEl.textContent = `${Math.round(pct * 100)}%`;
    const rewardEl = document.getElementById(`${slug}-monthly-reward`);
    if (rewardEl) {
        if (pct >= (profile.monthly_min_pct || 0.75)) {
            rewardEl.textContent = '🎁 ¡Recompensa desbloqueada!';
            rewardEl.classList.add('unlocked');
        } else {
            rewardEl.textContent = `🔒 ${Math.round(pct * 100)}% de ${Math.round((profile.monthly_min_pct || 0.75) * 100)}%`;
            rewardEl.classList.remove('unlocked');
        }
    }
}

// ── Reset ────────────────────────────────────

function resetWeek() {
    if (!confirm('¿Cerrar la semana actual?')) return;
    profiles.forEach(p => { if (state[p.slug]) state[p.slug].shieldUsed = false; });
    saveState();
    renderFamily();
    alert('✅ Semana cerrada.');
}

// ── Modal ────────────────────────────────────

function showModal(emoji, title, msg, stars) {
    document.getElementById('modal-emoji').textContent = emoji;
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-msg').textContent = msg;
    document.getElementById('modal-stars').textContent = stars;
    document.getElementById('celebration-modal').classList.remove('hidden');
}
function closeModal() { document.getElementById('celebration-modal').classList.add('hidden'); }

// ── Confetti ─────────────────────────────────

function launchConfetti(count = 80) {
    const canvas = document.getElementById('confetti-canvas');
    canvas.width = window.innerWidth; canvas.height = window.innerHeight;
    const ctx = canvas.getContext('2d');
    const colors = ['#c084fc', '#f472b6', '#fb923c', '#fbbf24', '#34d399', '#60a5fa'];
    const pieces = Array.from({ length: count }, () => ({
        x: Math.random() * canvas.width, y: -20,
        r: Math.random() * 8 + 4, color: colors[Math.floor(Math.random() * colors.length)],
        vx: (Math.random() - 0.5) * 6, vy: Math.random() * 4 + 2,
        va: (Math.random() - 0.5) * 0.15, angle: Math.random() * Math.PI * 2, life: 1
    }));
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let alive = false;
        pieces.forEach(p => {
            p.x += p.vx; p.y += p.vy; p.angle += p.va; p.life -= 0.008;
            if (p.y < canvas.height && p.life > 0) alive = true;
            ctx.save(); ctx.globalAlpha = Math.max(0, p.life);
            ctx.translate(p.x, p.y); ctx.rotate(p.angle);
            ctx.fillStyle = p.color; ctx.fillRect(-p.r / 2, -p.r / 2, p.r, p.r * 0.6);
            ctx.restore();
        });
        if (alive) requestAnimationFrame(animate);
        else ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    animate();
}

function playCheckSound() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator(); const gain = ctx.createGain();
        osc.connect(gain); gain.connect(ctx.destination);
        osc.frequency.setValueAtTime(600, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(900, ctx.currentTime + 0.1);
        gain.gain.setValueAtTime(0.15, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);
        osc.start(); osc.stop(ctx.currentTime + 0.15);
    } catch (e) { }
}

function updateHeaderDate() {
    const now = new Date();
    const el = document.getElementById('header-date');
    if (el) {
        const dateStr = now.toLocaleDateString('es-MX', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        const hour = now.getHours();
        const greeting = hour < 12 ? '🌅 Buenos días' : hour < 18 ? '☀️ Buenas tardes' : '🌙 Buenas noches';
        el.innerHTML = `${greeting}<br><strong>${dateStr}</strong>`;
    }
}

// ── Web Notifications (Reminder System) ─────

let notificationPermission = Notification.permission;
let reminderTime = localStorage.getItem('habitosfam_reminder_time') || '20:00';
let reminderInterval = null;

async function requestNotificationPermission() {
    if (!('Notification' in window)) {
        console.warn('Notifications not supported');
        return false;
    }
    if (Notification.permission === 'granted') return true;
    if (Notification.permission === 'denied') {
        alert('Las notificaciones están bloqueadas. Por favor habilítalas en la configuración del navegador.');
        return false;
    }
    const permission = await Notification.requestPermission();
    notificationPermission = permission;
    return permission === 'granted';
}

function showNotification(title, body, icon = '🌟') {
    if (Notification.permission !== 'granted') return;
    try {
        new Notification(title, {
            body,
            icon: '/icon-192.png',
            badge: '/icon-192.png',
            tag: 'habitosfam-reminder',
            requireInteraction: false
        });
    } catch (e) { console.warn('Notification failed', e); }
}

function scheduleDailyReminder() {
    if (reminderInterval) clearInterval(reminderInterval);
    
    const checkAndNotify = () => {
        const now = new Date();
        const [hours, minutes] = reminderTime.split(':').map(Number);
        if (now.getHours() === hours && now.getMinutes() === minutes) {
            const profilesList = profiles.map(p => p.name).join(', ') || 'tus hijos';
            showNotification(
                '🌟 Recordatorio de Hábitos',
                `¡Es hora de revisar los hábitos de ${profilesList}!`,
                '📋'
            );
        }
    };
    
    reminderInterval = setInterval(checkAndNotify, 60000);
    checkAndNotify();
}

function setReminderTime(time) {
    reminderTime = time;
    localStorage.setItem('habitosfam_reminder_time', time);
    scheduleDailyReminder();
}

function getReminderSettings() {
    return {
        permission: notificationPermission,
        time: reminderTime,
        enabled: notificationPermission === 'granted'
    };
}

// ── Micro-habit dopamine effects ─────────────

function playMicroCheckSound() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain); gain.connect(ctx.destination);
        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 0.08);
        gain.gain.setValueAtTime(0.1, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.12);
        osc.start(); osc.stop(ctx.currentTime + 0.12);
    } catch (e) { }
}

function spawnMicroSparkle(e) {
    const emojis = ['✨', '⭐', '🌟', '💫', '🎯', '✅'];
    const count = 5;
    const x = e.clientX || (e.target?.getBoundingClientRect()?.left || 200) + 20;
    const y = e.clientY || (e.target?.getBoundingClientRect()?.top || 200);

    for (let i = 0; i < count; i++) {
        const spark = document.createElement('div');
        spark.className = 'micro-sparkle';
        spark.textContent = emojis[Math.floor(Math.random() * emojis.length)];
        spark.style.left = `${x + (Math.random() - 0.5) * 40}px`;
        spark.style.top = `${y}px`;
        spark.style.setProperty('--dx', `${(Math.random() - 0.5) * 60}px`);
        spark.style.setProperty('--dy', `${-30 - Math.random() * 50}px`);
        document.body.appendChild(spark);
        setTimeout(() => spark.remove(), 800);
    }
}

function launchMiniConfetti(cx, cy) {
    const canvas = document.getElementById('confetti-canvas');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const ctx = canvas.getContext('2d');
    const colors = ['#c084fc', '#f472b6', '#fb923c', '#fbbf24', '#34d399', '#60a5fa'];
    const pieces = Array.from({ length: 25 }, () => ({
        x: cx, y: cy,
        r: Math.random() * 6 + 3,
        color: colors[Math.floor(Math.random() * colors.length)],
        vx: (Math.random() - 0.5) * 8,
        vy: -(Math.random() * 6 + 2),
        va: (Math.random() - 0.5) * 0.2,
        angle: Math.random() * Math.PI * 2,
        life: 1
    }));
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let alive = false;
        pieces.forEach(p => {
            p.x += p.vx; p.y += p.vy; p.vy += 0.15;
            p.angle += p.va; p.life -= 0.02;
            if (p.life > 0) alive = true;
            ctx.save(); ctx.globalAlpha = Math.max(0, p.life);
            ctx.translate(p.x, p.y); ctx.rotate(p.angle);
            ctx.fillStyle = p.color;
            ctx.fillRect(-p.r / 2, -p.r / 2, p.r, p.r * 0.6);
            ctx.restore();
        });
        if (alive) requestAnimationFrame(animate);
        else ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    animate();
}

// ── Boot ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    setupPinInputs();
    init();
});
