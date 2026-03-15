/**
 * HábitosFam – frontend/scripts/admin.ts
 * Admin panel logic converted to TypeScript.
 */

import { Profile, HealthInfo } from './types.ts';

const API = window.location.origin;
let adminPin: string = '';
let profiles: Profile[] = [];
let appSettings: any = {};


// ── API helper ────────────────────────────────

async function apiCall(path: string, opts: RequestInit = {}): Promise<any> {
    const headers = {
        'Content-Type': 'application/json',
        'X-Admin-Pin': adminPin,
        ...opts.headers,
    };
    const res = await fetch(`${API}${path}`, { ...opts, headers });
    if (res.status === 401) { logout(); throw new Error('Unauthorized'); }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Error' }));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
}

// ── Login/Logout ──────────────────────────────

export async function login() {
    const pinEl = document.getElementById('admin-pin') as HTMLInputElement;
    const pin = pinEl.value;
    if (!pin) return;
    try {
        await fetch(`${API}/api/admin/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pin })
        }).then(r => {
            if (!r.ok) throw new Error('Invalid PIN');
            return r.json();
        });
        adminPin = pin;
        localStorage.setItem('admin_pin', pin);
        document.getElementById('admin-login')?.classList.add('hidden');
        document.getElementById('admin-dashboard')?.classList.remove('hidden');
        loadDashboard();
    } catch (e) {
        const errEl = document.getElementById('login-error');
        if (errEl) errEl.textContent = '❌ PIN inválido';
    }
}

export function logout() {
    adminPin = '';
    localStorage.removeItem('admin_pin');
    document.getElementById('admin-login')?.classList.remove('hidden');
    document.getElementById('admin-dashboard')?.classList.add('hidden');
}

// ── Init ──────────────────────────────────────

export function initAdmin() {
    const saved = localStorage.getItem('admin_pin');
    if (saved) {
        adminPin = saved;
        document.getElementById('admin-login')?.classList.add('hidden');
        document.getElementById('admin-dashboard')?.classList.remove('hidden');
        loadDashboard();
    }
    document.getElementById('admin-pin')?.addEventListener('keydown', (e: KeyboardEvent) => {
        if (e.key === 'Enter') login();
    });
}

// ── Dashboard ─────────────────────────────────

async function loadDashboard() {
    try {
        // Load settings first for currency symbol
        try { appSettings = await apiCall('/api/admin/settings'); } catch (e) { appSettings = { currency_symbol: '$' }; }
        profiles = await apiCall('/api/admin/profiles');
        populateProfileSelects();
        loadProfiles();
        loadSettings();
        loadHealth();
    } catch (e) {
        console.error('Dashboard load error', e);
    }
}

function populateProfileSelects() {
    ['habit-profile-select', 'reward-profile-select', 'data-profile-select'].forEach(id => {
        const sel = document.getElementById(id) as HTMLSelectElement;
        if (!sel) return;
        sel.innerHTML = profiles.map(p =>
            `<option value="${p.slug}">${p.avatar} ${p.name} (${p.age}y)</option>`
        ).join('');
    });
}

// ── Tabs ──────────────────────────────────────

export function showSection(name: string, e: Event) {
    document.querySelectorAll('.admin-section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
    document.getElementById(`sec-${name}`)?.classList.add('active');
    (e.target as HTMLElement).classList.add('active');

    if (name === 'habits') loadHabits();
    if (name === 'rewards') loadRewardTiers();
    if (name === 'data') loadLogs();
}

// ── PROFILES ──────────────────────────────────

function loadProfiles() {
    const list = document.getElementById('profiles-list');
    if (!list) return;

    // @ts-ignore
    list.innerHTML = profiles.map(p => `
    <div class="admin-card ${p.is_active !== false ? '' : 'inactive'}">
        <div class="card-header">
            <span class="card-avatar">${p.avatar}</span>
            <div>
                <strong>${p.name}</strong>
                <span class="card-meta">${p.age} años · ${p.slug} · ${p.pin ? '🔒' : '🔓'}</span>
            </div>
        </div>
        <div class="card-stats">
            <span>💰 Base: ${appSettings.currency_symbol || '$'}${p.base_weekly_reward} / Full: ${appSettings.currency_symbol || '$'}${p.full_weekly_reward}</span>
            <span>📅 Mensual ${Math.round((p.monthly_min_pct || 0) * 100)}%: ${p.monthly_reward_desc}</span>
        </div>
        <div class="card-actions">
            <button class="btn-sm" onclick="editProfile('${p.slug}')">✏️ Editar</button>
            ${p.is_active !== false ? `<button class="btn-sm danger" onclick="deactivateProfile('${p.slug}')">🗑️</button>` : ''}
        </div>
    </div>
    `).join('');
}

export function showAddProfile() {
    const title = document.getElementById('profile-modal-title');
    if (title) title.textContent = 'Nuevo Perfil';
    
    (document.getElementById('pf-slug-original') as HTMLInputElement).value = '';
    ['pf-slug', 'pf-name', 'pf-avatar', 'pf-theme', 'pf-pin', 'pf-monthly-desc'].forEach(id => {
        (document.getElementById(id) as HTMLInputElement).value = '';
    });
    
    (document.getElementById('pf-age') as HTMLInputElement).value = '';
    (document.getElementById('pf-base') as HTMLInputElement).value = '2';
    (document.getElementById('pf-full') as HTMLInputElement).value = '4';
    (document.getElementById('pf-monthly-pct') as HTMLInputElement).value = '0.75';
    (document.getElementById('pf-slug') as HTMLInputElement).disabled = false;
    document.getElementById('profile-modal')?.classList.remove('hidden');
}

export function editProfile(slug: string) {
    const p = profiles.find(pr => pr.slug === slug);
    if (!p) return;
    const title = document.getElementById('profile-modal-title');
    if (title) title.textContent = `Editar ${p.name}`;
    
    (document.getElementById('pf-slug-original') as HTMLInputElement).value = slug;
    (document.getElementById('pf-slug') as HTMLInputElement).value = slug;
    (document.getElementById('pf-slug') as HTMLInputElement).disabled = true;
    (document.getElementById('pf-name') as HTMLInputElement).value = p.name;
    (document.getElementById('pf-age') as HTMLInputElement).value = p.age.toString();
    (document.getElementById('pf-avatar') as HTMLInputElement).value = p.avatar;
    (document.getElementById('pf-theme') as HTMLInputElement).value = p.theme;
    (document.getElementById('pf-pin') as HTMLInputElement).value = '';
    (document.getElementById('pf-base') as HTMLInputElement).value = p.base_weekly_reward.toString();
    (document.getElementById('pf-full') as HTMLInputElement).value = p.full_weekly_reward.toString();
    (document.getElementById('pf-monthly-pct') as HTMLInputElement).value = p.monthly_min_pct.toString();
    (document.getElementById('pf-monthly-desc') as HTMLTextAreaElement).value = p.monthly_reward_desc;
    document.getElementById('profile-modal')?.classList.remove('hidden');
}

export async function saveProfile(e: Event) {
    e.preventDefault();
    const original = (document.getElementById('pf-slug-original') as HTMLInputElement).value;
    const isEdit = !!original;
    const data: any = {
        slug: (document.getElementById('pf-slug') as HTMLInputElement).value,
        name: (document.getElementById('pf-name') as HTMLInputElement).value,
        age: parseInt((document.getElementById('pf-age') as HTMLInputElement).value),
        avatar: (document.getElementById('pf-avatar') as HTMLInputElement).value || '⭐',
        theme: (document.getElementById('pf-theme') as HTMLInputElement).value || 'default',
        weekly_reward_base: parseFloat((document.getElementById('pf-base') as HTMLInputElement).value),
        weekly_reward_full: parseFloat((document.getElementById('pf-full') as HTMLInputElement).value),
        monthly_min_pct: parseFloat((document.getElementById('pf-monthly-pct') as HTMLInputElement).value),
        monthly_reward_desc: (document.getElementById('pf-monthly-desc') as HTMLTextAreaElement).value,
    };
    const pin = (document.getElementById('pf-pin') as HTMLInputElement).value;
    if (pin) data.pin = pin;

    try {
        if (isEdit) {
            await apiCall(`/api/admin/profiles/${original}`, { method: 'PATCH', body: JSON.stringify(data) });
        } else {
            await apiCall('/api/admin/profiles', { method: 'POST', body: JSON.stringify(data) });
        }
        closeModalWindow('profile-modal');
        profiles = await apiCall('/api/admin/profiles');
        populateProfileSelects();
        loadProfiles();
    } catch (e: any) { alert('Error: ' + e.message); }
}

export async function deactivateProfile(slug: string) {
    if (!confirm(`¿Desactivar perfil "${slug}"?`)) return;
    try {
        await apiCall(`/api/admin/profiles/${slug}`, { method: 'DELETE' });
        profiles = await apiCall('/api/admin/profiles');
        populateProfileSelects();
        loadProfiles();
    } catch (e: any) { alert('Error: ' + e.message); }
}

// ── HABITS ────────────────────────────────────

export async function loadHabits() {
    const slug = (document.getElementById('habit-profile-select') as HTMLSelectElement).value;
    if (!slug) return;
    try {
        const habits = await apiCall(`/api/admin/profiles/${slug}/habits`);
        const list = document.getElementById('habits-list');
        if (!list) return;
        list.innerHTML = habits.map((h: any) => `
        <div class="habit-admin-card draggable-item ${h.is_active ? '' : 'inactive'}" 
             draggable="true" data-habit-id="${h.id}" data-sort="${h.sort_order}">
            <div class="habit-admin-header">
                <span class="drag-handle">☰</span>
                <span>${h.icon} ${h.name}</span>
                <div class="habit-admin-actions">
                    <button class="btn-sm" onclick="editHabit(${h.id})">✏️</button>
                    <button class="btn-sm" onclick="addMicroHabit(${h.id})">➕ Micro</button>
                    ${h.is_active ? `<button class="btn-sm danger" onclick="deleteHabit(${h.id})">🗑️</button>` : ''}
                </div>
            </div>
            <div class="habit-admin-meta">${h.habit_key} · ⭐${h.stars} · ${h.category}</div>
            <div class="micro-habits-list">
                ${(h.micro_habits || []).filter((m: any) => m.is_active).map((m: any) => `
                <div class="micro-item">
                    <span>${m.description}</span>
                    <div>
                        <button class="btn-xs" onclick="editMicro(${m.id}, '${m.description.replace(/'/g, "\\'")}', ${m.sort_order}, ${h.id})">✏️</button>
                        <button class="btn-xs danger" onclick="deleteMicro(${m.id})">✕</button>
                    </div>
                </div>`).join('')}
            </div>
        </div>`).join('');
        
        setupDragAndDrop();
    } catch (e) { console.error(e); }
}

function setupDragAndDrop() {
    const items = document.querySelectorAll('.draggable-item');
    let draggedItem: HTMLElement | null = null;
    
    items.forEach((node) => {
        const item = node as HTMLElement;
        item.addEventListener('dragstart', (e) => {
            draggedItem = item;
            item.classList.add('dragging');
            if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move';
        });
        
        item.addEventListener('dragend', () => {
            item.classList.remove('dragging');
            items.forEach(i => (i as HTMLElement).classList.remove('drag-over'));
            draggedItem = null;
        });
        
        item.addEventListener('dragover', (e) => {
            e.preventDefault();
            if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
        });
        
        item.addEventListener('dragenter', (e) => {
            e.preventDefault();
            if (item !== draggedItem) {
                item.classList.add('drag-over');
            }
        });
        
        item.addEventListener('dragleave', () => {
            item.classList.remove('drag-over');
        });
        
        item.addEventListener('drop', async (e) => {
            e.preventDefault();
            if (item === draggedItem || !draggedItem) return;
            
            const list = document.getElementById('habits-list');
            if (!list) return;

            const allItems = Array.from(list.querySelectorAll('.draggable-item'));
            const fromIdx = allItems.indexOf(draggedItem);
            const toIdx = allItems.indexOf(item);
            
            if (fromIdx === -1 || toIdx === -1) return;
            
            // Reorder in DOM
            if (fromIdx < toIdx) {
                item.parentNode?.insertBefore(draggedItem, item.nextSibling);
            } else {
                item.parentNode?.insertBefore(draggedItem, item);
            }
            
            // Update sort orders
            const newItems = Array.from(list.querySelectorAll('.draggable-item')) as HTMLElement[];
            const updates = newItems.map((it, idx) => ({
                id: parseInt(it.dataset.habitId || '0'),
                sort_order: idx
            }));
            
            // Save to API
            try {
                const slug = (document.getElementById('habit-profile-select') as HTMLSelectElement).value;
                await apiCall(`/api/admin/profiles/${slug}/habits/reorder`, {
                    method: 'POST',
                    body: JSON.stringify({ orders: updates })
                });
            } catch (e) {
                console.error('Failed to save order', e);
                loadHabits(); 
            }
        });
    });
}

export function showAddHabit() {
    const title = document.getElementById('habit-modal-title');
    if (title) title.textContent = 'Nuevo Hábito';
    (document.getElementById('ht-id') as HTMLInputElement).value = '';
    ['ht-key', 'ht-name', 'ht-desc', 'ht-motivation', 'ht-icon'].forEach(id => {
        (document.getElementById(id) as HTMLInputElement).value = '';
    });
    (document.getElementById('ht-cat') as HTMLSelectElement).value = 'general';
    (document.getElementById('ht-stars') as HTMLInputElement).value = '1';
    (document.getElementById('ht-order') as HTMLInputElement).value = '0';
    document.getElementById('habit-modal')?.classList.remove('hidden');
}

export async function editHabit(id: number) {
    const slug = (document.getElementById('habit-profile-select') as HTMLSelectElement).value;
    try {
        const habits = await apiCall(`/api/admin/profiles/${slug}/habits`);
        const h = habits.find((x: any) => x.id === id);
        if (!h) return;
        
        const title = document.getElementById('habit-modal-title');
        if (title) title.textContent = `Editar ${h.name}`;
        (document.getElementById('ht-id') as HTMLInputElement).value = h.id;
        (document.getElementById('ht-key') as HTMLInputElement).value = h.habit_key;
        (document.getElementById('ht-name') as HTMLInputElement).value = h.name;
        (document.getElementById('ht-icon') as HTMLInputElement).value = h.icon;
        (document.getElementById('ht-cat') as HTMLSelectElement).value = h.category;
        (document.getElementById('ht-stars') as HTMLInputElement).value = h.stars;
        (document.getElementById('ht-desc') as HTMLTextAreaElement).value = h.description || '';
        (document.getElementById('ht-motivation') as HTMLTextAreaElement).value = h.motivation || '';
        (document.getElementById('ht-order') as HTMLInputElement).value = h.sort_order || 0;
        
        document.getElementById('habit-modal')?.classList.remove('hidden');
    } catch (e: any) { alert('Error: ' + e.message); }
}

export async function saveHabit(e: Event) {
    e.preventDefault();
    const slug = (document.getElementById('habit-profile-select') as HTMLSelectElement).value;
    const id = (document.getElementById('ht-id') as HTMLInputElement).value;
    const data = {
        habit_key: (document.getElementById('ht-key') as HTMLInputElement).value,
        name: (document.getElementById('ht-name') as HTMLInputElement).value,
        icon: (document.getElementById('ht-icon') as HTMLInputElement).value || '⭐',
        category: (document.getElementById('ht-cat') as HTMLSelectElement).value,
        stars: parseInt((document.getElementById('ht-stars') as HTMLInputElement).value),
        description: (document.getElementById('ht-desc') as HTMLTextAreaElement).value,
        motivation: (document.getElementById('ht-motivation') as HTMLTextAreaElement).value,
        sort_order: parseInt((document.getElementById('ht-order') as HTMLInputElement).value),
    };
    try {
        if (id) {
            await apiCall(`/api/admin/habits/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
        } else {
            await apiCall(`/api/admin/profiles/${slug}/habits`, { method: 'POST', body: JSON.stringify(data) });
        }
        closeModalWindow('habit-modal');
        loadHabits();
    } catch (e: any) { alert('Error: ' + e.message); }
}

