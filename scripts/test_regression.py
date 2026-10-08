#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_regression.py — Suite de tests runtime (anti-regression) pour Running PWA.

Complement de preflight.py :
  - preflight.py = checks STATIQUES (build, syntaxe, pipeline, secrets...)
  - test_regression.py = checks RUNTIME (l'app se charge, les vues rendent,
    les KPI se calculent, zero erreur JS console).

A lancer APRES le build, AVANT le push :
    python3 scripts/test_regression.py

Sortie : PASS/FAIL par test. Un seul FAIL => NE PAS PUSHER (exit 1).
Chaque test prouve qu'une fonctionnalite cle n'a pas regresse.

Prerequis : playwright + chromium installes ; HTML build present dans
/mnt/user-data/outputs/plan-entrainement.html
"""
import os
import sys
for _d in (os.path.dirname(os.path.abspath(__file__)), os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")):
    if os.path.exists(os.path.join(_d, "paths.py")):
        sys.path.insert(0, _d)
from paths import WORK, OUT_HTML, SITE, DATA_JSON, html_url, site_text  # noqa: E402
from datamap import GROUPS  # noqa: E402
import json
import sys

HTML = html_url()

PASS = []
FAIL = []


def check(name, cond, detail=""):
    if cond:
        PASS.append(name)
    else:
        FAIL.append(f"{name}" + (f" — {detail}" if detail else ""))


def run():
    from playwright.sync_api import sync_playwright

    js_errors = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        p.on("pageerror", lambda e: js_errors.append(str(e)[:200]))
        # on ignore les erreurs reseau (meteo bloquee en sandbox)
        p.on("console", lambda m: js_errors.append("console:" + m.text[:150])
             if m.type == "error" and "net::" not in m.text and "fetch" not in m.text.lower()
             and "open-meteo" not in m.text else None)

        # ── T01 : l'app se charge sans erreur JS fatale ──
        p.goto(HTML, wait_until="load", timeout=20000)
        p.wait_for_timeout(1500)
        p.evaluate("var o=document.getElementById('rwoverlay');if(o)o.style.display='none';")
        check("T01 chargement sans erreur JS", len(js_errors) == 0,
              "; ".join(js_errors[:3]))

        # ── T02 : les 4 vues rendent du contenu ──
        # Les identifiants sont ceux reellement utilises par showTab() :
        # accueil / plan / cockpit / palmares. Un nom inconnu masque TOUTES
        # les vues sans lever d'erreur, d'ou la verification ciblee sur
        # #vue-<id> plutot que sur document.body (la barre de navigation
        # suffisait a franchir l'ancien seuil et rendait le test complaisant).
        views = ["accueil", "plan", "cockpit", "palmares"]
        for v in views:
            try:
                p.evaluate(f"showTab('{v}')")
                p.wait_for_timeout(400)
                res = p.evaluate(
                    "(function(v){var e=document.getElementById('vue-'+v);"
                    "if(!e)return{ok:false,n:0,vis:false};"
                    "var vis=getComputedStyle(e).display!=='none';"
                    "var n=(e.innerText||'').trim().length;"
                    "return{ok:vis&&n>200,n:n,vis:vis};})('" + v + "')")
                check(f"T02 vue {v} rend du contenu",
                      bool(res and res.get("ok")),
                      f"visible={res.get('vis')} texte={res.get('n')} car.")
            except Exception as e:
                check(f"T02 vue {v}", False, str(e)[:80])

        # ── T03 : _ckRebuild existe et tourne sans lever ──
        rebuild_ok = p.evaluate(
            "(function(){try{if(typeof _ckRebuild!=='function')return false;"
            "_ckRebuild();return true;}catch(e){return String(e);}})()")
        check("T03 _ckRebuild s'execute", rebuild_ok is True,
              str(rebuild_ok) if rebuild_ok is not True else "")

        # ── T04 : ACWR dynamique dans une plage plausible ──
        acwr = p.evaluate("typeof _dynamicACWR==='function'?_dynamicACWR():null")
        check("T04 ACWR calcule", acwr is not None and 0.2 <= acwr <= 3.0,
              f"valeur={acwr}")

        # ── T05 : forme du jour coherente (0-100) ──
        forme = p.evaluate(
            "typeof computeFormeScore==='function'?computeFormeScore():null")
        ok_forme = forme and 0 <= forme.get("score", -1) <= 100 and forme.get("components")
        check("T05 forme du jour 0-100 + composantes", bool(ok_forme),
              f"score={forme.get('score') if forme else 'N/A'}")

        # ── T06 : _curWeek renvoie la bonne semaine (S28 la semaine du 7 juil 2026) ──
        # (test tolerant : doit etre un entier plausible 1-53)
        cw = p.evaluate("typeof _curWeek==='function'?_curWeek():null")
        check("T06 _curWeek renvoie une semaine valide", isinstance(cw, int) and 1 <= cw <= 53,
              f"valeur={cw}")

        # ── T07 : le chat coach est retire (decision d'octobre 2026) ──
        gone = p.evaluate(
            "(function(){var n=['openCoach','closeCoach','coachSend','coachChip','initCoach',"
            "'_cBuildSystemPrompt','_cReply','_cAddMsg'];"
            "return n.filter(function(f){return typeof window[f]!=='undefined';});})()")
        check("T07 chat coach retire (fonctions)", gone == [], f"encore la : {gone}")
        no_dom = p.evaluate(
            "!document.getElementById('coach-ov')&&!document.querySelector('.botbar .bi.coach')")
        check("T07 chat coach retire (DOM : overlay et bouton)", bool(no_dom))
        check("T07 plus d'appel a api.anthropic.com", "api.anthropic.com" not in site_text())

        # ── T08 : les conseils calcules localement restent ──
        kept = p.evaluate(
            "['coachAvant','coachDebrief','_coachNudge','_ouvrirNudge']"
            ".filter(function(f){return typeof window[f]!=='function';})")
        check("T08 conseils locaux conserves (fonctions)", kept == [], f"manquantes : {kept}")
        check("T08 COACH_THEORY conserve",
              bool(p.evaluate("typeof COACH_THEORY!=='undefined'&&Object.keys(COACH_THEORY).length>0")))

        # ── T08b : la puce de conseil ouvre la feuille de detail, sans lien vers le coach ──
        try:
            p.evaluate("showTab('accueil')")
            p.evaluate("window._NUDGE_={icon:'X',txt:'conseil de test',tone:'info'};_ouvrirNudge();")
            p.wait_for_timeout(400)
            sheet = p.evaluate("document.getElementById('contenu').innerHTML")
            check("T08b feuille de conseil affichee, sans bouton coach",
                  "conseil de test" in sheet and "Ouvrir le coach" not in sheet)
            p.evaluate("fermer()")
            p.evaluate("window._NUDGE_=null;_ouvrirNudge();")  # ne doit pas lever d'erreur
            p.evaluate("fermer()")
        except Exception as e:
            check("T08b feuille de conseil", False, str(e)[:80])

        # ── T14 : barre de navigation a 4 onglets, accessible ──
        p.evaluate("showTab('accueil')")
        nav = p.evaluate(
            "(function(){var bs=[].slice.call(document.querySelectorAll('#botbar .bi'));"
            "return{n:bs.length,ids:bs.map(function(b){return b.id;}),"
            "small:bs.filter(function(b){var r=b.getBoundingClientRect();return r.width<44||r.height<44;}).length,"
            "label:document.getElementById('botbar').getAttribute('aria-label'),"
            "cur:bs.filter(function(b){return b.getAttribute('aria-current')==='page';}).map(function(b){return b.id;})};})()")
        check("T14 barre : 4 onglets dans l'ordre",
              nav["ids"] == ["tab-accueil", "tab-plan", "tab-cockpit", "tab-palmares"], str(nav["ids"]))
        check("T14 barre : cibles tactiles >= 44 px", nav["small"] == 0, f"{nav['small']} trop petite(s)")
        check("T14 barre : nav etiquetee", bool(nav["label"]))
        check("T14 barre : aria-current sur l'onglet actif seulement", nav["cur"] == ["tab-accueil"], str(nav["cur"]))
        p.evaluate("showTab('cockpit')")
        cur = p.evaluate("[].slice.call(document.querySelectorAll('#botbar .bi[aria-current=page]')).map(function(b){return b.id;})")
        check("T14 barre : aria-current suit l'onglet", cur == ["tab-cockpit"], str(cur))
        p.evaluate("showTab('accueil')")
        p.focus("#tab-accueil")
        order = ["tab-accueil"]
        for _ in range(3):
            p.keyboard.press("Tab")
            order.append(p.evaluate("document.activeElement&&document.activeElement.id"))
        check("T14 barre : ordre clavier (Tab)",
              order == ["tab-accueil", "tab-plan", "tab-cockpit", "tab-palmares"], str(order))
        p.focus("#tab-plan")
        p.keyboard.press("Enter")
        p.wait_for_timeout(300)
        check("T14 barre : Entree ouvre l'onglet",
              bool(p.evaluate("document.getElementById('vue-plan').style.display==='block'")))
        p.evaluate("showTab('accueil')")

        # ── T09 : KPI Cockpit — les 4 fenetres donnent des volumes croissants ──
        try:
            p.evaluate("showTab('cockpit')")
            p.wait_for_timeout(400)
            vols = []
            for w in [2, 4, 8, 12]:
                p.evaluate(f"_ckRenderAll({w})")
                p.wait_for_timeout(150)
                el = p.evaluate("document.getElementById('ck-km-val')?"
                                "document.getElementById('ck-km-val').textContent:null")
                vols.append(el)
            # au moins que les valeurs existent et different
            distinct = len(set(v for v in vols if v)) > 1
            check("T09 Cockpit : volumes varient par fenetre", distinct,
                  f"volumes={vols}")
        except Exception as e:
            check("T09 Cockpit fenetres", False, str(e)[:80])

        # ── T10 : ACWR KPI card — label coherent avec la valeur ──
        try:
            p.evaluate("_ckRenderAll(8)")
            p.wait_for_timeout(200)
            val = p.evaluate("parseFloat(document.getElementById('ck-acwr-val').textContent)")
            label = p.evaluate(
                "document.getElementById('ck-acwr-val').parentElement"
                ".querySelector('.ck-kd')?.textContent||''").lower()
            # coherence : <0.8 => frais/allegement ; >1.5 => surcharge ; sinon maitrise/eleve
            coherent = True
            if val < 0.8 and not ("frais" in label or "all" in label):
                coherent = False
            if val > 1.5 and not ("surcharge" in label or "\u00e9lev" in label or "elev" in label):
                coherent = False
            check("T10 KPI ACWR : label coherent avec valeur", coherent,
                  f"val={val} label='{label}'")
        except Exception as e:
            check("T10 KPI ACWR label", False, str(e)[:80])

        # ── T11 : ouverture d'une fiche seance loggee (S27 course) ──
        try:
            p.evaluate("showTab('seances')")
            p.wait_for_timeout(300)
            opened = p.evaluate(
                "(function(){try{ouvrirSeance(27,4);return true;}catch(e){return String(e);}})()")
            p.wait_for_timeout(400)
            has_rev = p.evaluate(
                "!!document.querySelector('.rev-coach,[class*=revue],[class*=rev]')")
            check("T11 fiche seance s'ouvre", opened is True, str(opened))
        except Exception as e:
            check("T11 fiche seance", False, str(e)[:80])

        # ── T12 : Palmares contient la Deraille ──
        try:
            p.evaluate("showTab('courses')")
            p.wait_for_timeout(400)
            has_der = p.evaluate(
                "document.body.textContent.includes('raille')"
                "||document.body.textContent.includes('2:52')")
            check("T12 Palmares affiche la Deraille", bool(has_der))
        except Exception as e:
            check("T12 Palmares", False, str(e)[:80])

        # ── T15 : donnees servies en JSON, hors du paquet JavaScript ──
        site_files = ["index.html", "src/app.js", "data/plan.json", "data/seances.json",
                      "data/historique.json", "data/meta.json", "data/changelog.json"]
        missing = [f for f in site_files if not os.path.exists(os.path.join(SITE, *f.split("/")))]
        check("T15 site : fichiers presents", missing == [], f"absents : {missing}")
        idx = os.path.join(SITE, "index.html")
        idx_txt = open(idx, encoding="utf-8").read() if os.path.exists(idx) else ""
        check("T15 index.html ne contient plus les donnees",
              bool(idx_txt) and "const SEMAINES=" not in idx_txt and "const SEANCES_BY_WEEK=" not in idx_txt
              and len(idx_txt) < 400_000, f"{len(idx_txt)} caracteres")

        data = json.load(open(DATA_JSON, encoding="utf-8"))
        expected = {name: data[key] for name, key in
                    [pair for g in GROUPS if g != "changelog" for pair in GROUPS[g]]}
        bad = p.evaluate(
            """(exp) => {
              function eq(a,b){ if(a===b) return true;
                if(typeof a!==typeof b||a===null||b===null||typeof a!=='object') return false;
                if(Array.isArray(a)!==Array.isArray(b)) return false;
                var ka=Object.keys(a), kb=Object.keys(b); if(ka.length!==kb.length) return false;
                return ka.every(function(k){return eq(a[k],b[k]);}); }
              return Object.keys(exp).filter(function(n){return !eq(window[n], exp[n]);});
            }""", expected)
        check("T15 donnees JSON identiques a data.json (toutes les constantes)", bad == [], f"differentes : {bad[:6]}")
        check("T15 CHANGELOG de depart = derniere entree",
              p.evaluate("CHANGELOG[0].build") == data["CHANGELOG"][0]["build"])

        # la fenetre de version n'est plus construite au demarrage : elle l'est a l'ouverture
        check("T15 panneau de versions non construit au demarrage",
              not p.evaluate("!!document.getElementById('ver-ov')"))
        p.evaluate("openVersionPanel()")
        try:
            p.wait_for_selector("#ver-ov.open", timeout=4000)
            n_items = p.evaluate("document.querySelectorAll('#ver-ov .ver-item').length")
            check("T15 panneau de versions : toutes les builds a l'ouverture",
                  n_items == len(data["CHANGELOG"]), f"{n_items} / {len(data['CHANGELOG'])}")
            p.evaluate("closeVersionPanel()")
        except Exception as e:
            check("T15 panneau de versions s'ouvre", False, str(e)[:80])

        # echec reseau : message lisible et bouton de relance, jamais un ecran blanc
        try:
            ctx2 = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            ctx2.route("**/data/*.json*", lambda r: r.abort())
            p2 = ctx2.new_page()
            p2.goto(HTML, wait_until="load", timeout=20000)
            p2.wait_for_timeout(800)
            err = p2.evaluate(
                "(function(){var e=document.getElementById('boot-err');"
                "if(!e)return null;var r=e.getBoundingClientRect();"
                "return{visible:r.width>0&&r.height>0,txt:e.innerText,btn:!!e.querySelector('button')};})()")
            check("T15 donnees indisponibles : message + bouton Reessayer",
                  bool(err and err["visible"] and "indisponible" in err["txt"].lower() and err["btn"]), str(err))
            ctx2.close()
        except Exception as e:
            check("T15 donnees indisponibles", False, str(e)[:80])

        # les seances loggees dans localStorage sont toujours restituees apres le chargement asynchrone
        try:
            target = p.evaluate(
                "(function(){var ks=Object.keys(SEANCES_BY_WEEK);for(var i=ks.length-1;i>=0;i--){"
                "var a=SEANCES_BY_WEEK[ks[i]];for(var j=0;j<a.length;j++){if(!(a[j].realise&&a[j].realise.statut==='fait'))return[ks[i],String(a[j].id)];}}return null;})()")
            wk, sid = target
            p.evaluate("(a)=>localStorage.setItem('runlog_v1',JSON.stringify({[a[0]+'-'+a[1]]:{statut:'fait',km:9.9,temps:'1:00:00'}}))", [wk, sid])
            p.reload(wait_until="load")
            p.wait_for_function("typeof findSeance==='function'&&typeof SEANCES_BY_WEEK!=='undefined'", timeout=8000)
            km = p.evaluate("(a)=>{var s=findSeance(a[0],a[1]);return s&&s.realise&&s.realise.km;}", [wk, sid])
            check("T15 seance loggee restituee apres rechargement", km == 9.9, f"km={km}")
            p.evaluate("localStorage.removeItem('runlog_v1')")
            p.reload(wait_until="load")   # retire la seance de test de la memoire de la page
            p.wait_for_function("typeof showTab==='function'&&!document.getElementById('boot-load')", timeout=8000)
            p.evaluate("var o=document.getElementById('rwoverlay');if(o)o.style.display='none';")
        except Exception as e:
            check("T15 seance loggee", False, str(e)[:80])

        # ── T16 : PWA iOS — manifeste, service worker versionne, hors-ligne, mise a jour ──
        mf_path = os.path.join(SITE, "manifest.json")
        mf = json.load(open(mf_path, encoding="utf-8")) if os.path.exists(mf_path) else {}
        sizes = sorted(i.get("sizes") for i in mf.get("icons", []))
        check("T16 manifeste : standalone, portee, langue, icones 192 et 512",
              mf.get("display") == "standalone" and mf.get("scope") == "./" and mf.get("lang") == "fr"
              and "192x192" in sizes and "512x512" in sizes, str({k: mf.get(k) for k in ("display", "scope", "lang")}))
        meta_build = json.load(open(os.path.join(SITE, "data", "meta.json"), encoding="utf-8"))["CHANGELOG"][0]["build"]
        sw_path = os.path.join(SITE, "sw.js")
        sw_txt = open(sw_path, encoding="utf-8").read() if os.path.exists(sw_path) else ""
        listed = [f for f in ["src/app.js", "data/plan.json", "data/seances.json", "data/historique.json",
                              "data/meta.json", "data/changelog.json", "index.html"] if f in sw_txt]
        check("T16 sw.js : cache nomme d'apres le build, tous les fichiers pre-caches",
              f"'{meta_build}'" in sw_txt and "__BUILD__" not in sw_txt and len(listed) == 7,
              f"build={meta_build} liste={len(listed)}/7")

        try:
            ctx3 = b.new_context(viewport={"width": 390, "height": 844}, service_workers="allow")
            # un ancien cache (plan-v34) existe deja avant l'installation du nouveau worker
            ctx3.add_init_script("caches.open('plan-v34').then(function(c){return c.put('/legacy',new Response('old'));});")
            p3 = ctx3.new_page()
            p3.goto(HTML, wait_until="load", timeout=20000)
            p3.wait_for_function("typeof SEMAINES!=='undefined'", timeout=8000)
            p3.evaluate("navigator.serviceWorker.ready.then(function(){return true;})")
            p3.wait_for_function("!!navigator.serviceWorker.controller", timeout=8000)
            keys = p3.evaluate("caches.keys()")
            check("T16 ancien cache plan-v34 remplace par plan-<build>",
                  "plan-v34" not in keys and f"plan-{meta_build}" in keys, str(keys))
            ctx3.set_offline(True)
            p3.reload(wait_until="load")
            p3.wait_for_function("typeof SEMAINES!=='undefined'&&SEMAINES.length>0", timeout=8000)
            off = p3.evaluate("(function(){var e=document.getElementById('boot-err');"
                              "return{err:!!e&&!e.hidden,tab:!!document.getElementById('tab-accueil')};})()")
            check("T16 hors-ligne : l'app s'ouvre avec ses donnees", off["tab"] and not off["err"], str(off))
            ctx3.close()
        except Exception as e:
            check("T16 hors-ligne / cache", False, str(e)[:120])

        try:
            ctx4 = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            p4 = ctx4.new_page()
            p4.goto(HTML, wait_until="load", timeout=20000)
            p4.wait_for_function("typeof _checkNewVersion==='function'", timeout=8000)
            p4.evaluate("_checkNewVersion()")
            p4.wait_for_timeout(300)
            same = p4.evaluate("!!document.getElementById('upd-banner')")
            check("T16 pas de bandeau quand la version est a jour", not same)
            newer = {"CHANGELOG": [{"build": meta_build + 1, "date": "x", "tag": "", "sha": "", "items": []}]}
            ctx4.route("**/data/meta.json*", lambda r: r.fulfill(
                status=200, content_type="application/json", body=json.dumps(newer)))
            p4.evaluate("_checkNewVersion(true)")
            p4.wait_for_selector("#upd-banner", timeout=4000)
            bn = p4.evaluate("(function(){var e=document.getElementById('upd-banner');"
                             "return{txt:e.innerText,btn:!!e.querySelector('button')};})()")
            check("T16 bandeau « Nouvelle version prête » + bouton quand un build plus recent existe",
                  "nouvelle version" in bn["txt"].lower() and bn["btn"], str(bn))
            ctx4.close()
        except Exception as e:
            check("T16 bandeau de mise a jour", False, str(e)[:120])

        # ── T17 : coherence des chiffres et des libelles ──
        p.evaluate("showTab('accueil')")
        n_home = int(p.evaluate("(document.querySelector('.wdg-st-solo b')||{}).textContent||-1"))
        n_wrap = p.evaluate("_wrappedData().n")
        check("T17 meme nombre de sorties sur l'accueil et sur Courses", n_home == n_wrap, f"accueil={n_home} courses={n_wrap}")
        lab_home = p.evaluate("(function(){var e=document.querySelector('.wdg-st-solo');return e?e.innerText:'';})()")
        check("T17 accueil : le compteur precise sa periode (« sorties du plan »)",
              "du plan" in lab_home.lower(), repr(lab_home))
        p.evaluate("showTab('palmares')")
        p.wait_for_timeout(200)
        lab_wr = p.evaluate("(function(){var e=document.querySelector('.wrl-t2');return e?e.innerText:'';})()")
        check("T17 Courses : « sorties du plan » et meme nombre que l'accueil",
              "sorties du plan" in lab_wr and lab_wr.strip().startswith(str(n_home)), repr(lab_wr))

        # la jauge VO2max affiche sa valeur des le premier affichage (seul l'arc s'anime)
        p.evaluate("showTab('cockpit')")
        p.wait_for_timeout(180)
        vo2_txt = p.evaluate("document.getElementById('vo2-val')&&document.getElementById('vo2-val').textContent")
        vo2 = p.evaluate("_estimVO2()&&_estimVO2().vo2")
        check("T17 jauge VO2max : valeur finale des le debut (pas de passage par 0)",
              vo2 is not None and str(vo2_txt) == str(vo2), f"affiche={vo2_txt} attendu={vo2}")
        p.evaluate("showTab('accueil')")

        # donnees vides : aucune valeur cassee (NaN, undefined, Infinity) affichee sur les 4 vues
        try:
            ctx5 = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            errs5 = []
            def _route_seances(r):
                resp = r.fetch()
                d = resp.json()
                for wk, arr in d["SEANCES_BY_WEEK"].items():
                    for se in arr:
                        se["realise"] = {"statut": "a_faire"}
                r.fulfill(response=resp, body=json.dumps(d), content_type="application/json")
            def _route_plan(r):
                resp = r.fetch()
                d = resp.json()
                d["PALMARES"] = []
                r.fulfill(response=resp, body=json.dumps(d), content_type="application/json")
            ctx5.route("**/data/seances.json*", _route_seances)
            ctx5.route("**/data/plan.json*", _route_plan)
            ctx5.route("**/*open-meteo.com/**", lambda r: r.abort())
            p5 = ctx5.new_page()
            p5.on("pageerror", lambda e: errs5.append(str(e)[:120]))
            p5.goto(HTML, wait_until="load", timeout=20000)
            p5.wait_for_function("typeof showTab==='function'&&!document.getElementById('boot-load')", timeout=10000)
            p5.wait_for_timeout(800)
            p5.evaluate("var o=document.getElementById('rwoverlay');if(o)o.style.display='none';")
            broken = []
            for v in ["accueil", "plan", "cockpit", "palmares"]:
                p5.evaluate(f"showTab('{v}')")
                p5.wait_for_timeout(500)
                txt = p5.evaluate(f"document.getElementById('vue-{v}').innerText")
                import re as _re
                for m in _re.finditer(r"NaN|undefined|Infinity|\[object Object\]", txt):
                    broken.append(f"{v}: ...{txt[max(0, m.start()-30):m.end()+10]!r}")
            check("T17 donnees vides : aucune valeur cassee (NaN, undefined, Infinity) sur les 4 vues",
                  broken == [], "; ".join(broken[:4]))
            check("T17 donnees vides : aucune erreur JavaScript", errs5 == [], "; ".join(errs5[:3]))
            ctx5.close()
        except Exception as e:
            check("T17 donnees vides", False, str(e)[:120])

        # ── T18 : mode sombre qui suit le reglage du telephone (prefers-color-scheme) ──
        try:
            for scheme, expected in (("dark", True), ("light", False)):
                ctxd = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block", color_scheme=scheme)
                ctxd.route("**/*open-meteo.com/**", lambda r: r.abort())
                pd = ctxd.new_page()
                pd.goto(HTML, wait_until="load", timeout=20000)
                pd.wait_for_function("typeof showTab==='function'&&!document.getElementById('boot-load')", timeout=10000)
                has = pd.evaluate("document.body.classList.contains('nuit')")
                check(f"T18 reglage {scheme} : mode nuit {'actif' if expected else 'inactif'}", has == expected, f"nuit={has}")
                if scheme == "dark":
                    bg = pd.evaluate("getComputedStyle(document.body).backgroundColor")
                    check("T18 mode sombre : fond de page sombre", bg in ("rgb(11, 18, 32)",), bg)
                    pd.emulate_media(color_scheme="light")
                    pd.wait_for_timeout(200)
                    check("T18 bascule en direct (sombre -> clair) sans recharger",
                          not pd.evaluate("document.body.classList.contains('nuit')"))
                    pd.emulate_media(color_scheme="dark")
                    pd.wait_for_timeout(200)
                    check("T18 bascule en direct (clair -> sombre) sans recharger",
                          bool(pd.evaluate("document.body.classList.contains('nuit')")))
                ctxd.close()
            idx_txt2 = open(os.path.join(SITE, "index.html"), encoding="utf-8").read()
            check("T18 theme-color declare pour le mode sombre",
                  'name="theme-color" content="#0b1220" media="(prefers-color-scheme: dark)"' in idx_txt2)
            # pas d'eclair clair au demarrage : l'ecran de chargement lui-meme est sombre
            ctxe = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block", color_scheme="dark")
            ctxe.route("**/data/plan.json*", lambda r: r.abort())   # reste sur l'ecran d'erreur
            pe = ctxe.new_page()
            pe.goto(HTML, wait_until="load", timeout=20000)
            pe.wait_for_timeout(600)
            bgerr = pe.evaluate("getComputedStyle(document.getElementById('boot-err')).backgroundColor")
            check("T18 ecran d'erreur de chargement sombre en mode sombre", bgerr != "rgb(248, 250, 252)" and bgerr.startswith("rgb(1"), bgerr)
            ctxe.close()
        except Exception as e:
            check("T18 mode sombre", False, str(e)[:140])

        # ── T13 : pas d'erreur JS accumulee sur tout le parcours ──
        check("T13 zero erreur JS sur tout le parcours", len(js_errors) == 0,
              "; ".join(js_errors[:3]))

        b.close()


def main():
    try:
        run()
    except Exception as e:
        print(f"\n\u2717 ERREUR FATALE du harnais de test : {e}")
        sys.exit(2)

    print("\n" + "=" * 56)
    print("  TEST REGRESSION — runtime (Running PWA)")
    print("=" * 56)
    for m in PASS:
        print(f"  \u2713 {m}")
    for m in FAIL:
        print(f"  \u2717 {m}")
    print("=" * 56)
    total = len(PASS) + len(FAIL)
    if FAIL:
        print(f"  RESULTAT : {len(FAIL)}/{total} test(s) ECHOUE(S) — NE PAS PUSHER")
        print("=" * 56)
        sys.exit(1)
    print(f"  RESULTAT : {len(PASS)}/{total} tests OK — aucune regression")
    print("=" * 56)
    sys.exit(0)


if __name__ == "__main__":
    main()
