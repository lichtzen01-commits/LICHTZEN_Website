"""Apply the approved menu (docs/IA.md) to every page of the static site.

Rewrites the desktop menu, the mobile menu and the footer company links.
Pages without a desktop menu (the 3D lamp configurator) are left alone.
Safe to run repeatedly. When a new page from docs/IA.md gets content, add
it to MENU below and run again.

Usage: python3 scripts/apply_nav.py deploy/site
"""
import glob
import html
import os
import re
import sys

# (label, url, submenu or None, url prefixes that mark this item as current)
MENU = [
    ("제품", "/products/", [
        ("전체 제품·조건 검색", "/products/", "용도·광원·조건으로 전체 제품 찾기"),
        ("UV 경화 장비", "/products/?category=equipment", "컨베이어형·인라인 UV 경화 시스템"),
        ("UV LED", "/products/?category=led", "스팟·라인형 UV LED 광원"),
        ("램프·광원", "/products/?category=lamps", "UV 램프와 교체용 광원"),
        ("IR·MIR 건조", "/products/?category=ir", "적외선 가열·건조 램프와 장치"),
        ("UV-C 소독기", "/uvc-disinfection/", "Wonder-Ray® 254nm·Far-UVC 222nm 소독 솔루션"),
        ("부품·전원·반사판", "/products/?category=components", "전원장치·반사판·교체 부품"),
        ("컨베이어 라인업", "/conveyors/", "경화·건조 공정용 컨베이어"),
        ("램프 사양 설계 (3D)", "/lamp/", "램프 사양을 3D로 설계해 보기"),
        ("제품 선정 가이드", "/selection-guide/", "공정 조건에 맞는 광원 고르기"),
    ], ("/products/", "/conveyors/", "/lamp/", "/selection-guide/", "/uvc-disinfection/")),
    ("적용 분야", "/solutions/", [
        ("전체 적용 분야", "/solutions/", "공정별 적용 분야 한눈에 보기"),
        ("필름·인쇄·코팅", "/solutions/film/", "필름·인쇄물·코팅층 UV 경화"),
        ("PCB·전자", "/solutions/pcb-printing/", "PCB 인쇄와 전자부품 공정"),
        ("정밀 접합·본딩", "/solutions/bonding/", "접착제 경화와 카메라 모듈 본딩"),
        ("IR 가열·건조", "/solutions/ir-drying/", "적외선으로 빠르게 가열·건조"),
    ], ("/solutions/",)),
    ("기술", "/technology/", [
        ("기술 개요", "/technology/", "광원별 특징과 검토 기준"),
        ("UV 램프 시스템", "/technology/#uv-lamp", "램프 종류·출력·길이와 냉각·전원 조건"),
        ("UV LED 시스템", "/technology/#uv-led", "스팟·선형·면형과 파장·냉각 조건"),
        ("IR 가열·건조", "/technology/#ir", "소재·목표 온도에 맞춘 광원과 설비"),
        ("검토 기준 비교", "/technology/#compare", "같은 기준으로 제품 비교하기"),
    ], ("/technology/",)),
    ("회사소개", "/company/", [
        ("회사 개요", "/company/", "1995년 설립, 리트젠 소개"),
        ("연혁", "/company/history/", "설립부터 지금까지의 발자취"),
        ("품질·인증", "/company/certifications/", "ISO 인증과 등록 특허"),
        ("사업부·조직·시설", "/company/organization/", "사업부 구성과 생산 시설"),
        ("오시는 길", "/company/location/", "군포 본사 위치와 교통"),
    ], ("/company/",)),
    ("자료·고객지원", "/support/", [
        ("고객지원 안내", "/support/", "A/S·자료·문의 창구 안내"),
        ("사양·카탈로그", "/resources/", "카탈로그 PDF와 제품 사양"),
        ("램프 A/S 접수", "/support/lamp-as/", "사용 중인 램프 점검·수리 신청"),
        ("자주 묻는 질문", "/support/#faq", "자주 받는 질문과 답변"),
        ("도면·자료 요청", "/contact/?product=자료요청", "도면·사양서 요청하기"),
    ], ("/support/", "/resources/", "/news/", "/privacy/")),
]
CHEVRON = "⌄"
# picture shown on the right of the dropdown for each submenu link
IMAGES = {
 "/products/": "/assets/optimized/c0d798d248f8.webp",
 "/products/?category=equipment": "/assets/optimized/b624afd8869d.webp",
 "/products/?category=led": "/assets/optimized/86a255b9898c.webp",
 "/products/?category=lamps": "/assets/media/lamps/mercury-uv-lamps-640.webp",
 "/products/?category=ir": "/assets/media/mir-700.webp",
 "/products/?category=uvc": "/assets/optimized/5ef1a6a7eb47.webp",
 "/uvc-disinfection/": "/assets/media/uvc/lineup.webp",
 "/products/?category=components": "/assets/optimized/26a8372c9a06.webp",
 "/conveyors/": "/assets/optimized/be08f86da32c.webp",
 "/lamp/": "/assets/optimized/80ace7326584-main.webp",
 "/selection-guide/": "/assets/optimized/a23e62ee0e74.webp",
 "/solutions/": "/assets/legacy/d103cbec0791.webp",
 "/solutions/film/": "/assets/optimized/6630029cc0f6-main.webp",
 "/solutions/pcb-printing/": "/assets/optimized/a23e62ee0e74.webp",
 "/solutions/bonding/": "/assets/optimized/a68c5ad53dfe.webp",
 "/solutions/ir-drying/": "/assets/media/ir-drying-oven.webp",
 "/technology/": "/assets/optimized/a23e62ee0e74.webp",
 "/technology/#uv-lamp": "/assets/media/lamps/mercury-uv-lamps-640.webp",
 "/technology/#uv-led": "/assets/optimized/86a255b9898c.webp",
 "/technology/#ir": "/assets/media/mir-700.webp",
 "/technology/#compare": "/assets/optimized/80ace7326584-main.webp",
 "/company/": "/assets/optimized/c0d798d248f8.webp",
 "/company/history/": "/assets/media/lamps/mercury-uv-lamps-640.webp",
 "/company/certifications/": "/assets/legacy/6e7e5d0cf7dc.webp",
 "/company/organization/": "/assets/optimized/497c210d2080.webp",
 "/company/location/": "/assets/optimized/9134e478c103.webp",
 "/support/": "/assets/optimized/a23e62ee0e74.webp",
 "/resources/": "/assets/optimized/news-uvc-brochures.webp",
 "/support/lamp-as/": "/assets/media/lamps/mercury-uv-lamps-640.webp",
 "/support/#faq": "/assets/optimized/80ace7326584-main.webp",
 "/contact/?product=자료요청": "/assets/optimized/26a8372c9a06.webp"
}
GROUP_IMAGE = {"/company/": "/assets/optimized/9134e478c103.webp", "/support/": "/assets/media/lamps/mercury-uv-lamps-640.webp"}



