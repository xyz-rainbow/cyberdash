#!/usr/bin/env python3
"""
CyberDash - Advanced Emoji Picker for Linux
Cyberpunk Style - GTK4 + libadwaita
"""

import gi
import sys
import os
import json
import threading
import requests
import keyboard
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gdk', '4.0')

from gi.repository import Gtk, Adw, Gdk, GLib, Gio

# Import local modules
from .services.hotkey_manager import HotkeyManager
from .services.clipboard_manager import ClipboardManager
from .services.translator_service import TranslatorService
from .services.emoji_data import EmojiDataManager
from .app.views.emoji_view import EmojiView
from .app.views.translator_view import TranslatorView
from .app.views.clipboard_view import ClipboardView
from .app.views.pinned_view import PinnedView
from .app.views.stickers_view import StickersView
from .app.views.settings_view import SettingsView
from .utils.config import ConfigManager


class CyberDashWindow(Adw.Window):
    """Main floating window for CyberDash"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.config = ConfigManager()
        
        # Window setup
        self.setup_window()
        
        # Services
        self.emoji_manager = EmojiDataManager()
        self.clipboard_manager = ClipboardManager()
        self.translator = TranslatorService(self.config)
        self.hotkey_manager = HotkeyManager(self)
        
        # UI Components
        self.setup_ui()
        
        # Load data
        self.load_data()
        
        # Position window
        self.position_window()
        
        # Register global hotkey
        self.hotkey_manager.register()
    
    def setup_window(self):
        """Configure window properties"""
        self.set_title("CyberDash")
        self.set_default_size(450, 550)
        self.set_resizable(False)
        self.set_decorated(True)
        self.set_focus_visible(True)
        
        # Enable transparency
        self.set_opacity(0.98)
        
        # Custom CSS
        self.setup_css()
    
    def setup_css(self):
        """Load custom CSS styles"""
        css_provider = Gtk.CssProvider()
        
        # Try to load from file, fallback to embedded
        css_path = Path(__file__).parent.parent / "styles" / "main.css"
        
        if css_path.exists():
            css_provider.load_from_file(Gio.File.new_for_path(str(css_path)))
        else:
            # Embedded minimal CSS
            css = """
            window {
                background: #0a0a0a;
            }
            """
            css_provider.load_from_data(css.encode())
        
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def setup_ui(self):
        """Build the main UI"""
        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.main_box)
        
        # Header
        self.setup_header()
        
        # Tab bar
        self.setup_tabs()
        
        # Content area
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.main_box.append(self.content_stack)
        
        # Views
        self.emoji_view = EmojiView(self.emoji_manager, self.on_emoji_selected)
        self.clipboard_view = ClipboardView(self.clipboard_manager, self.on_clipboard_select)
        self.translator_view = TranslatorView(self.translator, self.config, self.on_translate_done)
        self.pinned_view = PinnedView(self.on_pinned_select)
        self.stickers_view = StickersView(self.on_sticker_select)
        self.settings_view = SettingsView(self.config, self.on_settings_changed)
        
        # Add views to stack
        self.content_stack.add_titled(self.emoji_view, "emoji", "Emojis")
        self.content_stack.add_titled(self.stickers_view, "stickers", "Stickers")
        self.content_stack.add_titled(self.translator_view, "translator", "Traductor")
        self.content_stack.add_titled(self.clipboard_view, "clipboard", "Clipboard")
        self.content_stack.add_titled(self.pinned_view, "pinned", "Fijados")
        self.content_stack.add_titled(self.settings_view, "settings", "Settings")
        
        # Status bar
        self.setup_status_bar()
    
    def setup_header(self):
        """Setup header bar"""
        header = Gtk.HeaderBar()
        
        # Title label
        title = Gtk.Label()
        title.set_markup('<span foreground="#00FF41" font="Courier New">▸ CYBERDASH v1.0</span>')
        header.set_title_widget(title)
        
        # Close button
        close_btn = Gtk.Button()
        close_btn.set_icon_name("window-close-symbolic")
        close_btn.set_valign(Gtk.Align.CENTER)
        close_btn.connect("clicked", lambda _: self.hide())
        header.pack_end(close_btn)
        
        self.main_box.append(header)
    
    def setup_tabs(self):
        """Setup navigation tabs"""
        self.tabs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.tabs.set_homogeneous(True)
        self.tabs.set_margin_top(8)
        self.tabs.set_margin_bottom(8)
        self.tabs.set_margin_start(8)
        self.tabs.set_margin_end(8)
        
        tab_names = [
            ("emoji", "🎭"),
            ("stickers", "📦"),
            ("translator", "🌐"),
            ("clipboard", "📋"),
            ("pinned", "⭐"),
            ("settings", "⚙️")
        ]
        
        self.tab_buttons = {}
        
        for i, (name, icon) in enumerate(tab_names):
            btn = Gtk.Button()
            btn.set_label(icon)
            btn.set_valign(Gtk.Align.CENTER)
            btn.set_size_request(60, 40)
            
            # Style class
            btn.add_css_class("flat")
            if i == 0:
                btn.add_css_class("active")
            
            btn.connect("clicked", self.on_tab_clicked, name)
            self.tabs.append(btn)
            self.tab_buttons[name] = btn
        
        self.main_box.append(self.tabs)
    
    def setup_status_bar(self):
        """Setup status bar"""
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        status_box.set_margin_start(12)
        status_box.set_margin_end(12)
        status_box.set_margin_bottom(8)
        
        # Status indicator
        status_indicator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        status_indicator.set_spacing(6)
        
        dot = Gtk.DrawingArea()
        dot.set_size_request(8, 8)
        dot.set_draw_func(self.draw_status_dot)
        
        status_label = Gtk.Label()
        status_label.set_label("READY")
        status_label.set_css_classes(["status-label"])
        status_label.set_css_classes(["dim-label"])
        
        status_indicator.append(dot)
        status_indicator.append(status_label)
        
        # Version
        version = Gtk.Label()
        version.set_label("v1.0.0")
        version.set_hexpand(True)
        version.set_halign(Gtk.Align.END)
        
        status_box.append(status_indicator)
        status_box.append(version)
        
        self.main_box.append(status_box)
    
    def draw_status_dot(self, area, cr, width, height):
        """Draw green status dot"""
        cr.set_source_rgb(0.2, 0.8, 0.2)
        cr.arc(width/2, height/2, width/2, 0, 2 * 3.14159)
        cr.fill()
    
    def load_data(self):
        """Load emoji data and config"""
        # Load emoji data
        self.emoji_manager.load()
        
        # Load pinned items
        self.pinned_view.load()
        
        # Load clipboard history
        self.clipboard_manager.load()
    
    def position_window(self):
        """Position window at center of screen"""
        display = Gdk.Display.get_default()
        
        # Get primary monitor
        monitor = display.get_primary_monitor()
        if monitor is None:
            monitor = display.get_monitors().get_item(0)
        
        if monitor:
            workarea = monitor.get_geometry()
            window_width = 450
            window_height = 550
            
            # Center on monitor
            new_x = (workarea.width - window_width) // 2 + workarea.x
            new_y = (workarea.height - window_height) // 2 + workarea.y
            
            self.set_default_size(window_width, window_height)
            self.set_size_request(window_width, window_height)
    
    def on_tab_clicked(self, button, tab_name):
        """Handle tab selection"""
        # Update button styles
        for name, btn in self.tab_buttons.items():
            if name == tab_name:
                btn.add_css_class("active")
            else:
                btn.remove_css_class("active")
        
        # Switch content
        self.content_stack.set_visible_child_name(tab_name)
    
    def on_key_press(self, widget, event):
        """Handle keyboard shortcuts"""
        key = event.keyval
        state = event.state
        
        # Escape to close
        if key == Gdk.KEY_Escape:
            self.hide()
            return True
        
        # Number keys for tab switching
        if Gdk.KEY_1 <= key <= Gdk.KEY_6:
            tab_names = ["emoji", "stickers", "translator", "clipboard", "pinned", "settings"]
            idx = key - Gdk.KEY_1
            if idx < len(tab_names):
                self.on_tab_clicked(None, tab_names[idx])
                return True
        
        # Ctrl+V in translator - paste and translate
        if state & Gdk.ModifierType.CONTROL_MASK and key == Gdk.KEY_v:
            if self.content_stack.get_visible_child_name() == "translator":
                self.translator_view.paste_and_translate()
                return True
        
        return False
    
    def on_emoji_selected(self, emoji: str):
        """Handle emoji selection"""
        # Copy to clipboard
        self.clipboard_manager.copy_to_clipboard(emoji)
        
        # Add to top used
        self.emoji_manager.add_to_top_used(emoji)
        
        # Show notification
        self.show_toast(f"Copied: {emoji}")
    
    def on_clipboard_select(self, text: str):
        """Handle clipboard item selection"""
        self.clipboard_manager.copy_to_clipboard(text)
        self.show_toast("Copied to clipboard")
    
    def on_translate_done(self, original: str, translated: str):
        """Handle translation complete"""
        self.show_toast("Translation complete!")
    
    def on_pinned_select(self, item: str):
        """Handle pinned item selection"""
        self.clipboard_manager.copy_to_clipboard(item)
        self.show_toast(f"Copied: {item[:20]}...")
    
    def on_sticker_select(self, item: str):
        """Handle sticker/GIF selection"""
        self.clipboard_manager.copy_to_clipboard(item)
        self.show_toast("Copied to clipboard!")
    
    def on_settings_changed(self):
        """Handle settings change"""
        self.translator.reload_config()
        self.show_toast("Settings saved!")
    
    def show_toast(self, message: str):
        """Show toast notification"""
        # Simple toast implementation
        toast = Gtk.Label()
        toast.set_label(message)
        toast.set_margin(12)
        toast.set_halign(Gtk.Align.CENTER)
        
        # Position at bottom
        overlay = Gtk.Overlay()
        overlay.set_child(self.main_box)
        overlay.add_overlay(toast)
        
        self.set_child(overlay)
        
        # Auto remove after 2 seconds
        GLib.timeout_add(2000, lambda: overlay.remove_overlay(toast))
    
    def toggle(self):
        """Toggle window visibility"""
        if self.is_visible():
            self.hide()
        else:
            self.position_window()
            self.present()
    
    def cleanup(self):
        """Cleanup on close"""
        self.hotkey_manager.unregister()


class CyberDashApplication(Adw.Application):
    """Main application class"""
    
    def __init__(self):
        super().__init__(
            application_id="com.cyberdash.app",
            flags=Gio.ApplicationFlags.NON_UNIQUE
        )
        
        self.window = None
        
        self.connect("activate", self.on_activate)
        self.connect("shutdown", self.on_shutdown)
    
    def on_activate(self, app):
        """Handle application activation"""
        if self.window is None:
            self.window = CyberDashWindow(self)
        
        self.window.present()
    
    def on_shutdown(self, app):
        """Handle application shutdown"""
        if self.window:
            self.window.cleanup()


def main():
    """Entry point"""
    app = CyberDashApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
