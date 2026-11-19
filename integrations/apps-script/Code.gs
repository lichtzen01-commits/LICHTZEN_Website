/**
 * LICHTZEN 홈페이지 문의 수신 (Google Apps Script 웹 앱)
 * 홈페이지 채팅·문의 페이지가 보낸 문의를
 *  1) 구글 스프레드시트 '문의 목록'에 한 줄씩 누적하고 (첨부 파일은 드라이브 폴더에 보관, 시트에 링크)
 *  2) 회사 메일로 보내면서 지금까지의 누적 목록을 엑셀(.xlsx)로 첨부하고
 *  3) 고객에게 고객 언어로 접수 확인 메일을 보냅니다.
 * 설정 방법: docs/INQUIRY_SETUP.md
 */
const CONFIG = {
  TO: 'itl@lichtzen.com', // 모든 문의를 받을 주소. 여러 개면 쉼표로. 비워 두면 이 스크립트를 만든 계정의 Gmail로 받습니다.
  SEND_RECEIPT: true,    // 고객에게 접수 확인 메일 (고객 언어로)
  SHEET_ID: '',          // 문의 목록 스프레드시트 ID. 비워 두면 처음 문의 때 자동으로 만듭니다.
  DRIVE_FOLDER_ID: '',   // 첨부 파일 보관 폴더 ID. 비워 두면 자동으로 만듭니다.
  ATTACH_XLSX: true,     // 회사 메일에 누적 문의 목록(엑셀) 첨부
  MAX_FILES: 5,
  MAX_FILE_MB: 10,
  BLOCKED_EXT: ['exe', 'msi', 'bat', 'cmd', 'com', 'scr', 'pif', 'cpl', 'dll', 'js', 'jse', 'vbs', 'vbe', 'wsf', 'wsh', 'ps1', 'sh', 'jar', 'apk', 'app', 'lnk', 'reg', 'hta'],
  MAX_PER_HOUR: 40,      // 전체 시간당 최대 접수 (스팸 방지)
  MAX_PER_EMAIL_HOUR: 5, // 같은 이메일 시간당 최대 접수
};

const RECEIPT = {
  ko: ['[리트젠] 문의가 접수되었습니다', '문의해 주셔서 감사합니다.\n담당자가 내용을 확인한 뒤 이 메일 주소로 답변드리겠습니다.\n\n문의 분야: {topic}\n\n리트젠(LICHTZEN) · 070-4088-6117 · itl@lichtzen.com'],
  en: ['[LICHTZEN] We have received your inquiry', 'Thank you for contacting LICHTZEN.\nOur team will review your inquiry and reply to this email address.\n\nTopic: {topic}\n\nLICHTZEN Co., Ltd. · +82-70-4088-6117 · itl@lichtzen.com'],
  zh: ['[LICHTZEN] 我们已收到您的咨询', '感谢您联系LICHTZEN。\n负责人确认内容后将通过此邮箱回复您。\n\n咨询领域：{topic}\n\nLICHTZEN Co., Ltd. · +82-70-4088-6117 · itl@lichtzen.com'],
  ja: ['[LICHTZEN] お問い合わせを受け付けました', 'LICHTZENへお問い合わせいただきありがとうございます。\n担当者が内容を確認のうえ、このメールアドレスにご返信いたします。\n\nお問い合わせ分野：{topic}\n\nLICHTZEN Co., Ltd. · +82-70-4088-6117 · itl@lichtzen.com'],
  es: ['[LICHTZEN] Hemos recibido su consulta', 'Gracias por contactar con LICHTZEN.\nNuestro equipo revisará su consulta y le responderá a esta dirección de correo.\n\nTema: {topic}\n\nLICHTZEN Co., Ltd. · +82-70-4088-6117 · itl@lichtzen.com'],
  hi: ['[LICHTZEN] आपकी पूछताछ प्राप्त हो गई है', 'LICHTZEN से संपर्क करने के लिए धन्यवाद।\nहमारी टीम आपकी पूछताछ देखकर इसी ईमेल पते पर जवाब देगी।\n\nविषय: {topic}\n\nLICHTZEN Co., Ltd. · +82-70-4088-6117 · itl@lichtzen.com'],
};

