// Home "APPLICATIONS": four photo strips; the open strip widens and shows its description.
// Mouse: hover or focus opens a strip. Touch: the first tap opens it, a second tap follows the link.
// It moves to the next strip every 6 s until the visitor interacts, and stops for reduced motion.
(() => {
  const box = document.querySelector('[data-app-strips]');
  if (!box) return;
  const strips = [...box.querySelectorAll('.app-strip')];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let current = 0, timer = null, touched = false;

  const open = i => {
    current = i;
    strips.forEach((s, n) => {
      s.classList.toggle('is-open', n === i);
      s.setAttribute('aria-expanded', n === i ? 'true' : 'false');
    });
  };
  const stop = () => { clearInterval(timer); timer = null; };
  const start = () => {
    if (reduce || timer) return;
    timer = setInterval(() => open((current + 1) % strips.length), 6000);
  };

  strips.forEach((s, i) => {
    s.addEventListener('mouseenter', () => { if (!touched) { stop(); open(i); } });
    // Keyboard focus opens a strip; a tap also focuses the link, which must not count as opening it.
    s.addEventListener('focus', () => { if (s.matches(':focus-visible')) { stop(); open(i); } });
    s.addEventListener('touchstart', () => { touched = true; }, {passive: true});
    s.addEventListener('click', e => {
      if (!s.classList.contains('is-open')) { e.preventDefault(); stop(); open(i); }
    });
  });
  box.addEventListener('mouseleave', () => { if (!touched) start(); });

  // Only cycle while the section is on screen.
  new IntersectionObserver(es => es.forEach(en => (en.isIntersecting ? start() : stop())), {threshold: 0.35}).observe(box);
  open(0);
})();
