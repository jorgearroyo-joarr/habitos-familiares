"""
HábitosFam – backend/api/habits.py  (v3)
REST endpoints for habits, daily logs, auth, and dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/api", tags=["habits"])


# ── Auth ──────────────────────────────────────────────────────


@router.post("/auth/login", response_model=schemas.PinLoginOut)
def login(payload: schemas.PinLoginIn, db: Session = Depends(get_db)):
    """Unified login: returns role (admin/user) and profile scope."""
    result = crud.verify_pin(db, payload.pin)
    if not result:
        raise HTTPException(status_code=401, detail="PIN inválido")
    token = crud.generate_token(payload.pin)
    return schemas.PinLoginOut(
        success=True,
        role=result["role"],
        profile_slug=result.get("profile_slug"),
        token=token,
    )


# ── Settings (public – read only) ────────────────────────────


@router.get("/settings", response_model=schemas.AppSettingsOut)
def get_settings(db: Session = Depends(get_db)):
    cfg = crud.get_app_settings(db)
    if not cfg:
        return schemas.AppSettingsOut(
            currency_symbol="$",
            app_name="HábitosFam",
            streak_bonus_days=7,
            streak_bonus_pct=1.5,
        )
    return cfg


# ── Profiles ──────────────────────────────────────────────────


@router.get("/profiles", response_model=List[schemas.ProfileOut])
def list_profiles(db: Session = Depends(get_db)):
    profiles = crud.get_profiles(db)
    result = []
    for p in profiles:
        out = schemas.ProfileOut.model_validate(p)
        out.has_pin = p.pin_hash is not None
        result.append(out)
    return result


@router.get("/profiles/{slug}", response_model=schemas.ProfileOut)
def get_profile(slug: str, db: Session = Depends(get_db)):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{slug}' no encontrado")
    out = schemas.ProfileOut.model_validate(profile)
    out.has_pin = profile.pin_hash is not None
    return out


# ── Habit Config (from DB) ────────────────────────────────────


@router.get(
    "/profiles/{slug}/habits-config", response_model=List[schemas.HabitTemplateOut]
)
def get_habits_config(slug: str, db: Session = Depends(get_db)):
    """Get habit templates + micro-habits for a profile from DB."""
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{slug}' no encontrado")
    return crud.get_habit_templates(db, profile.id)


@router.get("/profiles/{slug}/reward-tiers", response_model=List[schemas.RewardTierOut])
def get_reward_tiers(
    slug: str, tier_type: str = "weekly", db: Session = Depends(get_db)
):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{slug}' no encontrado")
    return crud.get_reward_tiers(db, profile.id, tier_type)


# ── Today's log ───────────────────────────────────────────────


@router.get("/profiles/{slug}/today", response_model=schemas.DayLogOut)
def get_today_log(slug: str, db: Session = Depends(get_db)):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{slug}' no encontrado")

    today_str = date.today().isoformat()
    log = crud.get_day_log(db, profile.id, today_str)
    if not log:
        templates = crud.get_habit_templates(db, profile.id)
        return schemas.DayLogOut(
            id=0,
            profile_id=profile.id,
            date=today_str,
            completed_count=0,
            total=len(templates),
            pct=0.0,
            day_done=False,
            bonus_star=False,
            habit_entries=[],
            created_at=date.today().strftime("%Y-%m-%dT%H:%M:%S"),
        )
    return log


# ── Save habits ───────────────────────────────────────────────


@router.post(
    "/profiles/{slug}/habits", response_model=schemas.DayLogOut, status_code=201
)
def save_habits(slug: str, payload: schemas.DayLogIn, db: Session = Depends(get_db)):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{slug}' no encontrado")
    log = crud.upsert_day_log(db, profile.id, payload.date, payload.habits)
    return log


@router.post("/profiles/{slug}/complete-day", response_model=schemas.DayLogOut)
def complete_day(
    slug: str, payload: schemas.DayCompleteIn, db: Session = Depends(get_db)
):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{slug}' no encontrado")
    log = crud.complete_day(
        db,
        profile.id,
        payload.date,
        payload.completed_count,
        payload.total,
        payload.pct,
    )
    return log


# ── Stats ─────────────────────────────────────────────────────


@router.get("/profiles/{slug}/week", response_model=schemas.WeekStatsOut)
def get_week_stats(
    slug: str, week_start: Optional[str] = None, db: Session = Depends(get_db)
):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{slug}' no encontrado")
    return crud.compute_week_stats(db, profile, week_start)


@router.get("/profiles/{slug}/month", response_model=schemas.MonthStatsOut)
def get_month_stats(
    slug: str, month_key: Optional[str] = None, db: Session = Depends(get_db)
):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{slug}' no encontrado")
    return crud.compute_month_stats(db, profile, month_key)


@router.get("/profiles/{slug}/streak")
def get_streak(slug: str, db: Session = Depends(get_db)):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{slug}' no encontrado")
    streak = crud.compute_streak(db, profile.id)
    return {"profile": slug, "streak": streak}


# ── Dashboard ─────────────────────────────────────────────────


@router.get("/profiles/{slug}/dashboard", response_model=schemas.ProfileDashboardOut)
def get_dashboard(slug: str, db: Session = Depends(get_db)):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{slug}' no encontrado")
    return crud.get_profile_dashboard(db, profile)


# ── Charts / Trends ────────────────────────────────────────────


@router.get("/profiles/{slug}/trends", response_model=schemas.TrendResponse)
def get_trends(
    slug: str,
    period: str = "weekly",  # 'weekly' | 'monthly' | 'yearly'
    db: Session = Depends(get_db),
):
    """Get trend data for charts (daily completion rates)."""
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{slug}' no encontrado")
    if period not in ("weekly", "monthly", "yearly"):
        raise HTTPException(
            status_code=400,
            detail="Periodo inválido: usar 'weekly', 'monthly' o 'yearly'",
        )
    return crud.get_trend_data(db, profile, period)
