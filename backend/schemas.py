"""
HábitosFam – backend/schemas.py  (v3)
Pydantic v2 schemas for request/response validation.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# ── Auth schemas ──────────────────────────────────────────────


class PinLoginIn(BaseModel):
    pin: str = Field(..., min_length=4, max_length=8)


class PinLoginOut(BaseModel):
    success: bool
    role: str  # 'admin' | 'user'
    profile_slug: str | None = None
    token: str


# ── AppSettings schemas ──────────────────────────────────────


class AppSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    currency_symbol: str
    app_name: str
    streak_bonus_days: int
    streak_bonus_pct: float


class AppSettingsUpdate(BaseModel):
    admin_pin: str | None = None  # raw PIN, will be hashed
    currency_symbol: str | None = None
    app_name: str | None = None
    streak_bonus_days: int | None = None
    streak_bonus_pct: float | None = None


# ── Profile schemas ──────────────────────────────────────────


class ProfileBase(BaseModel):
    slug: str
    name: str
    age: int
    avatar: str = "⭐"
    theme: str = "default"


class ProfileCreate(ProfileBase):
    pin: str | None = None  # raw PIN
    weekly_reward_base: float = 2.0
    weekly_reward_full: float = 4.0
    monthly_reward_desc: str = "Actividad especial 🎪"
    monthly_min_pct: float = 0.75


class ProfileUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    avatar: str | None = None
    theme: str | None = None
    level_idx: int | None = None
    is_active: bool | None = None
    pin: str | None = None  # raw PIN
    weekly_reward_base: float | None = None
    weekly_reward_full: float | None = None
    monthly_reward_desc: str | None = None
    monthly_min_pct: float | None = None


class ProfileOut(ProfileBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    level_idx: int
    is_active: bool
    weekly_reward_base: float
    weekly_reward_full: float
    monthly_reward_desc: str
    monthly_min_pct: float
    has_pin: bool = False
    created_at: datetime


# ── HabitTemplate schemas ────────────────────────────────────


class MicroHabitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    description: str
    sort_order: int
    is_active: bool


class MicroHabitCreate(BaseModel):
    description: str
    sort_order: int = 0


class MicroHabitUpdate(BaseModel):
    description: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class HabitTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    habit_key: str
    name: str
    icon: str
    category: str
    stars: int
    description: str
    details: str
    motivation: str
    sort_order: int
    is_active: bool
    consecutive_days: int = 0
    is_mastered: bool = False
    mastered_at: str | None = None
    micro_habits: list[MicroHabitOut] = []


class HabitTemplateCreate(BaseModel):
    habit_key: str
    name: str
    icon: str = "⭐"
    category: str = "general"
    stars: int = 1
    description: str = ""
    details: str = ""
    motivation: str = ""
    sort_order: int = 0
    micro_habits: list[MicroHabitCreate] = []


class HabitTemplateUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None
    category: str | None = None
    stars: int | None = None
    description: str | None = None
    details: str | None = None
    motivation: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


# ── RewardTier schemas ───────────────────────────────────────


class RewardTierOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tier_type: str
    min_pct: float
    multiplier: float
    label: str
    emoji: str
    sort_order: int


class RewardTierCreate(BaseModel):
    tier_type: str = "weekly"  # 'weekly' or 'monthly'
    min_pct: float
    multiplier: float
    label: str = ""
    emoji: str = ""
    sort_order: int = 0


class RewardTierUpdate(BaseModel):
    min_pct: float | None = None
    multiplier: float | None = None
    label: str | None = None
    emoji: str | None = None
    sort_order: int | None = None


# ── HabitEntry schemas ───────────────────────────────────────


class HabitEntryIn(BaseModel):
    habit_id: str
    done: bool
    mini_tasks: dict[str, bool] = Field(default_factory=dict)


class HabitEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    habit_id: str
    done: bool
    mini_tasks_json: str


# ── DayLog schemas ───────────────────────────────────────────


class DayLogIn(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    habits: list[HabitEntryIn] = Field(default_factory=list)


class DayCompleteIn(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    completed_count: int
    total: int
    pct: float


class DayLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    profile_id: int
    date: str
    completed_count: int
    total: int
    pct: float
    day_done: bool
    bonus_star: bool
    habit_entries: list[HabitEntryOut] = []
    created_at: datetime


# ── Week/Month stats ─────────────────────────────────────────


class WeekStatsOut(BaseModel):
    profile_slug: str
    week_start: str
    week_end: str
    days_completed: int
    total_stars: int
    pct: float
    streak: int
    earned_amount: float
    currency: str = "$"
    day_logs: list[DayLogOut] = []


class MonthStatsOut(BaseModel):
    profile_slug: str
    month_key: str
    days_completed: int
    total_days: int
    pct: float
    reward_unlocked: bool
    reward_desc: str = ""
    currency: str = "$"


# ── Reward schemas ───────────────────────────────────────────


class WeekRewardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    profile_id: int
    week_start: str
    week_end: str
    days_completed: int
    total_pct: float
    earned_amount: float
    reward_paid: bool
    notes: str | None
    created_at: datetime


class RewardMarkPaid(BaseModel):
    notes: str | None = None


# ── Health / Admin ───────────────────────────────────────────


class HealthOut(BaseModel):
    status: str
    db_engine: str
    db_url_masked: str
    profiles: int
    total_day_logs: int


class ExportRow(BaseModel):
    profile: str
    date: str
    completed: int
    total: int
    pct: float
    day_done: bool


# ── Dashboard ────────────────────────────────────────────────


class HabitDashboardItem(BaseModel):
    habit_key: str
    habit_name: str
    total_days: int
    completed_days: int
    pct: float
    current_streak: int


class ProfileDashboardOut(BaseModel):
    profile_slug: str
    profile_name: str
    overall_pct: float
    total_active_days: int
    habits: list[HabitDashboardItem] = []


# ── Charts / Analytics ─────────────────────────────────────────


class TrendDataPoint(BaseModel):
    date: str
    completed: int
    total: int
    pct: float


class TrendResponse(BaseModel):
    profile_slug: str
    period: str  # 'weekly' | 'monthly' | 'yearly'
    data: list[TrendDataPoint]
    average_pct: float
    best_day: str | None = None
    improvement: float | None = None  # pct change vs previous period


# ── Habit Templates (Predefined) ───────────────────────────────


class HabitTemplateCategory(BaseModel):
    category: str
    description: str
    age_range: str
    habits: list[HabitTemplateCreate] = []


class HabitTemplatesCatalog(BaseModel):
    categories: list[HabitTemplateCategory]


# ── Month Auto-Close ───────────────────────────────────────────


class MonthCloseResult(BaseModel):
    profile_slug: str
    month_key: str
    days_completed: int
    total_days: int
    pct: float
    reward_unlocked: bool
    reward_amount: float
    reward_desc: str
    already_closed: bool = False
