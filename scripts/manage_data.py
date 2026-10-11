"""Convenience script to run data pipeline operations for EconLens AI.

Usage:
    python scripts/manage_data.py status
    python scripts/manage_data.py acquire
    python scripts/manage_data.py validate
    python scripts/manage_data.py standardize
    python scripts/manage_data.py report
    python scripts/manage_data.py all
"""

import sys
from pathlib import Path

# Ensure project root is in Python sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.data.pipeline import main

if __name__ == "__main__":
    main()
