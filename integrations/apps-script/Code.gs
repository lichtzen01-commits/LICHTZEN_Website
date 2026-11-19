/**
 * LICHTZEN 홈페이지 문의 수신 (Google Apps Script 웹 앱)
 * 홈페이지 채팅·문의 페이지가 보낸 문의를 메일로 보내고, 고객에게 고객 언어로 접수 확인 메일을 보냅니다.
 * 설정 방법: docs/INQUIRY_SETUP.md
 */
const CONFIG = {
  TO: '',                // 문의를 받을 주소. 비워 두면 이 스크립트를 만든 계정의 Gmail로 받습니다(테스트용).
                         // 회사 운영 시 'ltz@lichtzen.com' 처럼 넣습니다. 여러 개면 쉼표로.
  SEND_RECEIPT: true,    // 고객에게 접수 확인 메일 (고객 언어로)
  DRIVE_FOLDER_ID: '',   // 첨부 파일을 드라이브에도 보관하려면 폴더 ID
  MAX_FILES: 5,
  MAX_FILE_MB: 10,
  BLOCKED_EXT: ['exe', 'msi', 'bat', 'cmd', 'com', 'scr', 'pif', 'cpl', 'dll', 'js', 'jse', 'vbs', 'vbe', 'wsf', 'wsh', 'ps1', 'sh', 'jar', 'apk', 'app', 'lnk', 'reg', 'hta'],
  MAX_PER_HOUR: 40,      // 전체 시간당 최대 접수 (스팸 방지)
  MAX_PER_EMAIL_HOUR: 5, // 같은 이메일 시간당 최대 접수
};

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
    if (d.bot) return json({ok: true});                                  // 스팸 함정 칸
    const email = String(d.email || '').trim();
    const message = String(d.message || '').trim().slice(0, 8000);
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || !message) return json({ok: false, error: 'invalid'});
    if (!allow_(email)) return json({ok: false, error: 'rate'});

    const to = CONFIG.TO || Session.getEffectiveUser().getEmail();
    const files = (d.files || []).slice(0, CONFIG.MAX_FILES).map(toBlob_).filter(Boolean);
    let links = [];
    if (CONFIG.DRIVE_FOLDER_ID && files.length) {
      const folder = DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
      links = files.map(b => folder.createFile(b.copyBlob()).getUrl());
    }
    const who = d.who || [d.company, d.person].filter(Boolean).join(' / ');
    const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
    const info = [['문의 분야', d.topic], ['회사·담당자', who], ['이메일', email], ['연락처', d.phone], ['관심 제품·모델', d.product],
      ['첨부 파일', files.length ? files.map(b => b.getName()).join(', ') : '']].filter(r => r[1]);
    const html = '<div style="font-family:sans-serif;font-size:14px;color:#17201e">'
      + '<div style="white-space:pre-wrap;line-height:1.7">' + esc(message) + '</div>'
      + '<hr style="border:0;border-top:1px solid #e1e6e1;margin:20px 0">'
      + '<table style="border-collapse:collapse;font-size:13px;color:#3d4a43">'
      + info.map(r => '<tr><th style="text-align:left;padding:2px 14px 2px 0;font-weight:600;vertical-align:top">' + esc(r[0]) + '</th><td>' + esc(r[1]) + '</td></tr>').join('')
      + '</table>'
      + (links.length ? '<p style="font-size:13px">드라이브 보관: ' + links.map((u, i) => '<a href="' + u + '">' + esc(files[i].getName()) + '</a>').join(', ') + '</p>' : '')
      + '</div>';
    MailApp.sendEmail({
      to: to, replyTo: email, name: 'LICHTZEN 홈페이지',
      subject: '[홈페이지 문의] ' + (d.topic || '일반 문의') + ' · ' + (who || email),
      htmlBody: html, attachments: files,
    });
    if (CONFIG.SEND_RECEIPT) {
      const t = RECEIPT[d.lang] || RECEIPT[d.lang ? 'en' : 'ko'];
      MailApp.sendEmail({to: email, replyTo: to.split(',')[0], name: 'LICHTZEN', subject: t[0], body: t[1].replace('{topic}', String(d.topic || '-').slice(0, 80))});
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
  if (CONFIG.BLOCKED_EXT.indexOf(ext) >= 0) return null;
  const bytes = Utilities.base64Decode(f.data);
  if (!bytes.length || bytes.length > CONFIG.MAX_FILE_MB * 1024 * 1024) return null;
  return Utilities.newBlob(bytes, f.type || 'application/octet-stream', String(f.name).slice(0, 120));
}

function allow_(email) {
  const c = CacheService.getScriptCache();
  const hour = Utilities.formatDate(new Date(), 'UTC', 'yyyyMMddHH');
  const bump = (k, max) => { const n = Number(c.get(k) || 0) + 1; if (n > max) return false; c.put(k, String(n), 3600); return true; };
  return bump('all:' + hour, CONFIG.MAX_PER_HOUR) && bump('em:' + email.toLowerCase() + ':' + hour, CONFIG.MAX_PER_EMAIL_HOUR);
}

function json(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

/** 편집기에서 한 번 실행해 권한을 승인하고, 시험 메일 2통(문의 + 접수 확인)이 오는지 확인합니다. */
function testSend() {
  const me = Session.getEffectiveUser().getEmail();
  const r = doPost({postData: {contents: JSON.stringify({
    source: '시험', topic: 'UV / IR 램프 문의', message: '메탈할라이드 램프 1200mm 10개 견적 부탁드립니다.\n납기도 알려주세요.',
    email: me, who: '시험 회사 / 홍길동', lang: 'ko',
    files: [{name: 'test.txt', type: 'text/plain', data: Utilities.base64Encode('LICHTZEN test attachment')}],
  })}});
  console.log(r.getContent());
}
