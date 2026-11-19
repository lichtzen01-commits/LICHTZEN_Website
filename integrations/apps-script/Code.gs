/**
 * LICHTZEN 홈페이지 문의 수신 (Google Apps Script 웹 앱)
 * 홈페이지 채팅·문의 페이지가 보낸 문의를
 *  1) 구글 스프레드시트에 연도별 탭(2026, 2027 …)으로 한 줄씩 누적하고 (첨부 파일은 드라이브 폴더에 보관, 시트에 링크)
 *     '통계' 탭에 연도·분류별 건수 표와 그래프를 자동으로 갱신하고
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

const HEADERS = ['접수번호', '접수 시각', '상태', '국내/해외', '문의 경로', '분류', '고객이 고른 항목', '회사·담당자', '이메일', '연락처', '관심 제품·모델', '고객 언어', '문의 내용', '첨부 파일', '보낸 페이지', '담당자', '메모'];
const STATUS = ['접수', '진행 중', '견적 발송', '완료', '보류'];
const REGIONS = ['국내', '해외'];
// 사이트가 보내는 분류 코드 -> 통계에 쓰는 분류 이름 (언어와 상관없이 같은 분류로 집계)
const CATEGORY = {lamp: '램프 교체·소량 제작', led: 'LED UV 시스템', system: '장비·라인 도입', custom: '맞춤 설비 제작', spec: '기술 사양·견적',
  improve: '경화·건조 품질 문제', sample: '샘플 테스트', oem: 'OEM 공급', as: '램프 A/S', other: '기타'};
const CATEGORY_ORDER = Object.keys(CATEGORY).map(k => CATEGORY[k]);
const LANG_NAME = {ko: '한국어', en: '영어', zh: '중국어', ja: '일본어', es: '스페인어', hi: '힌디어'};

function doGet() { return json({ok: true, service: 'lichtzen-inquiry'}); }

function doPost(e) {
  try {
    const d = JSON.parse(e.postData.contents || '{}');
    if (d.bot) return json({ok: true});                                  // 스팸 함정 칸
    const email = String(d.email || '').trim();
    const message = String(d.message || '').trim().slice(0, 8000);
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || !message) return json({ok: false, error: 'invalid'});
    if (!e.internal && !human_(d.turnstile)) return json({ok: false, error: 'captcha'});  // Cloudflare Turnstile
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
      const year = Utilities.formatDate(now, 'Asia/Seoul', 'yyyy');
      const sheet = sheet_(year);
      const no = year + '-' + ('000' + sheet.getLastRow()).slice(-4);
      const category = CATEGORY[d.category] || CATEGORY.other;
      // 국내/해외: 한국어 화면이 아니거나 +82가 아닌 국제번호면 해외. 시트에서 직원이 고칠 수 있고, 통계는 고친 값을 따릅니다.
      const phone = String(d.phone || '').replace(/\s/g, '');
      const region = (d.lang && d.lang !== 'ko') || (/^\+/.test(phone) && !/^\+82/.test(phone)) ? '해외' : '국내';
      sheet.appendRow([no, stamp, STATUS[0], region, d.source || '', category, d.topic || '', who, email, d.phone || '', d.product || '',
        LANG_NAME[d.lang] || d.lang || '한국어', message, links.join('\n'), d.page || '', '', '']);
      try { stats_(sheet.getParent()); } catch (err) { console.error('stats', err); }
      SpreadsheetApp.flush();
      const total = sheet.getLastRow() - 1;

      // 2) 회사 메일 (+ 누적 목록 엑셀)
      const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
      const info = [['접수번호', no], ['국내/해외', region], ['분류', category], ['고객이 고른 항목', d.topic], ['회사·담당자', who], ['이메일', email], ['연락처', d.phone], ['관심 제품·모델', d.product],
        ['첨부 파일', files.length ? files.map(b => b.getName()).join(', ') : '']].filter(r => r[1]);
      const html = '<div style="font-family:sans-serif;font-size:14px;color:#17201e">'
        + '<div style="white-space:pre-wrap;line-height:1.7">' + esc(message) + '</div>'
        + '<hr style="border:0;border-top:1px solid #e1e6e1;margin:20px 0">'
        + '<table style="border-collapse:collapse;font-size:13px;color:#3d4a43">'
        + info.map(r => '<tr><th style="text-align:left;padding:2px 14px 2px 0;font-weight:600;vertical-align:top">' + esc(r[0]) + '</th><td>' + esc(r[1]) + '</td></tr>').join('')
        + '</table>'
        + '<p style="font-size:13px;color:#5b6670;margin-top:16px">' + year + '년 누적 문의 ' + total + '건 · <a href="' + sheet.getParent().getUrl() + '">문의 목록 시트 열기</a>'
        + (CONFIG.ATTACH_XLSX ? ' · 전체 목록 엑셀 첨부' : '') + '</p></div>';
      const attachments = files.slice(); let xlsxNote = '';
      if (CONFIG.ATTACH_XLSX) { try { attachments.push(xlsx_(sheet.getParent(), now)); } catch (err) { console.error('xlsx', err); xlsxNote = String(err && err.message || err).slice(0, 160); } }
      const body = xlsxNote ? html.replace('</div>', '') + '<p style="font-size:12px;color:#b42318">엑셀 첨부 실패: ' + esc(xlsxNote) + ' (Apps Script에서 testSend를 실행해 권한을 다시 승인하세요)</p></div>' : html;
      MailApp.sendEmail({
        to: to, replyTo: email, name: 'LICHTZEN 홈페이지',
        subject: '[홈페이지 문의] ' + (d.topic || '일반 문의') + ' · ' + (who || email),
        htmlBody: body, attachments: attachments,
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
    return json({ok: false, error: 'server', detail: String(err && err.message || err).slice(0, 180)});
  }
}

/** 문의 목록 파일을 열거나(없으면 만들고), 그해 연도 탭을 돌려줍니다. 연도 탭은 머리줄·상태 목록·줄 고정을 갖춥니다. */
function book_() {
  const props = PropertiesService.getScriptProperties();
  const id = CONFIG.SHEET_ID || props.getProperty('SHEET_ID');
  if (id) { try { return SpreadsheetApp.openById(id); } catch (err) {} }
  const ss = SpreadsheetApp.create('LICHTZEN 홈페이지 문의 목록');
  props.setProperty('SHEET_ID', ss.getId());
  ss.getSheets()[0].setName('통계');
  return ss;
}
function sheet_(year) {
  const ss = book_();
  let sh = ss.getSheetByName(year);
  if (!sh) {
    sh = ss.insertSheet(year, 1);                                       // '통계' 바로 뒤 = 최신 연도가 앞
    sh.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]).setFontWeight('bold').setBackground('#1b2a36').setFontColor('#ffffff');
    sh.setFrozenRows(1);
    sh.setColumnWidths(1, HEADERS.length, 120); sh.setColumnWidth(13, 420); sh.setColumnWidth(14, 260);
    sh.getRange('C2:C').setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(STATUS, true).build());
    sh.getRange('D2:D').setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(REGIONS, true).build());
    sh.getRange('M2:N').setWrap(true);
  }
  return sh;
}

