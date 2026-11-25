// Video cards: a local thumbnail with a play button; the YouTube player loads only when clicked.
(() => {
  document.addEventListener('click', e => {
    const btn = e.target.closest('[data-yt]');
    if (!btn) return;
    e.preventDefault();
    const id = btn.dataset.yt;
    const lang = (document.documentElement.lang || 'ko').slice(0, 2);
    const f = document.createElement('iframe');
    f.src = `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0&modestbranding=1&playsinline=1&hl=${lang}`;
    f.title = btn.getAttribute('aria-label') || 'video';
    f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.allowFullscreen = true;
    f.className = 'yt-frame';
    btn.replaceWith(f);
  });
})();
