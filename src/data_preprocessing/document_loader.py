"""
4 main duties:
- Load file .md in data/processed 
- Read Vietnamese text from the file
- Extract metadata from the file
- Return list of Document for file chunker.py to process
"""

from datetime import datetime
from pathlib import Path 

