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
import datetime
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import log_seance  # noqa: E402
import rewind_seance  # noqa: E402

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
        # jour libre : le lendemain de la derniere sortie de la reference (une date fixe finit par recevoir une vraie sortie, L14)
        dern = max(json.load(open(log_seance.REF, encoding="utf-8"))["activites"])
        jour = (datetime.date.fromisoformat(dern) + datetime.timedelta(days=1)).isoformat()
        e = dict(entree("20753555995"), start_local=jour + "T18:00:00", gear_total_distance=1294300)
        chemin_e = os.path.join(tmp, "e.json")
        json.dump(e, open(chemin_e, "w", encoding="utf-8"))
        gen_avant = open(log_seance.GEN, encoding="utf-8").read()
        build = int(gen_avant.split('CHANGELOG=[\n  {"build":', 1)[1].split(",", 1)[0])
        log_seance.main(["S44-3", chemin_e])
        out = json.load(open(os.path.join(tmp, "logs", "S44-3.json"), encoding="utf-8"))
        check("log ecrit avec realise et date du jour", out["realise"]["km"] == 10.04 and out["seance"].get("date") == jour)
        ref = json.load(open(log_seance.REF, encoding="utf-8"))
        check("reference : activite ajoutee en tete", list(ref["activites"])[0] == jour)
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
              json.load(open(log_seance.REF, encoding="utf-8"))["activites"][jour][0] == 10.0356)
        try:
            log_seance.main(["S44-3", chemin_e])
            check("refus de reecrire un log existant", False)
        except SystemExit:
            check("refus de reecrire un log existant", True)
    finally:
        shutil.rmtree(tmp)

def _encode(pts):
    """Encode (lat, lng) en polyline Google : pour fabriquer une polyline de test."""
    out, la, lo = [], 0, 0
    for p in pts:
        for v, w in ((round(p[0] * 1e5), la), (round(p[1] * 1e5), lo)):
            d = v - w
            d = ~(d << 1) if d < 0 else d << 1
            while d >= 0x20:
                out.append(chr((0x20 | (d & 0x1F)) + 63))
                d >>= 5
            out.append(chr(d + 63))
        la, lo = round(p[0] * 1e5), round(p[1] * 1e5)
    return "".join(out)


