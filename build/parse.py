import re

_COUNT_RE = re.compile(r"^\s*(\d+)\s*\[\s*(\d+)\s*\]\s*$")


def _clean_lines(cell):
    """셀 문자열을 줄 리스트로 정리. _x000D_ 와 개행 제거."""
    text = cell.replace("_x000D_", "")
    lines = [ln.strip() for ln in text.replace("\r", "\n").split("\n")]
    return [ln for ln in lines if ln]


def parse_pref_cell(cell):
    """지망 칸 1개를 파싱. 형식 불일치면 None.

    반환: {university, label, applied, accepted}
    - 마지막 줄이 N[M] 이어야 유효.
    - 첫 줄 = 대학명, 가운데 줄들 = 전형명/학과명(" · "로 결합), 괄호는 제거.
    """
    if not cell or not isinstance(cell, str):
        return None
    lines = _clean_lines(cell)
    if len(lines) < 2:
        return None
    m = _COUNT_RE.match(lines[-1])
    if not m:
        return None
    applied, accepted = int(m.group(1)), int(m.group(2))
    university = lines[0]
    middle = lines[1:-1]
    label_parts = [_strip_parens(p) for p in middle]
    label = " · ".join(p for p in label_parts if p)
    return {
        "university": university,
        "label": label,
        "applied": applied,
        "accepted": accepted,
    }


def _strip_parens(s):
    """앞뒤 괄호류 제거: (일반)->일반, [면접]->면접. 짝이 맞을 때만. 내부는 보존."""
    s = s.strip()
    pairs = {"(": ")", "[": "]"}
    if len(s) >= 2 and s[0] in pairs and s[-1] == pairs[s[0]]:
        return s[1:-1].strip()
    return s


_CAMPUS_SUFFIXES = ("칠암", "김해", "광주", "경산", "아산", "포항", "대구", "서울", "원주")


def normalize_name(s):
    """매칭용 정규화: 공백·괄호류·'전형' 접미·캠퍼스 접미 제거."""
    if not s:
        return ""
    s = s.strip()
    s = re.sub(r"[()\[\]]", "", s)          # 괄호류 제거
    while s.endswith("전형"):                # 끝의 '전형' 접미 제거(반복)
        s = s[:-2]
    s = s.replace(" ", "")
    for suf in _CAMPUS_SUFFIXES:            # 캠퍼스 접미 제거
        if len(s) > len(suf) + 1 and s.endswith(suf):
            s = s[: -len(suf)]
            break
    return s


def normalize_university(s):
    """대학명 정규화(= normalize_name; 캠퍼스 접미 포함)."""
    return normalize_name(s)


def match_key(university, name):
    return f"{normalize_university(university)}|{normalize_name(name)}"


def build_match_index(records):
    """원본 records → {정규화대학: [(정규화전형명, id)]} 인덱스."""
    idx = {}
    for r in records:
        u = normalize_university(r["university"])
        n = normalize_name(r.get("name") or "")
        idx.setdefault(u, []).append((n, r["id"]))
    return idx


def find_match(idx, university, label):
    """지망 (대학,라벨) → 원본 id (best-effort). 실패 시 None.
    - 같은 대학 후보 중 정규화 라벨이 완전일치 우선, 없으면 부분일치(포함관계).
    """
    u = normalize_university(university)
    target = normalize_name(label)
    cands = idx.get(u)
    if not cands or not target:
        return None
    for n, rid in cands:          # 1) 완전일치
        if n == target:
            return rid
    for n, rid in cands:          # 2) 부분일치
        if n and (target in n or n in target):
            return rid
    return None


def _parse_count(val):
    """'94 [33]' → (94, 33). 실패 시 (None, None)."""
    if val is None:
        return None, None
    m = _COUNT_RE.match(str(val))
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def _to_float(val):
    try:
        return round(float(val), 4)
    except (TypeError, ValueError):
        return None


