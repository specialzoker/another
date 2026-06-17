from build.parse import merge_records


def _rec(rid, applied, accepted, best, worst, avg, prefs):
    return {"id": rid, "sheet": "전형", "region": "경남", "university": "경상국립대",
            "type": "학생부교과", "name": "일반", "unit": None,
            "count": {"applied": applied, "accepted": accepted},
            "grades": {"best": best, "avg": avg, "median": avg, "worst": worst},
            "preferences": prefs}


def test_merge_combines_same_base_id():
    r1 = _rec("전형:경상국립대:학생부교과:일반", 3, 0, 1.13, 1.2, 1.16,
              [{"rank": 1, "university": "서울대", "label": "지역균형", "applied": 2, "accepted": 1}])
    r2 = _rec("전형:경상국립대:학생부교과:일반#2", 19, 7, 1.34, 5.52, 2.0,
              [{"rank": 1, "university": "서울대", "label": "지역균형", "applied": 3, "accepted": 0},
               {"rank": 2, "university": "연세대", "label": "추천형", "applied": 1, "accepted": 1}])
    out = merge_records([r1, r2])
    assert len(out) == 1
    m = out[0]
    assert m["id"] == "전형:경상국립대:학생부교과:일반"
    assert m["count"] == {"applied": 22, "accepted": 7}
    assert m["grades"]["best"] == 1.13
    assert m["grades"]["worst"] == 5.52
    assert m["grades"]["avg"] == round((1.16 * 3 + 2.0 * 19) / 22, 4)
    p = m["preferences"]
    assert p[0] == {"rank": 1, "university": "서울대", "label": "지역균형", "applied": 5, "accepted": 1}
    assert p[1] == {"rank": 2, "university": "연세대", "label": "추천형", "applied": 1, "accepted": 1}


def test_different_base_id_not_merged():
    a = _rec("전형:경희대:학생부종합:네오르네상스", 45, 8, 1.03, 3.36, 1.5, [])
    b = _rec("전형:경희대(국):학생부종합:네오르네상스", 10, 2, 2.0, 3.0, 2.5, [])
    b["university"] = "경희대(국)"; b["region"] = "경기"
    out = merge_records([a, b])
    assert len(out) == 2


def test_single_record_passes_through():
    r = _rec("전형:서울대:학생부종합:지역균형", 94, 33, 1.12, 1.45, 1.24,
             [{"rank": 1, "university": "고려대", "label": "학교추천", "applied": 60, "accepted": 44}])
    out = merge_records([r])
    assert len(out) == 1
    assert out[0]["id"] == "전형:서울대:학생부종합:지역균형"
    assert out[0]["preferences"][0]["applied"] == 60


def test_merge_strips_only_trailing_hash_number():
    out = merge_records([_rec("전형:경상국립대:학생부교과:일반#3", 1, 0, 1.5, 1.5, 1.5, [])])
    assert out[0]["id"] == "전형:경상국립대:학생부교과:일반"
