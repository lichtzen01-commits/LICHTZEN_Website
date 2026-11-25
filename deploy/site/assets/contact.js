// Inquiry wizard: 1) what do you need  2) photos/drawings and details  3) where to reply.
// The fields keep their names, so sending (inquiry.js → Apps Script) is unchanged.
(() => {
  const form = document.querySelector('.contact-form.one-stop');
  if (!form) return;
  const T = window.LTZ_T || (x => x);
  const NEED = {
    lamp: {title: '램프 사진이나 모델명을 알려주세요', photo: true, hint: ['램프 모델명', '수량', '사용 중인 장비', '증상'], ph: '예) 램프 모델명(또는 사진), 필요한 수량, 증상이나 필요한 부품'},
    system: {title: '공정 조건을 알려주세요', photo: false, hint: ['소재', '생산 속도', '조사 폭', '설치 공간', '희망 일정'], ph: '예) 소재, 생산 속도, 조사 폭, 설치 공간, 희망 일정'},
    improve: {title: '어떤 증상인지 보여주세요', photo: true, hint: ['증상', '사용 중인 램프·출력', '소재', '라인 속도'], ph: '예) 어떤 증상이 생기는지, 사용 중인 램프·출력, 시험할 소재'},
    sample: {title: '테스트할 소재를 알려주세요', photo: true, hint: ['소재', '잉크·코팅제', '원하는 결과', '수량'], ph: '예) 소재와 잉크·코팅제, 원하는 경화 결과, 샘플 수량'},
    docs: {title: '필요한 자료를 알려주세요', photo: false, hint: ['제품명', '카탈로그', '사양서', '도면'], ph: '예) 필요한 제품과 자료 종류(카탈로그, 사양서, 도면)'},
    other: {title: '자세히 알려주세요', photo: false, hint: [], ph: '예) 궁금한 점을 편하게 적어주세요.'},
  };
  const ALIAS = {as: 'lamp', oem: 'system'};
  const steps = [...form.querySelectorAll('.wz-step')];
  const back = form.querySelector('.wz-back'), next = form.querySelector('.wz-next'), submit = form.querySelector('.wz-submit');
  const status = form.querySelector('.form-status');
  const msg = form.querySelector('#message'), files = form.querySelector('#attachments');
  const drop = form.querySelector('.dropzone'), hints = form.querySelector('.wz-hints');
  let cur = 0;
  const need = () => (form.querySelector('input[name=need]:checked') || {}).value || 'other';
  const hasFiles = () => files && files.files.length > 0;

  const setNeed = () => {
    const n = NEED[need()];
    form.dataset.need = need();
    form.classList.toggle('photo-first', !!n.photo);
    form.querySelector('[data-step2-title]').textContent = T(n.title);
    msg.placeholder = T(n.ph);
    hints.replaceChildren(...n.hint.map(h => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'wz-hint'; b.textContent = '+ ' + T(h);
      b.addEventListener('click', () => { const line = T(h) + ': '; msg.value = (msg.value && !msg.value.endsWith('\n') ? msg.value + '\n' : msg.value) + line; msg.focus(); msg.setSelectionRange(msg.value.length, msg.value.length); b.disabled = true; });
      return b;
    }));
  };
  const show = i => {
    cur = i;
    steps.forEach((s, k) => { s.hidden = k !== i; });
    back.hidden = i === 0;
    next.hidden = i === steps.length - 1;
    submit.hidden = i !== steps.length - 1;
    form.querySelector('.wz-count b').textContent = i + 1;
    form.querySelector('.wz-bar i').style.width = ((i + 1) / steps.length * 100) + '%';
    status.textContent = '';
    const first = steps[i].querySelector('legend');
    if (first) { first.setAttribute('tabindex', '-1'); first.focus({preventScroll: true}); }
    const top = form.getBoundingClientRect().top + scrollY - 110;
    if (scrollY > top) scrollTo({top, behavior: 'smooth'});
  };
  const valid = i => {
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    if (i === 1) {
      msg.required = !hasFiles();
      if (msg.required && !msg.value.trim()) { msg.classList.add('is-invalid'); status.textContent = T('내용을 적거나 사진·도면을 올려 주세요.'); msg.focus(); return false; }
    }
    return true;
  };
  next.addEventListener('click', () => { if (valid(cur)) { if (cur === 0) setNeed(); show(cur + 1); } });
  back.addEventListener('click', () => show(cur - 1));
  form.querySelectorAll('input[name=need]').forEach(r => r.addEventListener('change', () => { setNeed(); setTimeout(() => show(1), 220); }));

  // drag and drop onto the photo area
  if (drop && files) {
    ['dragenter', 'dragover'].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.add('is-over'); }));
    ['dragleave', 'drop'].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.remove('is-over'); }));
    drop.addEventListener('drop', e => {
      if (!e.dataTransfer || !e.dataTransfer.files.length) return;
      const dt = new DataTransfer();
      [...files.files, ...e.dataTransfer.files].slice(0, 5).forEach(f => dt.items.add(f));
      files.files = dt.files;
      files.dispatchEvent(new Event('change', {bubbles: true}));
    });
    files.addEventListener('change', () => { drop.classList.toggle('has-files', hasFiles()); form.querySelector('[data-msg-req]').textContent = T(hasFiles() ? '선택' : '필수'); });
  }

  // arriving from a product or service link
  const params = new URLSearchParams(window.LTZ_PORTABLE_SEARCH || location.search);
  const start = ALIAS[params.get('need')] || params.get('need');
  const product = params.get('product');
  const radio = form.querySelector(`input[name=need][value="${start || (product ? 'system' : '')}"]`);
  if (radio) radio.checked = true;
  setNeed();
  if (product) msg.value = T('관심 제품') + ': ' + product + '\n';
  show(radio ? 1 : 0);

  const capBox = form.querySelector('[data-captcha]');
  const captcha = window.LTZCaptcha ? window.LTZCaptcha(capBox) : null;
  form.addEventListener('submit', e => {
    e.preventDefault();
    if (cur !== steps.length - 1) { next.click(); return; }
    msg.required = false;
    const missing = [...steps[cur].querySelectorAll('[required]')].filter(el => el.type === 'checkbox' ? !el.checked : !el.value.trim());
    const email = form.querySelector('#email');
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    if (missing.length || (email.value && !email.checkValidity())) {
      (missing.length ? missing : [email]).forEach(el => el.classList.add('is-invalid'));
      status.textContent = T(missing.length ? '빨간색으로 표시된 칸을 확인해 주세요.' : '이메일 주소를 다시 확인해 주세요.');
      (missing[0] || email).focus();
      return;
    }
    const v = id => (form.querySelector('#' + id) || {}).value || '';
    const picked = form.querySelector('input[name=need]:checked');
    const fileList = [...(files || {files: []}).files];
    if (fileList.length && window.LTZCheckFiles && !window.LTZCheckFiles(fileList)) { status.textContent = T('첨부할 수 없는 파일입니다. 파일당 10MB, 5개까지 보낼 수 있고 실행 파일은 보낼 수 없어요.'); return; }
    submit.disabled = true;
    status.textContent = T('보내는 중…');
    (window.LTZSendInquiry || (async () => ({ok: false, test: true})))({
      source: '문의 페이지', category: need() === 'docs' ? 'spec' : need(), topic: picked ? picked.closest('label').querySelector('strong').textContent : '',
      message: v('message') || T('(첨부 파일 참고)'), email: v('email'), company: v('company'), phone: v('phone'),
      product: product || '', files: fileList, captcha,
    }).then(r => {
      submit.disabled = false;
      status.textContent = '';
      if (!r.ok && !r.test) { status.textContent = T('전송하지 못했습니다. 잠시 후 다시 시도하시거나 아래로 연락해 주세요.') + ' itl@lichtzen.com · +82-70-4088-6117' + (r.error ? ' (code: ' + r.error + ')' : ''); return; }
      const done = form.querySelector('.contact-done');
      if (r.ok) done.querySelector('p').textContent = T('담당자가 확인한 뒤 입력하신 이메일로 답변드리겠습니다.');
      steps.forEach(f => { f.hidden = true; });
      form.querySelector('.wz-nav').hidden = true;
      form.querySelector('.wz-progress').hidden = true;
      done.hidden = false; done.setAttribute('tabindex', '-1'); done.focus();
    });
  });
})();
