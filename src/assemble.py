import datetime
import json
import os

from datamap import GROUPS, EAGER

data = json.load(open('data.json', encoding='utf-8'))
css = open('css.txt', encoding='utf-8').read()
css += open('css_extra.txt', encoding='utf-8').read()
BODY = open('body.html', encoding='utf-8').read()
latest = data['CHANGELOG'][0]
build = latest['build']


def dump(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':'))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8', newline=chr(10)).write(text)


# data/*.json : un objet {NOM_GLOBAL: valeur} par fichier (voir datamap.py)
for fname, pairs in GROUPS.items():
    write(f'site/data/{fname}.json', dump({name: data[key] for name, key in pairs}))
# meta.json : seulement la derniere entree du changelog (la liste complete est chargee a la demande)
write('site/data/meta.json', dump({'CHANGELOG': [{
    'build': build, 'date': latest['date'], 'tag': latest.get('tag', ''), 'sha': latest.get('sha', ''), 'items': []}],
    'BUILT_ON': os.environ.get('RUNNING_TODAY') or datetime.date.today().isoformat()}))

BOOT = """<script>
(function(){
var V="@@BUILD@@",EAGER=@@EAGER@@;
function get(f){return fetch("data/"+f+".json?v="+V).then(function(r){if(!r.ok)throw new Error(f+" "+r.status);return r.json();});}
function fail(){var l=document.getElementById("boot-load");if(l)l.hidden=true;var e=document.getElementById("boot-err");if(e)e.hidden=false;}
var cl=null;
window.loadChangelog=function(){
  if(!cl)cl=get("changelog").then(function(o){window.CHANGELOG=o.CHANGELOG;return o.CHANGELOG;}).catch(function(e){cl=null;throw e;});
  return cl;
};
Promise.all(EAGER.map(get)).then(function(all){
  all.forEach(function(o){Object.assign(window,o);});
  var s=document.createElement("script");
  s.src="src/app.js?v="+V;
  s.onload=function(){var l=document.getElementById("boot-load");if(l)l.remove();};
  s.onerror=fail;
  document.body.appendChild(s);
}).catch(fail);
})();
</script>"""

BOOT_UI = """<div id="boot-load" role="status">Chargement…</div>
<div id="boot-err" role="alert" hidden><p>Données indisponibles. Vérifie ta connexion puis réessaie.</p><button type="button" class="btn-nav" onclick="location.reload()">Réessayer</button></div>"""

BOOT_CSS = """#boot-load,#boot-err{position:fixed;inset:0;z-index:500;display:flex;flex-direction:column;gap:14px;align-items:center;justify-content:center;padding:24px;text-align:center;background:var(--gris-fond);color:var(--texte-trois);font-size:var(--t-callout)}
#boot-err{color:var(--texte)}#boot-load[hidden],#boot-err[hidden]{display:none}"""

HTML = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, must-revalidate"><meta http-equiv="Pragma" content="no-cache">
<title>Plan d'entraînement — {data['PROFIL']['prenom']} · Saison 2026</title>
<meta name="theme-color" content="#0f172a">
<link rel="manifest" href="manifest.json">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Plan">
<link rel="apple-touch-icon" href="icon-180.png">
<style>{css}{BOOT_CSS}</style></head>
<body>
{BODY}
{BOOT_UI}
{BOOT.replace('@@BUILD@@', str(build)).replace('@@EAGER@@', json.dumps(EAGER))}
</body></html>"""
write('site/index.html', HTML)
print("Écrit:", len(HTML), "caractères")
