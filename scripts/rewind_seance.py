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

Trace (fond de carte, build 283) : les 300 premiers et derniers metres sont retires (l'app est publique), le reste est
projete en Web Mercator exact avec un ancrage (EPSG:3857) pour poser les tuiles. Rewind deja ecrit :
    python scripts/rewind_seance.py S44-2 strava/<id>-polyline.json --retrace
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


MASQUE_M = 300      # metres masques au depart et a l'arrivee (zone de confidentialite, comme Strava)
RAYON = 6378137.0   # rayon de la sphere Web Mercator (EPSG:3857)


def _sol(a, b):
    """Distance au sol en metres entre deux points (lat, lng) : haversine."""
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * RAYON * math.asin(math.sqrt(h))


def _mercator(p):
    return RAYON * math.radians(p[1]), RAYON * math.log(math.tan(math.pi / 4 + math.radians(p[0]) / 2))


def projette(pts, distance=None, masque=MASQUE_M):
    """Trace masque et projete en Web Mercator exact (EPSG:3857).

    Retire les `masque` premiers et derniers metres (le polyline reduit de Strava est un peu plus court que la
    distance reelle : la coupe est faite sur la plus grande des deux mesures, donc jamais sous `masque` metres
    reels), puis place les points en metres Mercator relatifs a un ancrage entier (x, y en EPSG:3857) : la tuile
    de fond de carte se pose ainsi sur les rues. Les metres Mercator sont etires de 1/cos(lat) par rapport au sol,
    sans changer les formes.
    Retourne {"trace": [[x, y], ...], "ancrage": {"x", "y"}, "trace_d": [debut, fin] (metres reels le long de la
    sortie), "masque": metres}. Trace vide si la sortie est trop courte pour qu'il en reste quelque chose."""
    vide = {"trace": [], "ancrage": None, "trace_d": None, "masque": masque}
    if len(pts) < 2:
        return vide
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + _sol(pts[i - 1], pts[i]))
    long_poly = cum[-1]
    reel = float(distance) if distance else long_poly
    k = reel / long_poly if long_poly else 1.0
    coupe = masque * max(1.0, 1.0 / k)          # en metres de polyline
    if long_poly < 2 * coupe + 100:
        return vide

    def interp(d):
        j = next(i for i in range(1, len(cum)) if cum[i] >= d)
        f = (d - cum[j - 1]) / ((cum[j] - cum[j - 1]) or 1.0)
        return (pts[j - 1][0] + (pts[j][0] - pts[j - 1][0]) * f, pts[j - 1][1] + (pts[j][1] - pts[j - 1][1]) * f)

    gardes = [interp(coupe)] + [pts[i] for i in range(len(pts)) if coupe < cum[i] < long_poly - coupe] \
        + [interp(long_poly - coupe)]
    m = [_mercator(p) for p in gardes]
    x0, y0 = math.floor(min(x for x, _ in m)), math.floor(min(y for _, y in m))
    return {"trace": [[round(x - x0), round(y - y0)] for x, y in m], "ancrage": {"x": x0, "y": y0},
            "trace_d": [math.ceil(coupe * k), math.floor(reel - coupe * k)], "masque": masque}


def reduit(n, m=MAX_POINTS):
    """Indices de m points repartis sur n (premier et dernier compris)."""
    if n <= m:
        return list(range(n))
    return sorted({round(i * (n - 1) / (m - 1)) for i in range(m)})


def bouche(serie, mini=None):
    """Remplace les trous (null, NaN, FC sous le minimum : ceinture decrochee) par la derniere valeur valide."""
    ok = lambda x: isinstance(x, (int, float)) and x == x and (mini is None or x >= mini)
    premiere = next((x for x in serie if ok(x)), None)
    if premiere is None:
        raise SystemExit("flux sans aucune valeur valide")
    out, der = [], premiere
    for x in serie:
        der = x if ok(x) else der
        out.append(der)
    return out


def trace_de(e):
    """Champs du tracé (masqué, Mercator) à partir de l'entrée Strava ; rien si pas de polyline."""
    if not e.get("reduced_polyline"):
        return {"trace": []}
    r = projette(decode_polyline(e["reduced_polyline"]), (e.get("summary") or {}).get("distance"))
    return {k: v for k, v in r.items() if v is not None}


def construire(e, cib=None):
    st = e["streams"]
    n = len(st["time"])
    for c, k in FLUX:
        if c == "fc" and not st.get(k):
            continue  # pas de ceinture ni de capteur : le Rewind saute l'image du coeur
        if len(st.get(k) or []) != n:
            raise SystemExit(f"flux {k} absent ou de longueur differente ({len(st.get(k) or [])} pour {n})")
        st[k] = bouche(st[k], 40 if c == "fc" else None)
    if abs(st["distance"][-1] - e["summary"]["distance"]) > 60:
        raise SystemExit("le flux de distance ne correspond pas a la distance Strava")
    idx = reduit(n)
    flux = {c: [st[k][i] for i in idx] for c, k in FLUX if st.get(k)}
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
           "flux": flux, **trace_de(e), "tours": perf.get("laps") or [],
           "meilleurs": [b[:2] for b in perf.get("best_efforts", [])], "prs": prs}
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


def retrace(seance, entree):
    """Refait seulement le tracé d'un Rewind existant (masquage + ancrage) en relisant sa polyline ; le reste est gardé."""
    m = re.fullmatch(r"S?(\d+)-(\d+)", seance)
    if not m:
        raise SystemExit(f"seance illisible : {seance!r} (ex. S44-2)")
    chemin = os.path.join(DOSSIER, f"{int(m.group(1))}-{int(m.group(2))}.json")
    with open(chemin, encoding="utf-8") as f:
        out = json.load(f)
    with open(entree, encoding="utf-8") as f:
        e = json.load(f)
    if str(e["id"]) != str(out["strava_id"]):
        raise SystemExit(f"l'entree est l'activite {e['id']}, le Rewind {seance} est l'activite {out['strava_id']}")
    for k in ("trace", "ancrage", "trace_d", "masque"):
        out.pop(k, None)
    out.update(trace_de(e))
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"Rewind {seance} : tracé refait, {len(out['trace'])} points, "
          f"{'masqué à ' + str(out['masque']) + ' m' if out.get('ancrage') else 'sans tracé (sortie trop courte)'}")
    return chemin


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("seance")
    ap.add_argument("entree")
    ap.add_argument("--cible-allure")
    ap.add_argument("--cible-fc")
    ap.add_argument("--cible-source")
    ap.add_argument("--sec", action="store_true", help="affiche le resume sans rien ecrire")
    ap.add_argument("--retrace", action="store_true",
                    help="refait seulement le trace (masque 300 m + ancrage) d'un Rewind existant ; l'entree ne demande "
                         "que id, summary.distance et reduced_polyline")
    a = ap.parse_args(argv)
    if a.retrace:
        retrace(a.seance, a.entree)
        return 0
    ecrire(a.seance, a.entree, cible(a.cible_allure, a.cible_fc, a.cible_source), a.sec)


if __name__ == "__main__":
    sys.exit(main())
