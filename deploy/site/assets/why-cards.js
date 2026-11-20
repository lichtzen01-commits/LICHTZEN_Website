// "Why LICHTZEN" cards: staggered entrance, key numbers count up, light spotlight follows the pointer
// (a one-time light sweep on touch screens). Runs after site.js so it also works on translated pages.
(() => {
  const grid = document.querySelector('.why-reasons');
  if (!grid) return;
  const cards = [...grid.querySelectorAll('article')];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const KEY = /(^|[^\d.,])(31|22|15|40|18|39)(?![\d.,])/g;   // facts from the company profile, not years or ISO numbers
  const HAS = new RegExp(KEY.source);

  // Wrap the key numbers so they can be highlighted and counted.
  cards.forEach(card => {
    card.querySelectorAll('h3, p').forEach(el => {
      const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); const nodes = []; let n;
      while ((n = w.nextNode())) if (HAS.test(n.nodeValue)) nodes.push(n);
      nodes.forEach(node => {
        const frag = document.createDocumentFragment(); let last = 0; const s = node.nodeValue;
        s.replace(KEY, (m, pre, num, idx) => {
          frag.append(s.slice(last, idx) + pre);
          const span = document.createElement('span');
          span.className = 'why-num'; span.dataset.to = num; span.textContent = num;
          span.style.minWidth = num.length + 'ch';
          frag.append(span); last = idx + m.length; return m;
        });
        frag.append(s.slice(last)); node.replaceWith(frag);
      });
    });
  });

  const ease = t => 1 - Math.pow(1 - t, 3);
  const count = (span, delay) => {
    const to = +span.dataset.to;
    if (reduce) { span.textContent = to; return; }
    span.textContent = '0';
    setTimeout(() => {
      const t0 = performance.now(); const dur = 1400;
      const step = now => { const p = Math.min(1, (now - t0) / dur); span.textContent = Math.round(to * ease(p)); if (p < 1) requestAnimationFrame(step); };
      requestAnimationFrame(step);
    }, delay);
  };

  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => {
      if (!es.some(e => e.isIntersecting)) return;
      io.disconnect();
      cards.forEach((card, i) => card.querySelectorAll('.why-num').forEach(s => count(s, 250 + i * 70)));
    }, {threshold: 0.3});
    io.observe(grid);
    // Touch screens have no hover: sweep light across each card once as it comes into view.
    if (!reduce && matchMedia('(hover: none)').matches) {
      const sw = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-swept'); sw.unobserve(e.target); } }), {threshold: 0.6});
      cards.forEach(c => sw.observe(c));
    }
  }

  // Pointer spotlight.
  cards.forEach(card => card.addEventListener('pointermove', e => {
    const r = card.getBoundingClientRect();
    card.style.setProperty('--mx', (e.clientX - r.left) + 'px');
    card.style.setProperty('--my', (e.clientY - r.top) + 'px');
  }));
})();

// Global business metrics (100 / 1,000 / 39) count up when the section comes into view.
(() => {
  const nums = [...document.querySelectorAll('.business-metrics article strong')].map(st => {
    const node = [...st.childNodes].find(n => n.nodeType === 3 && /\d/.test(n.nodeValue));
    if (!node) return null;
    const txt = node.nodeValue.trim(); const to = +txt.replace(/,/g, '');
    const span = document.createElement('span'); span.className = 'metric-num'; span.textContent = txt; span.style.minWidth = txt.length + 'ch';
    node.replaceWith(span); return {span, to, txt};
  }).filter(Boolean);
  if (!nums.length || matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
  const fmt = n => n.toLocaleString('en-US');
  nums.forEach(n => { n.span.textContent = '0'; });
  const io = new IntersectionObserver(es => {
    if (!es.some(e => e.isIntersecting)) return;
    io.disconnect();
    nums.forEach((n, i) => setTimeout(() => {
      const t0 = performance.now(); const dur = 1800;
      const step = now => { const p = Math.min(1, (now - t0) / dur); n.span.textContent = fmt(Math.round(n.to * (1 - Math.pow(1 - p, 3)))); if (p < 1) requestAnimationFrame(step); else n.span.textContent = n.txt; };
      requestAnimationFrame(step);
    }, 200 + i * 150));
  }, {threshold: 0.15});
  io.observe(document.querySelector('.business-metrics'));
})();
