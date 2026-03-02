"""
HábitosFam – backend/crud.py  (v3)
Database CRUD operations.
All DB access goes through this module.
"""
import json
import hashlib
from datetime import datetime, date, timedelta
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import func

from . import models, schemas
from .config import settings
from .data_config import (
    _hash_pin, DEFAULT_ADMIN_PIN,
    PROFILE_TEMPLATES, HABIT_TEMPLATES, DEFAULT_WEEKLY_TIERS,
)


# ── PIN Auth ──────────────────────────────────────────────────

def verify_pin(db: Session, pin: str) -> dict:
    """
    Verify a PIN. Returns:
      {'role': 'admin', 'profile_slug': None}   if admin PIN
      {'role': 'user',  'profile_slug': 'alana'} if user PIN
      None if invalid
    """
    pin_hash = _hash_pin(pin)

    # Check admin PIN first
    app_cfg = db.query(models.AppSettings).filter(models.AppSettings.id == 1).first()
    if app_cfg and app_cfg.admin_pin_hash == pin_hash:
        return {"role": "admin", "profile_slug": None}

    # Check user PINs
    profile = db.query(models.Profile).filter(
        models.Profile.pin_hash == pin_hash,
        models.Profile.is_active == True,
    ).first()
    if profile:
        return {"role": "user", "profile_slug": profile.slug}

    return None


def generate_token(pin: str) -> str:
    return hashlib.sha256(f"{pin}{settings.secret_key}".encode()).hexdigest()[:32]


# ── AppSettings ───────────────────────────────────────────────

def get_app_settings(db: Session) -> models.AppSettings:
    return db.query(models.AppSettings).filter(models.AppSettings.id == 1).first()


def update_app_settings(db: Session, data: schemas.AppSettingsUpdate) -> models.AppSettings:
    cfg = get_app_settings(db)
    if not cfg:
        return None
    if data.admin_pin is not None:
        cfg.admin_pin_hash = _hash_pin(data.admin_pin)
    if data.currency_symbol is not None:
        cfg.currency_symbol = data.currency_symbol
    if data.app_name is not None:
        cfg.app_name = data.app_name
    if data.streak_bonus_days is not None:
        cfg.streak_bonus_days = data.streak_bonus_days
    if data.streak_bonus_pct is not None:
        cfg.streak_bonus_pct = data.streak_bonus_pct
    db.commit()
    db.refresh(cfg)
    return cfg


# ── Profiles ──────────────────────────────────────────────────

def get_profiles(db: Session):
    return db.query(models.Profile).filter(models.Profile.is_active == True).all()

def get_all_profiles(db: Session):
    return db.query(models.Profile).all()

def get_profile_by_slug(db: Session, slug: str):
    return db.query(models.Profile).filter(models.Profile.slug == slug).first()

def get_profile_by_id(db: Session, profile_id: int):
    return db.query(models.Profile).filter(models.Profile.id == profile_id).first()

