#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_reconciliation.py — LE controle generique qui manquait.

CONTEXTE
Cinq KPI ont derive en six semaines (ACWR fige, ACWR faux, MONTHLY aout,
GEAR, record semi). Aucun n'etait un bug de code : c'etaient cinq valeurs
recopiees a la main qui avaient cesse de correspondre a Strava.

Chaque fois, un garde-fou specifique a ete ajoute APRES coup. Resultat :
le controle d'ACWR ne detecte pas une derive de GEAR, celui de MONTHLY ne
voit pas un record perime. On empilait des controles ponctuels sans jamais
poser la regle generale.

CE SCRIPT POSE LA REGLE GENERALE :

    Toute valeur mesurable presente a la fois dans l'app et dans Strava
    doit concorder, quelle qu'elle soit.

Il ne cible pas un KPI en particulier. Il compare l'integralite des champs
numeriques de chaque seance loguee a la reference Strava, et echoue sur
toute divergence.

REFERENTIEL
Le referentiel ci-dessous a ete etabli par reconciliation integrale le
31/08/2026 : 42 seances verifiees une par une, un seul ecart trouve et
corrige (effort relatif du 30/06, 85 au lieu de 60).

MAINTENANCE
A chaque nouvelle seance loguee, ajouter sa ligne au referentiel avec les
valeurs Strava. Le controle A0 ci-dessous signale toute seance loguee qui
n'aurait pas de reference -- il est donc impossible d'oublier.
"""
import os
import sys
for _d in (os.path.dirname(os.path.abspath(__file__)), os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")):
    if os.path.exists(os.path.join(_d, "paths.py")):
        sys.path.insert(0, _d)
from paths import WORK, OUT_HTML, SRC, html_url  # noqa: E402
import json
import sys

DATA = os.path.join(WORK, "data.json")

# ── Referentiel Strava : date -> (km, effort_relatif, D+) ────────────
# Etabli par reconciliation integrale le 31/08/2026.
_REF = json.load(open(os.path.join(SRC, "strava_reference.json"), encoding="utf-8"))
STRAVA = {d: tuple(v) for d, v in _REF["activites"].items()}

# ── Parc chaussures Strava (ne peut pas etre derive des seances : les
#    chaussures servent aussi en randonnee et a velo) ─────────────────
GEAR_STRAVA = dict(_REF["chaussures"])

# ── Totaux mensuels Strava (mois CLOS, course a pied uniquement) ─────
# Verifies mois par mois contre Strava le 31/08/2026. Juin etait faux :
# 82 km / 5 sorties affiches contre 190 km / 15 sorties reels -- un trou
# de 108 km reste invisible parce que le referentiel initial ne couvrait
# que les seances a partir de juin ET que MONTHLY n'etait confronte a
# rien pour les mois anterieurs.
MOIS_STRAVA = {k: tuple(v) for k, v in _REF["mois"].items()}

TOL_KM, TOL_ELEV, TOL_GEAR, TOL_MOIS = 0.06, 2, 5, 3

ECARTS, OK, INFOS = [], [], []

d = json.load(open(DATA, encoding="utf-8"))

seances = {}
for wk, arr in d["SBW"].items():
    for s in arr:
        r = s.get("realise") or {}
        if r.get("statut") in ("fait", "partiel") and (r.get("km") or 0) > 0:
            if s["date"] in seances:
                # plusieurs seances le meme jour : on additionne, comme la reference
                r0, wk0, t0 = seances[s["date"]]
                el0, el1 = r0.get("elevation_gain"), r.get("elevation_gain")
                r = {"km": (r0.get("km") or 0) + (r.get("km") or 0),
                     "re": (r0.get("re") or 0) + (r.get("re") or 0),
                     "elevation_gain": (None if el0 is None or el1 is None else el0 + el1)}
                seances[s["date"]] = (r, wk0, t0 + " +1")
            else:
                seances[s["date"]] = (r, int(wk), s.get("titre", "")[:34])

print("=" * 74)
print("  RECONCILIATION STRAVA — controle generique")
print("=" * 74)
print(f"\n{len(seances)} seance(s) loguee(s) · {len(STRAVA)} reference(s) Strava\n")

# ══ A0 — toute seance loguee doit avoir une reference ═══════════════
# Sans ce controle, il suffirait d'oublier d'ajouter une ligne au
# referentiel pour qu'une seance echappe silencieusement a toute
# verification -- exactement le mode de defaillance qu'on veut fermer.
for dte in sorted(seances):
    if dte not in STRAVA:
        r, wk, t = seances[dte]
        ECARTS.append(f"A0 · {dte} S{wk} « {t} » : loguee mais ABSENTE du referentiel "
                      f"Strava ({r.get('km')} km) — ajouter sa ligne")

# ══ A1 — concordance champ par champ ════════════════════════════════
for dte in sorted(seances, reverse=True):
    if dte not in STRAVA:
        continue
    r, wk, t = seances[dte]
    sk, sre, sel = STRAVA[dte]
    ak, are, ael = r.get("km") or 0, r.get("re") or 0, r.get("elevation_gain")
    pb = []
    if abs(ak - sk) > TOL_KM:
        pb.append(f"km {ak} vs {sk:.2f} sur Strava")
    if are != sre:
        pb.append(f"effort relatif {are} vs {sre}")
    if ael is not None and sel is not None and abs(ael - sel) > TOL_ELEV:
        pb.append(f"D+ {ael} vs {sel}")
    if pb:
        ECARTS.append(f"A1 · {dte} S{wk} « {t} » : " + " ; ".join(pb))
    else:
        OK.append(f"{dte} S{wk} conforme")

# ══ A2 — parc chaussures ════════════════════════════════════════════
for g in d.get("GEAR", []):
    ref = GEAR_STRAVA.get(g["modele"])
    if ref is None:
        INFOS.append(f"{g['modele']} absent du referentiel chaussures")
        continue
    if abs(g["km"] - ref) > TOL_GEAR:
        ECARTS.append(f"A2 · GEAR {g['modele']} : {g['km']} km dans l'app vs {ref} km "
                      f"sur Strava ({g['km']-ref:+d} km) — resynchroniser")
    else:
        OK.append(f"GEAR {g['modele']} conforme ({g['km']} km)")

# ══ A3 — totaux mensuels des mois clos ══════════════════════════════
for m in d.get("MONTHLY", []):
    ref = MOIS_STRAVA.get(m["m"])
    if ref is None:
        continue          # mois en cours : deja couvert par A0/A1
    rkm, rso = ref
    if abs(m["km"] - rkm) > TOL_MOIS or m["sorties"] != rso:
        ECARTS.append(f"A3 · MONTHLY {m['m']} : {m['km']} km / {m['sorties']} sorties dans "
                      f"l'app vs {rkm} km / {rso} sorties sur Strava "
                      f"({m['km']-rkm:+d} km)")
    else:
        OK.append(f"MONTHLY {m['m']} conforme ({m['km']} km / {m['sorties']} sorties)")

# ══ RAPPORT ═════════════════════════════════════════════════════════
print(f"  {len(OK)} controle(s) conforme(s)")
if INFOS:
    print(f"\n── INFORMATIF ({len(INFOS)}) " + "─" * 44)
    for i in INFOS:
        print(f"   {i}")
if ECARTS:
    print(f"\n── ECARTS ({len(ECARTS)}) " + "─" * 48)
    for e in ECARTS:
        print(f"   !! {e}")
else:
    print("\n  Aucun ecart : l'app concorde integralement avec Strava.")
print("\n" + "=" * 74)
print(f"  RESULTAT : {len(ECARTS)} ecart(s) sur {len(OK)+len(ECARTS)} controle(s)")
print("=" * 74)
sys.exit(1 if ECARTS else 0)
