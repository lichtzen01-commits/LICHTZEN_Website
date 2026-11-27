"""Build the product selection guide (question chips + live candidate list).

Usage: python3 scripts/selection_guide.py deploy/site
Reads the product cards from products/index.html, tags each one with
purpose / material / line, and writes the selector into
selection-guide/index.html between <!--sel:start--> and <!--sel:end-->.
Run before build_langs.py.
"""
import re
import sys
from pathlib import Path

# purpose: cure, dry, clean, replace | material: film, pcb, bond, other | line: conv, roll, spot, lab
# "*" = fits any answer for that question
TAGS = {
    "uv-module-system":        ("cure", "film other", "roll conv"),
    "roll-to-roll-uv-system":  ("cure", "film", "roll"),
    "pcb-print-coating":       ("cure", "pcb", "conv"),
    "conveyor":                ("cure dry", "*", "conv"),
    "low-temperature-uv-system": ("cure", "other", "roll"),
    "compact-uv-system":       ("cure", "pcb bond", "lab conv"),
    "mir-drying-systems":      ("dry", "*", "conv"),
    "oled-amoled-uv-system":   ("cure", "bond", "conv"),
    "bonding-uv-system":       ("cure", "film bond", "conv"),
    "solar-cell-uv-system":    ("cure", "pcb", "lab"),
    "roll-coater-uv-system":   ("cure", "film other", "roll"),
    "film-print-coating":      ("cure", "film", "conv"),
    "display-printing-uv":     ("cure", "film", "conv"),
    "camera-module-bonding":   ("cure", "bond pcb", "conv"),
    "wafer-tape-remover":      ("cure", "pcb", "lab"),
    "roll-surface-treatment":  ("cure", "film", "roll"),
    "three-dimensional-uv":    ("cure", "other", "conv"),
    "double-sided-pcb-uv":     ("cure", "pcb", "conv"),
    "laboratory-uv-system":    ("cure", "*", "lab"),
    "handheld-uv-curing":      ("cure", "pcb bond", "spot"),
    "spot-uv-curing":          ("cure", "bond pcb", "spot"),
    "linear-uv-led":           ("cure", "bond pcb film", "conv"),
    "area-uv-led":             ("cure", "bond pcb", "spot conv"),
    "spot-uv-led":             ("cure", "bond pcb", "spot"),
    "spot-led-applications":   ("cure", "bond pcb", "spot"),
    "mercury-uv-lamp":         ("replace", "*", "*"),
    "metal-halide-uv-lamp":    ("replace", "*", "*"),
    "gallium-uv-lamp":         ("replace", "*", "*"),
    "exposure-lamps":          ("replace", "*", "*"),
    "capillary-gl-lamps":      ("replace", "*", "*"),
    "water-treatment-lamps":   ("clean", "*", "*"),
    "uv-cleaning-lamps":       ("clean", "*", "*"),
    "lamp-accessories":        ("replace", "*", "*"),
    "mir-lamps":               ("dry replace", "*", "*"),
    "nir-lamps":               ("dry replace", "*", "*"),
    "uv-power-supplies":       ("replace", "*", "*"),
    "uv-reflectors":           ("replace", "*", "*"),
    "uv-filters":              ("replace", "*", "*"),
    "far-uvc-lamps":           ("clean", "*", "*"),
    "wonder-ray-254nm":        ("clean", "*", "*"),
    "far-uvc-222nm":           ("clean", "*", "*"),
}

ICON = {
    "cure": '<path d="M12 3v3M5.6 5.6l2.1 2.1M3 12h3M18.4 5.6l-2.1 2.1M21 12h-3"/><path d="M4 17h16M7 21h10"/><path d="M8 13a4 4 0 0 1 8 0"/>',
    "dry": '<path d="M8 4c-2 3 2 4 0 7M12 4c-2 3 2 4 0 7M16 4c-2 3 2 4 0 7"/><rect x="3" y="14" width="18" height="6" rx="2"/>',
    "clean": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    "replace": '<path d="M4 12a8 8 0 0 1 14-5.3L20 9M20 4v5h-5"/><path d="M20 12a8 8 0 0 1-14 5.3L4 15M4 20v-5h5"/>',
}

Q = [
    ("p", "01", "무엇을 하려고 하세요?", [
        ("cure", "경화", "UV로 잉크·코팅·접착제 굳히기"),
        ("dry", "건조·가열", "적외선으로 도료·소재 말리기"),
        ("clean", "살균·세정", "UV-C로 물·공기·표면 처리"),
        ("replace", "램프·부품 교체", "쓰던 램프·전원·반사갓 바꾸기"),
    ]),
    ("m", "02", "어떤 소재·제품인가요?", [
        ("film", "필름·인쇄·코팅", ""),
        ("pcb", "PCB·전자·반도체", ""),
        ("bond", "접착·본딩·디스플레이", ""),
        ("other", "기타·성형품", ""),
    ]),
    ("l", "03", "라인은 어떤 형태인가요?", [
        ("conv", "컨베이어 라인", ""),
        ("roll", "롤·연속 라인", ""),
        ("spot", "스팟·국소 조사", ""),
        ("lab", "실험·소량 생산", ""),
    ]),
]


def chips(key, opts):
    out = []
    for val, label, sub in opts:
        ico = f'<svg aria-hidden="true" viewbox="0 0 24 24">{ICON[val]}</svg>' if key == "p" else ""
        small = f"<small>{sub}</small>" if sub else ""
        out.append(f'<button aria-pressed="false" class="sel-chip{" sel-big" if key == "p" else ""}" data-q="{key}" data-v="{val}" type="button">{ico}<span><strong>{label}</strong>{small}</span></button>')
    return "".join(out)