/** '통계' 탭을 다시 씁니다: 표 4개 + 그래프 4개 (분류·국내/해외·월별·연도별). */
function stats_(ss) {
  const years = ss.getSheets().map(sh => sh.getName()).filter(n => /^\d{4}$/.test(n)).sort();
  if (!years.length) return;
  const last = years[years.length - 1];
  const byCat = {}, byMonth = {}, byRegion = {}, lastCatRegion = {};
  years.forEach(y => {
    const sh = ss.getSheetByName(y); const n = sh.getLastRow() - 1; if (n < 1) return;
    sh.getRange(2, 1, n, 6).getValues().forEach(r => {
      const reg = r[3] === '해외' ? '해외' : '국내'; const cat = r[5] || CATEGORY.other; const m = Number(String(r[1]).slice(5, 7)) || 0;
      byCat[cat] = byCat[cat] || {}; byCat[cat][y] = (byCat[cat][y] || 0) + 1;
      byRegion[y] = byRegion[y] || {국내: 0, 해외: 0}; byRegion[y][reg]++;
      if (m) { byMonth[m] = byMonth[m] || {}; byMonth[m][y] = (byMonth[m][y] || 0) + 1; }
      if (y === last) { lastCatRegion[cat] = lastCatRegion[cat] || {국내: 0, 해외: 0}; lastCatRegion[cat][reg]++; }
    });
  });
  let st = ss.getSheetByName('통계'); if (!st) st = ss.insertSheet('통계', 0);
  st.getCharts().forEach(c => st.removeChart(c));
  st.clear();
  const cats = CATEGORY_ORDER.filter(c => byCat[c]).concat(Object.keys(byCat).filter(c => CATEGORY_ORDER.indexOf(c) < 0));
  const lastCats = cats.filter(c => lastCatRegion[c]);
  const sum = a => a.reduce((x, y) => x + y, 0);
  let row = 1;
  const table = (title, data) => {
    st.getRange(row, 1).setValue(title).setFontWeight('bold').setFontSize(13);
    st.getRange(row + 1, 1, data.length, data[0].length).setValues(data);
    st.getRange(row + 1, 1, 1, data[0].length).setFontWeight('bold').setBackground('#1b2a36').setFontColor('#ffffff');
    const at = row + 1; row += data.length + 3; return at;
  };
  // 표 1: 올해 분류 × 국내/해외
  const t1 = [['분류', '국내', '해외', '합계']].concat(lastCats.map(c => [c, lastCatRegion[c].국내, lastCatRegion[c].해외, lastCatRegion[c].국내 + lastCatRegion[c].해외]));
  t1.push(['합계', sum(t1.slice(1).map(r => r[1])), sum(t1.slice(1).map(r => r[2])), sum(t1.slice(1).map(r => r[3]))]);
  const a1 = table(last + '년 분류별 문의 수 (국내·해외)', t1);
  // 표 1-1: 올해 국내·해외 (원그래프용)
  const tot = t1[t1.length - 1];
  const a11 = table(last + '년 국내·해외', [['구분', '건수'], ['국내', tot[1]], ['해외', tot[2]]]);
  // 표 2: 연도 × 국내/해외
  const t2 = [['연도', '국내', '해외', '합계']].concat(years.map(y => { const r = byRegion[y] || {국내: 0, 해외: 0}; return [y + '년', r.국내, r.해외, r.국내 + r.해외]; }));
  const a2 = table('연도별 국내·해외 문의 수', t2);
  // 표 3: 분류 × 연도
  const t3 = [['분류'].concat(years, ['합계'])].concat(cats.map(c => { const v = years.map(y => (byCat[c] || {})[y] || 0); return [c].concat(v, [sum(v)]); }));
  table('연도·분류별 문의 수', t3);
  // 표 4: 월 × 연도
  const t4 = [['월'].concat(years)].concat([1,2,3,4,5,6,7,8,9,10,11,12].map(m => [m + '월'].concat(years.map(y => (byMonth[m] || {})[y] || 0))));
  const a4 = table('월별 문의 수', t4);
  st.setColumnWidth(1, 170);
  const col = Math.max(t1[0].length, t3[0].length, t4[0].length) + 2;
  const C = ['#4f7d18', '#6c5ce7', '#e8912d', '#5b7083'];
  const chart = (b, top, title, h) => st.insertChart(b.setPosition(top, col, 0, 0).setOption('title', title).setOption('legend', {position: 'top'})
    .setOption('colors', C).setOption('width', 660).setOption('height', h || 340).build());
  // 그래프 1: 올해 분류별 국내/해외 (누적 막대)
  if (lastCats.length) chart(st.newChart().setChartType(Charts.ChartType.BAR).addRange(st.getRange(a1, 1, lastCats.length + 1, 3)).setOption('isStacked', true), 1, last + '년 분류별 문의 수 (국내·해외)', 360);
  // 그래프 2: 국내·해외 비율 (올해)
  chart(st.newChart().setChartType(Charts.ChartType.PIE).addRange(st.getRange(a11, 1, 3, 2)).setOption('pieHole', 0.45), 20, last + '년 국내·해외 비율', 300);
  // 그래프 3: 연도별 국내·해외
  chart(st.newChart().setChartType(Charts.ChartType.COLUMN).addRange(st.getRange(a2, 1, years.length + 1, 3)).setOption('isStacked', true), 36, '연도별 국내·해외 문의 수', 300);
  // 그래프 4: 월별 추이
  chart(st.newChart().setChartType(Charts.ChartType.COLUMN).addRange(st.getRange(a4, 1, 13, years.length + 1)), 52, '월별 문의 수', 300);
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
  DriveApp.getFileById(ss.getId());                                     // needs the Drive permission; fails early with a clear message if missing
  const res = UrlFetchApp.fetch(url, {headers: {Authorization: 'Bearer ' + ScriptApp.getOAuthToken()}, muteHttpExceptions: true, followRedirects: true});
  const type = String(res.getHeaders()['Content-Type'] || '');
  if (res.getResponseCode() !== 200 || /text\/html/.test(type)) throw new Error('엑셀 내보내기 ' + res.getResponseCode() + ' ' + type.split(';')[0]);
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

// Cloudflare Turnstile 확인. 프로젝트 설정 > 스크립트 속성에 TURNSTILE_SECRET(비밀 키)이 있을 때만 검사합니다.
// 비밀 키는 이 파일이나 저장소에 적지 마세요.
function human_(token) {
  const secret = PropertiesService.getScriptProperties().getProperty('TURNSTILE_SECRET');
  if (!secret) return true;
  if (!token) return false;
  try {
    const r = UrlFetchApp.fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'post', payload: {secret: secret, response: String(token).slice(0, 2048)}, muteHttpExceptions: true});
    return JSON.parse(r.getContentText()).success === true;
  } catch (err) { return false; }
}