const HEADERS = ['접수번호', '접수 시각', '상태', '문의 경로', '문의 분야', '회사·담당자', '이메일', '연락처', '관심 제품·모델', '고객 언어', '문의 내용', '첨부 파일', '보낸 페이지', '담당자', '메모'];
const STATUS = ['접수', '진행 중', '견적 발송', '완료', '보류'];
const LANG_NAME = {ko: '한국어', en: '영어', zh: '중국어', ja: '일본어', es: '스페인어', hi: '힌디어'};

function doGet() { return json({ok: true, service: 'lichtzen-inquiry'}); }

function doPost(e) {
  try {
    const d = JSON.parse(e.postData.contents || '{}');
    if (d.bot) return json({ok: true});                                  // 스팸 함정 칸
    const email = String(d.email || '').trim();
    const message = String(d.message || '').trim().slice(0, 8000);
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || !message) return json({ok: false, error: 'invalid'});
    if (!allow_(email)) return json({ok: false, error: 'rate'});

    const lock = LockService.getScriptLock(); lock.waitLock(20000);      // 동시에 들어온 문의가 같은 줄을 쓰지 않게
    try {
      const to = CONFIG.TO || Session.getEffectiveUser().getEmail();
      const now = new Date();
      const stamp = Utilities.formatDate(now, 'Asia/Seoul', 'yyyy-MM-dd HH:mm');
      const files = (d.files || []).slice(0, CONFIG.MAX_FILES).map(toBlob_).filter(Boolean);
      const folder = folder_();
      const links = files.map(b => folder.createFile(b.copyBlob()).getUrl());
      const who = d.who || [d.company, d.person].filter(Boolean).join(' / ');

      // 1) 문의 목록에 한 줄 추가
      const sheet = sheet_();
      const no = Utilities.formatDate(now, 'Asia/Seoul', 'yyyy') + '-' + ('000' + sheet.getLastRow()).slice(-4);
      sheet.appendRow([no, stamp, STATUS[0], d.source || '', d.topic || '', who, email, d.phone || '', d.product || '',
        LANG_NAME[d.lang] || d.lang || '한국어', message, links.join('\n'), d.page || '', '', '']);
      SpreadsheetApp.flush();
      const total = sheet.getLastRow() - 1;

      // 2) 회사 메일 (+ 누적 목록 엑셀)
      const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
      const info = [['접수번호', no], ['문의 분야', d.topic], ['회사·담당자', who], ['이메일', email], ['연락처', d.phone], ['관심 제품·모델', d.product],
        ['첨부 파일', files.length ? files.map(b => b.getName()).join(', ') : '']].filter(r => r[1]);
      const html = '<div style="font-family:sans-serif;font-size:14px;color:#17201e">'
        + '<div style="white-space:pre-wrap;line-height:1.7">' + esc(message) + '</div>'
        + '<hr style="border:0;border-top:1px solid #e1e6e1;margin:20px 0">'
        + '<table style="border-collapse:collapse;font-size:13px;color:#3d4a43">'
        + info.map(r => '<tr><th style="text-align:left;padding:2px 14px 2px 0;font-weight:600;vertical-align:top">' + esc(r[0]) + '</th><td>' + esc(r[1]) + '</td></tr>').join('')
        + '</table>'
        + '<p style="font-size:13px;color:#5b6670;margin-top:16px">누적 문의 ' + total + '건 · <a href="' + sheet.getParent().getUrl() + '">문의 목록 시트 열기</a>'
        + (CONFIG.ATTACH_XLSX ? ' · 전체 목록 엑셀 첨부' : '') + '</p></div>';
      const attachments = files.slice();
      if (CONFIG.ATTACH_XLSX) { try { attachments.push(xlsx_(sheet.getParent(), now)); } catch (err) { console.error('xlsx', err); } }
      MailApp.sendEmail({
        to: to, replyTo: email, name: 'LICHTZEN 홈페이지',
        subject: '[홈페이지 문의] ' + (d.topic || '일반 문의') + ' · ' + (who || email),
        htmlBody: html, attachments: attachments,
      });

      // 3) 고객 접수 확인 메일
      if (CONFIG.SEND_RECEIPT) {
        const t = RECEIPT[d.lang] || RECEIPT[d.lang ? 'en' : 'ko'];
        MailApp.sendEmail({to: email, replyTo: to.split(',')[0], name: 'LICHTZEN', subject: t[0], body: t[1].replace('{topic}', String(d.topic || '-').slice(0, 80))});
      }
    } finally { lock.releaseLock(); }
    return json({ok: true});
  } catch (err) {
    console.error(err);
    return json({ok: false, error: 'server'});
  }
}

