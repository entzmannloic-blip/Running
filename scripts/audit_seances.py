#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_seances.py — Coherence INTERNE de chaque fiche de seance.

Une fiche decrit la meme seance a plusieurs endroits : titre, metriques,
struct (texte lu), segments (graphique), objectif, et realise. Rien ne
garantit structurellement que ces descriptions concordent — c'est
exactement le defaut qui a produit le graphique desynchronise du 14/08.

Ce script confronte ces descriptions entre elles, seance par seance,
sur les 132 fiches.
"""
import datetime as dt
import json
import re
import sys

D = json.load(open("/tmp/data.json", encoding="utf-8"))
TODAY = dt.date.today()

BUGS, ALERTES, INFOS = [], [], []
def bug(c, m):    BUGS.append((c, m))
def alerte(c, m): ALERTES.append((c, m))
def info(c, m):   INFOS.append((c, m))

toutes = []
for wk, arr in D["SBW"].items():
    for se in arr:
        se["_wk"] = int(wk)
        toutes.append(se)
toutes.sort(key=lambda x: (x.get("date") or ""))

A_VENIR = [s for s in toutes
           if s.get("date") and dt.date.fromisoformat(s["date"]) >= TODAY
           and (s.get("realise") or {}).get("statut", "a_faire") == "a_faire"]
PASSEES = [s for s in toutes if s not in A_VENIR]


def duree_annoncee(se):
    """Minutes annoncees dans les metriques, ou None."""
    d = str(se.get("metriques", {}).get("Durée", "")).strip()
    if not d:
        return None
    d = d.replace("~", "")
    m = re.match(r"^(\d+)\s*h\s*(\d{0,2})", d)
    if m:
        return int(m.group(1)) * 60 + (int(m.group(2)) if m.group(2) else 0)
    m = re.match(r"^(\d+)\s*[-–]\s*(\d+)", d)      # "45-60 min"
    if m:
        return (int(m.group(1)) + int(m.group(2))) // 2
    m = re.match(r"^(\d+):(\d{2})$", d)             # "58:31" = mm:ss
    if m:
        return int(m.group(1))
    m = re.match(r"^(\d+)", d)
    return int(m.group(1)) if m else None


def dist_annoncee(se):
    d = str(se.get("metriques", {}).get("Distance", ""))
    m = re.search(r"(\d+(?:[.,]\d+)?)", d.replace("~", ""))
    return float(m.group(1).replace(",", ".")) if m else None


print("=" * 68)
print("  AUDIT SEANCE PAR SEANCE — coherence interne des fiches")
print("=" * 68)
print(f"\n{len(toutes)} seances au total · {len(A_VENIR)} a venir · {len(PASSEES)} passees\n")

# ══ 1. GRAPHIQUE vs FICHE (seances a venir) ═══════════════════
for se in A_VENIR:
    seg = se.get("segments")
    if not seg:
        continue
    tot = seg[-1]["fin"] / 60
    ann = duree_annoncee(se)
    if ann and abs(tot - ann) > 15:
        bug("S1", f"S{se['_wk']} {se['date']} '{se.get('titre')}' : graphique {tot:.0f} min "
                  f"vs fiche {ann} min (ecart {tot-ann:+.0f})")
    noms = " ".join(x["nom"].lower() for x in seg)
    for st in se.get("struct", []):
        cle = (st.get("nom") or "").lower()
        if any(k in cle for k in ("spécifique", "allure", "seuil", "fractionné", "bloc")):
            if not any(k in noms for k in ("spécifique", "allure", "seuil", "fractionné", "bloc", "×", "x")):
                bug("S1", f"S{se['_wk']} {se['date']} : bloc '{st.get('nom')}' decrit dans la fiche "
                          f"mais absent du graphique")

# ══ 2. CHAINAGE DES SEGMENTS ══════════════════════════════════
for se in toutes:
    seg = se.get("segments")
    if not seg:
        continue
    if seg[0]["debut"] != 0:
        bug("S2", f"S{se['_wk']} {se['date']} : le graphique ne demarre pas a 0 "
                  f"(premier segment a {seg[0]['debut']}s)")
    for i in range(len(seg) - 1):
        if seg[i]["fin"] != seg[i + 1]["debut"]:
            bug("S2", f"S{se['_wk']} {se['date']} : trou ou chevauchement entre "
                      f"'{seg[i]['nom']}' (fin {seg[i]['fin']}) et '{seg[i+1]['nom']}' "
                      f"(debut {seg[i+1]['debut']})")
    for x in seg:
        if x["fin"] - x["debut"] != x["duree"]:
            bug("S2", f"S{se['_wk']} {se['date']} segment '{x['nom']}' : duree {x['duree']} "
                      f"incoherente avec debut/fin ({x['fin']-x['debut']})")
        if not (0 < x.get("hauteur", 0) <= 100):
            alerte("S2", f"S{se['_wk']} {se['date']} segment '{x['nom']}' : hauteur "
                         f"{x.get('hauteur')} hors bornes")

# ══ 3. COHERENCE DISTANCE / DUREE / ALLURE ════════════════════
for se in A_VENIR:
    km = dist_annoncee(se)
    mn = duree_annoncee(se)
    al = str(se.get("metriques", {}).get("Allure", ""))
    m = re.search(r"(\d+):(\d{2})", al)
    if not (km and mn and m):
        continue
    sec_km = int(m.group(1)) * 60 + int(m.group(2))
    attendu = km * sec_km / 60
    # tolerance large : l'allure affichee est souvent une fourchette
    if abs(attendu - mn) > max(20, mn * 0.35):
        alerte("S3", f"S{se['_wk']} {se['date']} '{se.get('titre')}' : {km:g} km a {al} "
                     f"donnerait ~{attendu:.0f} min, la fiche annonce {mn} min")

# ══ 4. SEANCES REALISEES vs PRESCRIT ══════════════════════════
ecarts_vol = []
for se in PASSEES:
    r = se.get("realise") or {}
    if r.get("statut") != "fait" or not r.get("km"):
        continue
    km_p = dist_annoncee(se)
    if not km_p:
        continue
    ecart = (r["km"] - km_p) / km_p * 100
    if abs(ecart) > 30:
        ecarts_vol.append((se["date"], se["_wk"], se.get("titre"), km_p, r["km"], ecart))
if ecarts_vol:
    for d, wk, t, p, rr, e in ecarts_vol[-8:]:
        info("S4", f"S{wk} {d} '{t[:34]}' : prescrit {p:g} km, realise {rr:g} km ({e:+.0f} %)")

# ══ 5. CHAUSSURES ═════════════════════════════════════════════
GEAR = {g["modele"]: g["km"] for g in D.get("GEAR", [])}
for se in A_VENIR:
    ch = se.get("chaussure")
    if not ch:
        alerte("S5", f"S{se['_wk']} {se['date']} '{se.get('titre')}' : aucune chaussure prescrite")
        continue
    trouve = [m for m in GEAR if m.lower() in ch.lower() or ch.lower() in m.lower()]
    if not trouve:
        bug("S5", f"S{se['_wk']} {se['date']} : chaussure '{ch}' absente du parc")
    elif GEAR[trouve[0]] > 900:
        bug("S5", f"S{se['_wk']} {se['date']} : '{trouve[0]}' prescrite alors qu'elle affiche "
                  f"{GEAR[trouve[0]]} km (zone de remplacement depassee)")

# ══ 6. CHAMPS ESSENTIELS ══════════════════════════════════════
for se in A_VENIR:
    for champ in ("titre", "type", "objectif", "metriques"):
        if not se.get(champ):
            bug("S6", f"S{se['_wk']} {se['date']} : champ '{champ}' vide")
    if not se.get("struct") and not se.get("segments"):
        alerte("S6", f"S{se['_wk']} {se['date']} '{se.get('titre')}' : ni struct ni segments")

# ══ 7. ORDRE CHRONOLOGIQUE DANS LA SEMAINE ════════════════════
for wk, arr in D["SBW"].items():
    dates = [(s.get("date"), s.get("titre")) for s in arr if s.get("date")]
    tri = sorted(d for d, _ in dates)
    if [d for d, _ in dates] != tri:
        info("S7", f"S{wk} : les seances ne sont pas stockees dans l'ordre chronologique "
                   f"(l'affichage doit trier)")

# ══ 8. COHERENCE TYPE vs INTENSITE ════════════════════════════
for se in A_VENIR:
    t = (se.get("type") or "").lower()
    fc = str(se.get("metriques", {}).get("FC", ""))
    nums = [int(x) for x in re.findall(r"\d{3}", fc)]
    if not nums:
        continue
    if ("ef" in t or "récup" in t or "endurance" in t) and max(nums) > 165:
        alerte("S8", f"S{se['_wk']} {se['date']} '{se.get('titre')}' : type '{se.get('type')}' "
                     f"mais FC cible monte a {max(nums)}")

# ══ RAPPORT ═══════════════════════════════════════════════════
for titre, lot in (("BUGS — incoherences dans la fiche", BUGS),
                   ("ALERTES — a verifier", ALERTES),
                   ("INFORMATIF", INFOS)):
    print(f"\n── {titre} ({len(lot)}) " + "─" * max(2, 44 - len(titre) // 2))
    if not lot:
        print("   rien a signaler")
    for c, m in lot:
        print(f"   [{c}] {m}")

print("\n" + "=" * 68)
print(f"  RESULTAT : {len(BUGS)} bug(s) · {len(ALERTES)} alerte(s) · {len(INFOS)} info(s)")
print("=" * 68)
sys.exit(1 if BUGS else 0)
