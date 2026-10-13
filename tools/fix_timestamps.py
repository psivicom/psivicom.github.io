# Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM | EUPL 1.2
import re
import pathlib
from dateutil import parser
import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]

def fix_timestamp(match):
    prefix = match.group(1)
    rest_of_line = match.group(2)
    
    # Safely extract ONLY the ISO-like timestamp from the line
    ts_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)', rest_of_line)
    if ts_match:
        ts_str = ts_match.group(1)
        try:
            dt = parser.parse(ts_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            dt_utc = dt.astimezone(datetime.timezone.utc)
            
            # Format strictly to .sssZ
            new_ts = dt_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            
            # Replace only the timestamp, preserving any trailing text (e.g., " | Hash: ...")
            new_rest = rest_of_line.replace(ts_str, new_ts, 1)
            return f"{prefix}: {new_rest}"
        except Exception:
            pass
            
    return match.group(0)

for f in ROOT.rglob('*.md'):
    text = f.read_text(encoding='utf-8', errors='ignore')
    orig = text

    def fix_last_updated(m):
        raw = m.group(1)
        try:
            dt = parser.parse(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            dt_utc = dt.astimezone(datetime.timezone.utc)
            ms = dt_utc.microsecond
            if ms == 0:
                return f"*Last updated: {dt_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')}*"
            else:
                return f"*Last updated: {dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z*"
        except Exception:
            return m.group(0)

    # Fix *Last updated: ...*
    text = re.sub(r'\*Last updated:\s*(.*?)\*', fix_last_updated, text)
    
    # Fix created:/updated: safely without breaking on trailing text
    text = re.sub(r'(created|updated):\s*([^\n]+)', fix_timestamp, text)

    if text != orig:
        f.write_text(text, encoding='utf-8')
        print(f"Fixed {f} to .sssZ")

print("✅ Timestamp normalization complete.")