def card_fit(src):
    """Photos far from the 16:9 card shape (tall or square ones such as the building) are shown whole, not cropped."""
    try:
        from PIL import Image
        w, h = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "deploy", "site", src.lstrip("/"))).size
    except Exception:
        return ""
    return " is-whole" if abs(w / h - 16 / 9) > 0.45 else ""

def current_index(url):
    # the longest matching prefix wins
    best, best_len = None, 0
    for i, (_, _, _, prefixes) in enumerate(MENU):
        for p in prefixes:
            if url.startswith(p) and len(p) > best_len:
                best, best_len = i, len(p)
    return best


def desktop(url):
    cur = current_index(url)
    parts = []
    for i, (label, href, sub, _) in enumerate(MENU):
        aria = ' aria-current="page"' if i == cur else ""
        link = f'<a{aria} href="{html.escape(href)}">{label}</a>'
        if not sub:
            parts.append(link)
            continue
        # a card per link: picture, name and one line about it
        cards = "".join(
            f'<a class="mega-card" href="{html.escape(h)}"><span class="mega-card-img{card_fit(IMAGES.get(h) or GROUP_IMAGE.get(href, ""))}"><img alt="" decoding="async" height="225" loading="lazy" src="{IMAGES.get(h) or GROUP_IMAGE.get(href, "")}" width="400"/></span>'
            f'<strong>{t}</strong><small>{d}</small></a>' for t, h, d in sub)
        parts.append(f'<div class="nav-group">{link}<button aria-expanded="false" aria-label="{label} 하위 메뉴" '
                     f'class="nav-expand" type="button">{CHEVRON}</button><div class="nav-panel nav-mega nav-cards">'
                     f'<div class="mega-head"><strong>{label}</strong></div>'
                     f'<div class="mega-cards">{cards}</div></div></div>')
    return '<nav aria-label="주 메뉴" class="desktop-nav">' + "".join(parts) + "</nav>"


def mobile(url):
    # phone menu: each group opens like an accordion and lists the same pages as the desktop dropdown
    cur = current_index(url)
    parts = []
    for i, (t, h, sub, _) in enumerate(MENU):
        here = ' aria-current="page"' if i == cur else ""
        if not sub:
            parts.append(f'<a{here} href="{html.escape(h)}">{t}</a>')
            continue
        links = "".join(f'<a href="{html.escape(sh)}">{st}</a>' for st, sh, _ in sub)
        parts.append(f'<details class="mobile-group"{" open" if i == cur else ""}><summary{here}>{t}</summary><div class="mobile-sub">{links}</div></details>')
    return f'<nav aria-label="모바일 메뉴" class="mobile-nav" id="mobile-nav">{"".join(parts)}<a href="/contact/">문의하기</a></nav>'


FOOTER_COMPANY_OLD = re.compile(r'(<div><strong>리트젠</strong>)(.*?)(</div>)', re.S)
FOOTER_COMPANY_NEW = ('<a href="/company/">회사 개요</a><a href="/company/history/">연혁</a>'
                      '<a href="/company/certifications/">품질·인증</a><a href="/company/greeting/">인사말</a>'
                      '<a href="/company/careers/">채용</a><a href="/company/location/">오시는 길</a>'
                      '<a href="https://www.youtube.com/@LICHTZEN" rel="noopener noreferrer" target="_blank">YouTube ↗</a>')


def main(root):
    changed = 0
    for path in sorted(glob.glob(os.path.join(root, "**", "index.html"), recursive=True)):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        if rel.startswith("tools/"):
            continue
        url = "/" + rel[: -len("index.html")]
        h = open(path, encoding="utf-8").read()
        new = re.sub(r'<nav aria-label="주 메뉴" class="desktop-nav">.*?</nav>', lambda m: desktop(url), h, count=1, flags=re.S)
        new = re.sub(r'<nav aria-label="모바일 메뉴"[^>]*>.*?</nav>', lambda m: mobile(url), new, count=1, flags=re.S)
        new = FOOTER_COMPANY_OLD.sub(lambda m: m.group(1) + FOOTER_COMPANY_NEW + m.group(3), new, count=1)
        if 'class="desktop-nav"' in new and "/assets/nav-mega.js" not in new:
            new = new.replace("</head>", '<script defer src="/assets/nav-mega.js"></script></head>', 1)
        if new != h:
            open(path, "w", encoding="utf-8").write(new)
            changed += 1
    print(f"menu applied to {changed} pages")


if __name__ == "__main__":
    main(sys.argv[1])