def parse_sheet(sheet_name, rows):
    """rows[0]=헤더, 이후 데이터행. (records, skipped_count) 반환.

    헤더에서 컬럼 위치를 찾는다(시트마다 '대학명'/'대명' 등 표기가 달라
    텍스트로 탐색). 지망 컬럼 = 헤더가 '<숫자>지망' 패턴.
    """
    header = [str(h).replace(" ", "") if h is not None else "" for h in rows[0]]

    def col(*names):
        for nm in names:
            if nm in header:
                return header.index(nm)
        return None

    def cell(row, ci):
        """안전 접근: 컬럼 없거나 행이 짧으면 None."""
        if ci is None or ci >= len(row):
            return None
        return row[ci]

    c_region = col("지역")
    c_univ = col("대학명", "대명")
    c_type = col("전형유형")
    c_name = col("전형명")
    c_unit = col("모집단위")
    c_count = col("사례수")
    c_best = col("최고")
    c_avg = col("평균")
    c_median = col("중간", "중간값")
    # '최저'는 등급(첫 등장)과 표 끝 머리글에 중복 → 사례수 직후의 첫 '최저' 사용
    _count_idx = c_count if c_count is not None else -1
    c_worst = next((i for i, h in enumerate(header) if h == "최저" and i > _count_idx), None)
    pref_cols = [i for i, h in enumerate(header) if re.match(r"^\d+지망$", h)]

    records, skipped = [], 0
    seen_ids = {}
    for row in rows[1:]:
        if cell(row, c_univ) in (None, ""):
            continue
        applied, accepted = _parse_count(cell(row, c_count))
        if applied is None:
            skipped += 1
            continue
        _u = cell(row, c_unit); unit = str(_u).strip() if _u else None
        prefs = []
        for rank, ci in enumerate(pref_cols, start=1):
            parsed = parse_pref_cell(cell(row, ci))
            if parsed:
                parsed["rank"] = rank
                prefs.append(parsed)
        _rg = cell(row, c_region); region = str(_rg).strip() if _rg else ""
        university = str(cell(row, c_univ)).strip()
        _tp = cell(row, c_type); type_ = str(_tp).strip() if _tp else ""
        _nm = cell(row, c_name); name = str(_nm).strip() if _nm else ""
        id_parts = [_sheet_key(sheet_name), university, type_, name]
        if unit:
            id_parts.append(unit)
        rid = ":".join(id_parts)
        n_seen = seen_ids.get(rid, 0) + 1
        seen_ids[rid] = n_seen
        if n_seen > 1:
            rid = f"{rid}#{n_seen}"
        records.append({
            "id": rid,
            "sheet": sheet_name,
            "region": region,
            "university": university,
            "type": type_,
            "name": name,
            "unit": unit,
            "count": {"applied": applied, "accepted": accepted},
            "grades": {
                "best": _to_float(cell(row, c_best)),
                "avg": _to_float(cell(row, c_avg)),
                "median": _to_float(cell(row, c_median)),
                "worst": _to_float(cell(row, c_worst)),
            },
            "preferences": prefs,
        })
    return records, skipped


def _sheet_key(sheet_name):
    return {
        "전형": "전형", "전형_인문": "전형", "전형_자연": "전형", "학과": "학과",
    }.get(sheet_name, sheet_name)


def _base_id(rid):
    """레코드 id 끝의 '#숫자' 접미 제거 → 병합 그룹 키."""
    return re.sub(r"#\d+$", "", rid)


def _weighted_avg(pairs):
    """pairs: [(value, weight)]. value None 은 제외. 전부 None 이면 None."""
    num = 0.0
    den = 0
    for v, w in pairs:
        if v is None:
            continue
        num += v * w
        den += w
    return round(num / den, 4) if den else None


def merge_records(records):
    """base-id 가 같은 레코드들을 한 레코드로 완전 병합.

    - count: applied/accepted 합산
    - grades: best=min, worst=max, avg/median=applied 가중평균
    - preferences: 정규화 대상(대학|전형) 기준 합산 → applied 내림차순 재정렬·재순위
    matchedId/rate 는 설정하지 않음(호출 측이 병합 후 수행).
    입력 순서를 보존한다.
    """
    groups = {}
    order = []
    for r in records:
        bid = _base_id(r["id"])
        if bid not in groups:
            groups[bid] = []
            order.append(bid)
        groups[bid].append(r)

    merged = []
    for bid in order:
        grp = groups[bid]
        if len(grp) == 1:
            r = dict(grp[0])
            r["id"] = bid
            merged.append(r)
            continue
        first = grp[0]
        applied = sum(r["count"]["applied"] for r in grp)
        accepted = sum(r["count"]["accepted"] for r in grp)
        bests = [r["grades"]["best"] for r in grp if r["grades"]["best"] is not None]
        worsts = [r["grades"]["worst"] for r in grp if r["grades"]["worst"] is not None]
        avg = _weighted_avg([(r["grades"]["avg"], r["count"]["applied"]) for r in grp])
        median = _weighted_avg([(r["grades"]["median"], r["count"]["applied"]) for r in grp])

        agg = {}
        porder = []
        for r in grp:
            for p in r["preferences"]:
                k = normalize_university(p["university"]) + "|" + normalize_name(p["label"])
                if k not in agg:
                    agg[k] = {"university": p["university"], "label": p["label"],
                              "applied": 0, "accepted": 0}
                    porder.append(k)
                agg[k]["applied"] += p["applied"]
                agg[k]["accepted"] += p["accepted"]
        prefs = [agg[k] for k in porder]
        prefs.sort(key=lambda x: x["applied"], reverse=True)
        for i, p in enumerate(prefs, start=1):
            p["rank"] = i

        merged.append({
            "id": bid,
            "sheet": first["sheet"],
            "region": first["region"],
            "university": first["university"],
            "type": first["type"],
            "name": first["name"],
            "unit": first["unit"],
            "count": {"applied": applied, "accepted": accepted},
            "grades": {
                "best": min(bests) if bests else None,
                "avg": avg,
                "median": median,
                "worst": max(worsts) if worsts else None,
            },
            "preferences": prefs,
        })
    return merged
