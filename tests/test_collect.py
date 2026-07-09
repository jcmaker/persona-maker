import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "core" / "visualizer"))
from build import collect
FIX = pathlib.Path(__file__).parent / "fixtures" / "personas"

def test_collect_personas_journeys_consultations():
    data = collect(FIX)
    ids = [p["id"] for p in data["personas"]]
    assert "p01" in ids and len(data["personas"]) == 3  # 깨진 카드 제외
    assert data["journeys"][0]["persona_id"] == "p01"
    assert data["consultations"][0]["topic"]
    assert data["config"]["persona_count"] == 5

def test_broken_card_becomes_warning_not_crash():
    data = collect(FIX)
    assert any("persona-99-broken.md" in w for w in data["warnings"])

def test_missing_required_field_warns():
    # persona-03 fixture는 confidence 필드 없음 → 경고 + assumption 기본값
    data = collect(FIX)
    p03 = next(p for p in data["personas"] if p["id"] == "p03")
    assert p03["confidence"] == "assumption"
    assert any("p03" in w and "confidence" in w for w in data["warnings"])
