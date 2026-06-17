from build.parse import parse_sheet

HEADER = ["지역","대학명","전형유형","전형명","사례수","최고","평균","중간","최저",
          "1 지망","2 지망","최저","교과","종합","논술","실기","기타"]

ROW = ["경남","인제대","학생부교과","의예,약학","2 [1]",1.08,1.11,1.11,1.14,
       "경상국립대_x000D_\n(일반)_x000D_\n1[0]",
       "서울대_x000D_\n(지역균형)_x000D_\n1[0]",
       "", "", "", "", "", ""]

def test_parse_sheet_builds_record():
    recs, skipped = parse_sheet("전형", [HEADER, ROW])
    assert len(recs) == 1
    r = recs[0]
    assert r["region"] == "경남"
    assert r["university"] == "인제대"
    assert r["type"] == "학생부교과"
    assert r["name"] == "의예,약학"
    assert r["unit"] is None
    assert r["count"] == {"applied": 2, "accepted": 1}
    assert r["grades"] == {"best":1.08,"avg":1.11,"median":1.11,"worst":1.14}
    assert r["id"] == "전형:인제대:학생부교과:의예,약학"
    assert len(r["preferences"]) == 2
    assert r["preferences"][0] == {
        "rank":1,"university":"경상국립대","label":"일반","applied":1,"accepted":0
    }

def test_hakgwa_sheet_has_unit():
    header = ["지역","대명","전형유형","전형명","모집단위","사례수",
              "최고","평균","중간","최저","1 지망","2 지망","인문","자연"]
    row = ["서울","중앙대","종합","CAU융합형인재","의학부(의예)","1 [0]",
           1,1,1,1,
           "가톨릭대_x000D_\n(지역균형)_x000D_\n의예과_x000D_\n1[1]","",
           "",""]
    recs, _ = parse_sheet("학과", [header, row])
    assert recs[0]["unit"] == "의학부(의예)"
    assert recs[0]["id"] == "학과:중앙대:종합:CAU융합형인재:의학부(의예)"
    assert recs[0]["preferences"][0]["label"] == "지역균형 · 의예과"
