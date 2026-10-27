#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_log_seance.py — tests de log_seance.py sur trois vraies seances deja loggees a la main.

    python scripts/test_log_seance.py

1. Le bloc « realise » produit depuis les reponses Strava (tests/fixtures/strava/) retrouve les
   valeurs loggees a la main dans data/seances.json : footing route avec decouplage (S44-2),
   allure marathon sans flux (S43-2), trail de 20 km avec arrets (S43-4).
2. Le script ecrit le log, la reference Strava, GEAR et le CHANGELOG (copies temporaires), et
   refuse de reecrire un log existant sans --force.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import log_seance  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures", "strava")
FAIL = []
CHAMPS = ("km", "temps", "allure", "fc_moy", "fc_max", "re", "cadence", "elevation_gain", "kcal",
          "pr", "ach", "splits")
CAS = [  # seance, activite Strava, flux, terrain attendu
    ("S44-2", "20753555995", True, "route"),
    ("S43-2", "20672053327", False, "route"),
    ("S43-4", "20710567399", False, "trail"),
]


def check(name, cond, detail=""):
    print(("  ✓ " if cond else "  ✗ ") + name + ("" if cond else f" — {detail}"))
    if not cond:
        FAIL.append(name)


def opts(**kw):
    base = dict(statut="fait", streams=None, blocs=None, titre=None, sous=None, rpe=None,
                commentaire=None, sans_changelog=False, force=False, sec=False)
    base.update(kw)
    return argparse.Namespace(**base)


def entree(aid):
    with open(os.path.join(FIX, aid, "entree.json"), encoding="utf-8") as f:
        return json.load(f)


def logge(cle):
    w, i = cle[1:].split("-")
    with open(os.path.join(ROOT, "data", "seances.json"), encoding="utf-8") as f:
        sbw = json.load(f)["SEANCES_BY_WEEK"]
    s = [s for s in sbw[w] if str(s["id"]) == i][0]
    textes = os.path.join(ROOT, "data", "textes.json")  # revues et splits charges a la demande
    if os.path.exists(textes):
        with open(textes, encoding="utf-8") as f:
            s["realise"].update(json.load(f)["SEANCES"].get(f"{w}-{i}", {}))
    return s


def test_valeurs():
    print("1. Valeurs retrouvees sur trois seances loggees a la main")
    for cle, aid, flux, terr in CAS:
        streams = os.path.join(FIX, aid, "streams.json") if flux else None
        log, _, _, _ = log_seance.construire(cle, entree(aid), opts(streams=streams))
        r, ref = log["realise"], logge(cle)["realise"]
        ecarts = {k: (r.get(k), ref.get(k)) for k in CHAMPS if r.get(k) != ref.get(k)}
        check(f"{cle} : {len(CHAMPS)} champs identiques au log manuel", not ecarts, str(ecarts)[:300])
        check(f"{cle} : terrain {terr}", r["terrain"] == terr, r["terrain"])
        check(f"{cle} : chaussure", log["seance"].get("chaussure_realise") == logge(cle).get("chaussure_realise"),
              f"{log['seance'].get('chaussure_realise')} / {logge(cle).get('chaussure_realise')}")
        if flux:
            check(f"{cle} : decouplage identique", r.get("decouplage") == ref.get("decouplage"),
                  f"{r.get('decouplage')} / {ref.get('decouplage')}")
            check(f"{cle} : temperature", r.get("temp") == ref.get("temp"))
    log, _, _, _ = log_seance.construire("S43-4", entree("20710567399"),
                                         opts(streams=os.path.join(FIX, "20753555995", "streams.json")))
    check("trail : decouplage refuse (non_calculable)", log["realise"]["decouplage"]["qualite"] == "non_calculable")
    log, _, _, _ = log_seance.construire("S44-2", entree("20753555995"), opts(blocs="1-8:Footing:vert,9:Accélération:orange,10:Retour:vert"))
    seg = log["seance"]["segments"]
    check("blocs : 3 segments, durees = somme des tours", [s["duree"] for s in seg] == [2826, 331, 340], str([s["duree"] for s in seg]))
    check("blocs : allure et FC du bloc", seg[1]["role"] == "Km 9 a 5:31/km, FC 151.", seg[1]["role"])


def test_ecriture():
    print("2. Ecriture des fichiers (copies temporaires)")
    tmp = tempfile.mkdtemp()
    try:
        for nom in ("GEN", "REF", "SEANCES"):
            src = getattr(log_seance, nom)
            dst = os.path.join(tmp, os.path.basename(src))
            shutil.copyfile(src, dst)
            setattr(log_seance, nom, dst)
        log_seance.LOGS = os.path.join(tmp, "logs")
        e = dict(entree("20753555995"), start_local="2026-10-29T18:00:00", gear_total_distance=1294300)
        chemin_e = os.path.join(tmp, "e.json")
        json.dump(e, open(chemin_e, "w", encoding="utf-8"))
        gen_avant = open(log_seance.GEN, encoding="utf-8").read()
        build = int(gen_avant.split('CHANGELOG=[\n  {"build":', 1)[1].split(",", 1)[0])
        log_seance.main(["S44-3", chemin_e])
        out = json.load(open(os.path.join(tmp, "logs", "S44-3.json"), encoding="utf-8"))
        check("log ecrit avec realise et date du jour", out["realise"]["km"] == 10.04 and out["seance"].get("date") == "2026-10-29")
        ref = json.load(open(log_seance.REF, encoding="utf-8"))
        check("reference : activite ajoutee en tete", list(ref["activites"])[0] == "2026-10-29")
        check("reference : chaussure a 1294 km", ref["chaussures"]["Clifton 10"] == 1294)
        gen = open(log_seance.GEN, encoding="utf-8").read()
        check("GEAR : Clifton 10 a 1294 km", '"modele":"Clifton 10","km":1294}' in gen)
        check(f"CHANGELOG : build {build + 1} en tete", f'CHANGELOG=[\n  {{"build":{build + 1},' in gen)
        compile(gen, "gen.py", "exec")
        check("gen.py reste du Python valide", True)
        ref_avant = open(log_seance.REF, encoding="utf-8").read()
        log_seance.main(["S44-3", chemin_e, "--force", "--sans-changelog"])
        check("--force : reference Strava inchangee", open(log_seance.REF, encoding="utf-8").read() == ref_avant)
        os.remove(os.path.join(tmp, "logs", "S44-3.json"))
        log_seance.main(["S44-3", chemin_e, "--sans-changelog"])
        check("sortie deja dans la reference : pas de double compte",
              json.load(open(log_seance.REF, encoding="utf-8"))["activites"]["2026-10-29"][0] == 10.0356)
        try:
            log_seance.main(["S44-3", chemin_e])
            check("refus de reecrire un log existant", False)
        except SystemExit:
            check("refus de reecrire un log existant", True)
    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    test_valeurs()
    test_ecriture()
    print("RESULTAT : " + ("OK" if not FAIL else f"{len(FAIL)} ECHEC(S)"))
    sys.exit(1 if FAIL else 0)
