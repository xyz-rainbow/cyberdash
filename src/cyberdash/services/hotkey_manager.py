"""Hotkey Manager - Global keyboard shortcuts"""

import os
import sys
import threading
import time
from typing import Callable, Optional

# Try different backends for global hotkeys
try:
    import keyboard
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False


class HotkeyManager:
    """Manages global keyboard shortcuts"""
    
    def __init__(self, window):
        self.window = window
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.shortcut = "super+."
    
    def register(self):
        """Register global hotkey"""
        if not HAS_KEYBOARD:
            print("Warning: keyboard module not available")
            return
        
        try:
            keyboard.add_hotkey(self.shortcut, self.on_hotkey)
            print(f"Registered hotkey: {self.shortcut}")
        except Exception as e:
            print(f"Failed to register hotkey: {e}")
    
    def unregister(self):
        """Unregister global hotkey"""
        if HAS_KEYBOARD:
            try:
                keyboard.remove_hotkey(self.shortcut)
            except:
                pass
    
    def on_hotkey(self):
        """Handle hotkey press"""
        if self.window:
            # Run in main thread
            def toggle():
                if hasattr(self.window, 'toggle'):
                    self.window.toggle()
            
            # Use GLib.idle_add for GTK thread safety
            from gi.repository import GLib
            GLib.idle_add(toggle)
    
    def set_shortcut(self, shortcut: str):
        """Change the hotkey"""
        self.unregister()
        self.shortcut = shortcut
        self.register()
