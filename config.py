import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot token - REQUIRED
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Numeric chat ID of your group (forward group) - REQUIRED
FORWARD_GROUP_ID = os.getenv("FORWARD_GROUP_ID")
if not FORWARD_GROUP_ID:
    raise ValueError("FORWARD_GROUP_ID environment variable is required")
try:
    FORWARD_GROUP_ID = int(FORWARD_GROUP_ID)
except ValueError:
    raise ValueError("FORWARD_GROUP_ID must be a valid integer")

# Telethon API credentials - REQUIRED
API_ID = os.getenv("API_ID")
if not API_ID:
    raise ValueError("API_ID environment variable is required")
try:
    API_ID = int(API_ID)
except ValueError:
    raise ValueError("API_ID must be a valid integer")

API_HASH = os.getenv("API_HASH")
if not API_HASH:
    raise ValueError("API_HASH environment variable is required")

# Session name for Telethon client
SESSION_NAME = os.getenv("SESSION_NAME", "contentcurator_session")

# List of target channels (usernames) - can be comma-separated in env var
CHANNELS_STR = os.getenv("CHANNELS", "gizmiztel")
CHANNELS = [channel.strip() for channel in CHANNELS_STR.split(",") if channel.strip()]

# Maximum number of posts to fetch per channel
LIMIT_PER_CHANNEL = int(os.getenv("LIMIT_PER_CHANNEL", "50"))
