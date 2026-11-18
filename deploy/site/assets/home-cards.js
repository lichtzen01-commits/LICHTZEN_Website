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
