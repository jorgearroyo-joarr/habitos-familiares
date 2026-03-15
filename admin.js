// ============================================
// HábitosFam – admin.js  (v3)
// Admin panel: profiles, habits, micro-habits,
// reward tiers, settings, data management
// ============================================

const API = window.location.origin;
let adminPin = '';
let profiles = [];
let appSettings = {};
let currentSection = 'profiles';

// ── API helper ────────────────────────────────

async function apiCall(path, opts = {}) {
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

async function login() {
    const pin = document.getElementById('admin-pin').value;
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
        document.getElementById('admin-login').classList.add('hidden');
        document.getElementById('admin-dashboard').classList.remove('hidden');
        loadDashboard();
    } catch (e) {
        document.getElementById('login-error').textContent = '❌ PIN inválido';
    }
}

function logout() {
    adminPin = '';
    localStorage.removeItem('admin_pin');
    document.getElementById('admin-login').classList.remove('hidden');
    document.getElementById('admin-dashboard').classList.add('hidden');
}

// ── Init ──────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('admin_pin');
    if (saved) {
        adminPin = saved;
        document.getElementById('admin-login').classList.add('hidden');
        document.getElementById('admin-dashboard').classList.remove('hidden');
        loadDashboard();
    }
    document.getElementById('admin-pin').addEventListener('keydown', e => {
        if (e.key === 'Enter') login();
    });
});

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
        const sel = document.getElementById(id);
        if (!sel) return;
        sel.innerHTML = profiles.map(p =>
            `<option value="${p.slug}">${p.avatar} ${p.name} (${p.age}y)</option>`
        ).join('');
    });
}

// ── Tabs ──────────────────────────────────────

