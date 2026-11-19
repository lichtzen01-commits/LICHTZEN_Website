/**
 * LICHTZEN 홈페이지 문의 수신 (Google Apps Script 웹 앱)
 * 홈페이지 채팅·문의 페이지가 보낸 내용을 회사 메일로 정리해 보내고, 고객에게 접수 확인 메일을 보냅니다.
 * 설정 방법: docs/INQUIRY_SETUP.md
 */
const CONFIG = {
  TO: 'ltz@lichtzen.com',          // 문의를 받을 주소 (여러 개면 쉼표로)
  SEND_RECEIPT: true,              // 고객에게 접수 확인 메일 (고객 언어로)
  DRIVE_FOLDER_ID: '',             // 첨부 파일을 드라이브에도 보관하려면 폴더 ID
  MAX_FILES: 3,
  MAX_FILE_MB: 5,
  ALLOWED_EXT: ['pdf', 'jpg', 'jpeg', 'png', 'webp'],
  MAX_PER_HOUR: 40,                // 전체 시간당 최대 접수 (스팸 방지)
  MAX_PER_EMAIL_HOUR: 5,           // 같은 이메일 시간당 최대 접수
};

const LANG_NAME = {ko: '한국어', en: '영어', zh: '중국어', ja: '일본어', es: '스페인어', hi: '힌디어'};

const RECEIPT = {
  ko: ['[리트젠] 문의가 접수되었습니다', '문의해 주셔서 감사합니다.\n담당자가 내용을 확인한 뒤 이 메일 주소로 답변드리겠습니다.\n\n문의 분야: {topic}\n\n리트젠(LICHTZEN) · 031-419-6700 · ltz@lichtzen.com'],
  en: ['[LICHTZEN] We have received your inquiry', 'Thank you for contacting LICHTZEN.\nOur team will review your inquiry and reply to this email address.\n\nTopic: {topic}\n\nLICHTZEN Co., Ltd. · +82-31-419-6700 · ltz@lichtzen.com'],
  zh: ['[LICHTZEN] 我们已收到您的咨询', '感谢您联系LICHTZEN。\n负责人确认内容后将通过此邮箱回复您。\n\n咨询领域：{topic}\n\nLICHTZEN Co., Ltd. · +82-31-419-6700 · ltz@lichtzen.com'],
  ja: ['[LICHTZEN] お問い合わせを受け付けました', 'LICHTZENへお問い合わせいただきありがとうございます。\n担当者が内容を確認のうえ、このメールアドレスにご返信いたします。\n\nお問い合わせ分野：{topic}\n\nLICHTZEN Co., Ltd. · +82-31-419-6700 · ltz@lichtzen.com'],
  es: ['[LICHTZEN] Hemos recibido su consulta', 'Gracias por contactar con LICHTZEN.\nNuestro equipo revisará su consulta y le responderá a esta dirección de correo.\n\nTema: {topic}\n\nLICHTZEN Co., Ltd. · +82-31-419-6700 · ltz@lichtzen.com'],
  hi: ['[LICHTZEN] आपकी पूछताछ प्राप्त हो गई है', 'LICHTZEN से संपर्क करने के लिए धन्यवाद।\nहमारी टीम आपकी पूछताछ देखकर इसी ईमेल पते पर जवाब देगी।\n\nविषय: {topic}\n\nLICHTZEN Co., Ltd. · +82-31-419-6700 · ltz@lichtzen.com'],
};

function doGet() { return json({ok: true, service: 'lichtzen-inquiry'}); }

