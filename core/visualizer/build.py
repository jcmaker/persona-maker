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

DEFAULT_CONFIG = {"model": "haiku", "persona_count": 5, "language": "ko"}
REQUIRED_CARD_FIELDS = ["id", "name", "role", "confidence"]

def _collect_markdown(dir_path, warnings):
    """cards/journeys/consultations 등 md 디렉토리를 정렬 순회하며 frontmatter를 파싱한다.
    파싱 실패 파일은 건너뛰고 warnings에 기록한다. 크래시하지 않는다."""
    items = []
    if not dir_path.is_dir():
        warnings.append(f"{dir_path.name}/ 디렉토리를 찾을 수 없습니다 ({dir_path})")
        return items
    for path in sorted(dir_path.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        try:
            meta, body = parse_frontmatter(text)
        except ValueError as e:
            warnings.append(f"{path.name}: frontmatter 파싱 실패 - {e}")
            continue
        meta["body"] = body.strip()
        items.append(meta)
    return items

def _load_config(personas_dir, warnings):
    config_path = personas_dir / "config.json"
    if not config_path.is_file():
        warnings.append(f"config.json을 찾을 수 없어 기본값을 사용합니다 ({config_path})")
        return dict(DEFAULT_CONFIG)
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        warnings.append(f"config.json 파싱 실패 - 기본값을 사용합니다: {e}")
        return dict(DEFAULT_CONFIG)

def collect(personas_dir):
    """personas_dir(config.json, cards/, journeys/, consultations/)을 읽어
    시각화에 필요한 데이터를 모은다. 파싱/검증 실패는 절대 크래시로 이어지지 않고
    warnings 리스트에 쌓인다."""
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
            warnings.append(f"{pid}: 필수 필드 '{field}' 누락")

    return {
        "config": config,
        "personas": personas,
        "journeys": journeys,
        "consultations": consultations,
        "warnings": warnings,
    }

MARKER_RE = re.compile(r"/\*__PERSONA_DATA__\*/.*?/\*__END__\*/", re.DOTALL)

def build_html(personas_dir, template_text):
    """personas_dir을 collect()로 읽어 template_text의
    /*__PERSONA_DATA__*/.../*__END__*/ 마커를 실제 JSON 데이터로 치환한 HTML 문자열을 돌려준다.
    마커가 없으면 ValueError."""
    if not MARKER_RE.search(template_text):
        raise ValueError(
            "template에서 /*__PERSONA_DATA__*/.../*__END__*/ 마커를 찾을 수 없습니다"
        )
    data = collect(personas_dir)
    payload = json.dumps(data, ensure_ascii=False)
    # persona body(마크다운)에 "</script>" 등이 섞여 있어도 HTML 파싱이 깨지지 않도록 이스케이프.
    payload = payload.replace("</", "<\\/")
    replacement = "/*__PERSONA_DATA__*/" + payload + "/*__END__*/"
    return MARKER_RE.sub(lambda _m: replacement, template_text, count=1)

def main():
    parser = argparse.ArgumentParser(description="persona-maker 시각화 HTML을 조립한다.")
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
        print(f"템플릿 파일을 찾을 수 없습니다: {template_path}", file=sys.stderr)
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
