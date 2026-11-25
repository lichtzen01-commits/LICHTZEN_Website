"""Tag products with the light they use so the site can colour them: UV (violet), LED (green), IR (orange),
UV-C (teal) and parts (slate). Adds data-light to product cards and product pages and a small UV/LED/IR tag
on each card. Korean pages only; run before build_langs.py. Safe to run again."""
import glob, os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "deploy/site"
IR = {"mir-drying-systems", "mir-lamps", "nir-lamps"}
UVC = {"far-uvc-lamps", "water-treatment-lamps", "uv-cleaning-lamps"}
LABEL = {"uv": "UV", "led": "LED", "ir": "IR", "uvc": "UV-C", "part": "PARTS"}


def light(slug, category):
    if slug in IR: return "ir"
    if slug in UVC: return "uvc"
    return {"led": "led", "components": "part", "ir": "ir", "uvc": "uvc"}.get(category, "uv")


def main():
    idx = os.path.join(ROOT, "products/index.html")
    s = open(idx, encoding="utf-8").read()
    kinds = {}

    def card(m):
        art = m.group(0)
        cat = re.search(r'data-product-category="([^"]*)"', art).group(1)
        slug = re.search(r'<a href="/products/([^/"]+)/', art).group(1)
        k = kinds[slug] = light(slug, cat)
        art = re.sub(r'\sdata-light="[^"]*"', "", art).replace('<article class="product-card"', f'<article class="product-card" data-light="{k}"', 1)
        art = re.sub(r'<span class="light-tag">[^<]*</span>', "", art)
        return art.replace('<div class="card-body"><small>', f'<div class="card-body"><span class="light-tag">{LABEL[k]}</span><small>', 1)

    s = re.sub(r'<article class="product-card".*?</article>', card, s, flags=re.S)
    open(idx, "w", encoding="utf-8").write(s)
    n = 0
    for slug, k in kinds.items():
        p = os.path.join(ROOT, "products", slug, "index.html")
        if not os.path.exists(p): continue
        t = open(p, encoding="utf-8").read()
        t = re.sub(r'<section class="product-overview"(?: data-light="[^"]*")?>', f'<section class="product-overview" data-light="{k}">', t, count=1)
        t = re.sub(r'<span class="light-tag">[^<]*</span>', "", t)
        t = t.replace('<div class="product-summary"><div class="eyebrow">', f'<div class="product-summary"><span class="light-tag">{LABEL[k]}</span><div class="eyebrow">', 1)
        open(p, "w", encoding="utf-8").write(t); n += 1
    print("cards", len(kinds), "product pages", n)


main()
