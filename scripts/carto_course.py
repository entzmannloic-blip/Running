#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
carto_course.py — trace d'une course (GPX, ou CSV lat,lon,ele) -> src/carto/<id>.json, lu par l'écran
« Le parcours » (carte 3D, profil, pentes, terrain). Voir docs/ENRICHISSEMENT.md, section « Carte d'une course ».

    python scripts/carto_course.py saintexpress src/carto/saintexpress-trace.csv
    python scripts/carto_course.py nice chemin/vers/MAM2026_parcours.gpx

Le fichier écrit contient la trace rééchantillonnée tous les PAS mètres (interpolation linéaire le long de
la distance), en entiers : latitude et longitude en 1e-5 degré, altitude en décimètres, codées en écarts
(le premier élément est absolu, les suivants sont des différences) pour rester léger. Pentes, montées,
heures de passage et terrain sont calculés par l'app (src/app.js, module « Parcours »), pas ici.
assemble.py publie src/carto/<id>.json en data/carto-<id>.json ; le dossier de course y renvoie par
DOSSIERS[<id>]["carto"]["trace"] dans src/gen.py.
"""
import csv
import json
import math
import os
import re
import sys

PAS = 25  # metres entre deux points de la trace publiee
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def lire(chemin):
    """[(lat, lon, ele)] depuis un GPX (trkpt) ou un CSV avec les colonnes lat, lon, ele."""
    if chemin.lower().endswith(".csv"):
        with open(chemin, encoding="utf-8") as f:
            return [(float(r["lat"]), float(r["lon"]), float(r["ele"])) for r in csv.DictReader(f)]
    txt = open(chemin, encoding="utf-8").read()
    pts = []
    for m in re.finditer(r'<trkpt\s+lat="([-\d.]+)"\s+lon="([-\d.]+)"\s*>(.*?)</trkpt>', txt, re.S):
        e = re.search(r"<ele>([-\d.]+)</ele>", m.group(3))
        if e:
            pts.append((float(m.group(1)), float(m.group(2)), float(e.group(1))))
    return pts


def haversine(a, b):
    r = 6371008.8
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    return 2 * r * math.asin(math.sqrt(math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2))


def reechantillonner(pts, pas=PAS):
    """Points tous les `pas` metres le long de la trace (dernier point inclus)."""
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + haversine(pts[i - 1], pts[i]))
    total, out, j = cum[-1], [], 1
    n = int(total // pas)
    for k in range(n + 1):
        x = k * pas
        while j < len(cum) - 1 and cum[j] < x:
            j += 1
        a, b = pts[j - 1], pts[j]
        t = 0.0 if cum[j] == cum[j - 1] else (x - cum[j - 1]) / (cum[j] - cum[j - 1])
        out.append(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))
    if total - n * pas > 1:
        out.append(pts[-1])
    return out, total


def deltas(vals):
    return [vals[0]] + [vals[i] - vals[i - 1] for i in range(1, len(vals))]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    cid, chemin = sys.argv[1], sys.argv[2]
    pts = lire(chemin)
    if len(pts) < 10:
        sys.exit(f"{chemin} : moins de 10 points lus")
    for a, b in zip(pts, pts[1:]):
        if haversine(a, b) > 1000:
            sys.exit(f"{chemin} : saut de plus d'1 km entre deux points ({a} -> {b}) — trace incomplète ?")
    rs, total = reechantillonner(pts)
    out = {"id": cid, "pas": PAS, "km": round(total / 1000, 3), "n": len(rs),
           "lat": deltas([round(p[0] * 1e5) for p in rs]),
           "lon": deltas([round(p[1] * 1e5) for p in rs]),
           "ele": deltas([round(p[2] * 10) for p in rs])}
    dest = os.path.join(ROOT, "src", "carto", f"{cid}.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, separators=(",", ":"))
    alt = [p[2] for p in rs]
    print(f"{dest} : {len(pts)} points lus -> {len(rs)} points tous les {PAS} m, {total / 1000:.2f} km, "
          f"altitude {min(alt):.0f} a {max(alt):.0f} m")


if __name__ == "__main__":
    main()
