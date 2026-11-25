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
PAGES = {  # page: (heading, [ids])
    "products/three-dimensional-uv/index.html": ("영상으로 보기", ["N7_0g4ogf5o"]),
    "products/linear-uv-led/index.html": ("영상으로 보기", ["QYc2a20WjYQ", "_c77coPgg1g"]),
    "products/area-uv-led/index.html": ("영상으로 보기", ["QYc2a20WjYQ"]),
    "products/mercury-uv-lamp/index.html": ("영상으로 보기", ["5-M4M0e4zOo"]),
    "products/metal-halide-uv-lamp/index.html": ("영상으로 보기", ["5-M4M0e4zOo"]),
    "products/compact-uv-system/index.html": ("영상으로 보기", ["-GxOH3cY0eI", "ZOhE1TvRvak"]),
    "products/spot-uv-curing/index.html": ("영상으로 보기", ["yMkU-Z1KLWM"]),
    "products/lamp-accessories/index.html": ("영상으로 보기", ["B64i6h5J5Sg"]),
    "products/uv-reflectors/index.html": ("영상으로 보기", ["B64i6h5J5Sg"]),
    "technology/index.html": ("측정과 시연 영상", ["ZOhE1TvRvak", "1SqHTXdxlBg", "-GxOH3cY0eI"]),
    "company/organization/index.html": ("생산 현장 영상", ["5-M4M0e4zOo"]),
    "resources/index.html": ("리트젠 영상", list(V)),
}
CONVEYOR = {  # conveyor card code → Ohsung Unicon video
    "C": "nu1Qoe3wMtM", "CC": "oUZOUFQtsGA", "CCKN": "3q4ZK-6uHMw", "CTW": "3ng3IgZ-ONw", "CVA": "CwjqeNZwksc",
    "CSL": "35-3sQHoGSU", "CA": "KEbSB21nANA", "CRO": "87jXsP5jJ98", "CX": "M1SLVlivKc8", "CME": "fXcQurk4gLQ",
    "CTO": "mwkEMrhnxFo", "CRD": "j0lkVoI5-l4",
}
PLAY = '<span aria-hidden="true" class="yt-btn"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z"/></svg></span>'
SCRIPT = '<script defer src="/assets/yt-lite.js?v=20261125a"></script>'


def card(vid, caption):
    c = html.escape(caption)
    return (f'<figure class="yt-card"><button aria-label="{c} 영상 재생" class="yt-thumb" data-yt="{vid}" type="button">'
            f'<img alt="{c}" decoding="async" height="540" loading="lazy" src="/assets/media/yt/{vid}.webp" width="960"/>{PLAY}</button>'
            f'<figcaption>{c}</figcaption></figure>')


def block(title, ids, channel=True):
    more = (f'<a class="inline-link yt-channel" href="{LTZ}" rel="noopener" target="_blank">유튜브 채널 보기 ↗</a>' if channel else "")
    return (f'<!--videos:start--><section class="video-section"><div class="container"><div class="video-head"><h2>{title}</h2>{more}</div>'
            f'<div class="yt-grid{" is-single" if len(ids) == 1 else ""}">' + "".join(card(i, V[i]) for i in ids) + '</div></div></section><!--videos:end-->')


def ensure_script(s):
    return s if "yt-lite.js" in s else s.replace("</body>", SCRIPT + "</body>", 1)


def main():
    n = 0
    for page, (title, ids) in PAGES.items():
        p = os.path.join(ROOT, page)
        s = open(p, encoding="utf-8").read()
        s = re.sub(r"<!--videos:start-->.*?<!--videos:end-->", "", s, flags=re.S)
        s = s.replace("</main>", block(title, ids) + "</main>", 1)
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
    open(p, "w", encoding="utf-8").write(ensure_script(s))
    print("video blocks on", n, "pages; conveyor buttons", s.count('class="cv-play"'))


main()
