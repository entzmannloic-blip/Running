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

    # --- renommage : deplacer un fichier hors perimetre vers data/ ne doit pas passer pour « donnees seulement » ---
    import subprocess

    def git(d, *a):
        return subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *a], cwd=d, capture_output=True,
                              text=True, encoding="utf-8")

    with tempfile.TemporaryDirectory() as d:
        git(d, "init", "-q", "-b", "main")
        os.makedirs(os.path.join(d, ".github", "workflows"))
        open(os.path.join(d, ".github", "workflows", "verify.yml"), "w").write("name: verify" + chr(10))
        os.makedirs(os.path.join(d, "data"))
        open(os.path.join(d, "data", "meta.json"), "w").write('{"CHANGELOG":[{"build":5}]}')
        git(d, "add", "-A")
        git(d, "commit", "-q", "-m", "base")
        git(d, "checkout", "-q", "-b", "pr")
        git(d, "mv", ".github/workflows/verify.yml", "data/verify.yml")
        git(d, "commit", "-q", "-m", "rename")
        r = subprocess.run([sys.executable, os.path.join(HERE, "pr_scope.py"), "main...pr"], cwd=d, capture_output=True,
                           text=True, encoding="utf-8")
        check("renommage du workflow vers data/ : refuse (pas DATA_ONLY)",
              r.returncode == 1 and "verify.yml" in r.stdout, (r.stdout + r.stderr)[:160])

    # --- le numero de build doit augmenter dans chaque PR ---
    def bump_check(new_build):
        with tempfile.TemporaryDirectory() as d:
            git(d, "init", "-q", "-b", "main")
            os.makedirs(os.path.join(d, "data"))
            open(os.path.join(d, "data", "meta.json"), "w").write('{"CHANGELOG":[{"build":5}]}')
            git(d, "add", "-A")
            git(d, "commit", "-q", "-m", "base")
            git(d, "checkout", "-q", "-b", "pr")
            open(os.path.join(d, "data", "meta.json"), "w").write('{"CHANGELOG":[{"build":%d}]}' % new_build)
            git(d, "commit", "-q", "-am", "pr")
            return subprocess.run([sys.executable, os.path.join(HERE, "check_build_increment.py"), "main"], cwd=d,
                                  capture_output=True, text=True, encoding="utf-8")
    r = bump_check(5)
    check("PR sans incrementation du build : refusee", r.returncode == 1, (r.stdout + r.stderr)[:160])
    r = bump_check(4)
    check("PR qui fait reculer le build : refusee", r.returncode == 1, (r.stdout + r.stderr)[:160])
    r = bump_check(6)
    check("PR qui incremente le build : acceptee", r.returncode == 0, (r.stdout + r.stderr)[:160])

    print("\n  RESULTAT :", "OK" if not FAIL else f"{len(FAIL)} echec(s) — NE PAS PUSHER")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
