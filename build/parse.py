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
