# 홈페이지 개선 참고 자료

리트젠(LTZ) 홈페이지 리뉴얼 작업에서 기준으로 삼는 자료입니다. 화면·메뉴·문구·SEO/GEO를 바꿀 때 먼저 확인합니다.

| 파일 | 내용 | 읽는 법 |
|---|---|---|
| `2026-08_B2B_Homepage_Reform_Proposal.pdf` | 「DBD 첫 단계 B2B Homepage 개혁」 제안서 (2026.08, 30쪽). 기존 홈페이지 진단, 벤치마킹, 메뉴·페이지별 화면 구성안 | `pdftotext -layout` 또는 Read 도구의 `pages` 범위 |
| `Homepage_Benchmark_References.pptx` | 참고 사이트 캡처 모음 (12장): GEW, IST, UVER, Excelitas, EYEON | `python-pptx`로 슬라이드 텍스트와 이미지 추출 |
| `2026-11_B2B_Homepage_SEO_GEO_8week_Plan_v3.docx` | B2B 홈페이지 리뉴얼·SEO·GEO 8주 실행 계획 v3 (2026.11.18) | `pandoc -t markdown` |

## 1. 제안서 (2026.08) 핵심

**기존 홈페이지 진단 (lichtzen.com)**: 종합 24/100 (F).
- 프레임(frame) 구조라 검색엔진과 AI가 본문을 거의 읽지 못함.
- 항목별 점수: Technical SEO 18, On-page 28, Content 22, GEO 12, EEAT 48, 해외 B2B 영업 24, 전환(CRO) 18.
- 핵심 문제: 텍스트 부족, 해외 바이어 관점 정보(OEM·납기·수출) 부족, 제품 상세·적용 산업·기술 콘텐츠·FAQ 부족, 메타데이터·URL 체계 미흡, 문의 유도 장치 부족.

**방향**: "작지만 강한 홈페이지(Tiny but Mighty)". 해외 바이어가 홈페이지만 보고 믿고 문의하도록 만든다.

**메뉴 (현실안)**: Home / Why LTZ / Products (적용 분야 포함) / Technology (Custom Engineering 포함) / Global Business / News / Contact.
- 이상안(참고): Home, About, Products, OEM/ODM Center, Technology Center, Quality & Certification, Global Market, Knowledge Center, Resource Center, Case Study, News & Insight, Contact.

**벤치마킹 역할 분담**
- Home·News → IST METZ (첫 화면 메시지, 산업별 진입)
- Why LTZ·Technology → Hönle (기술력·신뢰 요소, AI 친화적 기술 설명)
- Products → Excelitas (제품 상세·사양·적용 산업·다운로드)
- Global Business → IST METZ + GEW
- 따라 하지 말 것: Heraeus(규모), Nordson(라인업 방식)

**Home 구성 (30초 안에 회사 이해)**: Hero → Why LTZ(6개 강점) → Products(4개 카드) → Applications → Technology(4개 기술) → Global Business → News(최근 3건) → Contact(최종 CTA).
- Hero: 대형 장비·현장 이미지 + 2~3줄 가치 제안 + CTA 2개 (Request a Quote / Explore Products).
- Why LTZ 6개: 30+ Years Experience, Customized Engineering, In-house Manufacturing, Reliable Quality, One-stop Service, Global Business Partner.

**페이지별 요점**
- Why LTZ: 회사소개+차별화 통합. 경쟁력·회사 개요·제조 역량·품질(ISO)·R&D. CEO 인사말·조직도·긴 연혁·ESG 등은 별도 페이지 불필요.
- Products: Overview → 카테고리 → 적용 산업 → Why LTZ Products → 카탈로그 다운로드 → 견적 요청.
- Technology: 기술 철학 → 핵심 기술 → Engineering Process (Process Analysis → Concept Design → Engineering → Manufacturing → Factory Testing → Installation → Technical Support) → R&D → 강점 → 기술 자료 → Talk to an Engineer.
- Global Business: "Engineering Solutions Beyond Korea". 서비스 4개(맞춤 엔지니어링, 해외 프로젝트 지원, 해외 설치, 기술 서비스), 지원 산업, 과장 없는 지역 지도, CTA.
- News 비중: Technology Insights 40% / Project & Installation 30% / Exhibitions 20% / Company Updates 10%. 사내 행사 소식은 싣지 않음. 월 1~2건이라도 꾸준히.
- Contact: 필수 입력은 Company, Country, Email, Name, Industry, Inquiry 정도로 최소화. 모든 페이지 오른쪽 아래에 고정 버튼 (Request Quote / Talk to Engineer).

