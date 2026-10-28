#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rewind_seance.py — donnees du Rewind de seance (P4, lot 1).

Le shell n'atteint pas Strava : Claude lit Strava par MCP et recopie les reponses dans
strava/<id>-rewind.json (dossier ignore par Git), puis lance ce script, ou log_seance.py --rewind.
Il ecrit src/rewind/44-2.json ; assemble.py y ajoute les elements du coach tires de la revue et
publie data/rewind-44-2.json, charge seulement a l'ouverture du Rewind.

    python scripts/rewind_seance.py S44-2 strava/20753555995-rewind.json
           [--cible-allure 6:10- | 5:50-6:25] [--cible-fc 145 | 135-145] [--cible-source TEXTE]

--cible-* : seulement quand la cible appliquee differe du plan (seance remplacee). Sinon l'app lit
l'allure prevue au plan (metriques.Allure, plage « a-b/km »).

Fichier d'entree (champs Strava recopies tels quels) :
{"id":"20753555995","name":"…","start_local":"2026-10-27T17:04:11","location_summary":"Lyon, France",
 "summary":{"distance":10035.6,"moving_time":3510,"elapsed_time":3525,"elevation_gain":31,…},   list_activities
 "weather":{"condition":"Clear","temperature":18.4,…},                                            list_activities
 "reduced_polyline":"…",                                                   list_activities(include_polyline=true)
 "performance":{"pr_achievements":[{"type":"SegmentPersonalRecordSilver","entity_id":"…","rank":35}],
   "segment_efforts":[{"id":"…","name":"…","distance":417.8,"moving_time":199,"avg_hr":118.5}],
   "best_efforts":[["1K",327,"86843151821"]],
   "laps":[[moving_time,distance,avg_hr,max_hr,elevation_gain,elapsed_time]]},     get_activity_performance
 "streams":{"time":[…],"distance":[…],"altitude":[…],"velocity_smooth":[…],"heart_rate":[…]}}
                                     get_activity_streams(resolution=150, streams=[time, distance, altitude,
                                                                                    velocity_smooth, heart_rate])
