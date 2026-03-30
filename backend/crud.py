"""
HábitosFam – backend/crud.py  (v3)
Database CRUD operations.
All DB access goes through this module.
"""

import hashlib
import json
from datetime import date, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import backup, models, schemas
from .config import settings
from .data_config import (
    DEFAULT_ADMIN_PIN,
    DEFAULT_WEEKLY_TIERS,
    HABIT_TEMPLATES,
    PROFILE_TEMPLATES,
    _hash_pin,
)

# ── PIN Auth ──────────────────────────────────────────────────


def verify_pin(db: Session, pin: str) -> dict | None:
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
    profile = (
        db.query(models.Profile)
        .filter(
            models.Profile.pin_hash == pin_hash,
            models.Profile.is_active,
        )
        .first()
    )
    if profile:
        return {"role": "user", "profile_slug": profile.slug}

    return None


def generate_token(pin: str) -> str:
    h = hashlib.sha256(f"{pin}{settings.secret_key}".encode()).hexdigest()[:32]
    return f"{settings.token_prefix}{h}"


# ── AppSettings ───────────────────────────────────────────────


def get_app_settings(db: Session) -> models.AppSettings | None:
    return db.query(models.AppSettings).filter(models.AppSettings.id == 1).first()


def update_app_settings(
    db: Session, data: schemas.AppSettingsUpdate
) -> models.AppSettings | None:
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
    return db.query(models.Profile).filter(models.Profile.is_active).all()


def get_all_profiles(db: Session):
    return db.query(models.Profile).all()


def get_profile_by_slug(db: Session, slug: str):
    return db.query(models.Profile).filter(models.Profile.slug == slug).first()


def get_profile_by_id(db: Session, profile_id: int):
    return db.query(models.Profile).filter(models.Profile.id == profile_id).first()


