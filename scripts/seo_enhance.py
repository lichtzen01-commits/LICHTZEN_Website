"""Technical SEO pass over the static site (deploy/site). Safe to run again.

- title / meta description from docs/seo/pages.json
- canonical, Open Graph and JSON-LD (Organization, WebSite, WebPage,
  BreadcrumbList, Product without price) inside a marked block in <head>
- /website/ (a duplicate of the homepage) becomes a redirect to /
- width/height on raster images that lack them
- sitemap.xml and llms.txt

Usage: python3 scripts/seo_enhance.py deploy/site docs/seo/pages.json
"""
import datetime
import glob
import html
import json
import os
import re
import sys

from PIL import Image

SITE = "https://www.lichtzen.com"
ORG = {
    "@type": "Organization",
    "@id": SITE + "/#organization",
    "name": "LICHTZEN Co., Ltd.",
    "alternateName": ["㈜리트젠", "리트젠", "LTZ"],
    "url": SITE + "/",
    "logo": SITE + "/assets/legacy/a60690006a79.webp",
    "foundingDate": "1995-04-05",
    "numberOfEmployees": {"@type": "QuantitativeValue", "value": 50},
    "email": "ltz@lichtzen.com",
    "telephone": "+82-31-419-6700",
    "faxNumber": "+82-31-419-6226",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "구군포3길 2 (당정동)",
        "addressLocality": "군포시",
        "addressRegion": "경기도",
        "postalCode": "15842",
        "addressCountry": "KR",
    },
    "description": "UV·IR 광원과 UV 경화·IR/MIR 건조 시스템, UV LED 모듈을 설계·제조하는 광응용 기업",
    "sameAs": ["https://www.youtube.com/@LICHTZEN", "https://www.komachine.com/companies/lichtzen", "https://www.linkedin.com/company/-%EC%A3%BC-%EB%A6%AC%ED%8A%B8%EC%A0%A0/"],
}
GENERIC_PRODUCT_TEXT = "제품의 적용 분야와 특징, 모델별 사양을 확인하고 필요한 공정 조건을 상담하세요."
START, END = "<!--seo:start-->", "<!--seo:end-->"


def page_url(root, path):
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    return "/" + (rel[: -len("index.html")] if rel.endswith("index.html") else rel)


def text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def set_meta_description(h, desc):
    esc = html.escape(desc, quote=True)
    if re.search(r'<meta content="[^"]*" name="description"\s*/?>', h):
        return re.sub(r'<meta content="[^"]*" name="description"\s*/?>', f'<meta content="{esc}" name="description"/>', h, count=1)
    return h.replace("</title>", f'</title><meta content="{esc}" name="description"/>', 1)


def breadcrumb(url, h1, h):
    items = [{"name": "홈", "url": SITE + "/"}]
    parts = [p for p in url.strip("/").split("/") if p]
    labels = {"products": "제품", "solutions": "적용 분야", "company": "회사소개", "support": "고객지원",
              "news": "소식", "resources": "자료실", "technology": "기술", "contact": "상담·견적",
              "selection-guide": "제품 선정 가이드", "conveyors": "컨베이어", "lamp": "램프 사양 설계", "privacy": "개인정보처리방침",
              "uvc-disinfection": "UV-C 소독 솔루션"}
    for i, part in enumerate(parts):
        last = i == len(parts) - 1
        items.append({"name": h1 if last else labels.get(part, part), "url": SITE + "/" + "/".join(parts[: i + 1]) + "/"})
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": n + 1, "name": it["name"], "item": it["url"]} for n, it in enumerate(items)]}


def first_image(h):
    m = re.search(r'class="product-main-image"><img[^>]*src="([^"]+)"', h) or re.search(r'data-hero-poster[^>]*src="([^"]+)"', h) \
        or re.search(r'<main.*?<img[^>]*src="(/assets/(?:optimized|legacy|media)/[^"]+)"', h, re.S)
    return SITE + m.group(1) if m else ORG["logo"]


