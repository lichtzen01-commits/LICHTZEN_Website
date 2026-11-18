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
