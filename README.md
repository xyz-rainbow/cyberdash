# CyberDash - Advanced Emoji Picker for Linux
# Cyberpunk Style - GTK4 + libadwaita

## Installation

### From Source (Debian/Ubuntu)

```bash
# Install dependencies
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-libadwaita-1.0 libgirepository1.0-dev python3-pip python3-requests

# Install cyberdash
pip install .

# Or install in development mode
pip install -e .
```

### Build .deb Package

```bash
# Install build dependencies
sudo apt install dpkg-dev python3-all debhelper-compat

# Build package
dpkg-buildpackage -b -us -uc

# Install
sudo dpkg -i ../cyberdash_*.deb
```

## Features

- 🎭 Emoji picker with search in multiple languages
- 🌐 Translator with multiple API providers
- 📋 Clipboard history manager
- ⭐ Pinned/favorite items
- 🔥 ASCII Art & Stickers
- 🎨 Cyberpunk/VHS aesthetic

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Super + . | Toggle CyberDash |
| Esc | Close |
| Tab | Next section |
| 1-5 | Switch sections |
| Enter | Select/Copy |
| Ctrl+C | Copy selected |
| Ctrl+V | Paste & Translate |

## Configuration

Config file: `~/.config/cyberdash/config.json`

## License

MIT
