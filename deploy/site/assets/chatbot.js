// LTZ technical chat: visual shell with open/close only. Replies point to the inquiry form until the AI backend is connected.
(() => {
  const root = document.querySelector('[data-ltz-chat]');
  if (!root) return;
  const T = window.LTZ_T || (x => x);
  const fab = root.querySelector('.ltz-chat-fab');
  const panel = root.querySelector('.ltz-chat-panel');
  const log = root.querySelector('.ltz-chat-log');
  const form = root.querySelector('.ltz-chat-form');
  const input = form.querySelector('input');
  const contact = root.querySelector('[data-chat-contact]');
  const open = on => {
    panel.hidden = !on;
    root.classList.toggle('is-open', on);
    fab.setAttribute('aria-expanded', String(on));
    if (on) input.focus(); else fab.focus();
  };
  fab.addEventListener('click', () => open(panel.hidden));
  root.querySelector('.ltz-chat-close').addEventListener('click', () => open(false));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !panel.hidden) open(false); });
  const bubble = (who, text) => {
    const d = document.createElement('div');
    d.className = 'ltz-msg ' + who;
    const p = document.createElement('p'); p.textContent = text; d.appendChild(p);
    log.appendChild(d);
    return d;
  };
  const reply = need => {
    const d = bubble('bot', T('현재는 시범 화면이라 AI 답변이 아직 연결되지 않았습니다.'));
    const p = document.createElement('p'); p.textContent = T('문의 내용을 남겨 주시면 담당 엔지니어가 직접 연락드립니다.'); d.appendChild(p);
    const a = contact.cloneNode(true); a.hidden = false; a.className = 'ltz-chat-link';
    const u = new URL(a.getAttribute('href'), location.href); u.searchParams.set('need', need || 'other');
    a.setAttribute('href', u.pathname + u.search); d.appendChild(a);
    log.scrollTop = log.scrollHeight;
  };
  root.querySelectorAll('.ltz-chat-chips button').forEach(b => b.addEventListener('click', () => {
    bubble('user', b.textContent); reply(b.dataset.need);
  }));
  form.addEventListener('submit', e => {
    e.preventDefault();
    const v = input.value.trim(); if (!v) return;
    bubble('user', v); input.value = ''; reply('other');
  });
})();
