// Sends an inquiry to the company mailbox through Web3Forms (static site, no server of our own).
// Set ACCESS_KEY to the key Web3Forms emails to the receiving address (it is meant to be public in page code).
// While it is empty the site runs in test mode: nothing is sent and the caller shows a test notice.
(() => {
  const ACCESS_KEY = '';
  const ENDPOINT = 'https://api.web3forms.com/submit';
  const kst = () => new Date().toLocaleString('sv-SE', {timeZone: 'Asia/Seoul'}).slice(0, 16);  // 2026-11-19 09:37
  window.LTZSendInquiry = async ({source, topic, message, email, who, company, person, phone, product, files, bot}) => {
    if (bot) return {ok: true};                       // honeypot ticked: drop quietly
    if (!ACCESS_KEY) return {ok: false, test: true};
    const body = {
      access_key: ACCESS_KEY,
      subject: `[홈페이지 문의] ${topic || '일반 문의'} · ${company || who || email}`,
      from_name: 'LICHTZEN 홈페이지',
      email,                                          // Web3Forms uses this as Reply-To
      '문의 경로': source,
      '문의 분야': topic || '-',
      '문의 내용': message,
      ...(who !== undefined ? {'회사·성함': who || '-'} : {'회사명': company || '-', '담당자': person || '-'}),
      '연락처': phone || '-',
      '관심 제품·모델': product || '-',
      '첨부 파일(이름만)': files || '-',
      '보낸 페이지': location.href,
      '화면 언어': window.LTZ_LANG || 'ko',
      '접수 시각(KST)': kst(),
    };
    try {
      const r = await fetch(ENDPOINT, {method: 'POST', headers: {'Content-Type': 'application/json', Accept: 'application/json'}, body: JSON.stringify(body)});
      const j = await r.json().catch(() => ({}));
      return {ok: r.ok && j.success !== false};
    } catch (e) { return {ok: false}; }
  };
})();