def create_profile(db: Session, data: schemas.ProfileCreate):
    profile = models.Profile(
        slug=data.slug, name=data.name, age=data.age,
        avatar=data.avatar, theme=data.theme,
        weekly_reward_base=data.weekly_reward_base,
        weekly_reward_full=data.weekly_reward_full,
        monthly_reward_desc=data.monthly_reward_desc,
        monthly_min_pct=data.monthly_min_pct,
        pin_hash=_hash_pin(data.pin) if data.pin else None,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def update_profile(db: Session, profile: models.Profile, data: schemas.ProfileUpdate):
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "pin":
            if value is not None:
                profile.pin_hash = _hash_pin(value)
        else:
            setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile

def delete_profile(db: Session, profile: models.Profile):
    profile.is_active = False
    db.commit()


# ── HabitTemplate CRUD ───────────────────────────────────────

def get_habit_templates(db: Session, profile_id: int, active_only: bool = True):
    q = db.query(models.HabitTemplate).filter(models.HabitTemplate.profile_id == profile_id)
    if active_only:
        q = q.filter(models.HabitTemplate.is_active == True)
    return q.order_by(models.HabitTemplate.sort_order).all()

def get_habit_template(db: Session, template_id: int):
    return db.query(models.HabitTemplate).filter(models.HabitTemplate.id == template_id).first()

def create_habit_template(db: Session, profile_id: int, data: schemas.HabitTemplateCreate):
    tpl = models.HabitTemplate(
        profile_id=profile_id,
        habit_key=data.habit_key, name=data.name, icon=data.icon,
        category=data.category, stars=data.stars,
        description=data.description, details=data.details,
        motivation=data.motivation, sort_order=data.sort_order,
    )
    db.add(tpl)
    db.flush()
    # Add micro-habits
    for i, mh in enumerate(data.micro_habits):
        db.add(models.MicroHabit(
            habit_template_id=tpl.id,
            description=mh.description,
            sort_order=mh.sort_order if mh.sort_order else i,
        ))
    db.commit()
    db.refresh(tpl)
    return tpl

def update_habit_template(db: Session, tpl: models.HabitTemplate, data: schemas.HabitTemplateUpdate):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tpl, field, value)
    db.commit()
    db.refresh(tpl)
    return tpl

def delete_habit_template(db: Session, tpl: models.HabitTemplate):
    tpl.is_active = False
    db.commit()


# ── MicroHabit CRUD ──────────────────────────────────────────

def get_micro_habits(db: Session, template_id: int, active_only: bool = True):
    q = db.query(models.MicroHabit).filter(models.MicroHabit.habit_template_id == template_id)
    if active_only:
        q = q.filter(models.MicroHabit.is_active == True)
    return q.order_by(models.MicroHabit.sort_order).all()

def create_micro_habit(db: Session, template_id: int, data: schemas.MicroHabitCreate):
    mh = models.MicroHabit(
        habit_template_id=template_id,
        description=data.description,
        sort_order=data.sort_order,
    )
    db.add(mh)
    db.commit()
    db.refresh(mh)
    return mh

def update_micro_habit(db: Session, mh: models.MicroHabit, data: schemas.MicroHabitUpdate):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(mh, field, value)
    db.commit()
    db.refresh(mh)
    return mh

def delete_micro_habit(db: Session, mh: models.MicroHabit):
    mh.is_active = False
    db.commit()


# ── RewardTier CRUD ──────────────────────────────────────────

def get_reward_tiers(db: Session, profile_id: int, tier_type: str = "weekly"):
    return db.query(models.RewardTier).filter(
        models.RewardTier.profile_id == profile_id,
        models.RewardTier.tier_type == tier_type,
    ).order_by(models.RewardTier.sort_order).all()

def upsert_reward_tiers(db: Session, profile_id: int, tiers: List[schemas.RewardTierCreate]):
    # Delete existing tiers for this type
    tier_type = tiers[0].tier_type if tiers else "weekly"
    db.query(models.RewardTier).filter(
        models.RewardTier.profile_id == profile_id,
        models.RewardTier.tier_type == tier_type,
    ).delete()
    # Insert new
    for t in tiers:
        db.add(models.RewardTier(
            profile_id=profile_id,
            tier_type=t.tier_type,
            min_pct=t.min_pct,
            multiplier=t.multiplier,
            label=t.label,
            emoji=t.emoji,
            sort_order=t.sort_order,
        ))
    db.commit()
    return get_reward_tiers(db, profile_id, tier_type)


# ── DayLog ────────────────────────────────────────────────────

def get_day_log(db: Session, profile_id: int, date_str: str):
    return db.query(models.DayLog).filter(
        models.DayLog.profile_id == profile_id,
        models.DayLog.date == date_str,
    ).first()

