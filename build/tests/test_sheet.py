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


def test_bad_case_count_is_skipped():
    header = ["지역","대학명","전형유형","전형명","사례수","최고","평균","중간","최저","1 지망"]
    good = ["서울","연세대","교과","추천형","3 [1]",1.0,1.1,1.1,1.2,""]
    bad  = ["서울","고려대","교과","학교추천","비어있음",1.0,1.1,1.1,1.2,""]
    recs, skipped = parse_sheet("전형", [header, good, bad])
    assert len(recs) == 1
    assert skipped == 1

def test_short_row_does_not_crash():
    header = ["지역","대학명","전형유형","전형명","사례수","최고","평균","중간","최저","1 지망"]
    short = ["서울","서강대","교과","지역균형","2 [0]"]  # 등급·지망 칸 없음(짧은 행)
    recs, _ = parse_sheet("전형", [header, short])
    assert len(recs) == 1
    assert recs[0]["grades"]["best"] is None
    assert recs[0]["preferences"] == []

def test_duplicate_ids_are_disambiguated():
    header = ["지역","대학명","전형유형","전형명","사례수","최고","평균","중간","최저","1 지망"]
    r1 = ["경남","경상국립대","학생부교과","일반","3 [0]",1.13,1.2,1.2,1.3,""]
    r2 = ["경남","경상국립대","학생부교과","일반","19 [7]",1.34,1.5,1.5,1.7,""]
    r3 = ["경남","경상국립대","학생부교과","일반","31 [11]",3.47,3.8,3.8,4.0,""]
    recs, _ = parse_sheet("전형", [header, r1, r2, r3])
    ids = [r["id"] for r in recs]
    assert len(set(ids)) == 3                       # 전부 유일
    assert ids[0] == "전형:경상국립대:학생부교과:일반"   # 첫 행은 깨끗한 id 유지
    assert ids[1] == "전형:경상국립대:학생부교과:일반#2"
    assert ids[2] == "전형:경상국립대:학생부교과:일반#3"
    # count/grades 는 각 행 고유값 유지
    assert recs[0]["count"]["applied"] == 3
    assert recs[1]["count"]["applied"] == 19
