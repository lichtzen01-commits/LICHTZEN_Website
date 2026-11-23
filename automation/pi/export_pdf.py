"""PDF of one sheet of the invoice workbook (PI, or 'CI, PL'). A temporary copy sets that sheet's page numbering
to start at 1; the whole workbook is converted and only that sheet's pages are kept. The workbook is not changed."""
import os, re, shutil, subprocess, sys, tempfile, zipfile
src, sheet, out_pdf = sys.argv[1:4]
title = {"PI": "PROFORMA INVOICE", "CI, PL": "COMMERCIAL INVOICE"}[sheet]
with zipfile.ZipFile(src) as z:
    wb = z.read("xl/workbook.xml").decode(); rels = z.read("xl/_rels/workbook.xml.rels").decode()
rid = re.search(r'<sheet [^>]*name="%s"[^>]*r:id="([^"]+)"' % re.escape(sheet), wb).group(1)
target = "xl/" + re.search(r'Id="%s"[^>]*Target="([^"]+)"' % rid, rels).group(1)
tmp = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(out_pdf)))
copy = os.path.join(tmp, "only.xlsx")
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(copy, "w", zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        data = zin.read(info.filename)
        if info.filename == target:
            x = data.decode()
            # A4 like the office PCs (the template names no paper size), numbering from 1
            x = re.sub(r'(<pageSetup[^>]*?)\spaperSize="\d+"', r"\1", x, count=1)
            x = re.sub(r"<pageSetup ", '<pageSetup paperSize="9" firstPageNumber="1" useFirstPageNumber="1" ', x, count=1)
            # LibreOffice clips the page number at the template's footer distance; give the footer a little more room
            x = re.sub(r'(<pageMargins[^>]*\sfooter=")[^"]*"', r'\g<1>0.2"', x, count=1)
            data = x.encode()
        zout.writestr(info, data)
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, copy], capture_output=True, timeout=240)
full = os.path.join(tmp, "only.pdf")
n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", full], capture_output=True, text=True).stdout).group(1))
pages = [p for p in range(1, n + 1)
         if title in subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), full, "-"], capture_output=True, text=True).stdout]
parts = []
for p in pages:
    part = os.path.join(tmp, f"p{p}.pdf"); subprocess.run(["pdfseparate", "-f", str(p), "-l", str(p), full, part], check=True); parts.append(part)
if len(parts) == 1: shutil.move(parts[0], out_pdf)
else: subprocess.run(["pdfunite", *parts, out_pdf], check=True)
shutil.rmtree(tmp)
print("pdf", out_pdf, "pages", pages)
