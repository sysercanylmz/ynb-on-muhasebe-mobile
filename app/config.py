from pathlib import Path

APP_NAME = "YNB Ön Muhasebe Mobil"
PACKAGE_NAME = "ynbonmuhasebe"

BASE_DIR = Path(__file__).resolve().parent.parent
RESOURCE_DIR = BASE_DIR / "assets"

# main.py içinde Kivy App.user_data_dir ile güncellenir.
DATA_DIR = BASE_DIR / "data"
BELGE_DIR = DATA_DIR / "belgeler"
DATABASE_PATH = DATA_DIR / "on_muhasebe_mobile.db"

LOGO_PATH = RESOURCE_DIR / "logo.png"
ICON_PATH = RESOURCE_DIR / "app_icon.png"


def set_data_dir(path: str | Path) -> None:
    """Android/masaüstü fark etmeksizin verilerin yazılacağı klasörü ayarlar."""
    global DATA_DIR, BELGE_DIR, DATABASE_PATH
    DATA_DIR = Path(path)
    BELGE_DIR = DATA_DIR / "belgeler"
    DATABASE_PATH = DATA_DIR / "on_muhasebe_mobile.db"
