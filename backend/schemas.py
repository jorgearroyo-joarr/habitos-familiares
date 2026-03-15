"""
HábitosFam – backend/schemas.py  (v3)
Pydantic v2 schemas for request/response validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, List
from datetime import datetime


# ── Auth schemas ──────────────────────────────────────────────


class PinLoginIn(BaseModel):
    pin: str = Field(..., min_length=4, max_length=8)


class PinLoginOut(BaseModel):
    success: bool
    role: str  # 'admin' | 'user'
    profile_slug: Optional[str] = None
    token: str


# ── AppSettings schemas ──────────────────────────────────────


class AppSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    currency_symbol: str
    app_name: str
    streak_bonus_days: int
    streak_bonus_pct: float


class AppSettingsUpdate(BaseModel):
    admin_pin: Optional[str] = None  # raw PIN, will be hashed
    currency_symbol: Optional[str] = None
    app_name: Optional[str] = None
    streak_bonus_days: Optional[int] = None
    streak_bonus_pct: Optional[float] = None


# ── Profile schemas ──────────────────────────────────────────


class ProfileBase(BaseModel):
    slug: str
    name: str
    age: int
    avatar: str = "⭐"
    theme: str = "default"


class ProfileCreate(ProfileBase):
    pin: Optional[str] = None  # raw PIN
    weekly_reward_base: float = 2.0
    weekly_reward_full: float = 4.0
    monthly_reward_desc: str = "Actividad especial 🎪"
    monthly_min_pct: float = 0.75


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    avatar: Optional[str] = None
    theme: Optional[str] = None
    level_idx: Optional[int] = None
    is_active: Optional[bool] = None
    pin: Optional[str] = None  # raw PIN
    weekly_reward_base: Optional[float] = None
    weekly_reward_full: Optional[float] = None
    monthly_reward_desc: Optional[str] = None
    monthly_min_pct: Optional[float] = None


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
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


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
    micro_habits: List[MicroHabitOut] = []


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
    micro_habits: List[MicroHabitCreate] = []


class HabitTemplateUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    stars: Optional[int] = None
    description: Optional[str] = None
    details: Optional[str] = None
    motivation: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


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
    min_pct: Optional[float] = None
    multiplier: Optional[float] = None
    label: Optional[str] = None
    emoji: Optional[str] = None
    sort_order: Optional[int] = None


# ── HabitEntry schemas ───────────────────────────────────────


class HabitEntryIn(BaseModel):
    habit_id: str
    done: bool
    mini_tasks: Dict[str, bool] = Field(default_factory=dict)


class HabitEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    habit_id: str
    done: bool
    mini_tasks_json: str


# ── DayLog schemas ───────────────────────────────────────────


class DayLogIn(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    habits: List[HabitEntryIn] = Field(default_factory=list)


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
    habit_entries: List[HabitEntryOut] = []
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
    day_logs: List[DayLogOut] = []


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
    notes: Optional[str]
    created_at: datetime


class RewardMarkPaid(BaseModel):
    notes: Optional[str] = None


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
    habits: List[HabitDashboardItem] = []


# ── Charts / Analytics ─────────────────────────────────────────


class TrendDataPoint(BaseModel):
    date: str
    completed: int
    total: int
    pct: float


class TrendResponse(BaseModel):
    profile_slug: str
    period: str  # 'weekly' | 'monthly' | 'yearly'
    data: List[TrendDataPoint]
    average_pct: float
    best_day: Optional[str] = None
    improvement: Optional[float] = None  # pct change vs previous period


# ── Habit Templates (Predefined) ───────────────────────────────


class HabitTemplateCategory(BaseModel):
    category: str
    description: str
    age_range: str
    habits: List[HabitTemplateCreate] = []


class HabitTemplatesCatalog(BaseModel):
    categories: List[HabitTemplateCategory]


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
