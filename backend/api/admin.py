"""
HábitosFam – backend/api/admin.py  (v3)
Admin endpoints: profile CRUD, habit/micro-habit management,
reward tiers, settings, PIN management.
All protected by admin PIN header.
"""

import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..config import settings
from .. import crud, schemas, models

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ── Admin auth dependency ─────────────────────────────────────


def _verify_admin(
    x_admin_pin: Optional[str] = Header(None), db: Session = Depends(get_db)
):
    """Verify admin PIN from X-Admin-Pin header."""
    if not x_admin_pin:
        raise HTTPException(status_code=401, detail="Se requiere PIN de administrador")
    result = crud.verify_pin(db, x_admin_pin)
    if not result or result["role"] != "admin":
        raise HTTPException(status_code=401, detail="PIN de administrador inválido")
    return True


# ── Login ─────────────────────────────────────────────────────


@router.post("/login")
def admin_login(payload: schemas.PinLoginIn, db: Session = Depends(get_db)):
    result = crud.verify_pin(db, payload.pin)
    if not result or result["role"] != "admin":
        raise HTTPException(status_code=401, detail="PIN de administrador inválido")
    token = crud.generate_token(payload.pin)
    return {"success": True, "token": token, "role": "admin"}


# ── Settings ──────────────────────────────────────────────────


@router.get("/settings", response_model=schemas.AppSettingsOut)
def get_settings(db: Session = Depends(get_db), auth=Depends(_verify_admin)):
    return crud.get_app_settings(db)


@router.put("/settings", response_model=schemas.AppSettingsOut)
def update_settings(
    data: schemas.AppSettingsUpdate,
    db: Session = Depends(get_db),
    auth=Depends(_verify_admin),
):
    return crud.update_app_settings(db, data)


# ── Profile CRUD ──────────────────────────────────────────────


@router.get("/profiles", response_model=List[schemas.ProfileOut])
def admin_list_profiles(db: Session = Depends(get_db), auth=Depends(_verify_admin)):
    profiles = crud.get_all_profiles(db)
    result = []
    for p in profiles:
        out = schemas.ProfileOut.model_validate(p)
        out.has_pin = p.pin_hash is not None
        result.append(out)
    return result


@router.post("/profiles", response_model=schemas.ProfileOut, status_code=201)
def admin_create_profile(
    data: schemas.ProfileCreate,
    db: Session = Depends(get_db),
    auth=Depends(_verify_admin),
):
    existing = crud.get_profile_by_slug(db, data.slug)
    if existing:
        raise HTTPException(
            status_code=409, detail=f"El perfil '{data.slug}' ya existe"
        )
    profile = crud.create_profile(db, data)
    out = schemas.ProfileOut.model_validate(profile)
    out.has_pin = profile.pin_hash is not None
    return out


@router.patch("/profiles/{slug}", response_model=schemas.ProfileOut)
def admin_update_profile(
    slug: str,
    data: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    auth=Depends(_verify_admin),
):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    updated = crud.update_profile(db, profile, data)
    out = schemas.ProfileOut.model_validate(updated)
    out.has_pin = updated.pin_hash is not None
    return out


@router.delete("/profiles/{slug}")
def admin_delete_profile(
    slug: str, db: Session = Depends(get_db), auth=Depends(_verify_admin)
):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    crud.delete_profile(db, profile)
    return {"message": f"Profile '{slug}' deactivated"}


# ── Habit Template CRUD ───────────────────────────────────────


@router.get("/profiles/{slug}/habits", response_model=List[schemas.HabitTemplateOut])
def admin_list_habits(
    slug: str, db: Session = Depends(get_db), auth=Depends(_verify_admin)
):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return crud.get_habit_templates(db, profile.id, active_only=False)


@router.post(
    "/profiles/{slug}/habits", response_model=schemas.HabitTemplateOut, status_code=201
)
def admin_create_habit(
    slug: str,
    data: schemas.HabitTemplateCreate,
    db: Session = Depends(get_db),
    auth=Depends(_verify_admin),
):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return crud.create_habit_template(db, profile.id, data)


