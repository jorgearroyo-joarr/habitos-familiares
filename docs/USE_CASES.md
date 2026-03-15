# Use Cases — HábitosFam

## UC-1: User Profile Access
**Actor**: Child (User)
1. User opens the application.
2. User selects their profile from the home screen.
3. User enters their unique 4-digit PIN.
4. **Result**: System grants access to the user-specific dashboard.

## UC-2: Micro-Habit Tracking
**Actor**: Child (User)
1. User expands a habit card to view sub-tasks.
2. User checks a micro-habit sub-task.
3. System provides visual feedback (sparkles).
4. **Result**: Progress bar updates. If all sub-tasks are done, the main habit is marked as complete with confetti.

## UC-3: Admin Configuration
**Actor**: Parent (Admin)
1. Parent navigates to `/admin`.
2. Parent enters the Admin PIN.
3. Parent modifies a profile's reward tiers or habit icons.
4. **Result**: Changes are persisted to the database and reflect immediately in the User App.

## UC-4: Weekly/Monthly Closing
**Actor**: Parent (Admin)
1. Parent reviews the week/month statistics in the Admin Panel.
2. Parent clicks "Close Month".
3. System calculates the final percentage and unlocks rewards if thresholds are met.
4. **Result**: A permanent record of the reward is created.
