# 1단계 정보 구조안 (승인 요청)

결정된 절충안 메뉴를 기준으로 현재 67페이지를 다시 배치하고 새로 만들 페이지를 정했습니다.
근거 사실은 `docs/reference/company_facts.md`, 검색 의도는 8주 계획 7장과 제안서 10~11쪽 벤치마킹을 따랐습니다.

## 1. 원칙

- **주소는 가능한 한 그대로 둔다.** 메뉴만 다시 묶고, 기존 페이지 주소는 바꾸지 않는다. 테스트 사이트(GitHub Pages)는 서버 이전(301)을 지원하지 않기 때문이다.
- **새 메뉴(맞춤 제작·OEM, 품질·인증)는 새 주소로 만든다.**
- **같은 내용의 페이지는 하나만 남긴다.** `/website/`는 메인과 같은 페이지이므로 메인으로 보낸다.
- 메인은 요약, 각 메뉴는 상세. 모든 페이지 끝에는 그 페이지 목적에 맞는 문의 버튼을 둔다.

## 2. 메뉴 구조

```
제품                      /products/
├─ 전체 제품·조건 검색     /products/                     (기존)
├─ UV 경화 장비            /products/?category=equipment  (기존)
├─ UV LED 시스템           /products/?category=led        (기존)
├─ IR·MIR 건조             /products/?category=ir         (기존)
├─ 램프·광원               /products/?category=lamps      (기존)
├─ 램프 사양 설계(3D)      /lamp/                          (기존)
├─ UV-C 살균               /products/?category=uvc        (기존)
├─ 부품·전원·반사판        /products/?category=components (기존)
├─ 컨베이어 (오성유니콘)   /conveyors/                     (기존)
└─ 제품 선정 가이드        /selection-guide/               (기존)

적용 분야                 /solutions/                     (기존)
├─ 필름·인쇄·코팅          /solutions/film/                (기존)
├─ PCB·전자                /solutions/pcb-printing/        (기존)
├─ 정밀 접합·본딩          /solutions/bonding/             (기존)
├─ IR 가열·건조            /solutions/ir-drying/           (기존)
├─ 디스플레이·반도체 ★     /solutions/display-semiconductor/
├─ 2차전지·자동차 ★        /solutions/battery-automotive/
└─ 살균·의료 ★             /solutions/sterilization/

맞춤 제작·OEM ★           /custom/
├─ 소량·대체 램프 제작 ★   /custom/lamps/
├─ 맞춤 장비 설계·제작 ★   /custom/systems/
└─ OEM 공급 ★              /custom/oem/

기술                      /technology/                    (기존, 보강)
├─ 광원 기술 개요          /technology/
└─ 기술 FAQ ★              /technology/faq/

품질·인증 ★               /quality/
├─ 품질관리·검사 ★         /quality/
├─ 특허·인증               /company/certifications/        (기존 주소 유지)
└─ 품질 개선 사례 ★        /quality/cases/

회사소개 (Why LTZ)        /company/                       (기존, 보강)
├─ 왜 리트젠인가·개요      /company/
├─ 연혁                    /company/history/
├─ 사업부·조직·시설        /company/organization/
├─ 글로벌 비즈니스 ★       /company/global/
└─ 오시는 길               /company/location/
   (인사말·채용은 메뉴에서 빼고 하단 링크로)

자료·고객지원             /support/                       (기존)
├─ 카탈로그·사양 자료      /resources/                     (기존)
├─ 램프 A/S 접수           /support/lamp-as/               (기존)
└─ 소식                    /news/                          (기존 3건)

[상담·견적] 버튼           /contact/                       (기존, 4단계에서 개편)
```

★ = 새 페이지 13개. 새 페이지는 5단계(콘텐츠)에서 회사 자료로 채우고, 그 전까지는 메뉴에 노출하지 않는다.

## 3. 핵심 페이지별 검색 의도와 다음 행동

검색량을 확인한 순위가 아니라 고객 질문 가설입니다. 공개 후 검색 데이터로 검증합니다.

| 페이지 | 고객 질문·검색 의도 (국문 / 영문) | 다음 행동 |
|---|---|---|
| 메인 | 리트젠은 어떤 회사? UV 경화 장비 제조사 / UV curing system manufacturer Korea | 제품 찾기, 상담 |
| 제품 목록 | UV 경화기, UV LED 경화기, MIR 건조기 / UV LED curing system, MIR dryer | 조건 검색, 제품 상세 |
| 램프 상세 | 메탈할라이드 램프, 수은 UV 램프, 갈륨 램프 교체 / metal halide UV lamp replacement | 사양 확인, 교체 문의 |
| 소량·대체 램프 ★ | UV 램프 소량 주문 제작, 단종 램프 대체품 / custom UV lamp small quantity | 사진·치수 첨부 문의 |
| 맞춤 장비 ★ | UV 경화 장비 주문 제작, 질소 퍼지 UV 경화 / custom UV curing line | 공정 조건 문의 |
| OEM ★ | UV 램프 OEM, UV LED 모듈 OEM / UV lamp OEM manufacturer | OEM 조건 문의 |
| 디스플레이·반도체 ★ | UTG OCA UV 경화, 다이싱 테이프 UV / OCA UV LED curing UTG | 사례 확인, 상담 |
| 2차전지·자동차 ★ | 배터리 모듈 IR 경화 오븐, 고체전지 필름 UV / EV battery adhesive curing oven | 사례 확인, 상담 |
| 살균·의료 ★ | 222nm 살균기, UV-C 램프 / far-UVC 222nm | 자료 다운로드, 상담 |
| 기술 FAQ ★ | UV LED와 수은 램프 차이, 램프 수명, 메탈할라이드와 수은 차이 / UV LED vs mercury lamp | 관련 제품, 상담 |
| 품질·인증 ★ | ISO 9001 UV 장비 제조사, CE 인증 / ISO certified UV lamp manufacturer | 인증서 확인 |
| 글로벌 ★ | 해외 수출 실적, 해외 설치 지원 / UV curing supplier export | 해외 문의 |

## 4. 정리할 페이지

| 페이지 | 처리 |
|---|---|
| `/website/` | 메인과 중복 → 메인으로 이동(canonical + 자동 이동), 사이트맵에서 제외 |
| `/company/greeting/` | 메뉴에서 빼고 회사소개 하단 링크 |
| `/company/careers/` | 하단(푸터) 링크로 이동 |
| 얇은 페이지 27개 | 5단계에서 보강하거나 상위 페이지에 합침 |

## 5. 영문 (6단계)

`/en/` 아래 6페이지: `/en/`, `/en/company/`, `/en/products/`, `/en/custom/`, `/en/quality/`, `/en/contact/`. 국문 대응 페이지와 hreflang으로 연결.

## 6. 기존 lichtzen.com 주소 이전 (8단계)

기존 사이트는 프레임 구조이고 클라우드에서 접속이 막혀 전체 주소 목록을 아직 받지 못했다. 공개 전에 기존 주소 목록(`/page/page50` 등)을 받아 새 주소와 1:1로 대응시킨다.
