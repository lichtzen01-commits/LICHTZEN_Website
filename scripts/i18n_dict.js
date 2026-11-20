// Prints the current Korean->English dictionary (site.js + i18n.js + docs/i18n) as JSON, for the static English build.
const fs=require('fs');const path=require('path');const root=process.argv[2]||'deploy/site';
const out={};
const sj=fs.readFileSync(path.join(root,'assets/site.js'),'utf8');
const m=sj.match(/const SITE_TRANSLATIONS=Object\.assign\((\{[\s\S]*?\}),window\.LTZ_I18N_EXTRA/);
if(m){const base=JSON.parse(m[1]);for(const k in base)if(base[k].en)out[k]=base[k].en;}
global.window={};global.location={search:''};global.document={documentElement:{dataset:{}}};
eval(fs.readFileSync(path.join(root,'assets/i18n.js'),'utf8'));
for(const k in window.LTZ_I18N_EXTRA){const v=window.LTZ_I18N_EXTRA[k];if(v&&v.en)out[k]=v.en;}
for(const k in (window.LTZ_I18N_PLACEHOLDER||{})){const v=window.LTZ_I18N_PLACEHOLDER[k];if(v&&v.en)out[k]=v.en;}
const en=path.join('docs/i18n/en.json');if(fs.existsSync(en))Object.assign(out,JSON.parse(fs.readFileSync(en,'utf8')));
process.stdout.write(JSON.stringify(out));
