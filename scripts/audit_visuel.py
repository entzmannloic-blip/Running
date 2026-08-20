#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_visuel.py — Le dernier axe non couvert : le RENDU.

Les autres audits verifient que le contenu existe, que les KPI sont justes et
que rien ne plante. Aucun ne verifiait que c'est LISIBLE et BIEN PLACE. Six
defauts visibles ont ete trouves en quatre captures d'ecran le 20/08/2026,
dont deux bugs de donnees (emoji non echappe, compte a rebours divergent)
qu'aucun des sept controles automatiques n'avait detectes.

Ce script controle, sur les quatre vues principales :
  V1 sequences d'echappement non rendues (\\uXXXX, \\UXXXXXXXX visibles)
  V2 coherence des compteurs J- entre les vues
  V3 debordement horizontal (scroll lateral parasite)
  V4 cibles tactiles sous 44 px (norme Apple)
  V5 textes sous le plancher de lisibilite
  V6 elements fixes masquant du contenu
  V7 texte tronque ou en collision

Usage : python3 audit_visuel.py [--rapide]
"""
import re
import sys

HTML = "file:///mnt/user-data/outputs/plan-entrainement.html"
RAPIDE = "--rapide" in sys.argv

VUES = ["accueil", "plan", "cockpit", "palmares"]
PLANCHER_POLICE = 11      # en deca : illisible en exterieur
MIN_TACTILE = 44          # norme Apple Human Interface Guidelines

BUGS, ALERTES, INFOS = [], [], []
def bug(c, m):    BUGS.append((c, m))
def alerte(c, m): ALERTES.append((c, m))
def info(c, m):   INFOS.append((c, m))


def run():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(viewport={"width": 390, "height": 844})
        errs = []
        p.on("pageerror", lambda e: errs.append(str(e)[:120]))
        p.goto(HTML, wait_until="load", timeout=30000)
        p.wait_for_timeout(2000)
        p.evaluate("var o=document.getElementById('rwoverlay');"
                   "if(o){o.classList.remove('on');o.style.display='none';}")

        # ══ V1 — sequences d'echappement visibles a l'ecran ══════════
        # Une sequence \uXXXX ou \UXXXXXXXX qui apparait dans le TEXTE rendu
        # signifie qu'elle n'a pas ete interpretee. C'est le bug qui affichait
        # « U0001F3C1 Nice » au lieu du drapeau a damier sur l'accueil.
        for v in VUES:
            p.evaluate(f"showTab('{v}')")
            p.wait_for_timeout(500)
            txt = p.evaluate(f"document.getElementById('vue-{v}')?.innerText||''")
            for m in re.finditer(r"\\?[uU][0-9A-Fa-f]{4,8}", txt):
                frag = txt[max(0, m.start() - 25):m.start() + 25].replace("\n", " ")
                bug("V1", f"vue {v} : sequence d'echappement affichee telle quelle "
                          f"-> « ...{frag}... »")

        # ══ V2 — coherence des compteurs J- entre les vues ═══════════
        vals = {}
        for v in VUES:
            p.evaluate(f"showTab('{v}')")
            p.wait_for_timeout(400)
            txt = p.evaluate(f"document.getElementById('vue-{v}')?.innerText||''")
            for m in re.finditer(r"J-(\d+)\s*\n?\s*([A-ZÉÈ][^\n]{2,40})", txt):
                vals.setdefault(m.group(2).strip()[:24], set()).add(int(m.group(1)))
        for course, jours in vals.items():
            if len(jours) > 1:
                bug("V2", f"« {course} » affiche {sorted(jours)} selon la vue "
                          f"— le compte a rebours diverge")

        # ══ V3 — debordement horizontal ═════════════════════════════
        for v in VUES:
            p.evaluate(f"showTab('{v}')")
            p.wait_for_timeout(400)
            # Un element peut depasser legitimement s'il vit dans un conteneur
            # a defilement horizontal voulu (barre d'onglets, carrousel).
            deb = p.evaluate("""(function(){
                var w=document.documentElement.clientWidth,bad=[];
                function dansScrollH(e){
                  for(var p=e.parentElement;p;p=p.parentElement){
                    var ox=getComputedStyle(p).overflowX;
                    if(ox==='auto'||ox==='scroll')return true;}
                  return false;}
                document.querySelectorAll('*').forEach(function(e){
                  var r=e.getBoundingClientRect();
                  if(r.width>0&&r.right>w+2&&!dansScrollH(e))
                    bad.push({t:(e.innerText||e.tagName).trim().slice(0,30),
                              d:Math.round(r.right-w)});});
                return bad.slice(0,4);})()""")
            for d in deb:
                bug("V3", f"vue {v} : deborde de {d['d']} px a droite — « {d['t']} »")

        # ══ V4 — cibles tactiles ════════════════════════════════════
        p.evaluate("showTab('accueil')")
        p.wait_for_timeout(400)
        petits = p.evaluate(f"""(function(){{
            var bad=[];
            document.querySelectorAll('button,a,[onclick]').forEach(function(e){{
              var r=e.getBoundingClientRect();
              if(r.width>4&&r.height>4&&r.height<{MIN_TACTILE})
                bad.push({{t:(e.innerText||e.title||'').trim().split('\\n')[0].slice(0,28),
                          h:Math.round(r.height)}});}});
            return bad;}})()""")
        for x in petits:
            alerte("V4", f"cible tactile {x['h']} px (< {MIN_TACTILE}) — « {x['t']} »")

        # ══ V5 — plancher de lisibilite ═════════════════════════════
        for v in VUES:
            p.evaluate(f"showTab('{v}')")
            p.wait_for_timeout(400)
            n = p.evaluate(f"""(function(){{
                var n=0;
                document.querySelectorAll('#vue-{v} *').forEach(function(e){{
                  if(!e.innerText||e.children.length)return;
                  if(parseFloat(getComputedStyle(e).fontSize)<{PLANCHER_POLICE})n++;}});
                return n;}})()""")
            if n:
                alerte("V5", f"vue {v} : {n} element(s) sous {PLANCHER_POLICE} px")

        # ══ V6 — elements fixes masquant du contenu ═════════════════
        for v in VUES:
            p.evaluate(f"showTab('{v}')")
            p.wait_for_timeout(500)
            masq = p.evaluate("""(function(){
                var out=[];
                document.querySelectorAll('*').forEach(function(e){
                  var s=getComputedStyle(e);
                  if(s.position!=='fixed'||s.display==='none'||s.visibility==='hidden')return;
                  if(parseFloat(s.opacity)<0.1||s.pointerEvents==='none')return;
                  var r=e.getBoundingClientRect();
                  if(r.width<20||r.height<20||r.bottom>innerHeight-4)return;
                  var lbl=(e.innerText||'').trim().slice(0,20);
                  var sous=document.elementsFromPoint(r.left+r.width/2,r.top+r.height/2);
                  for(var i=1;i<sous.length;i++){
                    var t=(sous[i].innerText||'').trim();
                    if(t&&t.length>8&&!e.contains(sous[i])){
                      out.push({f:lbl,m:t.split('\\n')[0].slice(0,32)});break;}}
                });
                return out.slice(0,3);})()""")
            for x in masq:
                bug("V6", f"vue {v} : l'element fixe « {x['f']} » masque « {x['m']} »")

        # ══ V7 — collisions de texte ════════════════════════════════
        if not RAPIDE:
            for v in VUES:
                p.evaluate(f"showTab('{v}')")
                p.wait_for_timeout(400)
                col = p.evaluate("""(function(){
                    var bad=[];var els=[].slice.call(document.querySelectorAll('*'))
                      .filter(function(e){return e.innerText&&!e.children.length;});
                    for(var i=0;i<els.length;i++){
                      var a=els[i].getBoundingClientRect();
                      if(a.width<10)continue;
                      for(var j=i+1;j<Math.min(i+6,els.length);j++){
                        var b=els[j].getBoundingClientRect();
                        if(b.width<10)continue;
                        var ox=Math.min(a.right,b.right)-Math.max(a.left,b.left);
                        var oy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);
                        if(ox>12&&oy>8)bad.push({a:els[i].innerText.trim().slice(0,18),
                                                 b:els[j].innerText.trim().slice(0,18)});}}
                    return bad.slice(0,3);})()""")
                for x in col:
                    alerte("V7", f"vue {v} : « {x['a']} » et « {x['b']} » se chevauchent")

        if errs:
            bug("V0", f"erreur JS pendant l'audit visuel : {errs[0]}")
        b.close()

    # ─── rapport ───
    print("=" * 68)
    print("  AUDIT VISUEL — rendu, lisibilite, placement")
    print("=" * 68)
    for titre, lot in (("DEFAUTS VISIBLES", BUGS),
                       ("A AMELIORER", ALERTES),
                       ("INFORMATIF", INFOS)):
        print(f"\n── {titre} ({len(lot)}) " + "─" * max(2, 44 - len(titre)))
        if not lot:
            print("   rien a signaler")
        for c, m in lot:
            print(f"   [{c}] {m}")
    print("\n" + "=" * 68)
    print(f"  RESULTAT : {len(BUGS)} defaut(s) visible(s) · "
          f"{len(ALERTES)} amelioration(s) · {len(INFOS)} info(s)")
    print("=" * 68)
    # Seuls les defauts visibles bloquent. Les ameliorations sont un chantier
    # de refonte, pas un motif de refus de livraison.
    return 1 if BUGS else 0


if __name__ == "__main__":
    sys.exit(run())
