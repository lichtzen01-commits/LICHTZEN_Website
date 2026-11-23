"""Shipping mark laid out for the narrow, tall MARKS cell of the invoice: the diamond with the consignee on top,
then destination, PO number, SHIPPING MARK, MADE IN KOREA, each line as wide as the cell allows."""
import sys
from PIL import Image, ImageDraw, ImageFont
consignee, dest, po, out, ratio = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5])
F = "/usr/share/fonts/opentype/inter/"
W = 900; H = int(W * ratio)
img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
def fit(text, font_file, max_w, start=400):
    size = start
    while size > 8:
        f = ImageFont.truetype(F + font_file, size)
        if d.textlength(text, font=f) <= max_w: return f
        size -= 2
    return ImageFont.truetype(F + font_file, 8)
lines = [(dest, "Inter-Regular.otf"), ("PO NO. :", "Inter-Regular.otf"), (po, "Inter-Bold.otf"),
         ("SHIPPING MARK", "Inter-Regular.otf"), ("MADE IN KOREA", "Inter-Regular.otf")]
# one font size for all lines: the size at which the widest line fills 92% of the width
size = min(fit(t, f, W * 0.92).size for t, f in lines)
fonts = [ImageFont.truetype(F + f, size) for _, f in lines]
line_h = [f.getbbox("Hg")[3] - f.getbbox("Hg")[1] for f in fonts]
dw = W - 24; dh = int(dw * 0.4923)                     # same proportion as the diamond in the PPT
text_block = sum(line_h) 
gap = max(int(size * 0.45), (H - dh - text_block - 40) // (len(lines) + 1))
gap = min(gap, int(size * 2.6))
total = dh + text_block + gap * (len(lines) + 0) 
y0 = (H - total) // 2
cx = W // 2
pts = [(cx, y0), (W - 12, y0 + dh // 2), (cx, y0 + dh), (12, y0 + dh // 2)]
d.line(pts + [pts[0]], fill="black", width=max(8, W // 70), joint="curve")
name_f = fit(consignee, "Inter-Black.otf", dw * 0.62)
bb = d.textbbox((0, 0), consignee, font=name_f)
d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y0 + dh / 2 - (bb[3] - bb[1]) / 2 - bb[1]), consignee, fill="black", font=name_f)
y = y0 + dh + gap
for (t, _), f, h in zip(lines, fonts, line_h):
    bb = d.textbbox((0, 0), t, font=f)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y - f.getbbox("Hg")[1]), t, fill="black", font=f)
    y += h + gap
img.save(out); print("mark", out, img.size, "font", size)