def create_profile(db: Session, data: schemas.ProfileCreate):
    profile = models.Profile(
        slug=data.slug,
        name=data.name,
        age=data.age,
        avatar=data.avatar,
        theme=data.theme,
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
    backup.create_backup(reason=f"delete_profile_{profile.slug}")
    profile.is_active = False
    db.commit()


# ── HabitTemplate CRUD ───────────────────────────────────────


def get_habit_templates(db: Session, profile_id: int, active_only: bool = True):
    q = db.query(models.HabitTemplate).filter(
        models.HabitTemplate.profile_id == profile_id
    )
    if active_only:
        q = q.filter(models.HabitTemplate.is_active)
    return q.order_by(models.HabitTemplate.sort_order).all()


def get_habit_template(db: Session, template_id: int):
    return (
        db.query(models.HabitTemplate)
        .filter(models.HabitTemplate.id == template_id)
        .first()
    )


def create_habit_template(
    db: Session, profile_id: int, data: schemas.HabitTemplateCreate
):
    tpl = models.HabitTemplate(
        profile_id=profile_id,
        habit_key=data.habit_key,
        name=data.name,
        icon=data.icon,
        category=data.category,
        stars=data.stars,
        description=data.description,
        details=data.details,
        motivation=data.motivation,
        sort_order=data.sort_order,
    )
    db.add(tpl)
    db.flush()
    # Add micro-habits
    for i, mh in enumerate(data.micro_habits):
        db.add(
            models.MicroHabit(
                habit_template_id=tpl.id,
                description=mh.description,
                sort_order=mh.sort_order if mh.sort_order else i,
            )
        )
    db.commit()
    db.refresh(tpl)
    return tpl


def update_habit_template(
    db: Session, tpl: models.HabitTemplate, data: schemas.HabitTemplateUpdate
):
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
    q = db.query(models.MicroHabit).filter(
        models.MicroHabit.habit_template_id == template_id
    )
    if active_only:
        q = q.filter(models.MicroHabit.is_active)
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


def update_micro_habit(
    db: Session, mh: models.MicroHabit, data: schemas.MicroHabitUpdate
):
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
    return (
        db.query(models.RewardTier)
        .filter(
            models.RewardTier.profile_id == profile_id,
            models.RewardTier.tier_type == tier_type,
        )
        .order_by(models.RewardTier.sort_order)
        .all()
    )


def upsert_reward_tiers(
    db: Session, profile_id: int, tiers: list[schemas.RewardTierCreate]
):
    # Delete existing tiers for this type
    tier_type = tiers[0].tier_type if tiers else "weekly"
    db.query(models.RewardTier).filter(
        models.RewardTier.profile_id == profile_id,
        models.RewardTier.tier_type == tier_type,
    ).delete()
    # Insert new
    for t in tiers:
        db.add(
            models.RewardTier(
                profile_id=profile_id,
                tier_type=t.tier_type,
                min_pct=t.min_pct,
                multiplier=t.multiplier,
                label=t.label,
                emoji=t.emoji,
                sort_order=t.sort_order,
            )
        )
    db.commit()
    return get_reward_tiers(db, profile_id, tier_type)


# ── DayLog ────────────────────────────────────────────────────


def get_day_log(db: Session, profile_id: int, date_str: str):
    return (
        db.query(models.DayLog)
        .filter(
            models.DayLog.profile_id == profile_id,
            models.DayLog.date == date_str,
        )
        .first()
    )


def upsert_day_log(
    db: Session, profile_id: int, date_str: str, habits_data: list[schemas.HabitEntryIn]
):
    log = get_day_log(db, profile_id, date_str)
    if not log:
        total = len(get_habit_templates(db, profile_id))
        log = models.DayLog(profile_id=profile_id, date=date_str, total=total or 6)
        db.add(log)
        db.flush()

    # Track newly mastered habits for dopamine feedback
    newly_mastered = []

    # Upsert each habit entry
    for h in habits_data:
        entry = (
            db.query(models.HabitEntry)
            .filter(
                models.HabitEntry.day_log_id == log.id,
                models.HabitEntry.habit_id == h.habit_id,
            )
            .first()
        )

        mini_json = json.dumps(h.mini_tasks) if h.mini_tasks else "{}"

        was_done = entry.done if entry else False
        is_done = h.done

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

        # Update habit mastery if habit was just completed
        if is_done and not was_done:
            mastery_result = _update_habit_mastery(db, profile_id, h.habit_id)
            if mastery_result.get("just_mastered"):
                newly_mastered.append(mastery_result)

    # Recount
    entries = (
        db.query(models.HabitEntry).filter(models.HabitEntry.day_log_id == log.id).all()
    )
    done_count = sum(1 for e in entries if e.done)
    total = log.total or len(entries)
    log.completed_count = done_count
    log.pct = done_count / total if total > 0 else 0
    log.bonus_star = done_count == total and total > 0

    db.commit()
    db.refresh(log)
    return log, newly_mastered


# ── Habit Mastery System ─────────────────────────────────────────

MASTERY_DAYS_REQUIRED = 21  # Days to master a habit


def _update_habit_mastery(db: Session, profile_id: int, habit_key: str):
    """Update consecutive days and mastery status for a habit."""
    from datetime import timedelta

    # Get the habit template
    habit_tpl = (
        db.query(models.HabitTemplate)
        .filter(
            models.HabitTemplate.profile_id == profile_id,
            models.HabitTemplate.habit_key == habit_key,
        )
        .first()
    )
    if not habit_tpl or habit_tpl.is_mastered:
        return {"consecutive_days": 0, "is_mastered": False, "just_mastered": False}

    # Calculate consecutive days from day logs
    today = date.today()
    consecutive = 0
    check_date = today

    for i in range(MASTERY_DAYS_REQUIRED + 30):  # Check up to 30 days back
        log = get_day_log(db, profile_id, check_date.isoformat())
        if log:
            entry = next(
                (e for e in log.habit_entries if e.habit_id == habit_key), None
            )
            if entry and entry.done:
                consecutive += 1
            elif check_date != today:  # Allow today to not be done yet
                break
        check_date -= timedelta(days=1)

    was_mastered = habit_tpl.is_mastered
    habit_tpl.consecutive_days = consecutive

    if consecutive >= MASTERY_DAYS_REQUIRED and not was_mastered:
        habit_tpl.is_mastered = True
        habit_tpl.mastered_at = datetime.utcnow()
        db.commit()
        db.refresh(habit_tpl)
        return {
            "consecutive_days": consecutive,
            "is_mastered": True,
            "just_mastered": True,
            "habit_name": habit_tpl.name,
            "habit_icon": habit_tpl.icon,
        }

    db.commit()
    return {
        "consecutive_days": consecutive,
        "is_mastered": habit_tpl.is_mastered,
        "just_mastered": False,
    }


def complete_day(
    db: Session,
    profile_id: int,
    date_str: str,
    completed_count: int,
    total: int,
    pct: float,
):
    log = get_day_log(db, profile_id, date_str)
    if not log:
        log = models.DayLog(profile_id=profile_id, date=date_str, total=total)
        db.add(log)
        db.flush()

    log.completed_count = completed_count
    log.total = total
    log.pct = pct
    log.day_done = True
    log.bonus_star = completed_count == total and total > 0
    db.commit()
    db.refresh(log)
    return log


def get_day_logs_in_range(db: Session, profile_id: int, start: str, end: str):
    return (
        db.query(models.DayLog)
        .filter(
            models.DayLog.profile_id == profile_id,
            models.DayLog.date >= start,
            models.DayLog.date <= end,
        )
        .order_by(models.DayLog.date)
        .all()
    )


def get_all_day_logs(db: Session, profile_id: int):
    return (
        db.query(models.DayLog)
        .filter(models.DayLog.profile_id == profile_id)
        .order_by(models.DayLog.date.desc())
        .all()
    )


# ── Streak computation ────────────────────────────────────────


def compute_streak(db: Session, profile_id: int) -> int:
    logs = (
        db.query(models.DayLog)
        .filter(
            models.DayLog.profile_id == profile_id,
            models.DayLog.pct >= 0.5,
        )
        .order_by(models.DayLog.date.desc())
        .all()
    )

    if not logs:
        return 0

    streak = 0
    check = date.today()
    log_dates = {log.date for log in logs}

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


def get_week_dates(reference: date | None = None):
    ref = reference or date.today()
    monday = ref - timedelta(days=ref.weekday())
    dates = [(monday + timedelta(days=i)).isoformat() for i in range(7)]
    return dates[0], dates[6], dates


def compute_week_stats(
    db: Session, profile: models.Profile, week_start: str | None = None
):
    if week_start:
        from datetime import date as d

        ref = d.fromisoformat(week_start)
    else:
        ref = None

    monday_str, sunday_str, week_dates = get_week_dates(ref)
    logs = get_day_logs_in_range(db, profile.id, monday_str, sunday_str)
    log_map = {log.date: log for log in logs}

    stars = 0
    completed_days = 0

    # Get mastered habits count for bonus
    mastered_habits = (
        db.query(models.HabitTemplate)
        .filter(
            models.HabitTemplate.profile_id == profile.id,
            models.HabitTemplate.is_mastered == True,
        )
        .count()
    )

    for d_str in week_dates:
        log = log_map.get(d_str)
        if log:
            stars += log.completed_count
            # Bonus star for perfect day
            if log.bonus_star:
                stars += 1
            # Bonus stars for mastered habits (dopamine reward for consistency)
            if log.pct >= 0.5 and mastered_habits > 0:
                stars += mastered_habits  # +1 per mastered habit
            if log.pct >= 0.5:
                completed_days += 1

    total_possible = len(week_dates) * (profile.weekly_reward_full or 6)
    pct = stars / total_possible if total_possible > 0 else 0

    streak = compute_streak(db, profile.id)

    # Compute earned from DB tiers
    tiers = get_reward_tiers(db, profile.id, "weekly")
    earned = _compute_earned_from_tiers(
        tiers, pct, profile.weekly_reward_base, streak, db
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
        day_logs=[schemas.DayLogOut.model_validate(log) for log in logs],
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
    existing = (
        db.query(models.WeekReward)
        .filter(
            models.WeekReward.profile_id == profile.id,
            models.WeekReward.week_start == week_start,
        )
        .first()
    )
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


def bulk_close_week(db: Session, week_start: str):
    """Closes the specified week for all active profiles."""
    profiles = get_profiles(db)
    results = []
    for p in profiles:
        reward = close_week(db, p, week_start)
        results.append(reward)
    return results


def mark_reward_paid(db: Session, reward: models.WeekReward, notes: str | None):
    reward.reward_paid = True
    if notes:
        reward.notes = notes

    # Update profile balance
    reward.profile.balance += reward.earned_amount or 0

    db.commit()
    db.refresh(reward)
    return reward


# ── Virtual Economy ───────────────────────────────────────────


def purchase_item(
    db: Session, profile: models.Profile, item_type: str, item_id: str, cost: float
):
    """
    Handles a purchase in the virtual store.
    item_type: 'theme' | 'avatar'
    """
    if profile.balance < cost:
        return None  # Insufficient funds

    profile.balance -= cost

    if item_type == "theme":
        themes = json.loads(profile.unlocked_themes or '["default"]')
        if item_id not in themes:
            themes.append(item_id)
            profile.unlocked_themes = json.dumps(themes)
    elif item_type == "avatar":
        avatars = json.loads(profile.unlocked_avatars or "[]")
        if item_id not in avatars:
            avatars.append(item_id)
            profile.unlocked_avatars = json.dumps(avatars)

    db.commit()
    db.refresh(profile)
    return profile


# ── Month stats ───────────────────────────────────────────────


def compute_month_stats(
    db: Session, profile: models.Profile, month_key: str | None = None
):
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

    logs = get_day_logs_in_range(
        db, profile.id, first_day.isoformat(), end_date.isoformat()
    )
    completed = sum(1 for log in logs if log.pct >= 0.5)
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
        current_streak = 0
        last_done = None

        for log in sorted(all_logs, key=lambda log: log.date, reverse=True):
            entry = next(
                (e for e in log.habit_entries if e.habit_id == tpl.habit_key), None
            )
            if entry:
                total_days += 1
                if entry.done:
                    completed_days += 1
                    if last_done is None or (
                        last_done
                        and (
                            date.fromisoformat(last_done) - date.fromisoformat(log.date)
                        ).days
                        <= 1
                    ):
                        current_streak += 1
                    last_done = log.date
                else:
                    if last_done is None:
                        pass
                    else:
                        break  # streak broken

        habit_stats.append(
            schemas.HabitDashboardItem(
                habit_key=tpl.habit_key,
                habit_name=tpl.name,
                total_days=total_days,
                completed_days=completed_days,
                pct=completed_days / total_days if total_days > 0 else 0,
                current_streak=current_streak,
            )
        )

    overall_pct = (
        sum(h.pct for h in habit_stats) / len(habit_stats) if habit_stats else 0
    )

    return schemas.ProfileDashboardOut(
        profile_slug=str(profile.slug),
        profile_name=str(profile.name),
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


def reset_all_data(db: Session):
    """Delete all logs and rewards. Keeps profiles and habits."""
    backup.create_backup(reason="reset_all_data")
    db.query(models.HabitEntry).delete(synchronize_session=False)
    db.query(models.DayLog).delete(synchronize_session=False)
    db.query(models.WeekReward).delete(synchronize_session=False)
    db.commit()


def get_export_data(db: Session):
    logs = (
        db.query(models.DayLog)
        .join(models.Profile)
        .order_by(models.Profile.slug, models.DayLog.date)
        .all()
    )
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


# ── Trends / Charts ────────────────────────────────────────────


def get_trend_data(db: Session, profile: models.Profile, period: str):
    """Get daily trend data for charts."""
    from datetime import timedelta

    today = date.today()
    if period == "weekly":
        start_date = today - timedelta(days=6)
        days = 7
    elif period == "monthly":
        start_date = today - timedelta(days=29)
        days = 30
    else:  # yearly
        start_date = today - timedelta(days=364)
        days = 365

    logs = (
        db.query(models.DayLog)
        .filter(
            models.DayLog.profile_id == profile.id,
            models.DayLog.date >= start_date.isoformat(),
            models.DayLog.date <= today.isoformat(),
        )
        .order_by(models.DayLog.date)
        .all()
    )

    log_map = {log.date: log for log in logs}
    data = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        d_str = d.isoformat()
        log = log_map.get(d_str)
        if log:
            data.append(
                schemas.TrendDataPoint(
                    date=d_str,
                    completed=log.completed_count,
                    total=log.total,
                    pct=log.pct,
                )
            )
        else:
            data.append(
                schemas.TrendDataPoint(
                    date=d_str,
                    completed=0,
                    total=0,
                    pct=0.0,
                )
            )

    # Calculate stats
    valid_days = [d for d in data if d.total > 0]
    avg_pct = sum(d.pct for d in valid_days) / len(valid_days) if valid_days else 0
    best = max(valid_days, key=lambda d: d.pct, default=None)

    # Compare with previous period
    prev_start = start_date - timedelta(days=days)
    prev_logs = (
        db.query(models.DayLog)
        .filter(
            models.DayLog.profile_id == profile.id,
            models.DayLog.date >= prev_start.isoformat(),
            models.DayLog.date < start_date.isoformat(),
        )
        .all()
    )
    prev_valid = [log for log in prev_logs if log.total > 0]
    prev_avg = sum(log.pct for log in prev_valid) / len(prev_valid) if prev_valid else 0
    improvement = ((avg_pct - prev_avg) / prev_avg * 100) if prev_avg > 0 else None

    return schemas.TrendResponse(
        profile_slug=str(profile.slug),
        period=period,
        data=data,
        average_pct=avg_pct,
        best_day=best.date if best else None,
        improvement=float(improvement) if improvement is not None else None,
    )


# ── Month Auto-Close ─────────────────────────────────────────────


def close_month(db: Session, profile: models.Profile, month_key: str):
    """Automatically close a month and generate rewards."""
    year, month = month_key.split("-")
    start_date = f"{month_key}-01"
    if month == "12":
        next_month = f"{int(year) + 1}-01-01"
    else:
        next_month = f"{year}-{int(month) + 1:02d}-01"

    logs = (
        db.query(models.DayLog)
        .filter(
            models.DayLog.profile_id == profile.id,
            models.DayLog.date >= start_date,
            models.DayLog.date < next_month,
        )
        .all()
    )

    days_completed = sum(1 for log in logs if log.day_done)
    total_days = len(logs)
    pct = days_completed / total_days if total_days > 0 else 0

    # Check if already closed this month
    existing = (
        db.query(models.MonthReward)
        .filter(
            models.MonthReward.profile_id == profile.id,
            models.MonthReward.month_key == month_key,
        )
        .first()
    )

    if existing:
        return schemas.MonthCloseResult(
            profile_slug=str(profile.slug),
            month_key=month_key,
            days_completed=days_completed,
            total_days=total_days,
            pct=float(pct),
            reward_unlocked=bool(existing.reward_unlocked),
            reward_amount=float(profile.weekly_reward_full)
            if existing.reward_unlocked
            else 0.0,
            reward_desc=str(existing.reward_desc or profile.monthly_reward_desc or ""),
            already_closed=True,
        )

    reward_unlocked = pct >= profile.monthly_min_pct

    month_reward = models.MonthReward(
        profile_id=profile.id,
        month_key=month_key,
        days_completed=days_completed,
        total_days=total_days,
        pct=pct,
        reward_unlocked=reward_unlocked,
        reward_desc=profile.monthly_reward_desc,
    )
    db.add(month_reward)
    db.commit()
    db.refresh(month_reward)

    return schemas.MonthCloseResult(
        profile_slug=str(profile.slug),
        month_key=month_key,
        days_completed=days_completed,
        total_days=total_days,
        pct=float(pct),
        reward_unlocked=reward_unlocked,
        reward_amount=float(profile.weekly_reward_full) if reward_unlocked else 0.0,
        reward_desc=str(profile.monthly_reward_desc or ""),
        already_closed=False,
    )


# ── Habit Templates Catalog ─────────────────────────────────────


def get_habit_templates_catalog():
    """Return predefined habit templates by age category."""
    return schemas.HabitTemplatesCatalog(
        categories=[
            schemas.HabitTemplateCategory(
                category="higiene",
                description="Hábitos de higiene personal",
                age_range="3-6",
                habits=[
                    schemas.HabitTemplateCreate(
                        habit_key="lavarse_dientes",
                        name="Lavarse los dientes",
                        icon="🦷",
                        category="higiene",
                        stars=2,
                        description="Lavarse los dientes después de comer",
                        details="Usar cepillo y pasta dental",
                        motivation="¡Sonrisa sana!",
                        sort_order=1,
                        micro_habits=[
                            schemas.MicroHabitCreate(
                                description="Ir al baño", sort_order=1
                            ),
                            schemas.MicroHabitCreate(
                                description="Tomar el cepillo", sort_order=2
                            ),
                            schemas.MicroHabitCreate(
                                description="Poner pasta", sort_order=3
                            ),
                            schemas.MicroHabitCreate(
                                description="Cepillar 2 minutos", sort_order=4
                            ),
                        ],
                    ),
                    schemas.HabitTemplateCreate(
                        habit_key="bañarse",
                        name="Baño diario",
                        icon="🛁",
                        category="higiene",
                        stars=2,
                        description="Bañarse todos los días",
                        details="Uso de jabón y shampoo",
                        motivation="¡Limpio y fresco!",
                        sort_order=2,
                        micro_habits=[
                            schemas.MicroHabitCreate(
                                description="Preparar ropa", sort_order=1
                            ),
                            schemas.MicroHabitCreate(
                                description="Entrar al baño", sort_order=2
                            ),
                            schemas.MicroHabitCreate(
                                description="Enjabonarse", sort_order=3
                            ),
                            schemas.MicroHabitCreate(
                                description="Secarse bien", sort_order=4
                            ),
                        ],
                    ),
                ],
            ),
            schemas.HabitTemplateCategory(
                category="estudio",
                description="Hábitos de estudio y aprendizaje",
                age_range="6-12",
                habits=[
                    schemas.HabitTemplateCreate(
                        habit_key="hacer_tareas",
                        name="Hacer tareas",
                        icon="📚",
                        category="estudio",
                        stars=3,
                        description="Completar las tareas escolares",
                        details="Sin ayuda de adultos",
                        motivation="¡Casi un experto!",
                        sort_order=1,
                        micro_habits=[
                            schemas.MicroHabitCreate(
                                description="Sacar útiles", sort_order=1
                            ),
                            schemas.MicroHabitCreate(
                                description="Leer instrucciones", sort_order=2
                            ),
                            schemas.MicroHabitCreate(
                                description="Resolver ejercicios", sort_order=3
                            ),
                            schemas.MicroHabitCreate(
                                description="Revisar respuestas", sort_order=4
                            ),
                        ],
                    ),
                    schemas.HabitTemplateCreate(
                        habit_key="leer",
                        name="Leer un libro",
                        icon="📖",
                        category="estudio",
                        stars=2,
                        description="Leer al menos 15 minutos",
                        details="Libro de su elección",
                        motivation="¡Un nuevo mundo!",
                        sort_order=2,
                        micro_habits=[
                            schemas.MicroHabitCreate(
                                description="Elegir libro", sort_order=1
                            ),
                            schemas.MicroHabitCreate(
                                description="Sentarse cómodamente", sort_order=2
                            ),
                            schemas.MicroHabitCreate(
                                description="Leer 15 minutos", sort_order=3
                            ),
                        ],
                    ),
                ],
            ),
            schemas.HabitTemplateCategory(
                category="deporte",
                description="Hábitos de actividad física",
                age_range="5-14",
                habits=[
                    schemas.HabitTemplateCreate(
                        habit_key="ejercicio",
                        name="Ejercicio diario",
                        icon="⚽",
                        category="deporte",
                        stars=3,
                        description="30 minutos de actividad física",
                        details="Correr, jugar o deportes",
                        motion="¡ energía!",
                        sort_order=1,
                        micro_habits=[
                            schemas.MicroHabitCreate(
                                description="Calentar", sort_order=1
                            ),
                            schemas.MicroHabitCreate(
                                description="Jugar fuera", sort_order=2
                            ),
                            schemas.MicroHabitCreate(
                                description="Estirar", sort_order=3
                            ),
                        ],
                    ),
                ],
            ),
            schemas.HabitTemplateCategory(
                category="tecnologia",
                description="Tecnología para el Bien - Usar la tecnología de manera positiva",
                age_range="6-18",
                habits=[
                    schemas.HabitTemplateCreate(
                        habit_key="tech_crear",
                        name="Crear con Tecnología",
                        icon="💻",
                        category="tecnologia",
                        stars=2,
                        description="Crear algo digital positivo",
                        details="Programar, diseñar, escribir código",
                        motivation="¡La tecnología te permite crear cosas increíbles!",
                        sort_order=1,
                        micro_habits=[
                            schemas.MicroHabitCreate(
                                description="Practicar programación o código",
                                sort_order=1,
                            ),
                            schemas.MicroHabitCreate(
                                description="Crear algo digital (dibujo, historia, juego)",
                                sort_order=2,
                            ),
                        ],
                    ),
                    schemas.HabitTemplateCreate(
                        habit_key="tech_aprender",
                        name="Aprender con Tecnología",
                        icon="🔍",
                        category="tecnologia",
                        stars=2,
                        description="Investigar y aprender temas positivos",
                        details="Búsquedas productivas, cursos online",
                        motivation="¡Internet tiene todo el conocimiento del mundo!",
                        sort_order=2,
                        micro_habits=[
                            schemas.MicroHabitCreate(
                                description="Investigar un tema que me interese",
                                sort_order=1,
                            ),
                            schemas.MicroHabitCreate(
                                description="Ver un tutorial o curso constructivo",
                                sort_order=2,
                            ),
                        ],
                    ),
                    schemas.HabitTemplateCreate(
                        habit_key="tech_compartir",
                        name="Compartir Positivamente",
                        icon="📱",
                        category="tecnologia",
                        stars=2,
                        description="Usar la tecnología para conectar y ayudar",
                        details="Mensajes positivos, compartir conocimientos",
                        motivation="¡Comparte cosas buenas con el mundo!",
                        sort_order=3,
                        micro_habits=[
                            schemas.MicroHabitCreate(
                                description="Enviar un mensaje positivo a alguien",
                                sort_order=1,
                            ),
                            schemas.MicroHabitCreate(
                                description="Compartir algo útil con mi familia",
                                sort_order=2,
                            ),
                        ],
                    ),
                ],
            ),
        ]
    )


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
        existing = (
            db.query(models.Profile).filter(models.Profile.slug == tpl["slug"]).first()
        )
        if existing:
            continue

        profile = models.Profile(
            slug=tpl["slug"],
            name=tpl["name"],
            age=tpl["age"],
            avatar=tpl["avatar"],
            theme=tpl["theme"],
            pin_hash=_hash_pin(str(tpl.get("pin"))) if tpl.get("pin") else None,
            weekly_reward_base=tpl["weekly_reward_base"],
            weekly_reward_full=tpl["weekly_reward_full"],
            monthly_reward_desc=tpl["monthly_reward_desc"],
            monthly_min_pct=tpl["monthly_min_pct"],
        )
        db.add(profile)
        db.flush()

        # Habit templates + micro-habits
        habit_list = HABIT_TEMPLATES.get(str(tpl["slug"]), [])
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

            raw_mh = h.get("micro_habits", [])
            if isinstance(raw_mh, list):
                for j, desc in enumerate(raw_mh):
                    db.add(
                        models.MicroHabit(
                            habit_template_id=ht.id,
                            description=str(desc),
                            sort_order=j,
                        )
                    )

        # Default weekly reward tiers
        for tier in DEFAULT_WEEKLY_TIERS:
            db.add(
                models.RewardTier(
                    profile_id=profile.id,
                    tier_type="weekly",
                    min_pct=tier["min_pct"],
                    multiplier=tier["multiplier"],
                    label=tier["label"],
                    emoji=tier["emoji"],
                    sort_order=tier["sort_order"],
                )
            )

    db.commit()


# ── Comparison Charts (Admin) ─────────────────────────────────────


def get_comparison_charts(db: Session):
    """Get comparative stats for all profiles (for admin charts)."""
    from datetime import timedelta

    profiles = get_all_profiles(db)
    today = date.today()
    result = []

    for profile in profiles:
        if not profile.is_active:
            continue

        # Completion rate last 7 days
        week_start = today - timedelta(days=6)
        week_logs = (
            db.query(models.DayLog)
            .filter(
                models.DayLog.profile_id == profile.id,
                models.DayLog.date >= week_start.isoformat(),
                models.DayLog.date <= today.isoformat(),
            )
            .all()
        )
        valid_logs = [log for log in week_logs if log.total > 0]
        completion_rate_7d = (
            sum(log.pct for log in valid_logs) / len(valid_logs) * 100
            if valid_logs
            else 0.0
        )

        # Current streak
        current_streak = calculate_current_streak(db, profile)

        # Total rewards earned (weekly)
        total_rewards = (
            db.query(func.sum(models.WeekReward.earned_amount))
            .filter(models.WeekReward.profile_id == profile.id)
            .scalar()
        ) or 0.0

        # Weekly progress (last 4 weeks)
        weekly_progress = []
        for weeks_ago in range(4):
            week_start_i = today - timedelta(days=7 * (weeks_ago + 1))
            week_end = week_start_i + timedelta(days=6)
            w_logs = (
                db.query(models.DayLog)
                .filter(
                    models.DayLog.profile_id == profile.id,
                    models.DayLog.date >= week_start_i.isoformat(),
                    models.DayLog.date <= week_end.isoformat(),
                )
                .all()
            )
            w_valid = [log for log in w_logs if log.total > 0]
            w_pct = (
                sum(log.pct for log in w_valid) / len(w_valid) * 100 if w_valid else 0.0
            )
            weekly_progress.append(round(w_pct, 1))

        weekly_progress.reverse()  # Oldest to newest

        result.append(
            schemas.ProfileComparisonStats(
                slug=str(profile.slug),
                name=profile.name,
                avatar=profile.avatar,
                theme=profile.theme,
                completion_rate_7d=round(completion_rate_7d, 1),
                current_streak=current_streak,
                total_rewards_earned=round(float(total_rewards), 2),
                weekly_progress=weekly_progress,
            )
        )

    return schemas.ComparisonChartsOut(profiles=result, period="last_4_weeks")
