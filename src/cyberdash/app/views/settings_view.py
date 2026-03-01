"""Settings View"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from typing import Callable
from ...services.translator_service import LANGUAGES


class SettingsView(Gtk.Box):
    def __init__(self, config, on_changed: Callable):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.config = config
        self.on_changed = on_changed
        self._setup_ui()

    def _setup_ui(self):
        scroll = Gtk.ScrolledWindow()
        scroll.add_css_class("settings-scroll")
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_start(8)
        box.set_margin_end(8)
        box.set_margin_top(8)
        box.set_margin_bottom(8)

        # ── Hotkey ────────────────────────────────────
        box.append(self._make_group(
            "ATAJO GLOBAL",
            "Requiere keybinder3: sudo apt install gir1.2-keybinder-3.0",
            [("Combinación", "hotkey", "<Super>period", False)]
        ))

        # ── Translator ────────────────────────────────
        lang_group = self._make_group(
            "IDIOMA DESTINO",
            "Idioma por defecto para traducir",
            []
        )
        lang_combo = Gtk.ComboBoxText()
        for code, name in LANGUAGES.items():
            if code != "auto":
                lang_combo.append(code, name)
        lang_combo.set_active_id(self.config.get("target_language", "es"))
        lang_combo.connect("changed", lambda c: self.config.set("target_language", c.get_active_id()))
        lang_group.append(lang_combo)
        box.append(lang_group)

        # ── API Keys ──────────────────────────────────
        api_keys = self.config.get("api_keys", {})

        box.append(self._make_group(
            "OPENAI API KEY",
            "Para usar GPT como traductor",
            [("API Key", "_openai_key", api_keys.get("openai", ""), True)]
        ))

        box.append(self._make_group(
            "OLLAMA URL",
            "URL local de Ollama (defecto: localhost:11434)",
            [("URL", "_ollama_url", api_keys.get("ollama_url", "http://localhost:11434"), False)]
        ))

        box.append(self._make_group(
            "LIBRETRANSLATE",
            "URL e API key de LibreTranslate",
            [
                ("URL", "_libre_url", api_keys.get("libretranslate_url", "https://libretranslate.com"), False),
                ("API Key", "_libre_key", api_keys.get("libretranslate_key", ""), True),
            ]
        ))

        # ── Save button ───────────────────────────────
        save_btn = Gtk.Button(label="💾  GUARDAR CONFIGURACIÓN")
        save_btn.add_css_class("primary-btn")
        save_btn.set_halign(Gtk.Align.CENTER)
        save_btn.set_margin_top(16)
        save_btn.connect("clicked", self._on_save)
        box.append(save_btn)

        self._save_lbl = Gtk.Label(label="")
        self._save_lbl.add_css_class("detected-lang")
        self._save_lbl.set_halign(Gtk.Align.CENTER)
        box.append(self._save_lbl)

        # ── About ─────────────────────────────────────
        about = Gtk.Label()
        about.set_markup(
            '\n<span foreground="#1a5c1a" font="Courier New 10">'
            "CyberDash v1.0 — Emoji Picker para Linux\n"
            "GTK4 + libadwaita — Estilo Cyberpunk\n"
            "Super+. para abrir/cerrar"
            "</span>"
        )
        about.set_justify(Gtk.Justification.CENTER)
        about.set_margin_top(20)
        box.append(about)

        scroll.set_child(box)
        self.append(scroll)

        # Store entry refs for saving
        self._entries = {}

    def _make_group(self, title: str, desc: str, fields: list) -> Gtk.Box:
        group = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        group.add_css_class("settings-group")
        group.set_margin_top(4)
        group.set_margin_bottom(4)

        lbl = Gtk.Label(label=title)
        lbl.add_css_class("settings-label")
        lbl.set_halign(Gtk.Align.START)
        group.append(lbl)

        if desc:
            dlbl = Gtk.Label(label=desc)
            dlbl.add_css_class("status-text")
            dlbl.set_halign(Gtk.Align.START)
            dlbl.set_wrap(True)
            group.append(dlbl)

        for field_label, key, default, secret in fields:
            entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            entry_box.add_css_class("settings-entry")

            entry = Gtk.Entry()
            entry.set_text(self.config.get(key, default) if not key.startswith("_") else default)
            entry.set_hexpand(True)
            entry.set_visibility(not secret)
            entry.set_placeholder_text(field_label)
            entry_box.append(entry)

            self._entries[key] = (entry, key)
            group.append(entry_box)

        return group

    def _on_save(self, btn):
        api_keys = self.config.get("api_keys", {})

        for key, (entry, _) in self._entries.items():
            val = entry.get_text()
            if key == "hotkey":
                self.config.set("hotkey", val)
            elif key == "_openai_key":
                api_keys["openai"] = val
            elif key == "_ollama_url":
                api_keys["ollama_url"] = val
            elif key == "_libre_url":
                api_keys["libretranslate_url"] = val
            elif key == "_libre_key":
                api_keys["libretranslate_key"] = val

        self.config.set("api_keys", api_keys)
        self._save_lbl.set_label("✓  Guardado")
        if self.on_changed:
            self.on_changed()