def test_trace():
    import math
    print("3. Trace du Rewind : masquage des 300 m et Web Mercator (fond de carte)")
    rs = rewind_seance
    # ellipse fermee d'environ 9 km autour de Lyon (sans croisement), un point tous les ~10 m
    n = 900
    pts = [(45.7500 + 0.0130 * math.sin(2 * math.pi * i / n), 4.8400 + 0.0200 * math.cos(2 * math.pi * i / n)) for i in range(n + 1)]
    pts = [(round(a, 5), round(b, 5)) for a, b in pts]
    dec = rs.decode_polyline(_encode(pts))
    check("polyline de test : encodage puis decodage a 1e-5 pres", max(abs(a - c) + abs(b - d) for (a, b), (c, d) in zip(pts, dec)) < 3e-5)
    cum = [0.0]
    for i in range(1, len(dec)):
        cum.append(cum[-1] + rs._sol(dec[i - 1], dec[i]))
    longueur = cum[-1]
    r = rs.projette(dec, longueur)
    A, T = r["ancrage"], r["trace"]
    check("masque de 300 m et ancrage entier ecrits", r["masque"] == 300 and isinstance(A["x"], int) and isinstance(A["y"], int))

    def retour(p):  # trace -> lat/lng (inverse de Web Mercator)
        x, y = A["x"] + p[0], A["y"] + p[1]
        return math.degrees(2 * math.atan(math.exp(y / rs.RAYON)) - math.pi / 2), math.degrees(x / rs.RAYON)
    debut, fin = retour(T[0]), retour(T[-1])
    d_debut = min(cum[i] for i in range(len(dec)) if rs._sol(dec[i], debut) < 15) if any(rs._sol(q, debut) < 15 for q in dec) else None
    check("le trace commence a 300 m du depart (a 15 m pres, au moins 300 m)", d_debut is not None and 285 <= d_debut <= 345, str(d_debut))
    d_fin = longueur - max(cum[i] for i in range(len(dec)) if rs._sol(dec[i], fin) < 15)
    check("le trace s'arrete a 300 m de l'arrivee", 285 <= d_fin <= 345, str(d_fin))
    def rang(p):  # sommet du polyline le plus proche d'un point du trace
        q = retour(p)
        return min(range(len(dec)), key=lambda i: rs._sol(dec[i], q))
    check("tous les points du trace sont a plus de 300 m des extremites, le long de la course",
          all(295 <= cum[rang(p)] <= longueur - 295 for p in T) and len(T) < len(dec))
    check("trace_d : metres reels de la sortie, au moins 300 de chaque cote", r["trace_d"][0] >= 300 and longueur - r["trace_d"][1] >= 300, str(r["trace_d"]))
    milieu = len(T) // 2
    mid = retour(T[milieu])
    check("Web Mercator exact : un point du trace retrouve sa latitude et sa longitude (1 m)", min(rs._sol(mid, q) for q in dec) < 3.0,
          str(min(rs._sol(mid, q) for q in dec)))
    # distance reelle Strava plus grande que le polyline reduit (cas reel : 10 017 m pour 9 734 m) : on masque encore >= 300 m reels
    r2 = rs.projette(dec, longueur * 1.03)
    check("polyline plus court que la distance reelle : le masque reste d'au moins 300 m reels", r2["trace_d"][0] >= 300 and len(r2["trace"]) <= len(T), str(r2["trace_d"]))
    # polyline plus long que la distance reelle : on masque davantage de polyline pour tenir 300 m reels
    r3 = rs.projette(dec, longueur * 0.9)
    check("polyline plus long que la distance reelle : le masque reste d'au moins 300 m reels", r3["trace_d"][0] >= 300 and len(r3["trace"]) <= len(T), str(r3["trace_d"]))
    court = rs.projette(dec[:12], None)
    check("sortie trop courte : aucun trace plutot qu'un trace non masque", court["trace"] == [] and court["ancrage"] is None, str(len(court["trace"])))
    # --retrace : ne change que le trace
    tmp = tempfile.mkdtemp()
    try:
        dossier0 = rs.DOSSIER
        rs.DOSSIER = tmp
        ancien = {"strava_id": "123", "debut": "2026-10-29T18:00:00", "lieu": "Lyon, France", "flux": {"t": [1, 2]},
                  "trace": [[0, 0], [5, 5]], "tours": [[1, 2]], "prs": []}
        json.dump(ancien, open(os.path.join(tmp, "44-9.json"), "w", encoding="utf-8"))
        ent = os.path.join(tmp, "e.json")
        json.dump({"id": "123", "summary": {"distance": longueur}, "reduced_polyline": _encode(pts)}, open(ent, "w", encoding="utf-8"))
        rs.retrace("S44-9", ent)
        nouveau = json.load(open(os.path.join(tmp, "44-9.json"), encoding="utf-8"))
        check("--retrace : trace, ancrage et masque refaits, le reste du Rewind intact",
              nouveau["ancrage"] and nouveau["masque"] == 300 and len(nouveau["trace"]) > 100
              and all(nouveau[c] == ancien[c] for c in ("strava_id", "debut", "lieu", "flux", "tours", "prs")))
        json.dump({"id": "999", "summary": {"distance": longueur}, "reduced_polyline": _encode(pts)}, open(ent, "w", encoding="utf-8"))
        try:
            rs.retrace("S44-9", ent)
            check("--retrace : refus d'une autre activite Strava", False)
        except SystemExit:
            check("--retrace : refus d'une autre activite Strava", True)
    finally:
        rs.DOSSIER = dossier0
        shutil.rmtree(tmp)


if __name__ == "__main__":
    test_valeurs()
    test_ecriture()
    test_trace()
    print("RESULTAT : " + ("OK" if not FAIL else f"{len(FAIL)} ECHEC(S)"))
    sys.exit(1 if FAIL else 0)
