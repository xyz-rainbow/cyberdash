"""Stickers View - Stickers and GIFs"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib
import json
import requests
from pathlib import Path
from typing import Callable


class StickersView(Gtk.Box):
    """Stickers and GIFs view"""
    
    def __init__(self, on_select: Callable[[str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        
        self.on_select = on_select
        self.stickers = []
        self.gifs = []
        self.current_provider = "giphy"
        
        self.stickers_file = Path.home() / ".config" / "cyberdash" / "stickers.json"
        
        self.setup_ui()
        self.load_stickers()
    
    def setup_ui(self):
        """Setup UI"""
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_spacing(12)
        
        # Tab buttons for Stickers/GIFs
        tabs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        tabs.set_homogeneous(True)
        
        self.stickers_btn = Gtk.Button()
        self.stickers_btn.set_label("📦 STICKERS")
        self.stickers_btn.add_css_class("active")
        self.stickers_btn.connect("clicked", self.show_stickers)
        
        self.gifs_btn = Gtk.Button()
        self.gifs_btn.set_label("🎬 GIFS")
        self.gifs_btn.connect("clicked", self.show_gifs)
        
        tabs.append(self.stickers_btn)
        tabs.append(self.gifs_btn)
        self.append(tabs)
        
        # Search for GIFs
        self.search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.search_box.set_spacing(8)
        
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Buscar GIFs...")
        self.search_entry.connect("activated", self.search_gifs)
        
        search_btn = Gtk.Button()
        search_btn.set_label("🔍")
        search_btn.connect("clicked", self.search_gifs)
        
        self.search_box.append(self.search_entry)
        self.search_box.append(search_btn)
        self.append(self.search_box)
        
        # Provider selector
        provider_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        provider_box.set_spacing(8)
        
        provider_label = Gtk.Label()
        provider_label.set_label("Proveedor:")
        
        self.provider_combo = Gtk.ComboBoxText()
        self.provider_combo.append("giphy", "Giphy")
        self.provider_combo.append("tenor", "Tenor")
        self.provider_combo.set_active_id("giphy")
        self.provider_combo.connect("changed", self.on_provider_changed)
        
        provider_box.append(provider_label)
        provider_box.append(self.provider_combo)
        self.append(provider_box)
        
        # Content area
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        
        self.content_grid = Gtk.Grid()
        self.content_grid.set_halign(Gtk.Align.CENTER)
        self.content_grid.set_valign(Gtk.Align.START)
        
        scrolled.set_child(self.content_grid)
        self.append(scrolled)
        
        # Loading indicator
        self.loading_label = Gtk.Label()
        self.loading_label.set_label("")
        self.loading_label.set_halign(Gtk.Align.CENTER)
        self.append(self.loading_label)
        
        # Load default stickers
        self.load_default_stickers()
    
    def load_default_stickers(self):
        """Load default sticker pack"""
        default_stickers = [
            ("😺", "cat"),
            ("🐱", "cat2"),
            ("🐶", "dog"),
            ("🦊", "fox"),
            ("🐼", "panda"),
            ("🦁", "lion"),
            ("🐸", "frog"),
            ("🦄", "unicorn"),
            ("🌈", "rainbow"),
            ("🔥", "fire"),
            ("💯", "100"),
            ("😂", "laugh"),
            ("🤣", "rofl"),
            ("😍", "love"),
            ("🤔", "think"),
            ("😎", "cool"),
            ("🥳", "party"),
            ("🚀", "rocket"),
            ("💡", "idea"),
            ("⚡", "zap"),
        ]
        self.stickers = default_stickers
        self.show_stickers(None)
    
    def load_stickers(self):
        """Load user stickers"""
        if self.stickers_file.exists():
            try:
                with open(self.stickers_file, 'r') as f:
                    data = json.load(f)
                    user_stickers = data.get('stickers', [])
                    if user_stickers:
                        self.stickers.extend(user_stickers)
            except:
                pass
    
    def save_stickers(self):
        """Save user stickers"""
        self.stickers_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.stickers_file, 'w') as f:
            json.dump({'stickers': self.stickers}, f)
    
    def show_stickers(self, button):
        """Show stickers tab"""
        self.stickers_btn.add_css_class("active")
        self.gifs_btn.remove_css_class("active")
        self.search_box.set_visible(False)
        
        # Clear grid
        self.clear_grid()
        
        # Show stickers
        col = 0
        row = 0
        for sticker, name in self.stickers:
            btn = Gtk.Button()
            btn.set_label(sticker)
            btn.set_size_request(60, 60)
            btn.connect("clicked", self.on_sticker_clicked, sticker)
            self.content_grid.attach(btn, col, row, 1, 1)
            
            col += 1
            if col >= 5:
                col = 0
                row += 1
    
    def show_gifs(self, button):
        """Show GIFs tab"""
        self.gifs_btn.add_css_class("active")
        self.stickers_btn.remove_css_class("active")
        self.search_box.set_visible(True)
        
        # Clear and show message
        self.clear_grid()
        
        msg = Gtk.Label()
        msg.set_label("🔍 Busca GIFs en el buscador de arriba\n\nO usa los más populares:")
        msg.set_halign(Gtk.Align.CENTER)
        self.content_grid.attach(msg, 0, 0, 3, 1)
        
        # Load trending GIFs
        self.load_trending_gifs()
    
    def on_provider_changed(self, combo):
        """Handle provider change"""
        self.current_provider = combo.get_active_id()
        if self.search_entry.get_text():
            self.search_gifs(None)
        else:
            self.load_trending_gifs()
    
    def search_gifs(self, button):
        """Search GIFs"""
        query = self.search_entry.get_text().strip()
        if not query:
            self.load_trending_gifs()
            return
        
        self.loading_label.set_label("🔄 Buscando...")
        
        # Search in background
        GLib.idle_add(self._search_gifs, query)
    
    def _search_gifs(self, query: str):
        """Search GIFs implementation"""
        try:
            if self.current_provider == "giphy":
                # Giphy API (public beta key)
                url = "https://api.giphy.com/v1/gifs/search"
                params = {
                    "api_key": "dc6zaTOxFJmzC",
                    "q": query,
                    "limit": 25,
                    "rating": "g"
                }
            else:
                # Tenor API (public key)
                url = "https://tenor.googleapis.com/v2/search"
                params = {
                    "key": "AIzaSyAyimkuYQYF_FXVALexPuGQctUWRURdCYQ",
                    "q": query,
                    "limit": 25,
                    "contentfilter": "medium"
                }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            self.gifs = []
            
            if self.current_provider == "giphy":
                for item in data.get("data", []):
                    self.gifs.append({
                        "url": item["images"]["fixed_height"]["url"],
                        "preview": item["images"]["fixed_width_small"]["url"],
                        "title": item.get("title", "")
                    })
            else:
                for item in data.get("results", []):
                    self.gifs.append({
                        "url": item["media_formats"]["gif"]["url"],
                        "preview": item["media_formats"]["tinygif"]["url"],
                        "title": item.get("content_description", "")
                    })
            
            self.display_gifs()
            
        except Exception as e:
            print(f"Error searching GIFs: {e}")
            self.loading_label.set_label(f"Error: {str(e)}")
    
    def load_trending_gifs(self):
        """Load trending GIFs"""
        self.loading_label.set_label("🔄 Cargando trending...")
        GLib.idle_add(self._load_trending)
    
    def _load_trending(self):
        """Load trending GIFs implementation"""
        try:
            url = "https://api.giphy.com/v1/gifs/trending"
            params = {
                "api_key": "dc6zaTOxFJmzC",
                "limit": 25,
                "rating": "g"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            self.gifs = []
            for item in data.get("data", []):
                self.gifs.append({
                    "url": item["images"]["fixed_height"]["url"],
                    "preview": item["images"]["fixed_width_small"]["url"],
                    "title": item.get("title", "")
                })
            
            self.display_gifs()
            
        except Exception as e:
            self.loading_label.set_label(f"Error: {str(e)}")
    
    def display_gifs(self):
        """Display GIFs in grid"""
        self.clear_grid()
        self.loading_label.set_label("")
        
        if not self.gifs:
            msg = Gtk.Label()
            msg.set_label("No se encontraron GIFs")
            msg.set_halign(Gtk.Align.CENTER)
            self.content_grid.attach(msg, 0, 0, 3, 1)
            return
        
        col = 0
        row = 0
        for gif in self.gifs[:20]:
            # Create a button with the GIF preview
            btn = Gtk.Button()
            btn.set_size_request(100, 100)
            btn.set_tooltip_text(gif.get("title", ""))
            
            # Try to load image
            try:
                from gi.repository import GdkPixbuf
                loader = GdkPixbuf.PixbufLoader()
                response = requests.get(gif["preview"], timeout=5)
                loader.write(response.content)
                loader.close()
                pixbuf = loader.get_pixbuf()
                if pixbuf:
                    scaled = pixbuf.scale_simple(100, 100, GdkPixbuf.InterpType.BILINEAR)
                    image = Gtk.Image()
                    image.set_from_pixbuf(scaled)
                    btn.set_child(image)
            except:
                btn.set_label("GIF")
            
            btn.connect("clicked", self.on_gif_clicked, gif["url"])
            self.content_grid.attach(btn, col, row, 1, 1)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
    
    def clear_grid(self):
        """Clear content grid"""
        child = self.content_grid.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.content_grid.remove(child)
            child = next_child
    
    def on_sticker_clicked(self, button, sticker: str):
        """Handle sticker click"""
        if self.on_select:
            self.on_select(sticker)
    
    def on_gif_clicked(self, button, gif_url: str):
        """Handle GIF click - copy URL or download"""
        if self.on_select:
            # Copy GIF URL to clipboard
            self.on_select(gif_url)
    
    def add_sticker(self, sticker: str, name: str = ""):
        """Add a new sticker"""
        self.stickers.append((sticker, name))
        self.save_stickers()
        if self.stickers_btn.get_css_classes():
            self.show_stickers(None)
