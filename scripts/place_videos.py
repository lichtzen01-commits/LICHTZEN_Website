"""Place LICHTZEN and Ohsung Unicon YouTube videos on the Korean pages (run before build_langs.py).

Each video is a click-to-play card: a self-hosted thumbnail (assets/media/yt/<id>.webp) and a button that
swaps in the youtube-nocookie player. Blocks are wrapped in markers so the script can be run again."""
import html, re, sys, os

ROOT = sys.argv[1] if len(sys.argv) > 1 else "deploy/site"
LTZ = "https://www.youtube.com/@LICHTZEN"
OSUNG = "https://www.youtube.com/@%EC%A3%BC%EC%98%A4%EC%84%B1%EC%9C%A0%EB%8B%88%EC%BD%98"

V = {  # id: caption
    "N7_0g4ogf5o": "화장품 용기 UV LED 시스템",
    "QYc2a20WjYQ": "고출력 UV/IR LED 시스템",
    "5-M4M0e4zOo": "UV 램프 제작 과정",
    "_c77coPgg1g": "UV & IR LED 경화·건조 복합 시스템",
    "ZOhE1TvRvak": "UV 경화기와 광량계",
    "-GxOH3cY0eI": "UV 경화기 시연",
    "1SqHTXdxlBg": "UV 경화율 측정기",
    "yMkU-Z1KLWM": "INNOCURE 5000",
    "B64i6h5J5Sg": "자동 셔터 UV 램프 하우징",
}
S = {  # Shorts (vertical): id: caption
    "TWGsnTVhUL8": "222nm·254nm Far-UVC 솔루션",
    "VInr9EpVvTQ": "UVC 자동 소독 시스템 시연",
    "XP6SaMh467k": "UV-C 공간 소독 시스템 Wonder-Ray S8W4",
    "a7gt0lDqChA": "병실·요양시설 UV-C 소독",
    "hra2egguWuA": "엑시머 실험 설비",
    "yyjVBhrKgkA": "서랍형 UV LED 경화기",
    "cAnGuVd0UJ4": "NIR 근적외선 건조기",
    "3aboDX-0JE8": "IR 적외선 건조 시스템",
    "7mVt-unxFmA": "IR 적외선 모듈 장치",
    "aXH8LYqsWuo": "자동화 설비",
    "WsRxg4tnlxc": "복합식 LAB용 UV LED 경화기",
    "xohZHZim4KY": "화장품 경화기",
    "OBMfR0mZuF0": "박스 오븐",
    "cWXZpnVgUD8": "셔터 모듈형 경화 시스템",
    "KVBBP9EqYlw": "PCB 포팅용 UV LED 365nm 컨베이어",
    "lH2my7VAdwE": "VCSEL 적외선 LED 가열",
    "2EQn7k3l9To": "금속판 스크린 인쇄 UV LED 경화",
    "jwcLBUZf9ro": "구동 롤러 컨베이어",
    "Wt-tM-dFeoo": "SUS 매쉬 컨베이어",
    "F1OAB2viMIw": "벨트 컨베이어 (수평형·경사형)",
}
OS = {  # more Ohsung Unicon conveyor videos for the gallery
    "ojMoMYT-V9E": "탑 롤러 체인 컨베이어", "-IS_U5IsFdA": "매탑 체인 컨베이어", "AY9bbfSeSMk": "타이밍 벨트 트윈 컨베이어",
    "m_O8l46XFK0": "SUS 탑 체인 컨베이어", "bwN9TGsYDVQ": "PIC 체인 컨베이어", "JohyoZN-NHY": "트윈 링 벨트 컨베이어",
    "kAb-qlXPU9s": "슬라이드 트윈 컨베이어", "womg7SEuVYg": "SUS 구동 롤러 컨베이어", "GYNafncTFWc": "사이드 월 컨베이어",
    "uhTKJWAfLj0": "구동 롤러 + 수평 벨트 컨베이어", "Z8l7eT4u674": "SUS 중간구동 매탑 컨베이어", "WDxPz_TIdv8": "9C형 수평 벨트 컨베이어",
    "GknusP655Kc": "8C형 벨트 컨베이어",
    "nu1Qoe3wMtM": "7C형 수평 벨트 컨베이어", "35-3sQHoGSU": "슬란트(경사) 컨베이어", "oe3rTUgSA-M": "9CC 나이프엣지 중간구동 컨베이어",
}
PAGES = {  # page: (heading, [video ids], [shorts ids], channel)
    "products/three-dimensional-uv/index.html": ("영상으로 보기", ["N7_0g4ogf5o"], ["xohZHZim4KY"], "ltz"),
    "products/linear-uv-led/index.html": ("영상으로 보기", ["QYc2a20WjYQ", "_c77coPgg1g"], [], "ltz"),
    "products/area-uv-led/index.html": ("영상으로 보기", ["QYc2a20WjYQ"], ["yyjVBhrKgkA", "2EQn7k3l9To"], "ltz"),
    "products/mercury-uv-lamp/index.html": ("영상으로 보기", ["5-M4M0e4zOo"], [], "ltz"),
    "products/metal-halide-uv-lamp/index.html": ("영상으로 보기", ["5-M4M0e4zOo"], [], "ltz"),
    "products/compact-uv-system/index.html": ("영상으로 보기", ["-GxOH3cY0eI", "ZOhE1TvRvak"], [], "ltz"),
    "products/spot-uv-curing/index.html": ("영상으로 보기", ["yMkU-Z1KLWM"], [], "ltz"),
    "products/lamp-accessories/index.html": ("영상으로 보기", ["B64i6h5J5Sg"], [], "ltz"),
    "products/uv-reflectors/index.html": ("영상으로 보기", ["B64i6h5J5Sg"], [], "ltz"),
    "products/uv-module-system/index.html": ("영상으로 보기", [], ["cWXZpnVgUD8"], "ltz"),
    "products/laboratory-uv-system/index.html": ("영상으로 보기", [], ["WsRxg4tnlxc", "hra2egguWuA"], "ltz"),
    "products/pcb-print-coating/index.html": ("영상으로 보기", [], ["KVBBP9EqYlw"], "ltz"),
    "products/double-sided-pcb-uv/index.html": ("영상으로 보기", [], ["KVBBP9EqYlw"], "ltz"),
    "products/mir-drying-systems/index.html": ("영상으로 보기", ["_c77coPgg1g"], ["3aboDX-0JE8", "7mVt-unxFmA", "OBMfR0mZuF0"], "ltz"),
    "products/mir-lamps/index.html": ("영상으로 보기", [], ["7mVt-unxFmA", "3aboDX-0JE8"], "ltz"),
    "products/nir-lamps/index.html": ("영상으로 보기", [], ["cAnGuVd0UJ4"], "ltz"),
    "products/far-uvc-lamps/index.html": ("영상으로 보기", [], ["VInr9EpVvTQ", "XP6SaMh467k", "a7gt0lDqChA", "TWGsnTVhUL8"], "ltz"),
    "products/conveyor/index.html": ("오성유니콘 컨베이어 영상", ["nu1Qoe3wMtM", "35-3sQHoGSU"], ["F1OAB2viMIw", "Wt-tM-dFeoo", "jwcLBUZf9ro"], "osung"),
    "solutions/ir-drying/index.html": ("영상으로 보기", ["_c77coPgg1g"], ["3aboDX-0JE8", "OBMfR0mZuF0", "cAnGuVd0UJ4", "lH2my7VAdwE"], "ltz"),
    "solutions/pcb-printing/index.html": ("영상으로 보기", ["N7_0g4ogf5o"], ["KVBBP9EqYlw", "2EQn7k3l9To"], "ltz"),
    "solutions/bonding/index.html": ("영상으로 보기", ["yMkU-Z1KLWM"], [], "ltz"),
    "solutions/film/index.html": ("영상으로 보기", ["QYc2a20WjYQ"], ["cWXZpnVgUD8"], "ltz"),
    "support/index.html": ("측정·시연 영상", ["ZOhE1TvRvak", "1SqHTXdxlBg"], [], "ltz"),
    "technology/index.html": ("측정과 시연 영상", ["ZOhE1TvRvak", "1SqHTXdxlBg", "-GxOH3cY0eI"], [], "ltz"),
    "company/organization/index.html": ("생산 현장 영상", ["5-M4M0e4zOo"], ["aXH8LYqsWuo"], "ltz"),
    "news/medical-infection-control-exhibition-2026/index.html": ("관련 영상", [], ["VInr9EpVvTQ", "a7gt0lDqChA"], "ltz"),
    "resources/index.html": ("리트젠 영상", list(V), list(k for k in S if k not in ("jwcLBUZf9ro", "Wt-tM-dFeoo", "F1OAB2viMIw")), "ltz"),
}
CONVEYOR = {  # conveyor card code → Ohsung Unicon video
    "C": "nu1Qoe3wMtM", "CC": "oUZOUFQtsGA", "CCKN": "3q4ZK-6uHMw", "CTW": "3ng3IgZ-ONw", "CVA": "CwjqeNZwksc",
    "CSL": "35-3sQHoGSU", "CA": "KEbSB21nANA", "CRO": "87jXsP5jJ98", "CX": "M1SLVlivKc8", "CME": "fXcQurk4gLQ",
    "CTO": "mwkEMrhnxFo", "CRD": "j0lkVoI5-l4",
}
PLAY = '<span aria-hidden="true" class="yt-btn"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z"/></svg></span>'
SCRIPT = '<script defer src="/assets/yt-lite.js?v=20261125b"></script>'


