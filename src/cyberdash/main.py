#!/usr/bin/env python3
"""CyberDash - Entry point"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cyberdash import main

if __name__ == "__main__":
    sys.exit(main())
