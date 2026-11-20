// Short inquiry form: an optional inquiry type, the message, company and email.
(() => {
  const form = document.querySelector('.contact-form.one-stop');
  if (!form) return;
  const PLACEHOLDER = {
    lamp: '예) 램프 모델명(또는 사진), 필요한 수량, 증상이나 필요한 부품',
    system: '예) 소재, 생산 속도, 조사 폭, 설치 공간, 희망 일정',
    improve: '예) 어떤 증상이 생기는지, 사용 중인 램프·출력, 시험할 소재',
    other: '예) 궁금한 점을 편하게 적어주세요.',
  };
  // links from other pages still use the old need values
  const ALIAS = {as: 'lamp', oem: 'system', sample: 'improve'};
  const T = window.LTZ_T || (x => x);
  const msg = form.querySelector('#message');
  const select = need => { msg.placeholder = T(PLACEHOLDER[need] || PLACEHOLDER.other); };
  form.querySelectorAll('input[name=need]').forEach(r => r.addEventListener('change', () => select(r.value)));
  const params = new URLSearchParams(window.LTZ_PORTABLE_SEARCH || location.search);
  const start = ALIAS[params.get('need')] || params.get('need');
  const radio = start && form.querySelector(`input[name=need][value="${start}"]`);
  if (radio) radio.checked = true;
  select(radio ? radio.value : 'other');
  if (params.get('product')) msg.value = T('관심 제품') + ': ' + params.get('product') + '\n';

  const capBox = form.querySelector('[data-captcha]');
  const captcha = window.LTZCaptcha ? window.LTZCaptcha(capBox) : null;
  form.addEventListener('submit', e => {
    e.preventDefault();
    const status = form.querySelector('.form-status');
    const missing = [...form.querySelectorAll('[required]')].filter(el => el.type === 'checkbox' ? !el.checked : !el.value.trim());
    const email = form.querySelector('#email');
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    if (missing.length || (email.value && !email.checkValidity())) {
      (missing.length ? missing : [email]).forEach(el => el.classList.add('is-invalid'));
      status.textContent = T(missing.length ? '빨간색으로 표시된 칸을 확인해 주세요.' : '이메일 주소를 다시 확인해 주세요.');
      (missing[0] || email).focus();
      return;
    }
    const btn = form.querySelector('button[type=submit]');
    const v = id => (form.querySelector('#' + id) || {}).value || '';
    const need = form.querySelector('input[name=need]:checked');
    const fileList = [...(form.querySelector('#attachments') || {files: []}).files];
    if (fileList.length && window.LTZCheckFiles && !window.LTZCheckFiles(fileList)) { status.textContent = T('첨부할 수 없는 파일입니다. 파일당 10MB, 5개까지 보낼 수 있고 실행 파일은 보낼 수 없어요.'); return; }
    if (btn) btn.disabled = true;
    status.textContent = T('보내는 중…');
    (window.LTZSendInquiry || (async () => ({ok: false, test: true})))({
      source: '문의 페이지', category: need ? need.value : 'other', topic: need ? need.closest('label').querySelector('span').textContent : '', message: v('message'),
      email: v('email'), company: v('company'), phone: v('phone'), product: new URLSearchParams(window.LTZ_PORTABLE_SEARCH || location.search).get('product') || '', files: fileList, captcha,
    }).then(r => {
      if (btn) btn.disabled = false;
      status.textContent = '';
      if (!r.ok && !r.test) { status.textContent = T('전송하지 못했습니다. 잠시 후 다시 시도하시거나 아래로 연락해 주세요.') + ' itl@lichtzen.com · +82-70-4088-6117' + (r.error ? ' (code: ' + r.error + ')' : ''); return; }
      const done = form.querySelector('.contact-done');
      if (r.ok) done.querySelector('p').textContent = T('담당자가 확인한 뒤 입력하신 이메일로 답변드리겠습니다.');
      form.querySelectorAll('fieldset').forEach(f => { f.hidden = true; });
      done.hidden = false; done.setAttribute('tabindex', '-1'); done.focus();
    });
  });
})();
