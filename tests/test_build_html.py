import sys, pathlib, json, re
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "core" / "visualizer"))
from build import build_html
FIX = pathlib.Path(__file__).parent / "fixtures" / "personas"

def test_injects_json_into_marker(tmp_path):
    template = "<script>const DATA = /*__PERSONA_DATA__*/{}/*__END__*/;</script>"
    out = build_html(FIX, template)
    m = re.search(r"/\*__PERSONA_DATA__\*/(.*)/\*__END__\*/", out, re.DOTALL)
    data = json.loads(m.group(1))
    assert data["personas"][0]["id"] == "p01"

def test_marker_missing_raises():
    import pytest
    with pytest.raises(ValueError):
        build_html(FIX, "<html>no marker</html>")
