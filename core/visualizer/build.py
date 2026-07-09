"""persona-maker visualizer builder. Stdlib only."""
import re

def _parse_value(raw):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [] if not inner else [_parse_value(v) for v in _split_top(inner)]
    if raw.startswith("{") and raw.endswith("}"):
        out = {}
        for pair in _split_top(raw[1:-1]):
            k, v = pair.split(":", 1)
            out[k.strip().strip('"')] = _parse_value(v)
        return out
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return raw

def _split_top(s):
    parts, depth, cur = [], 0, ""
    in_str = False
    for ch in s:
        if ch == '"':
            in_str = not in_str
        if not in_str:
            if ch in "[{":
                depth += 1
            elif ch in "]}":
                depth -= 1
            elif ch == "," and depth == 0:
                parts.append(cur); cur = ""; continue
        cur += ch
    if cur.strip():
        parts.append(cur)
    return parts

def parse_frontmatter(text):
    m = re.match(r"\A---\n(.*?)\n---\n?(.*)\Z", text, re.DOTALL)
    if not m:
        raise ValueError("frontmatter block (---) not found")
    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, val = line.partition(":")
        meta[key.strip()] = _parse_value(val)
    return meta, m.group(2)
