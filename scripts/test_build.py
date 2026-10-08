#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_build.py — le build est reproductible, quelle que soit la date du jour.

gen.py calcule l'ACWR « a aujourd'hui ». Pour que la verification automatique
(python src/build.py --check) ne casse pas le lendemain d'un build, la date de
build est enregistree dans data/meta.json (BUILT_ON) et rejouee par --check.

    python scripts/test_build.py        (code retour 1 au premier echec)
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "src", "build.py")
FAIL = []


def check(name, cond, detail=""):
    print(("  ✓ " if cond else "  ✗ ") + name + ("" if cond else f" — {detail}"))
    if not cond:
        FAIL.append(name)


def build(work, today=None, extra=()):
    env = dict(os.environ, RUNNING_WORK=work, PYTHONUTF8="1")
    env.pop("RUNNING_TODAY", None)
    if today:
        env["RUNNING_TODAY"] = today
    return subprocess.run([sys.executable, BUILD, *extra], env=env, capture_output=True,
                          text=True, encoding="utf-8", cwd=ROOT)


def digest(site):
    h = {}
    for rel in ["index.html", "sw.js"] + ["data/" + n for n in sorted(os.listdir(os.path.join(site, "data")))]:
        h[rel] = hashlib.sha256(open(os.path.join(site, *rel.split("/")), "rb").read()).hexdigest()
    return h


def main():
    print("\nTEST BUILD — reproductibilite")
    # --stage : construit site/ dans un dossier temporaire, sans rien ecrire a la racine du depot.
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b, tempfile.TemporaryDirectory() as c:
        ra = build(a, "2026-10-20", ["--stage"])
        rb = build(b, "2026-10-20", ["--stage"])
        rc = build(c, "2026-11-02", ["--stage"])
        ok_sites = all(os.path.exists(os.path.join(w, "site", "index.html")) for w in (a, b, c))
        check("builds produits", ok_sites, (ra.stdout + ra.stderr)[-300:])
        if not ok_sites:
            sys.exit(1)
        data_a = json.load(open(os.path.join(a, "data.json"), encoding="utf-8"))
        check("gen.py suit RUNNING_TODAY (ACWR au 2026-10-20)", data_a["ACWR_DATA"]["ref"] == "2026-10-20",
              str(data_a["ACWR_DATA"]["ref"]))
        meta_a = json.load(open(os.path.join(a, "site", "data", "meta.json"), encoding="utf-8"))
        check("meta.json enregistre BUILT_ON", meta_a.get("BUILT_ON") == "2026-10-20", str(meta_a.get("BUILT_ON")))
        check("deux builds du meme jour sont identiques (octet pour octet)",
              digest(os.path.join(a, "site")) == digest(os.path.join(b, "site")))
        da, dc = digest(os.path.join(a, "site")), digest(os.path.join(c, "site"))
        check("un autre jour change les donnees datees (preuve que la date compte)",
              da["data/historique.json"] != dc["data/historique.json"])

    # --check rejoue la date du depot : insensible a la date du jour de la machine
    env_far = dict(os.environ, RUNNING_TODAY="2031-01-01", PYTHONUTF8="1")
    r = subprocess.run([sys.executable, BUILD, "--check"], env=env_far, capture_output=True,
                       text=True, encoding="utf-8", cwd=ROOT)
    check("build --check passe meme si la date du jour a change", r.returncode == 0,
          (r.stdout + r.stderr)[-300:])

    print("\n  RESULTAT :", "OK" if not FAIL else f"{len(FAIL)} echec(s) — NE PAS PUSHER")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
