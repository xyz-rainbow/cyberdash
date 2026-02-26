"""Settings View - Application settings"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from typing import Callable


class SettingsView(Gtk.Box):
    """Settings view"""
    
    def __init__(self, config, on_changed: Callable[[], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        
        self.config = config
        self.on_changed = on_changed
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_spacing(16)
        
        # Title
        title = Gtk.Label()
        title.set_label("⚙️ CONFIGURACIÓN")
        title.set_halign(Gtk.Align.START)
        title.add_css_class("cyber-top-used-title")
        
        self.append(title)
        
        # Hotkey setting
        hotkey_box = self.create_setting_group("Atajo Global", "Super + .")
        
        hotkey_entry = Gtk.Entry()
        hotkey_entry.set_text(self.config.get('hotkey', 'super+.'))
        hotkey_entry.connect("changed", self.on_hotkey_changed)
        
        hotkey_box.append(hotkey_entry)
        self.append(hotkey_box)
        
        # Language setting
        
        lang_box = self.create_setting_group("Idioma de traducción", "Por defecto")
        
        self.lang_combo = Gtk.ComboBoxText()
        languages = [
            ("en", "English"),
            ("es", "Español"),
            ("fr", "Français"),
            ("de", "Deutsch"),
            ("it", "Italiano"),
            ("pt", "Português"),
            ("ja", "日本語"),
            ("ko", "한국어"),
            ("zh", "中文"),
        ]
        
        for code, name in languages:
            self.lang_combo.append(code, name)
        
        current = self.config.get('target_language', 'es')
        self.lang_combo.set_active_id(current)
        self.lang_combo.connect("changed", self.on_lang_changed)
        
        lang_box.append(self.lang_combo)
        self.append(lang_box)
        
        # API Keys section
        api_title = Gtk.Label()
        api_title.set_label("🔑 API KEYS (Opcional)")
        api_title.set_halign(Gtk.Align.START)
        api_title.add_css_class("cyber-top-used-title")
        
        self.append(api_title)
        
        # OpenAI
        openai_box = self.create_setting_group("OpenAI API Key", "")
        
        self.openai_entry = Gtk.Entry()
        self.openai_entry.set_visibility(False)
        self.openai_entry.set_placeholder_text("sk-...")
        api_keys = self.config.get('api_keys', {})
        self.openai_entry.set_text(api_keys.get('openai', ''))
        self.openai_entry.connect("changed", self.on_api_changed, 'openai')
        
        openai_box.append(self.openai_entry)
        self.append(openai_box)
        
        # Ollama
        ollama_box = self.create_setting_group("Ollama URL", "Local")
        
        self.ollama_entry = Gtk.Entry()
        self.ollama_entry.set_placeholder_text("http://localhost:11434")
        self.ollama_entry.set_text(api_keys.get('ollama_url', 'http://localhost:11434'))
        self.ollama_entry.connect("changed", self.on_api_changed, 'ollama_url')
        
        ollama_box.append(self.ollama_entry)
        self.append(ollama_box)
        
        # Save button
        save_btn = Gtk.Button()
        save_btn.set_label("💾 GUARDAR CONFIGURACIÓN")
        save_btn.add_css_class("primary")
        save_btn.set_halign(Gtk.Align.CENTER)
        save_btn.connect("clicked", self.on_save_clicked)
        
        self.append(save_btn)
        
        # About
        about = Gtk.Label()
        about.set_label("CyberDash v1.0\nEmoji Picker para Linux\nEstilo Cyberpunk/VHS")
        about.set_halign(Gtk.Align.CENTER)
        about.set_justify(Gtk.Justify.CENTER)
        
        self.append(about)
    
    def create_setting_group(self, label: str, desc: str) -> Gtk.Box:
        """Create a setting group"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_spacing(4)
        
        label_widget = Gtk.Label()
        label_widget.set_label(label)
        label_widget.set_halign(Gtk.Align.START)
        
        box.append(label_widget)
        
        if desc:
            desc_widget = Gtk.Label()
            desc_widget.set_label(desc)
            desc_widget.set_halign(Gtk.Align.START)
            desc_widget.add_css_class("dim-label")
            box.append(desc_widget)
        
        return box
    
    def on_hotkey_changed(self, entry):
        """Handle hotkey change"""
        self.config.set('hotkey', entry.get_text())
    
    def on_lang_changed(self, combo):
        """Handle language change"""
        self.config.set('target_language', combo.get_active_id())
    
    def on_api_changed(self, entry, key: str):
        """Handle API key change"""
        api_keys = self.config.get('api_keys', {})
        api_keys[key] = entry.get_text()
        self.config.set('api_keys', api_keys)
    
    def on_save_clicked(self, button):
        """Handle save click"""
        self.config.save()
        
        if self.on_changed:
            self.on_changed()
