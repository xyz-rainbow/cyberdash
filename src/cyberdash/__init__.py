#!/usr/bin/env python3
"""
CyberDash - Emoji Picker & Tools for Linux
GTK4 + libadwaita — Estilo Cyberpunk
"""

import gi
import sys
import os
import subprocess
import threading
from pathlib import Path

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk, Adw, Gdk, GLib, Gio

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


TABS = [
    ("emoji",       "🎭", "Emojis"),
    ("stickers",    "📦", "Stickers"),
    ("translator",  "🌐", "Traductor"),
    ("clipboard",   "📋", "Portapapeles"),
    ("pinned",      "⭐", "Fijados"),
    ("settings",    "⚙️",  "Ajustes"),
]


class CyberDashWindow(Adw.Window):
    def __init__(self, app):
        super().__init__(application=app)
        self.app = app

        # Services
        self.config = ConfigManager()
        self.emoji_manager = EmojiDataManager()
        self.clipboard_manager = ClipboardManager()
        self.translator = TranslatorService(self.config)

        # Load data
        self.emoji_manager.load()
        self.clipboard_manager.load()

        # Window config
        self._setup_window()
        self._load_css()
        self._build_ui()

        # Hotkey (X11 keybinder3)
        self.hotkey = HotkeyManager(self._toggle)
        self.hotkey.register()

        # Remember the window that was focused before we opened
        self._prev_window_id: str | None = None

    # ── Window setup ───────────────────────────────────────────────────────

    def _setup_window(self):
        self.set_title("CyberDash")
        self.set_default_size(460, 580)
        self.set_resizable(False)
        # Remove default decorations for a cleaner look
        self.set_decorated(True)
        self.set_opacity(0.97)

        # Close to tray (hide) instead of quitting
        self.connect("close-request", self._on_close_request)

    def _load_css(self):
        css_provider = Gtk.CssProvider()
        css_path = Path(__file__).parent.parent / "styles" / "main.css"
        if css_path.exists():
            css_provider.load_from_file(Gio.File.new_for_path(str(css_path)))
        else:
            # Minimal embedded fallback
            css_provider.load_from_data(b"""
                window { background: #080c08; }
                * { color: #39ff14; font-family: monospace; }
            """)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    # ── UI ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(root)

        # Header
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(False)

        title = Gtk.Label()
        title.set_markup(
            '<span foreground="#39ff14" font="Courier New Bold 11" '
            'letter_spacing="3000">▸ CYBERDASH</span>'
        )
        header.set_title_widget(title)

        close_btn = Gtk.Button()
        close_btn.set_icon_name("window-close-symbolic")
        close_btn.connect("clicked", lambda _: self.hide())
        header.pack_end(close_btn)
        root.append(header)

        # Nav bar
        nav = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        nav.add_css_class("nav-bar")
        nav.set_homogeneous(True)
        nav.set_spacing(2)

        self._tab_btns: dict[str, Gtk.Button] = {}
        for tab_id, icon, tooltip in TABS:
            btn = Gtk.Button(label=icon)
            btn.add_css_class("nav-btn")
            btn.set_tooltip_text(tooltip)
            btn.connect("clicked", self._on_tab_clicked, tab_id)
            nav.append(btn)
            self._tab_btns[tab_id] = btn
        root.append(nav)

        # Content stack
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(80)
        self.stack.set_vexpand(True)
        root.append(self.stack)

        # Views
        self.emoji_view = EmojiView(self.emoji_manager, self._on_emoji_selected)
        self.stickers_view = StickersView(self._on_item_selected)
        self.translator_view = TranslatorView(self.translator, self.config, self._on_translate_done)
        self.clipboard_view = ClipboardView(self.clipboard_manager, self._on_clipboard_selected)
        self.pinned_view = PinnedView(self._on_item_selected)
        self.settings_view = SettingsView(self.config, self._on_settings_changed)

        self.pinned_view.load()

        self.stack.add_named(self.emoji_view,      "emoji")
        self.stack.add_named(self.stickers_view,   "stickers")
        self.stack.add_named(self.translator_view, "translator")
        self.stack.add_named(self.clipboard_view,  "clipboard")
        self.stack.add_named(self.pinned_view,     "pinned")
        self.stack.add_named(self.settings_view,   "settings")

        # Status bar
        status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        status.add_css_class("status-bar")
        status.set_spacing(6)

        dot = Gtk.Box()
        dot.add_css_class("status-dot")

        hotkey_label = "Super+." if self.hotkey.is_available else "Hotkey no disponible"
        slbl = Gtk.Label(label=f"READY  ·  {hotkey_label}")
        slbl.add_css_class("status-text")
        slbl.set_hexpand(True)

        vlbl = Gtk.Label(label="v1.0")
        vlbl.add_css_class("version-text")

        status.append(dot)
        status.append(slbl)
        status.append(vlbl)
        root.append(status)

        # Toast overlay (fixed implementation)
        self._toast_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._toast_box.set_halign(Gtk.Align.CENTER)
        self._toast_box.set_valign(Gtk.Align.END)
        self._toast_box.set_margin_bottom(10)
        self._toast_box.set_visible(False)
        root.append(self._toast_box)

        self._toast_lbl = Gtk.Label()
        self._toast_lbl.add_css_class("toast-label")
        self._toast_box.append(self._toast_lbl)

        # Keyboard shortcuts
        ctrl = Gtk.EventControllerKey()
        ctrl.connect("key-pressed", self._on_key_pressed)
        self.add_controller(ctrl)

        # Set initial tab
        self._switch_tab("emoji")

    # ── Tab switching ───────────────────────────────────────────────────────

    def _on_tab_clicked(self, btn, tab_id: str):
        self._switch_tab(tab_id)

    def _switch_tab(self, tab_id: str):
        self.stack.set_visible_child_name(tab_id)
        for tid, btn in self._tab_btns.items():
            if tid == tab_id:
                btn.add_css_class("active")
            else:
                btn.remove_css_class("active")

        # Refresh clipboard view when switching to it
        if tab_id == "clipboard":
            self.clipboard_view.refresh()

    # ── Keyboard shortcuts ──────────────────────────────────────────────────

    def _on_key_pressed(self, ctrl, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.hide()
            return True

        # 1-6 for tabs
        if Gdk.KEY_1 <= keyval <= Gdk.KEY_6:
            idx = keyval - Gdk.KEY_1
            if idx < len(TABS):
                self._switch_tab(TABS[idx][0])
                return True

        # Ctrl+V in translator = paste & translate
        if (state & Gdk.ModifierType.CONTROL_MASK) and keyval == Gdk.KEY_v:
            if self.stack.get_visible_child_name() == "translator":
                self.translator_view.paste_and_translate()
                return True

        return False

    # ── Callbacks ───────────────────────────────────────────────────────────

    def _on_emoji_selected(self, emoji: str):
        """Copy emoji to clipboard, optionally auto-paste"""
        success = self.clipboard_manager.copy_to_clipboard(emoji)
        self.emoji_manager.add_to_top_used(emoji)
        self.emoji_view.refresh_top_used()

        if success:
            if self.config.get("auto_paste", True):
                # Hide window, wait for it to lose focus, then paste
                self.hide()
                GLib.timeout_add(150, self._auto_paste)
            else:
                self.show_toast(f"Copiado: {emoji}")
        else:
            self.show_toast("⚠ Instala xclip: sudo apt install xclip")

    def _auto_paste(self):
        """Simulate Ctrl+V in the previously active window"""
        self.clipboard_manager.paste_to_app()
        return False  # Don't repeat

    def _on_item_selected(self, item: str):
        """Copy any item (sticker, ascii, pinned) to clipboard"""
        success = self.clipboard_manager.copy_to_clipboard(item)
        if success:
            if self.config.get("auto_paste", True):
                self.hide()
                GLib.timeout_add(150, self._auto_paste)
            else:
                self.show_toast(f"Copiado")
        else:
            self.show_toast("⚠ Instala xclip: sudo apt install xclip")

    def _on_clipboard_selected(self, text: str):
        """Re-copy a clipboard history item"""
        self.clipboard_manager.copy_to_clipboard(text)
        if self.config.get("auto_paste", True):
            self.hide()
            GLib.timeout_add(150, self._auto_paste)
        else:
            self.show_toast("Copiado al portapapeles")

    def _on_translate_done(self, original: str, translated: str):
        # Add translation to clipboard history for convenience
        self.clipboard_manager._add_to_history(translated)

    def _on_settings_changed(self):
        self.translator.reload_config()

    # ── Toast ───────────────────────────────────────────────────────────────

    def show_toast(self, message: str, duration_ms: int = 2000):
        self._toast_lbl.set_label(message)
        self._toast_box.set_visible(True)
        if hasattr(self, "_toast_tid") and self._toast_tid:
            GLib.source_remove(self._toast_tid)
        self._toast_tid = GLib.timeout_add(duration_ms, self._hide_toast)

    def _hide_toast(self):
        self._toast_box.set_visible(False)
        self._toast_tid = None
        return False

    # ── Visibility ──────────────────────────────────────────────────────────

    def _toggle(self):
        """Toggle window visibility (called from hotkey)"""
        if self.is_visible():
            self.hide()
        else:
            self._show_centered()

    def _show_centered(self):
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        if monitor is None:
            monitors = display.get_monitors()
            monitor = monitors.get_item(0)

        if monitor:
            geo = monitor.get_geometry()
            w, h = 460, 580
            # Position slightly above center (like Win+. popup)
            x = geo.x + (geo.width - w) // 2
            y = geo.y + (geo.height - h) // 2 - 40
            # GTK4 doesn't allow set_position directly; use default centering
            # self.set_position is not available in GTK4 – centering is done by WM

        self.present()

    def _on_close_request(self, window):
        """Hide instead of destroy"""
        self.hide()
        return True  # Prevent default destroy

    def cleanup(self):
        self.hotkey.unregister()


class CyberDashApplication(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.cyberdash.app",
            flags=Gio.ApplicationFlags.NON_UNIQUE,
        )
        self.window: CyberDashWindow | None = None
        self.connect("activate", self._on_activate)
        self.connect("shutdown", self._on_shutdown)

    def _on_activate(self, app):
        if self.window is None:
            self.window = CyberDashWindow(app)
        self.window.present()

    def _on_shutdown(self, app):
        if self.window:
            self.window.cleanup()


def main():
    app = CyberDashApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