function allow_(email) {
  const c = CacheService.getScriptCache();
  const hour = Utilities.formatDate(new Date(), 'UTC', 'yyyyMMddHH');
  const bump = (k, max) => { const n = Number(c.get(k) || 0) + 1; if (n > max) return false; c.put(k, String(n), 3600); return true; };
  return bump('all:' + hour, CONFIG.MAX_PER_HOUR) && bump('em:' + email.toLowerCase() + ':' + hour, CONFIG.MAX_PER_EMAIL_HOUR);
}

function json(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

/** 편집기에서 실행: 권한 승인 → 시트·폴더 자동 생성 → 시험 메일 2통(문의 + 접수 확인).
 *  시험으로 넣은 줄은 메일을 보낸 뒤 시트에서 자동으로 지우고 통계를 다시 계산합니다. */
function testSend() {
  const me = Session.getEffectiveUser().getEmail();
  const r = doPost({postData: {contents: JSON.stringify({
    source: '시험', category: 'other', topic: '연결 확인', message: '[시험] 홈페이지 문의 연결 확인용입니다. 이 줄은 시트에서 자동으로 지워집니다.',
    email: me, who: '시험', lang: 'ko',
  })}});
  console.log(r.getContent());
  removeRows_(row => row[4] === '시험');
  console.log('문의 목록 시트: ' + book_().getUrl());
}

/** 시험·임의 문의 지우기: '문의 경로'가 '시험'이거나 이메일이 스크립트 계정인 줄을 모두 지우고 통계를 다시 계산합니다. */
function removeTestRows() {
  const me = Session.getEffectiveUser().getEmail().toLowerCase();
  const n = removeRows_(row => row[4] === '시험' || String(row[8]).toLowerCase() === me);
  console.log('지운 줄: ' + n);
}

/** 전체 초기화: 모든 연도 탭의 문의 줄을 지우고(머리줄은 남김) 통계를 비웁니다. 정식 공개 직전에 한 번 실행하세요. */
function resetAllRows() {
  const n = removeRows_(() => true);
  console.log('지운 줄: ' + n + ' (첨부 폴더의 파일은 드라이브에서 직접 지우세요)');
}

/** 시트에서 줄을 직접 지운 뒤 실행: 통계 탭만 다시 계산합니다. (다음 문의가 들어올 때도 자동으로 다시 계산됩니다) */
function refreshStats() { stats_(book_()); console.log('통계를 다시 계산했습니다.'); }

function removeRows_(match) {
  const ss = book_(); let removed = 0;
  ss.getSheets().filter(sh => /^\d{4}$/.test(sh.getName())).forEach(sh => {
    const n = sh.getLastRow() - 1; if (n < 1) return;
    const rows = sh.getRange(2, 1, n, HEADERS.length).getValues();
    for (let i = rows.length - 1; i >= 0; i--) if (match(rows[i])) { sh.deleteRow(i + 2); removed++; }
  });
  stats_(ss);
  return removed;
}

/** 권한이 빠졌을 때 편집기에서 한 번 실행: 승인 안 된 권한(외부 서비스 연결 등)만 다시 묻습니다. 창의 항목을 모두 체크하고 허용하세요. */
function authorizeAll() {
  ScriptApp.requireAllScopes(ScriptApp.AuthMode.FULL);
  UrlFetchApp.fetch('https://www.google.com/generate_204', {muteHttpExceptions: true});
  DriveApp.getRootFolder();
  SpreadsheetApp.getActiveSpreadsheet();
  console.log('권한 확인 완료: 외부 서비스 연결·드라이브·시트·메일');
}
