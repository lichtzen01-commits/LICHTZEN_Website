// One-stop inquiry: pick a need, tap pain points, then three required fields.
(() => {
  const form = document.querySelector('.contact-form.one-stop');
  if (!form) return;
  const PAIN = {
    lamp: ['단종된 램프를 대체하고 싶어요', '수입 램프가 너무 비싸요', '납기가 급해요', '소량(1~10개)만 필요해요', '램프 수명이 짧아요', '모델명을 몰라 사진만 있어요'],
    system: ['새 라인에 경화기가 필요해요', '생산 속도를 높이고 싶어요', '수은 램프를 LED로 바꾸고 싶어요', '설치 공간이 좁아요', '컨베이어까지 한 번에 맡기고 싶어요', '예산 범위를 먼저 알고 싶어요'],
    improve: ['덜 굳어요(경화 불량)', '열 때문에 소재가 변형돼요', '얼룩·색 변화가 생겨요', '조도가 고르지 않아요', '전기료·발열을 줄이고 싶어요', '원인을 모르겠어요'],
    sample: ['우리 소재로 시험해 보고 싶어요', 'UV LED와 램프를 비교하고 싶어요', '조건(파장·광량)을 찾고 싶어요', '시험 성적이 필요해요'],
    oem: ['자체 브랜드로 공급받고 싶어요', '정기적으로 대량 구매할 예정이에요', '사양을 맞춤으로 바꾸고 싶어요', '표기·포장 조건이 있어요'],
    as: ['장비가 작동하지 않아요', '램프가 자주 꺼져요', '부품 교체가 필요해요', '정기 점검을 받고 싶어요'],
    other: ['무엇부터 물어볼지 모르겠어요', '회사소개서를 받고 싶어요', '견적만 빠르게 받고 싶어요', '방문 상담을 원해요'],
  };
  const PLACEHOLDER = {
    lamp: '예) 현재 램프 모델명(또는 사진), 전체 길이·발광장, 필요한 수량, 희망 납기',
    system: '예) 소재, 생산 속도, 조사 폭, 설치 공간, 희망 일정',
    improve: '예) 어떤 증상이 언제부터 생겼는지, 사용 중인 램프·출력, 소재와 속도',
    sample: '예) 시험할 소재와 코팅(잉크·접착제) 종류, 원하는 결과',
    oem: '예) 대상 품목, 예상 수량, 요청 사양, 표기·포장 조건, 희망 일정',
    as: '예) 장비 모델·구입 시기, 증상, 사진',
    other: '예) 궁금한 점을 편하게 적어주세요.',
  };
  const chips = form.querySelector('[data-pain-chips]');
  const msg = form.querySelector('#message');
  const select = need => {
    chips.innerHTML = '';
    (PAIN[need] || PAIN.other).forEach(text => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'pain-chip'; b.textContent = text; b.setAttribute('aria-pressed', 'false');
      b.addEventListener('click', () => {
        const on = b.getAttribute('aria-pressed') !== 'true';
        b.setAttribute('aria-pressed', String(on));
        const lines = msg.value.split('\n').filter(l => l.trim() && l.trim() !== '· ' + text);
        if (on) lines.unshift('· ' + text);
        msg.value = lines.join('\n') + (lines.length ? '\n' : '');
        msg.focus();
      });
      chips.appendChild(b);
    });
    msg.placeholder = PLACEHOLDER[need] || PLACEHOLDER.other;
  };
  form.querySelectorAll('input[name=need]').forEach(r => r.addEventListener('change', () => select(r.value)));
  const params = new URLSearchParams(window.LTZ_PORTABLE_SEARCH || location.search);
  const start = params.get('need');
  const radio = form.querySelector(`input[name=need][value="${start}"]`) || form.querySelector('input[name=need][value=other]');
  if (start && radio) radio.checked = true;
  select(radio ? radio.value : 'other');
  if (params.get('product')) form.querySelector('#product').value = params.get('product');

  form.addEventListener('submit', e => {
    e.preventDefault();
    const status = form.querySelector('.form-status');
    const missing = [...form.querySelectorAll('[required]')].filter(el => el.type === 'checkbox' ? !el.checked : !el.value.trim());
    const email = form.querySelector('#email');
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    if (missing.length || (email.value && !email.checkValidity())) {
      (missing.length ? missing : [email]).forEach(el => el.classList.add('is-invalid'));
      status.textContent = missing.length ? '빨간색으로 표시된 칸을 확인해 주세요.' : '이메일 주소를 다시 확인해 주세요.';
      (missing[0] || email).focus();
      return;
    }
    form.querySelectorAll('fieldset').forEach(f => { f.hidden = true; });
    const done = form.querySelector('.contact-done');
    done.hidden = false; done.setAttribute('tabindex', '-1'); done.focus();
  });
})();
