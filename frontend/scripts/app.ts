/**
 * HábitosFam – frontend/scripts/app.ts
 * Main application logic converted to TypeScript.
 */

import { Profile, AppSettings, Habit } from './types.ts';
import { PROGRESS_MESSAGES, DIAS } from './data.ts';

// Add Chart.js global type if needed (since it's loaded via CDN)
declare const Chart: any;

const API = window.location.origin;

// ── Session state ────────────────────────────
interface Session {
    role: 'admin' | 'user' | null;
    profileSlug: string | null;
    token: string | null;
    pin: string | null;
}

let session: Session = {
    role: null,
    profileSlug: null,
    token: null,
    pin: null,
};

let profiles: Profile[] = [];
let habitsConfig: Record<string, Habit[]> = {}; 
let appSettings: Partial<AppSettings> = {};
let state: Record<string, any> = {}; 
let activeProfile: string | null = null;

// ── API helpers ──────────────────────────────

async function api(path: string, opts: RequestInit = {}): Promise<any> {
    const res = await fetch(`${API}${path}`, {
        headers: { 'Content-Type': 'application/json', ...opts.headers },
        ...opts
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

// ── Init ─────────────────────────────────────

export async function init() {
    // Load settings
    try { 
        appSettings = await api('/api/settings'); 
    } catch (e) { 
        appSettings = { currency: '$', app_name: 'HábitosFam' }; 
    }

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

export function toggleTheme() {
    const html = document.documentElement;
    const btn = document.getElementById('theme-toggle');
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('habitosfam_theme', newTheme);
    if (btn) btn.textContent = newTheme === 'light' ? '🌙' : '☀️';
}

export function initTheme() {
    const savedTheme = localStorage.getItem('habitosfam_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.textContent = savedTheme === 'light' ? '🌙' : '☀️';
}

// ── Login ────────────────────────────────────

export function showLoginOverlay() {
    const overlay = document.getElementById('login-overlay');
    const app = document.getElementById('app-container');
    const err = document.getElementById('login-error');
    
    if (overlay) overlay.classList.remove('hidden');
    if (app) app.classList.add('hidden');
    if (err) err.textContent = '';
    
    const inputs = document.querySelectorAll('.pin-input') as NodeListOf<HTMLInputElement>;
    inputs.forEach(i => i.value = '');
    inputs[0]?.focus();
}

export function setupPinInputs() {
    const inputs = document.querySelectorAll('.pin-input') as NodeListOf<HTMLInputElement>;
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

export async function submitLogin() {
    const inputs = document.querySelectorAll('.pin-input') as NodeListOf<HTMLInputElement>;
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
        const err = document.getElementById('login-error');
        if (err) err.textContent = 'PIN inválido. Intenta de nuevo.';
        inputs.forEach(i => i.value = '');
        inputs[0]?.focus();
    }
}

export function logout() {
    session = { role: null, profileSlug: null, token: null, pin: null };
    localStorage.removeItem('habitosfam_session');
    localStorage.removeItem('habitosfam_state');
    showLoginOverlay();
}

// ── Load App ─────────────────────────────────

export async function loadApp() {
    const overlay = document.getElementById('login-overlay');
    const app = document.getElementById('app-container');
    if (overlay) overlay.classList.add('hidden');
    if (app) app.classList.remove('hidden');

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

function buildTabs(visibleProfiles: Profile[]) {
    const nav = document.getElementById('tab-nav');
    if (!nav) return;
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

function buildProfileSections(visibleProfiles: Profile[]) {
    const main = document.getElementById('app-main');
    if (!main) return;
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

    const currency = appSettings.currency || '$';

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

        <!-- Trends Button -->
        <button class="complete-day-btn ${p.slug}-btn" id="${p.slug}-trends-btn" onclick="showTrendsTab('${p.slug}')">
            📈 Ver Tendencias
        </button>
        `;

        if (famSection) main.insertBefore(section, famSection);
    });

    // Rebuild family section with ALL profiles (not just visible)
    buildFamilySection(profiles, currency);
}

function buildFamilySection(visibleProfiles: Profile[], currency: string) {
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

export function switchProfile(name: string) {
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

function renderProfile(slug: string) {
    const habits = habitsConfig[slug] || [];
    const todayKey = today();
    const todayHabits = state[slug]?.habits[todayKey] || {};
    const grid = document.getElementById(`${slug}-habits-grid`);
    if (!grid) return;

    // Save expanded state before re-rendering
    const expandedKeys = new Set<string>();
    grid.querySelectorAll('.habit-card.expanded').forEach(card => {
        const key = card.id?.replace(`card-${slug}-`, '');
        if (key) expandedKeys.add(key);
    });

    grid.innerHTML = '';
    habits.forEach(habit => {
        // @ts-ignore (legacy schema)
        if (habit.is_active === false) return; 
        const hState = todayHabits[habit.key] || { done: false, miniTasks: {} };
        const card = createHabitCard(habit, hState, slug);
        // Restore expanded state
        if (expandedKeys.has(habit.key)) {
            card.classList.add('expanded');
        }
        grid.appendChild(card);
    });

    updateDailyProgress(slug);
    updateProfileHeader(slug);
    updateCompleteButton(slug);
}

function createHabitCard(habit: Habit, hState: any, slug: string) {
    const card = document.createElement('div');
    const profile = profiles.find(p => p.slug === slug);
    const themeClass = `${profile?.theme || slug}-theme`;
    card.className = `habit-card ${themeClass}${hState.done ? ' completed' : ''}`;
    card.id = `card-${slug}-${habit.key}`;

    const microHabits = habit.micro_habits || [];
    // @ts-ignore (legacy schema)
    const miniTasksHTML = microHabits.filter(m => m.is_active !== false).map((mh, i) => {
        const done = hState.miniTasks[i] || false;
        return `
        <div class="mini-task${done ? ' done' : ''}" onclick="toggleMiniTask('${slug}', '${habit.key}', ${i}, event)" id="mini-${slug}-${habit.key}-${i}">
            <div class="mini-task-check">${done ? '✓' : ''}</div>
            <span>${mh.description}</span>
        </div>`;
    }).join('');

    // @ts-ignore
    const activeMicro = microHabits.filter(m => m.is_active !== false);
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
        <div class="habit-check" id="check-${slug}-${habit.key}" onclick="toggleHabit('${slug}', '${habit.key}')">${hState.done ? '✓' : ''}</div>
        <div class="habit-expand" onclick="toggleExpand('${slug}','${habit.key}',event)">▼</div>
    </div>
    `;

    return card;
}

export function toggleExpand(slug: string, habitKey: string, e: MouseEvent) {
    e.stopPropagation();
    const card = document.getElementById(`card-${slug}-${habitKey}`);
    if (card) card.classList.toggle('expanded');
}

export function toggleHabit(slug: string, habitKey: string) {
    const todayKey = today();
    if (!state[slug].habits[todayKey]) state[slug].habits[todayKey] = {};
    const habits = state[slug].habits[todayKey];
    if (!habits[habitKey]) habits[habitKey] = { done: false, miniTasks: {} };

    habits[habitKey].done = !habits[habitKey].done;

    // Auto-complete micro tasks when main toggled on
    if (habits[habitKey].done) {
        const config = (habitsConfig[slug] || []).find(h => h.key === habitKey);
        // @ts-ignore
        const micros = (config?.micro_habits || []).filter(m => m.is_active !== false);
        micros.forEach((_, i) => { habits[habitKey].miniTasks[i] = true; });
        playCheckSound();
    } else {
        habits[habitKey].miniTasks = {};
    }

    saveState();
    syncHabitsToAPI(slug);
    renderProfile(slug);
}

export function toggleMiniTask(slug: string, habitKey: string, idx: number, e: MouseEvent) {
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
    const config = (habitsConfig[slug] || []).find(h => h.key === habitKey);
    // @ts-ignore
    const micros = (config?.micro_habits || []).filter(m => m.is_active !== false);
    const allDone = micros.every((_, i) => habits[habitKey].miniTasks[i]);
    if (allDone && micros.length > 0) {
        habits[habitKey].done = true;
        playCheckSound();
        // Extra dopamine: mini confetti burst for completing all micro-habits
        const target = e.target as HTMLElement;
        const rect = target.closest('.habit-card')?.getBoundingClientRect();
        if (rect) launchMiniConfetti(rect.left + rect.width / 2, rect.top);
    }

    saveState();
    syncHabitsToAPI(slug);
    renderProfile(slug);
}

// ── API Sync ─────────────────────────────────

async function syncHabitsToAPI(slug: string) {
    const todayKey = today();
    const habits = state[slug]?.habits[todayKey] || {};
    const entries = Object.entries(habits).map(([id, h]: [string, any]) => ({
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

async function syncCompleteDayToAPI(slug: string, done: number, total: number, pct: number) {
    try {
        await api(`/api/profiles/${slug}/complete-day`, {
            method: 'POST',
            body: JSON.stringify({ date: today(), completed_count: done, total, pct })
        });
    } catch (e) { console.warn('complete-day sync failed', e); }
}

async function loadTodayFromAPI(slug: string) {
    try {
        const log = await api(`/api/profiles/${slug}/today`);
        if (!log || log.id === 0) return;
        const todayKey = today();
        if (!state[slug].habits[todayKey]) state[slug].habits[todayKey] = {};
        if (log.habit_entries && log.habit_entries.length > 0) {
            log.habit_entries.forEach((entry: any) => {
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

function updateDailyProgress(slug: string) {
    const todayKey = today();
    const habits = state[slug]?.habits[todayKey] || {};
    // @ts-ignore
    const total = (habitsConfig[slug] || []).filter(h => h.is_active !== false).length;
    const done = Object.values(habits).filter((h: any) => h.done).length;
    const pct = total > 0 ? (done / total) * 100 : 0;

    const bar = document.getElementById(`${slug}-progress-bar`);
    if (bar) bar.style.width = `${pct}%`;
    const count = document.getElementById(`${slug}-daily-count`);
    if (count) count.textContent = `${done}/${total} hábitos`;

    const msgs = PROGRESS_MESSAGES[slug] || PROGRESS_MESSAGES._default;
    const msgEl = document.getElementById(`${slug}-progress-msg`);
    if (msgEl) msgEl.textContent = msgs[done] || msgs[0];
}

function updateProfileHeader(slug: string) {
    const streak = computeStreak(slug);
    const streakEl = document.getElementById(`${slug}-streak-days`);
    if (streakEl) streakEl.textContent = streak.toString();
    if (state[slug]) state[slug].streak = streak;

    const weekData = computeWeekStats(slug);
    const starsEl = document.getElementById(`${slug}-week-stars`);
    if (starsEl) starsEl.textContent = weekData.stars.toString();

    const earned = computeWeeklyEarned(slug, weekData.pct);
    const currency = appSettings.currency || '$';
    const coinsEl = document.getElementById(`${slug}-week-coins`);
    if (coinsEl) coinsEl.textContent = `${currency}${earned.toFixed(2)}`;
}

function updateCompleteButton(slug: string) {
    const todayKey = today();
    const habits = state[slug]?.habits[todayKey] || {};
    // @ts-ignore
    const total = (habitsConfig[slug] || []).filter(h => h.is_active !== false).length;
    const done = Object.values(habits).filter((h: any) => h.done).length;
    const pct = total > 0 ? done / total : 0;

    const btn = document.getElementById(`${slug}-complete-btn`) as HTMLButtonElement;
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

export function completeDay(slug: string) {
    const todayKey = today();
    const habits = state[slug]?.habits[todayKey] || {};
    // @ts-ignore
    const total = (habitsConfig[slug] || []).filter(h => h.is_active !== false).length;
    const done = Object.values(habits).filter((h: any) => h.done).length;
    const pct = total > 0 ? done / total : 0;

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

function computeStreak(slug: string) {
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

function computeWeekStats(slug: string) {
    const weekDates = getWeekDates();
    const log = state[slug]?.dayLog || {};
    let stars = 0, totalPossible = 0;
    weekDates.forEach(d => {
        const entry = log[d];
        if (entry) {
            stars += entry.completedCount;
            if (entry.completedCount === entry.total) stars++;
            totalPossible += entry.total;
        }
    });
    const pct = totalPossible > 0 ? stars / (totalPossible + 7) : 0;
    return { stars, pct, weekDates };
}

function computeWeeklyEarned(slug: string, weekPct: number) {
    const profile = profiles.find(p => p.slug === slug);
    if (!profile) return 0;
    const streak = state[slug]?.streak || 0;
    const streakBonus = streak >= (appSettings.streak_days || 7) ? (appSettings.streak_bonus_pct || 1.5) : 1.0;

    const thresholds = [
        { min: 0.90, mult: 2.0 }, { min: 0.75, mult: 1.5 },
        { min: 0.60, mult: 1.0 }, { min: 0.40, mult: 0.5 }, { min: 0, mult: 0 }
    ];
    for (const t of thresholds) {
        if (weekPct >= t.min) return profile.base_weekly_reward * t.mult * streakBonus;
    }
    return 0;
}

// ── Dashboard ────────────────────────────────

async function renderDashboard(slug: string) {
    try {
        const data = await api(`/api/profiles/${slug}/dashboard`);
        const grid = document.getElementById(`${slug}-dashboard-grid`);
        if (!grid) return;

        grid.innerHTML = data.habits.map((h: any) => `
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
    const currency = appSettings.currency || '$';
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

function renderWeekCalendar(slug: string, weekDates: string[]) {
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

function renderMonthlyRing(profile: Profile) {
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

export function resetWeek() {
    if (!confirm('¿Cerrar la semana actual?')) return;
    profiles.forEach(p => { if (state[p.slug]) state[p.slug].shieldUsed = false; });
    saveState();
    renderFamily();
    alert('✅ Semana cerrada.');
}

// ── Modal ────────────────────────────────────

function showModal(emoji: string, title: string, msg: string, stars: string) {
    const emojiEl = document.getElementById('modal-emoji');
    const titleEl = document.getElementById('modal-title');
    const msgEl = document.getElementById('modal-msg');
    const starsEl = document.getElementById('modal-stars');
    const modal = document.getElementById('celebration-modal');

    if (emojiEl) emojiEl.textContent = emoji;
    if (titleEl) titleEl.textContent = title;
    if (msgEl) msgEl.textContent = msg;
    if (starsEl) starsEl.textContent = stars;
    if (modal) modal.classList.remove('hidden');
}
export function closeModal() { 
    const modal = document.getElementById('celebration-modal');
    if (modal) modal.classList.add('hidden'); 
}

// ── Confetti ─────────────────────────────────

export function launchConfetti(count = 80) {
    const canvas = document.getElementById('confetti-canvas') as HTMLCanvasElement;
    if (!canvas) return;
    canvas.width = window.innerWidth; canvas.height = window.innerHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const colors = ['#c084fc', '#f472b6', '#fb923c', '#fbbf24', '#34d399', '#60a5fa'];
    const pieces = Array.from({ length: count }, () => ({
        x: Math.random() * canvas.width, y: -20,
        r: Math.random() * 8 + 4, color: colors[Math.floor(Math.random() * colors.length)],
        vx: (Math.random() - 0.5) * 6, vy: Math.random() * 4 + 2,
        va: (Math.random() - 0.5) * 0.15, angle: Math.random() * Math.PI * 2, life: 1
    }));
    function animate() {
        if (!ctx) return;
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
        const AudioCtx = (window as any).AudioContext || (window as any).webkitAudioContext;
        const ctx = new AudioCtx();
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

let reminderTime = localStorage.getItem('habitosfam_reminder_time') || '20:00';
let reminderInterval: any = null;

export async function requestNotificationPermission() {
    if (!('Notification' in window)) return false;
    if (Notification.permission === 'granted') return true;
    const permission = await Notification.requestPermission();
    return permission === 'granted';
}

function showNotification(title: string, body: string) {
    if (Notification.permission !== 'granted') return;
    try {
        new Notification(title, {
            body,
            icon: '/public/icon-192.png',
            badge: '/public/icon-192.png',
            tag: 'habitosfam-reminder',
            requireInteraction: false
        });
    } catch (e) { console.warn('Notification failed', e); }
}

export function scheduleDailyReminder() {
    if (reminderInterval) clearInterval(reminderInterval);
    
    const checkAndNotify = () => {
        const now = new Date();
        const [hours, minutes] = reminderTime.split(':').map(Number);
        if (now.getHours() === hours && now.getMinutes() === minutes) {
            const list = profiles.map(p => p.name).join(', ') || 'tus hijos';
            showNotification('Recordatorio', `¡Es hora de revisar los hábitos de ${list}!`);
        }
    };
    
    reminderInterval = setInterval(checkAndNotify, 60000);
}

// ── Micro-habit dopamine effects ─────────────

function playMicroCheckSound() {
    try {
        const AudioCtx = (window as any).AudioContext || (window as any).webkitAudioContext;
        const ctx = new AudioCtx();
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

function spawnMicroSparkle(e: MouseEvent) {
    const emojis = ['✨', '⭐', '🌟', '💫', '🎯', '✅'];
    const count = 5;
    const targetRect = (e.target as HTMLElement)?.getBoundingClientRect();
    const x = e.clientX || (targetRect?.left || 200) + 20;
    const y = e.clientY || (targetRect?.top || 200);

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

export function launchMiniConfetti(cx: number, cy: number) {
    const canvas = document.getElementById('confetti-canvas') as HTMLCanvasElement;
    if (!canvas) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
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
        if (!ctx) return;
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
    }
    animate();
}

// ── Charts ───────────────────────────────────

let trendChart: any = null;

export async function loadTrendsChart(slug: string) {
    const container = document.getElementById(`${slug}-trends-container`);
    if (!container) return;

    try {
        const period = container.dataset.period || 'weekly';
        const data = await api(`/api/profiles/${slug}/trends?period=${period}`);
        
        const canvas = document.getElementById(`${slug}-trend-chart`) as HTMLCanvasElement;
        const ctx = canvas.getContext('2d');
        
        if (trendChart) trendChart.destroy();
        
        const isLight = document.documentElement.getAttribute('data-theme') === 'light';
        const textColor = isLight ? '#1e293b' : '#f1f5f9';
        const gridColor = isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)';
        
        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.data.map((d: any) => {
                    const date = new Date(d.date);
                    return `${date.getDate()}/${date.getMonth() + 1}`;
                }),
                datasets: [{
                    label: '% Completado',
                    data: data.data.map((d: any) => (d.pct * 100).toFixed(0)),
                    borderColor: '#a855f7',
                    backgroundColor: 'rgba(168, 85, 247, 0.2)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#a855f7',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: textColor } },
                },
                scales: {
                    x: {
                        ticks: { color: textColor, maxTicksLimit: 7 },
                        grid: { color: gridColor }
                    },
                    y: {
                        min: 0,
                        max: 100,
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    }
                }
            }
        });
    } catch (e) {}
}

export function showTrendsTab(slug: string) {
    const section = document.getElementById(`profile-${slug}`);
    if (!section) return;
    
    let trendsTab = document.getElementById(`${slug}-trends-tab`);
    if (!trendsTab) {
        trendsTab = document.createElement('div');
        trendsTab.id = `${slug}-trends-tab`;
        trendsTab.className = 'trends-tab';
        trendsTab.innerHTML = `
            <div class="trends-header">
                <h3>📊 Tendencias</h3>
                <div class="period-selector">
                    <button class="period-btn active" data-period="weekly" onclick="setTrendPeriod('${slug}', 'weekly')">Semana</button>
                    <button class="period-btn" data-period="monthly" onclick="setTrendPeriod('${slug}', 'monthly')">Mes</button>
                </div>
            </div>
            <div class="trends-chart-container" id="${slug}-trends-container" data-period="weekly">
                <canvas id="${slug}-trend-chart"></canvas>
            </div>
        `;
        section.appendChild(trendsTab);
    }
    loadTrendsChart(slug);
}

export function setTrendPeriod(slug: string, period: string) {
    const container = document.getElementById(`${slug}-trends-container`);
    if (container) container.dataset.period = period;
    loadTrendsChart(slug);
}
