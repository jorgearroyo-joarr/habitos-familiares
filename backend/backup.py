"""
HábitosFam – backend/backup.py
Automatic database backup module.
Creates backups before critical operations (reset, profile deletion, etc.)
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path

from .config import settings

logger = logging.getLogger(__name__)

BACKUP_DIR = Path(__file__).parent.parent / "backups"
MAX_BACKUPS = 5


def get_db_path() -> Path | None:
    """Extract the database file path from DATABASE_URL."""
    url = settings.database_url
    if url.startswith("sqlite:///"):
        db_path_str = url.replace("sqlite:///", "")
        if not db_path_str.startswith("/") and not db_path_str.startswith("X:"):
            return Path(__file__).parent.parent / db_path_str
        return Path(db_path_str)
    return None


def create_backup(reason: str = "manual") -> str | None:
    """Create a timestamped backup of the database."""
    db_path = get_db_path()
    if not db_path or not db_path.exists():
        logger.warning("⚠️ No SQLite database found, skipping backup")
        return None

    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"habitosfam_{timestamp}_{reason}.db"
    backup_path = BACKUP_DIR / backup_name

    try:
        shutil.copy2(db_path, backup_path)

        wal_path = db_path.with_suffix(".db-wal")
        shm_path = db_path.with_suffix(".db-shm")
        if wal_path.exists():
            shutil.copy2(
                wal_path, BACKUP_DIR / f"habitosfam_{timestamp}_{reason}.db-wal"
            )
        if shm_path.exists():
            shutil.copy2(
                shm_path, BACKUP_DIR / f"habitosfam_{timestamp}_{reason}.db-shm"
            )

        logger.info(f"✅ Backup created: {backup_name}")
        _cleanup_old_backups()
        return str(backup_path)
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        return None


def _cleanup_old_backups():
    """Remove old backups keeping only MAX_BACKUPS most recent."""
    if not BACKUP_DIR.exists():
        return

    backups = sorted(
        BACKUP_DIR.glob("habitosfam_*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    for old_backup in backups[MAX_BACKUPS:]:
        try:
            old_backup.unlink()
            logger.info(f"🗑️ Removed old backup: {old_backup.name}")

            wal = old_backup.with_suffix(".db-wal")
            shm = old_backup.with_suffix(".db-shm")
            if wal.exists():
                wal.unlink()
            if shm.exists():
                shm.unlink()
        except Exception as e:
            logger.warning(f"⚠️ Failed to remove {old_backup}: {e}")


def list_backups() -> list[dict]:
    """Return list of available backups."""
    if not BACKUP_DIR.exists():
        return []

    backups = []
    for f in sorted(BACKUP_DIR.glob("habitosfam_*.db"), reverse=True):
        stat = f.stat()
        backups.append(
            {
                "name": f.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
        )
    return backups
