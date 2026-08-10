#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_kpi.py — Verification de la JUSTESSE des KPI, pas de leur presence.

Les autres scripts verifient que les KPI s'affichent et ne plantent pas.
Celui-ci refait le calcul INDEPENDAMMENT depuis les seances loggees, puis
compare a ce que l'app produit reellement dans le navigateur.

Un KPI faux mais bien affiche est plus dangereux qu'un KPI absent :
c'est exactement le scenario de l'ACWR fige a 0.69 pendant quatre semaines.
"""
import datetime as dt
import json
import re
import sys

HTML = "file:///mnt/user-data/outputs/plan-entrainement.html"
D = json.load(open("/tmp/data.json", encoding="utf-8"))

ECARTS = []
OK = []


def cmp(nom, attendu, obtenu, tol=0.0, unite=""):
    """Compare une valeur recalculee a la valeur produite par l'app."""
    if obtenu is None:
        ECARTS.append(f"{nom} : l'app ne fournit PAS la valeur (attendu {attendu}{unite})")
        return
    try:
        a, o = float(attendu), float(obtenu)
    except (TypeError, ValueError):
        if str(attendu) != str(obtenu):
            ECARTS.append(f"{nom} : attendu {attendu!r}, obtenu {obtenu!r}")
        else:
            OK.append(nom)
        return
    if abs(a - o) > tol:
        ECARTS.append(f"{nom} : recalcul {a:g}{unite} vs app {o:g}{unite} (ecart {o-a:+.2f})")
    else:
        OK.append(f"{nom} = {o:g}{unite}")


# ══════════════════════════════════════════════════════════════
# 1. RECALCUL INDEPENDANT DEPUIS LES SEANCES LOGGEES
# ══════════════════════════════════════════════════════════════
seances = []
for wk, arr in D["SBW"].items():
    for s in arr:
        r = s.get("realise") or {}
        if r.get("statut") in ("fait", "partiel") and r.get("km"):
            seances.append({
                "wk": int(wk),
                "date": s.get("date"),
                "km": r.get("km") or 0,
                "re": r.get("re") or 0,
                "dplus": r.get("elevation_gain") or 0,
                "fc": r.get("fc_moy"),
            })

par_semaine = {}
for s in seances:
    d = par_semaine.setdefault(s["wk"], {"km": 0.0, "re": 0, "n": 0, "dplus": 0})
    d["km"] += s["km"]
    d["re"] += s["re"]
    d["dplus"] += s["dplus"]
    d["n"] += 1

print("=" * 66)
print("  AUDIT DE JUSTESSE DES KPI")
print("=" * 66)
print(f"\n{len(seances)} seances loggees avec kilometrage, "
      f"reparties sur {len(par_semaine)} semaines.\n")

print("── Volume recalcule par semaine " + "─" * 32)
for wk in sorted(par_semaine):
    v = par_semaine[wk]
    print(f"   S{wk} : {v['km']:6.1f} km | {v['n']} sorties | {v['dplus']:5} m D+ | RE {v['re']:4}")

# ── ACWR recalcule a la date de reference des donnees ──────────
DERNIERE = max(s["date"] for s in seances if s["date"])
ref = dt.date.fromisoformat(DERNIERE)
aigu = sum(s["re"] for s in seances
           if s["date"] and (ref - dt.date.fromisoformat(s["date"])).days < 7)
chron = sum(s["re"] for s in seances
            if s["date"] and (ref - dt.date.fromisoformat(s["date"])).days < 28)
acwr_calc = round(aigu / (chron / 4), 2) if chron else None

print(f"\n── ACWR recalcule (reference {DERNIERE}) " + "─" * 22)
print(f"   charge aigue 7j   : {aigu}")
print(f"   charge chronique  : {chron} sur 28j, soit {chron/4:.1f}/semaine")
print(f"   ACWR              : {acwr_calc}")

