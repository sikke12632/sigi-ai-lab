# 정답지 요약 (기준일 2026-10-11)

검증: `python3 tools/verify_gold.py gold_cloud/*.json` → 6개 파일 모두 **ERROR 0 / warning 0**.
검증기는 모든 choi·kim 인용문의 출처 원문을 다시 열어 실제 포함 여부를 확인하고, choi 값을 SEC companyfacts XBRL과 대조한다.

| 티커 | 최신 정기보고서 | YTD 기간 | kim | 1 | 2 | 3 | 4 | 5 | 6 | 7 | choi (영업이익 / 단기차입 / 유동LTD / 유동금융리스) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CMS | 10-Q 2026-06-30 (07-28 제출) | 2026-01-01~06-30 | 33 | 8 | 8 | 3 | 5 | 6 | 2 | 1 | value / none / value / value(산출) |
| SYY | 10-K 2026-06-27 (08-21 제출) | 2025-06-29~2026-06-27 | 40 | 9 | 6 | 6 | 14 | 2 | 2 | 1 | value / none / value(산출) / value |
| NPO | 10-Q 2026-06-30 (08-04 제출) | 2026-01-01~06-30 | 30 | 10 | 6 | 4 | 3 | 6 | 1 | 0 | value / none / value / none |
| WYNN | 10-Q 2026-06-30 (08-06 제출) | 2026-01-01~06-30 | 35 | 9 | 8 | 6 | 7 | 1 | 3 | 1 | value / none / value / not_determinable |
| BZH | 10-Q 2026-06-30 (08-07 제출) | 2025-10-01~2026-06-30 | 33 | 8 | 7 | 8 | 7 | 1 | 1 | 1 | value / value / none / none |
| BBW | 10-Q 2026-08-01 (09-10 제출) | 2026-02-01~08-01 | 33 | 8 | 5 | 9 | 7 | 1 | 2 | 1 | none / none / none / none |

(섹션 번호 1~7 = 1_results … 7_industry, none = none_presented)

## CMS
- 유동 금융리스: 재무상태표가 "Current portion of long-term debt and finance leases $870"로 합산 표시 → 주석의 장기부채 유동분 $864를 빼 $6 million으로 산출(인쇄값 아님, XBRL 없음). 산출을 허용할지 애매.
- 단기차입금: 연결 유동부채에 notes payable 행이 없고 CP·신용한도 차입 0 → none_presented. companyfacts의 OtherShortTermBorrowings $1M은 장기미지급금 유동분 태그로 판단해 제외.
- NorthStar 재생에너지 사업 철수는 8-K 없이 10-Q Item 5·실적 보도자료로만 공시 → 10-Q 인용으로 4_events에 넣음. 매수자·계약, 2025 가스요금 최종명령은 찾지 못함.
- J.H. Campbell DOE 명령 연장(8/14)·D.C. 항소법원 무효 판결(9/11)은 회사 공시가 없어 미시간 법무장관 보도자료를 regulator로 인용(법무장관이 소송 당사자라 분류가 애매).

## SYY
- 유동성 장기부채(리스 제외): "Current maturities of long-term debt" 1,201에 금융리스 72가 포함(리스 주석) → 1,129로 기재, XBRL 1,201과 다른 이유를 note에 기재. 공시 수치끼리의 차감을 허용할지 애매.
- 단기차입금: CP는 장기 리볼버로 뒷받침돼 장기부채로 분류되고 기말 CP·리볼버 잔액 0 → none_presented.
- JRD 인수(현금 $21.6 billion + 주식 91.5 million주)는 기준일 현재 미완료. 인수자금용 주식·채권 발행 8-K가 많아 4_events가 14건으로 길어짐.
- 3분기 비용 처리 후 4분기 일부 환입된 'legal matter'는 내용·금액 미공시로 제외하고 FTC second request(2026-05-27)를 5_legal에 기재. 정식 CFO 선임 공시는 찾지 못함(임시 CFO 체제).

