// Home page: section-by-section scrolling with ease-in-out (desktop wheel and keys),
// plus the scroll-triggered timeline and world-map light-up.
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Light up the export map and run the process timeline when they come into view.
  if (!reduce && 'IntersectionObserver' in window) {
    [['.global-map-panel', '.global-business', 'is-lit', 0.3], ['.flow-timeline', '.project-flow', 'is-run', 0.4]].forEach(([el, sec, cls, th]) => {
      const target = document.querySelector(el); const section = document.querySelector(sec);
      if (!target || !section) return;
      section.classList.add(cls + '-ready');
      const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { section.classList.add(cls); io.disconnect(); } }), {threshold: th});
      io.observe(target);
    });
  }

  if (reduce || !document.body.classList.contains('home-page')) return;
  if (!matchMedia('(min-width: 901px) and (pointer: fine)').matches) return;   // phones and tablets keep native scrolling
  const root = document.documentElement;
  root.classList.add('smooth-snap');
  const sections = [...document.querySelectorAll('main>section, .global-business, .final-screen')];
  const ease = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);   // easeInOutCubic
  let busy = false; let lockUntil = 0; let lastWheel = 0;

  const tops = () => sections.map(s => Math.round(s.getBoundingClientRect().top + scrollY));
  const animate = to => {
    const from = scrollY; const d = to - from;
    if (Math.abs(d) < 2) return;
    busy = true;
    const dur = Math.min(1100, 650 + Math.abs(d) * 0.25); const t0 = performance.now();
    const step = now => {
      const p = Math.min(1, (now - t0) / dur);
      scrollTo({top: from + d * ease(p), behavior: 'instant'});
      if (p < 1) requestAnimationFrame(step);
      else { busy = false; lockUntil = performance.now() + 180; }
    };
    requestAnimationFrame(step);
  };
  // Returns the scroll target for one step, or null to let the browser scroll natively (inside a tall section).
  const target = dir => {
    const y = scrollY; const vh = innerHeight; const t = tops();
    let i = 0; t.forEach((top, k) => { if (top <= y + 4) i = k; });
    const top = t[i]; const h = sections[i].offsetHeight; const bottom = top + h;
    const max = root.scrollHeight - vh;
    const tall = n => n > vh * 1.12;                                  // a few px taller than the screen still counts as one screen
    if (dir > 0) {
      if (tall(h) && bottom - (y + vh) > 6) return null;          // still inside a tall section
      return i + 1 < sections.length ? t[i + 1] : max;
    }
    if (y - top > 6) {
      if (y > bottom - 6) return Math.max(top, bottom - vh);            // coming back up from the footer
      return tall(h) && y - top > vh * 0.15 ? null : top;
    }
    if (i === 0) return 0;
    const ph = sections[i - 1].offsetHeight;
    return tall(ph) ? t[i - 1] + ph - vh : t[i - 1];                 // land on the bottom of a tall previous section
  };
  const go = (dir, e) => {
    const to = target(dir);
    if (to === null) return false;
    if (e) e.preventDefault();
    if (!busy) animate(to);
    return true;
  };

  addEventListener('wheel', e => {
    if (e.ctrlKey || Math.abs(e.deltaY) < Math.abs(e.deltaX)) return;
    if (e.target.closest && e.target.closest('.ltz-chat-panel, .nav-panel, .mobile-nav')) return;
    const now = performance.now(); const gap = now - lastWheel; lastWheel = now;
    if (busy) { e.preventDefault(); return; }
    if (now < lockUntil || (gap < 160 && now < lockUntil + 400)) { e.preventDefault(); lockUntil = now + 180; return; }   // trackpad momentum tail
    if (Math.abs(e.deltaY) < 3) return;
    go(Math.sign(e.deltaY), e);
  }, {passive: false});

  addEventListener('keydown', e => {
    if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.target.closest && e.target.closest('input, textarea, select, [contenteditable], .ltz-chat-panel')) return;
    const dir = {ArrowDown: 1, PageDown: 1, ' ': e.shiftKey ? -1 : 1, ArrowUp: -1, PageUp: -1}[e.key];
    if (dir) { if (busy) e.preventDefault(); else go(dir, e); }
  });
})();
