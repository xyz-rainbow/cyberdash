"""Clipboard Manager - Clipboard history and management"""

import json
import os
import subprocess
from pathlib import Path
from typing import List, Optional


class ClipboardManager:
    """Manages clipboard history"""
    
    def __init__(self):
        self.history: List[str] = []
        self.max_history = 50
        self.config_dir = Path.home() / ".config" / "cyberdash"
        self.history_file = self.config_dir / "clipboard_history.json"
    
    def load(self):
        """Load clipboard history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])[:self.max_history]
            except Exception as e:
                print(f"Error loading clipboard history: {e}")
                self.history = []
    
    def save(self):
        """Save clipboard history to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.history_file, 'w') as f:
                json.dump({'history': self.history}, f)
        except Exception as e:
            print(f"Error saving clipboard history: {e}")
    
    def add(self, text: str):
        """Add item to clipboard history"""
        if text and text.strip():
            # Remove if already exists
            if text in self.history:
                self.history.remove(text)
            
            # Add to beginning
            self.history.insert(0, text)
            
            # Trim to max size
            self.history = self.history[:self.max_history]
            
            # Save
            self.save()
    
    def get_history(self) -> List[str]:
        """Get clipboard history"""
        return self.history.copy()
    
    def copy_to_clipboard(self, text: str):
        """Copy text to system clipboard using shell command"""
        # Use xclip or xsel as fallback
        try:
            import subprocess
            # Try xclip first
            subprocess.run(['xclip', '-selection', 'clipboard', '-i'], 
                         input=text.encode(), check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            try:
                # Try xsel
                subprocess.run(['xsel', '--clipboard', '-i'], 
                             input=text.encode(), check=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                # Use wl-paste for Wayland
                try:
                    subprocess.run(['wl-copy'], input=text.encode(), check=True)
                except:
                    print("Warning: No clipboard tool available")
        
        # Also add to history
        self.add(text)
    
    def clear(self):
        """Clear clipboard history"""
        self.history = []
        self.save()
    
    def remove_item(self, text: str):
        """Remove specific item from history"""
        if text in self.history:
            self.history.remove(text)
            self.save()
