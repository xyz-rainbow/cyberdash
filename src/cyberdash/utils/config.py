"""Configuration Manager"""

import json
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "cyberdash"
        self.config_file = self.config_dir / "config.json"
        self.config = self._load()

    def _defaults(self) -> Dict[str, Any]:
        return {
            "hotkey": "super+period",
            "translator_provider": "mymemory",
            "target_language": "es",
            "api_keys": {
                "openai": "",
                "ollama_url": "http://localhost:11434",
                "libretranslate_url": "https://libretranslate.com",
                "libretranslate_key": "",
            },
            "auto_paste": True,
            "max_clipboard": 50,
        }

    def _load(self) -> Dict[str, Any]:
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    defaults = self._defaults()
                    defaults.update(data)
                    return defaults
            except Exception:
                pass
        return self._defaults()

    def save(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Config save error: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        self.config[key] = value
        self.save()

    def get_all(self) -> Dict[str, Any]:
        return self.config.copy()
