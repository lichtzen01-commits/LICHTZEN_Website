// Desktop home: every section should fit in one screen below the fixed header.
// If a section's content is taller than the space left, scale its content down (CSS zoom) just enough.
(() => {
  const secs = [...document.querySelectorAll('.home-page main>section:not(.hero), .home-page .global-business, .home-page .final-screen')];
  if (!secs.length) return;
  const fit = () => {
    const desktop = innerWidth >= 901 && innerHeight >= 500;
    const header = (document.querySelector('.site-header') || {}).offsetHeight || 0;
    secs.forEach(s => {
      // Scale the centred containers only; full-width parts (logo marquee) keep their width.
      const boxes = [...s.querySelectorAll(':scope > .container, :scope > div > .container, :scope > div:not([class*="marquee"]):not(.container)')]
        .filter(b => !b.querySelector('.container'));
      if (!boxes.length) return;
      boxes.forEach(b => { b.style.zoom = ''; });
      if (!desktop) return;
      const cs = getComputedStyle(s);
      const top = Math.max(parseFloat(cs.paddingTop), header + 16);
      const avail = innerHeight - top - Math.max(parseFloat(cs.paddingBottom), 16) - 20;   // 20px breathing room
      const kids = [...s.children];
      const height = () => {
        let a = 1e9, z = 0;
        kids.forEach(k => { const r = k.getBoundingClientRect(); if (r.height) { a = Math.min(a, r.top); z = Math.max(z, r.bottom); } });
        return z - a;
      };
      for (let i = 0; i < 5; i++) {               // repeat: content with vh units changes when zoomed
        const h = height();
        if (h <= avail + 1) break;
        const cur = parseFloat(boxes[0].style.zoom) || 1;
        const z = Math.max(0.62, cur * (1 - (h - avail) / h / (boxes.length > 1 ? 0.8 : 1)));
        boxes.forEach(b => { b.style.zoom = z.toFixed(3); });
      }
    });
  };
  let t; addEventListener('resize', () => { clearTimeout(t); t = setTimeout(fit, 150); });
  addEventListener('load', fit);
  if (document.fonts) document.fonts.ready.then(fit);
  fit();
})();
