"""
Setup the environment variables for API requests.

:author: Mukundan Thanigaivelan
"""

from pathlib import Path
import sys
from tkinter import Tk, simpledialog, messagebox

if getattr(sys, "frozen", False):
    ROOT_DIR = Path(sys.executable).resolve().parent.parent
else:
    ROOT_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = ROOT_DIR / "app" / ".env"

def ask(prompt: str, root: Tk) -> None:
    """
    Prompt user until non-empty input is provided.
    """
    while True:
        value = simpledialog.askstring(
            "First-Time Setup",
            prompt,
            parent=root
        )
        
        if value is None:
            if messagebox.askyesno(
                "Exit Setup",
                "Setup is required. Exit application?",
                parent=root
            ):
                root.destroy()
                raise SystemExit
            continue

        value = value.strip()
        if value:
            return value

        messagebox.showerror(
            "Invalid Input",
            f"{prompt} cannot be empty.",
            parent=root
        )

def create_env(root: Tk) -> None:
    """
    Create .env if it doesn't already exist.
    """
    root.withdraw()
    root.attributes("-topmost", True)

    if ENV_FILE.exists():
        return

    api_key = ask("API Key", root)
    api_secret = ask("API Secret", root)
    api_scopes = ask("API Scopes", root)
    bib_key = ask("Alma Bibkey", root)

    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)

    ENV_FILE.write_text(
        (
            f"API_KEY={api_key}\n"
            f"API_SECRET={api_secret}\n"
            f"API_SCOPES={api_scopes}\n"
            f"BIB_KEY={bib_key}\n"
        ),
        encoding="utf-8"
    )
    messagebox.showinfo(
        "Setup Complete",
        ".env created successfully!",
        parent=root
    )
