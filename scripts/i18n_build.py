"""Build the foreign-language dictionaries for the static site.

Sources (edit these, then run this script):
  docs/i18n/shared.json            {korean: {en, zh, ja, es, hi}}  strings used on several pages
  docs/i18n/pages/<slug>.json      same format, strings used on one page

Output:
  deploy/site/assets/i18n.js       shared block between the LTZ-SHARED markers
  deploy/site/assets/i18n-pages/<slug>.js
  every page's language loader also loads its own page dictionary (only for ?lang=xx visitors)

Run: python3 scripts/i18n_build.py deploy/site docs/i18n <cache-version>
"""
import glob, json, os, re, sys

LANGS = ["en", "zh", "ja", "es", "hi"]


def slug_for(rel):
    d = os.path.dirname(rel)
    return d.replace(os.sep, "__") if d else "index"


def load(path):
    data = json.load(open(path, encoding="utf-8"))
    for k, v in data.items():
        missing = [l for l in LANGS if not v.get(l)]
        if missing:
            raise SystemExit(f"{path}: '{k[:30]}' missing {missing}")
    return data


def js(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def main(site, src, ver):
    shared = load(os.path.join(src, "shared.json")) if os.path.exists(os.path.join(src, "shared.json")) else {}
    i18n = os.path.join(site, "assets", "i18n.js")
    text = open(i18n, encoding="utf-8").read()
    block = "/*LTZ-SHARED-START*/Object.assign(window.LTZ_I18N_EXTRA," + js(shared) + ");/*LTZ-SHARED-END*/\n"
    if "/*LTZ-SHARED-START*/" in text:
        text = re.sub(r"/\*LTZ-SHARED-START\*/.*?/\*LTZ-SHARED-END\*/\n", lambda m: block, text, flags=re.S)
    else:
        text = text.replace("window.LTZ_LANG=", block + "window.LTZ_LANG=", 1)
    open(i18n, "w", encoding="utf-8").write(text)

    out = os.path.join(site, "assets", "i18n-pages")
    os.makedirs(out, exist_ok=True)
    pages = {}
    for p in glob.glob(os.path.join(src, "pages", "*.json")):
        slug = os.path.splitext(os.path.basename(p))[0]
        pages[slug] = load(p)
        open(os.path.join(out, slug + ".js"), "w", encoding="utf-8").write(
            "Object.assign(window.LTZ_I18N_EXTRA," + js(pages[slug]) + ");\n")

    loader = re.compile(r"<script>\(function\(\)\{var l=new URLSearchParams\(location\.search\)\.get\(\"lang\"\);if\(l&&l!==\"ko\"\)document\.write\(.*?\);\}\)\(\);</script>")
    n = 0
    for path in glob.glob(os.path.join(site, "**", "*.html"), recursive=True):
        rel = os.path.relpath(path, site)
        html = open(path, encoding="utf-8").read()
        slug = slug_for(rel)
        tags = f"'<script src=\"/assets/i18n.js?v={ver}\"><\\/script>'"
        if slug in pages:
            tags += f"+'<script src=\"/assets/i18n-pages/{slug}.js?v={ver}\"><\\/script>'"
        new = f'<script>(function(){{var l=new URLSearchParams(location.search).get("lang");if(l&&l!=="ko")document.write({tags});}})();</script>'
        html2, k = loader.subn(lambda m: new, html)
        if k and html2 != html:
            open(path, "w", encoding="utf-8").write(html2)
            n += 1
    print(f"shared {len(shared)} strings, {len(pages)} page dictionaries, {n} pages updated")


if __name__ == "__main__":
    main(*sys.argv[1:4])
