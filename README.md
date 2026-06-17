# 2026 지원경향 분석 웹앱

작년 입시 교차지원·합격 경향 조회 도구.

## 사용 (학생·선생님)
`web/` 폴더의 `index.html` 더블클릭. 설치·인터넷 불필요.
공유: `web/` 폴더를 통째로 전달(USB/압축/카톡) 또는 GitHub Pages 업로드.

## 자료 갱신 (관리자)
1. 새 엑셀로 `build/build.py`의 `XLSX` 경로 수정
2. `python build/build.py` 실행 → `web/data/*.js` 갱신
3. 빌드 끝에 시트별 행수·매칭률 출력. 상세는 `web/data/report.json`.

## 한계
지망 칸 표기와 원본 행 표기 차이로 역방향 매칭은 best-effort(100% 아님).
미매칭은 "역방향 데이터 없음"으로 표시되며 순위표·카드는 항상 정확.

## 개발 테스트
`python -m pytest build/tests/ -v`
