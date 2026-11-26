/* UV-C pages: scroll reveal, count-up figures, growing bars, step cycling */
(function () {
  const page = document.querySelector('.uvc-page');
  if (!page) return;
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.documentElement.classList.add('uvc-motion');

  // reveal: cards and blocks fade up in sequence
  const groups = '.uvc-stats,.uvc-sols,.uvc-choose,.uvc-clinic,.uvc-spaces,.uvc-why,.uvc-steps,.uvc-list,.uvc-rooms,.uvc-models,.uvc-docs,.uvc-petri,.uvc-guide,.uvc-split,.uvc-tlv';
  page.querySelectorAll(groups).forEach(g => [...g.children].forEach((c, i) => { c.classList.add('mv'); c.style.setProperty('--d', Math.min(i, 8) * 80 + 'ms'); }));
  page.querySelectorAll('.uvc-head,.uvc-hero,.uvc-overview,.uvc-fx,.uvc-hosp,.table-scroll,.uvc-feat').forEach(el => el.classList.add('mv'));

  // count-up: ">99.999%", "Log 5.23", "0.007 ppm", "99.9%"
  const count = el => {
    const raw = el.textContent;
    const m = raw.match(/(\d+(?:[.,]\d+)?)/);
    if (!m || still) return;
    const num = parseFloat(m[1].replace(',', '.'));
    const dec = (m[1].split(/[.,]/)[1] || '').length;
    const [pre, post] = [raw.slice(0, m.index), raw.slice(m.index + m[1].length)];
    const t0 = performance.now(), dur = 1400;
    const step = now => {
      const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = pre + (num * e).toFixed(dec) + post;
      if (k < 1) requestAnimationFrame(step); else el.textContent = raw;
    };
    requestAnimationFrame(step);
  };

  const seen = new IntersectionObserver(entries => entries.forEach(en => {
    if (!en.isIntersecting) return;
    const el = en.target;
    el.classList.add('in');
    if (el.matches('.uvc-stat')) count(el.querySelector('strong'));
    seen.unobserve(el);
  }), {threshold: 0.18, rootMargin: '0px 0px -6% 0px'});
  page.querySelectorAll('.mv,.uvc-stat,.uvc-bar,.uvc-fx').forEach(el => seen.observe(el));

  // how-to steps: highlight one step after another while visible
  const steps = page.querySelector('.uvc-steps');
  if (steps && !still) {
    const items = [...steps.children];
    let i = 0, timer = 0;
    const tick = () => { items.forEach((li, n) => li.classList.toggle('is-on', n === i)); i = (i + 1) % items.length; };
    new IntersectionObserver(([en]) => {
      clearInterval(timer);
      if (en.isIntersecting) { tick(); timer = setInterval(tick, 2200); } else items.forEach(li => li.classList.remove('is-on'));
    }, {threshold: 0.35}).observe(steps);
  }

  // pause SVG motion graphics when off screen (saves battery)
  page.querySelectorAll('.uvc-fx').forEach(fx => new IntersectionObserver(([en]) => fx.classList.toggle('is-paused', !en.isIntersecting)).observe(fx));
})();
