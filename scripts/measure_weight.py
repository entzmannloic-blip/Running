#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""measure_weight.py — poids du site construit (brut et compresse gzip niveau 6).

    python scripts/measure_weight.py

Le « premier chargement » = index.html + src/app.js + data eager (plan, seances,
historique, meta). Reference avant refonte (build 224) : 1 fichier, 389 396 octets
compresses mesures sur GitHub Pages.
"""
import gzip
import os
import sys

for _d in (os.path.dirname(os.path.abspath(__file__)),
           os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")):
    if os.path.exists(os.path.join(_d, "paths.py")):
        sys.path.insert(0, _d)
from paths import SITE  # noqa: E402
from datamap import EAGER  # noqa: E402

FILES = ["index.html", "src/app.js"] + [f"data/{n}.json" for n in EAGER] + ["data/changelog.json"]


def size(rel):
    raw = open(os.path.join(SITE, *rel.split("/")), "rb").read()
    return len(raw), len(gzip.compress(raw, 6))


def main():
    tot_raw = tot_gz = 0
    print(f"{'fichier':26}{'brut':>10}{'gzip':>10}")
    for rel in FILES:
        raw, gz = size(rel)
        lazy = rel == "data/changelog.json"
        print(f"{rel:26}{raw:>10}{gz:>10}" + ("   (a la demande)" if lazy else ""))
        if not lazy:
            tot_raw += raw
            tot_gz += gz
    print(f"{'PREMIER CHARGEMENT':26}{tot_raw:>10}{tot_gz:>10}   (avant refonte : 389396 gzip)")


if __name__ == "__main__":
    main()
