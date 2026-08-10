#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_dette.py — Dette technique et incoherences METIER.

Les autres audits verifient que ca marche (runtime), que c'est juste (kpi)
et que les donnees se tiennent (data). Celui-ci cherche ce qui pourrit
doucement : champs morts, code mort, valeurs contradictoires entre
sections, protections manquantes.

Rien ici ne fait planter l'app aujourd'hui. Tout ici finit par couter cher.
"""
import json
import re

D = json.load(open("/tmp/data.json", encoding="utf-8"))
JS = open("/tmp/app.js", encoding="utf-8").read()
GEN = open("/tmp/gen.py", encoding="utf-8").read()
HTML = open("/mnt/user-data/outputs/plan-entrainement.html", encoding="utf-8").read()

DETTE, INCO, INFO = [], [], []

# ══ 1. CHAMPS DE DONNEES EXPORTES MAIS JAMAIS LUS ══════════════
# assemble.py renomme certaines cles a l'injection : on teste les deux noms.
ALIAS = {"SBW": "SEANCES_BY_WEEK"}
for cle in sorted(D.keys()):
    noms = {cle, ALIAS.get(cle, cle)}
    if not any(re.search(r"\b" + re.escape(n) + r"\b", JS) for n in noms):
        taille = len(json.dumps(D[cle], ensure_ascii=False))
        DETTE.append(f"champ '{cle}' exporte dans data.json mais JAMAIS lu par app.js "
                     f"({taille} octets de charge morte)")

# ══ 2. FONCTIONS JS DEFINIES ET JAMAIS APPELEES ════════════════
definies = set(re.findall(r"function\s+([A-Za-z_$][\w$]*)\s*\(", JS))
ignore = {"main", "init"}
mortes = []
for f in sorted(definies - ignore):
    # compte les occurrences hors ligne de definition
    appels = len(re.findall(r"(?<!function\s)\b" + re.escape(f) + r"\s*\(", JS))
    # une fonction peut n'etre appelee que depuis un onclick du HTML genere
    via_html = bool(re.search(re.escape(f) + r"\s*\(", HTML))
    if appels == 0 and not via_html and f"'{f}'" not in JS and f'"{f}"' not in JS:
        mortes.append(f)
if mortes:
    DETTE.append(f"{len(mortes)} fonction(s) definie(s) jamais appelee(s) : {', '.join(mortes[:8])}")

# ══ 3. INCOHERENCES METIER ═════════════════════════════════════
prof = D.get("PROFIL", {})
recs = D.get("RECORDS", [])
proj = D.get("PROJ", {})

cible = prof.get("cible_marathon")
for r in recs:
    if "arathon" in str(r.get("label", "")):
        val = str(r.get("val", ""))
        if cible and val and val.replace("~", "") != str(cible):
            INCO.append(f"objectif marathon contradictoire : PROFIL.cible_marathon = {cible}, "
                        f"mais RECORDS affiche « {r.get('label')} : {val} » ({r.get('sub')})")

if proj.get("mp_goal") and cible:
    # 3h45 => 5:20/km sur 42.195 ; verifie la coherence allure/temps
    m = re.match(r"(\d+)h(\d+)", str(cible))
    a = re.match(r"(\d+):(\d+)", str(proj["mp_goal"]))
    if m and a:
        sec_cible = int(m.group(1)) * 3600 + int(m.group(2)) * 60
        sec_allure = (int(a.group(1)) * 60 + int(a.group(2))) * 42.195
        if abs(sec_cible - sec_allure) > 240:
            INCO.append(f"cible {cible} et allure {proj['mp_goal']} incoherentes : "
                        f"l'allure donne {sec_allure/3600:.2f} h, la cible {sec_cible/3600:.2f} h")

# ══ 4. CHAUSSURE RETIREE PRESCRITE SUR DES SEANCES A VENIR ═════
RETIREES = ["Clifton 10"]
for wk, arr in D["SBW"].items():
    for s in arr:
        ch = s.get("chaussure") or ""
        st = (s.get("realise") or {}).get("statut", "a_faire")
        if st == "a_faire" and any(r in ch for r in RETIREES):
            INCO.append(f"S{wk} {s.get('date')} : chaussure retiree '{ch}' prescrite sur une seance A VENIR")

# ══ 5. PROTECTION DES ACCES localStorage ═══════════════════════
# on isole les acces et on regarde s'ils sont dans un try
non_proteges = 0
for m in re.finditer(r"localStorage\.(getItem|setItem|removeItem)", JS):
    debut = max(0, m.start() - 120)
    if "try" not in JS[debut:m.start()]:
        non_proteges += 1
if non_proteges:
    DETTE.append(f"{non_proteges} acces localStorage sans try/catch visible en amont — "
                 f"leve une exception en navigation privee sur certains navigateurs")

# ══ 6. VALEURS EN DUR SUSPECTES DANS gen.py ════════════════════
for m in re.finditer(r'"(charge7j|charge28j|acwr)"\s*:\s*([\d.]+)', GEN):
    INFO.append(f"KPI '{m.group(1)}' fige en dur dans gen.py (= {m.group(2)}) — "
                f"doit etre recalcule a chaque log, sinon il derive silencieusement")

# ══ 7. SEMAINES SANS OBJECTIF / CHARGE RENSEIGNES ══════════════
for s in D["SEMAINES"]:
    if not s.get("objectif"):
        DETTE.append(f"S{s['num']} : aucun objectif renseigne")

# ══ RAPPORT ════════════════════════════════════════════════════
print("=" * 66)
print("  AUDIT DETTE TECHNIQUE & INCOHERENCES METIER")
print("=" * 66)
for titre, lot in (("INCOHERENCES METIER (visibles par l'utilisateur)", INCO),
                   ("DETTE TECHNIQUE", DETTE),
                   ("POINTS DE VIGILANCE", INFO)):
    print(f"\n── {titre} ({len(lot)}) " + "─" * max(2, 40 - len(titre) // 2))
    if not lot:
        print("   rien a signaler")
    for x in lot:
        print(f"   • {x}")
print("\n" + "=" * 66)
print(f"  {len(INCO)} incoherence(s) · {len(DETTE)} dette(s) · {len(INFO)} vigilance(s)")
print("=" * 66)