**단계**: v1.0 (~6개월, 30~35쪽) → v1.5 (6개월~, 40~50쪽) → v2.0 (1~2년, 60~80쪽, Case Study·Knowledge Center). 연간 콘텐츠 30~35건.

**주의**: 제안서의 예시 문구(MIR, Optical Measurement & Control, Battery·Automotive 등)는 예시입니다. 실제 리트젠 제품·실적으로 확인한 뒤에만 게시합니다.

## 2. 벤치마킹 PPT 핵심

- 메인: GEW, IST, UVER처럼 UV LED 경화·램프 제조·정밀 검사·컨베이어 공정을 순서대로 보여주는 메인 영상. 실제 제조 역량이 드러나는 기술 중심 화면.
- 메인 소개문 초안: "리트젠은 1995년부터 시작된 30년 경력의, 광원 제작에서 경화·노광·살균·공기정화 응용제품을 개발·직접 제조하는 자외선 시스템 전문기업입니다. 솔루션도 제공합니다."
- 메인에 적용 제품, 간단한 회사 소개, 카탈로그, 기사 노출.
- 제품 탭: Excelitas 방식. 상품 페이지에는 항상 연락 정보를 넣는다.
- 메뉴: Excelitas처럼 솔루션·전문성·기술을 강조하는 사진과 글 배치.
- 적용 분야: EYEON 참고.

## 3. 8주 실행 계획 v3 (2026.11) 핵심

- 목표: 회사 역량 이해 → 검색·AI 검색으로 발견 → 쉬운 문의. CRM·견적·수금 자동화는 직원 전용 모듈.
- 일정: 2주차 M1 기획 확정, 4주차 M2 디자인 승인, 6주차 M3 통합 시연, 8주차 M4 공개.
- 문의: 회원가입 없이 회사명·회신 이메일·요청 내용 3개만 필수. 목적별(램프 교체·소량 제작 / 신규 장비·품질 개선 / OEM) 추가 항목.
- SEO: 페이지별 고유 title·description, canonical, XML 사이트맵, 301 이전, 국문·영문 hreflang, Search Console·Bing·네이버 등록.
- 구조화 데이터: Organization, BreadcrumbList, Product. 가격 0원·가짜 리뷰 금지.
- GEO: 회사 정보 언어별 일치, 질문형 FAQ, 표로 된 사양, 검토일 표시.
- 성능 목표: 초기 JS 압축 150KB 이하, LCP 2.5초·INP 200ms·CLS 0.1 이하.
- 근거 원칙: 1995년 설립·32개국 수출·연간 10억원 이상 수출은 원문·기준연도 확인 후 게시. 회사 존속·영구 공급을 단정하지 않음.

## 4. 두 문서의 차이 (결정 필요)

| 항목 | 제안서 (2026.08) | 8주 계획 v3 (2026.11) |
|---|---|---|
| 상위 메뉴 | Home / Why LTZ / Products / Technology / Global Business / News / Contact | 제품 / 적용 분야 / 맞춤 제작과 OEM / 품질과 신뢰 / 자료와 고객지원 / 회사소개 / 상담과 견적 |
| 기준 독자 | 해외 바이어 중심 (영문 문구 예시) | 국문 우선 + 영문 핵심 6개 페이지 |
| 문의 필수 항목 | Company, Country, Email, Name, Industry, Inquiry | 회사명, 회신 이메일, 요청 내용 3개 |
| 강조점 | Why LTZ, Technology, Global Business | 소량 제작, OEM, 품질 개선 사례 |

두 문서가 다를 때는 최신 문서(8주 계획 v3)를 기본으로 하고, 제안서의 Why LTZ·Technology·Global Business 구성과 벤치마킹 방향을 보강 자료로 씁니다. 메뉴 확정은 담당자 결정이 필요합니다.
