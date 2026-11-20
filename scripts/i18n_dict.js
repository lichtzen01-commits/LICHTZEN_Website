// Prints the current Korean -> <lang> dictionary (site.js + i18n.js + docs/i18n/<lang>.json) as JSON,
// for the static language builds (scripts/build_en.py).  Usage: node scripts/i18n_dict.js deploy/site [en|zh|ja|hi|es]
const fs=require('fs');const path=require('path');const root=process.argv[2]||'deploy/site';const lang=process.argv[3]||'en';
const out={};
const sj=fs.readFileSync(path.join(root,'assets/site.js'),'utf8');
const m=sj.match(/const SITE_TRANSLATIONS=Object\.assign\((\{[\s\S]*?\}),window\.LTZ_I18N_EXTRA/);
if(m){const base=JSON.parse(m[1]);for(const k in base)if(base[k][lang])out[k]=base[k][lang];}
global.window={};global.location={search:''};global.document={documentElement:{dataset:{}}};
eval(fs.readFileSync(path.join(root,'assets/i18n.js'),'utf8'));
for(const k in window.LTZ_I18N_EXTRA){const v=window.LTZ_I18N_EXTRA[k];if(v&&v[lang])out[k]=v[lang];}
for(const k in (window.LTZ_I18N_PLACEHOLDER||{})){const v=window.LTZ_I18N_PLACEHOLDER[k];if(v&&v[lang])out[k]=v[lang];}
const f=path.join('docs/i18n',lang+'.json');if(fs.existsSync(f))Object.assign(out,JSON.parse(fs.readFileSync(f,'utf8')));
process.stdout.write(JSON.stringify(out));