/** 문의 목록 시트: 없으면 만들고(머리줄·상태 목록·줄 고정), ID는 스크립트 속성에 기억합니다. */
function sheet_() {
  const props = PropertiesService.getScriptProperties();
  const id = CONFIG.SHEET_ID || props.getProperty('SHEET_ID');
  let ss = null;
  if (id) { try { ss = SpreadsheetApp.openById(id); } catch (err) { ss = null; } }
  if (!ss) {
    ss = SpreadsheetApp.create('LICHTZEN 홈페이지 문의 목록');
    props.setProperty('SHEET_ID', ss.getId());
  }
  let sh = ss.getSheetByName('문의 목록');
  if (!sh) {
    sh = ss.getSheets()[0]; sh.setName('문의 목록');
    sh.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]).setFontWeight('bold').setBackground('#1b2a36').setFontColor('#ffffff');
    sh.setFrozenRows(1);
    sh.setColumnWidths(1, HEADERS.length, 120); sh.setColumnWidth(11, 420); sh.setColumnWidth(12, 260);
    sh.getRange('C2:C').setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(STATUS, true).build());
    sh.getRange('K2:L').setWrap(true);
  }
  return sh;
}

/** 첨부 파일 보관 폴더: 없으면 만듭니다. */
function folder_() {
  const props = PropertiesService.getScriptProperties();
  const id = CONFIG.DRIVE_FOLDER_ID || props.getProperty('FOLDER_ID');
  if (id) { try { return DriveApp.getFolderById(id); } catch (err) {} }
  const f = DriveApp.createFolder('LICHTZEN 홈페이지 문의 첨부');
  props.setProperty('FOLDER_ID', f.getId());
  return f;
}

/** 스프레드시트 전체를 엑셀(.xlsx)로 내보냅니다. */
function xlsx_(ss, now) {
  const url = 'https://docs.google.com/spreadsheets/d/' + ss.getId() + '/export?format=xlsx';
  const res = UrlFetchApp.fetch(url, {headers: {Authorization: 'Bearer ' + ScriptApp.getOAuthToken()}, muteHttpExceptions: true});
  if (res.getResponseCode() !== 200) throw new Error('export ' + res.getResponseCode());
  return res.getBlob().setName('LICHTZEN_문의목록_' + Utilities.formatDate(now, 'Asia/Seoul', 'yyyyMMdd_HHmm') + '.xlsx');
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

/** 편집기에서 한 번 실행: 권한 승인 → 시트·폴더 자동 생성 → 시험 메일 2통(문의 + 접수 확인). 실행 로그에 시트 주소가 나옵니다. */
function testSend() {
  const me = Session.getEffectiveUser().getEmail();
  const r = doPost({postData: {contents: JSON.stringify({
    source: '시험', topic: 'UV / IR 램프 문의', message: '메탈할라이드 램프 1200mm 10개 견적 부탁드립니다.\n납기도 알려주세요.',
    email: me, who: '시험 회사 / 홍길동', lang: 'ko',
    files: [{name: 'test.txt', type: 'text/plain', data: Utilities.base64Encode('LICHTZEN test attachment')}],
  })}});
  console.log(r.getContent());
  console.log('문의 목록 시트: ' + sheet_().getParent().getUrl());
}
