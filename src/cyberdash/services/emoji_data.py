"""Emoji Data Manager - Handles emoji data with multilingual search"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import Counter


class EmojiDataManager:
    """Manages emoji data, search, and top used"""
    
    # Category definitions (WhatsApp/Instagram style)
    CATEGORIES = {
        "recent": "Recientes",
        "smileys": "Caras",
        "animals": "Animales",
        "food": "Comida",
        "activities": "Actividades",
        "travel": "Viajes",
        "objects": "Objetos",
        "symbols": "Símbolos",
        "flags": "Banderas",
        "ascii": "ASCII Art",
    }
    
    # Mapping to emoji categories
    EMOJI_CATEGORY_MAP = {
        "recent": [],
        "smileys": [
            "😀", "😃", "😄", "😁", "😆", "😅", "🤣", "😂", "🙂", "🙃",
            "😉", "😊", "😇", "🥰", "😍", "🤩", "😘", "😗", "☺️", "😚",
            "😙", "🥲", "😋", "😛", "😜", "🤪", "😝", "🤑", "🤗", "🤭",
            "🤫", "🤔", "🤐", "🤨", "😐", "😑", "😶", "😏", "😒", "🙄",
            "😬", "🤥", "😌", "😔", "😪", "🤤", "😴", "😷", "🤒", "🤕",
            "🤢", "🤮", "🤧", "🥵", "🥶", "🥴", "😵", "🤯", "🤠", "🥳",
            "🥸", "😎", "🤓", "🧐", "😕", "😟", "🙁", "☹️", "😮", "😯",
            "😲", "😳", "🥺", "😦", "😧", "😨", "😰", "😥", "😢", "😭",
            "😱", "😖", "😣", "😞", "😓", "😩", "😫", "🥱", "😤", "😡",
            "😠", "🤬", "😈", "👿", "💀", "☠️", "💩", "🤡", "👹", "👺",
            "👻", "👽", "👾", "🤖", "😺", "😸", "😹", "😻", "😼", "😽",
            "🙀", "😿", "😾", "🙈", "🙉", "🙊", "💋", "💌", "💘", "💝",
            "💖", "💗", "💓", "💞", "💕", "💟", "❣️", "💔", "❤", "🧡",
            "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍", "💯", "💢", "💥",
            "💫", "💦", "💨", "🕳️", "💣", "💬", "👁️‍🗨️", "🗨️", "🗯️", "💭",
            "💤", "👋", "🤚", "🖐️", "✋", "🖖", "👌", "🤌", "🤏", "✌️",
            "🤞", "🤟", "🤘", "🤙", "👈", "👉", "👆", "🖕", "👇", "☝️",
            "👍", "👎", "✊", "👊", "🤛", "🤜", "👏", "🙌", "👐", "🤲",
            "🤝", "🙏", "✍️", "💅", "🤳", "💪", "🦾", "🦿", "🦵", "🦶",
            "👂", "🦻", "👃", "🧠", "🫀", "🫁", "🦷", "🦴", "👀", "👁️",
            "👅", "👄"
        ],
        "animals": [
            "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐻‍❄️", "🐨",
            "🐯", "🦁", "🐮", "🐷", "🐸", "🐵", "🙈", "🙉", "🙊", "🐒",
            "🐔", "🐧", "🐦", "🐤", "🐣", "🐥", "🦆", "🦅", "🦉", "🦇",
            "🐺", "🐗", "🐴", "🦄", "🐝", "🪱", "🐛", "🦋", "🐌", "🐞",
            "🐜", "🪰", "🪲", "🪳", "🦟", "🦗", "🕷️", "🕸️", "🦂", "🐢",
            "🐍", "🦎", "🦖", "🦕", "🐙", "🦑", "🦐", "🦞", "🦀", "🐡",
            "🐠", "🐟", "🐬", "🐳", "🐋", "🦈", "🐊", "🐅", "🐆", "🦓",
            "🦍", "🦧", "🦣", "🐘", "🦛", "🦏", "🐪", "🐫", "🦒", "🦘",
            "🦬", "🐃", "🐂", "🐄", "🐎", "🐖", "🐏", "🐑", "🦙", "🐐",
            "🦌", "🐕", "🐩", "🦮", "🐕‍🦺", "🐈", "🐈‍⬛", "🪶", "🐓", "🦃",
            "🦤", "🦚", "🦜", "🦢", "🦩", "🕊️", "🐇", "🦝", "🦨", "🦡",
            "🦫", "🦦", "🦥", "🐁", "🐀", "🐿️", "🦔"
        ],
        "food": [
            "🍎", "🍐", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🫐", "🍈",
            "🍒", "🍑", "🥭", "🍍", "🥥", "🥝", "🍅", "🍆", "🥑", "🥦",
            "🥬", "🥒", "🌶️", "🫑", "🌽", "🥕", "🫒", "🧄", "🧅", "🥔",
            "🍠", "🥐", "🥯", "🍞", "🥖", "🥨", "🧀", "🥚", "🍳", "🧈",
            "🥞", "🧇", "🥓", "🥩", "🍗", "🍖", "🦴", "🌭", "🍔", "🍟",
            "🍕", "🫓", "🥪", "🥙", "🧆", "🌮", "🌯", "🫔", "🥗", "🥘",
            "🫕", "🍝", "🍜", "🍲", "🍛", "🍣", "🍱", "🥟", "🦪", "🍤",
            "🍙", "🍚", "🍘", "🍥", "🥠", "🥮", "🍢", "🍡", "🍧", "🍨",
            "🍦", "🥧", "🧁", "🍰", "🎂", "🍮", "🍭", "🍬", "🍫", "🍿",
            "🍩", "🍪", "🌰", "🥜", "🍯", "🥛", "🍼", "☕", "🫖", "🍵",
            "🧃", "🥤", "🧋", "🍶", "🍺", "🍻", "🥂", "🍷", "🥃", "🍸",
            "🍹", "🧉", "🍾", "🧊"
        ],
        "activities": [
            "⚽", "🏀", "🏈", "⚾", "🥎", "🎾", "🏐", "🏉", "🥏", "🎱",
            "🪀", "🏓", "🏸", "🏒", "🏑", "🥍", "🏏", "🪃", "🥅", "⛳",
            "🏹", "🎣", "🤿", "🥊", "🥋", "🎽", "🛹", "🛼", "🛷", "⛸️",
            "🥌", "🎿", "⛷️", "🏂", "🪂", "🏋️", "🤼", "🤸", "⛹️", "🤺",
            "🤾", "🏌️", "🏇", "⛳", "🧘", "🏄", "🏊", "🤽", "🚣", "🧗",
            "🚴", "🚵", "🎪", "🎭", "🎨", "🎬", "🎤", "🎧", "🎼", "🎹",
            "🥁", "🪘", "🎷", "🎺", "🪗", "🎸", "🪕", "🎻", "🪈", "🎲",
            "♟️", "🎯", "🎳", "🎮", "🎰", "🧩", "🧸", "🎁", "🎀", "🎊",
            "🎉", "🎈", "🎌", "🏮", "🪔", "🏮", "🎐", "🧧", "✉️", "📩",
            "📨", "📧", "💌", "📥", "📤", "📦", "🏷️", "📪", "📫", "📬",
            "📭", "📮", "📯", "📜", "📃", "📄", "📑", "🧾", "📊", "📈",
            "📉", "🗒️", "🗓️", "📆", "📅", "🗑️", "📇", "🗃️", "🗳️", "🗄️"
        ],
        "travel": [
            "🚗", "🚕", "🚙", "🚌", "🚎", "🏎️", "🚓", "🚑", "🚒", "🚐",
            "🛻", "🚚", "🚛", "🚜", "🏍️", "🛵", "🚲", "🛴", "🛺", "🚨",
            "🚔", "🚍", "🚘", "🚖", "🚡", "🚠", "🚟", "🚃", "🚋", "🚞",
            "🚝", "🚄", "🚅", "🚈", "🚂", "🚆", "🚇", "🚊", "🚉", "✈️",
            "🛫", "🛬", "🛩️", "💺", "🛰️", "🚀", "🛸", "🚁", "🛶", "⛵",
            "🚤", "🛥️", "🛳️", "⛴️", "🚢", "⚓", "⛽", "🚧", "🚦", "🚥",
            "🚏", "🗺️", "🗿", "🗽", "🗼", "🏰", "🏯", "🏟️", "🎡", "🎢",
            "🎠", "⛲", "⛱️", "🏖️", "🏝️", "🏜️", "🌋", "⛰️", "🏔️", "🗻",
            "🏕️", "⛺", "🛖", "🏠", "🏡", "🏘️", "🏚️", "🏗️", "🏭", "🏢",
            "🏬", "🏣", "🏤", "🏥", "🏦", "🏨", "🏪", "🏫", "🏩", "💒",
            "🏛️", "⛪", "🕌", "🕍", "🛕", "🕋", "⛩️", "🛤️", "🛣️", "🗾"
        ],
        "objects": [
            "⌚", "📱", "📲", "💻", "⌨️", "🖥️", "🖨️", "🖱️", "🖲️", "🕹️",
            "🗜️", "💽", "💾", "💿", "📀", "📼", "📷", "📸", "📹", "🎥",
            "📽️", "🎞️", "📞", "☎️", "📟", "📠", "📺", "📻", "🎙️", "🎚️",
            "🎛️", "🧭", "⏱️", "⏲️", "⏰", "🕰️", "⌛", "⏳", "📡", "🔋",
            "🔌", "💡", "🔦", "🕯️", "🪔", "🧯", "🛢️", "💸", "💵", "💴",
            "💶", "💷", "🪙", "💰", "💳", "💎", "⚖️", "🪜", "🧰", "🪛",
            "🔧", "🔨", "⚒️", "🛠️", "⛏️", "🪚", "🔩", "⚙️", "🪤", "🧱",
            "⛓️", "🧲", "🔫", "💣", "🧨", "🪓", "🔪", "🗡️", "⚔️", "🛡️",
            "🚬", "⚰️", "🪦", "⚱️", "🏺", "🔮", "📿", "🧿", "💈", "⚗️",
            "🔭", "🔬", "🕳️", "🩹", "🩺", "💊", "💉", "🩸", "🧬", "🦠",
            "🧫", "🧪", "🌡️", "🧹", "🪠", "🧺", "🧻", "🚽", "🚰", "🚿"
        ],
        "symbols": [
            "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔",
            "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟", "☮️",
            "✝️", "☪️", "🕉️", "☸️", "✡️", "🔯", "🕎", "☯️", "☦️", "🛐",
            "⛎", "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐",
            "♑", "♒", "♓", "🆔", "⚛️", "🉑", "☢️", "☣️", "📴", "📳",
            "🈶", "🈚", "🈸", "🈺", "🈷️", "✴️", "🆚", "💮", "🉐", "㊙️",
            "㊗️", "🈴", "🈵", "🈹", "🈲", "🅰️", "🅱️", "🆎", "🆑", "🅾️",
            "🆘", "❌", "⭕", "🛑", "⛔", "📛", "🚫", "💯", "💢", "♨️",
            "🚷", "🚯", "🚳", "🚱", "🔞", "📵", "🚭", "❗", "❕", "❓",
            "❔", "‼️", "⁉️", "🔅", "🔆", "〽️", "⚠️", "🚸", "🔱", "⚜️",
            "🔰", "♻️", "✅", "🈯", "💹", "❇️", "✳️", "❎", "🌐", "💠",
            "Ⓜ️", "🌀", "💤", "🏧", "🚾", "♿", "🅿️", "🛗", "🈳", "🈂️"
        ],
        "flags": [
            "🏳️", "🏴", "🏴‍☠️", "🏁", "🚩", "🎌", "🏳️‍🌈", "🏳️‍⚧️", "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "🇺🇸", "🇬🇧", "🇪🇸", "🇫🇷", "🇩🇪",
            "🇮🇹", "🇵🇹", "🇷🇺", "🇯🇵", "🇰🇷", "🇨🇳", "🇦🇪", "🇸🇦", "🇮🇳",
            "🇧🇷", "🇲🇽", "🇨🇦", "🇦🇺", "🇿🇦", "🇳🇬", "🇪🇬", "🇹🇷", "🇫🇮",
            "🇸🇪", "🇳🇴", "🇩🇰", "🇳🇱", "🇧🇪", "🇨🇭", "🇦🇹", "🇵🇱", "🇬🇷",
            "🇮🇪", "🇳🇿", "🇦🇷", "🇨🇴", "🇻🇪", "🇵🇪", "🇨🇱", "🇵🇾", "🇺🇾",
        ],
        "ascii": []
    }
    
    def __init__(self):
        self.data_dir = Path.home() / ".config" / "cyberdash"
        self.top_used_file = self.data_dir / "top_used.json"
        self.search_index_file = self.data_dir / "search_index.json"
        
        self.top_used: List[str] = []
        self.search_index: Dict[str, List[str]] = {}  # emoji -> search terms
        
        # Keyboard locale
        self.locale = self._detect_locale()
    
    def load(self):
        """Load emoji data and user data"""
        self.load_top_used()
        self.build_search_index()
    
    def _detect_locale(self) -> str:
        """Detect system keyboard locale"""
        import locale
        import os
        
        # Try to get from environment
        lang = os.environ.get('LANG', 'en_US').split('.')[0]
        
        # Check common locales
        if lang.startswith('es'):
            return 'es'
        elif lang.startswith('fr'):
            return 'fr'
        elif lang.startswith('de'):
            return 'de'
        elif lang.startswith('it'):
            return 'it'
        elif lang.startswith('pt'):
            return 'pt'
        elif lang.startswith('ja'):
            return 'ja'
        elif lang.startswith('ko'):
            return 'ko'
        elif lang.startswith('zh'):
            return 'zh'
        elif lang.startswith('ru'):
            return 'ru'
        
        return 'en'
    
    def load_top_used(self):
        """Load most used emojis"""
        if self.top_used_file.exists():
            try:
                with open(self.top_used_file, 'r') as f:
                    data = json.load(f)
                    self.top_used = data.get('top', [])[:20]
            except Exception as e:
                print(f"Error loading top used: {e}")
                self.top_used = []
    
    def save_top_used(self):
        """Save most used emojis"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.top_used_file, 'w') as f:
                json.dump({'top': self.top_used}, f)
        except Exception as e:
            print(f"Error saving top used: {e}")
    
    def add_to_top_used(self, emoji: str):
        """Add emoji to top used"""
        if emoji in self.top_used:
            self.top_used.remove(emoji)
        
        self.top_used.insert(0, emoji)
        self.top_used = self.top_used[:20]
        self.save_top_used()
    
    def build_search_index(self):
        """Build search index for emojis"""
        # Base terms (English)
        base_terms = {
            "😀": ["happy", "smile", "joy", "fun", "laugh"],
            "😂": ["laugh", "cry", "funny", "lol", "crying"],
            "😍": ["love", "heart", "crush", "heart eyes"],
            "🥰": ["love", "hearts", "affection"],
            "😘": ["kiss", "love", "blow kiss"],
            "🤔": ["think", "hmm", "thinking"],
            "😎": ["cool", "sunglasses", "awesome"],
            "😭": ["cry", "sad", "tears", "sobbing"],
            "💀": ["skull", "dead", "death", "kill"],
            "🔥": ["fire", "hot", "lit", "trending"],
            "💯": ["hundred", "perfect", "100", "score"],
            "❤️": ["heart", "love", "red heart"],
            "👍": ["thumbs up", "like", "ok", "good"],
            "👎": ["thumbs down", "dislike", "bad"],
            "🎉": ["party", "confetti", "celebration"],
            "🚀": ["rocket", "space", "launch", "fast"],
            "💡": ["idea", "light bulb", "thinking"],
            "⚠️": ["warning", "alert", "caution"],
            "✅": ["check", "done", "complete", "yes"],
            "❌": ["cross", "no", "cancel", "wrong"],
        }
        
        # Spanish terms
        spanish_terms = {
            "😀": ["feliz", "sonrisa", "alegre", "reír"],
            "😂": ["reír", "llorar", "gracioso", "jaja"],
            "😍": ["amor", "corazón", "enamorado"],
            "🥰": ["amor", "corazones", "cariño"],
            "😘": ["beso", "amor", "beso volador"],
            "🤔": ["pensar", "hmm", "pensando"],
            "😎": ["genial", "gafas", "increíble"],
            "😭": ["llorar", "triste", "lágrimas"],
            "💀": ["cráneo", "muerto", "muerte"],
            "🔥": ["fuego", "caliente", "genial"],
            "💯": ["cien", "perfecto", "puntaje"],
            "❤️": ["corazón", "amor"],
            "👍": ["me gusta", "bien", "ok"],
            "👎": ["no me gusta", "mal"],
            "🎉": ["fiesta", "confeti", "celebrar"],
            "🚀": ["cohete", "espacio", "lanzar"],
            "💡": ["idea", "bombilla"],
            "⚠️": ["advertencia", "alerta"],
            "✅": ["check", "hecho", "sí"],
            "❌": ["cruz", "no", "cancelar"],
        }
        
        # French terms
        french_terms = {
            "😀": ["heureux", "sourire", "joie"],
            "😂": ["rire", "pleurer", "drole"],
            "😍": ["amour", "coeur", "amoureux"],
            "🥰": ["amour", "coeurs", "affection"],
            "😘": ["bisou", "amour", "bisou volé"],
            "🤔": ["penser", "hmm", "réfléchir"],
            "😎": ["cool", "lunettes", "génial"],
            "😭": ["pleurer", "triste", "larmes"],
            "💀": ["crâne", "mort", "tué"],
            "🔥": ["feu", "chaud", "génial"],
            "💯": ["cent", "parfait"],
            "❤️": ["coeur", "amour"],
            "👍": ["j'aime", "bien", "ok"],
            "👎": ["j'aime pas", "mal"],
            "🎉": ["fête", "confettis", "célébrer"],
            "🚀": ["fusée", "espace", "lancer"],
            "💡": ["idée", "ampoule"],
            "⚠️": ["avertissement", "alerte"],
            "✅": ["coché", "fait", "oui"],
            "❌": ["croix", "non", "annuler"],
        }
        
        # German terms
        german_terms = {
            "😀": ["glücklich", "lächeln", "freude"],
            "😂": ["lachen", "weinen", "lustig"],
            "😍": ["liebe", "herz", "verliebt"],
            "🥰": ["liebe", "herzen", "zuneigung"],
            "😘": ["kuss", "liebe", "flughand"],
            "🤔": ["denken", "hmm", "nachdenken"],
            "😎": ["cool", "brille", "toll"],
            "😭": ["weinen", "traurig", "tränen"],
            "💀": ["schädel", "tot", "tod"],
            "🔥": ["feuer", "heiß", "toll"],
            "💯": ["hundert", "perfekt"],
            "❤️": ["herz", "liebe"],
            "👍": ["mag ich", "gut", "ok"],
            "👎": ["mag nicht", "schlecht"],
            "🎉": ["party", "konfetti", "feiern"],
            "🚀": ["rakete", "weltraum", "start"],
            "💡": ["idee", "glühbirne"],
            "⚠️": ["warnung", "alarm"],
            "✅": ["häkchen", "gemacht", "ja"],
            "❌": ["kreuz", "nein", "abbrechen"],
        }
        
        # Combine based on locale
        self.search_index = {}
        
        # Add English terms for all
        for emoji, terms in base_terms.items():
            self.search_index[emoji] = terms.copy()
        
        # Add locale-specific terms
        if self.locale == 'es':
            for emoji, terms in spanish_terms.items():
                if emoji in self.search_index:
                    self.search_index[emoji].extend(terms)
                else:
                    self.search_index[emoji] = terms
        elif self.locale == 'fr':
            for emoji, terms in french_terms.items():
                if emoji in self.search_index:
                    self.search_index[emoji].extend(terms)
                else:
                    self.search_index[emoji] = terms
        elif self.locale == 'de':
            for emoji, terms in german_terms.items():
                if emoji in self.search_index:
                    self.search_index[emoji].extend(terms)
                else:
                    self.search_index[emoji] = terms
    
    def search(self, query: str) -> List[str]:
        """Search emojis by query"""
        if not query:
            return []
        
        query = query.lower()
        results = []
        
        # Search in index
        for emoji, terms in self.search_index.items():
            for term in terms:
                if query in term or term in query:
                    results.append(emoji)
                    break
        
        return results
    
    def get_category_emojis(self, category: str) -> List[str]:
        """Get emojis for a category"""
        if category == "recent":
            return self.top_used if self.top_used else self.EMOJI_CATEGORY_MAP.get("smileys", [])[:20]
        
        return self.EMOJI_CATEGORY_MAP.get(category, [])
    
    def get_categories(self) -> Dict[str, str]:
        """Get all categories"""
        return self.CATEGORIES.copy()
    
    def get_top_used(self) -> List[str]:
        """Get top used emojis"""
        return self.top_used.copy()
