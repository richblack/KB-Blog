#!/usr/bin/env python3
import os
import sys

# Ensure we can import from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from publisher.entry.main import main

if __name__ == "__main__":
    # Change CWD to project root if running from scripts/
    # But usually we run from root. The config uses "./KB" so CWD must be root.
    # The import 'from publisher...' works if 'scripts' is in path or if we are in 'scripts'.
    # If we run 'python scripts/publish.py' from root, sys.path[0] is 'scripts/'.
    main()
