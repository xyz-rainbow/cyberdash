"""Stickers View - Stickers + GIF search (Giphy/Tenor)"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
import json
import threading
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Callable, List, Tuple


DEFAULT_STICKERS: List[Tuple[str, str]] = [
    ("😺", "cat"), ("🐱", "cat2"), ("🐶", "dog"), ("🦊", "fox"),
    ("🐼", "panda"), ("🦁", "lion"), ("🐸", "frog"), ("🦄", "unicorn"),
    ("🌈", "rainbow"), ("🔥", "fire"), ("💯", "100"), ("😂", "laugh"),
    ("🤣", "rofl"), ("😍", "love"), ("🤔", "think"), ("😎", "cool"),
    ("🥳", "party"), ("🚀", "rocket"), ("💡", "idea"), ("⚡", "zap"),
    ("💀", "skull"), ("👻", "ghost"), ("🤖", "robot"), ("👾", "alien"),
    ("🎮", "game"), ("🎯", "target"), ("🏆", "trophy"), ("💎", "gem"),
    ("🧠", "brain"), ("⭐", "star"),
]


class StickersView(Gtk.Box):
    def __init__(self, on_select: Callable[[str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.on_select = on_select
        self.stickers = list(DEFAULT_STICKERS)
        self.current_provider = "giphy"
        self.stickers_file = Path.home() / ".config" / "cyberdash" / "stickers.json"
        self._setup_ui()
        self._load_user_stickers()
        self._show_stickers(None)

    def _setup_ui(self):
        # Tab bar
        tabs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        tabs.set_homogeneous(True)
        tabs.set_margin_start(8)
        tabs.set_margin_end(8)
        tabs.set_margin_top(8)
        tabs.set_margin_bottom(4)

        self.stickers_btn = Gtk.Button(label="📦  STICKERS")
        self.stickers_btn.add_css_class("cat-btn")
        self.stickers_btn.connect("clicked", self._show_stickers)

        self.gifs_btn = Gtk.Button(label="🎬  GIFS")
        self.gifs_btn.add_css_class("cat-btn")
        self.gifs_btn.connect("clicked", self._show_gifs)

        tabs.append(self.stickers_btn)
        tabs.append(self.gifs_btn)
        self.append(tabs)

        # GIF search bar
        self.search_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.search_bar.set_margin_start(8)
        self.search_bar.set_margin_end(8)
        self.search_bar.set_margin_bottom(4)
        self.search_bar.set_visible(False)

        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Buscar GIFs...")
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("activate", self._search_gifs)

        search_btn = Gtk.Button(label="🔍")
        search_btn.add_css_class("swap-btn")
        search_btn.connect("clicked", self._search_gifs)

        self.provider_combo = Gtk.ComboBoxText()
        self.provider_combo.append("giphy", "Giphy")
        self.provider_combo.append("tenor", "Tenor")
        self.provider_combo.set_active_id("giphy")
        self.provider_combo.connect("changed", lambda c: setattr(self, "current_provider", c.get_active_id()))

        self.search_bar.append(self.search_entry)
        self.search_bar.append(search_btn)
        self.search_bar.append(self.provider_combo)
        self.append(self.search_bar)

        # Status
        self.status_lbl = Gtk.Label(label="")
        self.status_lbl.add_css_class("detected-lang")
        self.status_lbl.set_halign(Gtk.Align.CENTER)
        self.status_lbl.set_margin_bottom(4)
        self.append(self.status_lbl)

        # Content
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        self.flow = Gtk.FlowBox()
        self.flow.set_homogeneous(True)
        self.flow.set_min_children_per_line(5)
        self.flow.set_max_children_per_line(6)
        self.flow.set_row_spacing(4)
        self.flow.set_column_spacing(4)
        self.flow.set_margin_start(8)
        self.flow.set_margin_end(8)
        self.flow.set_margin_top(4)
        self.flow.set_margin_bottom(8)
        self.flow.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll.set_child(self.flow)
        self.append(scroll)

    def _clear_flow(self):
        while True:
            child = self.flow.get_first_child()
            if child is None:
                break
            self.flow.remove(child)

    def _set_tab(self, tab: str):
        if tab == "stickers":
            self.stickers_btn.add_css_class("active")
            self.gifs_btn.remove_css_class("active")
            self.search_bar.set_visible(False)
        else:
            self.gifs_btn.add_css_class("active")
            self.stickers_btn.remove_css_class("active")
            self.search_bar.set_visible(True)

    # ── Stickers ───────────────────────────────────────

    def _show_stickers(self, btn):
        self._set_tab("stickers")
        self.status_lbl.set_label("")
        self._clear_flow()
        for sticker, name in self.stickers:
            b = Gtk.Button(label=sticker)
            b.add_css_class("pinned-btn")
            b.set_size_request(58, 58)
            b.set_tooltip_text(name)
            b.connect("clicked", lambda w, s=sticker: self.on_select and self.on_select(s))
            child = Gtk.FlowBoxChild()
            child.set_child(b)
            self.flow.append(child)

    def _load_user_stickers(self):
        if self.stickers_file.exists():
            try:
                with open(self.stickers_file, "r") as f:
                    extra = json.load(f).get("stickers", [])
                    if extra:
                        self.stickers.extend(extra)
            except Exception:
                pass

    # ── GIFs ───────────────────────────────────────────

    def _show_gifs(self, btn):
        self._set_tab("gifs")
        self._clear_flow()
        self._fetch_async(None, trending=True)

    def _search_gifs(self, widget):
        query = self.search_entry.get_text().strip()
        if not query:
            self._fetch_async(None, trending=True)
        else:
            self.status_lbl.set_label("🔄 Buscando...")
            self._fetch_async(query, trending=False)

    def _fetch_async(self, query, trending: bool):
        self.status_lbl.set_label("🔄 Cargando...")
        threading.Thread(
            target=self._fetch_gifs,
            args=(query, trending),
            daemon=True
        ).start()

    def _fetch_gifs(self, query, trending: bool):
        """Network call — runs in background thread"""
        import json as _json
        try:
            if self.current_provider == "giphy":
                endpoint = "trending" if trending else "search"
                params = {"api_key": "dc6zaTOxFJmzC", "limit": 20, "rating": "g"}
                if not trending:
                    params["q"] = query
                url = f"https://api.giphy.com/v1/gifs/{endpoint}?{urllib.parse.urlencode(params)}"
                with urllib.request.urlopen(url, timeout=10) as r:
                    data = _json.loads(r.read())
                gifs = []
                for item in data.get("data", []):
                    try:
                        gifs.append({
                            "url": item["images"]["fixed_height"]["url"],
                            "preview": item["images"]["fixed_width_small"]["url"],
                            "title": item.get("title", "GIF"),
                        })
                    except (KeyError, TypeError):
                        continue
            else:  # Tenor
                endpoint = "featured" if trending else "search"
                params = {"key": "AIzaSyAyimkuYQYF_FXVALexPuGQctUWRURdCYQ", "limit": 20, "contentfilter": "medium"}
                if not trending:
                    params["q"] = query
                url = f"https://tenor.googleapis.com/v2/{endpoint}?{urllib.parse.urlencode(params)}"
                with urllib.request.urlopen(url, timeout=10) as r:
                    data = _json.loads(r.read())
                gifs = []
                for item in data.get("results", []):
                    try:
                        gifs.append({
                            "url": item["media_formats"]["gif"]["url"],
                            "preview": item["media_formats"]["tinygif"]["url"],
                            "title": item.get("content_description", "GIF"),
                        })
                    except (KeyError, TypeError):
                        continue

            GLib.idle_add(self._display_gifs, gifs)
        except Exception as e:
            GLib.idle_add(self.status_lbl.set_label, f"✗  {e}")

    def _display_gifs(self, gifs: list):
        self._clear_flow()
        self.status_lbl.set_label("")
        if not gifs:
            lbl = Gtk.Label(label="No se encontraron GIFs")
            lbl.add_css_class("empty-label")
            child = Gtk.FlowBoxChild()
            child.set_child(lbl)
            self.flow.append(child)
            return

        for gif in gifs:
            btn = Gtk.Button(label="GIF")
            btn.add_css_class("emoji-btn")
            btn.set_size_request(90, 70)
            btn.set_tooltip_text(gif.get("title", ""))
            url = gif["url"]
            btn.connect("clicked", lambda w, u=url: self.on_select and self.on_select(u))
            child = Gtk.FlowBoxChild()
            child.set_child(btn)
            self.flow.append(child)
            # Load preview in background
            threading.Thread(
                target=self._load_preview, args=(btn, gif["preview"]), daemon=True
            ).start()

    def _load_preview(self, btn: Gtk.Button, preview_url: str):
        try:
            from gi.repository import GdkPixbuf
            with urllib.request.urlopen(preview_url, timeout=5) as r:
                data = r.read()
            loader = GdkPixbuf.PixbufLoader()
            loader.write(data)
            loader.close()
            pixbuf = loader.get_pixbuf()
            if pixbuf:
                scaled = pixbuf.scale_simple(90, 70, GdkPixbuf.InterpType.BILINEAR)
                GLib.idle_add(self._set_img, btn, scaled)
        except Exception:
            pass

    def _set_img(self, btn: Gtk.Button, pixbuf):
        img = Gtk.Image()
        img.set_from_pixbuf(pixbuf)
        btn.set_child(img)
