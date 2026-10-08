#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_build_increment.py — le numero de build d'une PR doit etre superieur a celui de la branche de base.

    python scripts/check_build_increment.py origin/main

Sans cela, un build identique laisse sw.js inchange : le service worker ne se met pas a jour, le bandeau
« Nouvelle version prete » n'apparait pas et le cache hors-ligne reste perime (regle 3 de CLAUDE.md :
incrementer le build avant chaque push). Compare data/meta.json (genere par le build) a celui de la base.
Code retour 1 si le build n'a pas augmente.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = "data/meta.json"


def build_of(text):
    return int(json.loads(text)["CHANGELOG"][0]["build"])


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    cwd = os.getcwd()
    cur = build_of(open(os.path.join(cwd, META), encoding="utf-8").read())
    r = subprocess.run(["git", "show", f"{base}:{META}"], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print(f"check_build_increment : {META} absent de {base} — rien a comparer (build {cur})")
        return
    prev = build_of(r.stdout)
    if cur <= prev:
        print(f"check_build_increment : ✗ build {cur} <= build de {base} ({prev}) — incrementer le build (CHANGELOG de src/gen.py) puis relancer python src/build.py")
        sys.exit(1)
    print(f"check_build_increment : ✓ build {prev} -> {cur}")


if __name__ == "__main__":
    main()
