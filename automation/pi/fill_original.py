"""Fill the company's original FX#202 workbook for FX#203 by editing the sheet XML directly,
so the logo/signature images, styles and print settings stay exactly as in the original."""
import datetime, html, os, re, shutil, sys, zipfile

SRC, OUT = sys.argv[1], sys.argv[2]
WORK = os.path.join(os.path.dirname(OUT), "_work")
if os.path.isdir(WORK):
    shutil.rmtree(WORK)
with zipfile.ZipFile(SRC) as z:
    z.extractall(WORK)
P = lambda *a: os.path.join(WORK, *a)

def serial(d):
    return (d - datetime.date(1899, 12, 30)).days

def cell_xml(ref, style, value, kind):
    s = f' s="{style}"' if style is not None else ""
    if kind == "str":
        t = html.escape(value, quote=False)
        sp = ' xml:space="preserve"' if (t != t.strip() or "\n" in t) else ""
        return f'<c r="{ref}"{s} t="inlineStr"><is><t{sp}>{t}</t></is></c>'
    if kind == "num":
        return f'<c r="{ref}"{s}><v>{value}</v></c>'
    if kind == "f":
        return f'<c r="{ref}"{s}><f>{html.escape(value, quote=False)}</f></c>'
    if kind == "empty":
        return f'<c r="{ref}"{s}/>'
    raise ValueError(kind)

def col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n

class Sheet:
    def __init__(self, path):
        self.path = path
        self.x = open(path, encoding="utf-8").read()

    def row(self, r):
        m = re.search(r'<row r="%d"[^>]*?(?:/>|>.*?</row>)' % r, self.x, re.S)
        if not m:
            raise KeyError(f"row {r} missing")
        return m

    def style_of(self, ref):
        r = int(re.search(r"\d+", ref).group(0))
        m = re.search(r'<c r="%s"(?: s="(\d+)")?' % ref, self.row(r).group(0))
        return m.group(1) if m else None

    def set(self, ref, value, kind=None, style=None):
        if kind is None:
            kind = "empty" if value in (None, "") else ("num" if isinstance(value, (int, float)) else "str")
        r = int(re.search(r"\d+", ref).group(0))
        m = self.row(r)
        row = m.group(0)
        if style is None:
            style = self.style_of(ref)
        new = cell_xml(ref, style, value, kind)
        pat = re.compile(r'<c r="%s"(?:\s[^>]*)?(?:/>|>.*?</c>)' % ref, re.S)
        if pat.search(row):
            row2 = pat.sub(lambda _: new, row, count=1)
        else:  # insert in column order
            if row.endswith("/>"):
                row2 = row[:-2] + ">" + new + "</row>"
            else:
                cells = list(re.finditer(r'<c r="([A-Z]+)\d+"', row))
                pos = None
                for c in cells:
                    if col_index(c.group(1)) > col_index(ref):
                        pos = c.start(); break
                if pos is None:
                    pos = row.rindex("</row>")
                row2 = row[:pos] + new + row[pos:]
        self.x = self.x[:m.start()] + row2 + self.x[m.end():]

    def show(self, r):
        m = self.row(r)
        self.x = self.x[:m.start()] + m.group(0).replace(' hidden="1"', "", 1) + self.x[m.end():]

    def height(self, r, ht):
        m = self.row(r)
        row = re.sub(r'\sht="[^"]*"', "", m.group(0), count=1)
        row = row.replace("<row ", f'<row ht="{ht}" ', 1)
        if "customHeight" not in row:
            row = row.replace("<row ", '<row customHeight="1" ', 1)
        self.x = self.x[:m.start()] + row + self.x[m.end():]

    def save(self):
        # drop cached results of formulas so every program recalculates them (LibreOffice keeps cached values otherwise)
        def strip(m):
            c = m.group(0)
            if "<f" not in c:
                return c
            c = re.sub(r"<v(?:\s[^>]*)?>.*?</v>|<v(?:\s[^>]*)?/>", "", c, flags=re.S)
            return re.sub(r'^(<c [^>]*?)\st="(?:str|s|n|b|e)"', r"\1", c, count=1)
        # one cell at a time: self-closing cells, or a cell with its content
        self.x = re.sub(r'<c [^>]*?/>|<c [^>]*?[^/]>.*?</c>', strip, self.x, flags=re.S)
        open(self.path, "w", encoding="utf-8").write(self.x)

