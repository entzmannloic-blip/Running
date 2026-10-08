#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
capture_reference.py — Captures de reference des 4 vues (390 px), reproductibles.

    python scripts/capture_reference.py            # (re)ecrit tests/reference/*.png
    python scripts/capture_reference.py --check    # compare au dossier de reference
    python scripts/capture_reference.py --out DIR  # ecrit ailleurs

Reproductible : date figee, localStorage vide, meteo bloquee, animations reduites,
carrousel Rewind masque. A lancer apres `python src/build.py`.
"""
import os
import sys
import tempfile

for _d in (os.path.dirname(os.path.abspath(__file__)),
           os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")):
    if os.path.exists(os.path.join(_d, "paths.py")):
        sys.path.insert(0, _d)
from paths import ROOT, html_url  # noqa: E402

REF_DIR = os.path.join(ROOT, "tests", "reference")
VIEWS = ["accueil", "plan", "cockpit", "palmares"]
FIXED_NOW = "2026-10-08T10:00:00"


def capture(out_dir, scheme="light"):
    from playwright.sync_api import sync_playwright

    os.makedirs(out_dir, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2,
                            reduced_motion="reduce", color_scheme=scheme, locale="fr-FR",
                            timezone_id="Europe/Paris", service_workers="block")
        ctx.route("**/*open-meteo.com/**", lambda r: r.abort())
        p = ctx.new_page()
        p.clock.install(time=FIXED_NOW)
        p.goto(html_url(), wait_until="load", timeout=20000)
        p.wait_for_timeout(1500)
        p.evaluate("var o=document.getElementById('rwoverlay');if(o)o.style.display='none';")
        # le pied de page affiche le numero de build : on le masque pour que les
        # references ne changent pas a chaque build
        p.add_style_tag(content="#maj-foot,.maj-foot{visibility:hidden!important}")
        for v in VIEWS:
            p.evaluate(f"showTab('{v}')")
            p.wait_for_timeout(600)
            p.evaluate("window.scrollTo(0,0)")
            p.screenshot(path=os.path.join(out_dir, f"{v}.png"))
        b.close()


def main():
    args = sys.argv[1:]
    if "--check" in args:
        tmp = tempfile.mkdtemp(prefix="running-ref-")
        capture(tmp)
        diffs = [v for v in VIEWS
                 if not os.path.exists(os.path.join(REF_DIR, f"{v}.png"))
                 or open(os.path.join(tmp, f"{v}.png"), "rb").read()
                 != open(os.path.join(REF_DIR, f"{v}.png"), "rb").read()]
        if diffs:
            print("DIFFERENCES :", ", ".join(diffs), "(captures dans", tmp + ")")
            sys.exit(1)
        print("Captures identiques aux references (4/4)")
        return
    out = args[args.index("--out") + 1] if "--out" in args else REF_DIR
    capture(out)
    print("Captures ecrites dans", out)


if __name__ == "__main__":
    main()
