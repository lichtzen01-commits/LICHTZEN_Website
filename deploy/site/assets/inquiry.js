// Sends an inquiry (with attachments) to the Google Apps Script receiver in integrations/apps-script/Code.gs,
// which mails it to the company inbox. Paste the web app URL (ends in /exec) into ENDPOINT.
// While ENDPOINT is empty the site runs in test mode: nothing is sent and the caller shows a test notice.
(() => {
  const ENDPOINT = '';
  const LIMIT = {count: 3, each: 5 * 1024 * 1024, ext: /\.(pdf|jpe?g|png|webp)$/i};
  window.LTZ_FILE_LIMIT = LIMIT;
  window.LTZCheckFiles = list => list.length <= LIMIT.count && list.every(f => f.size <= LIMIT.each && LIMIT.ext.test(f.name));
  const b64 = f => new Promise((ok, no) => { const r = new FileReader(); r.onload = () => ok(String(r.result).split(',')[1] || ''); r.onerror = no; r.readAsDataURL(f); });
  window.LTZSendInquiry = async d => {
    if (d.bot) return {ok: true};                       // honeypot ticked: drop quietly
    if (!ENDPOINT) return {ok: false, test: true};
    try {
      const files = await Promise.all((d.files || []).map(async f => ({name: f.name, type: f.type, data: await b64(f)})));
      const payload = Object.assign({}, d, {files, page: location.href, lang: d.lang || window.LTZ_LANG || 'ko', browserLang: navigator.language});
      // text/plain keeps this a simple request (no CORS preflight), which Apps Script needs.
      const r = await fetch(ENDPOINT, {method: 'POST', body: JSON.stringify(payload)});
      const j = await r.json();
      return {ok: !!j.ok};
    } catch (e) { return {ok: false}; }
  };
})();
