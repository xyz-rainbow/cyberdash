"""Pinned View - Favorites/pinned items"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
import json
from pathlib import Path
from typing import Callable


class PinnedView(Gtk.Box):
    """Pinned/favorites view"""
    
    def __init__(self, on_select: Callable[[str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        
        self.on_select = on_select
        self.pinned_items = []
        
        self.pinned_file = Path.home() / ".config" / "cyberdash" / "pinned.json"
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        
        # Header
        header = Gtk.Label()
        header.set_label("⭐ EMOJIS FIJADOS")
        header.set_halign(Gtk.Align.START)
        header.add_css_class("cyber-top-used-title")
        
        self.append(header)
        
        # Grid for pinned items
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        
        self.grid = Gtk.FlowGrid()
        self.grid.set_max_children_per_line(8)
        self.grid.set_min_children_per_line(4)
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_valign(Gtk.Align.START)
        
        scrolled.set_child(self.grid)
        
        self.append(scrolled)
        
        # ASCII Art section
        ascii_header = Gtk.Label()
        ascii_header.set_label("ASCII ART")
        ascii_header.set_halign(Gtk.Align.START)
        ascii_header.set_margin_top(16)
        ascii_header.add_css_class("cyber-top-used-title")
        
        self.append(ascii_header)
        
        # ASCII grid
        ascii_scrolled = Gtk.ScrolledWindow()
        ascii_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        ascii_scrolled.set_vexpand(True)
        ascii_scrolled.set_height_request(150)
        
        self.ascii_grid = Gtk.FlowGrid()
        self.ascii_grid.set_max_children_per_line(4)
        self.ascii_grid.set_min_children_per_line(2)
        self.ascii_grid.set_halign(Gtk.Align.CENTER)
        
        ascii_scrolled.set_child(self.ascii_grid)
        
        self.append(ascii_scrolled)
    
    def load(self):
        """Load pinned items"""
        # Load emojis
        if self.pinned_file.exists():
            try:
                with open(self.pinned_file, 'r') as f:
                    data = json.load(f)
                    self.pinned_items = data.get('emojis', [])
            except:
                self.pinned_items = []
        else:
            self.pinned_items = []
        
        self.load_pinned_display()
        self.load_ascii_art()
    
    def load_pinned_display(self):
        """Display pinned emojis"""
        # Clear grid
        child = self.grid.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.grid.remove(child)
            child = next_child
        
        if not self.pinned_items:
            empty = Gtk.Label()
            empty.set_label("No hay emojis fijados\nHaz clic en ⭐ para añadir")
            empty.set_halign(Gtk.Align.CENTER)
            empty.set_justify(Gtk.Justify.CENTER)
            self.grid.append(empty)
            return
        
        for emoji in self.pinned_items:
            btn = Gtk.Button()
            btn.set_label(emoji)
            btn.set_size_request(50, 50)
            btn.connect("clicked", self.on_item_clicked, emoji)
            
            # Right click to remove
            btn.set_action_name("context-menu")
            
            self.grid.append(btn)
    
    def load_ascii_art(self):
        """Load ASCII art"""
        # Sample ASCII art
        ascii_art = [
            "(ಠ_ಠ)",
            "(┐『ಠ_ಠ)┐",
            "¯\\_(ツ)_/¯",
            "(⊙_⊙)",
            "(¬_¬)",
            "(^_~)",
            "(>_<)",
            "(^_^)",
            "(°°)",
            "(o_o)",
            "(;_;)",
            "(T_T)",
            "XD",
            "xD",
            ":)",
            ":(",
            ":D",
            ";)",
            "-_-",
            "¬¬",
        ]
        
        # Clear
        child = self.ascii_grid.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.ascii_grid.remove(child)
            child = next_child
        
        for art in ascii_art:
            btn = Gtk.Button()
            btn.set_label(art)
            btn.set_size_request(80, 40)
            btn.connect("clicked", self.on_item_clicked, art)
            self.ascii_grid.append(btn)
    
    def add_pinned(self, emoji: str):
        """Add emoji to pinned"""
        if emoji not in self.pinned_items:
            self.pinned_items.append(emoji)
            self.save()
            self.load_pinned_display()
    
    def remove_pinned(self, emoji: str):
        """Remove emoji from pinned"""
        if emoji in self.pinned_items:
            self.pinned_items.remove(emoji)
            self.save()
            self.load_pinned_display()
    
    def save(self):
        """Save pinned items"""
        Path.home() / ".config" / "cyberdash"
        self.pinned_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.pinned_file, 'w') as f:
            json.dump({'emojis': self.pinned_items}, f)
    
    def on_item_clicked(self, button, item: str):
        """Handle item click"""
        if self.on_select:
            self.on_select(item)
