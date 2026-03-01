"""Clipboard View"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from typing import Callable
from ...services.clipboard_manager import ClipboardManager


class ClipboardView(Gtk.Box):
    def __init__(self, clipboard_manager: ClipboardManager, on_select: Callable[[str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.cm = clipboard_manager
        self.on_select = on_select
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header.set_margin_start(10)
        header.set_margin_end(10)
        header.set_margin_top(8)
        header.set_margin_bottom(6)

        lbl = Gtk.Label(label="📋  HISTORIAL")
        lbl.add_css_class("section-header")
        lbl.set_halign(Gtk.Align.START)
        lbl.set_hexpand(True)

        clear_btn = Gtk.Button(label="Limpiar todo")
        clear_btn.add_css_class("danger-btn")
        clear_btn.connect("clicked", self._on_clear)

        header.append(lbl)
        header.append(clear_btn)
        self.append(header)

        # Scrollable list
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.list_box.set_spacing(0)
        scroll.set_child(self.list_box)
        self.append(scroll)

    def refresh(self):
        # Clear
        while True:
            child = self.list_box.get_first_child()
            if child is None:
                break
            self.list_box.remove(child)

        history = self.cm.get_history()
        if not history:
            lbl = Gtk.Label(label="El historial está vacío\nCopia algo para empezar")
            lbl.add_css_class("empty-label")
            lbl.set_justify(Gtk.Justification.CENTER)
            lbl.set_margin_top(40)
            self.list_box.append(lbl)
            return

        for text, timestamp in history[:50]:
            self.list_box.append(self._make_row(text, timestamp))

    def _make_row(self, text: str, timestamp: str) -> Gtk.Box:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        row.add_css_class("clip-item")
        row.set_spacing(6)

        # Text content
        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        info.set_hexpand(True)
        info.set_valign(Gtk.Align.CENTER)

        preview = text[:120].replace("\n", " ")
        if len(text) > 120:
            preview += "…"

        content_lbl = Gtk.Label(label=preview)
        content_lbl.add_css_class("clip-text")
        content_lbl.set_halign(Gtk.Align.START)
        content_lbl.set_ellipsize_mode_from_string = None  # handled by preview truncation
        info.append(content_lbl)

        if timestamp:
            ts_lbl = Gtk.Label(label=timestamp)
            ts_lbl.add_css_class("clip-time")
            ts_lbl.set_halign(Gtk.Align.START)
            info.append(ts_lbl)

        row.append(info)

        # Copy button
        copy_btn = Gtk.Button(label="📋")
        copy_btn.add_css_class("clip-action-btn")
        copy_btn.set_tooltip_text("Copiar")
        copy_btn.set_valign(Gtk.Align.CENTER)
        copy_btn.connect("clicked", self._on_copy, text)
        row.append(copy_btn)

        # Delete button
        del_btn = Gtk.Button(label="🗑")
        del_btn.add_css_class("clip-action-btn")
        del_btn.set_tooltip_text("Eliminar")
        del_btn.set_valign(Gtk.Align.CENTER)
        del_btn.connect("clicked", self._on_delete, text)
        row.append(del_btn)

        return row

    def _on_copy(self, btn, text: str):
        self.on_select(text)

    def _on_delete(self, btn, text: str):
        self.cm.remove_item(text)
        self.refresh()

    def _on_clear(self, btn):
        self.cm.clear()
        self.refresh()
