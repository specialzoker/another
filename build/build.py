"""엑셀 → web/data/*.js 산출 + 매칭 + 리포트.
실행(프로젝트 루트에서): python -m build.build   또는   python build/build.py
"""
import json
import os
import sys

# `python build/build.py` 로 실행해도 build 패키지를 import 할 수 있게 루트 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl
from build.parse import parse_sheet, build_match_index, find_match, merge_records

XLSX = r"C:\클라우드파일\다운 받은 파일\2026\2026 지원경향분석_전형_학과.xlsx"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "web", "data")

SHEET_KEYS = {
    "전형": "jeonhyeong",
    "전형_인문": "jeonhyeong_inmun",
    "전형_자연": "jeonhyeong_jayeon",
    "학과": "hakgwa",
}


def read_rows(ws):
    return [[c.value for c in row] for row in ws.iter_rows()]


def write_js(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    if not os.path.exists(XLSX):
        sys.exit(f"ERROR: 엑셀 파일을 찾을 수 없습니다:\n  {XLSX}")
    os.makedirs(OUT_DIR, exist_ok=True)
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    report = {"sheets": {}}
    index = []

    for sheet_name, key in SHEET_KEYS.items():
        ws = wb[sheet_name]
        rows = read_rows(ws)
        # 헤더 행 탐색: '사례수' 포함 행
        h = next((i for i, r in enumerate(rows)
                  if any(str(c).replace(" ", "") == "사례수" for c in r if c)), 0)
        records, skipped = parse_sheet(sheet_name, rows[h:])
        records = merge_records(records)

        idx = build_match_index(records)
        matched = total = 0
        for r in records:
            for p in r["preferences"]:
                total += 1
                mid = find_match(idx, p["university"], p["label"])
                p["matchedId"] = mid
                p["rate"] = round(p["accepted"] / p["applied"], 3) if p["applied"] else 0
                if mid:
                    matched += 1
            c = r["count"]
            r["rate"] = round(c["accepted"] / c["applied"], 3) if c["applied"] else 0

        write_js(
            os.path.join(OUT_DIR, f"{key}.js"),
            "window.__APPDATA__=window.__APPDATA__||{};window.__APPDATA__['%s']=%s;"
            % (key, json.dumps(records, ensure_ascii=False)),
        )
        for r in records:
            index.append({
                "id": r["id"], "key": key, "region": r["region"],
                "university": r["university"], "type": r["type"],
                "name": r["name"], "unit": r["unit"],
            })
        report["sheets"][key] = {
            "records": len(records), "skipped": skipped,
            "prefs": total, "matched": matched,
            "match_rate": round(matched / total, 3) if total else 0,
        }

    write_js(
        os.path.join(OUT_DIR, "index.js"),
        "window.__APPINDEX__=%s;" % json.dumps(index, ensure_ascii=False),
    )
    with open(os.path.join(OUT_DIR, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("BUILD DONE")
    for k, v in report["sheets"].items():
        print(f"  {k}: {v['records']} rows, skipped {v['skipped']}, "
              f"match {int(v['match_rate']*100)}%")


if __name__ == "__main__":
    main()
