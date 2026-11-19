// Product / application showcase: list on the left, one large panel on the right.
// Hover or focus a name to show it; otherwise it advances every 6 s while visible (not with reduced motion).
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('[data-showcase]').forEach(box => {
    const items = [...box.querySelectorAll('.showcase-item')];
    const panels = [...box.querySelectorAll('.showcase-panel')];
    let cur = 0; let paused = false; let visible = false; let timer = null;
    const show = i => {
      cur = (i + items.length) % items.length;
      items.forEach((it, k) => { it.classList.toggle('is-active', k === cur); it.setAttribute('aria-current', k === cur ? 'true' : 'false'); });
      panels.forEach((p, k) => { p.classList.toggle('is-active', k === cur); p.setAttribute('aria-hidden', String(k !== cur)); });
      box.classList.remove('is-timing'); void box.offsetWidth;                // restart the progress bar
      if (!reduce && !paused && visible) box.classList.add('is-timing');
    };
    const tick = () => { if (!paused && visible && !document.hidden) show(cur + 1); };
    const run = () => { clearInterval(timer); if (!reduce) timer = setInterval(tick, 6000); };
    items.forEach((it, k) => {
      it.addEventListener('mouseenter', () => { paused = true; show(k); });
      it.addEventListener('focus', () => { paused = true; show(k); });
    });
    box.addEventListener('mouseleave', () => { paused = false; show(cur); run(); });
    box.addEventListener('focusout', e => { if (!box.contains(e.relatedTarget)) { paused = false; show(cur); run(); } });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(es => es.forEach(e => { visible = e.isIntersecting; if (visible) { show(cur); run(); } else { clearInterval(timer); box.classList.remove('is-timing'); } }), {threshold: 0.4}).observe(box);
    }
    show(0);
  });
})();
