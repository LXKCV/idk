"""Sauvegarde automatique de la base de données SQLite."""

from datetime import datetime
from pathlib import Path
import shutil

from app.config import BACKUP_DIR, DATABASE_PATH


class BackupManager:
    """Crée des copies horodatées de la base locale."""

    def __init__(self, database_path: Path = DATABASE_PATH, backup_dir: Path = BACKUP_DIR) -> None:
        self.database_path = database_path
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> Path | None:
        """Copie la base dans le dossier backups et retourne le chemin créé."""
        if not self.database_path.exists():
            return None
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = self.backup_dir / f"erp_backup_{timestamp}.sqlite3"
        shutil.copy2(self.database_path, target)
        return target
