import os
import logging
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()

# ── Telegram credentials ──────────────────────────────────────────────────────
TG_BOT_TOKEN      = os.environ.get("TG_BOT_TOKEN", "")
APP_ID            = int(os.environ.get("APP_ID", "0"))
API_HASH          = os.environ.get("API_HASH", "")

# ── Channel / DB settings ─────────────────────────────────────────────────────
CHANNEL_ID        = int(os.environ.get("CHANNEL_ID", "0"))
OWNER_ID          = int(os.environ.get("OWNER_ID", "0"))

# ── MongoDB ───────────────────────────────────────────────────────────────────
DB_URI            = os.environ.get("DATABASE_URL", "")
DB_NAME           = os.environ.get("DATABASE_NAME", "filesharexbot")

# ── Web server (Render keeps the container alive via HTTP) ────────────────────
PORT              = int(os.environ.get("PORT", "8080"))

# ── Bot behaviour ─────────────────────────────────────────────────────────────
TG_BOT_WORKERS    = int(os.environ.get("TG_BOT_WORKERS", "4"))
PROTECT_CONTENT   = os.environ.get("PROTECT_CONTENT", "False") == "True"
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", "False") == "True"

# ── Force-subscribe ───────────────────────────────────────────────────────────
FORCE_SUB_CHANNEL = int(os.environ.get("FORCE_SUB_CHANNEL", "0"))
JOIN_REQUEST_ENABLE = os.environ.get("JOIN_REQUEST_ENABLED", None)

# ── Messages / captions ───────────────────────────────────────────────────────
START_PIC   = os.environ.get("START_PIC", "")
START_MSG   = os.environ.get(
    "START_MESSAGE",
    "Hello {first}!\n\nI can store private files in a specified Channel and share "
    "them via special links.",
)
FORCE_MSG   = os.environ.get(
    "FORCE_SUB_MESSAGE",
    "Hello {first}\n\n<b>You need to join my Channel/Group to use me.\n\nKindly join the Channel below.</b>",
)
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", None)

# ── Auto-delete ───────────────────────────────────────────────────────────────
AUTO_DELETE_TIME    = int(os.environ.get("AUTO_DELETE_TIME", "0"))
AUTO_DELETE_MSG     = os.environ.get(
    "AUTO_DELETE_MSG",
    "This file will be automatically deleted in {time} seconds. Please save it before then.",
)
AUTO_DEL_SUCCESS_MSG = os.environ.get(
    "AUTO_DEL_SUCCESS_MSG",
    "Your file has been successfully deleted. Thank you for using our service. ✅",
)

# ── Misc ──────────────────────────────────────────────────────────────────────
BOT_STATS_TEXT  = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "❌ Don't send me messages directly — I'm only a File Share bot!"

# ── Admins list ───────────────────────────────────────────────────────────────
try:
    ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split() if x]
except ValueError:
    raise Exception("ADMINS env var must contain space-separated integers.")

ADMINS.append(OWNER_ID)  # owner is always admin

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=5),
        logging.StreamHandler(),
    ],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
