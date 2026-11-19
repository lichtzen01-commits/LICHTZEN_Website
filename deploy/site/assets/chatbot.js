// Bottom-right inquiry chat: topic -> message (+ files) -> email -> (company/name) -> review -> send to the company mailbox.
// Speaks the visitor's language: ?lang= first, otherwise the browser language (other languages fall back to English).
(() => {
  const root = document.querySelector('[data-ltz-chat]');
  if (!root) return;
  const SUPPORTED = ['en', 'zh', 'ja', 'es', 'hi'];
  const param = new URLSearchParams(location.search).get('lang');
  const browser = (navigator.languages || [navigator.language || 'ko']).map(l => String(l).toLowerCase().slice(0, 2));
  const lang = param || (browser[0] === 'ko' ? 'ko' : (browser.find(l => SUPPORTED.includes(l)) || 'en'));
  const T = k => ((window.LTZ_I18N_EXTRA || {})[k] || (window.LTZ_I18N_PLACEHOLDER || {})[k] || {})[lang] || k;

  const fab = root.querySelector('.ltz-chat-fab');
  const panel = root.querySelector('.ltz-chat-panel');
  const log = root.querySelector('.ltz-chat-log');
  const chips = root.querySelector('.ltz-chat-chips');
  const form = root.querySelector('.ltz-chat-form');
  const input = form.querySelector('#ltz-chat-input');
  const fileInput = form.querySelector('input[type=file]');
  const privacy = root.querySelector('[data-chat-privacy]');
  const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  let state = 'start'; let data = {files: []};

  // Translate the static chat text when the page itself is Korean but the visitor is not.
  const localize = () => {
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let n;
    while ((n = w.nextNode())) { const k = n.nodeValue.trim(); const v = T(k); if (k && v !== k) n.nodeValue = n.nodeValue.replace(k, v); }
    input.placeholder = T(input.getAttribute('placeholder'));
    root.querySelectorAll('[aria-label]').forEach(el => el.setAttribute('aria-label', T(el.getAttribute('aria-label'))));
  };
  if (lang !== 'ko' && !window.LTZ_I18N_EXTRA) {
    const s = document.createElement('script');
    s.src = (document.querySelector('script[src*="chatbot.js"]') || {src: '/assets/chatbot.js'}).src.replace('chatbot.js', 'i18n.js');
    s.onload = localize; document.head.appendChild(s);
  } else if (lang !== 'ko') localize();

  const open = on => {
    panel.hidden = !on; fab.hidden = on;
    root.classList.toggle('is-open', on);
    fab.setAttribute('aria-expanded', String(on));
    if (on) input.focus(); else fab.focus();
  };
  fab.addEventListener('click', () => open(true));
  root.querySelector('.ltz-chat-close').addEventListener('click', () => open(false));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !panel.hidden) open(false); });

  const scroll = () => { log.scrollTop = log.scrollHeight; };
  const bubble = (who, text) => {
    const d = document.createElement('div'); d.className = 'ltz-msg ' + who;
    [].concat(text).forEach(t => { const p = document.createElement('p'); p.textContent = t; d.appendChild(p); });
    log.appendChild(d); scroll(); return d;
  };
  const ask = (text, type, ph) => {
    bubble('bot', [].concat(text).map(T));
    input.type = type || 'text'; input.placeholder = T(ph || '궁금한 내용을 입력해 주세요');
    form.hidden = false; input.focus();
  };
  const button = (label, cls, fn) => {
    const b = document.createElement('button'); b.type = 'button'; b.className = cls; b.textContent = T(label);
    b.addEventListener('click', fn); return b;
  };
  const size = n => n > 1048576 ? (n / 1048576).toFixed(1) + 'MB' : Math.max(1, Math.round(n / 1024)) + 'KB';

  form.querySelector('.ltz-chat-attach').addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => {
    const picked = [...fileInput.files]; fileInput.value = '';
    if (!picked.length) return;
    const all = data.files.concat(picked);
    if (!window.LTZCheckFiles(all)) { bubble('bot', T('첨부할 수 없는 파일입니다. 파일당 10MB, 5개까지 보낼 수 있고 실행 파일은 보낼 수 없어요.')); return; }
    data.files = all;
    const d = bubble('user', picked.map(f => '📎 ' + f.name + ' (' + size(f.size) + ')')); d.classList.add('file');
  });

  const review = () => {
    state = 'review'; form.hidden = true;
    const d = bubble('bot', T('아래 내용으로 보내드릴까요?'));
    const dl = document.createElement('dl'); dl.className = 'ltz-chat-summary';
    [['문의 분야', data.topic || T('일반 문의')], ['문의 내용', data.message], ['첨부 파일', data.files.map(f => f.name).join(', ') || '-'], ['이메일', data.email], ['회사·성함', data.who || '-']].forEach(([k, v]) => {
      const dt = document.createElement('dt'); dt.textContent = T(k); const dd = document.createElement('dd'); dd.textContent = v; dl.append(dt, dd);
    });
    const consent = document.createElement('label'); consent.className = 'ltz-chat-consent';
    const box = document.createElement('input'); box.type = 'checkbox';
    const span = document.createElement('span'); span.textContent = T('개인정보 수집·이용에 동의합니다.') + ' ';
    const link = privacy.cloneNode(true); link.hidden = false; link.target = '_blank'; link.rel = 'noopener'; link.textContent = T('내용 보기');
    span.appendChild(link); consent.append(box, span);
    const row = document.createElement('div'); row.className = 'ltz-chat-actions';
    const send = button('제출하기', 'ltz-chat-send', async () => {
      if (!box.checked) { consent.classList.add('is-invalid'); bubble('bot', T('개인정보 수집·이용에 동의해 주세요.')); return; }
      send.disabled = true; again.disabled = true; send.textContent = T('보내는 중…');
      // Show the result within ~1.5 s; Apps Script can take several seconds, so a slow request is
      // treated as received and only a later failure is reported.
      const fail = () => bubble('bot', [T('전송하지 못했습니다. 잠시 후 다시 시도하시거나 아래로 연락해 주세요.'), 'itl@lichtzen.com · +82-70-4088-6117']);
      const pending = window.LTZSendInquiry({source: '홈페이지 채팅', topic: data.topic, category: data.category || 'other', message: data.message, email: data.email, who: data.who || '', files: data.files, lang, bot: data.bot});
      const r = await Promise.race([pending, new Promise(ok => setTimeout(() => ok({slow: true}), 1500))]);
      row.remove(); consent.remove(); state = 'sent';
      if (r.test) bubble('bot', [T('지금은 테스트 사이트라 실제로 전송되지 않았습니다.'), T('정식 공개 후에는 담당자 메일로 바로 전달됩니다.')]);
      else if (r.ok || r.slow) bubble('bot', [T('문의가 접수되었습니다.'), T('담당자가 확인한 뒤 입력하신 이메일로 답변드리겠습니다.')]);
      else fail();
      if (r.slow) pending.then(x => { if (!x.ok) fail(); });
      const n = document.createElement('div'); n.className = 'ltz-chat-actions';
      n.appendChild(button('새 문의하기', 'ltz-chat-ghost', restart)); log.appendChild(n); scroll();
    });
    const again = button('다시 작성', 'ltz-chat-ghost', restart);
    row.append(send, again); d.append(dl, consent, row); scroll();
  };
  const restart = () => {
    data = {files: []}; state = 'start';
    log.querySelectorAll('.ltz-msg:not(:first-child),.ltz-chat-actions').forEach(x => x.remove());
    chips.hidden = false; ask('어떤 분야에 관심이 있으신가요?');
  };

  chips.querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
    data.topic = b.textContent; data.category = b.dataset.cat || 'other'; chips.hidden = true; bubble('user', b.textContent); state = 'message';
    ask(['궁금하신 내용을 편하게 적어 주세요. 제품명, 수량, 소재나 공정 조건을 함께 알려 주시면 더 정확히 답변드릴 수 있어요.', '사진·도면·사양서가 있으면 클립 버튼으로 첨부해 주세요.']);
  }));
  form.addEventListener('submit', e => {
    e.preventDefault();
    const v = input.value.trim(); if (!v) return;
    if (form.querySelector('[name=botcheck]').checked) data.bot = true;
    bubble('user', v); input.value = '';
    if (state === 'start' || state === 'message') { chips.hidden = true; data.message = v; state = 'email'; ask('답변 받으실 이메일 주소를 알려 주세요.', 'email', 'name@company.com'); }
    else if (state === 'email') {
      if (!EMAIL.test(v)) { ask('이메일 주소를 다시 확인해 주세요.', 'email', 'name@company.com'); return; }
      data.email = v; state = 'who';
      ask('회사명과 성함을 알려 주시면 더 빠르게 연락드릴 수 있어요. (선택)', 'text', '예) 회사명, 성함');
      const n = document.createElement('div'); n.className = 'ltz-chat-actions';
      n.appendChild(button('건너뛰기', 'ltz-chat-ghost', () => { n.remove(); review(); })); log.appendChild(n); scroll();
    } else if (state === 'who') { log.querySelectorAll('.ltz-chat-actions').forEach(x => x.remove()); data.who = v; review(); }
  });
})();
