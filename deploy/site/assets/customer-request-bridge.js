/* The lamp configurator runs in a sandboxed frame. Its quote and sample requests are passed here and sent
   through the website inquiry (inquiry.js -> Apps Script mail and sheet), with a Cloudflare check on this page.
   The frame never receives anything but the result. */
(() => {
  if (window.LTZCustomerBridgeInstalled) return;
  window.LTZCustomerBridgeInstalled = true;
  const T = s => (window.LTZ_T ? window.LTZ_T(s) : s);

  // Shows a small panel with the Cloudflare check and resolves with its token ('' if it is not used or times out).
  const captchaToken = () => {
    if (!window.LTZCaptcha) return Promise.resolve('');
    const wrap = document.createElement('div');
    wrap.className = 'lamp-captcha';
    const card = document.createElement('div');
    const title = document.createElement('strong');
    title.textContent = T('요청서를 보내기 전에 보안 확인을 합니다.');
    const box = document.createElement('div');
    box.className = 'ltz-captcha';
    card.append(title, box); wrap.append(card); document.body.append(wrap);
    const c = window.LTZCaptcha(box);
    if (!c) { wrap.remove(); return Promise.resolve(''); }
    return c.get().finally(() => setTimeout(() => wrap.remove(), 600));
  };

  const send = async p => {
    const sample = p.requestMode === 'sample';
    const lamp = p.lamp || {};
    const files = [];
    if (p.drawingSvg) files.push(new File([p.drawingSvg], 'LICHTZEN_lamp_drawing.svg', {type: 'image/svg+xml'}));
    const token = await captchaToken();
    const r = await window.LTZSendInquiry({
      source: '램프 3D 설계',
      category: sample ? 'sample' : 'spec',
      topic: sample ? '테스트 샘플 요청 (램프 3D 설계)' : '램프 견적 요청 (램프 3D 설계)',
      message: String(p.summary || JSON.stringify(p).slice(0, 6000)).slice(0, 7900),
      email: p.email, company: p.company, person: p.person,
      product: [lamp.type, lamp.overall ? lamp.overall + ' mm' : '', p.qty ? p.qty + ' pcs' : ''].filter(Boolean).join(' · '),
      files, token,
    });
    if (!r.ok) {
      const why = {captcha: '보안 확인이 끝나지 않았습니다.', rate: '잠시 후 다시 시도해 주세요.', invalid: '이메일 주소를 확인해 주세요.'}[String(r.error || '').split(':')[0]];
      throw Error(T(why || '전송하지 못했습니다. 잠시 후 다시 시도해 주세요.') + (why ? '' : ' (' + (r.error || 'test') + ')'));
    }
    return {request: {id: 'LTZ-' + String(p.clientRequestId || Date.now()).replace(/[^a-z0-9]/gi, '').slice(0, 8).toUpperCase()}};
  };

  window.addEventListener('message', async e => {
    const m = e.data;
    if (!m || m.type !== 'ltz-customer-request') return;
    const frame = [...document.querySelectorAll('iframe')].find(f => f.contentWindow === e.source);
    if (!frame || !String(frame.getAttribute('src') || '').includes('lamp-configurator')) return;
    const reply = data => e.source.postMessage({type: 'ltz-customer-request-result', id: m.id, ...data}, '*');
    try {
      if (JSON.stringify(m.payload).length > 2000000) throw Error(T('요청서가 너무 큽니다.'));
      if (!window.LTZSendInquiry) throw Error(T('전송하지 못했습니다. 잠시 후 다시 시도해 주세요.'));
      reply({result: await send(m.payload || {})});
    } catch (err) {
      reply({error: err.message || T('요청서를 처리할 수 없습니다.')});
    }
  });
})();
