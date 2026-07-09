import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "core" / "visualizer"))
from build import parse_frontmatter

def test_scalar_and_int():
    text = "---\nid: p01\nname: \"김서연\"\ntech_savviness: 4\n---\n본문"
    meta, body = parse_frontmatter(text)
    assert meta["id"] == "p01"
    assert meta["name"] == "김서연"
    assert meta["tech_savviness"] == 4
    assert body.strip() == "본문"

def test_inline_list_and_dict():
    text = '---\ngoals: ["빠른 결정", "재작업 방지"]\ndemographics: { age: 32, occupation: "디자이너" }\n---\n'
    meta, _ = parse_frontmatter(text)
    assert meta["goals"] == ["빠른 결정", "재작업 방지"]
    assert meta["demographics"]["age"] == 32

def test_negative_int_list():
    text = "---\nemotions: [1, -2, 0, 2, 1]\n---\n"
    meta, _ = parse_frontmatter(text)
    assert meta["emotions"] == [1, -2, 0, 2, 1]

def test_missing_frontmatter_raises():
    import pytest
    with pytest.raises(ValueError):
        parse_frontmatter("frontmatter 없는 문서")
