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
