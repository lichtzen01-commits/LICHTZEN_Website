// Home "LICHTZEN 영상": a small video under the direct contacts. On desktop the section below is tall
// and its frame grows from a small card to nearly full screen while the visitor scrolls,
// then the YouTube video starts (muted, as browsers require). Phones and reduced motion get a plain player.
(() => {
  const stage = document.querySelector('.film-stage');
  if (!stage) return;
  const frame = stage.querySelector('.film-frame');
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
    iframe.title = frame.closest('section').getAttribute('aria-label') || 'LICHTZEN';
    iframe.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    iframe.allowFullscreen = true;
    iframe.addEventListener('load', () => {
      ready = true;
      iframe.contentWindow.postMessage(JSON.stringify({event: 'listening'}), '*');
      if (wantPlay) play();
    });
    frame.appendChild(iframe);
  };
  const play = () => { wantPlay = true; load(); if (ready && !playing) { send('playVideo'); playing = true; frame.classList.add('is-playing'); } };
  const pause = () => { wantPlay = false; if (playing) { send('pauseVideo'); playing = false; } };

  // A click on the poster always plays (with sound controls in the YouTube player).
  frame.querySelector('.film-play').addEventListener('click', () => { frame.classList.add('is-playing'); play(); });
  // The teaser scrolls down to the stage.
  const teaser = document.querySelector('[data-film-teaser]');
  if (teaser) teaser.addEventListener('click', e => {
    e.preventDefault();
    const end = stage.offsetTop + Math.max(0, stage.offsetHeight - innerHeight);
    scrollTo({top: end, behavior: 'smooth'});
  });

  // Load the player shortly before it is needed.
  new IntersectionObserver(es => es.forEach(en => { if (en.isIntersecting) load(); }), {rootMargin: '600px 0px'}).observe(stage);

  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const wide = matchMedia('(min-width: 901px) and (min-height: 560px)');
  const ease = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  let raf = 0;

  const update = () => {
    raf = 0;
    if (!stage.classList.contains('is-scrub')) return;
    const header = (document.querySelector('.site-header') || {}).offsetHeight || 0;
    const r = stage.getBoundingClientRect();
    const run = Math.max(1, r.height - innerHeight);
    const p = Math.min(1, Math.max(0, -r.top / (run * 0.8)));      // fully grown at 80% of the run, then holds
    const e = ease(p);
    const big = Math.min(innerWidth * 0.92, (innerHeight - header - 56) * 16 / 9);
    const small = Math.min(420, innerWidth * 0.3);
    const scale = (small + (big - small) * e) / big;
    frame.style.width = big + 'px';
    frame.style.transform = `translateY(${header / 2}px) scale(${scale})`;
    frame.style.borderRadius = (22 - 12 * e) / scale + 'px';
    frame.style.setProperty('--film-inv', (1 / scale).toFixed(3));   // keeps the play button the same size
    stage.style.setProperty('--film-p', e.toFixed(3));
    if (p > 0.85 && r.bottom > innerHeight * 0.5) play();
    else if (p < 0.5 || r.bottom < innerHeight * 0.3) pause();
  };
  const onScroll = () => { if (!raf) raf = requestAnimationFrame(update); };

  const setup = () => {
    const on = !reduce && wide.matches;
    stage.classList.toggle('is-scrub', on);
    if (!on) { frame.style.width = frame.style.transform = frame.style.borderRadius = ''; stage.style.removeProperty('--film-p'); }
    update();
  };
  addEventListener('scroll', onScroll, {passive: true});
  addEventListener('resize', onScroll);
  wide.addEventListener ? wide.addEventListener('change', setup) : wide.addListener(setup);
  setup();

  // Plain player: pause when it leaves the screen.
  new IntersectionObserver(es => es.forEach(en => { if (!en.isIntersecting) pause(); }), {threshold: 0}).observe(stage);
})();
