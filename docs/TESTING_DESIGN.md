# Testing Design — HábitosFam

## 🧪 Unit Tests (Logic & CRUD)
*Implemented in `backend/tests/test_unit.py`*

| Test ID | Description | Component |
|---------|-------------|-----------|
| UT-1 | Verify PIN hashing and salting. | `crud.py` |
| UT-2 | Calculate weekly stars correctly (including bonus). | `crud.py` |
| UT-3 | Prevent out-of-range star counts. | `models.py` |
| UT-4 | Ensure profile slug uniqueness. | `models.py` |

## 🚦 Functional Tests (API Flows)
*Implemented in `backend/tests/test_functional.py`*

| Test ID | Description | Flow |
|---------|-------------|------|
| FT-1 | Login -> Fetch Profile -> Check Habit -> Verify Log is updated. | Full User Flow |
| FT-2 | Admin Login -> Change Settings -> Verify GET `/api/settings` change. | Config Flow |
| FT-3 | Zero-Privilege: Try to access Alana's logs with Sofia's PIN (should fail). | Security |

## 👥 User Acceptance Tests (Manual/Browser)
*To be executed via `walkthrough.md` sessions*

| Test ID | Scenario | Expected Result |
|---------|----------|-----------------|
| UAT-1 | Check all micro-habits on a profile. | Confetti celebration and "Perfect Day" message. |
| UAT-2 | Resize window to mobile view. | Dashboard remains usable and responsive. |
| UAT-3 | Change currency from $ to ₡ in Admin. | User dashboard updates immediately. |
