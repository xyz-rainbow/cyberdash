"""Translator View - Translation interface"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib

from typing import Callable


class TranslatorView(Gtk.Box):
    """Translator view"""
    
    def __init__(self, translator_service, config, on_done: Callable[[str, str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        
        self.translator = translator_service
        self.config = config
        self.on_done = on_done
        
        self.detected_lang = "auto"
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_spacing(12)
        
        # Provider selector
        provider_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        provider_box.set_spacing(8)
        
        provider_label = Gtk.Label()
        provider_label.set_label("Proveedor:")
        provider_label.set_halign(Gtk.Align.START)
        
        self.provider_combo = Gtk.ComboBoxText()
        providers = [
            ("mymemory", "MyMemory (Gratis)"),
            ("libretranslate", "LibreTranslate"),
            ("openai", "OpenAI (GPT)"),
            ("ollama", "Ollama (Local)"),
        ]
        
        for provider_id, provider_name in providers:
            self.provider_combo.append(provider_id, provider_name)
        
        current_provider = self.config.get('translator_provider', 'mymemory')
        self.provider_combo.set_active_id(current_provider)
        self.provider_combo.connect("changed", self.on_provider_changed)
        
        provider_box.append(provider_label)
        provider_box.append(self.provider_combo)
        
        self.append(provider_box)
        
        # Language selector
        lang_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        lang_box.set_spacing(8)
        
        # Source language
        self.source_combo = Gtk.ComboBoxText()
        self.populate_languages(self.source_combo, include_auto=True)
        self.source_combo.set_active_id("auto")
        self.source_combo.connect("changed", self.on_source_changed)
        
        # Swap button
        swap_btn = Gtk.Button()
        swap_btn.set_label("⇄")
        swap_btn.set_size_request(40, 36)
        swap_btn.connect("clicked", self.on_swap_languages)
        
        # Target language
        self.target_combo = Gtk.ComboBoxText()
        self.populate_languages(self.target_combo, include_auto=False)
        target_lang = self.config.get('target_language', 'es')
        self.target_combo.set_active_id(target_lang)
        
        lang_box.append(self.source_combo)
        lang_box.append(swap_btn)
        lang_box.append(self.target_combo)
        
        self.append(lang_box)
        
        # Input text
        self.input_view = Gtk.TextView()
        self.input_view.set_vexpand(False)
        self.input_view.set_height_request(80)
        self.input_view.set_wrap_mode(Gtk.WrapMode.WORD)
        
        input_frame = Gtk.Frame()
        input_frame.set_child(self.input_view)
        
        self.append(input_frame)
        
        # Translate button
        translate_btn = Gtk.Button()
        translate_btn.set_label("🌐 TRADUCIR")
        translate_btn.set_halign(Gtk.Align.CENTER)
        translate_btn.add_css_class("primary")
        translate_btn.connect("clicked", self.on_translate_clicked)
        
        self.append(translate_btn)
        
        # Output text
        self.output_view = Gtk.TextView()
        self.output_view.set_vexpand(False)
        self.output_view.set_height_request(80)
        self.output_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.output_view.set_editable(False)
        
        output_frame = Gtk.Frame()
        output_frame.set_child(self.output_view)
        
        self.append(output_frame)
        
        # Action buttons
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        action_box.set_homogeneous(True)
        action_box.set_spacing(8)
        
        # Copy button
        copy_btn = Gtk.Button()
        copy_btn.set_label("📋 Copiar")
        copy_btn.connect("clicked", self.on_copy_clicked)
        
        # Replace button
        replace_btn = Gtk.Button()
        replace_btn.set_label("🔄 Reemplazar en app")
        replace_btn.add_css_class("cyber-replace-btn")
        replace_btn.connect("clicked", self.on_replace_clicked)
        
        action_box.append(copy_btn)
        action_box.append(replace_btn)
        
        self.append(action_box)
        
        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_label("")
        self.status_label.set_halign(Gtk.Align.CENTER)
        self.append(self.status_label)
    
    def populate_languages(self, combo: Gtk.ComboBoxText, include_auto: bool = True):
        """Populate language dropdown"""
        if include_auto:
            combo.append("auto", "Auto-detectar")
        
        for code, name in self.translator.LANGUAGES.items():
            if code != "auto":
                combo.append(code, name)
    
    def on_provider_changed(self, combo):
        """Handle provider change"""
        provider = combo.get_active_id()
        self.config.set('translator_provider', provider)
        self.translator.set_provider(provider)
    
    def on_source_changed(self, combo):
        """Handle source language change"""
        pass
    
    def on_swap_languages(self, button):
        """Swap source and target languages"""
        source = self.source_combo.get_active_id()
        target = self.target_combo.get_active_id()
        
        if source != "auto":
            self.target_combo.set_active_id(source)
        
        self.source_combo.set_active_id(target)
    
    def on_translate_clicked(self, button):
        """Handle translate click"""
        # Get input text
        buffer = self.input_view.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
        
        if not text.strip():
            return
        
        self.status_label.set_label("Traduciendo...")
        
        # Get languages
        source = self.source_combo.get_active_id()
        target = self.target_combo.get_active_id()
        
        # Save target language
        self.config.set('target_language', target)
        
        # Translate in background
        GLib.idle_add(self._translate, text, source, target)
    
    def _translate(self, text: str, source: str, target: str):
        """Translate text"""
        try:
            result, detected = self.translator.translate(text, source, target)
            
            # Update output
            buffer = self.output_view.get_buffer()
            buffer.set_text(result)
            
            # Update detected language
            if source == "auto":
                self.detected_lang = detected
                self.status_label.set_label(f"✓ Detectado: {detected}")
            else:
                self.status_label.set_label("✓ Traducción completa")
            
            # Call callback
            if self.on_done:
                self.on_done(text, result)
                
        except Exception as e:
            self.status_label.set_label(f"Error: {str(e)}")
    
    def on_copy_clicked(self, button):
        """Copy translation to clipboard"""
        buffer = self.output_view.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
        
        if text:
            clipboard = Gtk.Clipboard.get_default(Gdk.Display.get_default())
            clipboard.set_text(text, -1)
            self.status_label.set_label("✓ Copiado al portapapeles")
    
    def on_replace_clicked(self, button):
        """Replace text in active application"""
        buffer = self.output_view.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
        
        if text:
            success = self.translator.replace_text_in_app(text)
            if success:
                self.status_label.set_label("✓ Texto reemplazado")
            else:
                self.status_label.set_label("✗ Error: Instala wtype o xdotool")
    
    def paste_and_translate(self):
        """Paste from clipboard and translate"""
        clipboard = Gtk.Clipboard.get_default(Gdk.Display.get_default())
        text = clipboard.wait_for_text()
        
        if text:
            buffer = self.input_view.get_buffer()
            buffer.set_text(text)
            self.on_translate_clicked(None)
