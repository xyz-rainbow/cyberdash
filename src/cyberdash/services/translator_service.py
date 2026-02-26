"""Translator Service - Multiple translation API providers"""

import json
import requests
from typing import Optional, Dict, List, Tuple
from enum import Enum


class TranslationProvider(Enum):
    """Available translation providers"""
    MYMEMORY = "mymemory"
    LIBRETRANSLATE = "libretranslate"
    GOOGLE = "google"
    DEEPL = "deepl"
    OPENAI = "openai"
    CLAUDE = "claude"
    GROQ = "groq"
    OLLAMA = "ollama"


class TranslatorService:
    """Translation service with multiple providers"""
    
    # Language codes
    LANGUAGES = {
        "auto": "Auto-detect",
        "en": "English",
        "es": "Español",
        "fr": "Français",
        "de": "Deutsch",
        "it": "Italiano",
        "pt": "Português",
        "ru": "Русский",
        "ja": "日本語",
        "ko": "한국어",
        "zh": "中文",
        "ar": "العربية",
        "hi": "हिन्दी",
        "tr": "Türkçe",
        "pl": "Polski",
        "nl": "Nederlands",
        "sv": "Svenska",
        "da": "Dansk",
        "fi": "Suomi",
        "no": "Norsk",
        "cs": "Čeština",
        "el": "Ελληνικά",
        "he": "עברית",
        "th": "ไทย",
        "vi": "Tiếng Việt",
        "id": "Bahasa Indonesia",
        "ms": "Bahasa Melayu",
        "uk": "Українська",
        "hu": "Magyar",
        "ro": "Română",
    }
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.provider = TranslationProvider.MYMEMORY
        self.api_keys = {}
        self.last_detected_lang = "en"
    
    def reload_config(self):
        """Reload configuration"""
        self.load_api_keys()
    
    def load_api_keys(self):
        """Load API keys from config"""
        config = self.config.get_all()
        api_keys = config.get('api_keys', {})
        
        self.api_keys = {
            'google': api_keys.get('google', ''),
            'deepl': api_keys.get('deepl', ''),
            'openai': api_keys.get('openai', ''),
            'claude': api_keys.get('claude', ''),
            'groq': api_keys.get('groq', ''),
            'ollama': api_keys.get('ollama_url', 'http://localhost:11434'),
        }
        
        # Set provider
        provider_name = config.get('translator_provider', 'mymemory')
        try:
            self.provider = TranslationProvider(provider_name)
        except ValueError:
            self.provider = TranslationProvider.MYMEMORY
    
    def set_provider(self, provider: str):
        """Set translation provider"""
        try:
            self.provider = TranslationProvider(provider)
        except ValueError:
            self.provider = TranslationProvider.MYMEMORY
    
    def get_languages(self) -> List[Tuple[str, str]]:
        """Get list of available languages"""
        return list(self.LANGUAGES.items())
    
    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        # Simple heuristic-based detection
        # For production, use a proper language detection library
        if not text:
            return "en"
        
        # Check for common patterns
        japanese_chars = sum(1 for c in text if '\u3040' <= c <= '\u309F' or '\u30A0' <= c <= '\u30FF')
        korean_chars = sum(1 for c in text if '\uAC00' <= c <= '\uD7AF')
        chinese_chars = sum(1 for c in text if '\u4E00' <= c <= '\u9FFF')
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        russian_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
        
        total = len(text)
        
        if japanese_chars / total > 0.1:
            return "ja"
        if korean_chars / total > 0.1:
            return "ko"
        if chinese_chars / total > 0.1:
            return "zh"
        if arabic_chars / total > 0.1:
            return "ar"
        if russian_chars / total > 0.1:
            return "ru"
        
        # Check for Spanish common words
        spanish_words = ['el', 'la', 'los', 'las', 'de', 'que', 'es', 'en', 'un', 'una', 'por', 'con', 'para']
        words = text.lower().split()
        spanish_count = sum(1 for w in words if w in spanish_words)
        
        if spanish_count >= 2:
            return "es"
        
        # Check for French
        french_words = ['le', 'la', 'les', 'de', 'des', 'un', 'une', 'et', 'est', 'que', 'qui', 'dans']
        french_count = sum(1 for w in words if w in french_words)
        
        if french_count >= 2:
            return "fr"
        
        # Check for German
        german_words = ['der', 'die', 'das', 'und', 'ist', 'ein', 'eine', 'von', 'mit', 'den', 'dem']
        german_count = sum(1 for w in words if w in german_words)
        
        if german_count >= 2:
            return "de"
        
        return "en"
    
    def translate(self, text: str, source: str = "auto", target: str = "en") -> Tuple[str, str]:
        """Translate text using selected provider"""
        if not text.strip():
            return "", ""
        
        # Auto-detect source
        if source == "auto":
            source = self.detect_language(text)
            self.last_detected_lang = source
        
        # Skip if same language
        if source == target:
            return text, source
        
        # Route to provider
        try:
            if self.provider == TranslationProvider.MYMEMORY:
                return self._translate_mymemory(text, source, target)
            elif self.provider == TranslationProvider.LIBRETRANSLATE:
                return self._translate_libretranslate(text, source, target)
            elif self.provider == TranslationProvider.OPENAI:
                return self._translate_openai(text, source, target)
            elif self.provider == TranslationProvider.OLLAMA:
                return self._translate_ollama(text, source, target)
            else:
                # Default to MyMemory
                return self._translate_mymemory(text, source, target)
        except Exception as e:
            print(f"Translation error: {e}")
            return f"[Error: {str(e)}]", source
    
    def _translate_mymemory(self, text: str, source: str, target: str) -> Tuple[str, str]:
        """Translate using MyMemory API (free, no key required)"""
        url = "https://api.mymemory.translated.net/get"
        params = {
            'q': text,
            'langpair': f"{source}|{target}"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('responseStatus') == 200:
            translated = data.get('responseData', {}).get('translatedText', text)
            return translated, source
        else:
            raise Exception(data.get('responseDetails', 'Translation failed'))
    
    def _translate_libretranslate(self, text: str, source: str, target: str) -> Tuple[str, str]:
        """Translate using LibreTranslate"""
        url = "https://libretranslate.com/translate"
        
        data = {
            'q': text,
            'source': source,
            'target': target,
            'format': 'text'
        }
        
        # Add API key if available
        api_key = self.api_keys.get('libretranslate', '')
        if api_key:
            data['api_key'] = api_key
        
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if 'translatedText' in result:
            return result['translatedText'], source
        else:
            raise Exception(result.get('error', 'Translation failed'))
    
    def _translate_openai(self, text: str, source: str, target: str) -> Tuple[str, str]:
        """Translate using OpenAI API"""
        api_key = self.api_keys.get('openai', '')
        if not api_key:
            raise Exception("OpenAI API key not configured")
        
        # Map language codes to names
        source_name = self.LANGUAGES.get(source, source)
        target_name = self.LANGUAGES.get(target, target)
        
        prompt = f"Translate the following text from {source_name} to {target_name}:\n\n{text}"
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 1000
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        result = response.json()
        
        if 'choices' in result:
            return result['choices'][0]['message']['content'], source
        else:
            raise Exception(result.get('error', {}).get('message', 'OpenAI translation failed'))
    
    def _translate_ollama(self, text: str, source: str, target: str) -> Tuple[str, str]:
        """Translate using local Ollama"""
        url = self.api_keys.get('ollama_url', 'http://localhost:11434')
        
        source_name = self.LANGUAGES.get(source, source)
        target_name = self.LANGUAGES.get(target, target)
        
        prompt = f"Translate this text from {source_name} to {target_name}. Only return the translation, nothing else:\n\n{text}"
        
        data = {
            'model': 'llama2',
            'prompt': prompt,
            'stream': False
        }
        
        response = requests.post(f"{url}/api/generate", json=data, timeout=60)
        result = response.json()
        
        if 'response' in result:
            return result['response'].strip(), source
        else:
            raise Exception("Ollama translation failed")
    
    def replace_text_in_app(self, text: str) -> bool:
        """Replace selected text in active application"""
        # This requires platform-specific implementation
        # For X11: use xdotool
        # For Wayland: use wtype or ydotool
        
        import os
        import subprocess
        
        # Detect display server
        wayland = os.environ.get('WAYLAND_DISPLAY')
        
        try:
            if wayland:
                # Try wtype for Wayland
                proc = subprocess.Popen(['wtype', '-'], stdin=subprocess.PIPE)
                proc.communicate(text.encode())
                return proc.returncode == 0
            else:
                # Try xdotool for X11
                subprocess.run(['xdotool', 'type', '--clearmodifiers', text], check=True)
                return True
        except FileNotFoundError:
            # Try xdotool as fallback
            try:
                subprocess.run(['xdotool', 'type', '--clearmodifiers', text], check=True)
                return True
            except:
                pass
        
        return False
