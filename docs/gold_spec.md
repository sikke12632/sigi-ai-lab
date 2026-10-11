# 정답지(gold) 작성 명세 — 2026-10-11 기준 6개사

이 문서는 사용자가 준 작업 지시를 그대로 옮기고, 실행 규칙을 덧붙인 것이다.

## 입력
- 기준일(cutoff): **2026-10-11** (UTC, 이날 23:59까지 공개된 자료만)
- 조사 창: 2026-04-14 ~ 2026-10-11 (180일). 그 이전 일은 tier `background`로만 기록
- 회사

| 티커 | 회사 | CIK | 결산월 |
|---|---|---|---|
| CMS | CMS Energy Corp | 0000811156 | 12월 |
| SYY | Sysco Corp | 0000096021 | 6월(52/53주) |
| NPO | Enpro Inc. | 0001164863 | 12월 |
| WYNN | Wynn Resorts Ltd | 0001174922 | 12월 |
| BZH | Beazer Homes USA Inc | 0000915840 | 9월 |
| BBW | Build-A-Bear Workshop Inc | 0001113809 | 1월(52/53주) |

- 자료: SEC EDGAR(공시 원문, XBRL/companyfacts), 회사 IR·보도자료, 실적발표 녹취, 규제기관·법원, 주요 언론. 주가·수익률 자료는 쓰지 않는다.

## 출력: `gold_cloud/{TICKER}.json`

```json
{
  "company": {"ticker": "XYZ", "cik": "0000000000", "name": "Example Corp"},
  "cutoff": "2026-10-11",
  "latest_periodic_report": {"form": "10-Q", "accession": "...", "period_end": "2026-06-30", "filed": "2026-08-.."},
  "choi": [
    {
      "target": "operating_income",
      "status": "value",
      "value_usd": -1322000,
      "printed": "(1,322)", "printed_scale": "thousands",
      "period_start": "2025-10-01", "period_end": "2026-06-30",
      "source": {"doc": "10-Q 0000000000-26-000000", "location": "Condensed Consolidated Statements of Operations", "quote": "원문 그대로의 행 텍스트"},
      "xbrl": {"tag": "us-gaap:OperatingIncomeLoss", "value": -1322000},
      "note": ""
    }
  ],
  "kim": [
    {
      "id": "XYZ-01", "section": "1_results", "tier": "required",
      "fact": "숫자는 원문에 인쇄된 그대로 쓴 한 문장 사실",
      "event_date": "2026-08-05", "published_date": "2026-08-05",
      "source": {"type": "sec", "doc": "8-K EX-99.1 0000000000-26-000001", "url": "https://...", "quote": "원문 그대로, 300자 이내"}
    }
  ],
  "searched_not_found": [{"section": "3_guidance", "checked": "무엇을 어디서 확인했는지"}]
}
```
(XYZ와 모든 값은 형식 예시일 뿐이다.)

### choi 대상 4개 (최신 정기보고서, 상장 지주회사 연결 기준)
- `operating_income`: 최신 정기보고서의 **회계연도 누적(YTD)** 기간
- `short_term_borrowings`: 기말 잔액
- `current_long_term_debt_ex_leases`: 기말 유동성 장기부채, 리스 제외
- `current_finance_leases`: 기말 유동성 금융리스 부채

`status`
- `value`: 값이 있음
- `none_presented`: 해당 계정이 재무제표에 없음 — 유동부채 목록과 관련 주석을 근거로 인용
- `not_determinable`: 판단 불가 — 이유를 `note`에

### kim 섹션
| 섹션 | 내용 | tier |
|---|---|---|
| `1_results` | 최신 분기·누적 실적(매출, 영업이익, GAAP 순이익, 전년비, 회사가 밝힌 원인, 일회성 항목) | required |
| `2_cash_debt` | 영업현금흐름 방향, 현금, 차입 증감, 큰 자금조달 | required |
| `3_guidance` | 현재 전망과 직전 전망 비교 | required (전망을 내는 회사만) |
| `4_events` | 조사 창 안의 8-K 사건(인수·매각, 경영진·이사 변경, 중요계약, 구조조정·손상, 사이버, 감사인·상장 문제) | required |
| `5_legal` | 회사가 공시한 중요 소송·조사 | required (중요한 것만) |
| `6_risks` | 일반 문구가 아닌 이 회사만의 구체적 위험 | optional |
| `7_industry` | 원 발표기관의 업계 통계 1~2개 | optional |

## 반드시 지킬 것
1. 모든 항목에 공개 원문의 그대로 인용(quote). 인용할 수 없는 사실은 넣지 않는다.
2. 기준일 이후 공개된 정보는 넣지 않는다.
3. 다른 정답지·채점 자료·이 프로젝트의 다른 산출물을 찾거나 참고하지 않는다(독립 작성).
4. 모르면 비워 두고(`null`, `not_determinable`) 이유를 적는다. 추정 금지.

## 함정
- 결산월: SYY·BZH·BBW는 회계연도가 달력과 다르다. YTD 시작일은 회사 회계연도 시작일, XBRL 컨텍스트 기간으로 확인.
- 연결 주체: CMS 10-K/10-Q는 Consumers Energy와 합본. Wynn도 자회사(Wynn Las Vegas, Wynn Macau) 공시가 따로 있다. 항상 상장 지주회사 연결 기준.
- 차입금 구분: 기업어음·신용한도 차입은 단기차입금. 유동성 장기부채와 섞지 않는다. 운용리스는 금융리스가 아니다.
- 실적 보도자료(8-K 2.02)는 `1_results`에만, `4_events`에 중복 금지. 주총 결과(5.07) 같은 일상 사건은 `optional`.
- SEC 요청: 식별 가능한 User-Agent, 초당 10회 이하.
- 같은 사건을 여러 출처가 다루면 회사 공시를 우선 인용.

## 완료 기준
1. 6개 JSON이 위 스키마로 파싱된다.
2. choi `value` 항목은 XBRL 태그가 있으면 `xbrl.value == value_usd`, 다르면 `note`에 이유.
3. 모든 kim quote가 출처 원문에 실제로 있는지 다시 열어 확인(확인 못 한 항목은 삭제).

## 실행 규칙 (작성 도구)
- `tools/secfetch.py`: 캐시·전역 속도제한(≈6회/초)이 걸린 수집기. `text URL --grep RE`로 원문을 읽고 quote는 그 출력에서 복사한다.
- `tools/verify_gold.py gold_cloud/X.json`: 스키마, 기준일, XBRL(companyfacts 대조), 모든 quote 원문 포함 여부를 재검사한다. **ERROR 0개**여야 완료.
- 표기 규칙
  - `fact`는 한국어 한 문장, 숫자는 원문 표기 그대로(예: `$1,834 million`, `(1,322)`).
  - `source.type`: `sec` | `company_ir` | `transcript` | `regulator` | `court` | `news` | `industry`
  - `source.doc`: `"<양식> <첨부> <accession>"` 예: `"8-K EX-99.1 0001104659-26-087288"`, `"10-Q 0000811156-26-000028"`. SEC 외 문서는 발표기관·제목.
  - `source.url`: 실제로 연 원문 URL(SEC는 `https://www.sec.gov/Archives/edgar/data/...` 직접 문서).
  - `event_date`: 사건 발생일(모르면 `null`), `published_date`: 원문 공개일.
  - choi `value_usd`는 달러 단위 정수, `printed`는 인쇄 그대로, `printed_scale`은 `units`|`thousands`|`millions`. `period_start`는 기말 잔액 항목이면 `null`.