# ── Comparaison avec ACWR_DATA fige dans les donnees ───────────
ad = D.get("ACWR_DATA", {})
print(f"\n── Coherence de ACWR_DATA " + "─" * 38)
cmp("ACWR_DATA.charge7j", aigu, ad.get("charge7j"), tol=0)
cmp("ACWR_DATA.charge28j", chron, ad.get("charge28j"), tol=0)
cmp("ACWR_DATA.acwr", acwr_calc, ad.get("acwr"), tol=0.02)
# le ratio doit etre coherent avec ses propres composantes
if ad.get("charge7j") and ad.get("charge28j"):
    interne = ad["charge7j"] / (ad["charge28j"] / 4)
    cmp("ACWR_DATA coherence interne", round(interne, 2), ad.get("acwr"), tol=0.02)

# ── MONTHLY vs SAISON2026 ──────────────────────────────────────
MON, SAI = D.get("MONTHLY", []), D.get("SAISON2026", {})
print(f"\n── Reconciliation MONTHLY / SAISON2026 " + "─" * 25)
cmp("total km", sum(m["km"] for m in MON), SAI.get("km"), tol=1)
cmp("total sorties", sum(m["sorties"] for m in MON), SAI.get("sorties"), tol=0)
cmp("total D+", sum(m["elev"] for m in MON), SAI.get("elev"), tol=1)

# ══════════════════════════════════════════════════════════════
# 3. COHERENCE DES CHIFFRES CITES DANS LES TEXTES
# ══════════════════════════════════════════════════════════════
# C'est le trou par lequel le bug de l'ACWR est passe : la valeur figee
# avait ete corrigee, mais les revues et slides continuaient d'annoncer
# l'ancien chiffre. Un texte qui contredit un KPI est un KPI faux.
print(f"\n── Chiffres cites dans les textes " + "─" * 30)
ad = D.get("ACWR_DATA", {})
acwr_ref = ad.get("acwr")
chron_ref = round(ad.get("charge28j", 0) / 4) if ad.get("charge28j") else None
aigu_ref = ad.get("charge7j")

# Seuls les textes COURANTS sont controles : une revue passee cite
# legitimement l'ACWR de son epoque, ce n'est pas une incoherence.
derniere = max(par_semaine) if par_semaine else None
textes = []
for s_ in D["SEMAINES"]:
    if s_.get("revue") and s_["num"] == derniere:
        textes.append((f"revue S{s_['num']}", s_["revue"]))
if D.get("REWINDS"):
    rw = D["REWINDS"][-1]
    for i, sl in enumerate(rw.get("slides", [])):
        textes.append((f"Rewind {rw['id']} slide {i+1}",
                       str(sl.get("big", "")) + " " + str(sl.get("txt", ""))))
if ad.get("interpretation"):
    textes.append(("interpretation ACWR", ad["interpretation"]))

suspects = 0
for nom, txt in textes:
    for m in re.finditer(r"ACWR[^0-9]{0,12}([01][.,]\d{2})", txt):
        val = float(m.group(1).replace(",", "."))
        if acwr_ref and abs(val - acwr_ref) > 0.02:
            ECARTS.append(f"{nom} : annonce un ACWR de {m.group(1)} alors que le KPI vaut {acwr_ref}")
            suspects += 1
    for m in re.finditer(r"chronique\D{0,14}(\d{3,4})\s*/\s*semaine", txt):
        val = int(m.group(1))
        if chron_ref and abs(val - chron_ref) > 3:
            ECARTS.append(f"{nom} : annonce une charge chronique de {val}/semaine alors que le KPI donne {chron_ref}")
            suspects += 1
    for m in re.finditer(r"aigu\D{0,10}(\d{3,4})", txt):
        val = int(m.group(1))
        if aigu_ref and abs(val - aigu_ref) > 3:
            ECARTS.append(f"{nom} : annonce une charge aigue de {val} alors que le KPI donne {aigu_ref}")
            suspects += 1
if not suspects:
    OK.append(f"{len(textes)} textes analyses : aucun chiffre en contradiction avec les KPI")