## NPO
- 조사 창 내 8-K는 5.02(CIO 사임)·5.07(주총)·2.02(실적)뿐. 인수·매각·신용계약·구조조정 공시는 찾지 못함.
- 금융리스: 10-Q에 리스 주석이 없어 2025 10-K의 "finance lease 금액이 중요하지 않아 공시하지 않음" 문구로 none_presented(not_determinable과 경계가 애매).
- 유동성 장기부채 $0.2 million은 금융리스 포함 여부를 확인할 공시가 없어 표시값 그대로 사용(note 기재).
- 리볼버 $130.0 million(2030년 만기)은 장기부채로 분류되어 단기차입금은 none_presented.
- 7_industry는 원 발표기관 통계를 검증하지 못해 생략. 석면 소송은 최신 10-Q에 없어 5_legal은 환경 충당금·TCE 소송으로 구성.

## WYNN
- 3_guidance: 공식 매출·이익 가이던스가 없어 Al Marjan 개장 시점·잔여 출자, 라스베이거스·마카오 capex 전망(1Q vs 2Q 10-Q)만 optional로 기록.
- 유동 금융리스: "Other accrued liabilities"에 섞여 있고 2Q 10-Q에 6/30 수치가 없어 not_determinable(최근 공시치는 2025년 말 $27,810천).
- 단기차입금: 리볼버 2개가 장기부채 안에 표시 → none_presented. 유동성 장기부채 1,428,965천에는 WML 전환사채·전환옵션 파생상품이 포함.
- 5_legal: 구체적 중요 소송 없이 일반 문구만 있어 optional 1건. 조사 창 안 5.02·손상·사이버·감사인 8-K 없음.
- DICJ(마카오 GGR) 원문은 XML이라 인용문이 공백 없이 붙어 있고, 게시일을 확인 못 해 published_date는 null.

## BZH
- 2026-08-06 Dream Finders Homes와 주당 $33.50 현금 합병 계약 → 8/7 실적 발표에서 전망 철회·콜 취소. 특별주총은 10/15(기준일 이후).
- 수치 가이던스는 8-K·10-Q에 없고 4/30 실적 콜에만 있어 MarketBeat 녹취로 인용. '현재 전망'은 철회 사실로 기재.
- 미분류 재무상태표 → 유동성 장기부채·금융리스는 none_presented. 리볼버 $340.0 million(2030년 3월 만기)은 명세 규칙(신용한도 차입=단기차입금)으로 단기차입금 value(비차원 XBRL 없어 xbrl null). 회사가 장기부채로 분류한 NPO·WYNN·SYY의 리볼버와 처리가 달라 가장 애매한 항목.
- 합병 관련 주주소송·정부조사 공시는 찾지 못함(5_legal은 소송충당금 $12.3 million 1건). ir.beazer.com은 403으로 열지 못함.

## BBW
- 영업이익: 손익계산서에 영업이익 행과 OperatingIncomeLoss XBRL이 모두 없어 none_presented(참고용 매출총이익−SG&A=34,825천달러는 note에만). value/not_determinable/none_presented 경계가 애매.
- 단기차입금·유동성장기부채·금융리스: 차입 없음(PNC 회전신용 미인출), 리스는 운용리스뿐 → 모두 none_presented.
- 중요 소송: 10-Q에 Legal Proceedings가 없고 HMRC 관세 분쟁만 공시(회사가 비중대로 판단) → optional로만 기록.
- 업계 통계: 완구 단독 통계가 없어 Census 전체 소매판매(2026년 8월)만 넣음. 출처 URL(marts_current.pdf)은 다음 발표 때 바뀌어 재검증 시 불일치 가능.
- 8-K 2.02 본문에 전년 비교 연도 오기('second quarter of 2026')가 있어 실적은 EX-99.1·10-Q로 인용.

## 공통
- SEC 요청은 식별 User-Agent와 전역 속도제한(약 6회/초)으로 수행. 주가·수익률 자료는 쓰지 않음.
- 리볼버 처리 기준: 회사가 재무상태표에서 장기부채로 분류한 경우는 단기차입금 none_presented, 미분류 재무상태표(BZH)는 명세 규칙에 따라 단기차입금으로 봄.
