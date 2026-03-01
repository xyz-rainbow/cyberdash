"""Clipboard Manager - GTK4 compatible, X11 focused"""

import json
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional


class ClipboardManager:
    """Manages clipboard with persistent history"""

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "cyberdash"
        self.history_file = self.config_dir / "clipboard_history.json"
        # List of (text, timestamp) tuples
        self.history: List[Tuple[str, str]] = []
        self.max_history = 50
        self._lock = threading.Lock()

    def load(self):
        """Load history from disk"""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    raw = data.get("history", [])
                    # Support both old (str) and new (list) formats
                    self.history = []
                    for item in raw:
                        if isinstance(item, list) and len(item) == 2:
                            self.history.append((item[0], item[1]))
                        elif isinstance(item, str):
                            self.history.append((item, ""))
                    self.history = self.history[: self.max_history]
            except Exception as e:
                print(f"Clipboard load error: {e}")
                self.history = []

    def _save(self):
        """Save history to disk"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"history": [[t, ts] for t, ts in self.history]},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception as e:
            print(f"Clipboard save error: {e}")

    def copy_to_clipboard(self, text: str) -> bool:
        """Copy text to X11 clipboard using xclip. Returns True on success."""
        if not text:
            return False

        # Try xclip (most reliable on X11)
        for cmd in [
            ["xclip", "-selection", "clipboard"],
            ["xsel", "--clipboard", "--input"],
            ["wl-copy"],  # Wayland fallback
        ]:
            try:
                proc = subprocess.run(
                    cmd,
                    input=text.encode("utf-8"),
                    capture_output=True,
                    timeout=2,
                )
                if proc.returncode == 0:
                    self._add_to_history(text)
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
            except Exception as e:
                print(f"Clipboard error with {cmd[0]}: {e}")

        print("Warning: No clipboard tool found (install xclip)")
        return False

    def paste_to_app(self) -> bool:
        """Simulate Ctrl+V in the previously focused window using xdotool"""
        try:
            subprocess.run(
                ["xdotool", "key", "--clearmodifiers", "ctrl+v"],
                timeout=2,
                capture_output=True,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def type_text(self, text: str) -> bool:
        """Type text directly into the previously focused window"""
        try:
            subprocess.run(
                ["xdotool", "type", "--clearmodifiers", "--", text],
                timeout=5,
                capture_output=True,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _add_to_history(self, text: str):
        """Add text to history (deduplicates, newest first)"""
        with self._lock:
            # Remove if duplicate
            self.history = [(t, ts) for t, ts in self.history if t != text]
            # Add to front
            ts = datetime.now().strftime("%H:%M")
            self.history.insert(0, (text, ts))
            self.history = self.history[: self.max_history]
            self._save()

    def get_history(self) -> List[Tuple[str, str]]:
        """Get list of (text, timestamp) tuples"""
        with self._lock:
            return list(self.history)

    def remove_item(self, text: str):
        with self._lock:
            self.history = [(t, ts) for t, ts in self.history if t != text]
            self._save()

    def clear(self):
        with self._lock:
            self.history = []
            self._save()
