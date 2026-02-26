"""CyberDash main entry point"""
import sys
import os

# Add src to path  
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cyberdash import CyberDashApplication

def main():
    app = CyberDashApplication()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