@router.patch("/habits/{habit_id}", response_model=schemas.HabitTemplateOut)
def admin_update_habit(
    habit_id: int,
    data: schemas.HabitTemplateUpdate,
    db: Session = Depends(get_db),
    auth=Depends(_verify_admin),
):
    tpl = crud.get_habit_template(db, habit_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="Plantilla de hábito no encontrada")
    return crud.update_habit_template(db, tpl, data)


@router.delete("/habits/{habit_id}")
def admin_delete_habit(
    habit_id: int, db: Session = Depends(get_db), auth=Depends(_verify_admin)
):
    tpl = crud.get_habit_template(db, habit_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="Plantilla de hábito no encontrada")
    crud.delete_habit_template(db, tpl)
    return {"message": "Habit deactivated"}


# ── MicroHabit CRUD ──────────────────────────────────────────


@router.post(
    "/habits/{habit_id}/micro-habits",
    response_model=schemas.MicroHabitOut,
    status_code=201,
)
def admin_create_micro(
    habit_id: int,
    data: schemas.MicroHabitCreate,
    db: Session = Depends(get_db),
    auth=Depends(_verify_admin),
):
    tpl = crud.get_habit_template(db, habit_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="Plantilla de hábito no encontrada")
    return crud.create_micro_habit(db, tpl.id, data)


@router.patch("/micro-habits/{micro_id}", response_model=schemas.MicroHabitOut)
def admin_update_micro(
    micro_id: int,
    data: schemas.MicroHabitUpdate,
    db: Session = Depends(get_db),
    auth=Depends(_verify_admin),
):
    mh = db.query(models.MicroHabit).filter(models.MicroHabit.id == micro_id).first()
    if not mh:
        raise HTTPException(status_code=404, detail="MicroHábito no encontrado")
    return crud.update_micro_habit(db, mh, data)


@router.delete("/micro-habits/{micro_id}")
def admin_delete_micro(
    micro_id: int, db: Session = Depends(get_db), auth=Depends(_verify_admin)
):
    mh = db.query(models.MicroHabit).filter(models.MicroHabit.id == micro_id).first()
    if not mh:
        raise HTTPException(status_code=404, detail="MicroHábito no encontrado")
    crud.delete_micro_habit(db, mh)
    return {"message": "MicroHabit deactivated"}


# ── Reorder Habits ───────────────────────────────────────────────


class HabitReorderItem(BaseModel):
    id: int
    sort_order: int


class HabitReorderList(BaseModel):
    orders: List[HabitReorderItem]


@router.post("/profiles/{slug}/habits/reorder")
def reorder_habits(
    slug: str,
    data: HabitReorderList,
    db: Session = Depends(get_db),
    auth=Depends(_verify_admin),
):
    """Reorder habits via drag and drop."""
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{slug}' no encontrado")

    for item in data.orders:
        tpl = crud.get_habit_template(db, item.id)
        if tpl and tpl.profile_id == profile.id:
            tpl.sort_order = item.sort_order

    db.commit()
    return {"message": "Habits reordered"}


# ── Reward Tier CRUD ─────────────────────────────────────────


@router.get("/profiles/{slug}/reward-tiers", response_model=List[schemas.RewardTierOut])
def admin_list_tiers(
    slug: str,
    tier_type: str = "weekly",
    db: Session = Depends(get_db),
    auth=Depends(_verify_admin),
):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return crud.get_reward_tiers(db, profile.id, tier_type)


@router.put("/profiles/{slug}/reward-tiers", response_model=List[schemas.RewardTierOut])
def admin_upsert_tiers(
    slug: str,
    tiers: List[schemas.RewardTierCreate],
    db: Session = Depends(get_db),
    auth=Depends(_verify_admin),
):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return crud.upsert_reward_tiers(db, profile.id, tiers)


