import sys
from pathlib import Path
from dotenv import load_dotenv

if getattr(sys, "frozen", False):
    # Running as a PyInstaller executable
    ENV_FILE = Path(sys.executable).resolve().parent / ".env"
else:
    # Running Python source code during development
    ENV_FILE = Path(__file__).resolve().parent / ".env"

def load_config() -> Path:
    """Load environment variables and return the .env path."""
    if not ENV_FILE.exists():
        raise FileNotFoundError(
            f".env file not found: {ENV_FILE}"
        )

    load_dotenv(ENV_FILE, override=True)
    return ENV_FILE