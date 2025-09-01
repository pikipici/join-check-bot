
import os
import logging
from typing import List

def _get(name, default=None):
    v = os.getenv(name, default)
    return v.strip() if isinstance(v, str) else v

API_ID = int(_get("API_ID", _get("APP_ID", "0")) or "0")
API_HASH = _get("API_HASH", _get("APP_HASH", ""))
BOT_TOKEN = _get("BOT_TOKEN", _get("TG_BOT_TOKEN", ""))

OWNER_ID = int(_get("OWNER_ID", "0") or "0")
ADMINS_ENV = _get("ADMINS", "")
ADMINS: List[int] = []
for tok in ADMINS_ENV.replace(",", " ").split():
    try:
        ADMINS.append(int(tok))
    except Exception:
        pass
if OWNER_ID and OWNER_ID not in ADMINS:
    ADMINS.append(OWNER_ID)

LOCALE = (_get("LOCALE", "id") or "id").lower()
BUTTONS_PER_ROW = int(_get("BUTTONS_PER_ROW", "2") or "2")

DEFAULT_CONTENT_URL = _get("CONTENT_URL", "https://example.com/your-content")
DEFAULT_START_IMAGE_URL = _get(
    "START_IMAGE_URL",
    "assets/hero.png"   # file lokal bawaan image
)

DATABASE_URL = _get("DATABASE_URL", "postgresql+psycopg://botuser:botpass@db:5432/botdb")
LOG_LEVEL = _get("LOG_LEVEL", "INFO")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise RuntimeError("Harap isi API_ID/API_HASH/BOT_TOKEN pada .env")

logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
                    format="[%(levelname)s] %(name)s: %(message)s")
LOG = logging.getLogger("join-check-bot-pro-buttons")
