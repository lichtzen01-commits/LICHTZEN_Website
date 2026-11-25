/* Product selection guide: question chips -> live candidate list -> contact */
(function () {
  const root = document.querySelector('[data-selector]');
  if (!root) return;
  const T = s => (window.LTZ_T ? window.LTZ_T(s) : s);
  const cards = [...root.querySelectorAll('.sel-card')];
  const chips = [...root.querySelectorAll('.sel-chip')];
  const state = {p: '', m: '', l: '', w: '', c: ''};
  const n = root.querySelector('[data-sel-n]');
  const label = root.querySelector('[data-sel-label]');
  const note = root.querySelector('[data-sel-note]');
  const reset = root.querySelector('[data-sel-reset]');
  const go = root.querySelector('[data-sel-go]');
  const NEED = {cure: 'system', dry: 'system', clean: 'system', replace: 'lamp'};
  const words = el => (el || '').split(/\s+/).filter(Boolean);
  const fits = (card, key, attr) => {
    const v = state[key];
    if (!v) return true;
    const list = words(card.dataset[attr]);
    return list.includes('*') || list.includes(v);
  };
  const match = (card, keys) => keys.every(([k, a]) => fits(card, k, a));
  const ALL = [['p', 'p'], ['m', 'm'], ['l', 'l'], ['w', 'wave'], ['c', 'cooling']];

  function chipText(key) {
    const b = chips.find(c => c.dataset.q === key && c.dataset.v === state[key]);
    return b ? b.querySelector('strong').textContent.trim() : '';
  }

  let render = function () {
    const simple = state.p === 'clean' || state.p === 'replace';
    root.querySelectorAll('[data-group="m"],[data-group="l"]').forEach(f => { f.hidden = simple; });
    if (simple) { state.m = ''; state.l = ''; }
    chips.forEach(c => c.setAttribute('aria-pressed', String(state[c.dataset.q] === c.dataset.v)));

    // relax the least important answers first when nothing fits
    let keys = ALL.slice(), shown = cards.filter(c => match(c, keys)), relaxed = false;
    while (!shown.length && keys.length > 1) {
      keys.pop(); relaxed = true;
      shown = cards.filter(c => match(c, keys));
    }
    cards.forEach(c => { c.hidden = !shown.includes(c); });
    const any = Object.values(state).some(Boolean);
    n.textContent = shown.length;
    label.textContent = any ? T('개 후보 제품') : T('개 제품 · 질문에 답하면 후보가 좁혀집니다');
    note.hidden = !relaxed;
    reset.hidden = !any;

    const parts = ['p', 'm', 'l', 'w', 'c'].map(chipText).filter(Boolean);
    const ready = [...root.querySelectorAll('.sel-check input:checked')].map(i => i.closest('label').textContent.trim());
    let product = T('제품 선정 가이드') + (parts.length ? ': ' + parts.join(' / ') : '');
    if (ready.length) product += '\n' + T('준비된 정보') + ': ' + ready.join(', ');
    const q = new URLSearchParams({need: NEED[state.p] || 'system', product});
    const lang = new URLSearchParams(window.LTZ_PORTABLE_SEARCH || location.search).get('lang');
    if (lang) q.set('lang', lang);
    const base = go.getAttribute('href').split('?')[0];
    go.setAttribute('href', base + '?' + q.toString());
  };

  // phones: the list sits below the questions, so offer a jump to it
  const float = root.querySelector('[data-sel-float]');
  const results = root.querySelector('.sel-results');
  let inView = false;
  const syncFloat = () => {
    const phone = matchMedia('(max-width:900px)').matches;
    float.hidden = !(phone && Object.values(state).some(Boolean) && !inView);
    root.querySelector('[data-sel-fn]').textContent = n.textContent;
  };
  if ('IntersectionObserver' in window) new IntersectionObserver(e => { inView = e[0].isIntersecting; syncFloat(); }, {rootMargin: '0px 0px -40% 0px'}).observe(results);
  float.addEventListener('click', () => results.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion:reduce)').matches ? 'auto' : 'smooth', block: 'start'}));

  chips.forEach(c => c.addEventListener('click', () => {
    const k = c.dataset.q;
    state[k] = state[k] === c.dataset.v ? '' : c.dataset.v;
    render(); syncFloat();
  }));
  reset.addEventListener('click', () => { Object.keys(state).forEach(k => { state[k] = ''; }); render(); syncFloat(); });
  root.querySelectorAll('.sel-check input').forEach(i => i.addEventListener('change', render));

  // desktop: keep the question panel vertically centred in the space below the header
  const panel = root.querySelector('.sel-panel');
  const centre = () => {
    if (!matchMedia('(min-width:901px)').matches) { panel.style.top = ''; return; }
    const head = (document.querySelector('.site-header') || {offsetHeight: 80}).offsetHeight;
    const free = innerHeight - head - panel.offsetHeight;
    panel.style.top = (head + Math.max(12, free / 2)) + 'px';
  };
  addEventListener('resize', centre);
  root.querySelectorAll('.sel-more').forEach(d => d.addEventListener('toggle', centre));
  const _render = render;
  render = function () { _render(); centre(); };

  // ?category=… from older links maps to a purpose
  const old = new URLSearchParams(window.LTZ_PORTABLE_SEARCH || location.search).get('purpose');
  if (old && NEED[old]) state.p = old;
  render();
})();
