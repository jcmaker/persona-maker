import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "core" / "visualizer"))
from build import parse_frontmatter

def test_scalar_and_int():
    text = "---\nid: p01\nname: \"Seoyeon Kim\"\ntech_savviness: 4\n---\nbody"
    meta, body = parse_frontmatter(text)
    assert meta["id"] == "p01"
    assert meta["name"] == "Seoyeon Kim"
    assert meta["tech_savviness"] == 4
    assert body.strip() == "body"

def test_inline_list_and_dict():
    text = '---\ngoals: ["fast decisions", "avoid rework"]\ndemographics: { age: 32, occupation: "designer" }\n---\n'
    meta, _ = parse_frontmatter(text)
    assert meta["goals"] == ["fast decisions", "avoid rework"]
    assert meta["demographics"]["age"] == 32

def test_negative_int_list():
    text = "---\nemotions: [1, -2, 0, 2, 1]\n---\n"
    meta, _ = parse_frontmatter(text)
    assert meta["emotions"] == [1, -2, 0, 2, 1]

def test_missing_frontmatter_raises():
    import pytest
    with pytest.raises(ValueError):
        parse_frontmatter("a document without frontmatter")