def upsert_day_log(db: Session, profile_id: int, date_str: str,
                   habits_data: List[schemas.HabitEntryIn]):
    log = get_day_log(db, profile_id, date_str)
    if not log:
        total = len(get_habit_templates(db, profile_id))
        log = models.DayLog(profile_id=profile_id, date=date_str, total=total or 6)
        db.add(log)
        db.flush()

    # Upsert each habit entry
    for h in habits_data:
        entry = db.query(models.HabitEntry).filter(
            models.HabitEntry.day_log_id == log.id,
            models.HabitEntry.habit_id == h.habit_id,
        ).first()

        mini_json = json.dumps(h.mini_tasks) if h.mini_tasks else "{}"

        if entry:
            entry.done = h.done
            entry.mini_tasks_json = mini_json
            entry.toggled_at = datetime.utcnow()
        else:
            entry = models.HabitEntry(
                day_log_id=log.id,
                habit_id=h.habit_id,
                done=h.done,
                mini_tasks_json=mini_json,
                toggled_at=datetime.utcnow(),
            )
            db.add(entry)

    # Recount
    entries = db.query(models.HabitEntry).filter(
        models.HabitEntry.day_log_id == log.id
    ).all()
    done_count = sum(1 for e in entries if e.done)
    total = log.total or len(entries)
    log.completed_count = done_count
    log.pct = done_count / total if total > 0 else 0
    log.bonus_star = (done_count == total and total > 0)

    db.commit()
    db.refresh(log)
    return log


def complete_day(db: Session, profile_id: int, date_str: str,
                 completed_count: int, total: int, pct: float):
    log = get_day_log(db, profile_id, date_str)
    if not log:
        log = models.DayLog(profile_id=profile_id, date=date_str, total=total)
        db.add(log)
        db.flush()

    log.completed_count = completed_count
    log.total = total
    log.pct = pct
    log.day_done = True
    log.bonus_star = (completed_count == total and total > 0)
    db.commit()
    db.refresh(log)
    return log


def get_day_logs_in_range(db: Session, profile_id: int, start: str, end: str):
    return db.query(models.DayLog).filter(
        models.DayLog.profile_id == profile_id,
        models.DayLog.date >= start,
        models.DayLog.date <= end,
    ).order_by(models.DayLog.date).all()


def get_all_day_logs(db: Session, profile_id: int):
    return db.query(models.DayLog).filter(
        models.DayLog.profile_id == profile_id
    ).order_by(models.DayLog.date.desc()).all()


# ── Streak computation ────────────────────────────────────────

def compute_streak(db: Session, profile_id: int) -> int:
    logs = db.query(models.DayLog).filter(
        models.DayLog.profile_id == profile_id,
        models.DayLog.pct >= 0.5,
    ).order_by(models.DayLog.date.desc()).all()

    if not logs:
        return 0

    streak = 0
    today_str = date.today().isoformat()
    check = date.today()
    log_dates = {l.date for l in logs}

    for i in range(365):
        key = check.isoformat()
        if key in log_dates:
            streak += 1
            check -= timedelta(days=1)
        elif i == 0:
            check -= timedelta(days=1)
        else:
            break

    return streak


# ── Week stats (uses DB reward tiers) ────────────────────────

def get_week_dates(reference: Optional[date] = None):
    ref = reference or date.today()
    monday = ref - timedelta(days=ref.weekday())
    dates = [(monday + timedelta(days=i)).isoformat() for i in range(7)]
    return dates[0], dates[6], dates


def compute_week_stats(db: Session, profile: models.Profile,
                        week_start: Optional[str] = None):
    if week_start:
        from datetime import date as d
        ref = d.fromisoformat(week_start)
    else:
        ref = None

    monday_str, sunday_str, week_dates = get_week_dates(ref)
    logs = get_day_logs_in_range(db, profile.id, monday_str, sunday_str)
    log_map = {l.date: l for l in logs}

    stars = 0
    completed_days = 0
    for d_str in week_dates:
        log = log_map.get(d_str)
        if log:
            stars += log.completed_count
            if log.bonus_star:
                stars += 1
            if log.pct >= 0.5:
                completed_days += 1

    total_possible = len(week_dates) * (profile.weekly_reward_full or 6)
    pct = stars / total_possible if total_possible > 0 else 0

    streak = compute_streak(db, profile.id)

    # Compute earned from DB tiers
    tiers = get_reward_tiers(db, profile.id, "weekly")
    earned = _compute_earned_from_tiers(
        tiers, pct, profile.weekly_reward_base,
        streak, db
    )

    # Currency
    cfg = get_app_settings(db)
    currency = cfg.currency_symbol if cfg else "$"

    return schemas.WeekStatsOut(
        profile_slug=profile.slug,
        week_start=monday_str,
        week_end=sunday_str,
        days_completed=completed_days,
        total_stars=stars,
        pct=pct,
        streak=streak,
        earned_amount=earned,
        currency=currency,
        day_logs=[schemas.DayLogOut.model_validate(l) for l in logs],
    )


