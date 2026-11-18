// Home card rows: advance one card every 6 seconds; pause while the visitor hovers, focuses or the row is off screen.
(() => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('.manual-card-viewport').forEach(viewport => {
    let paused = false, visible = false;
    const pause = v => () => { paused = v; };
    ['mouseenter', 'focusin', 'touchstart'].forEach(e => viewport.addEventListener(e, pause(true), {passive: true}));
    ['mouseleave', 'focusout'].forEach(e => viewport.addEventListener(e, pause(false)));
    new IntersectionObserver(es => es.forEach(x => { visible = x.isIntersecting; }), {threshold: 0.4}).observe(viewport);
    setInterval(() => {
      if (paused || !visible || document.hidden) return;
      const card = viewport.querySelector('a');
      const step = card ? card.getBoundingClientRect().width + 24 : viewport.clientWidth / 3;
      const atEnd = viewport.scrollLeft + viewport.clientWidth >= viewport.scrollWidth - 4;
      viewport.scrollTo({left: atEnd ? 0 : viewport.scrollLeft + step, behavior: 'smooth'});
    }, 6000);
  });
})();
// Sections fade up as they come into view.
(() => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
  const sections = document.querySelectorAll('.home-page main>section:not(.hero), .home-page .global-business, .home-page .final-screen');
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } }), {threshold: 0.18});
  sections.forEach(s => { s.classList.add('reveal-ready'); io.observe(s); });
})();