# ══════════════════════════════════════════════════════════════
# 2. CONFRONTATION AVEC LES KPI CALCULES PAR L'APP (runtime)
# ══════════════════════════════════════════════════════════════
print(f"\n── KPI calcules par l'app (navigateur) " + "─" * 25)
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(viewport={"width": 390, "height": 844})
        errs = []
        p.on("pageerror", lambda e: errs.append(str(e)[:120]))
        p.goto(HTML, wait_until="load", timeout=30000)
        p.wait_for_timeout(1800)
        p.evaluate("var o=document.getElementById('rwoverlay');"
                   "if(o){o.classList.remove('on');o.style.display='none';}")

        acwr_app = p.evaluate("typeof _dynamicACWR==='function'?_dynamicACWR():null")
        cmp("ACWR dynamique (app)", acwr_calc, acwr_app, tol=0.15)

        forme = p.evaluate("typeof computeFormeScore==='function'?computeFormeScore():null")
        if not forme:
            ECARTS.append("Forme du jour : computeFormeScore() ne renvoie rien")
        else:
            sc = forme.get("score")
            if sc is None or not (0 <= sc <= 100):
                ECARTS.append(f"Forme du jour : score hors bornes ({sc})")
            elif not forme.get("components"):
                ECARTS.append("Forme du jour : aucune composante detaillee")
            else:
                OK.append(f"Forme du jour = {sc}/100 ({len(forme['components'])} composantes)")

        # volumes Cockpit : doivent croitre avec la fenetre
        p.evaluate("showTab('cockpit')")
        p.wait_for_timeout(600)
        vols = {}
        for w in (2, 4, 8, 12):
            v = p.evaluate(f"(function(){{try{{return _CK.VOL[{w}].a.reduce(function(a,b){{return a+b;}},0);}}catch(e){{return null;}}}})()")
            vols[w] = v
        print(f"   volumes Cockpit par fenetre : {vols}")
        paires = [(2, 4), (4, 8), (8, 12)]
        for a_, b_ in paires:
            if vols.get(a_) is None or vols.get(b_) is None:
                ECARTS.append(f"Cockpit : volume indisponible pour {a_} ou {b_} semaines")
            elif vols[b_] < vols[a_] - 0.5:
                ECARTS.append(f"Cockpit : volume {b_} sem ({vols[b_]:.0f}) < {a_} sem ({vols[a_]:.0f}) — incoherent")
            else:
                OK.append(f"Cockpit volume croissant {a_}->{b_} sem")

        # Comparaison uniquement sur la profondeur reellement couverte par les
        # seances loggees : SBW ne remonte qu'a S25, alors que le Cockpit
        # s'appuie sur HIST, plus profond. Comparer sur 12 semaines produisait
        # un faux ecart de 46 %.
        prem = min(dt.date.fromisoformat(s["date"]) for s in seances if s["date"])
        sem_dispo = max(1, (ref - prem).days // 7)
        fen = max(w for w in (2, 4, 8, 12) if w <= sem_dispo)
        if vols.get(fen):
            born = ref - dt.timedelta(weeks=fen)
            attendu = sum(s["km"] for s in seances
                          if s["date"] and dt.date.fromisoformat(s["date"]) > born)
            ecart = abs(attendu - vols[fen]) / max(attendu, 1) * 100
            if ecart > 12:
                ECARTS.append(f"Cockpit {fen} sem : app {vols[fen]:.0f} km vs recalcul {attendu:.0f} km ({ecart:.0f} % d'ecart)")
            else:
                OK.append(f"Cockpit {fen} sem coherent ({vols[fen]:.0f} km vs {attendu:.0f} recalcules)")

        # semaine courante
        cw = p.evaluate("typeof _curWeek==='function'?_curWeek():null")
        cmp("semaine courante", dt.date.today().isocalendar()[1], cw, tol=0)

        if errs:
            ECARTS.append(f"erreurs JS pendant le calcul des KPI : {errs[0]}")
        b.close()
except Exception as e:
    ECARTS.append(f"runtime indisponible : {str(e)[:120]}")

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 66)
print(f"  CONTROLES CONFORMES ({len(OK)})")
print("=" * 66)
for o in OK:
    print(f"  OK   {o}")
if ECARTS:
    print("\n" + "=" * 66)
    print(f"  ECARTS DETECTES ({len(ECARTS)})")
    print("=" * 66)
    for e in ECARTS:
        print(f"  !!   {e}")
else:
    print("\n  Aucun ecart : tous les KPI verifies sont justes.")
print("=" * 66)
sys.exit(1 if ECARTS else 0)