export async function deleteHabit(id: number) {
    if (!confirm('¿Desactivar este hábito?')) return;
    try {
        await apiCall(`/api/admin/habits/${id}`, { method: 'DELETE' });
        loadHabits();
    } catch (e: any) { alert('Error: ' + e.message); }
}

// ── MICRO-HABITS ──────────────────────────────

export function addMicroHabit(habitId: number) {
    (document.getElementById('mh-id') as HTMLInputElement).value = '';
    (document.getElementById('mh-habit-id') as HTMLInputElement).value = habitId.toString();
    (document.getElementById('mh-desc') as HTMLInputElement).value = '';
    (document.getElementById('mh-order') as HTMLInputElement).value = '0';
    document.getElementById('micro-modal')?.classList.remove('hidden');
}

export function editMicro(id: number, desc: string, order: number, habitId: number) {
    (document.getElementById('mh-id') as HTMLInputElement).value = id.toString();
    (document.getElementById('mh-habit-id') as HTMLInputElement).value = habitId.toString();
    (document.getElementById('mh-desc') as HTMLInputElement).value = desc;
    (document.getElementById('mh-order') as HTMLInputElement).value = order.toString();
    document.getElementById('micro-modal')?.classList.remove('hidden');
}

export async function saveMicro(e: Event) {
    e.preventDefault();
    const id = (document.getElementById('mh-id') as HTMLInputElement).value;
    const habitId = (document.getElementById('mh-habit-id') as HTMLInputElement).value;
    const data = {
        description: (document.getElementById('mh-desc') as HTMLInputElement).value,
        sort_order: parseInt((document.getElementById('mh-order') as HTMLInputElement).value),
    };
    try {
        if (id) {
            await apiCall(`/api/admin/micro-habits/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
        } else {
            await apiCall(`/api/admin/habits/${habitId}/micro-habits`, { method: 'POST', body: JSON.stringify(data) });
        }
        closeModalWindow('micro-modal');
        loadHabits();
    } catch (e: any) { alert('Error: ' + e.message); }
}

export async function deleteMicro(id: number) {
    if (!confirm('¿Eliminar este micro-hábito?')) return;
    try {
        await apiCall(`/api/admin/micro-habits/${id}`, { method: 'DELETE' });
        loadHabits();
    } catch (e: any) { alert('Error: ' + e.message); }
}

// ── REWARD TIERS ──────────────────────────────

export async function loadRewardTiers() {
    const slug = (document.getElementById('reward-profile-select') as HTMLSelectElement).value;
    if (!slug) return;
    try {
        const tiers = await apiCall(`/api/admin/profiles/${slug}/reward-tiers?tier_type=weekly`);
        const list = document.getElementById('reward-tiers-list');
        if (!list) return;
        list.innerHTML = tiers.length ? tiers.map((t: any, i: number) => tierRow(t, i)).join('') :
            '<p class="empty-msg">No hay niveles configurados.</p>';
    } catch (e) { console.error(e); }
}

function tierRow(t: any, i: number) {
    return `
    <div class="tier-row" data-idx="${i}">
        <input type="number" class="tier-pct" value="${t.min_pct}" step="0.05" min="0" max="1" placeholder="Min %" />
        <input type="number" class="tier-mult" value="${t.multiplier}" step="0.5" min="0" placeholder="×Mult" />
        <input type="text" class="tier-label" value="${t.label}" placeholder="Label" />
        <input type="text" class="tier-emoji" value="${t.emoji}" maxlength="4" placeholder="Emoji" />
        <button class="btn-xs danger" onclick="this.parentElement.remove()">✕</button>
    </div>`;
}

export function addTierRow() {
    const list = document.getElementById('reward-tiers-list');
    if (!list) return;
    const idx = list.children.length;
    const div = document.createElement('div');
    div.innerHTML = tierRow({ min_pct: 0, multiplier: 1, label: '', emoji: '' }, idx);
    list.appendChild(div.firstElementChild!);
}

export async function saveTiers() {
    const slug = (document.getElementById('reward-profile-select') as HTMLSelectElement).value;
    const rows = document.querySelectorAll('.tier-row');
    const tiers = Array.from(rows).map((r, i) => ({
        tier_type: 'weekly',
        min_pct: parseFloat((r.querySelector('.tier-pct') as HTMLInputElement).value),
        multiplier: parseFloat((r.querySelector('.tier-mult') as HTMLInputElement).value),
        label: (r.querySelector('.tier-label') as HTMLInputElement).value,
        emoji: (r.querySelector('.tier-emoji') as HTMLInputElement).value,
        sort_order: i,
    }));
    try {
        await apiCall(`/api/admin/profiles/${slug}/reward-tiers`, {
            method: 'PUT', body: JSON.stringify(tiers)
        });
        alert('✅ Niveles guardados');
        loadRewardTiers();
    } catch (e: any) { alert('Error: ' + e.message); }
}

// ── SETTINGS ──────────────────────────────────

export async function loadSettings() {
    try {
        const s = await apiCall('/api/admin/settings');
        (document.getElementById('set-currency') as HTMLInputElement).value = s.currency_symbol;
        (document.getElementById('set-app-name') as HTMLInputElement).value = s.app_name;
        (document.getElementById('set-streak-days') as HTMLInputElement).value = s.streak_bonus_days;
        (document.getElementById('set-streak-pct') as HTMLInputElement).value = s.streak_bonus_pct;
    } catch (e) { console.error(e); }
}

export async function saveSettings(e: Event) {
    e.preventDefault();
    const data: any = {
        currency_symbol: (document.getElementById('set-currency') as HTMLInputElement).value,
        app_name: (document.getElementById('set-app-name') as HTMLInputElement).value,
        streak_bonus_days: parseInt((document.getElementById('set-streak-days') as HTMLInputElement).value),
        streak_bonus_pct: parseFloat((document.getElementById('set-streak-pct') as HTMLInputElement).value),
    };
    const pin = (document.getElementById('set-admin-pin') as HTMLInputElement).value;
    if (pin) data.admin_pin = pin;
    try {
        await apiCall('/api/admin/settings', { method: 'PUT', body: JSON.stringify(data) });
        alert('✅ Configuración guardada');
        if (pin) {
            adminPin = pin;
            localStorage.setItem('admin_pin', pin);
        }
    } catch (e: any) { alert('Error: ' + e.message); }
}

// ── DATA ──────────────────────────────────────

export async function loadLogs() {
    const slug = (document.getElementById('data-profile-select') as HTMLSelectElement).value;
    if (!slug) return;
    try {
        const logs = await apiCall(`/api/admin/profiles/${slug}/logs`);
        const list = document.getElementById('logs-list');
        if (!list) return;
        if (!logs.length) { list.innerHTML = '<p class="empty-msg">Sin registros.</p>'; return; }
        list.innerHTML = `<table class="data-table"><thead><tr><th>Fecha</th><th>Done</th><th>Total</th><th>%</th><th>✅</th><th></th></tr></thead><tbody>
        ${logs.map((l: any) => `<tr>
            <td>${l.date}</td><td>${l.completed_count}</td><td>${l.total}</td>
            <td>${Math.round(l.pct * 100)}%</td><td>${l.day_done ? '✅' : '—'}</td>
            <td><button class="btn-xs danger" onclick="deleteLog('${slug}', '${l.date}')">🗑️</button></td>
        </tr>`).join('')}
        </tbody></table>`;
    } catch (e) { console.error(e); }

    const exportLink = document.getElementById('export-csv-link') as HTMLAnchorElement;
    if (exportLink) exportLink.href = `${API}/api/admin/export/csv`;
}

export async function deleteLog(slug: string, dateStr: string) {
    if (!confirm(`¿Eliminar registro ${dateStr}?`)) return;
    try {
        await apiCall(`/api/admin/profiles/${slug}/logs/${dateStr}`, { method: 'DELETE' });
        loadLogs();
    } catch (e: any) { alert('Error: ' + e.message); }
}

async function loadHealth() {
    try {
        const h: HealthInfo = await apiCall('/api/admin/health');
        const el = document.getElementById('health-info');
        if (!el) return;
        el.innerHTML = `
        <div class="health-item"><span>Estado</span><strong>${h.status === 'ok' ? '🟢 Online' : '🔴 Error'}</strong></div>
        <div class="health-item"><span>Motor DB</span><strong>${h.db_engine}</strong></div>
        <div class="health-item"><span>Perfiles</span><strong>${h.profiles}</strong></div>
        <div class="health-item"><span>Registros</span><strong>${h.total_day_logs}</strong></div>
        `;
    } catch (e) { console.error(e); }
}

export async function resetAllData() {
    if (!confirm('⚠️ ¿BORRAR TODOS los datos? Esta acción no se puede deshacer.')) return;
    if (!confirm('¿Estás realmente seguro?')) return;
    try {
        await apiCall('/api/admin/reset-all-data', { method: 'POST' });
        alert('✅ Todos los datos han sido borrados');
        loadLogs();
        loadHealth();
    } catch (e: any) { alert('Error: ' + e.message); }
}

// ── Modal helper ──────────────────────────────

export function closeModalWindow(id: string) {
    document.getElementById(id)?.classList.add('hidden');
}