function doPost(e) {
  try {
    const d = JSON.parse(e.postData.contents || '{}');
    if (d.bot) return json({ok: true});                                  // honeypot
    const email = String(d.email || '').trim();
    const message = String(d.message || '').trim().slice(0, 8000);
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || !message) return json({ok: false, error: 'invalid'});
    if (!allow_(email)) return json({ok: false, error: 'rate'});

    const lang = RECEIPT[d.lang] ? d.lang : (d.lang ? 'en' : 'ko');
    const files = (d.files || []).slice(0, CONFIG.MAX_FILES).map(toBlob_).filter(Boolean);
    let links = [];
    if (CONFIG.DRIVE_FOLDER_ID && files.length) {
      const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
      links = files.map(b => folder.createFile(b.copyBlob()).getUrl());
    }
    let translated = '';
    if (lang !== 'ko' || !/[가-힣]/.test(message)) {
      try { translated = LanguageApp.translate(message, '', 'ko'); } catch (err) { translated = ''; }
    }
    const who = d.who || [d.company, d.person].filter(Boolean).join(' / ');
    const rows = [
      ['문의 경로', d.source], ['문의 분야', d.topic], ['회사·담당자', who], ['이메일', email], ['연락처', d.phone],
      ['관심 제품·모델', d.product], ['고객 언어', (LANG_NAME[d.lang] || d.lang || '한국어') + (d.browserLang ? ' (브라우저 ' + d.browserLang + ')' : '')],
      ['보낸 페이지', d.page], ['접수 시각', Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm') + ' KST'],
    ].filter(r => r[1]);
    const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
    const block = (title, text) => '<h3 style="margin:20px 0 6px;font-size:15px">' + title + '</h3><div style="white-space:pre-wrap;padding:12px;background:#f4f6f2;border-radius:8px">' + esc(text) + '</div>';
    let html = '<div style="font-family:sans-serif;font-size:14px;color:#17201e">'
      + (lang !== 'ko' ? '<p style="padding:10px 12px;background:#fff6db;border-radius:8px"><b>해외 문의</b> · ' + esc(LANG_NAME[d.lang] || d.lang) + '로 답변해 주세요. 답장하면 고객에게 바로 갑니다.</p>' : '')
      + '<table style="border-collapse:collapse">' + rows.map(r => '<tr><th style="text-align:left;padding:4px 14px 4px 0;color:#5b6660;vertical-align:top">' + esc(r[0]) + '</th><td style="padding:4px 0">' + esc(r[1]) + '</td></tr>').join('') + '</table>'
      + block('문의 내용', message)
      + (translated && translated !== message ? block('한국어 번역 (자동 번역, 참고용)', translated) : '')
      + (files.length ? '<p style="margin-top:16px">첨부 파일 ' + files.length + '개' + (links.length ? ': ' + links.map((u, i) => '<a href="' + u + '">' + esc(files[i].getName()) + '</a>').join(', ') : ' (메일에 첨부)') + '</p>' : '')
      + '</div>';
    MailApp.sendEmail({
      to: CONFIG.TO, replyTo: email, name: 'LICHTZEN 홈페이지',
      subject: '[홈페이지 문의]' + (lang !== 'ko' ? '[' + (LANG_NAME[d.lang] || d.lang) + ']' : '') + ' ' + (d.topic || '일반 문의') + ' · ' + (who || email),
      htmlBody: html, attachments: files,
    });
    if (CONFIG.SEND_RECEIPT) {
      const t = RECEIPT[lang];
      MailApp.sendEmail({to: email, replyTo: CONFIG.TO.split(',')[0], name: 'LICHTZEN', subject: t[0], body: t[1].replace('{topic}', String(d.topic || '-').slice(0, 80))});
    }
    return json({ok: true});
  } catch (err) {
    console.error(err);
    return json({ok: false, error: 'server'});
  }
}

function toBlob_(f) {
  if (!f || !f.name || !f.data) return null;
  const ext = String(f.name).split('.').pop().toLowerCase();
  if (CONFIG.ALLOWED_EXT.indexOf(ext) < 0) return null;
  const bytes = Utilities.base64Decode(f.data);
  if (bytes.length > CONFIG.MAX_FILE_MB * 1024 * 1024) return null;
  return Utilities.newBlob(bytes, f.type || 'application/octet-stream', String(f.name).slice(0, 120));
}

function allow_(email) {
  const c = CacheService.getScriptCache();
  const hour = Utilities.formatDate(new Date(), 'UTC', 'yyyyMMddHH');
  const bump = (k, max) => { const n = Number(c.get(k) || 0) + 1; if (n > max) return false; c.put(k, String(n), 3600); return true; };
  return bump('all:' + hour, CONFIG.MAX_PER_HOUR) && bump('em:' + email.toLowerCase() + ':' + hour, CONFIG.MAX_PER_EMAIL_HOUR);
}

function json(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

/** 편집기에서 한 번 실행해 권한을 승인하고, 받는 주소로 시험 메일이 오는지 확인합니다. */
function testSend() {
  const r = doPost({postData: {contents: JSON.stringify({source: '시험', topic: 'UV / IR lamps', message: 'Please quote 10 metal halide lamps, 1200 mm.', email: CONFIG.TO.split(',')[0], who: 'Test Co.', lang: 'en', browserLang: 'en-US', page: 'test'})}});
  console.log(r.getContent());
}
