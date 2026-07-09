"""persona-maker visualizer builder. Stdlib only."""
import argparse
import json
import pathlib
import re
import sys

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

DEFAULT_CONFIG = {"model": "haiku", "persona_count": 5, "language": "en"}
REQUIRED_CARD_FIELDS = ["id", "name", "role", "confidence"]

def _collect_markdown(dir_path, warnings):
    """Walk a markdown directory (cards/journeys/consultations) in sorted order and
    parse frontmatter. Files that fail to parse are skipped and logged to warnings.
    Never crashes."""
    items = []
    if not dir_path.is_dir():
        warnings.append(f"directory {dir_path.name}/ not found ({dir_path})")
        return items
    for path in sorted(dir_path.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        try:
            meta, body = parse_frontmatter(text)
        except ValueError as e:
            warnings.append(f"{path.name}: frontmatter parse failed - {e}")
            continue
        meta["body"] = body.strip()
        items.append(meta)
    return items

def _load_config(personas_dir, warnings):
    config_path = personas_dir / "config.json"
    if not config_path.is_file():
        warnings.append(f"config.json not found, using defaults ({config_path})")
        return dict(DEFAULT_CONFIG)
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        warnings.append(f"config.json parse failed, using defaults: {e}")
        return dict(DEFAULT_CONFIG)

def collect(personas_dir):
    """Read personas_dir (config.json, cards/, journeys/, consultations/) and gather
    the data the visualization needs. Parse/validation failures never crash — they
    accumulate in the warnings list."""
    personas_dir = pathlib.Path(personas_dir)
    warnings = []

    config = _load_config(personas_dir, warnings)
    personas = _collect_markdown(personas_dir / "cards", warnings)
    journeys = _collect_markdown(personas_dir / "journeys", warnings)
    consultations = _collect_markdown(personas_dir / "consultations", warnings)

    for p in personas:
        pid = p.get("id", "?")
        for field in REQUIRED_CARD_FIELDS:
            if field in p:
                continue
            if field == "confidence":
                p["confidence"] = "assumption"
            else:
                p[field] = ""
            warnings.append(f"{pid}: missing required field '{field}'")

    return {
        "config": config,
        "personas": personas,
        "journeys": journeys,
        "consultations": consultations,
        "warnings": warnings,
    }

MARKER_RE = re.compile(r"/\*__PERSONA_DATA__\*/.*?/\*__END__\*/", re.DOTALL)

def build_html(personas_dir, template_text):
    """Read personas_dir via collect() and return an HTML string where the
    /*__PERSONA_DATA__*/.../*__END__*/ marker in template_text is replaced with the
    actual JSON data. Raises ValueError if the marker is absent."""
    if not MARKER_RE.search(template_text):
        raise ValueError(
            "marker /*__PERSONA_DATA__*/.../*__END__*/ not found in template"
        )
    data = collect(personas_dir)
    payload = json.dumps(data, ensure_ascii=False)
    # Escape "</script>" (etc.) that may appear in a persona body (markdown) so it
    # does not break HTML parsing.
    payload = payload.replace("</", "<\\/")
    replacement = "/*__PERSONA_DATA__*/" + payload + "/*__END__*/"
    return MARKER_RE.sub(lambda _m: replacement, template_text, count=1)

def main():
    parser = argparse.ArgumentParser(description="Assemble the persona-maker visualization HTML.")
    parser.add_argument("--personas-dir", default="personas")
    parser.add_argument(
        "--template",
        default=str(pathlib.Path(__file__).parent / "template.html"),
    )
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    personas_dir = pathlib.Path(args.personas_dir)
    template_path = pathlib.Path(args.template)
    output_path = pathlib.Path(args.output) if args.output else personas_dir / "index.html"

    if not template_path.is_file():
        print(f"template file not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    template_text = template_path.read_text(encoding="utf-8")
    html = build_html(personas_dir, template_text)

    warnings = collect(personas_dir)["warnings"]
    for w in warnings:
        print(w, file=sys.stderr)

    output_path.write_text(html, encoding="utf-8")
    print(str(output_path))

if __name__ == "__main__":
    main()
