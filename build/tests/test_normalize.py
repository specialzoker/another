from build.parse import normalize_name, match_key, build_match_index, find_match

def test_normalize_removes_parens_and_spaces():
    assert normalize_name("(일반)") == "일반"
    assert normalize_name("학생부교과:학교추천") == "학생부교과:학교추천"
    assert normalize_name(" 추천형 전형 ") == "추천형"  # 공백·"전형" 접미 제거

def test_normalize_removes_campus_suffix():
    assert normalize_name("경상국립대칠암") == "경상국립대"
    assert normalize_name("인제대김해") == "인제대"
    assert normalize_name("전남대광주") == "전남대"

def test_match_key_combines_university_and_name():
    assert match_key("고려대", "학교추천") == "고려대|학교추천"

def test_find_match_best_effort():
    records = [
        {"id": "a", "university": "고려대", "type": "학생부교과", "name": "학생부교과:학교추천"},
        {"id": "b", "university": "연세대", "type": "학생부교과", "name": "추천형"},
    ]
    idx = build_match_index(records)
    assert find_match(idx, "고려대", "학교추천") == "a"
    assert find_match(idx, "연세대", "추천형") == "b"
    assert find_match(idx, "서울대", "지역균형") is None

def test_find_match_multiple_candidates_first_wins():
    # 같은 대학에 후보가 여러 개이고 라벨이 모호한 부분문자열이면
    # 삽입 순서상 첫 후보를 반환한다(best-effort, first-wins).
    records = [
        {"id": "a", "university": "고려대", "type": "교과", "name": "학생부교과:학교추천"},
        {"id": "b", "university": "고려대", "type": "종합", "name": "학생부종합:학교추천"},
    ]
    idx = build_match_index(records)
    # "학교추천"은 둘 다의 부분문자열 → 첫 후보 a 반환
    assert find_match(idx, "고려대", "학교추천") == "a"
