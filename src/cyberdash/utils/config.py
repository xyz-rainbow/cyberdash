"""Configuration Manager"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manages CyberDash configuration"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "cyberdash"
        self.config_file = self.config_dir / "config.json"
        
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return self.get_defaults()
    
    def get_defaults(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "hotkey": "super+.",
            "translator_provider": "mymemory",
            "target_language": "en",
            "api_keys": {
                "google": "",
                "deepl": "",
                "openai": "",
                "claude": "",
                "groq": "",
                "ollama_url": "http://localhost:11434"
            },
            "startup": False,
            "show_top_used": True,
            "max_clipboard": 50,
            "theme": "cyberpunk"
        }
    
    def save(self):
        """Save configuration to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set config value"""
        self.config[key] = value
        self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all config"""
        return self.config.copy()
    
    def update(self, data: Dict[str, Any]):
        """Update multiple config values"""
        self.config.update(data)
        self.save()