def build(site: Path):
    prod = (site / "products/index.html").read_text(encoding="utf-8")
    cards = []
    for m in re.finditer(r'<article([^>]*)>(.*?)</article>', prod, re.S):
        attrs, body = m.groups()
        href = re.search(r'href="/products/([^/"]+)/"', body)
        if not href or href.group(1) not in TAGS:
            continue
        slug = href.group(1)
        p, mat, line = TAGS[slug]
        get = lambda a: (re.search(a + r'="([^"]*)"', attrs) or [None, ""])[1]
        body = re.sub(r'<span class="inline-link">.*?</span>', "", body, flags=re.S)
        body = body.replace('loading="lazy"', 'loading="lazy"')
        cards.append(
            f'<article class="sel-card" data-light="{get("data-light")}" data-p="{p}" data-m="{mat}" data-l="{line}" '
            f'data-wave="{get("data-wave")}" data-cooling="{get("data-cooling")}">{body}</article>')

    cards.sort(key=lambda c: 'data-p="cure dry"' in c)  # shared conveyor last
    q_html = "".join(
        f'<fieldset class="sel-q" data-group="{k}"><legend><span>{n}</span>{t}</legend><div class="sel-opts">{chips(k, o)}</div></fieldset>'
        for k, n, t, o in Q)
    more = (
        '<details class="sel-more"><summary>파장·냉각 방식을 알면 더 좁히기</summary>'
        '<fieldset class="sel-q" data-group="w"><legend>파장</legend><div class="sel-opts">'
        + "".join(f'<button aria-pressed="false" class="sel-chip" data-q="w" data-v="{w}" type="button"><span><strong>{w} nm</strong></span></button>' for w in (365, 385, 395, 405))
        + '</div></fieldset><fieldset class="sel-q" data-group="c"><legend>냉각 방식</legend><div class="sel-opts">'
        + "".join(f'<button aria-pressed="false" class="sel-chip" data-q="c" data-v="{v}" type="button"><span><strong>{t}</strong></span></button>' for v, t in (("air", "공랭식"), ("water", "수랭식"), ("natural", "자연 냉각")))
        + "</div></fieldset></details>")
    checklist = "".join(
        f'<label class="sel-check"><input type="checkbox"/><span>{t}</span></label>'
        for t in ("적용 소재와 경화·건조 대상", "조사 폭·면적과 이송 조건", "설치 공간과 냉각·전원 조건", "기존 장비·램프 모델명과 사진"))

    block = (
        '<!--sel:start--><section class="b2b-section sel-section"><div class="container sel-layout" data-selector="">'
        f'<div class="sel-panel">{q_html}{more}'
        '<button class="sel-reset" data-sel-reset="" hidden="" type="button">처음부터 다시 고르기</button>'
        '<button class="sel-float" data-sel-float="" hidden="" type="button"><span>후보 제품 보기</span><strong data-sel-fn="">0</strong></button></div>'
        '<div class="sel-results"><div class="sel-head"><p aria-live="polite" class="sel-count" role="status" data-sel-count="">'
        '<strong data-sel-n="">0</strong><span data-sel-label="">개 제품 · 질문에 답하면 후보가 좁혀집니다</span></p>'
        '<p class="sel-note" data-sel-note="" hidden="">조건에 딱 맞는 제품이 없어 가까운 제품을 보여 드립니다.</p></div>'
        f'<div class="sel-grid">{"".join(cards)}</div>'
        '<div class="sel-cta"><div><h2>이 조건으로 상담받기</h2><p>준비된 정보를 체크하면 문의서에 함께 넘겨 드립니다.</p>'
        f'<div class="sel-checks">{checklist}</div></div>'
        '<a class="button sel-go" data-sel-go="" href="/contact/?need=system">이 조건으로 문의하기<svg aria-hidden="true" viewbox="0 0 24 24"><path d="M4 12h15M13 6l6 6-6 6"></path></svg></a>'
        '<p class="sel-fine">결과는 제품군 단위입니다. 실제 모델의 사양과 조합은 상세 정보 또는 기술 상담에서 확인해 주세요.</p></div>'
        '</div></div></section><!--sel:end-->')

    page = site / "selection-guide/index.html"
    h = page.read_text(encoding="utf-8")
    if "<!--sel:start-->" in h:
        h = re.sub(r"<!--sel:start-->.*?<!--sel:end-->", lambda _: block, h, flags=re.S)
    else:
        h, n = re.subn(r'<section class="b2b-section"><div class="container selection-guide-layout">.*?</aside></div></section>', lambda _: block, h, flags=re.S)
        assert n == 1, "old selection layout not found"
    h = re.sub(r'<p>제품군을 고르고, 확인된 파장·냉각 조건으로 후보 제품을 좁혀 보세요.</p>',
               '<p>질문 세 개에 답하면 맞는 제품이 바로 아래에 좁혀집니다. 파장이나 냉각 방식을 몰라도 괜찮습니다.</p>', h)
    if "selector.js" not in h:
        h = h.replace("</head>", '<script defer="" src="/assets/selector.js?v=20261125b"></script></head>', 1)
    page.write_text(h, encoding="utf-8")
    print("selection guide:", len(cards), "products")


if __name__ == "__main__":
    build(Path(sys.argv[1]))
