import pathlib
import sys

# Put the pipeline/ directory (parent of tests/) on sys.path so tests can
# `import config`, `import councilmatic`, etc. the same flat way the modules do.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
