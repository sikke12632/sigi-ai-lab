# 개인 주식 리서치 저장소

공개 자료(SEC EDGAR 공시 원문·XBRL, 회사 보도자료 등)로 미국 상장사를 조사하고, 모든 사실에 원문 인용을 붙여 보관한다.

## 구성
- `docs/gold_spec.md` — 정답지 작성 명세(스키마, 섹션, 규칙)
- `gold_cloud/` — 회사별 정답지 JSON과 `SUMMARY.md`
- `tools/secfetch.py` — SEC 공정접근 정책(식별 User-Agent, 속도제한)을 지키는 캐시 수집기
- `tools/verify_gold.py` — 정답지 검증기: 스키마, 기준일, XBRL 대조, 모든 인용문이 원문에 실제로 있는지 재확인

## 사용법
```bash
python3 tools/secfetch.py filings 811156 --since 2026-04-14     # 공시 목록
python3 tools/secfetch.py text <URL> --grep "notes payable"     # 원문 검색
python3 tools/verify_gold.py gold_cloud/*.json                  # 전체 검증
```
SEC 요청에 쓸 연락처는 환경변수 `SEC_USER_AGENT="이름 이메일"`로 바꿀 수 있다.
