"""Emoji View - Main emoji picker view"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk

from typing import Callable, List


class EmojiView(Gtk.Box):
    """Emoji picker view"""
    
    def __init__(self, emoji_manager, on_select: Callable[[str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        
        self.emoji_manager = emoji_manager
        self.on_select = on_select
        self.current_category = "recent"
        
        self.setup_ui()
        self.load_emojis()
    
    def setup_ui(self):
        """Setup the UI"""
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        
        # Search box
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Buscar emoji...")
        self.search_entry.set_icon_from_icon_name(Gtk.PositionType.END, "system-search-symbolic")
        self.search_entry.connect("changed", self.on_search_changed)
        self.append(self.search_entry)
        
        # Top used section
        self.top_used_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.top_used_box.set_margin_top(8)
        self.top_used_box.set_margin_bottom(8)
        
        top_used_label = Gtk.Label()
        top_used_label.set_label("⭐ MÁS USADOS")
        top_used_label.set_halign(Gtk.Align.START)
        top_used_label.add_css_class("cyber-top-used-title")
        self.top_used_box.append(top_used_label)
        
        self.top_used_grid = Gtk.FlowGrid()
        self.top_used_grid.set_max_children_per_line(10)
        self.top_used_grid.set_min_children_per_line(5)
        self.top_used_grid.set_halign(Gtk.Align.CENTER)
        self.top_used_box.append(self.top_used_grid)
        
        self.append(self.top_used_box)
        
        # Category tabs
        self.categories_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.categories_box.set_homogeneous(True)
        self.categories_box.set_margin_top(8)
        
        categories = [
            ("recent", "🕐"),
            ("smileys", "😀"),
            ("animals", "🐶"),
            ("food", "🍕"),
            ("activities", "⚽"),
            ("travel", "✈️"),
            ("objects", "💡"),
            ("symbols", "❤️"),
            ("flags", "🏳️"),
            ("ascii", "ASCII"),
        ]
        
        self.category_buttons = {}
        
        for cat_id, cat_icon in categories:
            btn = Gtk.Button()
            btn.set_label(cat_icon)
            btn.set_size_request(40, 36)
            btn.connect("clicked", self.on_category_clicked, cat_id)
            self.categories_box.append(btn)
            self.category_buttons[cat_id] = btn
        
        self.append(self.categories_box)
        
        # Scrollable emoji grid
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        
        self.emoji_grid = Gtk.FlowGrid()
        self.emoji_grid.set_max_children_per_line(8)
        self.emoji_grid.set_min_children_per_line(8)
        self.emoji_grid.set_halign(Gtk.Align.CENTER)
        self.emoji_grid.set_valign(Gtk.Align.START)
        
        scrolled.set_child(self.emoji_grid)
        
        self.append(scrolled)
        
        # Set initial category
        self.update_category_buttons("recent")
    
    def load_emojis(self):
        """Load emojis for current category"""
        # Clear grid
        child = self.emoji_grid.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.emoji_grid.remove(child)
            child = next_child
        
        # Load top used
        self.load_top_used()
        
        # Load category emojis
        emojis = self.emoji_manager.get_category_emojis(self.current_category)
        
        for emoji in emojis:
            self.add_emoji_button(emoji)
    
    def load_top_used(self):
        """Load top used emojis"""
        # Clear
        child = self.top_used_grid.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.top_used_grid.remove(child)
            child = next_child
        
        # Get top used
        top_used = self.emoji_manager.get_top_used()
        
        if top_used:
            self.top_used_box.set_visible(True)
            for emoji in top_used[:10]:
                btn = Gtk.Button()
                btn.set_label(emoji)
                btn.set_size_request(36, 36)
                btn.connect("clicked", self.on_emoji_clicked, emoji)
                self.top_used_grid.append(btn)
        else:
            self.top_used_box.set_visible(False)
    
    def add_emoji_button(self, emoji: str):
        """Add emoji button to grid"""
        btn = Gtk.Button()
        btn.set_label(emoji)
        btn.set_size_request(40, 40)
        btn.connect("clicked", self.on_emoji_clicked, emoji)
        self.emoji_grid.append(btn)
    
    def on_search_changed(self, entry):
        """Handle search input"""
        query = entry.get_text()
        
        if not query:
            self.current_category = "recent"
            self.load_emojis()
            return
        
        # Search emojis
        results = self.emoji_manager.search(query)
        
        # Clear grid
        child = self.emoji_grid.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.emoji_grid.remove(child)
            child = next_child
        
        # Add results
        for emoji in results[:50]:
            self.add_emoji_button(emoji)
    
    def on_category_clicked(self, button, category: str):
        """Handle category selection"""
        self.current_category = category
        self.update_category_buttons(category)
        self.load_emojis()
    
    def update_category_buttons(self, active: str):
        """Update category button states"""
        for cat_id, btn in self.category_buttons.items():
            if cat_id == active:
                btn.add_css_class("active")
            else:
                btn.remove_css_class("active")
    
    def on_emoji_clicked(self, button, emoji: str):
        """Handle emoji selection"""
        if self.on_select:
            self.on_select(emoji)