def card(vid, caption, short=False):
    c = html.escape(caption)
    return (f'<figure class="yt-card{" is-short" if short else ""}"><button aria-label="{c} 영상 재생" class="yt-thumb" data-yt="{vid}" type="button">'
            f'<img alt="{c}" decoding="async" height="{960 if short else 540}" loading="lazy" src="/assets/media/yt/{vid}.webp" width="{540 if short else 960}"/>{PLAY}</button>'
            f'<figcaption>{c}</figcaption></figure>')


def caption(i):
    return V.get(i) or S.get(i) or OS.get(i) or ""


def block(title, ids, shorts=(), channel="ltz"):
    url = OSUNG if channel == "osung" else LTZ
    more = f'<a class="inline-link yt-channel" href="{url}" rel="noopener" target="_blank">유튜브 채널 보기 ↗</a>'
    body = ""
    if ids:
        body += f'<div class="yt-grid{" is-single" if len(ids) == 1 and not shorts else ""}">' + "".join(card(i, caption(i)) for i in ids) + "</div>"
    if shorts:
        body += '<div class="yt-grid yt-shorts">' + "".join(card(i, caption(i), True) for i in shorts) + "</div>"
    return (f'<!--videos:start--><section class="video-section"><div class="container"><div class="video-head"><h2>{title}</h2>{more}</div>'
            + body + '</div></section><!--videos:end-->')


