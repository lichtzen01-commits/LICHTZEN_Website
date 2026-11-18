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
        ("전체 제품·조건 검색", "/products/"),
        ("UV 경화 장비", "/products/?category=equipment"),
        ("UV LED", "/products/?category=led"),
        ("램프·광원", "/products/?category=lamps"),
        ("IR·MIR 건조", "/products/?category=ir"),
        ("UV-C 살균", "/products/?category=uvc"),
        ("부품·전원·반사판", "/products/?category=components"),
        ("컨베이어 라인업", "/conveyors/"),
        ("램프 사양 설계 (3D)", "/lamp/"),
        ("제품 선정 가이드", "/selection-guide/"),
    ], ("/products/", "/conveyors/", "/lamp/", "/selection-guide/")),
    ("적용 분야", "/solutions/", [
        ("전체 적용 분야", "/solutions/"),
        ("필름·인쇄·코팅", "/solutions/film/"),
        ("PCB·전자", "/solutions/pcb-printing/"),
        ("정밀 접합·본딩", "/solutions/bonding/"),
        ("IR 가열·건조", "/solutions/ir-drying/"),
    ], ("/solutions/",)),
    ("기술", "/technology/", None, ("/technology/",)),
    ("품질·인증", "/company/certifications/", None, ("/company/certifications/",)),
    ("회사소개", "/company/", [
        ("회사 개요", "/company/"),
        ("연혁", "/company/history/"),
        ("사업부·조직·시설", "/company/organization/"),
        ("오시는 길", "/company/location/"),
    ], ("/company/",)),
    ("자료·고객지원", "/support/", [
        ("고객지원 안내", "/support/"),
        ("사양·카탈로그", "/resources/"),
        ("램프 A/S 접수", "/support/lamp-as/"),
        ("자주 묻는 질문", "/support/#faq"),
        ("도면·자료 요청", "/contact/?product=자료요청"),
    ], ("/support/", "/resources/", "/news/", "/privacy/")),
]
CHEVRON = "⌄"
# picture shown on the right of the dropdown for each submenu link
IMAGES = {
 "/products/": "/assets/optimized/c0d798d248f8.webp",
 "/products/?category=equipment": "/assets/optimized/b624afd8869d.webp",
 "/products/?category=led": "/assets/optimized/86a255b9898c.webp",
 "/products/?category=lamps": "/assets/optimized/4ead903d2b00.webp",
 "/products/?category=ir": "/assets/optimized/2f4d31281ba9.webp",
 "/products/?category=uvc": "/assets/optimized/5ef1a6a7eb47.webp",
 "/products/?category=components": "/assets/optimized/26a8372c9a06.webp",
 "/conveyors/": "/assets/optimized/be08f86da32c.webp",
 "/lamp/": "/assets/optimized/80ace7326584.webp",
 "/selection-guide/": "/assets/optimized/a23e62ee0e74.webp",
 "/solutions/": "/assets/legacy/d103cbec0791.webp",
 "/solutions/film/": "/assets/optimized/6630029cc0f6.webp",
 "/solutions/pcb-printing/": "/assets/optimized/a23e62ee0e74.webp",
 "/solutions/bonding/": "/assets/optimized/a68c5ad53dfe.webp",
 "/solutions/ir-drying/": "/assets/optimized/2f4d31281ba9.webp"
}
GROUP_IMAGE = {"/company/": "/assets/optimized/9134e478c103.webp", "/support/": "/assets/optimized/4ead903d2b00.webp"}


def current_index(url):
    # the longest matching prefix wins, so /company/certifications/ is 품질·인증
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
        default = IMAGES.get(sub[0][1]) or GROUP_IMAGE.get(href, "")
        links = "".join(f'<a data-mega-img="{IMAGES.get(h) or default}" href="{html.escape(h)}">{t}</a>' for t, h in sub)
        figure = (f'<figure class="mega-figure"><img alt="" decoding="async" height="386" loading="lazy" src="{default}" width="750"/>'
                  f'<figcaption>{sub[0][0]}</figcaption></figure>') if default else ""
        parts.append(f'<div class="nav-group">{link}<button aria-expanded="false" aria-label="{label} 하위 메뉴" '
                     f'class="nav-expand" type="button">{CHEVRON}</button><div class="nav-panel nav-mega">'
                     f'<div class="mega-head"><strong>{label}</strong><a href="{html.escape(href)}">{label} 전체 보기 →</a></div>'
                     f'<div class="mega-links">{links}</div>{figure}</div></div>')
    return '<nav aria-label="주 메뉴" class="desktop-nav">' + "".join(parts) + "</nav>"


def mobile(url):
    cur = current_index(url)
    links = "".join(f'<a{" aria-current=\"page\"" if i == cur else ""} href="{html.escape(h)}">{t}</a>'
                    for i, (t, h, _, _) in enumerate(MENU))
    return f'<nav aria-label="모바일 메뉴" class="mobile-nav" id="mobile-nav">{links}<a href="/contact/">문의하기</a></nav>'


FOOTER_COMPANY_OLD = re.compile(r'(<div><strong>리트젠</strong>)(.*?)(</div>)', re.S)
FOOTER_COMPANY_NEW = ('<a href="/company/">회사 개요</a><a href="/company/history/">연혁</a>'
                      '<a href="/company/certifications/">품질·인증</a><a href="/company/greeting/">인사말</a>'
                      '<a href="/company/careers/">채용</a><a href="/company/location/">오시는 길</a>'
                      '<a href="https://www.youtube.com/@LTZ-LICHTZEN" rel="noopener noreferrer" target="_blank">YouTube ↗</a>')


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
