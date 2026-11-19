// Sends an inquiry (with attachments) to the Google Apps Script receiver in integrations/apps-script/Code.gs,
// which mails it to the company inbox. Paste the web app URL (ends in /exec) into ENDPOINT.
// While ENDPOINT is empty the site runs in test mode: nothing is sent and the caller shows a test notice.
(() => {
  const ENDPOINT = 'https://script.google.com/macros/s/AKfycbyputSB0hBF1liR88gskddIM0VZPVwacEV9YoIeCdBx1mESUfw8FsqbXfN2HWVLN8Me/exec';
  // Any document, spreadsheet, image, drawing or archive; programs and scripts are refused (mail servers reject them too).
  const LIMIT = {count: 5, each: 10 * 1024 * 1024, total: 20 * 1024 * 1024, blocked: /\.(exe|msi|bat|cmd|com|scr|pif|cpl|dll|js|jse|vbs|vbe|wsf|wsh|ps1|sh|jar|apk|app|lnk|reg|hta)$/i};
  window.LTZ_FILE_LIMIT = LIMIT;
  window.LTZCheckFiles = list => list.length <= LIMIT.count && list.reduce((n, f) => n + f.size, 0) <= LIMIT.total && list.every(f => f.size > 0 && f.size <= LIMIT.each && !LIMIT.blocked.test(f.name));
  const b64 = f => new Promise((ok, no) => { const r = new FileReader(); r.onload = () => ok(String(r.result).split(',')[1] || ''); r.onerror = no; r.readAsDataURL(f); });
  window.LTZSendInquiry = async d => {
    if (d.bot) return {ok: true};                       // honeypot ticked: drop quietly
    if (!ENDPOINT) return {ok: false, test: true};
    try {
      const files = await Promise.all((d.files || []).map(async f => ({name: f.name, type: f.type, data: await b64(f)})));
      const payload = Object.assign({}, d, {files, page: location.href, lang: d.lang || window.LTZ_LANG || 'ko', browserLang: navigator.language});
      // text/plain keeps this a simple request (no CORS preflight), which Apps Script needs.
      const r = await fetch(ENDPOINT, {method: 'POST', body: JSON.stringify(payload)});
      const text = await r.text();
      let j = null; try { j = JSON.parse(text); } catch (e) {}
      // No JSON back usually means a Google sign-in or authorization page: wrong deployment access or missing permission.
      if (!j) return {ok: false, error: /accounts\.google|ServiceLogin|signin/i.test(text) ? 'login' : (/authoriz|권한/i.test(text) ? 'auth' : 'html-' + r.status)};
      return {ok: !!j.ok, error: j.error ? j.error + (j.detail ? ': ' + j.detail : '') : undefined};
    } catch (e) { return {ok: false, error: 'network'}; }
  };
})();
