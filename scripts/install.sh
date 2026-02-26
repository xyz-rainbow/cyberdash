#!/bin/bash
# CyberDash Installation Script

set -e

echo "🔧 Installing CyberDash..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "📌 Python version: $PYTHON_VERSION"

# Install system dependencies (Debian/Ubuntu)
echo "📦 Installing system dependencies..."

if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y \
        python3-gi \
        python3-gi-cairo \
        gir1.2-gtk-4.0 \
        gir1.2-libadwaita-1.0 \
        libgirepository1.0-dev \
        python3-pip \
        python3-requests \
        keyboard
elif command -v pacman &> /dev/null; then
    sudo pacman -S --noconfirm \
        python-gobject \
        gtk4 \
        libadwaita \
        python-pip \
        python-keyboard
elif command -v dnf &> /dev/null; then
    sudo dnf install -y \
        python3-gobject \
        gtk4 \
        libadwaita \
        python3-pip \
        python3-requests \
        python-keyboard
fi

# Install keyboard module if not available
if ! python3 -c "import keyboard" 2>/dev/null; then
    echo "📦 Installing keyboard module..."
    pip3 install keyboard
fi

# Install CyberDash
echo "📦 Installing CyberDash..."
pip3 install --user --upgrade .

# Create autostart desktop entry
echo "📝 Creating autostart entry..."
mkdir -p ~/.config/autostart

cat > ~/.config/autostart/cyberdash.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=CyberDash
Comment=Advanced Emoji Picker for Linux
Exec=cyberdash
Icon=emoji-symbolic
Terminal=false
Categories=Utility;Accessories;
StartupNotify=false
EOF

echo ""
echo "✅ CyberDash installed successfully!"
echo ""
echo "Usage:"
echo "  • Run 'cyberdash' to start"
echo "  • Press Super + . to open emoji picker"
echo "  • Configure API keys in Settings"
echo ""
echo "Optional dependencies for text replacement:"
echo "  • X11: sudo apt install xdotool"
echo "  • Wayland: sudo apt install wtype"
echo ""