# ---------- order data (JSON file, argv[3]) ----------
import json
CFG = json.load(open(sys.argv[3], encoding="utf-8"))
INV, INV_DATE = CFG["invoice"], datetime.date.fromisoformat(CFG["invoice_date"])
PO_NO, PO_DATE = CFG["po_no"], CFG["po_date"]
DEPART = CFG["departure"]
MARK_PNG = CFG.get("mark_png")
# non-commercial lines (samples, free replacements, returned lamps) keep their unit price for reference and show
# "non-commercial" in AMOUNT, as in the FX#204 PI the sales team corrected
ITEMS = [(i["desc"], i["qty"], i.get("price"), i.get("non_commercial", i.get("price") is None)) for i in CFG["items"]]
NC_TEXT = CFG.get("non_commercial_text", "non-commercial")
NC_NOTE = CFG.get("non_commercial_note", "")

# ---------- 작성창 (sheet1) ----------
s1 = Sheet(P("xl", "worksheets", "sheet1.xml"))
s1.set("B9", DEPART)
s1.set("B10", DEPART)
s1.set("B11", INV)
s1.set("B12", INV_DATE.isoformat())        # written as text so it reads 2026-06-11 on every PC
s1.set("B13", PO_NO)
s1.set("B14", PO_DATE)
remarks_old = re.search(r'<c r="B17"[^>]*>.*?</c>', s1.x, re.S).group(0)
REMARKS = ('\n* When making wire transfers, select the "OUR" option to cover your national banking fees. Ensure the exact '
           'amount is transferred directly to us to prevent additional charges on your next invoice in case of non-compliance.\n'
           '* WARRANTY : 1 YEAR' + ('\n\n' + NC_NOTE if NC_NOTE else ''))
s1.set("B17", REMARKS)
for i, (desc, qty, price, nc) in enumerate(ITEMS):
    r = 20 + i
    s1.show(r)
    s1.set(f"A{r}", desc, style="18")
    s1.set(f"B{r}", qty, "num", style="20")
    s1.set(f"C{r}", "EA", style="20")
    if nc:
        s1.set(f"D{r}", price if price is not None else "", "num" if price is not None else "empty", style="78")
        s1.set(f"E{r}", NC_TEXT, style="79")
    else:
        s1.set(f"D{r}", price, "num", style="78")
        s1.set(f"E{r}", f"D{r}*B{r}", "f", style="79")
for ref in ("B39", "B40", "B41"):          # packing is decided at shipment
    s1.set(ref, "TBD")
s1.save()

# ---------- PI (sheet2) ----------
s2 = Sheet(P("xl", "worksheets", "sheet2.xml"))
s2.set("C12", REMARKS)
for i, (desc, qty, price, nc) in enumerate(ITEMS):
    r = 19 + i
    s2.show(r)
    st = dict(A="223" if r == 19 else "224", B="18", C="56" if r == 19 else "20", D="19" if r <= 20 else "20", E="78", F="79")
    s2.set(f"A{r}", "", "empty", st["A"])   # the shipping mark picture goes in MARKS
    s2.set(f"B{r}", desc, style=st["B"])
    s2.set(f"C{r}", qty, "num", st["C"])
    s2.set(f"D{r}", "EA", style=st["D"])
    if nc:
        s2.set(f"E{r}", price if price is not None else "", "num" if price is not None else "empty", st["E"])
        s2.set(f"F{r}", NC_TEXT, style="20")   # centred like the sales team's PI
    else:
        s2.set(f"E{r}", price, "num", st["E"])
        s2.set(f"F{r}", f"E{r}*C{r}", "f", st["F"])
s2.save()

# ---------- CI, PL (sheet3) ----------
s3 = Sheet(P("xl", "worksheets", "sheet3.xml"))
s3.set("C12", REMARKS) if '<c r="C12"' in s3.x else None
s3.set("I12", REMARKS) if '<c r="I12"' in s3.x else None
for i, (desc, qty, price, nc) in enumerate(ITEMS):
    r = 19 + i
    s3.show(r)
    first = r == 19
    st = dict(A="223" if first else "224", B="18", C="56" if first else "20", D="19" if r <= 20 else "20", E="78", F="79")
    s3.set(f"A{r}", "", "empty", st["A"])
    s3.set(f"B{r}", desc, style=st["B"])
    s3.set(f"C{r}", qty, "num", st["C"])
    s3.set(f"D{r}", "EA", style=st["D"])
    if nc:
        s3.set(f"E{r}", price if price is not None else "", "num" if price is not None else "empty", st["E"])
        s3.set(f"F{r}", NC_TEXT, style="20")   # centred like the sales team's PI
    else:
        s3.set(f"E{r}", price, "num", st["E"])
        s3.set(f"F{r}", f"E{r}*C{r}", "f", st["F"])
    s3.set(f"G{r}", "", "empty", st["A"])
    s3.set(f"H{r}", desc, style="18")
    s3.set(f"I{r}", qty, "num", st["C"])
    s3.set(f"J{r}", "EA", style=st["D"])
