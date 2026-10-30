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


# textes.json : revues de seance et de semaine, splits, slides des Rewinds. Charges a l'ouverture
# d'une fiche (window.loadTextes), donc retires des fichiers lus au demarrage. data.json reste complet.
full = data
data = json.loads(json.dumps(full))
textes = {'SEANCES': {}, 'SEMAINES': {}, 'REWINDS': {}}
for w, arr in data['SBW'].items():
    for s in arr:
        r = s.get('realise') or {}
        t = {k: r.pop(k) for k in ('revue', 'splits') if k in r}
        if t:
            textes['SEANCES'][f"{w}-{s['id']}"] = t
for s in data['SEMAINES']:
    if 'revue' in s:
        textes['SEMAINES'][str(s['num'])] = s.pop('revue')
for rw in data['REWINDS']:
    if 'slides' in rw:
        textes['REWINDS'][rw['id']] = rw.pop('slides')
write('site/data/textes.json', dump(textes))

# Rewind de seance (P4) : un fichier par seance (src/rewind/44-2.json, ecrit par scripts/rewind_seance.py),
# publie en data/rewind-44-2.json et charge a l'ouverture du Rewind. On y ajoute les elements du coach tires de
# la revue (rien n'est reformule) ; la cible appliquee (seance remplacee) va aussi dans realise.cible.
import glob
import html as _html
import re


def _texte(h):
    return _html.unescape(re.sub(r'<[^>]+>', '', h or '')).strip()


def coach_de(revue):
    """Verdict, ce qui est bien, a corriger, conseil. Convention : <p data-coach="verdict|bien|corriger|conseil">.
    Revues plus anciennes : decoupage par intertitres en gras (« Le point a corriger », « Ce qui est bon », « Suite »,
    « Verdict : A »), le premier paragraphe portant le verdict."""
    out = {}
    for cle, corps in re.findall(r'<p[^>]*data-coach="(verdict|bien|corriger|conseil)"[^>]*>(.*?)</p>', revue, re.S):
        m = re.match(r'\s*<strong>(.*?)</strong>(.*)', corps, re.S)
        out[cle] = _texte(m.group(2)) if (m and cle != 'verdict' and _texte(m.group(2))) else _texte(corps)
    if out:
        return out
    for i, p in enumerate(re.findall(r'<p>(.*?)</p>', revue, re.S)):
        m = re.match(r'\s*<strong>(.*?)</strong>(.*)', p, re.S)
        tete, reste = (_texte(m.group(1)), _texte(m.group(2))) if m else ('', _texte(p))
        bas = tete.lower()
        mv = re.match(r'verdict\s*:\s*([A-E][+-]?)\.?', bas, re.I)
        if i == 0:
            out['verdict'] = tete or reste
            if tete and reste:
                out['bien_implicite'] = reste
        elif mv:
            out['note'], out['note_texte'] = mv.group(1).upper(), reste
        elif re.search(r'corriger|à revoir|point faible|surveiller|reste haut', bas):
            out['corriger'] = reste
        elif re.search(r'ce qui est bon|ce qui est bien|le bon|solide', bas):
            out['bien'] = reste
        elif re.search(r'^suite|pour la suite|prochaine|conseil', bas):
            out['conseil'] = reste
    if 'bien' not in out and 'bien_implicite' in out:
        out['bien'] = out['bien_implicite']
    out.pop('bien_implicite', None)
    return out


rewinds = []
for chemin in sorted(glob.glob(os.path.join('rewind', '*.json'))):
    cle = os.path.basename(chemin)[:-5]
    w, n = cle.split('-')
    pleine = next((s for s in full['SBW'].get(w, []) if str(s['id']) == n), None)
    if not pleine or (pleine.get('realise') or {}).get('statut') not in ('fait', 'partiel'):
        raise SystemExit(f'Rewind {cle} : seance absente ou non realisee')
    rw = json.load(open(chemin, encoding='utf-8'))
    rw['coach'] = coach_de(pleine['realise'].get('revue') or '')
    write(f'site/data/rewind-{cle}.json', dump(rw))
    rewinds.append(cle)
assert rewinds == data['REWIND_SEANCE'], 'index des Rewinds (gen.py) different des fichiers publies'

# Carte d'une course (écran « Le parcours ») : trace rééchantillonnée par scripts/carto_course.py dans
# src/carto/<id>.json, publiée en data/carto-<id>.json ; chaque dossier qui en déclare une doit l'avoir.
cartos = []
for chemin in sorted(glob.glob(os.path.join('carto', '*.json'))):
    cle = os.path.basename(chemin)[:-5]
    tr = json.load(open(chemin, encoding='utf-8'))
    assert tr.get('id') == cle and len(tr['lat']) == len(tr['lon']) == len(tr['ele']) == tr['n'], f'carto {cle} : trace incoherente'
    write(f'site/data/carto-{cle}.json', dump(tr))
    cartos.append(cle)
