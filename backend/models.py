"""
HábitosFam – backend/models.py  (v3)
SQLAlchemy ORM models.

v3 additions:
  - PIN auth per profile + admin
  - HabitTemplate & MicroHabit (DB-driven habits)
  - RewardTier (configurable thresholds)
  - AppSettings (global config singleton)
  - Profile: reward amounts, monthly config, currency
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base

# ── Global settings (singleton row id=1) ──────────────────────

class AppSettings(Base):
    """Global application configuration (single row)."""
    __tablename__ = "app_settings"

    id               = Column(Integer, primary_key=True, default=1)
    admin_pin_hash   = Column(String(128), nullable=False)
    currency_symbol  = Column(String(10), default="$")
    app_name         = Column(String(100), default="HábitosFam")
    streak_bonus_days = Column(Integer, default=7)
    streak_bonus_pct = Column(Float, default=1.5)  # 1.5 = +50%
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Profile ───────────────────────────────────────────────────

class Profile(Base):
    """Family member profile with PIN auth and reward config."""
    __tablename__ = "profiles"

    id                = Column(Integer, primary_key=True, index=True)
    slug              = Column(String(50), unique=True, nullable=False, index=True)
    name              = Column(String(100), nullable=False)
    age               = Column(Integer, nullable=False)
    avatar            = Column(String(10), default="⭐")
    theme             = Column(String(50), default="default")
    level_idx         = Column(Integer, default=0)
    is_active         = Column(Boolean, default=True)

    # Auth
    pin_hash          = Column(String(128), nullable=True)  # hashed user PIN

    # Reward config (per-profile)
    weekly_reward_base = Column(Float, default=2.0)
    weekly_reward_full = Column(Float, default=4.0)
    monthly_reward_desc = Column(String(255), default="Actividad especial 🎪")
    monthly_min_pct   = Column(Float, default=0.75)  # 75% to unlock monthly

    created_at        = Column(DateTime, default=datetime.utcnow)
    updated_at        = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    day_logs        = relationship("DayLog", back_populates="profile", cascade="all, delete-orphan")
    rewards         = relationship("WeekReward", back_populates="profile", cascade="all, delete-orphan")
    month_rewards   = relationship("MonthReward", back_populates="profile", cascade="all, delete-orphan")
    habit_templates = relationship("HabitTemplate", back_populates="profile", cascade="all, delete-orphan")
    reward_tiers    = relationship("RewardTier", back_populates="profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Profile({self.slug}, {self.name}, {self.age}y)>"


# ── Habit Templates (DB-driven habit definitions) ─────────────

class HabitTemplate(Base):
    """Defines a habit assigned to a profile. Admin-configurable."""
    __tablename__ = "habit_templates"
    __table_args__ = (
        UniqueConstraint("profile_id", "habit_key", name="uq_profile_habit_key"),
    )

    id          = Column(Integer, primary_key=True, index=True)
    profile_id  = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    habit_key   = Column(String(50), nullable=False)    # 'sport', 'study', etc.
    name        = Column(String(150), nullable=False)
    icon        = Column(String(10), default="⭐")
    category    = Column(String(50), default="general")
    stars       = Column(Integer, default=1)
    description = Column(String(255), default="")
    details     = Column(Text, default="")
    motivation  = Column(String(255), default="")
    sort_order  = Column(Integer, default=0)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    # Relationships
    profile      = relationship("Profile", back_populates="habit_templates")
    micro_habits = relationship("MicroHabit", back_populates="habit_template",
                                cascade="all, delete-orphan", order_by="MicroHabit.sort_order")

    def __repr__(self):
        return f"<HabitTemplate({self.habit_key}, {self.name})>"


class MicroHabit(Base):
    """Individual micro-task within a habit template."""
    __tablename__ = "micro_habits"

    id                = Column(Integer, primary_key=True, index=True)
    habit_template_id = Column(Integer, ForeignKey("habit_templates.id", ondelete="CASCADE"), nullable=False)
    description       = Column(String(255), nullable=False)
    sort_order        = Column(Integer, default=0)
    is_active         = Column(Boolean, default=True)
    created_at        = Column(DateTime, default=datetime.utcnow)

    # Relationships
    habit_template = relationship("HabitTemplate", back_populates="micro_habits")

    def __repr__(self):
        return f"<MicroHabit({self.description[:30]})>"


# ── Reward Tiers (configurable per-profile) ───────────────────

class RewardTier(Base):
    """Configurable reward threshold per profile."""
    __tablename__ = "reward_tiers"

    id          = Column(Integer, primary_key=True, index=True)
    profile_id  = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    tier_type   = Column(String(20), default="weekly")  # 'weekly' or 'monthly'
    min_pct     = Column(Float, nullable=False)
    multiplier  = Column(Float, nullable=False)
    label       = Column(String(100), default="")
    emoji       = Column(String(10), default="")
    sort_order  = Column(Integer, default=0)

    # Relationships
    profile = relationship("Profile", back_populates="reward_tiers")

    def __repr__(self):
        return f"<RewardTier({self.min_pct}→×{self.multiplier})>"


# ── Daily Tracking ────────────────────────────────────────────

class DayLog(Base):
    """Daily habit completion log for a profile."""
    __tablename__ = "day_logs"
    __table_args__ = (
        UniqueConstraint("profile_id", "date", name="uq_profile_date"),
    )

    id              = Column(Integer, primary_key=True, index=True)
    profile_id      = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    date            = Column(String(10), nullable=False, index=True)
    completed_count = Column(Integer, default=0)
    total           = Column(Integer, default=6)
    pct             = Column(Float, default=0.0)
    day_done        = Column(Boolean, default=False)
    bonus_star      = Column(Boolean, default=False)
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile       = relationship("Profile", back_populates="day_logs")
    habit_entries = relationship("HabitEntry", back_populates="day_log", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DayLog({self.date}, {self.completed_count}/{self.total})>"


class HabitEntry(Base):
    """Individual habit state within a DayLog."""
    __tablename__ = "habit_entries"
    __table_args__ = (
        UniqueConstraint("day_log_id", "habit_id", name="uq_daylog_habit"),
    )

    id             = Column(Integer, primary_key=True, index=True)
    day_log_id     = Column(Integer, ForeignKey("day_logs.id", ondelete="CASCADE"), nullable=False)
    habit_id       = Column(String(50), nullable=False)
    done           = Column(Boolean, default=False)
    mini_tasks_json = Column(Text, default="{}")
    toggled_at     = Column(DateTime, nullable=True)

    day_log = relationship("DayLog", back_populates="habit_entries")

    def __repr__(self):
        return f"<HabitEntry({self.habit_id}, done={self.done})>"


# ── Rewards ───────────────────────────────────────────────────

class WeekReward(Base):
    """Weekly reward summary for a profile."""
    __tablename__ = "week_rewards"
    __table_args__ = (
        UniqueConstraint("profile_id", "week_start", name="uq_profile_week"),
    )

    id              = Column(Integer, primary_key=True, index=True)
    profile_id      = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    week_start      = Column(String(10), nullable=False)
    week_end        = Column(String(10), nullable=False)
    days_completed  = Column(Integer, default=0)
    total_pct       = Column(Float, default=0.0)
    streak_at_close = Column(Integer, default=0)
    shield_used     = Column(Boolean, default=False)
    earned_amount   = Column(Float, default=0.0)
    reward_paid     = Column(Boolean, default=False)
    notes           = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    profile = relationship("Profile", back_populates="rewards")

    def __repr__(self):
        return f"<WeekReward({self.week_start}, ${self.earned_amount:.2f})>"


class MonthReward(Base):
    """Monthly reward summary for a profile."""
    __tablename__ = "month_rewards"
    __table_args__ = (
        UniqueConstraint("profile_id", "month_key", name="uq_profile_month"),
    )

    id              = Column(Integer, primary_key=True, index=True)
    profile_id      = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    month_key       = Column(String(7), nullable=False)
    days_completed  = Column(Integer, default=0)
    total_days      = Column(Integer, default=0)
    pct             = Column(Float, default=0.0)
    reward_unlocked = Column(Boolean, default=False)
    reward_paid     = Column(Boolean, default=False)
    reward_desc     = Column(String(255), nullable=True)
    notes           = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    profile = relationship("Profile", back_populates="month_rewards")

    def __repr__(self):
        return f"<MonthReward({self.month_key}, {self.pct*100:.0f}%)>"
