#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Wrapper script for launching the Streamlit app from the root directory.
"""

import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the main app
from src.web.streamlit_app import main

if __name__ == "__main__":
    main()