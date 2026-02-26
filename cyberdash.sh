#!/bin/bash
# CyberDash launcher
# Run as user (not root)

# Set GTK backend based on display server
if [ -n "$WAYLAND_DISPLAY" ]; then
    export GDK_BACKEND=wayland
else
    export GDK_BACKEND=x11
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run from src directory with python module
cd "$SCRIPT_DIR/src"
exec python3 -m cyberdash "$@"
