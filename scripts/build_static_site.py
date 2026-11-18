"""Turn the single-file test bundle (Lichtzen_Test_Sales_System*.html) into a
static website folder that any static host (Netlify, Cloudflare Pages, Cafe24
web hosting) can serve.

Only the public homepage is exported. The sales workspace, the admin preview
and the embedded business data (quotes, orders, claims) stay out of the build.

Usage:
    python3 scripts/build_static_site.py <bundle.html> <output_dir>
"""
import base64
import glob
import gzip
import json
import os
import re
import shutil
import sys

SKIP_PAGES = {"/sales/", "/admin-preview.html"}


def main(bundle, out):
    src = open(bundle, encoding="utf-8").read()
    meta = json.loads(re.search(r'<script id="ltz-index" type="application/json">(.*?)</script>', src, re.S).group(1))
    blobs = dict(re.findall(r'<script id="(r\d+)" type="application/octet-stream">(.*?)</script>', src, re.S))

    def data(rid):
        raw = base64.b64decode(blobs[rid])
        return gzip.decompress(raw) if meta["codecs"].get(rid) == "gzip" else raw

    def save(path, rid):
        target = os.path.join(out, path.lstrip("/") + ("index.html" if path.endswith("/") else ""))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as f:
            f.write(data(rid))

    if os.path.exists(out):
        shutil.rmtree(out)
    for path, rid in meta["pages"].items():
        if path not in SKIP_PAGES:
            save(path, rid)
    for path, item in meta["assets"].items():
        save(path, item["id"])
    for path, rid in {**meta["styles"], **meta["scripts"], **meta["tools"]}.items():
        if "admin" not in path and "sales" not in path:
            save(path, rid)

    # Links to the excluded internal screens and to the backend runtime.
    for page in glob.glob(os.path.join(out, "**", "*.html"), recursive=True):
        if os.sep + "tools" + os.sep in page:
            continue
        html = open(page, encoding="utf-8").read()
        fixed = html.replace('<script src="/assets/runtime.js"></script>', "")
        fixed = re.sub(r'<a href="/admin-preview.html">[^<]*</a>', "", fixed)
        fixed = re.sub(r'<a href="/sales/"[^>]*>.*?</a>', "", fixed, flags=re.S)
        if fixed != html:
            open(page, "w", encoding="utf-8").write(fixed)

    # Without the bundle wrapper there is no media store or portable query string.
    media = os.path.join(out, "assets", "media-store.js")
    js = open(media, encoding="utf-8").read()
    js = js.replace("if(!document.documentElement.dataset.adminPreview&&",
                    "if(window.LTZMedia&&!document.documentElement.dataset.adminPreview&&")
    open(media, "w", encoding="utf-8").write(js)
    site_js = os.path.join(out, "assets", "site.js")
    js = open(site_js, encoding="utf-8").read()
    js = js.replace("new URLSearchParams(window.LTZ_PORTABLE_SEARCH)",
                    "new URLSearchParams(window.LTZ_PORTABLE_SEARCH||location.search)")
    open(site_js, "w", encoding="utf-8").write(js)

    # Test site: keep it out of search engines until launch.
    with open(os.path.join(out, "robots.txt"), "w") as f:
        f.write("User-agent: *\nDisallow: /\n")

    pages = len([p for p in glob.glob(os.path.join(out, "**", "index.html"), recursive=True) if "/tools/" not in p])
    print(f"exported {pages} pages to {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
