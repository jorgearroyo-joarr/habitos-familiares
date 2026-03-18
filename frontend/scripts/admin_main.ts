/**
 * HábitosFam – frontend/scripts/admin_main.ts
 * Glue code to expose admin.ts to HTML handlers and boot the admin panel.
 */

import * as Admin from './admin.ts';

// Expose to window for legacy onclick handlers in admin.html
(window as any).login = Admin.login;
(window as any).logout = Admin.logout;
(window as any).showSection = Admin.showSection;
(window as any).showAddProfile = Admin.showAddProfile;
(window as any).editProfile = Admin.editProfile;
(window as any).saveProfile = Admin.saveProfile;
(window as any).deactivateProfile = Admin.deactivateProfile;
(window as any).loadHabits = Admin.loadHabits;
(window as any).showAddHabit = Admin.showAddHabit;
(window as any).editHabit = Admin.editHabit;
(window as any).saveHabit = Admin.saveHabit;
(window as any).deleteHabit = Admin.deleteHabit;
(window as any).addMicroHabit = Admin.addMicroHabit;
(window as any).editMicro = Admin.editMicro;
(window as any).saveMicro = Admin.saveMicro;
(window as any).deleteMicro = Admin.deleteMicro;
(window as any).loadRewardTiers = Admin.loadRewardTiers;
(window as any).addTierRow = Admin.addTierRow;
(window as any).saveTiers = Admin.saveTiers;
(window as any).loadSettings = Admin.loadSettings;
(window as any).saveSettings = Admin.saveSettings;
(window as any).loadLogs = Admin.loadLogs;
(window as any).deleteLog = Admin.deleteLog;
(window as any).resetAllData = Admin.resetAllData;
(window as any).closeModalWindow = Admin.closeModalWindow;
(window as any).bulkCloseWeek = Admin.bulkCloseWeek;

// Initialize when DOM ready
document.addEventListener('DOMContentLoaded', () => {
    Admin.initAdmin();
});
