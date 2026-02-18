import json
import os
from pathlib import Path

SEEN_FILE = Path(os.environ.get("SEEN_FILE", "/tmp/seen_coupons.json"))

def load_seen() -> set[str]:
    if not SEEN_FILE.exists():
        return set()
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (json.JSONDecodeError, IOError):
        return set()

def save_seen(seen: set[str]) -> None:
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)

def clear_seen() -> None:
    if SEEN_FILE.exists():
        SEEN_FILE.unlink()
