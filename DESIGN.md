---
name: LICHTZEN B2B website
description: 리트젠 홈페이지 디자인 기준. 산업용 광원·장비 제조사의 신뢰감을 주는 절제된 화면 — 짙은 남색·녹색 바탕의 첫 화면, 흰색·연한 녹회색 본문, 로고에서 온 라임 그린 포인트, 큰 한국어 제목과 넓은 여백.
colors:
  ink: "#17201e"          # 본문 글자, 진한 버튼
  muted: "#66716c"        # 보조 글자 (흰 배경 대비 5.1:1)
  green: "#8bbd3e"        # 로고 라임 그린 — 주요 버튼 배경, 점·선 포인트 (글자색으로 쓰지 않음)
  green-dark: "#477611"   # 녹색 계열 글자·링크 (흰 배경 대비 5.4:1)
  green-text: "#566f36"   # 작은 라벨·번호 (연녹 배경에서도 4.5:1 이상)
  navy: "#101d24"         # 상단 헤더, 첫 화면 바탕
  forest: "#142e24"       # 글로벌 영역 바탕
  line: "#e1e6e1"         # 구분선
  paper: "#f4f6f2"        # 연한 영역 바탕
  paper-green: "#f3f6f0"  # 프로젝트 진행 방식 영역 바탕
  white: "#ffffff"
typography:
  family: '"Pretendard", "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif'
  body: { size: 16px, line-height: 1.7, letter-spacing: -0.035em }
  hero-title: { size: "clamp(40px, 4.4vw, 68px)", weight: 650, line-height: 1.24, letter-spacing: -0.065em }
  h2: { size: 39px, weight: 650, line-height: 1.35, letter-spacing: -0.055em }
  h3: { size: 17-21px, line-height: 1.45-1.5 }
  eyebrow: { size: 11px, weight: 700, letter-spacing: 0.16em, case: upper, english }
  small-label: { size: 9-12px, letter-spacing: 1px }
layout:
  content-width: 1320px
  side-gutter: { desktop: 56px, "≤1200px": 32px, "≤600px": 20px }
  section-padding: { desktop: 100-120px, mobile: 70-80px }
  breakpoints: [1200px, 1100px, 900px, 600px]
components:
  button-primary: "녹색 배경(#8bbd3e) + 진한 글자(#182410), 높이 52px, 화살표 아이콘"
  button-dark: "ink 배경 + 흰 글자"
  button-text: "배경 없는 글자 링크 + 화살표"
  card: "흰 배경, 1px 구분선, 모서리 각진 형태(라운드 최소)"
  floating-cta: "모든 페이지 오른쪽 아래 '상담·견적' 고정 버튼"
---

# LICHTZEN 디자인 기준

## 1. 원칙

1. **사실이 디자인보다 먼저.** 숫자·인증·국가·고객사는 `docs/reference/company_facts.md`에 있는 것만 쓴다. 꾸밈용 가짜 수치, 가짜 후기, 가짜 로고를 쓰지 않는다.
2. **절제된 산업 톤.** 짙은 남색·숲색 바탕과 흰 본문, 포인트는 로고 라임 그린 하나. 그라데이션·네온·유리 효과를 쓰지 않는다.
3. **한 화면, 한 메시지.** 섹션마다 영문 eyebrow(작은 라벨) → 큰 한국어 제목 → 1~2줄 설명 → 내용 → 다음 행동 링크 순서.
4. **모든 페이지는 문의로 끝난다.** 페이지 목적에 맞는 문의 링크를 섹션 끝과 페이지 끝에 둔다.

## 2. 색

녹색 한 가지로 칠하지 않고, 회사 제품(UV·IR 광원)과 연결된 보조 색을 역할별로 나눠 쓴다. (2026-11-19)

