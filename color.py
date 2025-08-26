"""
color.py — A tiny palette for Node coloring and arrow-key cycling.
"""

COLORS = [
    (1.0, 0.0, 0.0),   # red
    (0.0, 1.0, 0.0),   # green
    (0.0, 0.0, 1.0),   # blue
    (1.0, 1.0, 0.0),   # yellow
    (1.0, 0.0, 1.0),   # magenta
    (0.0, 1.0, 1.0),   # cyan
    (1.0, 0.5, 0.0),   # orange
    (1.0, 1.0, 1.0)    # white
]
MIN_COLOR = 0
MAX_COLOR = len(COLORS) - 1