s3.save()

# Remarks cells in CI/PL may be formulas or literals; report what they hold.
# ---------- workbook: drop the calc chain and recalculate on open ----------
wb = open(P("xl", "workbook.xml"), encoding="utf-8").read()
wb = re.sub(r"<calcPr([^>]*)/>", lambda m: "<calcPr" + re.sub(r'\sfullCalcOnLoad="[^"]*"', "", m.group(1)) + ' fullCalcOnLoad="1"/>', wb)
open(P("xl", "workbook.xml"), "w", encoding="utf-8").write(wb)
if os.path.exists(P("xl", "calcChain.xml")):
    os.remove(P("xl", "calcChain.xml"))
    rels = open(P("xl", "_rels", "workbook.xml.rels"), encoding="utf-8").read()
    rels = re.sub(r'<Relationship [^>]*Target="calcChain.xml"[^>]*/>', "", rels)
    open(P("xl", "_rels", "workbook.xml.rels"), "w", encoding="utf-8").write(rels)
    ct = open(P("[Content_Types].xml"), encoding="utf-8").read()
    ct = re.sub(r'<Override [^>]*PartName="/xl/calcChain.xml"[^>]*/>', "", ct)
    open(P("[Content_Types].xml"), "w", encoding="utf-8").write(ct)

# ---------- shipping mark picture ----------
EXTRA = []
if MARK_PNG:
    from PIL import Image
    im = Image.open(MARK_PNG).convert("RGB")
    im.thumbnail((1200, 3600))   # keep the print resolution of the mark
    os.makedirs(P("xl", "media"), exist_ok=True)
    im.save(P("xl", "media", "image6.png"))
    EXTRA.append("xl/media/image6.png")
    EMU_PX, ROW_EMU = 9525, int(24.95 * 12700)
    col_emu = int(((15.625 * 7 + 5) // 1) * EMU_PX)          # MARKS column, 15.625 characters wide
    cx = int(col_emu * 0.94); cy = int(cx * im.height / im.width)
    if cy > len(ITEMS) * ROW_EMU * 0.94:
        cy = int(len(ITEMS) * ROW_EMU * 0.94); cx = int(cy * im.width / im.height)
    area = len(ITEMS) * ROW_EMU                                # all item rows are shown
    top = (area - cy) // 2
    row, row_off = 18 + top // ROW_EMU, top % ROW_EMU
    col_off = (col_emu - cx) // 2
    A = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    def anchor(col, pid, rid):
        return (f'<xdr:oneCellAnchor><xdr:from><xdr:col>{col}</xdr:col><xdr:colOff>{col_off}</xdr:colOff><xdr:row>{row}</xdr:row>'
                f'<xdr:rowOff>{row_off}</xdr:rowOff></xdr:from><xdr:ext cx="{cx}" cy="{cy}"/><xdr:pic><xdr:nvPicPr>'
                f'<xdr:cNvPr id="{pid}" name="Shipping mark {pid}"/><xdr:cNvPicPr><a:picLocks noChangeAspect="1"/></xdr:cNvPicPr>'
                f'</xdr:nvPicPr><xdr:blipFill><a:blip xmlns:r="{A}" r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch>'
                f'</xdr:blipFill><xdr:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
                f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></xdr:spPr></xdr:pic><xdr:clientData/></xdr:oneCellAnchor>')
    for drawing, cols in (("drawing2", (0,)), ("drawing3", (0, 6))):
        rels_p = P("xl", "drawings", "_rels", drawing + ".xml.rels")
        rels = open(rels_p, encoding="utf-8").read()
        rid = "rIdMark"
        rels = rels.replace("</Relationships>", f'<Relationship Id="{rid}" Type="{A}/image" Target="../media/image6.png"/></Relationships>')
        open(rels_p, "w", encoding="utf-8").write(rels)
        d_p = P("xl", "drawings", drawing + ".xml")
        d = open(d_p, encoding="utf-8").read()
        d = d.replace("</xdr:wsDr>", "".join(anchor(c, 90 + i, rid) for i, c in enumerate(cols)) + "</xdr:wsDr>")
        open(d_p, "w", encoding="utf-8").write(d)

# ---------- zip back in the original member order ----------
with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        path = P(*info.filename.split("/"))
        if os.path.exists(path):
            zout.write(path, info.filename)
    for name in EXTRA:
        zout.write(P(*name.split("/")), name)
shutil.rmtree(WORK)
print("written", OUT)
