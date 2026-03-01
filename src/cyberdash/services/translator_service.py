"""Translator Service - Multiple providers"""

import subprocess
import os
from typing import Tuple, Dict, List


LANGUAGES: Dict[str, str] = {
    "auto": "Auto-detectar",
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
    "uk": "Українська",
    "cs": "Čeština",
    "el": "Ελληνικά",
    "he": "עברית",
    "th": "ไทย",
    "vi": "Tiếng Việt",
    "id": "Bahasa Indonesia",
    "hu": "Magyar",
    "ro": "Română",
}


class TranslatorService:
    LANGUAGES = LANGUAGES

    def __init__(self, config):
        self.config = config
        self.provider = config.get("translator_provider", "mymemory")
        self.last_detected = "en"

    def reload_config(self):
        self.provider = self.config.get("translator_provider", "mymemory")

    def set_provider(self, provider: str):
        self.provider = provider
        self.config.set("translator_provider", provider)

    def detect_language(self, text: str) -> str:
        """Heuristic language detection"""
        if not text:
            return "en"

        def ratio(start, end):
            count = sum(1 for c in text if start <= c <= end)
            return count / max(len(text), 1)

        if ratio("\u3040", "\u30FF") > 0.1:
            return "ja"
        if ratio("\uAC00", "\uD7AF") > 0.1:
            return "ko"
        if ratio("\u4E00", "\u9FFF") > 0.1:
            return "zh"
        if ratio("\u0600", "\u06FF") > 0.1:
            return "ar"
        if ratio("\u0400", "\u04FF") > 0.1:
            return "ru"

        words = set(text.lower().split())
        if len(words & {"el","la","los","las","de","que","es","en","un","una","por","con","para","se","lo"}) >= 2:
            return "es"
        if len(words & {"le","la","les","de","des","un","une","et","est","que","qui","dans","je","tu"}) >= 2:
            return "fr"
        if len(words & {"der","die","das","und","ist","ein","eine","von","mit","den","dem","ich","du"}) >= 2:
            return "de"
        return "en"

    def translate(self, text: str, source: str = "auto", target: str = "es") -> Tuple[str, str]:
        """Translate text. Returns (translated_text, detected_source_lang)"""
        if not text.strip():
            return "", source

        if source == "auto":
            source = self.detect_language(text)
            self.last_detected = source

        if source == target:
            return text, source

        try:
            if self.provider == "mymemory":
                return self._mymemory(text, source, target)
            elif self.provider == "libretranslate":
                return self._libretranslate(text, source, target)
            elif self.provider == "openai":
                return self._openai(text, source, target)
            elif self.provider == "ollama":
                return self._ollama(text, source, target)
            else:
                return self._mymemory(text, source, target)
        except Exception as e:
            raise RuntimeError(f"{self.provider}: {e}")

    def _mymemory(self, text: str, source: str, target: str) -> Tuple[str, str]:
        import urllib.request
        import urllib.parse
        import json

        params = urllib.parse.urlencode({"q": text, "langpair": f"{source}|{target}"})
        url = f"https://api.mymemory.translated.net/get?{params}"

        req = urllib.request.Request(url, headers={"User-Agent": "CyberDash/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        if data.get("responseStatus") == 200:
            return data["responseData"]["translatedText"], source
        raise RuntimeError(data.get("responseDetails", "MyMemory error"))

    def _libretranslate(self, text: str, source: str, target: str) -> Tuple[str, str]:
        import urllib.request
        import urllib.parse
        import json

        api_keys = self.config.get("api_keys", {})
        url = api_keys.get("libretranslate_url", "https://libretranslate.com")
        key = api_keys.get("libretranslate_key", "")

        payload = {"q": text, "source": source, "target": target, "format": "text"}
        if key:
            payload["api_key"] = key

        data_bytes = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{url}/translate",
            data=data_bytes,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())

        if "translatedText" in result:
            return result["translatedText"], source
        raise RuntimeError(result.get("error", "LibreTranslate error"))

    def _openai(self, text: str, source: str, target: str) -> Tuple[str, str]:
        import urllib.request
        import json

        api_key = self.config.get("api_keys", {}).get("openai", "")
        if not api_key:
            raise RuntimeError("OpenAI API key not configured")

        src_name = LANGUAGES.get(source, source)
        tgt_name = LANGUAGES.get(target, target)
        prompt = f"Translate from {src_name} to {tgt_name}. Return ONLY the translation:\n\n{text}"

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())

        return result["choices"][0]["message"]["content"].strip(), source

    def _ollama(self, text: str, source: str, target: str) -> Tuple[str, str]:
        import urllib.request
        import json

        url = self.config.get("api_keys", {}).get("ollama_url", "http://localhost:11434")
        src_name = LANGUAGES.get(source, source)
        tgt_name = LANGUAGES.get(target, target)
        prompt = f"Translate from {src_name} to {tgt_name}. Return ONLY the translation:\n\n{text}"

        payload = {"model": "llama2", "prompt": prompt, "stream": False}
        req = urllib.request.Request(
            f"{url}/api/generate",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())

        if "response" in result:
            return result["response"].strip(), source
        raise RuntimeError("Ollama error")

    def replace_text_in_app(self, text: str) -> bool:
        """Type text into previously focused window"""
        try:
            subprocess.run(
                ["xdotool", "type", "--clearmodifiers", "--", text],
                timeout=5,
                capture_output=True,
            )
            return True
        except Exception:
            return False