def _compute_earned_from_tiers(tiers, pct, base_reward, streak, db):
    cfg = get_app_settings(db)
    streak_days = cfg.streak_bonus_days if cfg else 7
    streak_pct = cfg.streak_bonus_pct if cfg else 1.5

    streak_bonus = streak_pct if streak >= streak_days else 1.0

    for tier in sorted(tiers, key=lambda t: -t.min_pct):
        if pct >= tier.min_pct:
            return base_reward * tier.multiplier * streak_bonus
    return 0


# ── WeekReward ────────────────────────────────────────────────

def close_week(db: Session, profile: models.Profile, week_start: str):
    existing = db.query(models.WeekReward).filter(
        models.WeekReward.profile_id == profile.id,
        models.WeekReward.week_start == week_start,
    ).first()
    if existing:
        return existing

    stats = compute_week_stats(db, profile, week_start)
    reward = models.WeekReward(
        profile_id=profile.id,
        week_start=stats.week_start,
        week_end=stats.week_end,
        days_completed=stats.days_completed,
        total_pct=stats.pct,
        streak_at_close=stats.streak,
        earned_amount=stats.earned_amount,
    )
    db.add(reward)
    db.commit()
    db.refresh(reward)
    return reward


def mark_reward_paid(db: Session, reward: models.WeekReward, notes: Optional[str]):
    reward.reward_paid = True
    if notes:
        reward.notes = notes
    db.commit()
    db.refresh(reward)
    return reward


# ── Month stats ───────────────────────────────────────────────

def compute_month_stats(db: Session, profile: models.Profile,
                         month_key: Optional[str] = None):
    if not month_key:
        month_key = date.today().strftime("%Y-%m")

    year, month = map(int, month_key.split("-"))
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)

    today_date = date.today()
    end_date = min(last_day, today_date)

    logs = get_day_logs_in_range(db, profile.id, first_day.isoformat(), end_date.isoformat())
    completed = sum(1 for l in logs if l.pct >= 0.5)
    total = (end_date - first_day).days + 1

    pct = completed / total if total > 0 else 0

    cfg = get_app_settings(db)
    currency = cfg.currency_symbol if cfg else "$"

    return schemas.MonthStatsOut(
        profile_slug=profile.slug,
        month_key=month_key,
        days_completed=completed,
        total_days=total,
        pct=pct,
        reward_unlocked=(pct >= profile.monthly_min_pct),
        reward_desc=profile.monthly_reward_desc or "",
        currency=currency,
    )


# ── Dashboard ─────────────────────────────────────────────────

def get_profile_dashboard(db: Session, profile: models.Profile):
    templates = get_habit_templates(db, profile.id)
    all_logs = get_all_day_logs(db, profile.id)

    habit_stats = []
    for tpl in templates:
        total_days = 0
        completed_days = 0
        streak = 0
        current_streak = 0
        last_done = None

        for log in sorted(all_logs, key=lambda l: l.date, reverse=True):
            entry = next(
                (e for e in log.habit_entries if e.habit_id == tpl.habit_key),
                None
            )
            if entry:
                total_days += 1
                if entry.done:
                    completed_days += 1
                    if last_done is None or (last_done and
                        (date.fromisoformat(last_done) - date.fromisoformat(log.date)).days <= 1):
                        current_streak += 1
                    last_done = log.date
                else:
                    if last_done is None:
                        pass
                    else:
                        break  # streak broken

        habit_stats.append(schemas.HabitDashboardItem(
            habit_key=tpl.habit_key,
            habit_name=tpl.name,
            total_days=total_days,
            completed_days=completed_days,
            pct=completed_days / total_days if total_days > 0 else 0,
            current_streak=current_streak,
        ))

    overall_pct = sum(h.pct for h in habit_stats) / len(habit_stats) if habit_stats else 0

    return schemas.ProfileDashboardOut(
        profile_slug=profile.slug,
        profile_name=profile.name,
        overall_pct=overall_pct,
        total_active_days=len(all_logs),
        habits=habit_stats,
    )


