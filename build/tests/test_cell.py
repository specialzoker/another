from build.parse import parse_pref_cell

def test_simple_cell():
    cell = "경상국립대_x000D_\n(일반)_x000D_\n1[0]"
    assert parse_pref_cell(cell) == {
        "university": "경상국립대", "label": "일반",
        "applied": 1, "accepted": 0,
    }

def test_count_with_spaces():
    cell = "고려대_x000D_\n학교추천_x000D_\n60 [44]"
    assert parse_pref_cell(cell) == {
        "university": "고려대", "label": "학교추천",
        "applied": 60, "accepted": 44,
    }

def test_merged_univ_track():
    cell = "영남대일반학생_x000D_\n1[0]"
    assert parse_pref_cell(cell) == {
        "university": "영남대일반학생", "label": "",
        "applied": 1, "accepted": 0,
    }

def test_hakgwa_three_lines():
    cell = "가톨릭대_x000D_\n(지역균형)_x000D_\n의예과_x000D_\n1[1]"
    assert parse_pref_cell(cell) == {
        "university": "가톨릭대", "label": "지역균형 · 의예과",
        "applied": 1, "accepted": 1,
    }

def test_empty_or_malformed_returns_none():
    assert parse_pref_cell(None) is None
    assert parse_pref_cell("") is None
    assert parse_pref_cell("그냥텍스트_x000D_\n없음") is None
