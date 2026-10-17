import os
import sys
import struct
import zlib
import numpy as np

# Tell Python to load modules from src/core/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'core'))

from psvc_reference import (
    seal, open_container, encode_text, content_hash, validate_file,
    write_file, read_file, PSVCError,
    MAGIC, VERSION, HEADER_SIZE,
    PRECISION_INT8, PRECISION_FLOAT16, PRECISION_FLOAT32
)