for _id, _d in data['DOSSIERS'].items():
    _t = (_d.get('carto') or {}).get('trace')
    assert not _t or _t in cartos, f'dossier {_id} : trace {_t} absente de src/carto/'

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
var tx=null;
window.loadTextes=function(){
  if(!tx)tx=get("textes").catch(function(e){tx=null;throw e;});
  return tx;
};
window.loadChangelog=function(){
  if(!cl)cl=get("changelog").then(function(o){window.CHANGELOG=o.CHANGELOG;return o.CHANGELOG;}).catch(function(e){cl=null;throw e;});
  return cl;
};
var T0=(window.performance&&performance.now)?performance.now():0;
/* Écran de démarrage (build 287) : le tracé orange se dessine ; quand l'app est prête (et au plus tôt 900 ms
   après le début du démarrage, le temps que le tracé finisse), l'événement boot-sortie lance l'entrée de
   l'Accueil et l'écran s'efface en fondu. Sous réduire les animations : rien n'attend, l'écran disparaît. */
function sortie(){
  var l=document.getElementById("boot-load");if(!l)return;
  var rm=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches,now=(window.performance&&performance.now)?performance.now():0;
  setTimeout(function(){
    try{document.dispatchEvent(new Event("boot-sortie"));}catch(e){}
    if(rm){l.remove();return;}
    l.classList.add("sortie");setTimeout(function(){l.remove();},420);
  },rm?0:Math.max(0,T0+900-now));
}
Promise.all(EAGER.map(get)).then(function(all){
  all.forEach(function(o){Object.assign(window,o);});
  var s=document.createElement("script");
  s.src="src/app.js?v="+V;
  s.onload=sortie;
  s.onerror=fail;
  document.body.appendChild(s);
}).catch(fail);
})();
</script>"""

BOOT_UI = """<div id="boot-load" role="status"><svg class="boot-mark" viewBox="0 0 132 66" aria-hidden="true"><path pathLength="1" d="M8 50C24 50 28 16 46 16S68 52 86 44 108 14 122 18"/><circle cx="122" cy="18" r="7"/></svg><p class="boot-lb" aria-hidden="true">Saison 2026</p><span class="sr-only">Chargement…</span></div>
<div id="boot-err" role="alert" hidden><p>Données indisponibles. Vérifie ta connexion puis réessaie.</p><button type="button" class="btn-nav" onclick="location.reload()">Réessayer</button></div>"""

BOOT_CSS = """#boot-load,#boot-err{position:fixed;inset:0;z-index:500;display:flex;flex-direction:column;gap:14px;align-items:center;justify-content:center;padding:24px;text-align:center;background:var(--gris-fond);color:var(--texte-trois);font-size:var(--t-callout)}
#boot-err{color:var(--texte)}#boot-load[hidden],#boot-err[hidden]{display:none}
#boot-load .boot-mark{width:132px;height:66px;overflow:visible}
#boot-load .boot-mark path{fill:none;stroke:var(--primary);stroke-width:7;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:0}
#boot-load .boot-mark circle{fill:var(--primary);transform-box:fill-box;transform-origin:center}
#boot-load .boot-lb{margin:0;font-family:var(--f-num);font-weight:800;font-size:22px;letter-spacing:.01em;color:var(--texte)}
@media (prefers-reduced-motion:no-preference){
  #boot-load .boot-mark path{animation:bootTrace 720ms cubic-bezier(.25,1,.5,1) 60ms both}
  #boot-load .boot-mark circle{animation:bootPoint 240ms cubic-bezier(.25,1,.5,1) 620ms both}
  #boot-load .boot-lb{animation:bootLb 360ms cubic-bezier(.25,1,.5,1) 280ms both}
  #boot-load.sortie{opacity:0;pointer-events:none;transition:opacity 400ms cubic-bezier(.25,1,.5,1)}
  #boot-load.sortie .boot-mark{scale:1.08;transition:scale 400ms cubic-bezier(.25,1,.5,1)}
}
@keyframes bootTrace{from{stroke-dashoffset:1}}
@keyframes bootPoint{from{transform:scale(0)}}
@keyframes bootLb{from{opacity:0;transform:translateY(6px)}}"""

HTML = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, must-revalidate"><meta http-equiv="Pragma" content="no-cache">
<title>Plan d'entraînement — {data['PROFIL']['prenom']} · Saison 2026</title>
<meta name="theme-color" content="#F4F4F6">
<link rel="preload" href="src/fonts/barlow-semi-condensed-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
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
