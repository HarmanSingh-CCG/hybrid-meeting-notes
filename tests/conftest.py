import sys
from pathlib import Path

# Make the repo root importable when running pytest from any cwd
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
