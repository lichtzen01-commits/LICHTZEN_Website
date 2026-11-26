"""Contact-first site footer (Korean pages; run before build_langs.py, which localises numbers and email)."""
import glob, os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "deploy/site"
I = lambda d: f'<span aria-hidden="true" class="fc-ico"><svg fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" viewBox="0 0 24 24">{d}</svg></span>'
PHONE = I('<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>')
GLOBE = I('<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>')
MAIL = I('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>')
YT = '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12 31 31 0 0 0 1 16.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8zM9.7 15.1V8.9l5.8 3.1z" fill="currentColor"/></svg>'
LI = '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M20.4 20.5h-3.6v-5.6c0-1.3 0-3-1.8-3s-2.1 1.4-2.1 2.9v5.7H9.3V9h3.4v1.6c.5-.9 1.6-1.8 3.4-1.8 3.6 0 4.3 2.4 4.3 5.5zM5.3 7.4a2.1 2.1 0 1 1 0-4.2 2.1 2.1 0 0 1 0 4.2zM7.1 20.5H3.5V9h3.6zM22.2 0H1.8C.8 0 0 .8 0 1.7v20.6c0 .9.8 1.7 1.8 1.7h20.4c1 0 1.8-.8 1.8-1.7V1.7C24 .8 23.2 0 22.2 0z" fill="currentColor"/></svg>'

FOOTER = (
    '<footer class="site-footer integrated-footer contact-footer"><div class="container">'
    '<div class="footer-contact" data-mail-keep="">'
    f'<div class="fc-card fc-duo">{PHONE}<span class="fc-label">국내 상담</span><a href="tel:0314196700"><strong>031-419-6700</strong></a><a class="fc-mail" href="mailto:ltz@lichtzen.com">ltz@lichtzen.com</a></div>'
    f'<div class="fc-card fc-duo">{GLOBE}<span class="fc-label">해외 영업</span><a href="tel:07040886117"><strong>070-4088-6117</strong></a><a class="fc-mail" href="mailto:itl@lichtzen.com">itl@lichtzen.com</a></div>'
    '<a class="fc-card fc-as" href="/support/lamp-as/"><img alt="램프 A/S 접수 QR 코드" decoding="async" height="1600" loading="lazy" src="/assets/optimized/637167068a01.webp" width="1600"/>'
    '<span class="fc-label">램프 A/S 접수</span><strong>QR 또는 여기를 눌러 접수</strong></a>'
    f'<a class="fc-card" href="https://www.youtube.com/@LICHTZEN" rel="noopener noreferrer" target="_blank"><span aria-hidden="true" class="fc-ico">{YT}</span><span class="fc-label">YouTube</span><strong>@LICHTZEN</strong></a>'
    f'<a class="fc-card" data-social="linkedin" href="https://www.linkedin.com/company/-%EC%A3%BC-%EB%A6%AC%ED%8A%B8%EC%A0%A0/" rel="noopener noreferrer" target="_blank"><span aria-hidden="true" class="fc-ico">{LI}</span><span class="fc-label">LinkedIn</span><strong>LICHTZEN</strong></a>'
    '</div>'
    '<div class="footer-links"><nav aria-label="바로가기">'
    '<a href="/products/">제품 찾기</a><a href="/resources/">사양·카탈로그</a><a href="/lamp/">3D 램프 설계</a>'
    '<a href="/company/location/">오시는 길</a><a href="/company/careers/">채용</a>'
    '<a href="https://www.osucon.co.kr/main.html" rel="noopener noreferrer" target="_blank">오성유니콘 ↗</a></nav>'
    '</div></div>'
    '<div class="footer-bottom"><div class="footer-company"><img alt="LICHTZEN SINCE 1995" class="canonical-logo" decoding="async" height="168" loading="lazy" src="/assets/legacy/a60690006a79.webp" width="360"/>'
    '<p><strong>주식회사 리트젠</strong><span>대표 성수현</span><span>사업자등록번호 113-81-58151</span><br/>경기도 군포시 구군포3길 2 (당정동)</p></div>'
    '<div class="footer-legal"><a href="/privacy/">개인정보처리방침</a><span>© 2026 LICHTZEN CO., LTD.</span></div></div>'
    '</div></footer>')

n = 0
for f in glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True):
    rel = os.path.relpath(f, ROOT)
    if rel.split(os.sep)[0] in ("en", "zh", "ja", "hi", "es", "website", "tools"):
        continue
    s = open(f, encoding="utf-8").read()
    t = re.sub(r'<footer class="site-footer integrated-footer[^"]*">.*?</footer>', FOOTER, s, count=1, flags=re.S)
    if t != s:
        open(f, "w", encoding="utf-8").write(t); n += 1
print("footer on", n, "pages")
