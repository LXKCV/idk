"""Configuration centrale de l'application ERP.

Ce module regroupe les chemins, couleurs et constantes fonctionnelles afin
que l'interface, la base de données et les services partagent une seule source
fiable de configuration.
"""

from pathlib import Path


# Racine du projet, calculée depuis le dossier app/.
BASE_DIR = Path(__file__).resolve().parent.parent

# Dossiers fonctionnels demandés dans le cahier des charges.
ASSETS_DIR = BASE_DIR / "assets"
DATABASE_DIR = BASE_DIR / "database"
PDF_DIR = BASE_DIR / "pdf"
BACKUP_DIR = BASE_DIR / "backups"

# Fichier SQLite principal.
DATABASE_PATH = DATABASE_DIR / "erp.sqlite3"

# Seuil métier par défaut pour l'alerte stock faible.
DEFAULT_LOW_STOCK_THRESHOLD = 5

# Palette sombre premium inspirée des interfaces SaaS modernes.
COLORS = {
    "background": "#0F172A",
    "panel": "#111827",
    "panel_light": "#1F2937",
    "card": "#172033",
    "primary": "#7C3AED",
    "primary_hover": "#6D28D9",
    "accent": "#22D3EE",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text": "#F8FAFC",
    "muted": "#94A3B8",
    "border": "#334155",
}

# Typographies utilisées dans l'application.
FONT_FAMILY = "Inter"
TITLE_FONT = (FONT_FAMILY, 28, "bold")
SUBTITLE_FONT = (FONT_FAMILY, 16)
BODY_FONT = (FONT_FAMILY, 13)
SMALL_FONT = (FONT_FAMILY, 11)
