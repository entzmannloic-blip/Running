#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_runtime.py — Audit RUNTIME exhaustif (playwright).

Difference avec test_regression.py (16 tests cibles) : ici on ouvre
SYSTEMATIQUEMENT tout ce qui est ouvrable — les 30 semaines, les 132 seances,
tous les Rewinds, toutes les fenetres Cockpit — et on capture la moindre
erreur JS. Objectif : trouver les bugs qui ne se voient que sur un
chemin precis.
"""
import datetime as _dt
import json
import sys

HTML = "file:///mnt/user-data/outputs/plan-entrainement.html"
DATA = json.load(open("/tmp/data.json", encoding="utf-8"))

ANO = []
def ano(code, msg):
    ANO.append((code, msg))

def run():
    from playwright.sync_api import sync_playwright

    errs = []
    def note(src, txt):
        t = str(txt)[:180]
        if "net::" in t or "open-meteo" in t or "Failed to fetch" in t:
            return
        errs.append(f"[{src}] {t}")

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        p.on("pageerror", lambda e: note("pageerror", e))
        p.on("console", lambda m: note("console", m.text) if m.type == "error" else None)

        p.goto(HTML, wait_until="load", timeout=30000)
        p.wait_for_timeout(1500)
        p.evaluate("var o=document.getElementById('rwoverlay');if(o){o.classList.remove('on');o.style.display='none';}")

        # ═══ 1. TOUTES LES SEMAINES ═══
        print("── 1. Ouverture des 30 semaines ...")
        semaines = [s["num"] for s in DATA["SEMAINES"]]
        for num in semaines:
            before = len(errs)
            try:
                p.evaluate(f"ouvrirSemaine({num})")
                p.wait_for_timeout(90)
                txt = p.evaluate("(document.getElementById('contenu')?.innerText||'').trim().length")
                if txt < 80:
                    ano("R1", f"S{num} : vue semaine quasi vide ({txt} caracteres)")
                # le placeholder de revue ne doit pas s'afficher si la semaine est finie et loggee
                ph = p.evaluate("(document.getElementById('contenu')?.innerText||'').includes('Revue de la semaine à venir')")
                loggee = any((x.get("realise") or {}).get("statut") in ("fait", "partiel")
                             for x in DATA["SBW"].get(str(num), []))
                if ph and loggee and num < 33:
                    ano("R2", f"S{num} : seances loggees mais placeholder 'Revue a venir' affiche")
                p.evaluate("typeof fermer==='function'&&fermer()")
                p.wait_for_timeout(360)
            except Exception as e:
                ano("R1", f"S{num} : exception a l'ouverture — {str(e)[:90]}")
            if len(errs) > before:
                ano("R1", f"S{num} : erreur JS — {errs[-1][:110]}")

        # ═══ 2. TOUTES LES SEANCES ═══
        print("── 2. Ouverture des 132 seances ...")
        ouvertes = 0
        for wk, arr in DATA["SBW"].items():
            for se in arr:
                before = len(errs)
                try:
                    p.evaluate(f"ouvrirSeance({int(wk)},{se['id']})")
                    p.wait_for_timeout(60)
                    n = p.evaluate("(document.getElementById('contenu')?.innerText||'').trim().length")
                    if n < 60:
                        ano("R3", f"S{wk} seance {se['id']} '{se.get('titre')}' : fiche quasi vide ({n} car.)")
                    else:
                        ouvertes += 1
                    p.evaluate("typeof fermer==='function'&&fermer()")
                    p.wait_for_timeout(360)
                except Exception as e:
                    ano("R3", f"S{wk} seance {se['id']} : exception — {str(e)[:90]}")
                if len(errs) > before:
                    ano("R3", f"S{wk} seance {se['id']} '{se.get('titre')}' : erreur JS — {errs[-1][:110]}")
        print(f"   {ouvertes} fiches ouvertes correctement")

        # ═══ 3. TOUS LES REWINDS ═══
        print("── 3. Parcours integral de chaque Rewind ...")
        for rw in DATA["REWINDS"]:
            before = len(errs)
            try:
                p.evaluate(f"rwOpen('{rw['id']}')")
                p.wait_for_timeout(180)
                on = p.evaluate("document.getElementById('rwoverlay')?.classList.contains('on')")
                if not on:
                    ano("R4", f"Rewind {rw['id']} : l'overlay ne s'ouvre pas")
                    continue
                for i in range(len(rw["slides"])):
                    vide = p.evaluate("(document.getElementById('rwoverlay')?.innerText||'').trim().length<20")
                    if vide:
                        ano("R4", f"Rewind {rw['id']} slide {i+1} : contenu vide")
                    p.evaluate("typeof rwNext==='function'&&rwNext()")
                    p.wait_for_timeout(70)
                p.evaluate("typeof rwClose==='function'&&rwClose()")
                p.wait_for_timeout(60)
            except Exception as e:
                ano("R4", f"Rewind {rw['id']} : exception — {str(e)[:90]}")
            if len(errs) > before:
                ano("R4", f"Rewind {rw['id']} : erreur JS — {errs[-1][:110]}")

        # ═══ 4. ONGLETS + COCKPIT (toutes fenetres) ═══
        print("── 4. Onglets et fenetres Cockpit ...")
        for v in ["accueil", "plan", "cockpit", "palmares"]:
            before = len(errs)
            try:
                p.evaluate(f"showTab('{v}')")
                p.wait_for_timeout(300)
                n = p.evaluate("(document.body.innerText||'').trim().length")
                if n < 100:
                    ano("R5", f"onglet {v} : rendu quasi vide")
            except Exception as e:
                ano("R5", f"onglet {v} : exception — {str(e)[:90]}")
            if len(errs) > before:
                ano("R5", f"onglet {v} : erreur JS — {errs[-1][:110]}")

        p.evaluate("showTab('cockpit')"); p.wait_for_timeout(300)
        for w in [2, 4, 8, 12, 26, 52]:
            before = len(errs)
            try:
                p.evaluate(f"typeof _ckRenderAll==='function'&&_ckRenderAll({w})")
                p.wait_for_timeout(140)
            except Exception as e:
                ano("R6", f"Cockpit fenetre {w} semaines : exception — {str(e)[:90]}")
            if len(errs) > before:
                ano("R6", f"Cockpit fenetre {w} sem : erreur JS — {errs[-1][:110]}")

        # ═══ 5. SCROLL REEL (piege connu : molette, pas scrollTo) ═══
        print("── 5. Scroll par evenements molette reels ...")
        try:
            p.evaluate("showTab('plan')")
            p.wait_for_timeout(300)
            y0 = p.evaluate("window.scrollY")
            for _ in range(14):
                p.mouse.wheel(0, 380)
                p.wait_for_timeout(60)
            y1 = p.evaluate("window.scrollY")
            if y1 <= y0:
                ano("R7", f"la page ne defile pas a la molette (scrollY {y0} -> {y1})")
            for _ in range(14):
                p.mouse.wheel(0, -380)
                p.wait_for_timeout(60)
        except Exception as e:
            ano("R7", f"scroll : exception — {str(e)[:90]}")

        # ═══ 6. NAVIGATION CROISEE (aller-retour rapide) ═══
        print("── 6. Navigation croisee intensive ...")
        before = len(errs)
        try:
            for _ in range(3):
                for v in ["accueil", "cockpit", "plan", "palmares", "accueil"]:
                    p.evaluate(f"showTab('{v}')")
                    p.wait_for_timeout(60)
                p.evaluate("ouvrirSemaine(32)"); p.wait_for_timeout(80)
                p.evaluate("typeof fermer==='function'&&fermer()"); p.wait_for_timeout(50)
        except Exception as e:
            ano("R8", f"navigation croisee : exception — {str(e)[:90]}")
        if len(errs) > before:
            ano("R8", f"navigation croisee : erreur JS — {errs[-1][:110]}")

        # ═══ 7. COHERENCE AFFICHEE : semaine courante ═══
        print("── 7. Coherence de la semaine courante ...")
        cw = p.evaluate("typeof _curWeek==='function'?_curWeek():null")
        attendu = _dt.date.today().isocalendar()[1]
        if cw != attendu:
            ano("R9", f"_curWeek() renvoie {cw} — attendu {attendu} ({_dt.date.today().isoformat()})")

        # ═══ 8. DOUBLONS D'ID DOM ═══
        print("── 8. Identifiants DOM dupliques ...")
        dups = p.evaluate("""(function(){
            var seen={},d=[];
            document.querySelectorAll('[id]').forEach(function(e){
                if(seen[e.id])d.push(e.id); else seen[e.id]=1;});
            return d.slice(0,10);})()""")
        if dups:
            ano("R10", f"id DOM dupliques : {', '.join(dups)}")

        b.close()

    # ─── RAPPORT ───
    print("\n" + "=" * 64)
    print("  AUDIT RUNTIME EXHAUSTIF")
    print("=" * 64)
    if not ANO:
        print("\n  Aucune anomalie runtime detectee.")
    else:
        groupes = {}
        for code, msg in ANO:
            groupes.setdefault(code, []).append(msg)
        for code in sorted(groupes):
            print(f"\n── {code} ({len(groupes[code])}) " + "─" * 40)
            for m in groupes[code][:12]:
                print(f"  {m}")
            if len(groupes[code]) > 12:
                print(f"  ... et {len(groupes[code])-12} autre(s)")
    print("\n" + "=" * 64)
    print(f"  ANOMALIES RUNTIME : {len(ANO)}")
    print(f"  ERREURS JS BRUTES CAPTUREES : {len(errs)}")
    for e in errs[:5]:
        print(f"    {e[:150]}")
    print("=" * 64)
    return len(ANO)

if __name__ == "__main__":
    sys.exit(0 if run() == 0 else 1)
