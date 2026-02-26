"""Clipboard View - Clipboard history"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk

from typing import Callable


class ClipboardView(Gtk.Box):
    """Clipboard history view"""
    
    def __init__(self, clipboard_manager, on_select: Callable[[str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        
        self.clipboard_manager = clipboard_manager
        self.on_select = on_select
        
        self.setup_ui()
        self.load_history()
    
    def setup_ui(self):
        """Setup UI"""
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        
        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        title = Gtk.Label()
        title.set_label("📋 HISTORIAL")
        title.set_halign(Gtk.Align.START)
        
        clear_btn = Gtk.Button()
        clear_btn.set_label("Limpiar")
        clear_btn.set_halign(Gtk.Align.END)
        clear_btn.set_hexpand(True)
        clear_btn.connect("clicked", self.on_clear_clicked)
        
        header.append(title)
        header.append(clear_btn)
        
        self.append(header)
        
        # List
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        
        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.list_box.set_spacing(4)
        
        scrolled.set_child(self.list_box)
        
        self.append(scrolled)
    
    def load_history(self):
        """Load clipboard history"""
        # Clear list
        child = self.list_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.list_box.remove(child)
            child = next_child
        
        # Load items
        history = self.clipboard_manager.get_history()
        
        if not history:
            empty = Gtk.Label()
            empty.set_label("El historial está vacío")
            empty.set_halign(Gtk.Align.CENTER)
            self.list_box.append(empty)
            return
        
        for item in history[:20]:
            self.add_item(item)
    
    def add_item(self, text: str):
        """Add clipboard item to list"""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        row.set_margin_top(4)
        row.set_margin_bottom(4)
        
        # Content
        content = Gtk.Label()
        content.set_label(text[:80] + ("..." if len(text) > 80 else ""))
        content.set_halign(Gtk.Align.START)
        content.set_hexpand(True)
        
        # Copy button
        copy_btn = Gtk.Button()
        copy_btn.set_icon_name("document-copy-symbolic")
        copy_btn.set_size_request(36, 36)
        copy_btn.connect("clicked", self.on_item_clicked, text)
        
        # Delete button
        delete_btn = Gtk.Button()
        delete_btn.set_icon_name("user-trash-symbolic")
        delete_btn.set_size_request(36, 36)
        delete_btn.connect("clicked", self.on_delete_clicked, text)
        
        row.append(content)
        row.append(copy_btn)
        row.append(delete_btn)
        
        self.list_box.append(row)
    
    def on_item_clicked(self, button, text: str):
        """Handle item click"""
        if self.on_select:
            self.on_select(text)
    
    def on_delete_clicked(self, button, text: str):
        """Handle delete click"""
        self.clipboard_manager.remove_item(text)
        self.load_history()
    
    def on_clear_clicked(self, button):
        """Handle clear click"""
        self.clipboard_manager.clear()
        self.load_history()
