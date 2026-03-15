/**
 * HábitosFam – frontend/scripts/index_main.ts
 * Glue code to expose app.ts to HTML handlers and boot the app.
 */

import * as App from './app.ts';

// Expose to window for legacy onclick handlers in index.html
(window as any).toggleTheme = App.toggleTheme;
(window as any).logout = App.logout;
(window as any).submitLogin = App.submitLogin;
(window as any).switchProfile = App.switchProfile;
(window as any).completeDay = App.completeDay;
(window as any).showTrendsTab = App.showTrendsTab;
(window as any).setTrendPeriod = App.setTrendPeriod;
(window as any).closeModal = App.closeModal;
(window as any).toggleHabit = App.toggleHabit;
(window as any).toggleMiniTask = App.toggleMiniTask;
(window as any).toggleExpand = App.toggleExpand;
(window as any).launchConfetti = App.launchConfetti;

// Initialize when DOM ready
document.addEventListener('DOMContentLoaded', () => {
    App.setupPinInputs();
    App.init();
});
