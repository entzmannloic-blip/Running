#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pr_scope.py — une PR est-elle « donnees seulement » (fusion automatique permise) ?

    python scripts/pr_scope.py <base>...<head>     ex. origin/main...HEAD
    python scripts/pr_scope.py --files a b c

Perimetre autorise : data/, fit/, src/gen.py, src/hist.json, src/strava_reference.json, index.html, sw.js
(index.html, sw.js et data/ sont GENERES par le build, verifie par `build.py --check`).
Tout autre fichier (src/app.js, CSS, workflows, scripts...) = PR de code, annoncee avant fusion.
Code retour 0 = donnees seulement, 1 = code (fichiers hors perimetre listes).
"""
import subprocess
import sys

ALLOWED_PREFIXES = ("data/", "fit/")
ALLOWED_FILES = {"src/gen.py", "src/hist.json", "src/strava_reference.json", "index.html", "sw.js"}


def classify(files):
    files = [f.strip().replace("\\", "/") for f in files if f.strip()]
    if not files:
        return False, []
    off = [f for f in files if f not in ALLOWED_FILES and not f.startswith(ALLOWED_PREFIXES)]
    return not off, off


def main():
    args = sys.argv[1:]
    if args and args[0] == "--files":
        files = args[1:]
    else:
        rng = args[0] if args else "origin/main...HEAD"
        # --no-renames : un fichier deplace hors perimetre (ex. le workflow vers data/) doit lister aussi son ancien chemin
        files = subprocess.run(["git", "diff", "--no-renames", "--name-only", rng], capture_output=True, text=True,
                               encoding="utf-8").stdout.splitlines()
    ok, off = classify(files)
    if ok:
        print(f"DATA_ONLY ({len(files)} fichiers)")
        sys.exit(0)
    print("CODE" if files else "VIDE", "— hors perimetre :", ", ".join(off) if off else "(aucun fichier)")
    sys.exit(1)


if __name__ == "__main__":
    main()
