"""Emoji View"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from typing import Callable
from ...services.emoji_data import EmojiDataManager, CATEGORIES


class EmojiView(Gtk.Box):
    def __init__(self, emoji_manager: EmojiDataManager, on_select: Callable[[str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.emoji_manager = emoji_manager
        self.on_select = on_select
        self.current_category = "recent"
        self._search_timeout = None
        self._setup_ui()
        self._load_category("recent")

    def _setup_ui(self):
        # ── Search ─────────────────────────────────────
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        search_box.add_css_class("search-box")
        search_box.set_margin_start(8)
        search_box.set_margin_end(8)
        search_box.set_margin_top(8)
        search_box.set_margin_bottom(4)

        self.search = Gtk.Entry()
        self.search.set_placeholder_text("🔍  Buscar emoji...")
        self.search.set_hexpand(True)
        self.search.connect("changed", self._on_search_changed)
        search_box.append(self.search)
        self.append(search_box)

        # ── Top Used ───────────────────────────────────
        self.top_bar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.top_bar.add_css_class("top-used-bar")

        lbl = Gtk.Label(label="★  MÁS USADOS")
        lbl.add_css_class("section-header")
        lbl.set_halign(Gtk.Align.START)
        self.top_bar.append(lbl)

        top_scroll = Gtk.ScrolledWindow()
        top_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        top_scroll.set_min_content_height(50)

        self.top_flow = Gtk.FlowBox()
        self.top_flow.set_homogeneous(True)
        self.top_flow.set_min_children_per_line(8)
        self.top_flow.set_max_children_per_line(20)
        self.top_flow.set_row_spacing(2)
        self.top_flow.set_column_spacing(2)
        self.top_flow.set_margin_start(4)
        self.top_flow.set_margin_end(4)
        self.top_flow.set_margin_bottom(4)
        self.top_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.top_flow.connect("child-activated", self._on_flow_child_activated)

        top_scroll.set_child(self.top_flow)
        self.top_bar.append(top_scroll)
        self.append(self.top_bar)

        # ── Category Bar ───────────────────────────────
        cat_scroll = Gtk.ScrolledWindow()
        cat_scroll.add_css_class("cat-scroll")
        cat_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        cat_scroll.set_min_content_height(38)

        cat_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        cat_box.set_spacing(2)
        cat_box.set_margin_start(4)
        cat_box.set_margin_end(4)

        self._cat_btns = {}
        for cat_id, (icon, label) in CATEGORIES.items():
            btn = Gtk.Button(label=icon)
            btn.add_css_class("cat-btn")
            btn.set_tooltip_text(label)
            btn.connect("clicked", self._on_cat_clicked, cat_id)
            cat_box.append(btn)
            self._cat_btns[cat_id] = btn

        cat_scroll.set_child(cat_box)
        self.append(cat_scroll)

        # ── Emoji Grid ─────────────────────────────────
        scroll = Gtk.ScrolledWindow()
        scroll.add_css_class("emoji-grid-scroll")
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        self.flow = Gtk.FlowBox()
        self.flow.set_homogeneous(True)
        self.flow.set_min_children_per_line(8)
        self.flow.set_max_children_per_line(10)
        self.flow.set_row_spacing(2)
        self.flow.set_column_spacing(2)
        self.flow.set_margin_start(4)
        self.flow.set_margin_end(4)
        self.flow.set_margin_top(4)
        self.flow.set_margin_bottom(4)
        self.flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flow.connect("child-activated", self._on_flow_child_activated)

        scroll.set_child(self.flow)
        self.append(scroll)

        self._update_cat_buttons("recent")

    def _make_emoji_btn(self, emoji: str) -> Gtk.FlowBoxChild:
        btn = Gtk.Button(label=emoji)
        btn.add_css_class("emoji-btn")
        btn.set_size_request(42, 42)
        btn._emoji = emoji

        child = Gtk.FlowBoxChild()
        child.set_child(btn)
        child._emoji = emoji

        btn.connect("clicked", self._on_emoji_btn_clicked, emoji)
        return child

    def _on_emoji_btn_clicked(self, btn, emoji: str):
        self.on_select(emoji)

    def _on_flow_child_activated(self, flowbox, child):
        if hasattr(child, "_emoji"):
            self.on_select(child._emoji)

    def _clear_flow(self, flow):
        while True:
            child = flow.get_first_child()
            if child is None:
                break
            flow.remove(child)

    def _load_category(self, category: str):
        self._clear_flow(self.flow)
        emojis = self.emoji_manager.get_category_emojis(category)
        for emoji in emojis:
            self.flow.append(self._make_emoji_btn(emoji))
        self._load_top_used()

    def _load_top_used(self):
        self._clear_flow(self.top_flow)
        top = self.emoji_manager.get_top_used()
        if top:
            self.top_bar.set_visible(True)
            for emoji in top[:16]:
                btn = Gtk.Button(label=emoji)
                btn.add_css_class("emoji-btn")
                btn.set_size_request(38, 38)
                btn._emoji = emoji

                child = Gtk.FlowBoxChild()
                child.set_child(btn)
                child._emoji = emoji
                btn.connect("clicked", self._on_emoji_btn_clicked, emoji)
                self.top_flow.append(child)
        else:
            self.top_bar.set_visible(False)

    def _on_cat_clicked(self, btn, category: str):
        self.current_category = category
        self.search.set_text("")
        self._update_cat_buttons(category)
        self._load_category(category)

    def _update_cat_buttons(self, active: str):
        for cat_id, btn in self._cat_btns.items():
            if cat_id == active:
                btn.add_css_class("active")
            else:
                btn.remove_css_class("active")

    def _on_search_changed(self, entry):
        # Debounce: wait 200ms after last keystroke
        if self._search_timeout:
            GLib.source_remove(self._search_timeout)
        self._search_timeout = GLib.timeout_add(200, self._do_search)

    def _do_search(self):
        self._search_timeout = None
        query = self.search.get_text().strip()
        if not query:
            self._load_category(self.current_category)
            return
        results = self.emoji_manager.search(query)
        self._clear_flow(self.flow)
        for emoji in results:
            self.flow.append(self._make_emoji_btn(emoji))

    def refresh_top_used(self):
        self._load_top_used()
