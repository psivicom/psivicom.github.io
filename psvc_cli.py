# psvc_cli.py
# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
# Author: Louis-Philippe Audette
# ORCID: https://orcid.org/0000-000X-XXXX-XXXX
#
# RFC 1001 Command Line Interface
# Usage: python psvc_cli.py [create|inspect|validate|open] ...

import sys
import argparse
import numpy as np
from pathlib import Path
from psvc_reference import (
    encode_text, seal, open_container, write_file, read_file,
    validate_file, content_hash, PSVCError,
    PRECISION_INT8, PRECISION_FLOAT16, PRECISION_FLOAT32, DEFAULT_DIM
)

PRECISION_MAP = {"int8": PRECISION_INT8, "float16": PRECISION_FLOAT16, "float32": PRECISION_FLOAT32}

def cmd_create(args):
    """Create a .psvc container from text or random vector."""
    if args.text:
        vector = encode_text(args.text, dim=args.dim)
        print(f"[CREATE] Encoded text into {args.dim}-dim vector")
    elif args.random:
        vector = np.random.randn(args.dim).astype(np.float32)
        vector /= np.linalg.norm(vector)
        print(f"[CREATE] Generated random {args.dim}-dim vector")
    else:
        print("[ERROR] Provide --text or --random")
        return 1
    
    precision = PRECISION_MAP[args.precision]
    chash = content_hash(vector)
    
    if args.output:
        out_path = args.output
    else:
        out_path = f"{chash}.psvc"
    
    write_file(vector, out_path, precision)
    
    size = Path(out_path).stat().st_size 
    
    print(f"[CREATE] Sealed: {out_path}")
    print(f"[CREATE] Content hash: {chash}")
    print(f"[CREATE] Precision: {args.precision}")
    print(f"[CREATE] File size: {size} bytes")
    return 0

def cmd_inspect(args):
    """Inspect a .psvc container header."""
    try:
        info = validate_file(args.file)
        print(f"=== RFC 1001 Container: {args.file} ===")
        for key, value in info.items():
            print(f"  {key}: {value}")
        return 0
    except PSVCError as e:
        print(f"[INVALID] {e}")
        return 1
    except FileNotFoundError:
        print(f"[ERROR] File not found: {args.file}")
        return 1

def cmd_validate(args):
    """Validate a .psvc container (full decompression test)."""
    try:
        vector = read_file(args.file)
        chash = content_hash(vector)
        print(f"[VALID] {args.file}")
        print(f"  Dimensions: {len(vector)}")
        print(f"  Norm: {np.linalg.norm(vector):.6f}")
        print(f"  Content hash: {chash}")
        print(f"  Min: {vector.min():.4f}, Max: {vector.max():.4f}")
        return 0
    except PSVCError as e:
        print(f"[INVALID] {e}")
        return 1
    except FileNotFoundError:
        print(f"[ERROR] File not found: {args.file}")
        return 1

def cmd_open(args):
    """Open a .psvc container and show the vector."""
    try:
        vector = read_file(args.file)
        print(f"=== Opened: {args.file} ===")
        print(f"  Shape: {vector.shape}")
        print(f"  Dtype: {vector.dtype}")
        print(f"  First 10 values: {vector[:10]}")
        return 0
    except PSVCError as e:
        print(f"[INVALID] {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(
        description="RFC 1001 Pico Service Container (.psvc) CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python psvc_cli.py create --text "Goldstream forage forecast" --precision int8
  python psvc_cli.py create --random --dim 4096 --precision float16
  python psvc_cli.py inspect a16330272f3f.psvc
  python psvc_cli.py validate a16330272f3f.psvc
  python psvc_cli.py open a16330272f3f.psvc
        """
    )
    subparsers = parser.add_subparsers(dest="command")
    
    p_create = subparsers.add_parser("create", help="Create a .psvc container")
    p_create.add_argument("--text", type=str, help="Text to encode as vector")
    p_create.add_argument("--random", action="store_true", help="Generate random vector")
    p_create.add_argument("--dim", type=int, default=DEFAULT_DIM, help=f"Dimensions (default {DEFAULT_DIM})")
    p_create.add_argument("--precision", choices=["int8", "float16", "float32"], default="int8")
    p_create.add_argument("--output", type=str, help="Output filename")
    p_create.set_defaults(func=cmd_create)
    
    p_inspect = subparsers.add_parser("inspect", help="Inspect container header")
    p_inspect.add_argument("file", help=".psvc file to inspect")
    p_inspect.set_defaults(func=cmd_inspect)
    
    p_validate = subparsers.add_parser("validate", help="Validate container (full test)")
    p_validate.add_argument("file", help=".psvc file to validate")
    p_validate.set_defaults(func=cmd_validate)
    
    p_open = subparsers.add_parser("open", help="Open and display vector")
    p_open.add_argument("file", help=".psvc file to open")
    p_open.set_defaults(func=cmd_open)
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
