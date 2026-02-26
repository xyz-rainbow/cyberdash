#!/bin/bash
# CyberDash launcher
# Run as user (not root)

# Set GTK backend based on display server
if [ -n "$WAYLAND_DISPLAY" ]; then
    export GDK_BACKEND=wayland
else
    export GDK_BACKEND=x11
fi

# Add source to path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/src"

# Run the app
exec python3 -m cyberdash "$@"
