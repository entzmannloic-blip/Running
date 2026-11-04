#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
carto_seance.py — la séance en 3D (build 297) : src/carto/seance-<sem>-<n>.json, lu par l'écran « Le parcours »
ouvert sur une séance (CP.seance dans src/app.js, bouton « Voir en 3D » du Rewind et de la fiche).

    python scripts/carto_seance.py S44-2 strava/20753555995-flux500.json
    (ou log_seance.py ... --rewind strava/<id>-rewind.json --flux3d strava/<id>-flux500.json)

Sources, sans rien inventer :
- le tracé : celui du Rewind (src/rewind/44-2.json), DÉJÀ masqué de 300 m à chaque bout (build 283), reconverti
  de Web Mercator (ancrage + écarts en mètres) en latitude et longitude. Le masque est gardé tel quel : la carte 3D
  ne montre rien de plus que le Rewind publié. Un Rewind sans tracé masqué est refusé.
- l'altitude, le temps, la vitesse et la FC : get_activity_streams(activity_id, resolution=500,
  streams=["time","distance","altitude","velocity_smooth","heart_rate"]), recopié dans strava/<id>-flux500.json :
    {"id":"20753555995","streams":{"time":[…],"distance":[…],"altitude":[…],"velocity_smooth":[…],"heart_rate":[…]}}
  (la réponse de l'outil telle quelle sous "streams" ; dossier strava/ ignoré par Git).

Le fichier écrit suit le format de scripts/carto_course.py (un point tous les 25 m, entiers codés en écarts) :
lat et lon en 1e-5 degré, ele en décimètres, plus t (secondes écoulées depuis le départ de la sortie), v (vitesse
en cm/s) et fc (bpm), et d0 : la distance réelle de la sortie au premier point (le début du tracé masqué).
Les points sont pris à distance réelle constante entre trace_d[0] et trace_d[1] (le tracé réduit de Strava est
un peu plus court que la distance réelle : la position sur le tracé est mise à l'échelle, comme dans le Rewind).
assemble.py le publie en data/carto-seance-44-2.json et ajoute "carto3d" au Rewind publié.
"""
import json
import math
import os
import sys

PAS = 25
RAYON = 6378137.0
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLUX = ("time", "distance", "altitude", "velocity_smooth", "heart_rate")


def latlon(x, y):
    """Web Mercator exact (EPSG:3857, mètres) -> (lat, lon) en degrés : l'inverse de rewind_seance._mercator."""
    return math.degrees(2 * math.atan(math.exp(y / RAYON)) - math.pi / 2), math.degrees(x / RAYON)


def haversine(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * RAYON * math.asin(math.sqrt(h))


def bouche(serie, mini=None, nom=""):
    """Trous (null, NaN, FC sous le minimum : ceinture décrochée) remplacés par la dernière valeur valide."""
    ok = lambda x: isinstance(x, (int, float)) and x == x and (mini is None or x >= mini)
    premiere = next((x for x in serie if ok(x)), None)
    if premiere is None:
        raise SystemExit(f"flux {nom} sans aucune valeur valide")
    out, der = [], premiere
    for x in serie:
        der = x if ok(x) else der
        out.append(der)
    return out


def interp(xs, ys, x):
    """Interpolation linéaire de ys en x (xs croissante)."""
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    lo, hi = 0, len(xs) - 1
    while hi - lo > 1:
        m = (lo + hi) // 2
        if xs[m] <= x:
            lo = m
        else:
            hi = m
    sp = xs[hi] - xs[lo]
    f = (x - xs[lo]) / sp if sp > 0 else 0.0
    return ys[lo] + (ys[hi] - ys[lo]) * f


def deltas(vals):
    return [vals[0]] + [vals[i] - vals[i - 1] for i in range(1, len(vals))]


def construire(rw, flux):
    """Le fichier 3D d'une séance à partir de son Rewind (tracé masqué) et de ses flux Strava à 500 points."""
    tr, a, td = rw.get("trace") or [], rw.get("ancrage") or {}, rw.get("trace_d") or []
    if len(tr) < 2 or not isinstance(a.get("x"), int) or not isinstance(a.get("y"), int) or len(td) != 2 \
            or (rw.get("masque") or 0) < 300:
        raise SystemExit("Rewind sans tracé masqué (ancrage, trace_d, masque >= 300) : rien à mettre en 3D")
    dist = (rw.get("resume") or {}).get("distance")
    if not dist or td[0] < 300 or dist - td[1] < 300:
        raise SystemExit(f"Rewind : trace_d {td} ne laisse pas 300 m masqués à chaque bout ({dist} m)")
    s = flux.get("streams") or flux
    manque = [k for k in FLUX if not s.get(k)]
    if manque:
        raise SystemExit(f"flux absents : {', '.join(manque)}")
    n = len(s["time"])
    if n < 100 or any(len(s[k]) != n for k in FLUX):
        raise SystemExit(f"flux trop courts ou de longueurs différentes ({ {k: len(s[k]) for k in FLUX} })")
    D = bouche(s["distance"], nom="distance")
    for i in range(1, n):          # distance croissante (un GPS qui recule d'un mètre ne casse pas l'interpolation)
        D[i] = max(D[i], D[i - 1])
    T, A, V = bouche(s["time"], nom="time"), bouche(s["altitude"], nom="altitude"), bouche(s["velocity_smooth"], 0, "vitesse")
    F = bouche(s["heart_rate"], 40, "fc")
    if abs(D[-1] - dist) > max(150, dist * 0.03):
        raise SystemExit(f"flux de {D[-1]:.0f} m pour une sortie de {dist:.0f} m : ce n'est pas la même activité ?")

    pts = [latlon(a["x"] + x, a["y"] + y) for x, y in tr]
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + haversine(pts[i - 1], pts[i]))
    S, d0, d1 = cum[-1], float(td[0]), float(td[1])
    if S < 100:
        raise SystemExit("tracé trop court")
    nb = int((d1 - d0) // PAS) + 1
    reels = [d0 + k * PAS for k in range(nb)]
    if d1 - reels[-1] > 1:
        reels.append(d1)
    lats, lons = [p[0] for p in pts], [p[1] for p in pts]
    out = {"lat": [], "lon": [], "ele": [], "t": [], "v": [], "fc": []}
    for r in reels:
        pos = (r - d0) / (d1 - d0) * S
        out["lat"].append(round(interp(cum, lats, pos) * 1e5))
        out["lon"].append(round(interp(cum, lons, pos) * 1e5))
        out["ele"].append(round(interp(D, A, r) * 10))
        out["t"].append(round(interp(D, T, r)))
        out["v"].append(round(interp(D, V, r) * 100))
        out["fc"].append(round(interp(D, F, r)))
    for i in range(1, len(reels)):
        out["t"][i] = max(out["t"][i], out["t"][i - 1])
    return {"pas": PAS, "d0": round(d0), "km": round((reels[-1] - d0) / 1000, 3), "n": len(reels),
            "masque": rw["masque"], "source": "rewind+streams500",
            **{k: deltas(v) for k, v in out.items()}}


def cle_de(seance):
    if not seance.startswith("S") or "-" not in seance:
        raise SystemExit("séance attendue sous la forme S44-2")
    return seance[1:]


def ecrire(seance, entree, sec_seul=False):
    cle = cle_de(seance)
    chemin_rw = os.path.join(ROOT, "src", "rewind", f"{cle}.json")
    if not os.path.exists(chemin_rw):
        raise SystemExit(f"{chemin_rw} absent : le tracé de la 3D vient du Rewind (rewind_seance.py d'abord)")
    rw = json.load(open(chemin_rw, encoding="utf-8"))
    flux = json.load(open(entree, encoding="utf-8"))
    if flux.get("id") and str(flux["id"]) != str(rw.get("strava_id")):
        raise SystemExit(f"flux de l'activité {flux['id']}, Rewind de l'activité {rw.get('strava_id')}")
    out = {"id": f"seance-{cle}", "seance": seance, "strava_id": str(rw.get("strava_id")), **construire(rw, flux)}
    dest = os.path.join(ROOT, "src", "carto", f"seance-{cle}.json")
    alt = [v / 10 for v in _cumul(out["ele"])]
    print(f"{seance} en 3D : {out['n']} points tous les {PAS} m, km {out['d0'] / 1000:.2f} à "
          f"{(out['d0'] + out['km'] * 1000) / 1000:.2f} (300 m masqués à chaque bout), altitude {min(alt):.0f} à {max(alt):.0f} m"
          + (" [--sec : rien écrit]" if sec_seul else f" -> {os.path.relpath(dest, ROOT)}"))
    if not sec_seul:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, separators=(",", ":"))
    return out


def _cumul(a):
    o, v = [], 0
    for x in a:
        v += x
        o.append(v)
    return o


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    sec = "--sec" in args
    args = [x for x in args if x != "--sec"]
    if len(args) != 2:
        sys.exit(__doc__)
    ecrire(args[0], args[1], sec)
    return 0


if __name__ == "__main__":
    sys.exit(main())
