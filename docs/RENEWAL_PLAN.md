# 리트젠 B2B 홈페이지 개선 계획

작성일 2026-11-18. 기준 자료는 `docs/reference/` 세 문서(리뉴얼 제안서 2026.08, 벤치마킹 PPT, 8주 실행 계획 v3)입니다.

## 1. 목표

- 해외·국내 구매·기술 담당자가 **30초 안에** 리트젠이 무엇을 만들고 어떤 문제를 해결하는지 이해한다.
- 검색엔진과 AI 검색(ChatGPT·Gemini·Perplexity 등)이 회사·제품·제작 역량을 **읽고 인용**할 수 있다.
- 방문자가 제품·근거를 확인한 뒤 **쉽게 문의**한다 (필수 입력 최소화, 목적별 문의).
- 제안서 진단 점수 **24/100 → 80 이상**을 목표로, 같은 항목으로 단계마다 다시 측정한다.

## 2. 작업 원칙

1. **근거 있는 사실만 게시**: 연혁·수출·매출·인증·고객사·사례는 원문 확인 후 게시. 제안서 예시 문구를 사실처럼 쓰지 않는다.
2. **문서가 다르면 8주 계획 v3 우선**, 메뉴처럼 결정이 필요한 것은 담당자 확인.
3. **작게 바꾸고 바로 확인**: 단계마다 테스트 사이트에 배포 → 담당자 확인 → 다음 단계.
4. **업무 데이터는 공개 저장소에 넣지 않는다**: 고객 PO·견적·클레임·계좌 등.
5. 매 단계 자동 점검: 전 페이지 열기·콘솔 오류·끊긴 링크·이미지·모바일 화면.

## 3. 작업 기반

- 홈페이지 원본: `deploy/site` (67페이지 정적 사이트). 개선은 여기서 직접 한다.
- 영업 시스템 테스트 HTML: `deploy/bundle` (샘플 데이터).
- 테스트 사이트 배치(0단계에서 변경): 루트 `/` = 개선 중인 홈페이지, `/test/` = 영업 시스템 포함 테스트 HTML.

## 4. 단계별 계획

| 단계 | 내용 | 주요 스킬 | 담당자 확인 |
|---|---|---|---|
| **0. 기준선 진단** | 테스트 사이트 배치 정리, 현재 상태 점수화(제안서 7개 항목: Technical SEO·On-page·Content·GEO·EEAT·해외 B2B·CRO), 화면 품질·접근성 진단, 문제 목록 | seo-audit, audit-website-aeo, web-interface-guidelines, impeccable, agent-browser, playwright-skill | 진단 결과 공유 |
| **1. 정보 구조 확정 (M1)** | 메뉴·페이지 목록·URL 표, 페이지별 검색 의도·고객 질문 가설, 기존 URL 이전 대응표 초안 | site-architecture, research-keywords, geo-content-research, front-end-system-design | **메뉴 결정**, 공개할 수치·고객사 결정 |
| **2. 기술 SEO 기반** | 페이지별 고유 title·description(현재 제품 32개가 같은 설명), canonical, OG 태그, JSON-LD(Organization·BreadcrumbList·Product, 가격·리뷰 없음), sitemap.xml·robots.txt, hreflang 구조, 이미지 alt·크기, 성능 예산(초기 JS 150KB) | seo-technical, seo-schema, schema, seo-sitemap, improve-aeo-geo, seo-images | 없음 (기술 작업) |
| **3. 메인·디자인 (M2)** | 메인을 "요약 + 신뢰" 순서로 재구성(Hero → Why LTZ → 제품 → 적용 분야 → 기술 → 글로벌 → 소식 → 문의), 핵심 메시지 확정, 디자인 시스템(DESIGN.md) 정리, 모바일 개선, 겹치는 플로팅 버튼 정리 | design-md, impeccable, design-taste-frontend, ui-ux-pro-max, copywriting, apple-design, gsap-* | **시안 승인** |
| **4. 문의 흐름 (CRO)** | 필수 3개(회사명·이메일·요청 내용), 목적별 분기(램프 교체·소량 제작 / 신규 장비·품질 개선 / OEM), 제품 페이지에서 제품명 자동 전달, 사진·도면 첨부, 모든 페이지 고정 버튼(견적 요청·엔지니어 상담) | cro, signup, copywriting, web-interface-guidelines | 문의 항목 승인 |
| **5. 핵심 콘텐츠** | 소량 제작·OEM·품질과 인증 페이지, 기술 FAQ 6개, 품질 개선 사례 2개, 제품 상세 공통 양식(사양 HTML 표·적용 조건·관련 제품·문의), Technology·Global Business 페이지, 게시 전 사실 검증 | write-seo-geo-content, seo-content-brief, faq-page, audit-content, create-geo-charts, copy-editing | **원고·근거 자료 제공 및 승인** |
| **6. 영문 핵심 6페이지** | 메인·회사소개·제품군·맞춤 제작과 OEM·품질과 인증·문의, 국문 대응 페이지와 hreflang 연결 | seo-hreflang, copywriting | 영문 원고 승인 |
| **7. 통합 검수** | 전 페이지 자동 점검, Core Web Vitals(LCP 2.5초·INP 200ms·CLS 0.1), 접근성, SEO·GEO 재채점, 실무자 5명 사용성 시험(회사 진행) | playwright-skill, seo-audit, seo-performance, audit-website-aeo, javascript-testing-best-practices | 검수 결과 확인 |
| **8. 공개 준비** | lichtzen.com 연결 방식·호스팅 결정, 기존 URL 301 이전, 실제 문의 메일 발송 연결, Search Console·네이버 서치어드바이저·Bing 등록 | seo-google, seo-bing | **공개 승인** |

1~4단계는 기술·구조 작업이라 빠르게 진행할 수 있고, 5~6단계는 회사 자료와 원고 승인 속도에 달려 있습니다.

## 5. 결정 사항 (2026-11-18)

1. **메뉴 구조: 절충안** — 제품 / 적용 분야 / 맞춤 제작·OEM / 기술 / 품질·인증 / 회사소개(Why LTZ) / 자료·고객지원 + 상담·견적 버튼.
2. **재무 수치: 수출실적만 남김** — 2025년 수출실적(한국무역협회 증명서 기준)만 게시하고 매출액·영업이익은 뺀다.
3. **고객사 로고: 동의 받음 → 유지.**
4. **핵심 메시지: 새로 제안** — 3단계 시안에서 후보 2~3개를 제시하고 선택한다.

## 6. 회사에서 준비할 자료

- 연혁 원문(설립 연도·사명 변경), 공장·연구소·검사 현장 사진
- 수출 국가 목록과 기준(누적/연도), 수출실적 증명 자료
- 인증서(CE·ISO 등)와 적용 제품·유효기간, 특허 목록
- 소량 제작·OEM 대응 범위, 최소 수량·납기 산정 기준
- 공개 가능한 품질 개선 사례 2건(문제·검토·조치·결과)
- 최신 카탈로그·브로슈어 PDF, 자주 받는 기술 질문

## 7. 진행 방식

- 단계가 끝날 때마다 테스트 사이트에 배포하고 링크와 변경 요약을 공유합니다.
- 진행 상황은 이 문서의 표에 표시합니다.
