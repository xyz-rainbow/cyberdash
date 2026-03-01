"""Translator View"""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk, GLib
import threading
from typing import Callable
from ...services.translator_service import TranslatorService, LANGUAGES


class TranslatorView(Gtk.Box):
    def __init__(self, translator: TranslatorService, config, on_done: Callable):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.translator = translator
        self.config = config
        self.on_done = on_done
        self._setup_ui()

    def _setup_ui(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        self.append(box)

        # Provider row
        prov_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        prov_lbl = Gtk.Label(label="Proveedor:")
        prov_lbl.add_css_class("provider-label")

        self.provider_combo = Gtk.ComboBoxText()
        providers = [
            ("mymemory", "MyMemory (gratuito)"),
            ("libretranslate", "LibreTranslate"),
            ("openai", "OpenAI GPT"),
            ("ollama", "Ollama local"),
        ]
        for pid, pname in providers:
            self.provider_combo.append(pid, pname)
        cur = self.config.get("translator_provider", "mymemory")
        self.provider_combo.set_active_id(cur)
        self.provider_combo.connect("changed", self._on_provider_changed)

        prov_row.append(prov_lbl)
        prov_row.append(self.provider_combo)
        box.append(prov_row)

        # Language row
        lang_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.src_combo = Gtk.ComboBoxText()
        self.src_combo.append("auto", "Auto-detectar")
        for code, name in LANGUAGES.items():
            if code != "auto":
                self.src_combo.append(code, name)
        self.src_combo.set_active_id("auto")
        self.src_combo.set_hexpand(True)
        lang_row.append(self.src_combo)

        swap_btn = Gtk.Button(label="⇄")
        swap_btn.add_css_class("swap-btn")
        swap_btn.connect("clicked", self._swap_langs)
        lang_row.append(swap_btn)

        self.tgt_combo = Gtk.ComboBoxText()
        for code, name in LANGUAGES.items():
            if code != "auto":
                self.tgt_combo.append(code, name)
        tgt = self.config.get("target_language", "es")
        self.tgt_combo.set_active_id(tgt)
        self.tgt_combo.set_hexpand(True)
        lang_row.append(self.tgt_combo)

        box.append(lang_row)

        # Input
        in_frame = Gtk.Frame()
        in_frame.add_css_class("text-area")
        self.input_view = Gtk.TextView()
        self.input_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.input_view.set_size_request(-1, 85)
        self.input_view.set_top_margin(6)
        self.input_view.set_left_margin(8)
        self.input_view.set_right_margin(8)
        in_frame.set_child(self.input_view)
        box.append(in_frame)

        # Buttons
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_row.set_homogeneous(True)

        paste_btn = Gtk.Button(label="📋 Pegar")
        paste_btn.add_css_class("primary-btn")
        paste_btn.connect("clicked", self._paste_text)
        btn_row.append(paste_btn)

        trans_btn = Gtk.Button(label="🌐 Traducir")
        trans_btn.add_css_class("primary-btn")
        trans_btn.connect("clicked", self._on_translate)
        btn_row.append(trans_btn)

        box.append(btn_row)

        # Detected lang label
        self.detected_lbl = Gtk.Label(label="")
        self.detected_lbl.add_css_class("detected-lang")
        self.detected_lbl.set_halign(Gtk.Align.START)
        box.append(self.detected_lbl)

        # Output
        out_frame = Gtk.Frame()
        out_frame.add_css_class("text-area")
        self.output_view = Gtk.TextView()
        self.output_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.output_view.set_editable(False)
        self.output_view.set_cursor_visible(False)
        self.output_view.set_size_request(-1, 85)
        self.output_view.set_top_margin(6)
        self.output_view.set_left_margin(8)
        self.output_view.set_right_margin(8)
        out_frame.set_child(self.output_view)
        box.append(out_frame)

        # Action buttons
        act_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        act_row.set_homogeneous(True)

        copy_btn = Gtk.Button(label="📋 Copiar traducción")
        copy_btn.add_css_class("primary-btn")
        copy_btn.connect("clicked", self._copy_output)
        act_row.append(copy_btn)

        replace_btn = Gtk.Button(label="⌨️ Escribir en app")
        replace_btn.add_css_class("primary-btn")
        replace_btn.connect("clicked", self._replace_in_app)
        act_row.append(replace_btn)

        box.append(act_row)

        # Status
        self.status_lbl = Gtk.Label(label="")
        self.status_lbl.add_css_class("detected-lang")
        self.status_lbl.set_halign(Gtk.Align.CENTER)
        box.append(self.status_lbl)

    def _on_provider_changed(self, combo):
        self.translator.set_provider(combo.get_active_id())

    def _swap_langs(self, btn):
        src = self.src_combo.get_active_id()
        tgt = self.tgt_combo.get_active_id()
        if src and src != "auto":
            self.tgt_combo.set_active_id(src)
        if tgt:
            self.src_combo.set_active_id(tgt)

    def _get_input_text(self) -> str:
        buf = self.input_view.get_buffer()
        return buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)

    def _set_output_text(self, text: str):
        self.output_view.get_buffer().set_text(text)

    def _get_output_text(self) -> str:
        buf = self.output_view.get_buffer()
        return buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)

    def _paste_text(self, btn):
        """Paste from clipboard into input using GTK4 API"""
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.read_text_async(None, self._on_clipboard_text, None)

    def _on_clipboard_text(self, clipboard, result, user_data):
        try:
            text = clipboard.read_text_finish(result)
            if text:
                self.input_view.get_buffer().set_text(text)
                self._on_translate(None)
        except Exception as e:
            self.status_lbl.set_label(f"Error pegando: {e}")

    def _on_translate(self, btn):
        text = self._get_input_text().strip()
        if not text:
            return
        src = self.src_combo.get_active_id() or "auto"
        tgt = self.tgt_combo.get_active_id() or "es"
        self.config.set("target_language", tgt)
        self.status_lbl.set_label("⟳  Traduciendo...")

        def do_translate():
            try:
                result, detected = self.translator.translate(text, src, tgt)
                GLib.idle_add(self._on_translate_done, result, detected, None)
            except Exception as e:
                GLib.idle_add(self._on_translate_done, None, None, str(e))

        threading.Thread(target=do_translate, daemon=True).start()

    def _on_translate_done(self, result, detected, error):
        if error:
            self.status_lbl.set_label(f"✗  {error}")
        else:
            self._set_output_text(result)
            lang_name = LANGUAGES.get(detected, detected)
            self.detected_lbl.set_label(f"Detectado: {lang_name}")
            self.status_lbl.set_label("✓  Traducción completada")
            if self.on_done:
                self.on_done(self._get_input_text(), result)

    def _copy_output(self, btn):
        text = self._get_output_text()
        if not text:
            return
        # GTK4 clipboard write
        clipboard = Gdk.Display.get_default().get_clipboard()
        # Use subprocess as reliable fallback
        import subprocess
        try:
            subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True)
            self.status_lbl.set_label("✓  Copiado al portapapeles")
        except Exception:
            try:
                subprocess.run(["xsel", "--clipboard", "--input"], input=text.encode(), check=True)
                self.status_lbl.set_label("✓  Copiado al portapapeles")
            except Exception as e:
                self.status_lbl.set_label(f"✗  {e}")

    def _replace_in_app(self, btn):
        text = self._get_output_text()
        if not text:
            return
        if self.translator.replace_text_in_app(text):
            self.status_lbl.set_label("✓  Texto escrito en la app")
        else:
            self.status_lbl.set_label("✗  Instala xdotool: sudo apt install xdotool")

    def paste_and_translate(self):
        self._paste_text(None)
