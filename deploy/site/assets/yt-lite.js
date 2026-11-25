// Video cards: a local thumbnail with a play button. Clicking opens the YouTube player full screen
// (an overlay over the whole page, and real full screen where the browser allows it). Esc, the X button
// or leaving full screen closes it.
(() => {
  let box = null;
  const close = () => {
    if (!box) return;
    const b = box; box = null;
    if (document.fullscreenElement === b) document.exitFullscreen().catch(() => {});
    b.remove();
    document.documentElement.classList.remove('yt-open');
  };
  const open = (id, short, label) => {
    close();
    const lang = (document.documentElement.lang || 'ko').slice(0, 2);
    box = document.createElement('div');
    box.className = 'yt-modal' + (short ? ' is-short' : '');
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', label || 'video');
    box.innerHTML = `<button class="yt-modal-close" type="button" aria-label="${({ko:'닫기',en:'Close',zh:'关闭',ja:'閉じる',hi:'बंद करें',es:'Cerrar'})[lang] || 'Close'}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg></button><div class="yt-modal-stage"></div>`;
    const f = document.createElement('iframe');
    const cc = lang !== 'ko' ? `&cc_load_policy=1&cc_lang_pref=${lang === 'zh' ? 'zh-Hans' : lang}` : '';
    f.src = `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0&modestbranding=1&playsinline=1&fs=1&hl=${lang}${cc}`;
    f.title = label || 'video';
    f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.allowFullscreen = true;
    box.querySelector('.yt-modal-stage').appendChild(f);
    box.addEventListener('click', e => { if (e.target === box || e.target.closest('.yt-modal-close')) close(); });
    document.body.appendChild(box);
    document.documentElement.classList.add('yt-open');
    if (box.requestFullscreen) box.requestFullscreen().catch(() => {});
    box.querySelector('.yt-modal-close').focus({preventScroll: true});
  };
  document.addEventListener('click', e => {
    const btn = e.target.closest('[data-yt]');
    if (!btn) return;
    e.preventDefault();
    open(btn.dataset.yt, !!btn.closest('.is-short'), btn.getAttribute('aria-label'));
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
  document.addEventListener('fullscreenchange', () => { if (box && !document.fullscreenElement) close(); });

  // Short process clips: play only while on screen (muted loop), never for reduced motion.
  const clips = document.querySelectorAll('video[data-loop-clip]');
  if (clips.length && 'IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const io = new IntersectionObserver(es => es.forEach(en => {
      const v = en.target;
      if (en.isIntersecting) { v.preload = 'auto'; v.play().catch(() => {}); } else v.pause();
    }), {threshold: 0.35});
    clips.forEach(v => io.observe(v));
  }
})();
