"""Hotkey Manager - X11 global shortcuts via keybinder3"""

import threading
from typing import Optional, Callable


class HotkeyManager:
    """
    Global hotkey registration for X11 using keybinder3.
    Falls back to a warning if keybinder3 is not installed.

    Install:  sudo apt install gir1.2-keybinder-3.0
    """

    def __init__(self, callback: Callable):
        self.callback = callback
        self.shortcut = "<Super>period"  # keybinder format
        self._registered = False

        # Try to import keybinder
        try:
            import gi
            gi.require_version("Keybinder", "3.0")
            from gi.repository import Keybinder
            self._keybinder = Keybinder
            Keybinder.init()
            self._available = True
        except Exception as e:
            self._keybinder = None
            self._available = False
            print(f"[HotkeyManager] keybinder3 not available: {e}")
            print("  Install with: sudo apt install gir1.2-keybinder-3.0")

    def register(self, shortcut: Optional[str] = None):
        """Register the global hotkey"""
        if shortcut:
            self.shortcut = shortcut

        if not self._available:
            print(f"[HotkeyManager] Hotkey not registered (keybinder3 missing)")
            return

        try:
            self._keybinder.bind(self.shortcut, self._on_hotkey)
            self._registered = True
            print(f"[HotkeyManager] Registered: {self.shortcut}")
        except Exception as e:
            print(f"[HotkeyManager] Failed to register {self.shortcut}: {e}")

    def unregister(self):
        """Unregister the hotkey"""
        if self._available and self._registered:
            try:
                self._keybinder.unbind(self.shortcut)
                self._registered = False
            except Exception:
                pass

    def _on_hotkey(self, keystring: str):
        """Called by keybinder on hotkey press (main GTK thread)"""
        if self.callback:
            self.callback()

    @property
    def is_available(self) -> bool:
        return self._available