def head_block(url, title, desc, h1, h, is_product, category, published=""):
    canonical = SITE + url
    image = first_image(h)
    graph = [ORG, {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "리트젠 LICHTZEN",
                   "inLanguage": "ko-KR", "publisher": {"@id": ORG["@id"]}},
             {"@type": "WebPage", "@id": canonical + "#webpage", "url": canonical, "name": title, "description": desc,
              "inLanguage": "ko-KR", "isPartOf": {"@id": SITE + "/#website"}, "about": {"@id": ORG["@id"]}}]
    if url != "/":
        graph.append(breadcrumb(url, h1, h))
    faq = [(text(q), text(a)) for q, a in re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p>", h, re.S)]
    if faq:
        graph.append({"@type": "FAQPage", "@id": canonical + "#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    if is_product:
        graph.append({"@type": "Product", "@id": canonical + "#product", "name": h1, "description": desc, "image": image,
                      "category": category, "brand": {"@type": "Brand", "name": "LICHTZEN"},
                      "manufacturer": {"@id": ORG["@id"]}, "url": canonical})
    if published:   # news posts: the date comes from the old board (docs/seo/pages.json)
        graph.append({"@type": "NewsArticle", "@id": canonical + "#article", "headline": h1[:110], "description": desc,
                      "image": image, "datePublished": published, "dateModified": published, "inLanguage": "ko-KR",
                      "author": {"@id": ORG["@id"]}, "publisher": {"@id": ORG["@id"]},
                      "mainEntityOfPage": {"@id": canonical + "#webpage"}})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    e = lambda s: html.escape(s, quote=True)
    og_type = "product" if is_product else ("website" if url == "/" else "article" if url.startswith("/news/") else "website")
    return (f'{START}<link href="{e(canonical)}" rel="canonical"/>'
            f'<meta content="{og_type}" property="og:type"/><meta content="리트젠 LICHTZEN" property="og:site_name"/>'
            f'<meta content="ko_KR" property="og:locale"/><meta content="{e(title)}" property="og:title"/>'
            f'<meta content="{e(desc)}" property="og:description"/><meta content="{e(canonical)}" property="og:url"/>'
            f'<meta content="{e(image)}" property="og:image"/><meta content="summary_large_image" name="twitter:card"/>'
            f'<script type="application/ld+json">{ld}</script>{END}')


def add_image_sizes(root, h):
    def fix(m):
        tag = m.group(0)
        if "width=" in tag:
            return tag
        src = re.search(r'src="(/[^"]+)"', tag)
        if not src or src.group(1).endswith(".svg"):
            return tag
        path = os.path.join(root, src.group(1).lstrip("/"))
        try:
            w, hh = Image.open(path).size
        except Exception:
            return tag
        return tag.replace("<img", f'<img width="{w}" height="{hh}"', 1)
    return re.sub(r"<img\b[^>]*>", fix, h)


def main(root, config):
    cfg = {k: v for k, v in json.load(open(config, encoding="utf-8")).items() if not k.startswith("_")}
    today = datetime.date.today().isoformat()
    pages = sorted(p for p in glob.glob(os.path.join(root, "**", "index.html"), recursive=True)
                   if f"{os.sep}tools{os.sep}" not in p)
    sitemap = []
    for path in pages:
        url = page_url(root, path)
        h = open(path, encoding="utf-8").read()
        if url == "/website/":
            h = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"/><title>리트젠 LICHTZEN</title>'
                 f'<link href="{SITE}/" rel="canonical"/><meta content="noindex" name="robots"/>'
                 '<meta content="0; url=/" http-equiv="refresh"/></head>'
                 '<body><p><a href="/">리트젠 홈페이지로 이동</a></p></body></html>\n')
            open(path, "w", encoding="utf-8").write(h)
            continue
        h = re.sub(re.escape(START) + ".*?" + re.escape(END), "", h, flags=re.S)
        over = cfg.get(url, {})
        if over.get("title"):
            h = re.sub(r"<title>.*?</title>", f"<title>{html.escape(over['title'])}</title>", h, count=1, flags=re.S)
        if over.get("description"):
            h = set_meta_description(h, over["description"])
            if GENERIC_PRODUCT_TEXT in h:
                h = h.replace(f"<p>{GENERIC_PRODUCT_TEXT}</p>", f"<p>{html.escape(over['description'])}</p>")
        title = text(re.search(r"<title>(.*?)</title>", h, re.S).group(1))
        dm = re.search(r'<meta content="([^"]*)" name="description"', h)
        desc = html.unescape(dm.group(1)) if dm else ""
        h1m = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
        h1 = text(h1m.group(1)) if h1m else title
        is_product = url.startswith("/products/") and url != "/products/"
        cat = re.search(r"<dt>제품군</dt><dd>(.*?)</dd>", h)
        h = h.replace("</head>", head_block(url, title, desc, h1, h, is_product, text(cat.group(1)) if cat else "", over.get("datePublished", "")) + "</head>", 1)
        h = add_image_sizes(root, h)
        open(path, "w", encoding="utf-8").write(h)
        sitemap.append(f"<url><loc>{SITE}{url}</loc><lastmod>{today}</lastmod></url>")

    with open(os.path.join(root, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "\n".join(sitemap) + "\n</urlset>\n")
    with open(os.path.join(root, "llms.txt"), "w", encoding="utf-8") as f:
        f.write("# 리트젠 LICHTZEN\n\n"
                "> 1995년 설립한 한국의 광응용 제조기업. UV 램프(수은·메탈할라이드·갈륨)·MIR/NIR 램프·UV LED 모듈과 "
                "UV 경화·IR/MIR 건조 시스템을 설계·제조합니다. 본사·공장·연구소: 경기도 군포시. ISO 9001·ISO 14001.\n\n"
                "## 주요 페이지\n\n"
                f"- [제품 찾기]({SITE}/products/): UV 경화 장비, UV LED, IR·MIR 건조, 램프·광원, UV-C 살균, 부품\n"
                f"- [UV-C 소독 솔루션]({SITE}/uvc-disinfection/): Wonder-Ray® 254nm UV-C 소독기(S8W4·S8), 222nm Far-UVC 모듈, 시험·인증, 적용 공간\n"
                f"- [적용 분야]({SITE}/solutions/): 필름·인쇄·코팅, PCB, 정밀 본딩, IR 가열·건조\n"
                f"- [기술]({SITE}/technology/): 광원 선택과 공정 검토\n"
                f"- [회사소개]({SITE}/company/): 연혁, 조직, 특허·인증\n"
                f"- [상담·견적]({SITE}/contact/): 제품·공정 문의\n")
    print(f"updated {len(sitemap)} pages, sitemap {len(sitemap)} urls")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