def ensure_script(s):
    return s if "yt-lite.js" in s else s.replace("</body>", SCRIPT + "</body>", 1)


def main():
    n = 0
    for page, (title, ids, shorts, ch) in PAGES.items():
        p = os.path.join(ROOT, page)
        s = open(p, encoding="utf-8").read()
        s = re.sub(r"<!--videos:start-->.*?<!--videos:end-->", "", s, flags=re.S)
        s = s.replace("</main>", block(title, ids, shorts, ch) + "</main>", 1)
        open(p, "w", encoding="utf-8").write(ensure_script(s)); n += 1
    # conveyor cards: a play button over the card photo
    p = os.path.join(ROOT, "conveyors/index.html")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"<!--cv:start-->.*?<!--cv:end-->", "", s, flags=re.S)
    def per_card(m):
        art = m.group(0)
        code = re.search(r'conveyor-card-meta"><span>[^<]*</span><strong>([^<]+)</strong>', art)
        vid = code and CONVEYOR.get(code.group(1).split("/")[0].strip())
        if not vid:
            return art
        btn = (f'<!--cv:start--><button aria-label="오성유니콘 컨베이어 영상 재생" class="cv-play" data-yt="{vid}" type="button">'
               f'{PLAY}<span>영상</span></button><!--cv:end-->')
        return art.replace("</article>", btn + "</article>", 1)
    s = re.sub(r'<article class="conveyor-card".*?</article>', per_card, s, flags=re.S)
    s = s.replace("오성유니콘 홈페이지 ↗</a>", f'오성유니콘 홈페이지 ↗</a><!--cv:start--><a class="button cv-channel" href="{OSUNG}" rel="noopener" target="_blank">오성유니콘 유튜브 ↗</a><!--cv:end-->', 1) if "cv-channel" not in s else s
    gallery = block("오성유니콘 컨베이어 영상 더보기", [k for k in OS if k not in CONVEYOR.values()], [], "osung").replace("<!--videos:", "<!--cvg:")
    s = re.sub(r"<!--cvg:start-->.*?<!--cvg:end-->", "", s, flags=re.S).replace("</main>", gallery + "</main>", 1)
    open(p, "w", encoding="utf-8").write(ensure_script(s))
    print("video blocks on", n, "pages; conveyor buttons", s.count('class="cv-play"'))


main()
