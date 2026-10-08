#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_ci_tools.py — tests de validate_data.py et pr_scope.py (outils de la verification automatique).

    python scripts/test_ci_tools.py
"""
import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
FAIL = []


def check(name, cond, detail=""):
    print(("  ✓ " if cond else "  ✗ ") + name + ("" if cond else f" — {detail}"))
    if not cond:
        FAIL.append(name)


def load(d, name):
    return json.load(open(os.path.join(d, name + ".json"), encoding="utf-8"))


def save(d, name, obj):
    json.dump(obj, open(os.path.join(d, name + ".json"), "w", encoding="utf-8"), ensure_ascii=False)


def main():
    print("\nTEST OUTILS CI")
    import validate_data
    import pr_scope

    src = os.path.join(ROOT, "data")
    check("donnees du depot valides", validate_data.validate(src) == [], str(validate_data.validate(src))[:200])

    def mutated(fn):
        with tempfile.TemporaryDirectory() as d:
            for n in os.listdir(src):
                shutil.copy(os.path.join(src, n), os.path.join(d, n))
            fn(d)
            return validate_data.validate(d)

    def dup_id(d):
        s = load(d, "seances")
        wk = next(iter(s["SEANCES_BY_WEEK"]))
        arr = s["SEANCES_BY_WEEK"][wk]
        arr.append(copy.deepcopy(arr[0]))
        save(d, "seances", s)

    def bad_date(d):
        s = load(d, "seances")
        wk = next(iter(s["SEANCES_BY_WEEK"]))
        s["SEANCES_BY_WEEK"][wk][0]["date"] = "31/02/2026"
        save(d, "seances", s)

    def changelog_order(d):
        c = load(d, "changelog")
        c["CHANGELOG"][0], c["CHANGELOG"][1] = c["CHANGELOG"][1], c["CHANGELOG"][0]
        save(d, "changelog", c)

    def meta_mismatch(d):
        m = load(d, "meta")
        m["CHANGELOG"][0]["build"] += 1
        save(d, "meta", m)

    def missing_key(d):
        p = load(d, "plan")
        del p["PHASES"]
        save(d, "plan", p)

    def nan_text(d):
        p = load(d, "plan")
        p["PROFIL"]["prenom"] = "NaN"
        save(d, "plan", p)

    for label, fn in [("id de seance en double", dup_id), ("date de seance invalide", bad_date),
                      ("changelog dans le desordre", changelog_order), ("build de meta.json incoherent", meta_mismatch),
                      ("cle de donnees manquante", missing_key), ("valeur NaN affichable", nan_text)]:
        errs = mutated(fn)
        check(f"detecte : {label}", len(errs) >= 1, "aucune erreur remontee")

    # --- perimetre d'une PR (fusion automatique) ---
    ok, off = pr_scope.classify(["data/seances.json", "data/meta.json", "src/gen.py", "src/strava_reference.json", "index.html", "sw.js", "fit/S41-3.fit"])
    check("PR de donnees : perimetre autorise", ok and off == [], str(off))
    ok, off = pr_scope.classify(["data/seances.json", "src/app.js", ".github/workflows/verify.yml"])
    check("PR touchant le code : refusee, fichiers listes", (not ok) and off == ["src/app.js", ".github/workflows/verify.yml"], str(off))
    ok, off = pr_scope.classify([])
    check("PR vide : pas de fusion automatique", not ok)

    print("\n  RESULTAT :", "OK" if not FAIL else f"{len(FAIL)} echec(s) — NE PAS PUSHER")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
