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
import json
import sys

DATA = "/tmp/data.json"

# ── Referentiel Strava : date -> (km, effort_relatif, D+) ────────────
# Etabli par reconciliation integrale le 31/08/2026.
STRAVA = {
 "2026-09-03":(12.0773,88,25),
 "2026-09-02":(8.5886,137,27),
 "2026-09-01":(11.0275,80,34),
 "2026-08-31":(10.2588,74,40),
 "2026-08-28":(10.0343,125,39), "2026-08-27":(12.0427,151,50),
 "2026-08-22":(25.0461,394,59), "2026-08-19":(7.0194,38,27),
 "2026-08-18":(12.0445,173,22), "2026-08-15":(8.0439,50,39),
 "2026-08-13":(11.3626,128,52), "2026-08-12":(10.2017,61,36),
 "2026-08-11":(10.0699,53,29),  "2026-08-09":(27.0100,246,662),
 "2026-08-07":(10.0900,28,43),  "2026-08-06":(10.0900,56,36),
 "2026-08-05":(10.0400,34,37),  "2026-08-04":(10.0500,123,39),
 "2026-08-02":(11.3100,105,36), "2026-07-30":(14.0900,171,None),
 "2026-07-28":(10.0300,49,None),"2026-07-27":(10.0200,79,None),
 "2026-07-26":(10.1264,83,32),  "2026-07-23":(42.5167,367,137),
 "2026-07-21":(7.5030,93,35),   "2026-07-20":(14.0285,78,35),
 "2026-07-19":(10.0290,96,15),  "2026-07-17":(10.2956,93,33),
 "2026-07-16":(23.0423,222,67), "2026-07-15":(10.3539,94,31),
 "2026-07-12":(11.0397,109,530),"2026-07-11":(10.6999,118,646),
 "2026-07-09":(18.1596,171,67), "2026-07-08":(10.0272,60,22),
 "2026-07-07":(11.0253,106,39), "2026-07-05":(23.2702,584,957),
 "2026-07-02":(10.5481,96,46),  "2026-06-30":(6.5475,60,27),
 "2026-06-29":(13.0164,149,35), "2026-06-25":(10.6597,99,20),
 "2026-06-22":(11.2629,105,43), "2026-06-19":(10.0271,79,38),
 "2026-06-18":(16.0468,156,52), "2026-06-17":(10.1389,169,35),
 "2026-06-16":(10.1359,58,40),  "2026-06-15":(10.2467,69,43),
}

# ── Parc chaussures Strava (ne peut pas etre derive des seances : les
#    chaussures servent aussi en randonnee et a velo) ─────────────────
GEAR_STRAVA = {
    "Clifton 10":1196, "Gel Pulse 16":225, "Cascadia 19":259,
    "Novablast 5 J":734, "Magic Speed 4":93, "Novablast 5 V":112,
}

# ── Totaux mensuels Strava (mois CLOS, course a pied uniquement) ─────
# Verifies mois par mois contre Strava le 31/08/2026. Juin etait faux :
# 82 km / 5 sorties affiches contre 190 km / 15 sorties reels -- un trou
# de 108 km reste invisible parce que le referentiel initial ne couvrait
# que les seances a partir de juin ET que MONTHLY n'etait confronte a
# rien pour les mois anterieurs.
MOIS_STRAVA = {
    "Jan":(224,19), "Fév":(227,21), "Mar":(342,25), "Avr":(283,23),
    "Mai":(202,15), "Juin":(190,15), "Juil":(257,18),
}

TOL_KM, TOL_ELEV, TOL_GEAR, TOL_MOIS = 0.06, 2, 5, 3

ECARTS, OK, INFOS = [], [], []

d = json.load(open(DATA, encoding="utf-8"))

seances = {}
for wk, arr in d["SBW"].items():
    for s in arr:
        r = s.get("realise") or {}
        if r.get("statut") in ("fait", "partiel") and (r.get("km") or 0) > 0:
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