# ── Logs & Rewards ───────────────────────────────────────────


@router.get("/profiles/{slug}/logs")
def admin_get_logs(
    slug: str, db: Session = Depends(get_db), auth=Depends(_verify_admin)
):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return crud.get_all_day_logs(db, profile.id)


@router.get("/profiles/{slug}/rewards")
def admin_get_rewards(
    slug: str, db: Session = Depends(get_db), auth=Depends(_verify_admin)
):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return (
        db.query(models.WeekReward)
        .filter(models.WeekReward.profile_id == profile.id)
        .order_by(models.WeekReward.week_start.desc())
        .all()
    )


@router.post("/profiles/{slug}/close-week")
def admin_close_week(
    slug: str,
    week_start: str,
    db: Session = Depends(get_db),
    auth=Depends(_verify_admin),
):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return crud.close_week(db, profile, week_start)


@router.post("/rewards/{reward_id}/mark-paid", response_model=schemas.WeekRewardOut)
def mark_reward_paid(
    reward_id: int,
    payload: schemas.RewardMarkPaid,
    db: Session = Depends(get_db),
    auth=Depends(_verify_admin),
):
    reward = (
        db.query(models.WeekReward).filter(models.WeekReward.id == reward_id).first()
    )
    if not reward:
        raise HTTPException(status_code=404, detail="Recompensa no encontrada")
    return crud.mark_reward_paid(db, reward, payload.notes)


@router.delete("/profiles/{slug}/logs/{date_str}")
def admin_delete_log(
    slug: str, date_str: str, db: Session = Depends(get_db), auth=Depends(_verify_admin)
):
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    log = crud.get_day_log(db, profile.id, date_str)
    if not log:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    db.delete(log)
    db.commit()
    return {"message": f"Log for {slug} on {date_str} deleted"}


# ── Health & Export ──────────────────────────────────────────


@router.get("/health", response_model=schemas.HealthOut)
def health_check(db: Session = Depends(get_db), auth=Depends(_verify_admin)):
    return crud.get_health(db, settings.database_url, settings.db_engine_type)


@router.post("/seed", status_code=201)
def seed_data(db: Session = Depends(get_db), auth=Depends(_verify_admin)):
    crud.seed_default_data(db)
    return {"message": "Default data seeded successfully"}


@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db), auth=Depends(_verify_admin)):
    rows = crud.get_export_data(db)
    output = io.StringIO()
    writer = csv.DictWriter(
        output, fieldnames=["profile", "date", "completed", "total", "pct", "day_done"]
    )
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=habitosfam_export.csv"},
    )


@router.post("/reset-all-data")
def reset_all_data(db: Session = Depends(get_db), auth=Depends(_verify_admin)):
    crud.reset_all_data(db)
    return {"message": "All log data has been reset"}


# ── Templates Catalog ───────────────────────────────────────────


@router.get("/templates/catalog", response_model=schemas.HabitTemplatesCatalog)
def get_templates_catalog():
    """Get predefined habit templates by category."""
    return crud.get_habit_templates_catalog()


# ── Month Auto-Close ────────────────────────────────────────────


@router.post("/profiles/{slug}/close-month", response_model=schemas.MonthCloseResult)
def close_month(
    slug: str,
    month_key: str,
    db: Session = Depends(get_db),
    auth=Depends(_verify_admin),
):
    """Close a specific month and generate rewards."""
    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{slug}' no encontrado")
    return crud.close_month(db, profile, month_key)


@router.post(
    "/profiles/{slug}/close-current-month", response_model=schemas.MonthCloseResult
)
def close_current_month(
    slug: str, db: Session = Depends(get_db), auth=Depends(_verify_admin)
):
    """Close the current month."""
    from datetime import date

    profile = crud.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil '{slug}' no encontrado")
    today = date.today()
    month_key = f"{today.year}-{today.month:02d}"
    return crud.close_month(db, profile, month_key)