# ── Health / Admin ────────────────────────────────────────────

def get_health(db: Session, db_url: str, db_engine_type: str):
    profiles = db.query(func.count(models.Profile.id)).scalar()
    logs = db.query(func.count(models.DayLog.id)).scalar()

    masked_url = db_url
    if "@" in db_url:
        parts = db_url.split("@")
        masked_url = parts[0].split("://")[0] + "://***@" + parts[1]

    return schemas.HealthOut(
        status="ok",
        db_engine=db_engine_type,
        db_url_masked=masked_url,
        profiles=profiles,
        total_day_logs=logs,
    )


def get_export_data(db: Session):
    logs = db.query(models.DayLog).join(models.Profile).order_by(
        models.Profile.slug, models.DayLog.date
    ).all()
    return [
        {
            "profile": log.profile.slug,
            "date": log.date,
            "completed": log.completed_count,
            "total": log.total,
            "pct": log.pct,
            "day_done": log.day_done,
        }
        for log in logs
    ]


# ── Seeding ───────────────────────────────────────────────────

def seed_default_data(db: Session):
    """Seed profiles, habits, micro-habits, reward tiers, and app settings."""
    # AppSettings
    cfg = db.query(models.AppSettings).filter(models.AppSettings.id == 1).first()
    if not cfg:
        cfg = models.AppSettings(
            id=1,
            admin_pin_hash=_hash_pin(DEFAULT_ADMIN_PIN),
            currency_symbol="$",
            app_name="HábitosFam",
        )
        db.add(cfg)
        db.flush()

    # Profiles
    for tpl in PROFILE_TEMPLATES:
        existing = db.query(models.Profile).filter(models.Profile.slug == tpl["slug"]).first()
        if existing:
            continue

        profile = models.Profile(
            slug=tpl["slug"],
            name=tpl["name"],
            age=tpl["age"],
            avatar=tpl["avatar"],
            theme=tpl["theme"],
            pin_hash=_hash_pin(tpl["pin"]) if tpl.get("pin") else None,
            weekly_reward_base=tpl["weekly_reward_base"],
            weekly_reward_full=tpl["weekly_reward_full"],
            monthly_reward_desc=tpl["monthly_reward_desc"],
            monthly_min_pct=tpl["monthly_min_pct"],
        )
        db.add(profile)
        db.flush()

        # Habit templates + micro-habits
        habit_list = HABIT_TEMPLATES.get(tpl["slug"], [])
        for i, h in enumerate(habit_list):
            ht = models.HabitTemplate(
                profile_id=profile.id,
                habit_key=h["habit_key"],
                name=h["name"],
                icon=h["icon"],
                category=h["category"],
                stars=h["stars"],
                description=h.get("description", ""),
                details=h.get("details", ""),
                motivation=h.get("motivation", ""),
                sort_order=i,
            )
            db.add(ht)
            db.flush()

            for j, desc in enumerate(h.get("micro_habits", [])):
                db.add(models.MicroHabit(
                    habit_template_id=ht.id,
                    description=desc,
                    sort_order=j,
                ))

        # Default weekly reward tiers
        for tier in DEFAULT_WEEKLY_TIERS:
            db.add(models.RewardTier(
                profile_id=profile.id,
                tier_type="weekly",
                min_pct=tier["min_pct"],
                multiplier=tier["multiplier"],
                label=tier["label"],
                emoji=tier["emoji"],
                sort_order=tier["sort_order"],
            ))

    db.commit()
