// Home "LICHTZEN 영상": a small video card under the direct contacts.
// Desktop: while the visitor scrolls on, the card itself grows out of its place to nearly full screen
// over a darkening backdrop, then the YouTube video starts (muted, as browsers require).
// Phones, tablets and reduced motion get a plain player below the contacts.
(() => {
  const stage = document.querySelector('.film-stage');
  if (!stage) return;
  const frame = stage.querySelector('.film-frame');
  const home = frame.parentNode;
  const teaser = document.querySelector('[data-film-teaser]');
  const thumb = teaser && teaser.querySelector('.need-video-thumb');
  const id = frame.dataset.film;
  const lang = (document.documentElement.lang || 'ko').slice(0, 2);
  let iframe = null, ready = false, playing = false, wantPlay = false;

  const send = func => {
    if (iframe && ready) iframe.contentWindow.postMessage(JSON.stringify({event: 'command', func, args: []}), '*');
  };
  const load = () => {
    if (iframe) return;
    iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube-nocookie.com/embed/${id}?enablejsapi=1&mute=1&playsinline=1&rel=0&modestbranding=1&loop=1&playlist=${id}&hl=${lang}&origin=${encodeURIComponent(location.origin)}`;
    iframe.title = stage.getAttribute('aria-label') || 'LICHTZEN';
    iframe.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    iframe.allowFullscreen = true;
    iframe.addEventListener('load', () => {
      ready = true;
      iframe.contentWindow.postMessage(JSON.stringify({event: 'listening'}), '*');
      if (wantPlay) play();
    });
    frame.appendChild(iframe);
  };
  const play = () => { wantPlay = true; load(); frame.classList.add('is-playing'); if (ready && !playing) { send('playVideo'); playing = true; } };
  const pause = () => { wantPlay = false; if (playing) { send('pauseVideo'); playing = false; } if (scrub) frame.classList.remove('is-playing'); };

  // Load the player shortly before it is needed.
  new IntersectionObserver(es => es.forEach(en => { if (en.isIntersecting) load(); }), {rootMargin: '900px 0px'}).observe(stage);

  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const wide = matchMedia('(min-width: 901px) and (min-height: 560px)');
  const ease = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const backdrop = document.createElement('div');
  backdrop.className = 'film-backdrop';
  document.body.appendChild(backdrop);
  let scrub = false, raf = 0, activeUntil = 0;

  // Scroll positions (page coordinates) for the current layout.
  const marks = () => {
    const vh = innerHeight; const top = stage.getBoundingClientRect().top + scrollY;
    const start = top - vh;                         // the stage starts to enter: the card is in its place
    const grown = top;                              // fully grown when the stage reaches the top (one snap)
    const hold = top + stage.offsetHeight - vh;     // after this the video scrolls away with the page
    return {start, grown, hold, vh};
  };

  const update = () => {
    raf = 0;
    if (!scrub) return;
    const {start, grown, hold, vh} = marks();
    const y = scrollY; const vw = document.documentElement.clientWidth;
    const p = Math.min(1, Math.max(0, (y - start) / (grown - start)));
    const e = ease(p);
    // grown size: the largest 16:9 box that fits the whole screen (it covers the header while it plays)
    const bigW = Math.min(vw, vh * 16 / 9);
    const bigH = bigW * 9 / 16;
    const to = {x: (vw - bigW) / 2, y: (vh - bigH) / 2, w: bigW};
    const t = thumb.getBoundingClientRect();
    const from = {x: t.left, y: t.top, w: t.width || 128};
    let x = from.x + (to.x - from.x) * e, top = from.y + (to.y - from.y) * e;
    const w = from.w + (to.w - from.w) * e;
    if (y > hold) top -= y - hold;                  // leave with the page after the hold
    const s = w / bigW;
    frame.style.width = bigW + 'px';
    frame.style.transform = `translate(${x}px, ${top}px) scale(${s})`;
    frame.style.borderRadius = (10 * (1 - e)) / s + 'px';
    frame.style.setProperty('--film-inv', ((0.5 + 0.5 * e) / s).toFixed(3));
    const onScreen = top < vh && top + bigH * s > 0;
    frame.style.visibility = onScreen ? 'visible' : 'hidden';
    frame.classList.toggle('is-grown', p > 0.98);
    backdrop.style.opacity = y < hold ? (e * 0.94).toFixed(3) : 0;
    if (p > 0.98 && y < hold + vh * 0.3) play();
    else if (p < 0.7 || y > hold + vh * 0.3) pause();
    // keep following the card for a moment: the section's slide-in animation moves it without a scroll event
    if (performance.now() < activeUntil && !raf) raf = requestAnimationFrame(update);
  };
  const onScroll = () => { activeUntil = performance.now() + 1500; if (!raf) raf = requestAnimationFrame(update); };
  ['transitionstart', 'transitionend', 'animationstart', 'animationend'].forEach(t => document.addEventListener(t, onScroll, true));

  const toGrown = () => { const {grown} = marks(); scrollTo({top: grown, behavior: 'smooth'}); };
  if (teaser) teaser.addEventListener('click', e => {
    e.preventDefault();
    if (scrub) toGrown(); else stage.scrollIntoView({behavior: 'smooth', block: 'center'});
  });
  frame.querySelector('.film-play').addEventListener('click', () => { if (scrub && !frame.classList.contains('is-grown')) toGrown(); else play(); });

  const setup = () => {
    scrub = !reduce && wide.matches && !!thumb;
    document.body.classList.toggle('film-scrub', scrub);
    stage.classList.toggle('is-scrub', scrub);
    // a fixed element must not sit inside a transformed (revealed) section, so the frame moves to <body>
    (scrub ? document.body : home).appendChild(frame);
    if (!scrub) {
      ['width', 'transform', 'borderRadius', 'visibility'].forEach(k => { frame.style[k] = ''; });
      backdrop.style.opacity = 0;
    }
    update();
  };
  addEventListener('scroll', onScroll, {passive: true});
  addEventListener('resize', onScroll);
  wide.addEventListener ? wide.addEventListener('change', setup) : wide.addListener(setup);
  setup();
  addEventListener('load', onScroll);

  // Plain player: pause when it leaves the screen.
  new IntersectionObserver(es => es.forEach(en => { if (!scrub && !en.isIntersecting) pause(); }), {threshold: 0}).observe(stage);
})();
