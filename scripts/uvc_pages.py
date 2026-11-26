"""Build the UV-C disinfection pages (Wonder-Ray® 254nm / Far-UVC 222nm).

Usage: python3 scripts/uvc_pages.py deploy/site      (run before apply_nav.py)

Content comes from LICHTZEN's own UV-C disinfection microsite (product data, KC registration, KTL/KTR/KCL
test reports, clinical evaluation report 2024). Images were extracted from it and upscaled into
assets/media/uvc/. The page shell (head, header, footer) is copied from an existing product page, so the
regular pipeline (apply_nav, seo_enhance, place_videos, footer, build_langs) finishes each page.
"""
import html
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "deploy/site"
M = "/assets/media/uvc/"
ARROW = '<svg aria-hidden="true" viewbox="0 0 24 24"><path d="M4 12h15M13 6l6 6-6 6"></path></svg>'
SRC_CLINIC = "출처: 「의료환경에 적합한 자외선소독기 개발과 임상평가보고서」(2024년)"
HUB, P254, P222, EVID, APPS = ("/uvc-disinfection/", "/products/wonder-ray-254nm/", "/products/far-uvc-222nm/",
                               "/uvc-disinfection/evidence/", "/uvc-disinfection/applications/")

e = html.escape


def img(name, alt, w, h, cls="", eager=False):
    c = f' class="{cls}"' if cls else ""
    lazy = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img alt="{e(alt)}"{c} decoding="async" height="{h}" {lazy} src="{M}{name}.webp" width="{w}"/>'


def link(href, text, cls="inline-link"):
    return f'<a class="{cls}" href="{href}">{text}{ARROW}</a>'


def contact(product, label="상담 문의하기"):
    return link(f"/contact/?need=system&product={e(product)}", label, "button uvc-cta-btn")


def top(eyebrow, h1, lead, crumbs):
    bc = '<a href="/">HOME</a>' + "".join(
        f'<svg aria-hidden="true" viewbox="0 0 24 24"><path d="m9 5 7 7-7 7"></path></svg>'
        + (f'<a href="{u}">{t}</a>' if u else f"<span>{t}</span>") for t, u in crumbs)
    return (f'<section class="page-top uvc-top"><div class="container"><nav aria-label="현재 위치" class="breadcrumb">{bc}</nav>'
            f'<div class="eyebrow">{eyebrow}</div><h1>{h1}</h1><p>{lead}</p></div></section>')


def section(inner, cls="", sid=""):
    i = f' id="{sid}"' if sid else ""
    return f'<section class="b2b-section uvc-sec {cls}"{i}><div class="container">{inner}</div></section>'


def head(eyebrow, h2, p=""):
    return f'<div class="section-head uvc-head"><span class="eyebrow">{eyebrow}</span><h2>{h2}</h2>{f"<p>{p}</p>" if p else ""}</div>'


