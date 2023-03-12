import os
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).parent
ROBOCOMPDSL_DIR = CURRENT_DIR / ".."
sys.path.append(str(ROBOCOMPDSL_DIR))