function showSection(name) {
    currentSection = name;
    document.querySelectorAll('.admin-section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
    document.getElementById(`sec-${name}`).classList.add('active');
    event.target.classList.add('active');

    if (name === 'habits') loadHabits();
    if (name === 'rewards') loadRewardTiers();
    if (name === 'data') loadLogs();
}

// ── PROFILES ──────────────────────────────────

function loadProfiles() {
    const list = document.getElementById('profiles-list');
    list.innerHTML = profiles.map(p => `
    <div class="admin-card ${p.is_active ? '' : 'inactive'}">
        <div class="card-header">
            <span class="card-avatar">${p.avatar}</span>
            <div>
                <strong>${p.name}</strong>
                <span class="card-meta">${p.age} años · ${p.slug} · ${p.has_pin ? '🔒' : '🔓'}</span>
            </div>
        </div>
        <div class="card-stats">
            <span>💰 Base: ${appSettings.currency_symbol || '$'}${p.weekly_reward_base} / Full: ${appSettings.currency_symbol || '$'}${p.weekly_reward_full}</span>
            <span>📅 Mensual ${Math.round(p.monthly_min_pct * 100)}%: ${p.monthly_reward_desc}</span>
        </div>
        <div class="card-actions">
            <button class="btn-sm" onclick="editProfile('${p.slug}')">✏️ Editar</button>
            ${p.is_active ? `<button class="btn-sm danger" onclick="deactivateProfile('${p.slug}')">🗑️</button>` : ''}
        </div>
    </div>
    `).join('');
}

function showAddProfile() {
    document.getElementById('profile-modal-title').textContent = 'Nuevo Perfil';
    document.getElementById('pf-slug-original').value = '';
    ['pf-slug', 'pf-name', 'pf-avatar', 'pf-theme', 'pf-pin', 'pf-monthly-desc'].forEach(id =>
        document.getElementById(id).value = '');
    document.getElementById('pf-age').value = '';
    document.getElementById('pf-base').value = '2';
    document.getElementById('pf-full').value = '4';
    document.getElementById('pf-monthly-pct').value = '0.75';
    document.getElementById('pf-slug').disabled = false;
    document.getElementById('profile-modal').classList.remove('hidden');
}

function editProfile(slug) {
    const p = profiles.find(pr => pr.slug === slug);
    if (!p) return;
    document.getElementById('profile-modal-title').textContent = `Editar ${p.name}`;
    document.getElementById('pf-slug-original').value = slug;
    document.getElementById('pf-slug').value = slug;
    document.getElementById('pf-slug').disabled = true;
    document.getElementById('pf-name').value = p.name;
    document.getElementById('pf-age').value = p.age;
    document.getElementById('pf-avatar').value = p.avatar;
    document.getElementById('pf-theme').value = p.theme;
    document.getElementById('pf-pin').value = '';
    document.getElementById('pf-base').value = p.weekly_reward_base;
    document.getElementById('pf-full').value = p.weekly_reward_full;
    document.getElementById('pf-monthly-pct').value = p.monthly_min_pct;
    document.getElementById('pf-monthly-desc').value = p.monthly_reward_desc;
    document.getElementById('profile-modal').classList.remove('hidden');
}

async function saveProfile(e) {
    e.preventDefault();
    const original = document.getElementById('pf-slug-original').value;
    const isEdit = !!original;
    const data = {
        slug: document.getElementById('pf-slug').value,
        name: document.getElementById('pf-name').value,
        age: parseInt(document.getElementById('pf-age').value),
        avatar: document.getElementById('pf-avatar').value || '⭐',
        theme: document.getElementById('pf-theme').value || 'default',
        weekly_reward_base: parseFloat(document.getElementById('pf-base').value),
        weekly_reward_full: parseFloat(document.getElementById('pf-full').value),
        monthly_min_pct: parseFloat(document.getElementById('pf-monthly-pct').value),
        monthly_reward_desc: document.getElementById('pf-monthly-desc').value,
    };
    const pin = document.getElementById('pf-pin').value;
    if (pin) data.pin = pin;

    try {
        if (isEdit) {
            await apiCall(`/api/admin/profiles/${original}`, { method: 'PATCH', body: JSON.stringify(data) });
        } else {
            await apiCall('/api/admin/profiles', { method: 'POST', body: JSON.stringify(data) });
        }
        closeModal('profile-modal');
        profiles = await apiCall('/api/admin/profiles');
        populateProfileSelects();
        loadProfiles();
    } catch (e) { alert('Error: ' + e.message); }
}

async function deactivateProfile(slug) {
    if (!confirm(`¿Desactivar perfil "${slug}"?`)) return;
    try {
        await apiCall(`/api/admin/profiles/${slug}`, { method: 'DELETE' });
        profiles = await apiCall('/api/admin/profiles');
        populateProfileSelects();
        loadProfiles();
    } catch (e) { alert('Error: ' + e.message); }
}

// ── HABITS ────────────────────────────────────

async function loadHabits() {
    const slug = document.getElementById('habit-profile-select').value;
    if (!slug) return;
    try {
        const habits = await apiCall(`/api/admin/profiles/${slug}/habits`);
        const list = document.getElementById('habits-list');
        list.innerHTML = habits.map(h => `
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
                ${h.micro_habits.filter(m => m.is_active).map(m => `
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
    let draggedItem = null;
    
    items.forEach(item => {
        item.addEventListener('dragstart', (e) => {
            draggedItem = item;
            item.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        });
        
        item.addEventListener('dragend', () => {
            item.classList.remove('dragging');
            items.forEach(i => i.classList.remove('drag-over'));
            draggedItem = null;
        });
        
        item.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
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
            if (item === draggedItem) return;
            
            const list = document.getElementById('habits-list');
            const allItems = Array.from(list.querySelectorAll('.draggable-item'));
            const fromIdx = allItems.indexOf(draggedItem);
            const toIdx = allItems.indexOf(item);
            
            if (fromIdx === -1 || toIdx === -1) return;
            
            // Reorder in DOM
            if (fromIdx < toIdx) {
                item.parentNode.insertBefore(draggedItem, item.nextSibling);
            } else {
                item.parentNode.insertBefore(draggedItem, item);
            }
            
            // Update sort orders
            const newItems = Array.from(list.querySelectorAll('.draggable-item'));
            const updates = newItems.map((it, idx) => ({
                id: parseInt(it.dataset.habitId),
                sort_order: idx
            }));
            
            // Save to API
            try {
                const slug = document.getElementById('habit-profile-select').value;
                await apiCall(`/api/admin/profiles/${slug}/habits/reorder`, {
                    method: 'POST',
                    body: JSON.stringify({ orders: updates })
                });
            } catch (e) {
                console.error('Failed to save order', e);
                loadHabits(); // Reload on error
            }
        });
    });
}

function showAddHabit() {
    document.getElementById('habit-modal-title').textContent = 'Nuevo Hábito';
    document.getElementById('ht-id').value = '';
    ['ht-key', 'ht-name', 'ht-desc', 'ht-motivation', 'ht-icon'].forEach(id =>
        document.getElementById(id).value = '');
    document.getElementById('ht-cat').value = 'general';
    document.getElementById('ht-stars').value = '1';
    document.getElementById('ht-order').value = '0';
    document.getElementById('habit-modal').classList.remove('hidden');
}

async function editHabit(id) {
    const slug = document.getElementById('habit-profile-select').value;
    try {
        const habits = await apiCall(`/api/admin/profiles/${slug}/habits`);
        const h = habits.find(x => x.id === id);
        if (!h) return;
        
        document.getElementById('habit-modal-title').textContent = `Editar ${h.name}`;
        document.getElementById('ht-id').value = h.id;
        document.getElementById('ht-key').value = h.habit_key;
        document.getElementById('ht-name').value = h.name;
        document.getElementById('ht-icon').value = h.icon;
        document.getElementById('ht-cat').value = h.category;
        document.getElementById('ht-stars').value = h.stars;
        document.getElementById('ht-desc').value = h.description || '';
        document.getElementById('ht-motivation').value = h.motivation || '';
        document.getElementById('ht-order').value = h.sort_order || 0;
        
        document.getElementById('habit-modal').classList.remove('hidden');
    } catch (e) { alert('Error: ' + e.message); }
}

async function saveHabit(e) {
    e.preventDefault();
    const slug = document.getElementById('habit-profile-select').value;
    const id = document.getElementById('ht-id').value;
    const data = {
        habit_key: document.getElementById('ht-key').value,
        name: document.getElementById('ht-name').value,
        icon: document.getElementById('ht-icon').value || '⭐',
        category: document.getElementById('ht-cat').value,
        stars: parseInt(document.getElementById('ht-stars').value),
        description: document.getElementById('ht-desc').value,
        motivation: document.getElementById('ht-motivation').value,
        sort_order: parseInt(document.getElementById('ht-order').value),
    };
    try {
        if (id) {
            await apiCall(`/api/admin/habits/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
        } else {
            await apiCall(`/api/admin/profiles/${slug}/habits`, { method: 'POST', body: JSON.stringify(data) });
        }
        closeModal('habit-modal');
        loadHabits();
    } catch (e) { alert('Error: ' + e.message); }
}

async function deleteHabit(id) {
    if (!confirm('¿Desactivar este hábito?')) return;
    try {
        await apiCall(`/api/admin/habits/${id}`, { method: 'DELETE' });
        loadHabits();
    } catch (e) { alert('Error: ' + e.message); }
}

// ── MICRO-HABITS ──────────────────────────────

function addMicroHabit(habitId) {
    document.getElementById('mh-id').value = '';
    document.getElementById('mh-habit-id').value = habitId;
    document.getElementById('mh-desc').value = '';
    document.getElementById('mh-order').value = '0';
    document.getElementById('micro-modal').classList.remove('hidden');
}

function editMicro(id, desc, order, habitId) {
    document.getElementById('mh-id').value = id;
    document.getElementById('mh-habit-id').value = habitId;
    document.getElementById('mh-desc').value = desc;
    document.getElementById('mh-order').value = order;
    document.getElementById('micro-modal').classList.remove('hidden');
}

async function saveMicro(e) {
    e.preventDefault();
    const id = document.getElementById('mh-id').value;
    const habitId = document.getElementById('mh-habit-id').value;
    const data = {
        description: document.getElementById('mh-desc').value,
        sort_order: parseInt(document.getElementById('mh-order').value),
    };
    try {
        if (id) {
            await apiCall(`/api/admin/micro-habits/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
        } else {
            await apiCall(`/api/admin/habits/${habitId}/micro-habits`, { method: 'POST', body: JSON.stringify(data) });
        }
        closeModal('micro-modal');
        loadHabits();
    } catch (e) { alert('Error: ' + e.message); }
}

async function deleteMicro(id) {
    if (!confirm('¿Eliminar este micro-hábito?')) return;
    try {
        await apiCall(`/api/admin/micro-habits/${id}`, { method: 'DELETE' });
        loadHabits();
    } catch (e) { alert('Error: ' + e.message); }
}

// ── REWARD TIERS ──────────────────────────────

async function loadRewardTiers() {
    const slug = document.getElementById('reward-profile-select').value;
    if (!slug) return;
    try {
        const tiers = await apiCall(`/api/admin/profiles/${slug}/reward-tiers?tier_type=weekly`);
        const list = document.getElementById('reward-tiers-list');
        list.innerHTML = tiers.length ? tiers.map((t, i) => tierRow(t, i)).join('') :
            '<p class="empty-msg">No hay niveles configurados.</p>';
    } catch (e) { console.error(e); }
}

function tierRow(t, i) {
    return `
    <div class="tier-row" data-idx="${i}">
        <input type="number" class="tier-pct" value="${t.min_pct}" step="0.05" min="0" max="1" placeholder="Min %" />
        <input type="number" class="tier-mult" value="${t.multiplier}" step="0.5" min="0" placeholder="×Mult" />
        <input type="text" class="tier-label" value="${t.label}" placeholder="Label" />
        <input type="text" class="tier-emoji" value="${t.emoji}" maxlength="4" placeholder="Emoji" />
        <button class="btn-xs danger" onclick="this.parentElement.remove()">✕</button>
    </div>`;
}

function addTierRow() {
    const list = document.getElementById('reward-tiers-list');
    const idx = list.children.length;
    const div = document.createElement('div');
    div.innerHTML = tierRow({ min_pct: 0, multiplier: 1, label: '', emoji: '' }, idx);
    list.appendChild(div.firstElementChild);
}

async function saveTiers() {
    const slug = document.getElementById('reward-profile-select').value;
    const rows = document.querySelectorAll('.tier-row');
    const tiers = Array.from(rows).map((r, i) => ({
        tier_type: 'weekly',
        min_pct: parseFloat(r.querySelector('.tier-pct').value),
        multiplier: parseFloat(r.querySelector('.tier-mult').value),
        label: r.querySelector('.tier-label').value,
        emoji: r.querySelector('.tier-emoji').value,
        sort_order: i,
    }));
    try {
        await apiCall(`/api/admin/profiles/${slug}/reward-tiers`, {
            method: 'PUT', body: JSON.stringify(tiers)
        });
        alert('✅ Niveles guardados');
        loadRewardTiers();
    } catch (e) { alert('Error: ' + e.message); }
}

// ── SETTINGS ──────────────────────────────────

async function loadSettings() {
    try {
        const s = await apiCall('/api/admin/settings');
        document.getElementById('set-currency').value = s.currency_symbol;
        document.getElementById('set-app-name').value = s.app_name;
        document.getElementById('set-streak-days').value = s.streak_bonus_days;
        document.getElementById('set-streak-pct').value = s.streak_bonus_pct;
    } catch (e) { console.error(e); }
}

async function saveSettings(e) {
    e.preventDefault();
    const data = {
        currency_symbol: document.getElementById('set-currency').value,
        app_name: document.getElementById('set-app-name').value,
        streak_bonus_days: parseInt(document.getElementById('set-streak-days').value),
        streak_bonus_pct: parseFloat(document.getElementById('set-streak-pct').value),
    };
    const pin = document.getElementById('set-admin-pin').value;
    if (pin) data.admin_pin = pin;
    try {
        await apiCall('/api/admin/settings', { method: 'PUT', body: JSON.stringify(data) });
        alert('✅ Configuración guardada');
        if (pin) {
            adminPin = pin;
            localStorage.setItem('admin_pin', pin);
        }
    } catch (e) { alert('Error: ' + e.message); }
}

// ── DATA ──────────────────────────────────────

async function loadLogs() {
    const slug = document.getElementById('data-profile-select').value;
    if (!slug) return;
    try {
        const logs = await apiCall(`/api/admin/profiles/${slug}/logs`);
        const list = document.getElementById('logs-list');
        if (!logs.length) { list.innerHTML = '<p class="empty-msg">Sin registros.</p>'; return; }
        list.innerHTML = `<table class="data-table"><thead><tr><th>Fecha</th><th>Done</th><th>Total</th><th>%</th><th>✅</th><th></th></tr></thead><tbody>
        ${logs.map(l => `<tr>
            <td>${l.date}</td><td>${l.completed_count}</td><td>${l.total}</td>
            <td>${Math.round(l.pct * 100)}%</td><td>${l.day_done ? '✅' : '—'}</td>
            <td><button class="btn-xs danger" onclick="deleteLog('${slug}', '${l.date}')">🗑️</button></td>
        </tr>`).join('')}
        </tbody></table>`;
    } catch (e) { console.error(e); }

    // Export link
    document.getElementById('export-csv-link').href = `${API}/api/admin/export/csv`;
}

async function deleteLog(slug, dateStr) {
    if (!confirm(`¿Eliminar registro ${dateStr}?`)) return;
    try {
        await apiCall(`/api/admin/profiles/${slug}/logs/${dateStr}`, { method: 'DELETE' });
        loadLogs();
    } catch (e) { alert('Error: ' + e.message); }
}

async function loadHealth() {
    try {
        const h = await apiCall('/api/admin/health');
        document.getElementById('health-info').innerHTML = `
        <div class="health-item"><span>Estado</span><strong>${h.status === 'ok' ? '🟢 Online' : '🔴 Error'}</strong></div>
        <div class="health-item"><span>Motor DB</span><strong>${h.db_engine}</strong></div>
        <div class="health-item"><span>Perfiles</span><strong>${h.profiles}</strong></div>
        <div class="health-item"><span>Registros</span><strong>${h.total_day_logs}</strong></div>
        `;
    } catch (e) { console.error(e); }
}

async function resetAllData() {
    if (!confirm('⚠️ ¿BORRAR TODOS los datos? Esta acción no se puede deshacer.')) return;
    if (!confirm('¿Estás realmente seguro?')) return;
    try {
        await apiCall('/api/admin/reset-all-data', { method: 'POST' });
        alert('✅ Todos los datos han sido borrados');
        loadLogs();
        loadHealth();
    } catch (e) { alert('Error: ' + e.message); }
}

// ── Modal helper ──────────────────────────────

function closeModal(id) {
    document.getElementById(id).classList.add('hidden');
}
