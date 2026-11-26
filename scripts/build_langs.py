"""Build static foreign-language pages (/en/ /zh/ /ja/ /hi/ /es/) from the Korean pages in deploy/site.

Search engines and AI assistants read the HTML a server sends, not text that a
script swaps in later, so each language is written out as real pages:

  deploy/site/<lang>/<same path>/index.html   translated text, title, meta,
                                              canonical, Open Graph and JSON-LD
  every page                                  hreflang for all six languages + x-default (en)
  sitemap.xml                                 every version with alternates
  llms.txt                                    gains an English section

Translations come from the runtime dictionaries (assets/site.js + i18n.js) plus
docs/i18n/<lang>.json. Run after any Korean content change:

    python3 scripts/seo_enhance.py deploy/site docs/seo/pages.json   (Korean title/description/JSON-LD/sitemap)
    python3 scripts/build_langs.py deploy/site                       (always last: rewrites sitemap, llms.txt, /<lang>/)

It prints Korean text that still has no translation and writes it to
docs/i18n/<lang>_missing.json, so the phrase can be added and the build rerun.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from bs4 import BeautifulSoup, Comment

DOMAIN = "https://www.lichtzen.com"
HANGUL = re.compile("[가-힣]")
LANG = {  # code: (html lang / hreflang, og:locale, JSON-LD inLanguage)
    "en": ("en", "en_US", "en"),
    "zh": ("zh-Hans", "zh_CN", "zh-Hans"),
    "ja": ("ja", "ja_JP", "ja"),
    "hi": ("hi", "hi_IN", "hi"),
    "es": ("es", "es_ES", "es"),
}
SKIP_TOP = ("assets/", "tools/", "website/") + tuple(l + "/" for l in LANG)
NO_EN = {"404.html"}
ATTRS = ("alt", "aria-label", "title", "placeholder")
META_NAMES = {"description", "twitter:title", "twitter:description"}
META_PROPS = {"og:title", "og:description", "og:site_name", "og:image:alt"}
ADDRESS = {"streetAddress": "2 Gugunpo 3-gil (Dangjeong-dong)", "addressLocality": "Gunpo-si", "addressRegion": "Gyeonggi-do"}
PHONES = [("031-419-6700", "+82-31-419-6700"), ("031-419-6226", "+82-31-419-6226"), ("070-4088-6117", "+82-70-4088-6117")]


def page_path(rel):
    """deploy-relative file -> URL path ('company/index.html' -> '/company/')."""
    rel = rel.replace(os.sep, "/")
    return "/" + (rel[: -len("index.html")] if rel.endswith("index.html") else rel)


def internal(href):
    return href.startswith("/") and not href.startswith("//") and not href.startswith(tuple("/" + t for t in SKIP_TOP))


def load_dict(site, lang):
    out = subprocess.run(["node", os.path.join(os.path.dirname(__file__), "i18n_dict.js"), site, lang], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def tr(D, s, missing):
    if not s or not HANGUL.search(s):
        return s
    k = s.strip()
    v = D.get(k)
    if v is None:
        missing.add(k)
        return s
    return s.replace(k, v)


def head_links(soup, path):
    """canonical-adjacent alternates; identical on both language versions."""
    head = soup.head
    for l in head.find_all("link", rel="alternate"):
        if l.get("hreflang"):
            l.decompose()
    anchor = head.find("link", rel="canonical")
    alts = [("ko", DOMAIN + path)] + [(LANG[l][0], DOMAIN + "/" + l + path) for l in LANG] + [("x-default", DOMAIN + "/en" + path)]
    for lang, url in alts:
        tag = soup.new_tag("link", rel="alternate", hreflang=lang, href=url)
        if anchor:
            anchor.insert_after(tag)
            anchor = tag
        else:
            head.append(tag)


def picker(soup, path):
    for a in soup.select("[data-language-code]"):
        code = a["data-language-code"]
        a["href"] = path if code == "ko" else "/" + code + path
        a["hreflang"] = "ko" if code == "ko" else LANG.get(code, (code,))[0]


def jsonld(D, node, missing, path, lang):
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if k == "inLanguage":
                out[k] = LANG[lang][2]
            elif k in ADDRESS and isinstance(v, str) and HANGUL.search(v):
                out[k] = ADDRESS[k]
            elif k in ("@id", "url", "item") and isinstance(v, str) and v.startswith(DOMAIN + "/") and "#organization" not in v and "#website" not in v and v != DOMAIN + "/":
                out[k] = DOMAIN + "/" + lang + v[len(DOMAIN):]
            elif k == "item" and v == DOMAIN + "/":
                out[k] = DOMAIN + "/" + lang + "/"
            elif k == "alternateName":
                out[k] = v
            else:
                out[k] = jsonld(D, v, missing, path, lang)
        return out
    if isinstance(node, list):
        return [jsonld(D, v, missing, path, lang) for v in node]
    if isinstance(node, str):
        return tr(D, node, missing)
    return node


def translate_page(D, html, path, missing, lang):
    soup = BeautifulSoup(html, "html.parser")
    root = soup.html
    root["lang"] = LANG[lang][0]
    root["data-static-lang"] = lang

    # "<strong>(주)리트젠</strong>의 ..." : the translated sentence already names the company,
    # so the separate Korean company-name element would repeat it.
    for el in soup.find_all(["strong", "b", "span"]):
        nxt = el.next_sibling
        if el.get_text(strip=True) in ("(주)리트젠", "㈜리트젠", "리트젠") and isinstance(nxt, str) and nxt.lstrip().startswith("의 "):
            el.decompose()
    for t in soup.find_all(string=True):
        if isinstance(t, Comment) or t.parent.name in ("script", "style"):
            continue
        new = tr(D, str(t), missing)
        for ko, intl in PHONES:
            new = new.replace(ko, intl)
        if not t.find_parent(attrs={"data-mail-keep": True}):
            new = new.replace("ltz@lichtzen.com", "itl@lichtzen.com")
        if new != str(t):
            t.replace_with(new)

    for el in soup.find_all(True):
        for a in ATTRS:
            v = el.get(a)
            if isinstance(v, str):
                el[a] = tr(D, v, missing)
        if el.name == "meta" and (el.get("name") in META_NAMES or el.get("property") in META_PROPS):
            el["content"] = tr(D, el.get("content", ""), missing)
        if el.name == "meta" and el.get("property") == "og:locale":
            el["content"] = LANG[lang][1]
        if el.name == "meta" and el.get("property") == "og:url":
            el["content"] = DOMAIN + "/" + lang + path
        if el.name == "link" and el.get("rel") == ["canonical"]:
            el["href"] = DOMAIN + "/" + lang + path
        if el.name in ("a", "form", "area"):
            for a in ("href", "action"):
                v = el.get(a)
                if isinstance(v, str):
                    if internal(v) and not el.has_attr("data-language-code"):
                        el[a] = "/" + lang + v
                    elif v.startswith("mailto:ltz@") and not el.find_parent(attrs={"data-mail-keep": True}):
                        el[a] = v.replace("mailto:ltz@", "mailto:itl@")
                    elif v.startswith("tel:0"):
                        el[a] = "tel:+82" + v[5:]
        if el.has_attr("data-products-url") or el.has_attr("data-guided-finder"):
            el["data-products-url"] = "/" + lang + "/products/"

    if soup.title and soup.title.string:
        soup.title.string = tr(D, soup.title.string, missing)
    loc = soup.head.find("meta", property="og:locale")
    if loc and not soup.head.find("meta", property="og:locale:alternate"):
        loc.insert_after(soup.new_tag("meta", attrs={"property": "og:locale:alternate", "content": "ko_KR"}))

    for s in soup.find_all("script"):
        body = s.string or ""
        if s.get("type") == "application/ld+json" and body.strip():
            s.string = json.dumps(jsonld(D, json.loads(body), missing, path, lang), ensure_ascii=False, separators=(",", ":"))
        elif body.startswith("window.LTZ_TEST_SEED"):
            s.decompose()
        elif body.startswith('(function(){var l=new URLSearchParams(location.search).get("lang");'):
            # Translated pages always load the dictionaries (the chat and form messages need them).
            s.string = body.replace('if(l&&l!=="ko")', 'if(l!=="ko")')

    head_links(soup, path)
    picker(soup, path)
    return str(soup)


def add_alternates_ko(html, path):
    soup = BeautifulSoup(html, "html.parser")
    if not soup.head:
        return html
    head_links(soup, path)
    picker(soup, path)
    return str(soup)


def sitemap(site, paths):
    sm = os.path.join(site, "sitemap.xml")
    text = open(sm, encoding="utf-8").read()
    lastmod = dict(re.findall(r"<loc>" + re.escape(DOMAIN) + r"(/[^<]*)</loc><lastmod>([^<]+)</lastmod>", text))
    rows = []
    for p in sorted(paths):
        alt = f'<xhtml:link rel="alternate" hreflang="ko" href="{DOMAIN}{p}"/>' + "".join(
            f'<xhtml:link rel="alternate" hreflang="{LANG[l][0]}" href="{DOMAIN}/{l}{p}"/>' for l in LANG) + (
            f'<xhtml:link rel="alternate" hreflang="x-default" href="{DOMAIN}/en{p}"/>')
        lm = lastmod.get(p, "")
        for loc in [p] + ["/" + l + p for l in LANG]:
            rows.append(f"<url><loc>{DOMAIN}{loc}</loc>" + (f"<lastmod>{lm}</lastmod>" if lm else "") + alt + "</url>")
    open(sm, "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(rows) + "\n</urlset>\n")


def llms(site, pages):
    path = os.path.join(site, "llms.txt")
    text = open(path, encoding="utf-8").read()
    text = text.split("\n## English pages")[0].rstrip() + "\n"
    lines = ["", "## English pages", "", "LICHTZEN Co., Ltd. (Gunpo, Korea, founded 1995) designs and manufactures UV and IR light sources, UV curing and IR/MIR drying systems, and UV LED modules. Every page below is the English version of the Korean page at the same path without /en. Chinese, Japanese, Hindi and Spanish versions are at /zh/, /ja/, /hi/ and /es/.", ""]
    for p, title, desc in sorted(pages):
        lines.append(f"- [{title}]({DOMAIN}/en{p})" + (f": {desc}" if desc else ""))
    open(path, "w", encoding="utf-8").write(text + "\n".join(lines) + "\n")


def main(site):
    paths, listing, total = [], [], {}
    sources = []
    for fn in sorted(glob.glob(os.path.join(site, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(fn, site).replace(os.sep, "/")
        if rel.startswith(SKIP_TOP) or rel in NO_EN:
            continue
        html = open(fn, encoding="utf-8").read()
        if "<head" not in html:
            continue
        sources.append((fn, rel, page_path(rel), html))
    for lang in LANG:
        D = load_dict(site, lang)
        out_root = os.path.join(site, lang)
        if os.path.exists(out_root):
            shutil.rmtree(out_root)
        missing = set()
        for fn, rel, path, html in sources:
            out = translate_page(D, html, path, missing, lang)
            target = os.path.join(out_root, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            open(target, "w", encoding="utf-8").write(out)
            if lang == "en":
                s = BeautifulSoup(out, "html.parser")
                d = s.find("meta", attrs={"name": "description"})
                listing.append((path, (s.title.string or path).strip() if s.title else path, d.get("content", "").strip() if d else ""))
        total[lang] = len(missing)
        miss_file = os.path.join(site, "..", "..", "docs", "i18n", lang + "_missing.json")
        if missing:
            json.dump(sorted(missing), open(miss_file, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        elif os.path.exists(miss_file):
            os.remove(miss_file)
    for fn, rel, path, html in sources:
        open(fn, "w", encoding="utf-8").write(add_alternates_ko(html, path))
        paths.append(path)
    sitemap(site, paths)
    llms(site, listing)
    print(f"{len(paths)} pages x {len(LANG)} languages written; untranslated phrases: {total}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "deploy/site")
