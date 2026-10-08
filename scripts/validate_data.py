#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_data.py — controle de format des data/*.json publies.

    python scripts/validate_data.py [dossier]     (defaut : data/ a la racine du depot)

Verifie la structure, pas la justesse metier (celle-ci est couverte par les audits) :
cles attendues (src/datamap.py), identifiants et dates des seances, ordre du changelog,
coherence meta.json / changelog, absence de valeurs affichables cassees (NaN, undefined).
Code retour 1 s'il y a au moins une erreur.
"""
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
from datamap import GROUPS  # noqa: E402

BROKEN = re.compile(r"\bNaN\b|\bundefined\b|\[object Object\]")


def _iso(s):
    try:
        datetime.date.fromisoformat(s)
        return True
    except (TypeError, ValueError):
        return False


def _walk_strings(o, path=""):
    if isinstance(o, str):
        yield path, o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from _walk_strings(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _walk_strings(v, f"{path}[{i}]")


def validate(d):
    errs = []
    files = {}
    for name in list(GROUPS) + ["meta"]:
        p = os.path.join(d, name + ".json")
        if not os.path.exists(p):
            errs.append(f"{name}.json absent")
            continue
        try:
            files[name] = json.load(open(p, encoding="utf-8"))
        except ValueError as e:
            errs.append(f"{name}.json illisible : {e}")
    for name, pairs in GROUPS.items():
        if name in files:
            for key, _ in pairs:
                if key not in files[name]:
                    errs.append(f"{name}.json : cle {key} manquante")
    if "seances" in files and "SEANCES_BY_WEEK" in files["seances"]:
        sbw = files["seances"]["SEANCES_BY_WEEK"]
        for wk, arr in sbw.items():
            if not str(wk).isdigit() or not isinstance(arr, list):
                errs.append(f"seances : semaine {wk} mal formee")
                continue
            ids = [s.get("id") for s in arr]
            if len(ids) != len(set(ids)):
                errs.append(f"seances : id en double en semaine {wk}")
            for s in arr:
                if "date" in s and s["date"] is not None and not _iso(s["date"]):
                    errs.append(f"seances : date invalide en semaine {wk} (id {s.get('id')}) : {s['date']!r}")
                if not isinstance(s.get("realise", {}), dict):
                    errs.append(f"seances : realise mal forme en semaine {wk} (id {s.get('id')})")
    if "plan" in files:
        for r in files["plan"].get("RACES", []):
            if not _iso(r.get("date")):
                errs.append(f"plan : date de course invalide : {r.get('nom')!r}")
    if "changelog" in files and "CHANGELOG" in files["changelog"]:
        builds = [e.get("build") for e in files["changelog"]["CHANGELOG"]]
        if not builds or not all(isinstance(b, int) for b in builds):
            errs.append("changelog : numeros de build absents ou non entiers")
        else:
            if builds[0] != max(builds):
                errs.append(f"changelog : la premiere entree n'est pas le dernier build ({builds[0]} / max {max(builds)})")
            if len(builds) != len(set(builds)):
                errs.append("changelog : numeros de build en double")
            meta = files.get("meta", {}).get("CHANGELOG", [{}])[0].get("build")
            if meta != builds[0]:
                errs.append(f"meta.json : build {meta} different de la derniere entree du changelog ({builds[0]})")
    if "meta" in files and not _iso(files["meta"].get("BUILT_ON")):
        errs.append("meta.json : BUILT_ON absent ou invalide")
    for name, content in files.items():
        if name == "changelog":   # prose de developpement : parle legitimement de NaN / undefined
            continue
        for path, s in _walk_strings(content):
            if BROKEN.search(s):
                errs.append(f"{name}.json{path} : valeur affichable cassee ({s[:40]!r})")
                break
    return errs


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data")
    errs = validate(d)
    print(f"validate_data : {d}")
    for e in errs:
        print("  ✗", e)
    print("  RESULTAT :", "OK" if not errs else f"{len(errs)} erreur(s) — NE PAS PUSHER")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