"""
import argparse
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER = os.path.join(ROOT, "src", "rewind")
MAX_POINTS = 160
FLUX = (("t", "time"), ("d", "distance"), ("alt", "altitude"), ("v", "velocity_smooth"), ("fc", "heart_rate"))
RANG = {"SegmentPersonalRecordGold": 1, "SegmentPersonalRecord": 1, "PersonalRecord": 1,
        "SegmentPersonalRecordSilver": 2, "SegmentPersonalRecordBronze": 3}


def sec(m):
    a, b = m.split(":")
    return int(a) * 60 + int(b)


def cible(allure, fc, source):
    """'6:10-' = 6:10/km ou plus lent ; '5:50-6:25' = plage ; fc '145' = maximum, '135-145' = plage."""
    if not allure and not fc:
        return None
    c, mots = {"rapide": None, "lent": None}, []
    if allure:
        m = re.fullmatch(r"(\d:\d\d)\s*-\s*(\d:\d\d)?", allure.strip())
        if not m:
            raise SystemExit(f"--cible-allure illisible : {allure!r} (ex. 6:10- ou 5:50-6:25)")
        a = sec(m.group(1))
        if m.group(2):
            b = sec(m.group(2))
            c["rapide"], c["lent"] = min(a, b), max(a, b)
            mots.append(f"{m.group(1)}-{m.group(2)}/km")
        else:
            c["rapide"] = a
            mots.append(f"{m.group(1)}/km ou plus lent")
    if fc:
        m = re.fullmatch(r"(\d{3})(?:\s*-\s*(\d{3}))?", fc.strip())
        if not m:
            raise SystemExit(f"--cible-fc illisible : {fc!r} (ex. 145 ou 135-145)")
        if m.group(2):
            c["fc_min"], c["fc_max"] = int(m.group(1)), int(m.group(2))
            mots.append(f"FC {m.group(1)}-{m.group(2)}")
        else:
            c["fc_max"] = int(m.group(1))
            mots.append(f"FC {m.group(1)} au maximum")
    c["texte"] = ", ".join(mots)
    c["source"] = source or "Cible appliquée au log (séance modifiée)"
    return c


def decode_polyline(s):
    pts, i, lat, lng = [], 0, 0, 0
    while i < len(s):
        for k in (0, 1):
            shift = res = 0
            while True:
                b = ord(s[i]) - 63
                i += 1
                res |= (b & 0x1F) << shift
                shift += 5
                if b < 0x20:
                    break
            d = ~(res >> 1) if res & 1 else res >> 1
            if k == 0:
                lat += d
            else:
                lng += d
        pts.append((lat / 1e5, lng / 1e5))
    return pts


def projette(pts):
    """Coordonnees locales en metres (x vers l'est, y vers le nord), origine au coin bas-gauche."""
    la0 = sum(p[0] for p in pts) / len(pts)
    k = math.cos(math.radians(la0))
    xy = [(p[1] * 111320 * k, p[0] * 110540) for p in pts]
    x0, y0 = min(x for x, _ in xy), min(y for _, y in xy)
    return [[round(x - x0), round(y - y0)] for x, y in xy]


def reduit(n, m=MAX_POINTS):
    """Indices de m points repartis sur n (premier et dernier compris)."""
    if n <= m:
        return list(range(n))
    return sorted({round(i * (n - 1) / (m - 1)) for i in range(m)})


def construire(e, cib=None):
    st = e["streams"]
    n = len(st["time"])
    for _, k in FLUX:
        if len(st.get(k) or []) != n:
            raise SystemExit(f"flux {k} absent ou de longueur differente ({len(st.get(k) or [])} pour {n})")
    if abs(st["distance"][-1] - e["summary"]["distance"]) > 60:
        raise SystemExit("le flux de distance ne correspond pas a la distance Strava")
    idx = reduit(n)
    flux = {c: [st[k][i] for i in idx] for c, k in FLUX}
    perf = e.get("performance") or {}
    noms = {s["id"]: s for s in perf.get("segment_efforts", [])}
    efforts = {b[2]: b for b in perf.get("best_efforts", []) if len(b) > 2}
    prs = []
    for p in perf.get("pr_achievements", []):
        rang = RANG.get(p.get("type"))
        if not rang:
            continue
        s, b = noms.get(p.get("entity_id")), efforts.get(p.get("entity_id"))
        if s:
            prs.append({"rang": rang, "nom": s["name"], "distance": s["distance"], "t": s["moving_time"],
                        "fc": round(s["avg_hr"]) if s.get("avg_hr") else None})
        elif b:
            prs.append({"rang": rang, "nom": b[0], "distance": None, "t": b[1], "fc": None})
    s = e["summary"]
    w = e.get("weather") or {}
    out = {"strava_id": str(e["id"]), "debut": e["start_local"], "lieu": e.get("location_summary"),
           "meteo": {"temperature": w.get("temperature"), "condition": w.get("condition")},
           "resume": {k: s.get(k) for k in ("distance", "moving_time", "elapsed_time", "elevation_gain")},
           "flux": flux, "trace": projette(decode_polyline(e["reduced_polyline"])),
           "tours": perf.get("laps") or [], "meilleurs": [b[:2] for b in perf.get("best_efforts", [])], "prs": prs}
    if cib:
        out["cible"] = cib
    return out


def ecrire(seance, entree, cib=None, sec_seul=False):
    m = re.fullmatch(r"S?(\d+)-(\d+)", seance)
    if not m:
        raise SystemExit(f"seance illisible : {seance!r} (ex. S44-2)")
    cle = f"{int(m.group(1))}-{int(m.group(2))}"
    with open(entree, encoding="utf-8") as f:
        e = json.load(f)
    out = construire(e, cib)
    texte = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    chemin = os.path.join(DOSSIER, f"{cle}.json")
    if not sec_seul:
        os.makedirs(DOSSIER, exist_ok=True)
        with open(chemin, "w", encoding="utf-8", newline="\n") as f:
            f.write(texte + "\n")
    print(f"Rewind {cle} : {len(out['flux']['t'])} points de flux, {len(out['trace'])} points de trace, "
          f"{len(out['prs'])} trophee(s), {round(len(texte) / 1024, 1)} Ko -> {os.path.relpath(chemin, ROOT)}")
    return chemin


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("seance")
    ap.add_argument("entree")
    ap.add_argument("--cible-allure")
    ap.add_argument("--cible-fc")
    ap.add_argument("--cible-source")
    ap.add_argument("--sec", action="store_true", help="affiche le resume sans rien ecrire")
    a = ap.parse_args(argv)
    ecrire(a.seance, a.entree, cible(a.cible_allure, a.cible_fc, a.cible_source), a.sec)


if __name__ == "__main__":
    sys.exit(main())
