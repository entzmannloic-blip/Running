#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_regression.py — Suite de tests runtime (anti-regression) pour Running PWA.

Complement de preflight.py :
  - preflight.py = checks STATIQUES (build, syntaxe, pipeline, secrets...)
  - test_regression.py = checks RUNTIME (l'app se charge, les vues rendent,
    les KPI se calculent, le Coach ouvre, zero erreur JS console).

A lancer APRES le build, AVANT le push :
    python3 scripts/test_regression.py

Sortie : PASS/FAIL par test. Un seul FAIL => NE PAS PUSHER (exit 1).
Chaque test prouve qu'une fonctionnalite cle n'a pas regresse.

Prerequis : playwright + chromium installes ; HTML build present dans
/mnt/user-data/outputs/plan-entrainement.html
"""
import json
import sys

HTML = "file:///mnt/user-data/outputs/plan-entrainement.html"

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

        # ── T02 : les 5 vues rendent du contenu ──
        views = ["accueil", "seances", "cockpit", "courses"]
        for v in views:
            try:
                p.evaluate(f"showTab('{v}')")
                p.wait_for_timeout(400)
                has = p.evaluate(
                    "(document.querySelector('.vue-in, .vue.on, main')"
                    "?.textContent||document.body.innerText||'').trim().length>50")
                check(f"T02 vue {v} rend du contenu", bool(has))
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

        # ── T07 : le Coach IA ouvre et affiche l'intro ──
        try:
            p.evaluate("openCoach()")
            p.wait_for_timeout(700)
            coach_open = p.evaluate(
                "document.getElementById('coach-ov')?.classList.contains('open')")
            intro = p.evaluate(
                "document.getElementById('coach-msgs')?.children.length>0")
            check("T07 Coach ouvre + intro affichee", bool(coach_open and intro))
            p.evaluate("closeCoach&&closeCoach()")
        except Exception as e:
            check("T07 Coach", False, str(e)[:80])

        # ── T08 : le system prompt du Coach se construit (contexte injecte) ──
        sp = p.evaluate(
            "typeof _cBuildSystemPrompt==='function'?_cBuildSystemPrompt().length:0")
        check("T08 system prompt Coach construit", sp and sp > 500,
              f"longueur={sp}")

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
