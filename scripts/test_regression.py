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


CHROME_JS = """var chrome=function(root){var sel='h1,h2,h3,h4,button,.ac-lb,.ac-puce,.fs-kick,.seance-tag,.st-chip,.cat-badge,.sem-num,.phase-lab,label,summary,[role=tab],.vue-titre,.lt-title';
  var rx=/\\p{Extended_Pictographic}/u,out=[];root.querySelectorAll(sel).forEach(function(e){if(e.closest('.rev-coach'))return;
  var t=(e.innerText||'').trim();if(rx.test(t))out.push(t.slice(0,40));});return out;};
"""


def check(name, cond, detail=""):
    if cond:
        PASS.append(name)
    else:
        FAIL.append(f"{name}" + (f" — {detail}" if detail else ""))
        # dans GitHub Actions, chaque echec devient une annotation lisible sans ouvrir les journaux
        if os.environ.get("GITHUB_ACTIONS"):
            msg = (f"{name} — {detail}" if detail else name).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
            print(f"::error title=Regression::{msg[:900]}", flush=True)


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
            val = p.evaluate("parseFloat(String(document.getElementById('ck-acwr-val').textContent).replace(',','.'))")
            label = p.evaluate("(document.getElementById('ckc-puce')||{}).textContent||''").lower()
            # coherence (lot 5 : puce de zone de la carte Charge) : <0.8 => sous-charge ; >1.5 => surcharge ; sinon optimale/vigilance
            coherent = bool(label)
            if val < 0.8 and "sous-charge" not in label:
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
              /* ACWR_DATA.acwr, charge7j et charge28j sont recalcules en direct par l'app (fenetre glissante
                 7/28 jours a la date du telephone) : ils ne valent les chiffres du build que le jour du build. */
              function vif(n,o){if(n!=='ACWR_DATA'||!o||typeof o!=='object')return o;var c=Object.assign({},o);
                delete c.acwr;delete c.charge7j;delete c.charge28j;return c;}
              return Object.keys(exp).filter(function(n){return !eq(vif(n,window[n]), vif(n,exp[n]));});
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
        n_home = int(p.evaluate("(document.querySelector('.ac-sorties b')||{}).textContent||-1"))
        n_wrap = p.evaluate("_wrappedData().n")
        check("T17 meme nombre de sorties sur l'accueil et sur Courses", n_home == n_wrap, f"accueil={n_home} courses={n_wrap}")
        lab_home = p.evaluate("(function(){var e=document.querySelector('.ac-sorties');return e?e.innerText:'';})()")
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

        # ── T18 : pas de mode sombre : l'app reste blanche meme si le telephone est en sombre ──
        try:
            ctxd = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block", color_scheme="dark")
            ctxd.route("**/*open-meteo.com/**", lambda r: r.abort())
            pd = ctxd.new_page()
            pd.goto(HTML, wait_until="load", timeout=20000)
            pd.wait_for_function("typeof showTab==='function'&&!document.getElementById('boot-load')", timeout=10000)
            has = pd.evaluate("document.body.classList.contains('nuit')")
            bg = pd.evaluate("getComputedStyle(document.body).backgroundColor")
            check("T18 telephone en sombre : l'app reste blanche (pas de classe nuit)", not has, f"nuit={has}")
            check("T18 telephone en sombre : fond de page clair", bg == "rgb(244, 244, 246)", bg)
            ctxd.close()
            idx_t18 = open(os.path.join(SITE, "index.html"), encoding="utf-8").read()
            check("T18 une seule balise theme-color, sans variante sombre",
                  idx_t18.count('name="theme-color"') == 1 and 'media="(prefers-color-scheme' not in idx_t18)
        except Exception as e:
            check("T18 app toujours blanche", False, str(e)[:140])

        # ── T19 : semaines ISO et fin d'annee (S53 deborde sur janvier 2027) ──
        import re as _re2
        for iso_date, expected_week in (("2026-12-31T10:00:00", 53), ("2027-01-01T10:00:00", 53),
                                        ("2027-01-03T23:30:00", 53), ("2027-01-04T08:00:00", 1)):
            try:
                ctxy = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
                ctxy.route("**/*open-meteo.com/**", lambda r: r.abort())
                py_ = ctxy.new_page()
                errs_y = []
                py_.on("pageerror", lambda e: errs_y.append(str(e)[:120]))
                py_.clock.install(time=iso_date)
                py_.goto(HTML, wait_until="load", timeout=20000)
                py_.wait_for_function("typeof showTab==='function'&&!document.getElementById('boot-load')", timeout=10000)
                py_.wait_for_timeout(600)
                py_.evaluate("var o=document.getElementById('rwoverlay');if(o)o.style.display='none';")
                wk = py_.evaluate("isoWeek(new Date())")
                bad_y = []
                for v in ("accueil", "plan", "cockpit", "palmares"):
                    py_.evaluate(f"showTab('{v}')")
                    py_.wait_for_timeout(300)
                    txt = py_.evaluate(f"document.getElementById('vue-{v}').innerText")
                    if _re2.search(r"NaN|undefined|Infinity", txt):
                        bad_y.append(v)
                check(f"T19 {iso_date[:10]} : semaine ISO {expected_week}, 4 vues sans NaN ni erreur",
                      wk == expected_week and not bad_y and not errs_y, f"semaine={wk} vues={bad_y} erreurs={errs_y[:2]}")
                ctxy.close()
            except Exception as e:
                check(f"T19 {iso_date[:10]}", False, str(e)[:120])

        # ── T20 : le Cockpit affiche ce que les donnees brutes donnent (debugCockpit) ──
        # Recalcule a part chaque serie (volume, charge, D+, cadence, ACWR, allure facile, zones FC,
        # fatigue) et compare a la valeur affichee. Ne couvre pas la fraicheur des donnees (alertes).
        try:
            pd = b.new_page(viewport={"width": 390, "height": 844})
            pd.goto(HTML, wait_until="load", timeout=20000)
            pd.wait_for_timeout(1200)
            pd.evaluate("showTab('cockpit')")
            pd.wait_for_timeout(500)
            dbg = pd.evaluate("debugCockpit()")
            ec = dbg.get("ecarts", [])
            check("T20 Cockpit : valeurs affichees = recalcul independant (%d controles)" % len(dbg.get("controles", [])),
                  dbg.get("ok") is True,
                  "; ".join("%s: affiche %s, attendu %s" % (e["nom"], e["affiche"], e["attendu"]) for e in ec[:3]))
            pd.close()
        except Exception as e:
            check("T20 debugCockpit", False, str(e)[:120])

        # ── T21 : textes charges a la demande (data/textes.json) ──
        # Pas lus au demarrage ; une fiche seance, une fiche semaine et un Rewind affichent leur texte.
        try:
            D = json.load(open(DATA_JSON, encoding="utf-8"))
            sem = max(s["num"] for s in D["SEMAINES"] if s.get("revue"))
            wk = str(sem)
            se = next(x for x in D["SBW"][wk] if (x.get("realise") or {}).get("revue"))
            rw = D["REWINDS"][-1]["id"]
            pt = b.new_page(viewport={"width": 390, "height": 844})
            vus = []
            pt.on("request", lambda r: vus.append(r.url))
            pt.goto(HTML, wait_until="load", timeout=20000)
            pt.wait_for_timeout(1200)
            check("T21 textes.json non charge au demarrage", not any("textes.json" in u for u in vus),
                  str([u for u in vus if "textes" in u])[:120])
            pt.evaluate(f"ouvrirSeance({sem},{json.dumps(se['id'])})")
            pt.wait_for_timeout(800)
            txt = pt.evaluate("[...document.querySelectorAll('.rev-coach')].map(e=>e.innerHTML).join('')")
            check(f"T21 fiche S{sem}-{se['id']} : revue affichee apres chargement",
                  len(txt) > 50 and txt != "—", txt[:80])
            pt.evaluate(f"ouvrirSemaine({sem})")
            pt.wait_for_timeout(600)
            body = pt.evaluate("document.body.textContent")
            check(f"T21 fiche semaine {sem} : revue presente, pas de placeholder",
                  "Revue de la semaine à venir" not in body, "placeholder affiche")
            pt.evaluate(f"rwOpen('{rw}')")
            pt.wait_for_timeout(500)
            check(f"T21 Rewind {rw} s'ouvre avec ses slides",
                  pt.evaluate("!!document.querySelector('#rwoverlay.on') && rwCur && rwCur.slides.length>0") is True)
            pt.close()
        except Exception as e:
            check("T21 textes a la demande", False, str(e)[:120])

        # ── T22 : systeme de mouvement (P3) ──
        # Avec transitions de vue, sans l'API (iOS < 18) et sous « reduire les animations » :
        # l'app change d'onglet, ouvre et ferme une fiche, ne laisse aucun graphe masque, ne casse rien.
        def page_mvt(reduce=False, sans_vt=False):
            ctx = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block",
                                reduced_motion="reduce" if reduce else "no-preference")
            if sans_vt:
                ctx.add_init_script("delete Document.prototype.startViewTransition;")
            ctx.add_init_script("""window.__vt=0;(function(){var o=Document.prototype.startViewTransition;
                if(o)Document.prototype.startViewTransition=function(){window.__vt++;return o.apply(this,arguments);};})();""")
            pg = ctx.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
            pg.goto(HTML, wait_until="load", timeout=20000)
            pg.wait_for_function("typeof showTab==='function'&&!document.getElementById('boot-load')", timeout=10000)
            pg.wait_for_timeout(900)
            return ctx, pg, errs

        try:
            ctx, pm, errs = page_mvt()
            pm.click("#tab-cockpit")
            pm.wait_for_timeout(700)
            # les graphes du Cockpit sont dans des zones repliees : on les ouvre comme l'utilisateur
            pm.evaluate("[1,2,3].forEach(n=>{const b=document.querySelector('[onclick=\"_ckZone('+n+',this)\"]');if(b)b.click();})")
            pm.evaluate("document.querySelectorAll('[onclick=\"_ckToggleSec(this)\"]').forEach(b=>b.click())")
            pm.evaluate("window.scrollTo(0,0)")
            st = pm.evaluate("""({vt:window.__vt,vue:document.getElementById('vue-cockpit').style.display,
                cur:document.getElementById('tab-cockpit').getAttribute('aria-current'),
                attr:document.documentElement.dataset.vt||'',nom:getComputedStyle(document.getElementById('botbar')).viewTransitionName})""")
            check("T22 onglet par la barre : transition de vue, puis etat propre",
                  st["vt"] == 1 and st["vue"] == "block" and st["cur"] == "page" and st["attr"] == "" and st["nom"] in ("none", ""), str(st))
            # graphes : on parcourt le Cockpit, aucun graphe visible ne reste masque
            for _ in range(14):
                pm.mouse.wheel(0, 500)
                pm.wait_for_timeout(120)
            pm.wait_for_timeout(1100)
            gr = pm.evaluate("""(()=>{const v=[...document.querySelectorAll('#vue-cockpit svg')].filter(s=>{const r=s.getBoundingClientRect();return r.width>0&&r.height>0;});
                return {traces:v.filter(s=>s.dataset.trace==='fait').length,masques:v.filter(s=>s.classList.contains('tr-wait')&&s.dataset.trace==='fait').length,
                        lignes:[...document.querySelectorAll('#vue-cockpit svg[data-trace=fait] .tr-l')].filter(p=>getComputedStyle(p).opacity!=='1').length};})()""")
            check("T22 graphes du Cockpit tracés puis affichés en entier", gr["traces"] >= 3 and gr["masques"] == 0 and gr["lignes"] == 0, str(gr))
            # barre d'onglets : cachee en descendant, revient en remontant
            pm.evaluate("window.scrollTo(0,0)")
            pm.wait_for_timeout(1600)
            pm.mouse.wheel(0, 700)
            pm.wait_for_timeout(400)
            cache = pm.evaluate("document.getElementById('botbar').classList.contains('bb-cache')")
            pm.mouse.wheel(0, -260)
            pm.wait_for_timeout(400)
            revient = not pm.evaluate("document.getElementById('botbar').classList.contains('bb-cache')")
            check("T22 barre d'onglets : se retracte en descendant, revient en remontant", cache and revient, f"cachee={cache} revient={revient}")
            # carte -> fiche -> carte
            pm.click("#tab-accueil")
            pm.wait_for_timeout(800)
            avant = pm.evaluate("window.__vt")
            pm.click(".ac-pro")
            pm.wait_for_timeout(900)
            ouv = pm.evaluate("""({o:document.getElementById('overlay').classList.contains('ouverte'),n:document.getElementById('contenu').innerHTML.length,
                noms:[...document.querySelectorAll('[style*=view-transition-name]')].filter(e=>e.style.viewTransitionName&&e.style.viewTransitionName!=='none').length})""")
            pm.click(".btn-close-round")
            pm.wait_for_timeout(900)
            fer = pm.evaluate("""({o:document.getElementById('overlay').classList.contains('ouverte'),vt:window.__vt,
                noms:[...document.querySelectorAll('[style*=view-transition-name]')].filter(e=>e.style.viewTransitionName&&e.style.viewTransitionName!=='none').length,
                sans:document.getElementById('overlay').classList.contains('vt-sans'),fixe:document.body.style.position})""")
            check("T22 carte de séance -> fiche -> carte (transitions de vue)",
                  ouv["o"] and ouv["n"] > 200 and ouv["noms"] == 0 and not fer["o"] and fer["vt"] == avant + 2
                  and fer["noms"] == 0 and not fer["sans"] and fer["fixe"] == "", f"{ouv} {fer}")
            # chiffres cles : la valeur finale est celle que l'app ecrit
            pm.wait_for_timeout(300)
            v1 = pm.evaluate("[...document.querySelectorAll('.ac-forme-v,.ac-jn')].map(e=>e.textContent)")
            pm.evaluate("renderHeader()")
            v2 = pm.evaluate("[...document.querySelectorAll('.ac-forme-v,.ac-jn')].map(e=>e.textContent)")
            check("T22 chiffres clés : valeur finale exacte après le comptage", len(v1) >= 1 and v1 == v2, f"{v1} / {v2}")
            # profil de Nice : se dessine au scroll, legende calculee
            pm.evaluate("ouvrirDossier('nice')")
            pm.wait_for_timeout(700)
            pf = pm.evaluate("""(()=>{const l=document.querySelector('.dos-prof .dp-line'),c=document.querySelector('.dos-prof-cap');
                return {l:!!l&&l.getAttribute('pathLength')==='1',anim:l?getComputedStyle(l).animationName:'',cap:c?c.textContent:''};})()""")
            check("T22 profil de Nice : tracé au scroll, légende juste", pf["l"] and "dpTrace" in pf["anim"] and "897" not in pf["cap"] and "km" in pf["cap"], str(pf))
            pm.evaluate("fermer()")
            check("T22 aucune erreur JS (transitions de vue)", not errs, "; ".join(errs[:2]))
            ctx.close()
        except Exception as e:
            check("T22 mouvement (transitions de vue)", False, str(e)[:160])

        try:
            ctx, pm, errs = page_mvt()
            pm.click("#tab-plan")
            pm.wait_for_timeout(150)
            pm.mouse.click(*pm.evaluate("(()=>{const r=document.getElementById('tab-cockpit').getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2];})()"))
            pm.wait_for_timeout(900)
            apres_tap = pm.evaluate("_ongletActif()")
            pm.evaluate("goTab('accueil');goTab('plan');goTab('palmares')")
            pm.wait_for_timeout(900)
            fin = pm.evaluate("""({v:_ongletActif(),attr:document.documentElement.dataset.vt||''})""")
            check("T22 toucher pendant une transition : pris en compte ; trois onglets d'affilée : le dernier gagne, sans erreur",
                  apres_tap == "cockpit" and fin["v"] == "palmares" and fin["attr"] == "" and not errs, f"tap={apres_tap} {fin} {errs[:2]}")
            ctx.close()
        except Exception as e:
            check("T22 toucher pendant une transition", False, str(e)[:160])

        try:
            ctx, pm, errs = page_mvt(sans_vt=True)
            pm.click("#tab-plan")
            st = pm.evaluate("({vue:document.getElementById('vue-plan').style.display,vin:document.getElementById('vue-plan').classList.contains('vue-in'),vt:window.__vt})")
            pm.click(".sem-carte")
            pm.wait_for_timeout(500)
            o = pm.evaluate("document.getElementById('overlay').classList.contains('ouverte')")
            pm.click(".btn-close-round")
            pm.wait_for_timeout(500)
            f = pm.evaluate("document.getElementById('overlay').classList.contains('ouverte')")
            check("T22 sans transitions de vue (iOS < 18) : onglet immédiat avec repli CSS, fiche de semaine",
                  st["vue"] == "block" and st["vin"] and st["vt"] == 0 and o and not f and not errs, f"{st} ouverte={o} fermee={not f} {errs[:1]}")
            ctx.close()
        except Exception as e:
            check("T22 sans transitions de vue", False, str(e)[:160])

        try:
            ctx, pm, errs = page_mvt(reduce=True)
            pm.click("#tab-cockpit")
            st = pm.evaluate("({vt:window.__vt,vue:document.getElementById('vue-cockpit').style.display})")
            pm.wait_for_timeout(600)
            for _ in range(6):
                pm.mouse.wheel(0, 600)
                pm.wait_for_timeout(120)
            pm.wait_for_timeout(300)
            r = pm.evaluate("""({cache:document.getElementById('botbar').classList.contains('bb-cache'),
                masques:document.querySelectorAll('svg.tr-wait').length,
                anims:document.getAnimations().filter(a=>a.playState==='running'&&!(a.effect&&a.effect.getComputedTiming().iterations===Infinity)).length})""")
            check("T22 réduire les animations : aucune transition, barre fixe, graphes jamais masqués",
                  st["vt"] == 0 and st["vue"] == "block" and not r["cache"] and r["masques"] == 0 and not errs, f"{st} {r} {errs[:1]}")
            ctx.close()
        except Exception as e:
            check("T22 réduire les animations", False, str(e)[:160])

        # ── T23 : Rewind de séance (P4 lot 1) — annonce, bouton de la fiche, 9 images, Où j'en suis ──
        def rewind_parcours(pm):
            pm.evaluate("var o=document.getElementById('rwoverlay');if(o)o.classList.remove('on');")
            ann = pm.evaluate("(function(){var c=document.getElementById('ac-coach');return !!c&&!c.hidden&&/Le coach a analys/.test(c.innerText)&&!!c.querySelector('.ac-btn-o');})()")
            der = pm.evaluate("REWIND_SEANCE.map(c=>{const [w,i]=c.split('-');const s=SEANCES_BY_WEEK[w].find(x=>String(x.id)===i);return [s.date+'|'+c,c];}).sort().pop()[1]")
            w, i = der.split("-")
            pm.evaluate(f"ouvrirSeance('{w}',{i})")
            pm.wait_for_selector("#contenu .fs-revoir", timeout=5000)  # bouton « Revoir ma séance » de la fiche faite
            pm.click("#contenu .fs-revoir")
            pm.wait_for_selector(".rs:not([hidden]) .rs-sl", timeout=5000)
            labels, ko = [], 0
            for _ in range(9):
                labels.append(pm.evaluate("document.querySelector('.rs-sl:last-child').getAttribute('aria-label')"))
                ko += pm.evaluate("document.querySelector('.rs-sl:last-child').innerText.includes('pas pu être calculée')")
                pm.keyboard.press("ArrowRight")
                pm.wait_for_timeout(150)
            ferme = pm.evaluate("document.querySelector('.rs').hidden")
            vu = pm.evaluate("localStorage.getItem('rs_vu')")
            return ann, labels, ko, ferme, vu == der

        try:
            ctx, pm, errs = page_mvt()
            ann, labels, ko, ferme, vu = rewind_parcours(pm)
            check("T23 Rewind de séance : carte du coach sur l'Accueil, bouton de la fiche, 9 images calculées, fermeture, carte toujours là",
                  ann and len(set(labels)) == 9 and ko == 0 and ferme and vu and pm.evaluate("!document.getElementById('ac-coach').hidden") and not errs,
                  f"annonce={ann} images={len(set(labels))} ko={ko} ferme={ferme} vu={vu} {errs[:1]}")
            pm.evaluate("rsOuvrir('44-2',0)")
            pm.wait_for_timeout(5300)
            img = pm.evaluate("document.querySelector('.rs-sl:last-child').getAttribute('aria-label')")
            pm.keyboard.press("Escape")
            pm.evaluate("rsOuvrir('44-2',7)")
            pm.wait_for_timeout(6000)
            coach = pm.evaluate("document.querySelector('.rs-sl:last-child').getAttribute('aria-label')")
            check("T23 défilement automatique ; l'analyse du coach attend « Continuer »",
                  img.startswith("2 sur 9") and coach.startswith("8 sur 9"), f"{img} / {coach}")
            dock = pm.evaluate("""(()=>{const s=document.querySelector('.rs-sl:last-child'),d=s.querySelector('.rs-defile'),b=s.querySelector('.rs-dock .rs-btn:not(.second)');
                return {hors:!!(b&&d)&&!d.contains(b),visible:!!b&&b.getBoundingClientRect().bottom<=innerHeight}})()""")
            pm.click(".rs-sl:last-child .rs-dock .rs-btn:not(.second)")
            pm.wait_for_timeout(500)
            neuf = pm.evaluate("document.querySelector('.rs-sl:last-child').getAttribute('aria-label')")
            check("T31 analyse du coach : « Continuer » hors de la zone qui défile, visible sans défiler, mène à l'image 9",
                  dock["hors"] and dock["visible"] and neuf.startswith("9 sur 9"), f"{dock} {neuf}")
            pm.keyboard.press("Escape")
            pm.evaluate("rsOuvrir('44-2',4)")
            pm.wait_for_selector(".rs-sl:last-child .rs-fc", timeout=5000)
            clair = pm.evaluate("""(()=>{const lum=c=>{const m=(c||'').match(/[0-9.]+/g);if(!m)return 1;return (0.2126*m[0]+0.7152*m[1]+0.0722*m[2])/255;};
                return [lum(getComputedStyle(document.querySelector('.rs-sl:last-child .rs-fc')).stroke)]})()""")
            check("T31 le cœur : courbe de FC lisible sur fond blanc (pas de trait presque blanc)", clair[0] < 0.6, f"luminance {clair}")
            pm.keyboard.press("Escape")
            pm.evaluate("showTab('cockpit')")
            pm.wait_for_selector("#vue-cockpit .ck-z[data-zone='2']", timeout=5000)
            pm.click("#vue-cockpit .ck-z[data-zone='2']")
            pm.wait_for_selector("#ck-ou .ck-ou-btn", timeout=5000)
            pm.click("#ck-ou .ck-ou-btn")
            pm.wait_for_timeout(900)
            ou = pm.evaluate("[...document.querySelectorAll('.rs-ou-carte .rs-verd')].map(v=>v.innerText.trim())")
            check("T23 Où j'en suis : 5 courbes, chacune avec un verdict",
                  len(ou) == 5 and all(v in ("Progresse", "Stable", "Recule", "À confirmer", "En hausse", "En baisse") for v in ou) and not errs, f"{ou} {errs[:1]}")
            ctx.close()
        except Exception as e:
            check("T23 Rewind de séance", False, str(e)[:160])

        try:
            ctx, pm, errs = page_mvt(sans_vt=True)
            ann, labels, ko, ferme, vu = rewind_parcours(pm)
            check("T23 Rewind sans transitions de vue (iOS < 18)", len(set(labels)) == 9 and ko == 0 and ferme and not errs,
                  f"images={len(set(labels))} ko={ko} ferme={ferme} {errs[:1]}")
            ctx.close()
        except Exception as e:
            check("T23 Rewind sans transitions de vue", False, str(e)[:160])

        try:
            ctx, pm, errs = page_mvt(reduce=True)
            pm.evaluate("rsOuvrir('44-2',0)")
            pm.wait_for_selector(".rs:not([hidden]) .rs-sl", timeout=5000)
            pm.wait_for_timeout(5600)
            r = pm.evaluate("""({img:document.querySelector('.rs-sl:last-child').getAttribute('aria-label'),
                anims:document.getAnimations().filter(a=>a.playState==='running'&&a.effect&&a.effect.target&&document.querySelector('.rs').contains(a.effect.target)).length,
                cachee:[...document.querySelectorAll('.rs-sl:last-child *')].filter(e=>getComputedStyle(e).opacity==='0').length})""")
            pm.keyboard.press("Escape")
            ann, labels, ko, ferme, vu = rewind_parcours(pm)
            check("T23 Rewind sous réduire les animations : pas de défilement ni d'animation, rien de masqué",
                  r["img"].startswith("1 sur 9") and r["anims"] == 0 and r["cachee"] == 0 and len(set(labels)) == 9 and ko == 0 and not errs,
                  f"{r} images={len(set(labels))} {errs[:1]}")
            ctx.close()
        except Exception as e:
            check("T23 Rewind sous réduire les animations", False, str(e)[:160])

        # ── T32 : fond de carte du tracé (build 283) : avec tuiles, sans accès, mode avion, réduire les animations ──
        import math
        import re as _re
        TUILE_URL = _re.compile(r"^https://tile\.openstreetmap\.org/(\d+)/(\d+)/(\d+)\.png$")

        def page_carte(mode, reduce=False):
            ctx = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block",
                                reduced_motion="reduce" if reduce else "no-preference")
            if mode == "avion":  # hors connexion : l'app ne doit même pas demander de tuile
                ctx.add_init_script("Object.defineProperty(navigator,'onLine',{get:()=>false});")
            urls = []

            def tuile(r):
                if mode == "echec":
                    r.abort()
                    return
                urls.append(r.request.url)
                m = TUILE_URL.match(r.request.url)
                z, x, y = m.groups() if m else ("?", "?", "?")
                r.fulfill(status=200, content_type="image/svg+xml",
                          body=(f'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256"><rect width="256" height="256" fill="#e9ecee"/>'
                                f'<text x="16" y="40" font-size="28">{z}/{x}/{y}</text></svg>').encode())
            ctx.route("**/tile.openstreetmap.org/**", tuile)
            pg = ctx.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
            pg.goto(HTML, wait_until="load", timeout=20000)
            pg.wait_for_function("typeof showTab==='function'&&!document.getElementById('boot-load')", timeout=10000)
            pg.wait_for_timeout(600)
            pg.evaluate("var o=document.getElementById('rwoverlay');if(o)o.classList.remove('on');")
            pg.evaluate("rsOuvrir('44-5',1)")
            pg.wait_for_selector(".rs-sl:last-child .rs-tracecarte svg", timeout=6000)
            pg.wait_for_timeout(900)
            return ctx, pg, errs, urls

        LIRE_CARTE = """(()=>{const c=document.querySelector('.rs-sl:last-child .rs-tracecarte'),a=c.querySelector('.rs-attrib');
            return {imgs:[...c.querySelectorAll('.rs-fond img')].map(i=>({src:i.getAttribute('src'),left:parseFloat(i.style.left),top:parseFloat(i.style.top),w:parseFloat(i.style.width)})),
              attrib:getComputedStyle(a).display!=='none'?a.innerText.trim():null,attribPx:parseFloat(getComputedStyle(a).fontSize),href:a.querySelector('a').href,
              casing:c.querySelector('svg > path').getAttribute('d'),lignes:c.querySelectorAll('svg g > line').length,
              box:c.getBoundingClientRect().width,legende:!!document.querySelector('.rs-sl:last-child .rs-legende'),
              cap:document.querySelector('.rs-sl:last-child .rs-cap').innerText,aria:c.querySelector('svg').getAttribute('aria-label')}})()"""
        try:
            rw = json.load(open(os.path.join(SITE, "data", "rewind-44-5.json"), encoding="utf-8"))
            ctx, pc, errs, urls = page_carte("tuiles")
            r = pc.evaluate(LIRE_CARTE)
            ok_urls = bool(urls) and all(TUILE_URL.match(u) for u in urls)
            # alignement : un point du tracé retombe, au centième de pixel près, là où la tuile Web Mercator le place
            R_ = 6378137.0
            i = len(rw["trace"]) // 2
            mx, my = rw["ancrage"]["x"] + rw["trace"][i][0], rw["ancrage"]["y"] + rw["trace"][i][1]
            lng = math.degrees(mx / R_)
            lat = math.degrees(2 * math.atan(math.exp(my / R_)) - math.pi / 2)
            nums = [float(v) for v in _re.findall(r"-?\d+\.?\d*", r["casing"])]
            px, py = nums[2 * i], nums[2 * i + 1]
            ecart = None
            for im in r["imgs"]:
                z, tx, ty = (int(v) for v in TUILE_URL.match(im["src"]).groups())
                n = 2 ** z
                fx = (lng + 180) / 360 * n
                fy = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
                if int(fx) == tx and int(fy) == ty:
                    X = (im["left"] + (fx - tx) * im["w"]) * 3.2
                    Y = (im["top"] + (fy - ty) * im["w"]) * 3.2
                    ecart = max(abs(X - px), abs(Y - py))
            check("T32 fond de carte : tuiles OpenStreetMap demandées, posées en Web Mercator (le tracé tombe sur la tuile, écart < 0,2 px de 320)",
                  len(r["imgs"]) >= 2 and ok_urls and ecart is not None and ecart < 0.2 and len(urls) == len(r["imgs"]) and not errs,
                  f"imgs={len(r['imgs'])} urls={len(urls)} ok_urls={ok_urls} ecart={ecart} {errs[:1]}")
            check("T32 fond de carte : attribution « © OpenStreetMap contributors » (lien openstreetmap.org/copyright) visible en petit (12 px minimum), tracé coloré par-dessus, légende et mention des 300 m",
                  r["attrib"] == "© OpenStreetMap contributors" and r["href"] == "https://www.openstreetmap.org/copyright" and r["attribPx"] >= 12 and r["lignes"] > 100 and r["legende"]
                  and "300 premiers" in r["cap"] and "300" in r["aria"], f"{r['attrib']} {r['attribPx']} lignes={r['lignes']} {r['cap'][:60]}")
            sw = open(os.path.join(SITE, "sw.js"), encoding="utf-8").read()
            check("T32 pas de tuiles dans le pré-cache ; le service worker ne prend pas les requêtes d'un autre domaine",
                  "openstreetmap" not in sw and "url.origin!==location.origin" in sw.replace(" ", ""), "")
            ctx.close()
        except Exception as e:
            check("T32 fond de carte avec tuiles", False, str(e)[:200])

        try:  # les cartes de l'analyse du coach ne partagent aucun style avec le fond de carte du tracé (build 285)
            ctx = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            ctx.route("**/tile.openstreetmap.org/**", lambda r: r.abort())
            pc = ctx.new_page()
            pc.goto(HTML, wait_until="load", timeout=20000)
            pc.wait_for_function("typeof showTab==='function'&&!document.getElementById('boot-load')", timeout=10000)
            pc.wait_for_timeout(600)
            pc.evaluate("var o=document.getElementById('rwoverlay');if(o)o.classList.remove('on');")
            pc.evaluate("rsOuvrir('44-5',7)")
            pc.wait_for_selector(".rs-carte.verdict", timeout=6000)
            pc.wait_for_timeout(500)
            r = pc.evaluate("""(()=>{const c=document.querySelector('.rs-carte.verdict'),s=getComputedStyle(c),r=c.getBoundingClientRect();
                return {ar:s.aspectRatio,ov:s.overflow,w:r.width,h:r.height,sh:c.scrollHeight}})()""")
            check("T32 cartes du coach : hauteur naturelle (ni carrées ni tronquées)",
                  r["ar"] == "auto" and r["ov"] == "visible" and r["h"] < r["w"] * 0.8 and r["sh"] <= r["h"] + 1, str(r))
            ctx.close()
        except Exception as e:
            check("T32 cartes du coach", False, str(e)[:200])

        try:
            ctx, pc, errs, urls = page_carte("echec")
            r = pc.evaluate(LIRE_CARTE)
            check("T32 sans accès aux tuiles (réseau coupé) : le tracé seul, ni case vide ni image cassée, pas d'attribution, pas d'erreur",
                  len(r["imgs"]) == 0 and r["attrib"] is None and r["lignes"] > 100 and r["box"] > 200 and not errs,
                  f"imgs={len(r['imgs'])} attrib={r['attrib']} lignes={r['lignes']} {errs[:1]}")
            ctx.close()
            ctx, pc, errs, urls = page_carte("avion")
            r = pc.evaluate(LIRE_CARTE)
            check("T32 hors connexion (mode avion) : aucune tuile demandée, le tracé seul, sans erreur",
                  len(urls) == 0 and len(r["imgs"]) == 0 and r["attrib"] is None and r["lignes"] > 100 and not errs,
                  f"urls={len(urls)} imgs={len(r['imgs'])} attrib={r['attrib']} {errs[:1]}")
            ctx.close()
        except Exception as e:
            check("T32 fond de carte sans tuiles", False, str(e)[:200])

        try:
            ctx, pc, errs, urls = page_carte("tuiles", reduce=True)
            r = pc.evaluate(LIRE_CARTE)
            anim = pc.evaluate("""({anims:document.getAnimations().filter(a=>a.playState==='running'&&a.effect&&a.effect.target&&document.querySelector('.rs').contains(a.effect.target)).length,
                cachee:[...document.querySelectorAll('.rs-sl:last-child *')].filter(e=>getComputedStyle(e).opacity==='0').length})""")
            check("T32 fond de carte sous réduire les animations : tuiles affichées d'un coup, aucune animation, rien de masqué",
                  len(r["imgs"]) >= 2 and r["attrib"] and anim["anims"] == 0 and anim["cachee"] == 0 and not errs, f"{len(r['imgs'])} {anim} {errs[:1]}")
            ctx.close()
        except Exception as e:
            check("T32 fond de carte sous réduire les animations", False, str(e)[:200])

        # ── T24 : direction blanc et orange (lot 5) : police des chiffres embarquee, jetons orange ──
        try:
            ctxf = b.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            ctxf.route("**/*open-meteo.com/**", lambda r: r.abort())
            pf = ctxf.new_page()
            pf.goto(HTML, wait_until="load", timeout=20000)
            pf.wait_for_function("typeof showTab==='function'&&!document.getElementById('boot-load')", timeout=10000)
            pf.evaluate("document.fonts.load('700 28px \"Barlow Semi Condensed\"')")
            pf.wait_for_function("document.fonts.check('700 28px \"Barlow Semi Condensed\"')", timeout=5000)
            prim = pf.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--primary').trim().toLowerCase()")
            check("T24 police des chiffres chargee depuis l'app (hors ligne) et orange primaire",
                  prim == "#f4561d", f"--primary={prim}")
            sw = open(os.path.join(SITE, "sw.js"), encoding="utf-8").read()
            check("T24 polices dans le pre-cache du service worker",
                  all(f"./src/fonts/barlow-semi-condensed-latin-{w}-normal.woff2" in sw for w in (700, 800)))
            # Accueil (lot 5, PR 2) : l'ordre de la maquette, pas de compteur de records, aucun emoji
            pf.evaluate("showTab('accueil')")
            pf.wait_for_timeout(300)
            ac = pf.evaluate("""(function(){var v=document.getElementById('vue-accueil'),ids=[...v.querySelectorAll('.ac > *')].map(function(e){
                return e.id||e.className.split(' ').filter(function(c){return /^ac-(tete|coach|pro|forme|carte)$/.test(c)||c==='forme-detail';}).pop()||e.tagName;});
              return {ordre:ids.join(','),records:/records/i.test(v.innerText),emoji:/\\p{Extended_Pictographic}/u.test(v.innerText),
                semaine:v.querySelectorAll('.ac-jour').length,jn:(v.querySelector('.ac-jn .cnt')||{}).textContent};})()""")
            check("T25 Accueil : en-tête, analyse du coach, prochaine séance, météo, forme, semaine (7 jours), courses, année ; sans records ni emoji",
                  ac["ordre"].startswith("ac-tete,ac-coach,ac-pro,wdg-meteo-slot,ac-forme,forme-detail,ac-carte,ac-carte,ac-carte")
                  and not ac["records"] and not ac["emoji"] and ac["semaine"] == 7 and (ac["jn"] or "").isdigit(), str(ac))
            # Fiche d'une seance faite (lot 5, PR 3) : chiffres, analyse du coach, trace et zones, km par km, seance prevue
            pf.evaluate("ouvrirSeance('44',3)")
            pf.wait_for_selector("#fs-trace:not([hidden]) svg", timeout=6000)
            pf.wait_for_selector("#fs-zones:not([hidden]) .fs-zbar", timeout=6000)
            fi = pf.evaluate("""(function(){var f=document.querySelector('#contenu .fs');return {
                chif:f.querySelectorAll('.fs-chif .fs-st').length, pvr:f.querySelectorAll('.fs-pvr-r[role=row]').length-1,
                coach:['Le verdict','Ce qui est bien','À corriger','Pour la suite'].every(function(t){return f.innerText.indexOf(t)>=0;}),
                km:f.querySelectorAll('#fs-km .fs-km-l .fs-km-r').length, bande:!!f.querySelector('#fs-km .fs-bande'),
                segs:f.querySelectorAll('#fs-trace line').length, prevue:!!f.querySelector('.fs-struct li'),
                vide:/NaN|undefined|Infinity/.test(f.innerText), emoji:/\\p{Extended_Pictographic}/u.test(f.innerText.replace(/[\\s\\S]*Lire la revue compl[èe]te/,''))};})()""")
            check("T26 fiche d'une séance faite : chiffres, prévu face au réalisé, analyse en 4 parties, tracé coloré, zones, km par km sur la bande de cible, séance prévue",
                  fi["chif"] == 6 and fi["pvr"] == 3 and fi["coach"] and fi["km"] >= 10 and fi["bande"] and fi["segs"] > 50
                  and fi["prevue"] and not fi["vide"], str(fi))
            pf.evaluate("fermer()")
            # Seances, fiche semaine, fiche d'une seance a faire (lot 5, partie B) : sans couleur de phase ni emoji dans l'interface
            pf.evaluate("showTab('plan')")
            pf.wait_for_timeout(300)
            pl = pf.evaluate(CHROME_JS + """(function(){var v=document.getElementById('vue-plan');return {cartes:v.querySelectorAll('.sem-carte').length,
                semaines:SEMAINES.length,puces:v.querySelectorAll('.phase-puce').length,cur:v.querySelectorAll('.sem-carte.sem-cur').length,emo:chrome(v)};})()""")
            pf.evaluate("ouvrirSemaine(44)")
            pf.wait_for_timeout(500)
            sw = pf.evaluate(CHROME_JS + """(function(){var c=document.getElementById('contenu');return {fsw:!!c.querySelector('.fsw'),
                ses:c.querySelectorAll('.seance-carte').length,attendu:(SEANCES_BY_WEEK[44]||[]).length,emo:chrome(c)};})()""")
            pf.evaluate("fermer()")
            cle = pf.evaluate("(function(){var t=new Date().toISOString().slice(0,10);for(var w in SEANCES_BY_WEEK){var a=SEANCES_BY_WEEK[w];for(var i=0;i<a.length;i++){var r=a[i].realise||{};if((!r.statut||r.statut==='a_faire')&&a[i].date>=t&&a[i].struct&&a[i].struct.length)return [w,a[i].id];}}return null;})()")
            fp = {"cle": cle}
            if cle:
                pf.evaluate(f"ouvrirSeance('{cle[0]}',{cle[1]})")
                pf.wait_for_timeout(500)
                fp = pf.evaluate(CHROME_JS + """(function(){var c=document.getElementById('contenu'),f=c.querySelector('.fp');return {fp:!!f,
                    titres:f?[...f.querySelectorAll('h3')].map(function(h){return h.textContent;}):[],log:!!c.querySelector('#logform'),emo:chrome(c),
                    vide:/NaN|undefined|Infinity/.test(c.innerText)};})()""")
                pf.evaluate("fermer()")
            check("T27 Séances, fiche semaine, fiche à faire : cartes sans couleur de phase, semaine en cours marquée, sections de la fiche, aucun emoji dans l'interface",
                  pl["cartes"] == pl["semaines"] and pl["puces"] == 0 and pl["cur"] <= 1 and not pl["emo"]
                  and sw["fsw"] and sw["ses"] == sw["attendu"] and not sw["emo"]
                  and fp.get("fp") and "Le réalisé" in fp.get("titres", []) and "Le déroulé" in fp.get("titres", []) and fp.get("log")
                  and not fp.get("emo") and not fp.get("vide"), f"{pl} {sw} {fp}")
            # Cockpit (lot 5, partie B) : 4 onglets, Aujourd'hui comme la maquette, Ou j'en suis en ligne, Records, tableau de bord dans Analyse
            pf.evaluate("showTab('cockpit')")
            pf.wait_for_selector("#ck-ou-liste .ck-ou-r", state="attached", timeout=8000)
            ck = pf.evaluate("(function(){" + CHROME_JS + """var v=document.getElementById('vue-cockpit'),z=function(n){return v.querySelector('.ck-zone[data-zone="'+n+'"]');};
                return {onglets:[...v.querySelectorAll('.ck-z')].map(function(b){return b.textContent;}),sel:v.querySelectorAll('.ck-z[aria-selected="true"]').length,
                  ind:z(1).querySelectorAll('.ckf-r').length,puce:(document.getElementById('ckc-puce')||{}).textContent||'',pt:(document.getElementById('ckc-pt')||{style:{}}).style.left||'',
                  acwr:(document.getElementById('ck-acwr-val')||{}).dataset.fin||'',vo2:!!z(1).querySelector('#vo2-val'),barres:z(1).querySelectorAll('#ck-sem-barres rect').length,
                  ou:z(2).querySelectorAll('.ck-ou-r').length,rec:z(4).querySelectorAll('.ckr-r').length,recAtt:(typeof RECORDS_PERF!=='undefined'?RECORDS_PERF.length:0),
                  dash:!!z(3).querySelector('#dash-contenu'),emo:chrome(v),vide:/NaN|undefined|Infinity/.test(v.innerText)};})()""")
            check("T28 Cockpit : 4 onglets, forme et ses 4 indicateurs, charge (zone et repère), VO2max, 12 semaines, 5 courbes « Où j'en suis », records, tableau de bord dans Analyse, aucun emoji",
                  ck["onglets"] == ["Aujourd'hui", "Progression", "Records", "Analyse"] and ck["sel"] == 1 and ck["ind"] == 4 and ck["puce"] and ck["pt"]
                  and ck["acwr"] and ck["vo2"] and ck["barres"] == 12 and ck["ou"] >= 3 and ck["rec"] == ck["recAtt"] > 0 and ck["dash"]
                  and not ck["emo"] and not ck["vide"], str(ck))
            # Courses, dossier de course, Rewind de semaine, saison en chiffres (lot 5, partie B) : fond blanc, aucun emoji d'interface
            pf.evaluate("showTab('palmares')")
            pf.wait_for_timeout(300)
            cr = pf.evaluate("(function(){" + CHROME_JS + """var v=document.getElementById('vue-palmares');return {titre:(v.querySelector('.vue-titre')||{}).textContent,
                passees:v.querySelectorAll('.crs-p').length,attendu:(typeof PALMARES!=='undefined'?PALMARES.length:0),emo:chrome(v)};})()""")
            pf.evaluate("ouvrirDossier('nice')")
            pf.wait_for_timeout(400)
            dos = pf.evaluate("(function(){" + CHROME_JS + """var c=document.getElementById('contenu');return {sec:c.querySelectorAll('.dos .fs-sec').length,emo:chrome(c)};})()""")
            pf.evaluate("fermer()")
            pf.evaluate("rwOpen(REWINDS[REWINDS.length-1].id)")
            pf.wait_for_timeout(300)
            rw = pf.evaluate("""(function(){var c=document.getElementById('rwcard');var bg=getComputedStyle(c).backgroundColor;rwClose();return bg;})()""")
            pf.evaluate("openWrapped()")
            pf.wait_for_timeout(300)
            wr = pf.evaluate("""(function(){var st=document.querySelector('.wr-stage');var r=[getComputedStyle(st).backgroundColor,/\\p{Extended_Pictographic}/u.test(document.getElementById('wrapped-ov').innerText)];_wrappedClose();return r;})()""")
            check("T29 Courses, dossier de course, Rewind de semaine et saison en chiffres : blancs, sans emoji d'interface",
                  cr["titre"] == "Courses" and cr["passees"] == cr["attendu"] and not cr["emo"] and dos["sec"] >= 8 and not dos["emo"]
                  and rw == "rgb(255, 255, 255)" and wr[0] == "rgb(255, 255, 255)" and not wr[1], f"{cr} {dos} {rw} {wr}")
            # Panneaux (lot 5, partie B) : aucun emoji dans les titres, étiquettes, puces et boutons, croix de fermeture présentes
            pf.evaluate("localStorage.setItem('meteo_cache',JSON.stringify({temp:18,app:17,code:2,wind:12,rain:20,precip:.4,tomorrow_max:21,hourly_today:[[18,16],[19,15]],hourly_tomorrow:[[8,12],[9,13]]}))")
            pf.evaluate("showTab('accueil');renderHeader()")
            pan = {}
            ouvertures = [("météo", "_ouvrirMeteo()"), ("records", "_ouvrirRecords()"), ("versions", "openVersionPanel()"),
                          ("aide forme", "openCkHelp('forme')"), ("aide acwr", "openCkHelp('acwr')"), ("aide cadence", "openCkHelp('cad')"),
                          ("théorie", "(function(){for(var w in SEANCES_BY_WEEK){var a=SEANCES_BY_WEEK[w];for(var i=0;i<a.length;i++){if(typeof RICH_THEORY!=='undefined'&&RICH_THEORY[seanceTag(a[i])]){openTheory(w,a[i].id);return;}}}})()"),
                          ("menu séance", "openSM(44,'4')"), ("log rapide", "ouvrirQuickLog(44,4)")]
            for nom, code in ouvertures:
                try:
                    pf.evaluate(code)
                    pf.wait_for_timeout(350)
                    pan[nom] = pf.evaluate("(function(){" + CHROME_JS + "return chrome(document.body);})()")
                except Exception as e:
                    pan[nom] = ["erreur " + str(e)[:60]]
                pf.evaluate("['fermer','closeCkHelp','closeTheory','closeVersionPanel','closeSM','closeQuickLog'].forEach(function(f){try{if(typeof window[f]==='function')window[f]();}catch(e){}})")
                pf.keyboard.press("Escape")
                pf.wait_for_timeout(200)
            vides = pf.evaluate("[...document.querySelectorAll('button')].filter(function(b){return /fermer|close/i.test((b.getAttribute('onclick')||'')+(b.getAttribute('aria-label')||''))&&!(b.textContent||'').trim()&&!b.querySelector('svg');}).length")
            check("T30 panneaux (météo, records, versions, aides, théorie, menu, log rapide) : sans emoji d'interface, croix de fermeture présentes",
                  all(not v for v in pan.values()) and vides == 0, f"{ {k: v for k, v in pan.items() if v} } vides={vides}")
            ctxf.close()
        except Exception as e:
            check("T24 police des chiffres embarquee", False, str(e)[:160])

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