| 역할 | 색 | 변수 | 쓰는 곳 |
|---|---|---|---|
| 브랜드 | 라임 `#8bbd3e` | `--green` | 로고, 문의 버튼, 채팅 버튼, 어두운 섹션의 큰 제목, 지도 빛 |
| 구조 | 딥 네이비 `#1b2a36` | `--navy` | 큰 영문 제목, 단계 원(01~06), 아이콘 선, 컨베이어 화살표 |
| 강조 | UV 바이올렛 `#5246b8`(글자) · `#6c5ce7`(선·면) · `#efedfc`(연한 면) | `--uv-ink` `--uv` `--uv-soft` | 작은 영문 라벨, STEP 표시, 강조 숫자, 아이콘의 빛·포인트, 스포트라이트 |
| 열·움직임 | IR 앰버 `#e8912d` · `#fdf0e1` | `--ir` `--ir-soft` | 컨베이어 위 상자, 아이콘의 열·불꽃·도착 표시 (글자로는 쓰지 않음, 대비 부족) |
| 보조 글자 | 슬레이트 `#56606a`, 선 `#5b7083` | `--muted` `--steel` | 설명문, 보조선 |
| 배경 | 차가운 회색 `#f2f4f6` · `#f3f5f8`, 테두리 `#dae1e8` | | 섹션·카드 바탕 (녹색 끼 없는 중립) |

- 글자색은 배경 대비 **4.5:1 이상** (작은 글자 포함). 새 색을 쓰기 전에 대비를 확인한다.
- 라임은 흰 배경 위 글자로 쓰지 않는다(2.2:1). 앰버도 글자로 쓰지 않는다.
- 어두운 바탕(네이비) 위 글자는 흰색, `#c3ea7a`(라임 밝은 톤), `#dde8e0`.
- 한 화면에 라임·바이올렛·앰버를 모두 크게 쓰지 않는다. 라임은 행동(버튼), 바이올렛은 정보 강조, 앰버는 작은 포인트.

## 3. 글자

- 본문 글꼴은 Pretendard 우선이지만 **현재 웹폰트 파일을 불러오지 않아** Noto Sans KR·시스템 글꼴로 표시된다. 공개 전에 Pretendard(OFL 라이선스)를 자체 호스팅할지 결정한다.
- 한국어 줄바꿈은 단어 단위(`word-break: keep-all`). 제목은 의미 단위로 `<br/>`를 넣어 끊는다.
- 영문 eyebrow는 대문자·넓은 자간, 한국어 제목은 좁은 자간(-0.05em 안팎).

## 4. 배치

- 본문 최대 폭 1320px, 좌우 여백 PC 56px / 태블릿 32px / 모바일 20px.
- 섹션 사이 여백은 PC 100~120px, 모바일 70~80px.
- 그리드: 강점·카드 3열 → 태블릿 2~3열 → 모바일 1열. 단계(flow)는 6열 → 3열 → 1열.
- 가로 스크롤은 지도 패널처럼 의도한 곳만.
- 메인은 한 화면에 한 메시지(7화면). PC는 휠·키보드 한 번에 한 화면씩 easeInOutCubic(0.65~1.1초)으로 이동하고, 화면보다 많이 긴 섹션(지도)은 안에서 일반 스크롤. 모바일은 근접 스냅.
- 메인 섹션의 영문 제목은 큰 심볼형(40~82px, 굵게, 딥그린 #4f7d18, 어두운 섹션은 #c3ea7a).
- 단계 표현은 원형 노드(딥그린 #18402c)와 연결선·화살표로 잇는다. 모바일은 세로.
- 버튼: 모서리 14px, 누를 때 살짝 작아지고(0.97) 올렸을 때 떠오름. 고정 버튼은 초록 알약 "문의하기".
- 움직임은 `prefers-reduced-motion`에서 모두 끈다(카드 자동 넘김·로고 흐름·지도 곡선).

## 5. 성능 예산

- 첫 화면 HTML에 큰 인라인 그림을 넣지 않는다. 세계지도처럼 큰 SVG는 `assets/`의 별도 파일로 둔다 (메인 HTML 156KB → 38KB).
- 모바일 LCP 2.5초, CLS 0.1, 초기 JS 150KB 이하. 이미지는 `width`·`height`를 넣는다.

## 6. 접근성

- WCAG AA: 대비 4.5:1, 키보드로 모든 메뉴·버튼·스크롤 영역 접근, `:focus-visible` 표시 유지.
- 아이콘만 있는 버튼은 `aria-label`, 장식 이미지는 `alt=""`.
- 현재 위치 메뉴는 `aria-current="page"`.

## 7. 구현 위치

- 공통 스타일: `deploy/site/assets/site.css` (리뉴얼 추가분은 파일 끝 주석 구역)
- 메뉴: `scripts/apply_nav.py` · 검색용 정보: `scripts/seo_enhance.py` + `docs/seo/pages.json`
