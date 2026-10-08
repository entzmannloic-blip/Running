#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_race.py — Reproduction ciblee de la race condition suspectee dans fermer().

fermer() planifie contenu.innerHTML='' dans un setTimeout de 300 ms.
Si l'utilisateur rouvre une fiche AVANT l'echeance, le vidage differe
s'applique a la NOUVELLE vue, qui devient blanche.

Ce script mesure a partir de quel delai le bug disparait.
"""
import os
import sys
for _d in (os.path.dirname(os.path.abspath(__file__)), os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")):
    if os.path.exists(os.path.join(_d, "paths.py")):
        sys.path.insert(0, _d)
from paths import WORK, OUT_HTML, html_url  # noqa: E402
from playwright.sync_api import sync_playwright

HTML = html_url()

with sync_playwright() as pw:
    b = pw.chromium.launch()
    p = b.new_page(viewport={"width": 390, "height": 844})
    p.goto(HTML, wait_until="load", timeout=30000)
    p.wait_for_timeout(1500)
    p.evaluate("var o=document.getElementById('rwoverlay');if(o){o.classList.remove('on');o.style.display='none';}")

    print("Scenario : ouvrir une semaine, la fermer, en rouvrir une autre apres X ms")
    print("puis mesurer le contenu 400 ms plus tard.\n")
    print(f"{'delai avant reouverture':>26} | {'contenu apres 400ms':>20} | verdict")
    print("-" * 70)

    resultats = []
    for delai in [0, 50, 100, 150, 200, 250, 290, 310, 350, 500]:
        p.evaluate("ouvrirSemaine(31)")
        p.wait_for_timeout(400)
        p.evaluate("fermer()")
        p.wait_for_timeout(delai)
        p.evaluate("ouvrirSemaine(32)")
        p.wait_for_timeout(400)          # au-dela de l'echeance du setTimeout
        n = p.evaluate("(document.getElementById('contenu')?.innerText||'').trim().length")
        ok = n > 200
        resultats.append((delai, n, ok))
        print(f"{delai:>23} ms | {n:>17} car. | {'OK' if ok else '*** VUE VIDE ***'}")
        p.evaluate("fermer()")
        p.wait_for_timeout(400)

    casses = [r for r in resultats if not r[2]]
    print("\n" + "=" * 70)
    if casses:
        seuil = max(r[0] for r in casses)
        print(f"BUG CONFIRME : la vue est vidée si l'on rouvre dans les {seuil} ms")
        print(f"suivant la fermeture. {len(casses)}/{len(resultats)} delais testes echouent.")
    else:
        print("Aucune race condition reproduite.")
    print("=" * 70)
    b.close()
