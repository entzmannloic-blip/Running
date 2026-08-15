#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_data.py — Audit STATIQUE exhaustif des donnees (data.json) + du code (app.js).
Complement de preflight/regression/audit_cockpit : cherche les incoherences
METIER et les bombes a retardement, pas seulement les crashs.

Sortie : liste d'anomalies classees par severite.
  BUG      = defaut avere, l'utilisateur le voit ou le subira
  RISQUE   = piege latent, casse a la prochaine occasion
  INFO     = a surveiller, pas bloquant
"""
import json
import re
import datetime as dt
from collections import Counter, defaultdict

DATA = "/tmp/data.json"
APPJS = "/tmp/app.js"

ANO = []
def bug(code, msg):    ANO.append(("BUG", code, msg))
def risque(code, msg): ANO.append(("RISQUE", code, msg))
def info(code, msg):   ANO.append(("INFO", code, msg))

d = json.load(open(DATA, encoding="utf-8"))
js = open(APPJS, encoding="utf-8").read()

SEM = d["SEMAINES"]
SBW = d["SBW"]
TODAY = dt.date.today()   # etait fige au 2026-08-09

# ══ A. COHERENCE DES SEANCES ══════════════════════════════════
toutes = []
for wk, arr in SBW.items():
    for se in arr:
        se["_wk"] = int(wk)
        toutes.append(se)

# A1 — dates dans la bonne semaine ISO
for se in toutes:
    if not se.get("date"):
        continue
    try:
        dd = dt.date.fromisoformat(se["date"])
    except Exception:
        bug("A1", f"S{se['_wk']} '{se.get('titre')}' : date illisible {se['date']!r}")
        continue
    iso = dd.isocalendar()[1]
    if iso != se["_wk"]:
        bug("A1", f"S{se['_wk']} '{se.get('titre')}' date {se['date']} tombe en semaine ISO {iso}")

# A2 — seances passees encore 'a faire' (non loggees)
en_retard = []
for se in toutes:
    if not se.get("date"):
        continue
    dd = dt.date.fromisoformat(se["date"])
    r = se.get("realise") or {}
    statut = r.get("statut", "a_faire")
    if dd < TODAY and statut == "a_faire":
        en_retard.append((se["date"], se["_wk"], se.get("titre"), se.get("type")))
if en_retard:
    repos = [x for x in en_retard if x[3] == "Repos"]
    autres = [x for x in en_retard if x[3] != "Repos"]
    if autres:
        bug("A2", f"{len(autres)} seance(s) passee(s) jamais loggee(s) : "
                  + ", ".join(f"{x[0]} S{x[1]} {x[2]}" for x in autres[:6]))
    if repos:
        info("A2", f"{len(repos)} jour(s) de repos passe(s) restes 'a faire' "
                   f"(cosmetique, ex. {repos[-1][0]} S{repos[-1][1]})")

# A3 — doublons d'id de seance
ids = Counter((se["_wk"], se.get("id")) for se in toutes if se.get("id"))
for i, n in ids.items():
    if n > 1:
        bug("A3", f"id duplique dans S{i[0]} : {i[1]!r} x{n}")

# A4 — dates dupliquees dans une meme semaine
for wk, arr in SBW.items():
    dates = [s["date"] for s in arr if s.get("date")]
    for dte, n in Counter(dates).items():
        if n > 1:
            titres = [s.get("titre") for s in arr if s.get("date") == dte]
            info("A4", f"S{wk} : {n} seances le meme jour {dte} ({', '.join(map(str,titres))})")

# A5 — chaussure retiree encore prescrite/portee
GEAR = {g["modele"]: g for g in d.get("GEAR", [])}
# Strava indique retired=false sur toutes les paires, mais les Clifton 10
# ont bel et bien ete RETIREES DE LA ROTATION le 27/07 sur decision coach
# (delamination de semelle constatee sur photos, puis 1179 km au compteur).
# La decision d'entrainement prime sur le flag Strava, jamais mis a jour.
# Vider cette liste au build 179 etait une regression : le controle A5
# cessait de signaler une prescription de paire retiree.
RETIREES = ["Clifton 10"]
for se in toutes:
    ch = se.get("chaussure") or ""
    for r in RETIREES:
        if r in ch:
            dd = se.get("date", "?")
            r_ = se.get("realise") or {}
            etat = r_.get("statut", "a_faire")
            if etat == "a_faire":
                bug("A5", f"S{se['_wk']} {dd} : chaussure RETIREE '{r}' encore PRESCRITE sur une seance a venir")
            else:
                info("A5", f"S{se['_wk']} {dd} : chaussure retiree '{r}' portee (deja constate)")

# A6 — km realise incoherent avec l'allure et le temps
def parse_allure(a):
    m = re.match(r"^(\d+):(\d{2})", a or "")
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None

for se in toutes:
    r = se.get("realise") or {}
    if not r.get("km") or not r.get("allure") or not r.get("temps"):
        continue
    if re.search(r"[a-zA-Z]", (r["allure"] or "").replace("/km","")): continue
    sec_km = parse_allure(r["allure"])
    m = re.match(r"^(\d+)h(\d{2})", r["temps"] or "")
    if not (sec_km and m):
        continue
    total = int(m.group(1)) * 3600 + int(m.group(2)) * 60
    attendu = total / sec_km
    if abs(attendu - r["km"]) > max(1.2, r["km"] * 0.06):
        bug("A6", f"S{se['_wk']} {se.get('date')} : km/temps/allure incoherents "
                  f"({r['km']} km, {r['temps']}, {r['allure']} => attendu ~{attendu:.1f} km)")

# A7 — FC hors bornes physiologiques
for se in toutes:
    r = se.get("realise") or {}
    for k in ("fc_moy", "fc_max"):
        v = r.get(k)
        if v and not (90 <= v <= 200):
            bug("A7", f"S{se['_wk']} {se.get('date')} : {k}={v} hors bornes plausibles")
    if r.get("fc_moy") and r.get("fc_max") and r["fc_moy"] > r["fc_max"]:
        bug("A7", f"S{se['_wk']} {se.get('date')} : fc_moy {r['fc_moy']} > fc_max {r['fc_max']}")

# ══ A8 — GRAPHIQUE DE STRUCTURE vs SEANCE PRESCRITE ═══════════
# La fiche de seance a DEUX descriptions de la meme chose : 'struct'
# (le texte lu par l'utilisateur) et 'segments' (le graphique). Modifier
# l'une sans l'autre affiche un graphique qui decrit une autre seance.
# Constate sur la longue du 14/08 : le graphique montrait encore la
# longue de 18 km remplacee la veille, sans le bloc allure marathon.
# On ne controle que les seances A VENIR : sur une seance passee, les
# segments documentent legitimement la prescription d'origine.
for se in toutes:
    seg = se.get("segments")
    if not seg or not se.get("date"):
        continue
    if dt.date.fromisoformat(se["date"]) < TODAY:
        continue
    if (se.get("realise") or {}).get("statut", "a_faire") != "a_faire":
        continue
    total_min = seg[-1]["fin"] / 60
    duree = str(se.get("metriques", {}).get("Durée", ""))
    m = re.search(r"(\d+)\s*h\s*(\d*)", duree) or re.search(r"(\d+)", duree)
    if not m:
        continue
    if "h" in duree:
        annonce = int(m.group(1)) * 60 + (int(m.group(2)) if m.lastindex and m.group(2) else 0)
    else:
        annonce = int(m.group(1))
    if abs(total_min - annonce) > 15:
        bug("A8", f"S{se['_wk']} {se['date']} '{se.get('titre')}' : le graphique de structure "
                  f"totalise {total_min:.0f} min alors que la fiche annonce {annonce} min "
                  f"— segments et struct decrivent des seances differentes")
    # coherence des noms : un bloc annonce dans struct doit exister en segment
    noms_seg = " ".join(x["nom"].lower() for x in seg)
    for st in se.get("struct", []):
        cle = st.get("nom", "").lower()
        if "spécifique" in cle or "allure" in cle:
            if "allure" not in noms_seg and "spécifique" not in noms_seg and "seuil" not in noms_seg:
                bug("A8", f"S{se['_wk']} {se['date']} : la fiche decrit un bloc '{st.get('nom')}' "
                          f"absent du graphique de structure")

# ══ B. REVUES & REWINDS ═══════════════════════════════════════
semaines_avec_seances_loggees = sorted({
    se["_wk"] for se in toutes
    if (se.get("realise") or {}).get("statut") in ("fait", "partiel")
})
sem_revue = {s["num"] for s in SEM if s.get("revue")}
for wk in semaines_avec_seances_loggees:
    # La semaine EN COURS n'a pas encore de revue, c'est normal : elle
    # s'ecrit une fois la semaine bouclee. Le 'pass' precedent ne sautait
    # pas l'iteration, la semaine courante etait donc signalee a tort.
    if wk == TODAY.isocalendar()[1]:
        continue
    if wk not in sem_revue:
        bug("B1", f"S{wk} a des seances loggees mais AUCUNE revue de coach")

rw_ids = {r["id"] for r in d.get("REWINDS", [])}
for wk in semaines_avec_seances_loggees:
    if f"S{wk}" not in rw_ids:
        info("B2", f"S{wk} n'a pas de Rewind")

# B3 — Rewinds atteignables depuis l'UI ?
boutons = set(re.findall(r"rwOpen\('(S\d+)'\)", js))
# Un bouton peut aussi etre construit dynamiquement : rwOpen('S${s.num}').
# Dans ce cas tous les Rewinds existants sont atteignables.
dynamique = bool(re.search(r"rwOpen\('S\$\{[^}]+\}'\)", js))
orphelins = [] if dynamique else sorted(rw_ids - boutons)
if orphelins:
    auto = re.search(r"rwAuto.*?REWINDS\[REWINDS\.length-1\]", js, re.S)
    bug("B3", f"Rewinds sans bouton d'ouverture dans l'UI : {', '.join(orphelins)}. "
              f"Le seul bouton est code en dur sur {sorted(boutons) or 'aucun'}"
              + (" ; rwAuto n'ouvre que le dernier, et seulement le lundi." if auto else ""))

# ══ C. CODE : handlers orphelins ══════════════════════════════
definies = set(re.findall(r"function\s+([A-Za-z_$][\w$]*)\s*\(", js))
definies |= set(re.findall(r"(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:function|\()", js))
appelees = set(re.findall(r'onclick=\\?"([A-Za-z_$][\w$]*)\s*\(', js))
BUILTINS = {"showTab","history","window","document","alert","confirm","event",
            "if","for","while","return","switch","catch","function","typeof","new"}
manquantes = sorted(appelees - definies - BUILTINS)
if manquantes:
    bug("C1", f"fonction(s) appelee(s) en onclick mais jamais definie(s) : {', '.join(manquantes)}")

# C2 — stockage navigateur interdit en artifact / fragile en PWA
ls = len(re.findall(r"localStorage", js))
if ls:
    info("C2", f"{ls} usages de localStorage (OK en PWA autonome, mais tout est perdu "
               f"si l'utilisateur vide les donnees du site)")

# C3 — try/catch autour des acces localStorage
brut = re.findall(r"(?<!try\{)localStorage\.(?:get|set)Item", js)
info("C3", f"{len(brut)} acces localStorage reperes — verifier qu'ils sont proteges en navigation privee")

# ══ D. KPI / COHERENCE CHIFFREE ═══════════════════════════════
MON = d.get("MONTHLY", [])
SAI = d.get("SAISON2026", {})
som_km = sum(m["km"] for m in MON)
som_sor = sum(m["sorties"] for m in MON)
if SAI:
    if abs(som_km - SAI.get("km", 0)) > 40:
        bug("D1", f"MONTHLY totalise {som_km} km mais SAISON2026 affiche {SAI.get('km')} km "
                  f"(ecart {som_km - SAI.get('km',0):+d})")
    if abs(som_sor - SAI.get("sorties", 0)) > 3:
        bug("D1", f"MONTHLY totalise {som_sor} sorties mais SAISON2026 affiche {SAI.get('sorties')}")

acwr = d.get("ACWR_DATA", {})
if acwr:
    a7, a28, val = acwr.get("charge7j"), acwr.get("charge28j"), acwr.get("acwr")
    if a7 and a28:
        calc = a7 / (a28 / 4)
        if abs(calc - val) > 0.06:
            bug("D2", f"ACWR affiche {val} mais {a7}/({a28}/4) = {calc:.2f}")

# D3 — volume realise vs cible par semaine
for s in SEM:
    arr = SBW.get(str(s["num"]), [])
    real = sum((x.get("realise") or {}).get("km", 0) for x in arr)
    if real and s.get("km") and real > s["km"] * 1.25:
        info("D3", f"S{s['num']} : {real:.1f} km realises pour {s['km']} km cibles "
                   f"(+{(real/s['km']-1)*100:.0f} %)")

# ══ E. GEAR ═══════════════════════════════════════════════════
for g in d.get("GEAR", []):
    if g["km"] > 900:
        risque("E1", f"{g['modele']} a {g['km']} km — au-dela de la zone de remplacement (700-900 km)")

# ══ RAPPORT ═══════════════════════════════════════════════════
print("=" * 64)
print("  AUDIT STATIQUE DES DONNEES ET DU CODE")
print("=" * 64)
ordre = {"BUG": 0, "RISQUE": 1, "INFO": 2}
for sev in ("BUG", "RISQUE", "INFO"):
    lot = [a for a in ANO if a[0] == sev]
    if not lot:
        continue
    print(f"\n── {sev} ({len(lot)}) " + "─" * (46 - len(sev)))
    for _, code, msg in lot:
        print(f"  [{code}] {msg}")
n_bug = sum(1 for a in ANO if a[0] == "BUG")
print("\n" + "=" * 64)
print(f"  RESULTAT : {n_bug} bug(s), "
      f"{sum(1 for a in ANO if a[0]=='RISQUE')} risque(s), "
      f"{sum(1 for a in ANO if a[0]=='INFO')} info(s)")
print("=" * 64)
# Bloquant uniquement sur les BUG : les INFO sont de la veille, pas des defauts.
import sys as _sys
_sys.exit(1 if n_bug else 0)
