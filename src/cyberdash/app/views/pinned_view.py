"""Pinned / Favorites View"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
import json
from pathlib import Path
from typing import Callable

ASCII_ART = [
    "¯\\_(ツ)_/¯", "(ಠ_ಠ)", "(╯°□°）╯︵ ┻━┻", "┬─┬ノ(°-°ノ)",
    "(づ｡◕‿‿◕｡)づ", "( ͡° ͜ʖ ͡°)", "(•_•)", "¯\\(°_o)/¯",
    "(>_<)", "(^_^)", "(;_;)", "(T_T)", "XD", ":)", ":(", ":D",
    ";)", "-_-", "¬¬", "(°°)", "(o_o)", "(•ω•)", "o_O", "O_o",
    "｀ヘ´", "ヽ(°〇°)ﾒ", "(╬ಠ益ಠ)", "ٷ(°◡°)ٷ", "✿◠‿◠",
]


class PinnedView(Gtk.Box):
    def __init__(self, on_select: Callable[[str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.on_select = on_select
        self.pinned_items = []
        self.pinned_file = Path.home() / ".config" / "cyberdash" / "pinned.json"
        self._setup_ui()

    def _setup_ui(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Pinned emojis
        lbl1 = Gtk.Label(label="⭐  EMOJIS FIJADOS")
        lbl1.add_css_class("section-header")
        lbl1.set_halign(Gtk.Align.START)
        lbl1.set_margin_start(10)
        lbl1.set_margin_top(8)
        lbl1.set_margin_bottom(4)
        content.append(lbl1)

        self.pinned_flow = Gtk.FlowBox()
        self.pinned_flow.set_homogeneous(True)
        self.pinned_flow.set_min_children_per_line(6)
        self.pinned_flow.set_max_children_per_line(10)
        self.pinned_flow.set_row_spacing(4)
        self.pinned_flow.set_column_spacing(4)
        self.pinned_flow.set_margin_start(8)
        self.pinned_flow.set_margin_end(8)
        self.pinned_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        content.append(self.pinned_flow)

        # ASCII Art
        lbl2 = Gtk.Label(label="⌨  ASCII ART")
        lbl2.add_css_class("section-header")
        lbl2.set_halign(Gtk.Align.START)
        lbl2.set_margin_start(10)
        lbl2.set_margin_top(16)
        lbl2.set_margin_bottom(4)
        content.append(lbl2)

        ascii_flow = Gtk.FlowBox()
        ascii_flow.set_homogeneous(False)
        ascii_flow.set_min_children_per_line(3)
        ascii_flow.set_max_children_per_line(4)
        ascii_flow.set_row_spacing(4)
        ascii_flow.set_column_spacing(4)
        ascii_flow.set_margin_start(8)
        ascii_flow.set_margin_end(8)
        ascii_flow.set_margin_bottom(12)
        ascii_flow.set_selection_mode(Gtk.SelectionMode.NONE)

        for art in ASCII_ART:
            btn = Gtk.Button(label=art)
            btn.add_css_class("ascii-btn")
            btn.connect("clicked", self._on_clicked, art)
            child = Gtk.FlowBoxChild()
            child.set_child(btn)
            ascii_flow.append(child)

        content.append(ascii_flow)

        scroll.set_child(content)
        self.append(scroll)

    def load(self):
        if self.pinned_file.exists():
            try:
                with open(self.pinned_file, "r") as f:
                    self.pinned_items = json.load(f).get("emojis", [])
            except Exception:
                self.pinned_items = []
        self._refresh_pinned()

    def _refresh_pinned(self):
        while True:
            child = self.pinned_flow.get_first_child()
            if child is None:
                break
            self.pinned_flow.remove(child)

        if not self.pinned_items:
            lbl = Gtk.Label(label="Sin emojis fijados\nPulsa ⭐ en la vista de emojis")
            lbl.add_css_class("empty-label")
            lbl.set_justify(Gtk.Justification.CENTER)
            lbl.set_margin_top(12)
            child = Gtk.FlowBoxChild()
            child.set_child(lbl)
            self.pinned_flow.append(child)
            return

        for emoji in self.pinned_items:
            btn = Gtk.Button(label=emoji)
            btn.add_css_class("pinned-btn")
            btn.connect("clicked", self._on_clicked, emoji)
            child = Gtk.FlowBoxChild()
            child.set_child(btn)
            self.pinned_flow.append(child)

    def add_pinned(self, emoji: str):
        if emoji not in self.pinned_items:
            self.pinned_items.append(emoji)
            self._save()
            self._refresh_pinned()

    def remove_pinned(self, emoji: str):
        if emoji in self.pinned_items:
            self.pinned_items.remove(emoji)
            self._save()
            self._refresh_pinned()

    def _save(self):
        self.pinned_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.pinned_file, "w") as f:
            json.dump({"emojis": self.pinned_items}, f)

    def _on_clicked(self, btn, item: str):
        self.on_select(item)