def faq(items, title="자주 묻는 질문"):
    return section(f'<div class="faq-list uvc-faq" id="faq"><h2>{title}</h2>'
                   + "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items) + "</div>")


def stat_cards(rows):
    return '<div class="uvc-stats">' + "".join(
        f'<div class="uvc-stat"><strong>{big}</strong><span>{what}</span><small>{src}</small></div>' for big, what, src in rows) + "</div>"


def table(head_row, rows, cls="uvc-table"):
    th = "".join(f"<th>{c}</th>" for c in head_row)
    body = "".join("<tr>" + f"<th>{r[0]}</th>" + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>" for r in rows)
    return f'<div class="table-scroll"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


CLINIC = (
    '<div class="uvc-clinic">'
    + "".join(f'<figure>{img(n, cap, 1200, 900)}<figcaption><strong>{cap}</strong><span>{sub}</span></figcaption></figure>'
              for n, cap, sub in (("chart-before", "청소 전", "다양한 표면에서 오염균이 검출됨"),
                                  ("chart-after", "일반 청소 후", "일부 오염이 남을 수 있음"),
                                  ("chart-uvc", "UV-C 소독 후", "오염 수준이 크게 감소함")))
    + f'</div><p class="uvc-src">종합병원 4곳 · 장기요양기관 2곳 임상평가 · {SRC_CLINIC}</p>')

TEST_ROWS = [("Log 5.23", "대장균(E. coli) 살균소독력 · 99.999% 이상 저감", "KTR 시험성적서 TBK-2024-007080 (2024.11.25)"),
             ("Log 5.18", "황색포도상구균(S. aureus) 살균소독력 · 99.999% 이상 저감", "KTR 시험성적서 TBK-2024-007080 (2024.11.25)"),
             ("99.9%", "부유바이러스 저감율 (phi X174)", "KTL 성적서 24-072340-01-1 (2024.12.04)"),
             ("99.9%", "부유세균 저감율 (S. epidermidis)", "KTL 성적서 24-072340-01-2 (2024.12.04)"),
             ("0.007 ppm", "측정 오존 농도 · 실내 기준 0.06 ppm 이하", "KTL 성적서 24-072340-01-3 (2024.12.10)"),
             ("KC", "방송통신기자재등의 적합등록", "등록번호 R-R-LU0-WonderRay-W12 (2025.04.29)")]

BS8628 = table(["병원균", "15분 노출 (Log 감소)", "30분 노출 (Log 감소)"],
               [("S. aureus", "6.0", "6.0"), ("E. coli", "5.0", "5.0"), ("C. difficile", "5.0", "5.0"),
                ("C. albicans", "5.6", "6.0"), ("M. peregrinum", "5.1", "5.8")])

COMPARE = table(["구분", "254nm · Wonder-Ray®-S8W4", "222nm · Far-UVC"], [
    ("사용 가능 환경", "사람이 없는 공간 전용", "사람이 있는 공간에서도 사용 가능"),
    ("살균 방식", "고출력 직접 조사", "표피까지만 도달하는 저침투 조사"),
    ("살균력", "&gt;99.999% (5 Log)", "E. coli · S. enterica 99.9%"),
    ("피부 TLV", "10 mJ/cm²", "479 mJ/cm²"),
    ("소비 전력", "1,850W", "6W ~ 30W (타입별)"),
    ("대표 형태", "이동형 소독 장비", "고정형 소형 램프 모듈"),
    ("대표 적용처", "병실, 무인 소독이 가능한 시설 공간", "진료실, 사무실, 카페, 대중교통 등 상주 공간")])

SPACES = [  # name, image, wavelength, text
    ("요양시설", "care-home", "254nm / 222nm", "장기요양기관 2곳에서 임상평가를 완료했습니다. 병실은 254nm으로 소독하고, 공용 공간과 식당처럼 어르신이 머무는 곳은 222nm Far-UVC로 재실 중에도 상시 살균할 수 있습니다."),
    ("학교", "school", "222nm", "교실처럼 하루 종일 사람이 머무는 공간은 222nm Far-UVC로 재실 중에도 공기와 표면을 살균할 수 있습니다. 공간 크기에 맞춰 타입 A·B·C 중 적합한 모델을 선택합니다."),
    ("사무실", "office", "222nm", "직원들이 상주하는 사무 공간에서도 222nm Far-UVC로 업무 중단 없이 공기와 표면을 지속적으로 관리할 수 있습니다."),
    ("대중교통", "transit", "222nm", "버스, 지하철처럼 좁고 사람이 계속 오가는 공간에는 컴팩트한 222nm 타입 A·B 모듈이 적합합니다. 탑승객이 있는 상태에서도 작동합니다."),
    ("화장실", "restroom", "222nm", "이용자가 끊이지 않는 공용 화장실은 222nm Far-UVC로 공간을 비우지 않고도 공기와 표면을 관리할 수 있습니다."),
    ("식·음료 사업장", "food-plant", "222nm", "작업자가 상주하는 식품·음료 제조 및 가공 라인에서도 222nm Far-UVC로 공정을 멈추지 않고 공기와 표면을 관리할 수 있습니다."),
    ("피트니스센터", "fitness", "222nm", "운동 기구를 여러 이용자가 함께 사용하는 피트니스센터에서도 222nm Far-UVC로 운영 중단 없이 공기와 표면을 관리할 수 있습니다."),
    ("축사", "livestock", "222nm", "가축이 있는 축사에서도 222nm Far-UVC를 지속적으로 운영할 수 있어 가축 전염병 예방 목적으로 활용할 수 있습니다."),
    ("카페·상업공간", "public-space", "222nm", "영업 시간 내내 고객과 직원이 함께 있는 카페, 매장에는 222nm 타입 B가 적합합니다. 영업을 중단하지 않고 살균 환경을 유지할 수 있습니다."),
    ("치과·의료기관", "hospital-lobby", "254nm / 222nm", "진료 중에는 222nm Far-UVC로 진료실 공기와 표면을 살균하고, 진료가 없는 시간에는 254nm Wonder-Ray®로 공간 전체를 소독하는 이중 전략을 권장합니다."),
]


# motion graphics (animated by CSS in site.css, paused off screen by uvc-motion.js)
SKIN_FX = (
    '<div class="uvc-fx uvc-skin" aria-label="222nm과 254nm의 피부 도달 깊이 비교 애니메이션"><div class="sk-stage"><div class="sk-pic">'
    '<svg viewbox="0 0 1000 400" role="img" aria-hidden="true"><defs>'
    '<linearGradient id="gv" gradientUnits="userSpaceOnUse" x1="0" y1="70" x2="0" y2="155"><stop offset="0" stop-color="#d4caff"/><stop offset="1" stop-color="#6c5ce7"/></linearGradient>'
    '<linearGradient id="gc" gradientUnits="userSpaceOnUse" x1="0" y1="70" x2="0" y2="290"><stop offset="0" stop-color="#b5f2f5"/><stop offset="1" stop-color="#14a3ac"/></linearGradient></defs>'
    '<rect class="sk-air" x="0" y="0" width="1000" height="130"/>'
    '<rect class="sk-dead" x="0" y="130" width="1000" height="45"/>'
    '<rect class="sk-epi" x="0" y="175" width="1000" height="115"/>'
    '<g class="sk-basal">' + "".join(f'<circle cx="{x}" cy="278" r="11"/>' for x in range(150, 1000, 30)) + '</g>'
    '<rect class="sk-derm" x="0" y="290" width="1000" height="110"/>'
    '<line class="sk-beam v" x1="250" y1="72" x2="250" y2="150" stroke="url(#gv)"/>'
    '<line class="sk-beam c" x1="560" y1="72" x2="560" y2="282" stroke="url(#gc)"/>'
    '<circle class="sk-hit v" cx="250" cy="152" r="12"/><circle class="sk-hit c" cx="560" cy="280" r="14"/>'
    '</svg>'
    '<span class="sk-tag v" style="left:25%">222nm</span><span class="sk-tag c" style="left:56%">254nm</span>'
    '<span class="sk-layer" style="top:38%">각질층</span><span class="sk-layer" style="top:56%">표피</span>'
    '<span class="sk-layer" style="top:70%">기저세포</span><span class="sk-layer" style="top:87%">진피</span></div>'
    '<div class="sk-call v" style="left:28.5%;top:38%"><span class="uvc-wave is-222">222nm Far-UVC</span><strong>각질층에서 흡수</strong>'
    '<p>피부 바깥의 죽은 세포층에서 대부분 흡수되어 살아있는 세포에 거의 닿지 않습니다. 사람이 있는 공간에서도 사용할 수 있습니다.</p></div>'
    '<div class="sk-call c" style="left:59.5%;top:70%"><span class="uvc-wave">254nm UV-C</span><strong>살아있는 세포까지 도달</strong>'
    '<p>미생물 DNA에 강하게 작용해 빠르게 살균하지만 사람의 살아있는 세포까지 닿으므로 사람이 없는 공간에서만 사용합니다.</p></div>'
    '</div></div>')

ROOM_FX = (
    '<figure class="uvc-fx uvc-room" aria-label="360° 모션 감지와 UV-C 조사 애니메이션">'
    '<svg viewbox="0 0 420 300" role="img">'
    '<rect class="rm-floor" x="10" y="10" width="400" height="280" rx="18"/>'
    '<rect class="rm-bed" x="40" y="40" width="96" height="150" rx="12"/><rect class="rm-pillow" x="52" y="50" width="72" height="28" rx="8"/>'
    '<rect class="rm-bed" x="290" y="40" width="96" height="150" rx="12"/><rect class="rm-pillow" x="302" y="50" width="72" height="28" rx="8"/>'
    '<g class="rm-uv"><circle class="rm-ring" cx="213" cy="160" r="40"/><circle class="rm-ring r2" cx="213" cy="160" r="40"/><circle class="rm-ring r3" cx="213" cy="160" r="40"/></g>'
    '<g class="rm-sweep"><path d="M213 160 L213 40 A120 120 0 0 1 317 100 Z"/></g>'
    '<circle class="rm-dev" cx="213" cy="160" r="20"/><circle class="rm-core" cx="213" cy="160" r="8"/>'
    '<g class="rm-person"><circle cx="0" cy="-16" r="9"/><rect x="-9" y="-5" width="18" height="26" rx="8"/></g>'
    '<g class="rm-alert"><rect x="120" y="226" width="186" height="34" rx="17"/><text x="213" y="248">인체 감지 · 램프 차단</text></g>'
    '<g class="rm-on"><rect x="140" y="226" width="146" height="34" rx="17"/><text x="213" y="248">UV-C 소독 중</text></g>'
    '</svg><figcaption>360° 모션 센서가 사람의 접근을 감지하면 UV 조사 중이라도 램프 전원을 즉시 차단합니다.</figcaption></figure>')


def space_cards(items, more=True):
    return '<div class="uvc-spaces">' + "".join(
        f'<article class="uvc-space">{img(i, n + " 적용 예시", 1400, 1050)}<div><span class="uvc-wave">{w}</span><h3>{n}</h3>'
        + (f"<p>{t}</p>" if more else "") + "</div></article>" for n, i, w, t in items) + "</div>"


def two_solutions():
    card = lambda image, w, tag, title, lead, body, models, href: (
        f'<article class="uvc-sol" data-wave="{w}"><div class="uvc-sol-img">{img(image, title, 862, 1400)}</div><div class="uvc-sol-body">'
        f'<span class="uvc-wave">{tag}</span><h3>{title}</h3><strong>{lead}</strong><p>{body}</p><small>{models}</small>'
        f'{link(href, "제품 자세히 보기")}</div></article>')
    return ('<div class="uvc-sols">'
            + card("wonder-ray-s8w4", "254", "신속한 공간 소독", "254nm UV-C 자외선 소독기", "사람이 잠시 비운 공간",
                   "병실, 중환자실, 격리실, 요양시설 등 사람이 잠시 비운 공간을 짧은 시간에 빠르고 효과적으로 소독합니다.",
                   "Wonder-Ray®-S8W4 (표준형) · Wonder-Ray®-S8 (소형)", P254)
            + card("far-uvc-type-a", "222", "지속적인 공간 살균", "222nm Far-UVC 자외선 소독기", "사람이 머무는 공간",
                   "병원 로비, 학교, 사무실, 대중교통처럼 사람이 머무는 공간에서 공기와 표면을 지속적으로 살균합니다.",
                   "Wonder-Ray® Far-UVC · 타입 A · B · C", P222)
            + "</div>")


def hub():
    body = top("UV-C DISINFECTION", "UV-C 자외선 소독 솔루션",
               "254nm UV-C로 비운 공간을 빠르게 소독하고, 222nm Far-UVC로 사람이 머무는 공간을 계속 관리합니다. "
               "1995년부터 UV 광원을 만들어 온 리트젠의 Wonder-Ray® 시리즈입니다.",
               [("UV-C 소독 솔루션", "")])
    body += section(f'<div class="uvc-hero">{img("lineup", "Wonder-Ray 254nm 소독기와 Far-UVC 222nm 모듈", 1400, 1050, eager=True)}'
                    '<div><span class="eyebrow">PRODUCT LINE UP</span><h2>병원부터 일상까지, 공간에 맞는 자외선 소독</h2>'
                    '<p>공간을 비울 수 있는지, 사람이 계속 머무는지에 따라 알맞은 제품이 다릅니다. 254nm는 무인 공간의 신속한 소독에, '
                    '222nm Far-UVC는 유인 공간의 지속적인 살균에 맞춰 설계했습니다.</p>'
                    + stat_cards([("&gt;99.999%", "254nm 살균력 (5 Log)", "BS 8628:2022 기준 자체시험"),
                                  ("99.9%", "부유바이러스·부유세균 저감", "KTL 시험성적서 (2024.12)"),
                                  ("0.007 ppm", "측정 오존 농도", "실내 기준 0.06 ppm 이하")])
                    + "</div></div>", "uvc-first")
    body += section(head("SOLUTIONS", "상황에 맞는 두 가지 UV-C 솔루션") + two_solutions())
    body += section(head("HOW IT WORKS", "같은 UV-C, 다른 도달 깊이", "254nm는 미생물 DNA에 강하게 작용해 빠르게 살균하지만 사람의 살아있는 세포까지 닿고, 222nm는 피부 바깥에서 흡수되어 사람이 있는 공간에서도 쓸 수 있습니다.") + SKIN_FX, "uvc-dark")
    body += section(head("WHICH SPACE", "어떤 공간을 소독하시나요?", "공간의 사용 방식에 따라 적합한 자외선 소독 방식이 달라집니다.")
                    + '<div class="uvc-choose">'
                    f'<a href="{P254}" class="uvc-pick">{img("ward", "UV-C 소독기가 놓인 병실", 1200, 1600)}<span class="uvc-wave">254nm 추천</span><h3>사람이 잠시 비운 공간</h3>'
                    '<p>병실 · 중환자실 · 격리실 · 요양시설 · 수술실</p><strong>짧은 시간 안에 공간 전체를 빠르게 소독합니다.</strong></a>'
                    f'<a href="{P222}" class="uvc-pick is-222">{img("hospital-lobby", "사람이 머무는 병원 대기실", 1200, 900)}<span class="uvc-wave">222nm 추천</span><h3>사람이 머무는 공간</h3>'
                    '<p>병원 로비 · 학교 · 사무실 · 대중교통 · 상업공간</p><strong>사람이 있는 동안에도 공기와 표면을 살균합니다.</strong></a></div>', "pale")
    body += section(head("CLINICAL EVIDENCE", "일반 청소로 놓칠 수 있는 부분까지",
                         "사람이 직접 하는 청소만으로는 손이 닿지 않거나 놓치는 부분이 생길 수 있습니다. 254nm UV-C 소독으로 청소 후 남을 수 있는 오염을 추가로 관리합니다.")
                    + CLINIC + link(EVID, "시험·임상 근거 자세히 보기"))
    body += section(head("APPLICATIONS", "적용 공간") + space_cards(SPACES[:8], more=False) + link(APPS, "적용 공간 자세히 보기"), "pale")
    why = (("/assets/media/lamps/mercury-uv-lamps-640.webp", "리트젠 UV 램프", "1995", "SINCE", "1995년부터 쌓은 광원 기술", "UV 램프, MIR 램프, UV 경화·노광 시스템, UV LED를 개발해 온 광원 설계·시스템 기술로 UV-C 공간 살균 솔루션을 만듭니다."),
           (M + "lineup.webp", "Wonder-Ray 254nm 소독기와 Far-UVC 222nm 모듈", "254 · 222", "nm", "공간에 맞는 두 가지 파장", "254nm 단파장 UV-C는 무인 공간 소독에, 222nm Far-UVC는 유인 공간의 지속적인 관리에 맞춰 제공합니다."),
           (M + "cert-kc.webp", "방송통신기자재등 적합등록", "KC", "KTL · KTR", "시험과 평가로 확인한 기술", "KC 적합등록, KTL·KTR 시험성적서, 종합병원·장기요양기관 임상평가로 효과와 안전성을 확인했습니다."))
    body += section(head("WHY LICHTZEN", "왜 리트젠인가") + '<div class="uvc-why">' + "".join(
        f'<article><div class="uvc-why-img"><img alt="{e(alt)}" decoding="async" loading="lazy" src="{src}"/>'
        f'<span class="uvc-why-num"><b>{num}</b><small>{sub}</small></span></div><div class="uvc-why-body"><h3>{t}</h3><p>{d}</p></div></article>'
        for src, alt, num, sub, t, d in why) + "</div>", "pale")
    body += faq([
        ("254nm UV-C와 222nm Far-UVC는 어떻게 다른가요?", "254nm UV-C는 미생물 DNA 흡수율이 높은 파장으로 짧은 시간에 강력하게 살균하지만 인체에도 작용하므로 사람이 없는 공간에서만 사용합니다. 222nm Far-UVC는 피부 표피의 각질층에서 대부분 흡수되어 피부 TLV가 479 mJ/cm²(254nm는 10 mJ/cm²)로, 사람이 있는 공간에서도 지속적으로 사용할 수 있습니다."),
        ("Wonder-Ray® 254nm 소독기를 사람이 있을 때 사용해도 되나요?", "아니요. 254nm 소독기는 반드시 사람이 없는 공간에서만 작동해야 합니다. 360° 모션 감지 센서가 인체·동물을 감지하면 UV 조사 중이라도 램프 전원을 즉시 차단하고, 비상 정지 버튼으로 언제든 작동을 멈출 수 있습니다."),
        ("한 번 소독하는 데 시간이 얼마나 걸리나요?", "병실 크기와 구조에 맞는 적정 조사 시간을 시뮬레이션으로 산출해 사용하며, 권장 시간은 30분 이상입니다. BS 8628:2022 기준 자체시험에서 15분 노출만으로 S. aureus 6.0 Log, E. coli 5.0 Log 감소를 확인했습니다."),
        ("소독 중 오존이 발생하지 않나요?", "Wonder-Ray®는 오존이 발생할 수 있는 특정 파장을 차단하도록 설계했습니다. KTL 시험(2024.12.10)에서 측정된 오존 농도는 0.007 ppm으로, 실내 오존 기준 0.06 ppm의 약 12% 수준입니다."),
        ("어떤 인증과 시험을 받았나요?", "방송통신기자재등의 적합등록(KC, R-R-LU0-WonderRay-W12), KTR 살균소독력 시험(TBK-2024-007080), KTL 부유바이러스·부유세균·오존 시험, 기능특허 10-2771631, 디자인특허 30-1329825를 보유하고 있습니다."),
        ("보증 기간은 어떻게 되나요?", "기기 무상 A/S 보증은 1년, 램프 사용 보증시간은 5,000시간입니다. 222nm Far-UVC 램프는 사용 환경에 따라 최대 약 8,000시간까지 사용할 수 있습니다.")])
    return body


def p254():
    body = top("254nm UV-C", "Wonder-Ray® 254nm UV-C 자외선 소독기",
               "사람이 잠시 비운 병실과 시설을 빠르고 효과적으로 소독하는 이동형 UV-C 소독기입니다.",
               [("UV-C 소독 솔루션", HUB), ("254nm UV-C 소독기", "")])
    body += ('<div class="container"><section class="product-overview uvc-overview" data-light="uvc"><div class="product-main-image">'
             + img("wonder-ray-s8w4", "Wonder-Ray S8W4 표준형 UV-C 소독기", 862, 1400, eager=True)
             + '</div><div class="product-summary"><span class="light-tag">UV-C</span><div class="eyebrow">Wonder-Ray® Series</div>'
             '<h2>신속한 공간 소독</h2><p>상부 4개·하부 8개, 총 12개의 254nm UV-C 램프로 병실 전체에 조사량을 고르게 전달하고 음영 구역을 최소화하도록 설계했습니다.</p>'
             '<dl class="key-info"><dt>제품군</dt><dd>UV-C 자외선 소독기</dd><dt>모델</dt><dd>Wonder-Ray®-S8W4 (표준형) · Wonder-Ray®-S8 (소형)</dd>'
             '<dt>살균력</dt><dd>&gt;99.999% (5 Log, 표준형)</dd><dt>인증</dt><dd>KC 적합등록 · 기능특허 · 디자인특허</dd></dl>'
             + contact("Wonder-Ray 254nm UV-C 소독기", "이 제품 문의하기") + "</div></section></div>")
    body += section(head("WHY UV-C", "일반 청소로 놓칠 수 있는 부분까지",
                         "254nm UV-C 자외선 소독으로 일반 청소 후 남을 수 있는 오염까지 추가로 관리합니다.")
                    + '<div class="uvc-clinic is-photo">' + "".join(
                        f'<figure>{img(n, c, 1400, 1050)}<figcaption><strong>{c}</strong><span>{s}</span></figcaption></figure>'
                        for n, c, s in (("clean-before", "청소 전 실내 측정 환경", "다양한 표면에서 오염 확인"),
                                        ("clean-after", "일반 청소 후", "청소 후에도 일부 오염이 남을 수 있음"),
                                        ("uvc-after", "UV-C 소독 후", "잔존 오염 수준이 크게 감소")))
                    + f'</div><p class="uvc-src">종합병원 4곳 · 장기요양시설 2곳 임상평가 · {SRC_CLINIC}</p>')
    steps = (("장비를 배치합니다", "소독할 공간에 Wonder-Ray®를 이동·배치합니다."),
             ("원하는 방식으로 소독을 설정합니다", "스크린 터치, 리모컨, 모바일, 태블릿으로 소독 시간을 설정합니다."),
             ("소독을 시작합니다", "설정을 확인한 후 UV-C 소독을 시작합니다."),
             ("소독이 완료됩니다", "설정된 시간이 지나면 소독이 완료되고, 공간을 다시 사용할 수 있습니다."))
    body += section(head("HOW TO USE", "어떻게 사용하나요?") + '<ol class="uvc-steps">' + "".join(
        f'<li>{img(f"step{i + 1}", t, 1150, 840)}<span>STEP {i + 1}</span><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(steps))
        + '</ol><p class="uvc-src">* 정확한 소독 시간은 공간 크기와 사용 조건에 따라 달라질 수 있습니다.</p>', "pale")
    feats = (("360° 모션 감지", "UV 조사 중 인체가 감지되면 램프 전원을 차단하는 안전 기능입니다."),
             ("날개형 상부 램프", "상부까지 UV-C를 조사해 공간의 사각지대를 줄입니다."),
             ("적정 조사량 제공", "공간의 크기와 구조를 고려해 UV-C 조사 조건을 설정합니다."),
             ("이동과 보관을 고려한 구조", "자동 상승·하강 구조와 접이식 설계로 이동과 보관이 편리합니다."),
             ("비산방지 설계", "램프 파손 시 유리 조각의 비산을 줄이는 필름을 적용했습니다."),
             ("이동 편의 바퀴", "작은 턱이나 문턱도 수월하게 넘을 수 있는 바퀴 구조로 병실 간 이동이 편리합니다."))
    body += section(head("KEY FEATURES", "Wonder-Ray® 주요 기능", "안전성과 사용 편의성을 고려한 의료환경 UV-C 소독 시스템")
                    + '<div class="uvc-feat"><div class="uvc-size">'
                    + f'<figure>{img("s8w4-stored", "Wonder-Ray S8W4 보관 시", 764, 1240)}<figcaption>보관 시 <strong>Ø66 × 159cm</strong></figcaption></figure>'
                    + f'<figure>{img("s8w4-open", "Wonder-Ray S8W4 작동 시", 662, 1102)}<figcaption>작동 시 <strong>Ø115 × 225cm</strong></figcaption></figure>'
                    + '</div><ul class="uvc-list">' + "".join(f"<li><strong>{t}</strong><span>{d}</span></li>" for t, d in feats) + "</ul></div>")
    body += section(head("SAFETY", "사용 환경을 고려한 안전 설계") + ROOM_FX + '<ul class="uvc-list is-grid">' + "".join(
        f"<li><strong>{t}</strong><span>{d}</span></li>" for t, d in (
            ("인체 감지 센서", "UV 조사 중 사람의 접근을 감지하면 전원을 자동 차단합니다."),
            ("비상 정지 기능", "예상치 못한 상황에서 장비를 즉시 정지할 수 있습니다."),
            ("상태 표시등", "백색(대기) · 청색 점멸(소독 대기) · 청색 점등(소독 중) · 적색 점등(오류, 완전 정지) · 적색 점멸(오류 알람, 일정 시간 후 재가동)."),
            ("오존 억제", "오존이 발생할 수 있는 특정 파장을 차단해 소독 후에도 실내 오존 농도를 기준치(0.06 ppm) 이하로 유지합니다."),
            ("KC 인증", "국내 KC 적합등록을 받은 제품으로 안전 및 적합성 기준을 충족합니다."),
            ("사용 수칙", "반드시 사람이 없는 공간에서만 작동하고, 작동 중에는 기기를 직접 바라보거나 신체를 노출하지 마세요.")))
        + "</ul>", "pale")
    body += section(head("CLINICAL &amp; TEST DATA", "시험과 데이터로 확인된 UV-C 성능") + stat_cards(TEST_ROWS)
                    + "<h3 class=\"uvc-h3\">살균력 시험 (BS 8628:2022)</h3>" + BS8628
                    + '<p class="uvc-src">대상 장비: Wonder-Ray®-S8W4 · 측정위치: 수평면, 거리 2m, 높이 1m · 자체시험</p>' + link(EVID, "시험·임상 근거 자세히 보기"))
    body += section(head("APPLICATION", "어떤 공간에 사용할 수 있나요?", "사람이 잠시 비운 공간을 신속하게 소독해야 할 때") + '<div class="uvc-rooms">' + "".join(
        f"<figure>{img(i, n, w, h)}<figcaption>{n}</figcaption></figure>" for n, i, w, h in (
            ("병실", "ward", 1200, 1600), ("중환자실", "icu", 750, 1000), ("격리실", "isolation", 1000, 750),
            ("요양시설", "care-home", 1000, 750), ("식품관", "food-hall", 1000, 750))) + "</div>", "pale")
    body += section(head("SPECIFICATION", "Wonder-Ray® Series 제품 사양") + '<div class="uvc-models">'
                    + f'<figure>{img("wonder-ray-s8w4", "Wonder-Ray S8W4", 862, 1400)}<figcaption><strong>Wonder-Ray®-S8W4</strong> 표준형 · 램프 12개(상부 4·하부 8)</figcaption></figure>'
                    + f'<figure>{img("wonder-ray-s8", "Wonder-Ray S8", 862, 1400)}<figcaption><strong>Wonder-Ray®-S8</strong> 소형 · 램프 4개(105cm)</figcaption></figure></div>'
                    + table(["항목", "Wonder-Ray®-S8W4 (표준형)", "Wonder-Ray®-S8 (소형)"], [
                        ("램프 타입 (살균파장)", "UV-C 램프 (254nm)", "UV-C 램프 (254nm)"),
                        ("램프 길이 × 수량", "상부 40cm × 4개 / 하부 105cm × 8개", "105cm × 4개"),
                        ("살균력", "&gt;99.999% (5 Log, 거리 2m)", "99.99% 이상 (거리 1m)"),
                        ("제품 크기", "작동 시 Ø115 × 225cm · 보관 시 Ø66 × 159cm", "Ø52 × 160cm"),
                        ("소비 전력", "1,850W (AC220V)", "AC220V · 소비전력은 상담 시 안내"),
                        ("조작 방법", "기본: 터치패널 · 리모컨 / 옵션: 태블릿 · 스마트폰", "터치패널 · 리모컨"),
                        ("안전 대책", "모션 센서 (인체·동물) · 비상 정지 버튼", "모션 센서 (인체·동물) · 비상 정지 버튼"),
                        ("제품 인증", "KC 적합등록", "KC 적합등록"),
                        ("램프 사용 보증시간", "5,000시간", "5,000시간"),
                        ("무상 A/S 보증", "기기 1년", "기기 1년"),
                        ("지적재산권", "기능특허 10-2771631 · 디자인특허 30-1329825", "—")])
                    + '<p class="uvc-src">* 상부 날개 램프가 펼쳐지는 공간에는 장비 파손·고장을 막기 위해 장애물이 없어야 합니다.</p>')
    body += faq([
        ("Wonder-Ray® 254nm 소독기는 사람이 있을 때 사용할 수 있나요?", "아니요. 254nm UV-C는 인체에도 강하게 작용하므로 반드시 사람이 없는 공간에서만 작동해야 합니다. 360° 모션 감지 센서가 인체·동물을 감지하면 즉시 램프 전원을 차단합니다."),
        ("표준형(S8W4)과 소형(S8)은 어떻게 고르나요?", "표준형은 날개형 상부 램프를 포함해 램프 12개로 병실 전체를 소독하며 거리 2m에서 99.999% 이상 살균력을 확인했습니다. 소형은 105cm 램프 4개로 거리 1m에서 99.99% 이상 살균력을 갖춰 좁은 공간에 적합합니다."),
        ("소독 시간은 어떻게 정하나요?", "병실 크기와 구조에 맞는 적정 조사 시간을 시뮬레이션으로 산출하며 권장 시간은 30분 이상입니다. 터치패널·리모컨, 옵션으로 태블릿·스마트폰에서 설정할 수 있습니다."),
        ("램프 수명과 보증은 어떻게 되나요?", "램프 사용 보증시간은 5,000시간이며 누적 사용시간이 본체에 표시됩니다. 기기 무상 A/S 보증 기간은 1년입니다.")])
    return body


def p222():
    body = top("222nm FAR-UVC", "Wonder-Ray® Far-UVC 222nm 자외선 소독기",
               "사람이 있는 순간에도 공간 위생은 계속됩니다. 222nm Far-UVC로 사람이 머무는 공간의 공기와 표면을 지속적으로 관리합니다.",
               [("UV-C 소독 솔루션", HUB), ("222nm Far-UVC 소독기", "")])
    body += ('<div class="container"><section class="product-overview uvc-overview" data-light="uvc"><div class="product-main-image">'
             + img("far-uvc-type-a", "Far-UVC 222nm 타입 A 모듈", 1400, 1366, eager=True)
             + '</div><div class="product-summary"><span class="light-tag">UV-C</span><div class="eyebrow">Wonder-Ray® Far-UVC</div>'
             '<h2>지속적인 공간 살균</h2><p>작은 공간에 맞게 설계된 컴팩트한 222nm Far-UVC 모듈입니다. 공간 크기에 따라 타입 B(실내 공간)·타입 C(넓은 공간)로도 구성할 수 있습니다.</p>'
             '<dl class="key-info"><dt>제품군</dt><dd>Far-UVC 자외선 소독기</dd><dt>파장</dt><dd>222nm (Far-UVC)</dd>'
             '<dt>타입 A</dt><dd>DC 12V · 6W · 40 × 60 × 70mm</dd><dt>살균력</dt><dd>E. coli · S. enterica 99.9% 저감 (KCL)</dd></dl>'
             + contact("Wonder-Ray Far-UVC 222nm", "이 제품 문의하기") + "</div></section></div>")
    body += section(head("WHY FAR-UVC", "사람이 머무는 공간을 위한 222nm") + '<ul class="uvc-list is-grid">' + "".join(
        f"<li><strong>{t}</strong><span>{d}</span></li>" for t, d in (
            ("사람이 있는 공간에 적합", "사람이 이용하는 공간의 지속적인 위생 관리에 활용됩니다."),
            ("공기와 표면을 함께 관리", "공기와 표면의 위생 관리를 지속적으로 보완해 더 깨끗한 환경을 유지합니다."),
            ("공간에 맞는 설치와 운영", "설치 높이, 조사 조건, 공간 환경을 고려해 다양한 공간에 적용할 수 있습니다."),
            ("시험자료로 확인한 성능", "공인 시험기관의 시험자료와 데이터를 바탕으로 성능을 확인했습니다.")))
        + "</ul>")
    body += section(head("SAFETY BASIS", "피부 표피에서 흡수되는 파장",
                         "222nm은 표피의 죽은 각질 세포층에서 대부분 흡수되어 살아있는 기저세포와 눈에 도달하는 양이 매우 적습니다.")
                    + SKIN_FX + '<div class="uvc-tlv">' + "".join(
                        f'<div class="uvc-bar"><span>{lab}</span><div><i style="--v:{min(100, v / 4.79):.1f}%"></i><b>{v} mJ/cm²</b></div></div>'
                        for lab, v in (("피부 · 222nm", 479), ("피부 · 254nm", 10), ("눈 · 222nm", 161), ("눈 · 254nm", 6)))
                    + '</div><p class="uvc-src">TLV(허용 노출 한계치)는 ACGIH(미국 산업위생전문가협의회)가 제시하는 자외선 노출 한계 기준입니다. '
                      '실제 적용은 조사량, 설치 높이, 운용 시간 등 사용 조건을 함께 고려합니다.</p>', "pale")
    body += section(head("TEST &amp; DATA", "시험으로 확인한 222nm Far-UVC 성능")
                    + stat_cards([("99.9%", "대장균 (E. coli) 저감", "시험조건: 30cm · 13분"),
                                  ("99.9%", "살모넬라균 (S. enterica) 저감", "시험조건: 30cm · 13분")])
                    + '<div class="uvc-petri">' + "".join(f'<figure>{img(n, c, 1400, 1400)}<figcaption><strong>{c}</strong><span>{s}</span></figcaption></figure>'
                                                       for n, c, s in (("petri-before", "Far-UVC 조사 전", "세균이 많이 관찰됨"),
                                                                       ("petri-after", "Far-UVC 조사 후", "세균이 현저히 감소함")))
                    + '</div><p class="uvc-src">한국건설생활환경시험연구원(KCL) 시험 결과 기반</p>')
    body += section(head("SPECIFICATION", "제품 사양")
                    + table(["모델", "적용 장소", "소비전력"], [("타입 A", "작은 공간", "~6W"), ("타입 B", "실내 공간", "~12W"), ("타입 C", "넓은 공간", "~30W")])
                    + '<h3 class="uvc-h3">타입 A 상세 사양</h3>'
                    + table(["항목", "타입 A"], [("파장", "222nm (Far-UVC)"), ("입력 전원", "DC 12V"), ("소비 전력", "6W"),
                                                ("UV-C 광 세기", "500 μW/cm² (거리 5cm) · 30 μW/cm² (거리 30cm)"), ("크기", "40 × 60 × 70mm"),
                                                ("램프 사용 보증시간", "5,000시간 (사용 환경에 따라 최대 약 8,000시간)"), ("무상 A/S 보증", "기기 1년")])
                    + '<p class="uvc-src">* 타입 B·C의 상세 사양(입력 전원, 광 세기, 수명 등)은 상담 시 안내해 드립니다.</p>', "pale")
    body += section(head("APPLICATION", "사람이 머무는 다양한 공간에 적용할 수 있습니다")
                    + space_cards([s for s in SPACES if s[2] == "222nm"][:6], more=False) + link(APPS, "적용 공간 자세히 보기"))
    body += section(head("COMPARE", "254nm · 222nm 비교", "공간과 상황에 맞는 파장을 한눈에 비교해 보세요.") + COMPARE
                    + link(P254, "254nm Wonder-Ray® 소독기 보기") + " " + link("/products/far-uvc-lamps/", "Far-UVC 엑시머 램프(광원) 보기"), "pale")
    body += faq([
        ("Far-UVC 222nm는 사람이 있는 공간에서 사용해도 되나요?", "222nm는 피부 표피의 각질층에서 대부분 흡수되어 피부 TLV가 479 mJ/cm²로 254nm(10 mJ/cm²)보다 여유가 큽니다. ACGIH 기준 안에서 사람이 있는 공간에서도 지속적으로 작동할 수 있으며, 제품별 권장 설치 거리와 조사 범위를 지켜 설치해야 합니다."),
        ("타입 A·B·C는 어떻게 다른가요?", "타입 A는 작은 공간(~6W), 타입 B는 실내 공간(~12W), 타입 C는 넓은 공간(~30W)용입니다. 공간 크기에 맞는 모델을 선택하면 더 효과적으로 살균할 수 있습니다."),
        ("살균 효과는 어떻게 확인했나요?", "한국건설생활환경시험연구원(KCL) 시험에서 거리 30cm, 13분 조사 조건으로 대장균(E. coli)과 살모넬라균(S. enterica)이 각각 99.9% 저감되었습니다."),
        ("램프는 얼마나 사용할 수 있나요?", "램프 사용 보증시간은 5,000시간이며 사용 환경에 따라 최대 약 8,000시간까지 사용할 수 있습니다. 기기 무상 A/S 보증 기간은 1년입니다.")])
    return body


def evidence():
    body = top("TEST &amp; CERTIFICATION", "UV-C 소독기 시험·인증 근거",
               "BS 8628:2022 살균력 시험, 종합병원·장기요양기관 임상평가, KTL·KTR·KCL 공인 시험과 KC 적합등록으로 확인한 결과입니다.",
               [("UV-C 소독 솔루션", HUB), ("시험·인증 근거", "")])
    body += section(head("STERILIZATION TEST", "살균력 시험 (BS 8628:2022)", "유럽표준 BS 8628:2022에 따른 자체시험 결과입니다. 측정위치: 수평면, 거리 2m, 높이 1m.")
                    + BS8628 + '<p class="uvc-src">대상 장비: Wonder-Ray®-S8W4 · 살균력 99.999% 이상</p>', "uvc-first")
    body += section(head("CLINICAL EVALUATION", "임상평가 결과", "종합병원 4곳, 장기요양기관 2곳에서 진행한 임상평가 결과입니다.")
                    + '<p class="uvc-lead">종합병원 중환자실 1인실 7곳을 포함한 실제 병원 현장에서, 청소만 했을 때보다 UV-C 소독 후 바닥면과 각 접촉 표면의 오염균 수가 '
                      '검출 한계 수준까지 크게 감소하는 것을 확인했습니다. 특히 바닥면은 청소 후에도 오염균이 높게 남는 경향을 보였으나, UV-C 소독 후에는 모든 측정 지점에서 '
                      '균일하게 낮은 수준을 유지했습니다.</p>' + CLINIC, "pale")
    body += section(head("ACCREDITED TESTS", "공인 시험성적서", "한국산업기술시험원(KTL), 한국화학융합시험연구원(KTR)의 공인 시험 결과입니다.") + stat_cards(TEST_ROWS))
    docs = (("cert-patent", "등록특허 · 자외선을 이용한 살균기", "등록번호 10-2771631"),
            ("cert-kc", "방송통신기자재등 적합등록", "R-R-LU0-WonderRay-W12 · 모델 LTZ-WonderRay-W12"),
            ("cert-ktl-virus", "KTL 부유바이러스 저감 시험", "결과 99.9%"),
            ("cert-ktl-bacteria", "KTL 부유세균 저감 시험", "결과 99.9%"),
            ("cert-ktl-ozone", "KTL 오존 발생 관련 시험", "결과 최대 0.007 ppm"),
            ("cert-ktr", "KTR 살균소독력 시험", "TBK-2024-007080"))
    body += section(head("CERTIFICATES &amp; IP", "제품 인증과 지적재산권") + '<div class="uvc-docs">' + "".join(
        f'<figure>{img(n, t, 1400, 1980)}<figcaption><strong>{t}</strong><span>{s}</span></figcaption></figure>' for n, t, s in docs)
        + '</div><p class="uvc-src">디자인특허 등록번호 30-1329825</p>', "pale")
    body += section(head("OZONE", "오존 관련 데이터", "오존이 발생할 수 있는 특정 파장을 차단하는 설계입니다.")
                    + stat_cards([("0.007 ppm", "측정 오존 발생 농도", "KTL 시험, 2024.12.10"), ("0.06 ppm 이하", "실내 오존 농도 기준", "측정값은 기준치의 약 12% 수준")])
                    + '<p class="uvc-lead">Wonder-Ray®는 오존이 발생할 수 있는 특정 파장을 차단해 공기 중 오존 발생을 억제합니다. 램프에는 특수 필름을 코팅해 외부 충격에 의한 파손을 줄이고, 유사시 사람을 보호합니다.</p>')
    body += section(head("SAFETY GUIDE", "사용 안전 가이드", "제품별로 권장되는 사용 환경과 안전 수칙입니다.") + '<div class="uvc-guide">'
                    + "<div><h3>Wonder-Ray®-S8W4 (254nm)</h3><ul>" + "".join(f"<li>{x}</li>" for x in (
                        "반드시 사람이 없는 공간에서만 작동하세요.", "작동 중에는 기기를 직접 바라보거나 신체 일부를 노출하지 마세요.",
                        "병실 크기와 구조에 맞는 적정 조사 시간을 시뮬레이션으로 산출해 사용하세요 (권장 30분 이상).",
                        "기기 무상 A/S 보증 기간은 1년, 램프 사용 보증시간은 5,000시간이며 누적 사용시간이 본체에 표시됩니다.")) + "</ul></div>"
                    + "<div><h3>Wonder-Ray® Far-UVC (222nm)</h3><ul>" + "".join(f"<li>{x}</li>" for x in (
                        "사람이 있는 공간에서도 사용할 수 있으나, 타입별 권장 설치 거리와 조사 범위를 지켜 설치하세요.",
                        "공간 크기에 맞는 모델(타입 A~C)을 선택하면 더 효과적으로 살균할 수 있습니다.",
                        "램프 사용 보증시간은 5,000시간이며, 사용 환경에 따라 최대 약 8,000시간까지 사용할 수 있습니다. 기기 무상 A/S 보증 기간은 1년입니다.")) + "</ul></div></div>"
                    + '<p class="uvc-src">* 실제 사용 환경에 따라 살균 효과가 다를 수 있습니다.</p>', "pale")
    body += section(head("COMPARE", "254nm · 222nm 비교") + COMPARE + link(HUB, "UV-C 소독 솔루션 보기"))
    return body


def applications():
    body = top("APPLICATIONS", "UV-C 소독 적용 공간", "공간의 사용 방식에 따라 254nm UV-C와 222nm Far-UVC 중 알맞은 솔루션을 제안합니다.",
               [("UV-C 소독 솔루션", HUB), ("적용 공간", "")])
    body += section('<div class="uvc-hosp">' + img("hospital", "병원 적용 사례", 1400, 1867)
                    + '<div><span class="eyebrow">HOSPITAL &amp; HEALTHCARE</span><h2>병원 공간에 맞는 두 가지 자외선 솔루션</h2>'
                    '<p>병실, 중환자실처럼 소독 시간 동안 비워 둘 수 있는 공간은 254nm UV-C로 신속하게 소독합니다. 대기실, 복도처럼 사람이 계속 머무는 공간은 222nm Far-UVC로 지속적인 살균 환경을 만듭니다.</p>'
                    '<div class="uvc-split"><div><span class="uvc-wave">사람이 없는 공간 → 254nm UV-C</span><p>병실 · 중환자실 · 수술실 · 격리실</p>' + link(P254, "254nm 제품 보기") + '</div>'
                    '<div><span class="uvc-wave is-222">사람이 있는 공간 → 222nm Far-UVC</span><p>대기실 · 복도 · 접수공간 · 공용공간</p>' + link(P222, "222nm 제품 보기") + "</div></div></div></div>", "uvc-first")
    body += section(head("BY SPACE", "공간별 추천 솔루션") + space_cards(SPACES), "pale")
    body += faq([
        ("병원에서는 어떤 제품을 써야 하나요?", "병실, 중환자실, 수술실, 격리실처럼 소독 시간 동안 비울 수 있는 공간은 254nm Wonder-Ray® 소독기를, 대기실·복도·접수공간처럼 사람이 계속 머무는 공간은 222nm Far-UVC를 권장합니다."),
        ("사람이 계속 있는 사무실이나 학교에도 쓸 수 있나요?", "네. 222nm Far-UVC는 사람이 있는 동안에도 공기와 표면을 지속적으로 관리할 수 있도록 설계했습니다. 공간 크기에 따라 타입 A·B·C 중 선택합니다."),
        ("축사나 식품 공장에도 적용할 수 있나요?", "네. 가축이 있는 축사와 작업자가 상주하는 식품·음료 제조·가공 라인에서도 222nm Far-UVC를 운영을 멈추지 않고 사용할 수 있습니다.")])
    return body


PAGES = {
    HUB: ("UV-C 자외선 소독기 · Far-UVC 222nm 살균 솔루션 | 리트젠 LICHTZEN",
          "병실은 254nm UV-C 소독기 Wonder-Ray®로 빠르게, 사람이 머무는 공간은 222nm Far-UVC로 지속적으로. KC 적합등록, KTL·KTR 시험, 임상평가로 확인한 리트젠 UV-C 소독 솔루션.", hub),
    P254: ("Wonder-Ray® 254nm UV-C 자외선 소독기 (S8W4·S8) | 리트젠 LICHTZEN",
           "병실·중환자실·격리실을 위한 이동형 254nm UV-C 소독기. 램프 12개, 99.999% 이상(5 Log) 살균력, 360° 모션 감지, 오존 0.007 ppm, KC 적합등록.", p254),
    P222: ("Far-UVC 222nm 자외선 소독기 · 유인 공간 살균 모듈 | 리트젠 LICHTZEN",
           "사람이 있는 공간에서도 쓰는 222nm Far-UVC 소독 모듈. 타입 A(6W)·B·C, E. coli·S. enterica 99.9% 저감(KCL), 피부 TLV 479 mJ/cm².", p222),
    EVID: ("UV-C 소독기 시험성적서·KC 인증·임상평가 | 리트젠 LICHTZEN",
           "Wonder-Ray® UV-C 소독기의 BS 8628:2022 살균력 시험, 종합병원·장기요양기관 임상평가, KTL·KTR 시험성적서, KC 적합등록, 오존 0.007 ppm 데이터.", evidence),
    APPS: ("UV-C 소독 적용 공간 · 병원·요양시설·학교·사무실 | 리트젠 LICHTZEN",
           "병원, 요양시설, 학교, 사무실, 대중교통, 화장실, 식품 공장, 피트니스센터, 축사까지 공간별로 254nm UV-C와 222nm Far-UVC 소독 솔루션을 안내합니다.", applications),
}


def shell(site):
    s = open(os.path.join(site, "products/far-uvc-lamps/index.html"), encoding="utf-8").read()
    a, b = s.split('<main id="main">', 1)
    rest = b.split("</main>", 1)[1]
    a = re.sub(r"<!--seo:start-->.*?<!--seo:end-->", "", a, flags=re.S)
    rest = re.sub(r"<!--videos:start-->.*?<!--videos:end-->", "", rest, flags=re.S)
    return a, rest


def main(site):
    a, rest = shell(site)
    for url, (title, desc, fn) in PAGES.items():
        h = re.sub(r"<title>.*?</title>", f"<title>{e(title)}</title>", a, count=1, flags=re.S)
        h = re.sub(r'<meta content="[^"]*" name="description"\s*/?>', f'<meta content="{e(desc)}" name="description"/>', h, count=1)
        path = os.path.join(site, url.strip("/"), "index.html")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tail = rest.replace("</body>", '<script defer="" src="/assets/uvc-motion.js?v=20261126b"></script></body>', 1)
        open(path, "w", encoding="utf-8").write(h + '<main id="main" class="uvc-page">' + fn() + "</main>" + tail)
    # product catalog: two cards in the UV-C family (read by selection_guide.py too)
    p = os.path.join(site, "products/index.html")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"<!--uvc:start-->.*?<!--uvc:end-->", "", s, flags=re.S)
    card = lambda href, im, w, hh, small, title, desc, search: (
        f'<article class="product-card" data-cooling="" data-light="uvc" data-product-card="" data-product-category="uvc" data-search="{e(search)}" data-shape="" data-wave="">'
        f'<a href="{href}"><div class="card-image"><img alt="{e(title)}" decoding="async" height="{hh}" loading="lazy" src="{M}{im}.webp" width="{w}"/></div>'
        f'<div class="card-body"><span class="light-tag">UV-C</span><small>{small}</small><h3>{title}</h3><p>{desc}</p>'
        f'<span class="inline-link">제품 정보 보기{ARROW}</span></div></a></article>')
    cards = ("<!--uvc:start-->"
             + card(P254, "wonder-ray-s8w4", 862, 1400, "UV-C 자외선 소독기", "Wonder-Ray® 254nm UV-C 소독기",
                    "사람이 잠시 비운 병실·중환자실을 빠르게 소독하는 이동형 UV-C 소독기입니다. 99.999% 이상 살균력과 360° 모션 감지를 갖췄습니다.",
                    "Wonder-Ray S8W4 S8 254nm UV-C 소독기 병실 중환자실 격리실 요양시설 살균 KC")
             + card(P222, "far-uvc-type-a", 1400, 1366, "Far-UVC 자외선 소독기", "Far-UVC 222nm 자외선 소독기",
                    "사람이 머무는 공간에서도 공기와 표면을 지속적으로 살균하는 222nm Far-UVC 모듈입니다. 타입 A·B·C로 공간 크기에 맞춥니다.",
                    "Far-UVC 222nm 소독기 타입 A B C 유인 공간 살균 학교 사무실 대중교통")
             + "<!--uvc:end-->")
    anchor = '<article class="product-card" data-cooling="" data-light="uvc" data-product-card="" data-product-category="uvc"'
    i = s.find(anchor)
    s = s[:i] + cards + s[i:] if i >= 0 else s
    s = re.sub(r'(data-result-count="">)\d+', lambda m: m.group(1) + str(s.count('data-product-card=""')), s, count=1)
    open(p, "w", encoding="utf-8").write(s)
    print("uvc pages:", len(PAGES))


if __name__ == "__main__":
    main(ROOT)
