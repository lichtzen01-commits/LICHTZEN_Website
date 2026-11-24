// Dropdown menu: show the picture of the hovered or focused link on the right.
(() => {
  document.querySelectorAll('.nav-mega').forEach(panel => {
    const img = panel.querySelector('.mega-figure img');
    const cap = panel.querySelector('.mega-figure figcaption');
    if (!img) return;
    const show = a => {
      const src = a.getAttribute('data-mega-img');
      if (src && img.getAttribute('src') !== src) img.setAttribute('src', src);
      if (cap) cap.textContent = a.textContent;
      panel.querySelectorAll('.mega-links a').forEach(x => x.classList.toggle('is-active', x === a));
    };
    panel.querySelectorAll('.mega-links a').forEach(a => {
      a.addEventListener('mouseenter', () => show(a));
      a.addEventListener('focus', () => show(a));
    });
  });
})();

// Moving the pointer from one menu to the next: keep a menu open across the gap between items,
// and swap panels without replaying the fade, so the dropdown does not blink.
(() => {
  const nav = document.querySelector('.desktop-nav');
  if (!nav) return;
  document.documentElement.classList.add('mega-js');
  const groups = [...nav.querySelectorAll('.nav-group')];
  let timer = 0;
  // While a menu is open the header turns solid and the first-screen film holds still,
  // so nothing moves behind or around the dropdown; the film continues when the menu closes.
  const film = document.querySelector('video.hero-video');
  let resume = false;
  const sync = () => {
    const open = groups.some(x => x.classList.contains('is-hover'));
    if (open === document.documentElement.classList.contains('mega-open')) return;
    document.documentElement.classList.toggle('mega-open', open);
    if (!film) return;
    if (open) { resume = !film.paused; if (resume) film.pause(); }
    else if (resume) { resume = false; film.play().catch(() => {}); }
  };
  const close = g => { g.classList.remove('is-hover'); sync(); };
  groups.forEach(g => {
    g.addEventListener('mouseenter', () => {
      clearTimeout(timer);
      const other = groups.some(x => x !== g && x.classList.contains('is-hover'));
      nav.classList.toggle('is-switching', other);
      groups.forEach(x => { if (x !== g) close(x); });
      g.classList.add('is-hover');
      sync();
    });
  });
  // stay open anywhere on the menu bar (also in the gaps between items); close shortly after leaving it
  nav.addEventListener('mouseleave', () => { clearTimeout(timer); timer = setTimeout(() => { groups.forEach(close); nav.classList.remove('is-switching'); }, 200); });
  nav.addEventListener('mouseenter', () => clearTimeout(timer));
  // a plain link (기술) closes the menu if the pointer rests on it, not when it only passes over
  nav.querySelectorAll(':scope > a').forEach(a => a.addEventListener('mouseenter', () => { clearTimeout(timer); timer = setTimeout(() => { groups.forEach(close); nav.classList.remove('is-switching'); }, 250); }));
})();
