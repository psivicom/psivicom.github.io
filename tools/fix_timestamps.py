import re, pathlib
from dateutil import parser
import datetime

ROOT = pathlib.Path('.')

for f in ROOT.rglob('*.md'):
    text = f.read_text(encoding='utf-8', errors='ignore')
    orig = text

    def fix(m):
        raw = m.group(1)
        try:
            dt = parser.parse(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            dt_utc = dt.astimezone(datetime.timezone.utc)
            # keep millis if present, else .000
            ms = dt_utc.microsecond
            if ms == 0:
                return f"*Last updated: {dt_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')}*"
            else:
                return f"*Last updated: {dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z*"
        except:
            return m.group(0)

    text = re.sub(r'\*Last updated:\s*(.*?)\*', fix, text)
    # also fix created:/updated:
    text = re.sub(r'(created|updated):\s*([^\n]+)', lambda m: f"{m.group(1)}: {parser.parse(m.group(2)).astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')}" if '.000Z' not in m.group(2) and 'Z' in m.group(2) or 'Z' not in m.group(2) else m.group(0) , text)

    if text != orig:
        f.write_text(text, encoding='utf-8')
        print(f"Fixed {f} to .sssZ")
