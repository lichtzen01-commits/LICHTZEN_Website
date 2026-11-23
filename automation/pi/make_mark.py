"""Shipping mark: slide 1 of the customer's mark PPT with a 'PO NO. : <po>' line, saved as PPTX and as a trimmed PNG."""
import os, subprocess, sys, zipfile
from PIL import Image, ImageOps
src, po, out_pptx, out_png = sys.argv[1:5]
with zipfile.ZipFile(src) as z:
    names = z.namelist(); data = {n: z.read(n) for n in names}
s = data["ppt/slides/slide1.xml"].decode()
s = s.replace('<a:off x="230737" y="4658980"/><a:ext cx="11613733" cy="1938992"/>',
              '<a:off x="230737" y="4420000"/><a:ext cx="11613733" cy="2400000"/>')
i = s.index('name="TextBox 5"'); head, tail = s[:i], s[i:]
tail = tail.replace('sz="4000"', 'sz="3400"').replace('sz="4800"', 'sz="3400"')
j = tail.index("</a:p>") + len("</a:p>")
tail = tail[:j] + ('<a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="en-US" altLang="ko-KR" sz="3400" b="1" dirty="0"/>'
                   f'<a:t>PO NO. : {po}</a:t></a:r></a:p>') + tail[j:]
data["ppt/slides/slide1.xml"] = (head + tail).encode()
with zipfile.ZipFile(out_pptx, "w", zipfile.ZIP_DEFLATED) as z:
    for n in names: z.writestr(n, data[n])
outdir = os.path.dirname(os.path.abspath(out_png))
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, out_pptx], capture_output=True, timeout=180)
pdf = os.path.join(outdir, os.path.splitext(os.path.basename(out_pptx))[0] + ".pdf")
subprocess.run(["pdftoppm", "-f", "1", "-l", "1", "-r", "200", "-png", pdf, os.path.join(outdir, "_m")], check=True)
im = Image.open(os.path.join(outdir, "_m-1.png")).convert("RGB")
b = ImageOps.invert(im).getbbox(); pad = 30
im.crop((max(0, b[0]-pad), max(0, b[1]-pad), min(im.width, b[2]+pad), min(im.height, b[3]+pad))).save(out_png)
print("mark", out_png)
