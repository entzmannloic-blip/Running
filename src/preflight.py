#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preflight.py — Verification automatique AVANT chaque push (build Running PWA).

Encode chaque erreur passee en test mecanique : une erreur qui devient un
check ne peut plus etre oubliee. A lancer depuis /tmp apres gen.py + assemble.py,
juste avant le push GitHub.

    python3 preflight.py

Sortie : liste PASS/FAIL. Si un seul FAIL critique => NE PAS PUSHER.
Chaque check reference la lecon correspondante dans docs/LESSONS.md.
"""
import json
import os
import re
import subprocess
import sys

TMP = "/tmp"
OUT_HTML = "/mnt/user-data/outputs/plan-entrainement.html"
DATA = os.path.join(TMP, "data.json")
GEN = os.path.join(TMP, "gen.py")
APP = os.path.join(TMP, "app.js")

CRIT = []   # echecs bloquants
WARN = []   # avertissements non bloquants
OK = []


def crit(msg):
    CRIT.append(msg)


def warn(msg):
    WARN.append(msg)


def ok(msg):
    OK.append(msg)


# ─────────────────────────────────────────────────────────────
# L01 — Pipeline : gen.py et assemble.py doivent tourner depuis /tmp
#       Sinon assemble.py lit un data.json perime => HTML stale.
# ─────────────────────────────────────────────────────────────
def check_pipeline_fresh():
    if not os.path.exists(DATA):
        crit("L01 pipeline : /tmp/data.json absent — gen.py n'a pas tourne depuis /tmp")
        return
    if not os.path.exists(OUT_HTML):
        crit("L01 pipeline : HTML de sortie absent — assemble.py n'a pas tourne")
        return
    # data.json doit etre plus recent que gen.py (regenere apres la derniere edition)
    if os.path.getmtime(DATA) < os.path.getmtime(GEN):
        crit("L01 pipeline : data.json plus vieux que gen.py — RELANCER gen.py depuis /tmp")
    else:
        ok("L01 pipeline : data.json frais (posterieur a gen.py)")
    # HTML doit etre plus recent que data.json
    if os.path.getmtime(OUT_HTML) < os.path.getmtime(DATA):
        crit("L01 pipeline : HTML plus vieux que data.json — RELANCER assemble.py depuis /tmp")
    else:
        ok("L01 pipeline : HTML frais (posterieur a data.json)")


# ─────────────────────────────────────────────────────────────
# L02 — Le numero de build dans l'HTML doit matcher gen.py CHANGELOG[0]
#       Sinon on pousse un ancien build (arrive builds 60/61).
# ─────────────────────────────────────────────────────────────
def check_build_number():
    gen = open(GEN, encoding="utf-8").read()
    m = re.search(r'CHANGELOG=\[\s*\{"build":(\d+)', gen)
    if not m:
        crit("L02 build : impossible de lire CHANGELOG[0].build dans gen.py")
        return
    gen_build = int(m.group(1))
    html = open(OUT_HTML, encoding="utf-8").read()
    hm = re.search(r'"build":\s*(\d+)', html)
    if not hm:
        crit("L02 build : numero de build introuvable dans l'HTML")
        return
    html_build = int(hm.group(1))
    if gen_build != html_build:
        crit(f"L02 build : gen.py dit build {gen_build} mais HTML contient {html_build} "
             f"— HTML STALE, relancer le pipeline")
    else:
        ok(f"L02 build : coherent (build {gen_build})")


# ─────────────────────────────────────────────────────────────
# L03 — JS valide (node --check) — attrape les erreurs de syntaxe
#       introduites par un str_replace maladroit.
# ─────────────────────────────────────────────────────────────
def check_node():
    if not os.path.exists(APP):
        warn("L03 node : /tmp/app.js absent, check saute")
        return
    r = subprocess.run(["node", "--check", APP], capture_output=True, text=True)
    if r.returncode != 0:
        crit(f"L03 node : app.js invalide — {r.stderr.strip()[:200]}")
    else:
        ok("L03 node : app.js valide")


# ─────────────────────────────────────────────────────────────
# L04 — Pas de surrogate-pair d'emoji en dur dans app.js
#       ('\ud83d\udccd' casse la fonction JS silencieusement).
#       On tolere les emojis litteraux (1 codepoint) ; on interdit
#       les paires \uD8xx\uDCxx ecrites en toutes lettres.
# ─────────────────────────────────────────────────────────────
def check_surrogates():
    if not os.path.exists(APP):
        return
    src = open(APP, encoding="utf-8").read()
    # sequence textuelle \ud8xx suivie de \udcxx (echappement JS ecrit en clair)
    bad = re.findall(r'\\u[dD][89abAB][0-9a-fA-F]{2}\\u[dD][c-fC-F][0-9a-fA-F]{2}', src)
    if bad:
        crit(f"L04 emoji : {len(bad)} surrogate-pair(s) echappee(s) en dur dans app.js "
             f"(ex {bad[0]}) — utiliser \\U0001Fxxx ou le caractere litteral")
    else:
        ok("L04 emoji : aucune surrogate-pair echappee")


# ─────────────────────────────────────────────────────────────
# L05 — Coherence des semaines : chaque date realise doit tomber
#       dans la bonne semaine ISO (29 juin = lundi S27, pas S26).
# ─────────────────────────────────────────────────────────────
def _iso_week_monday_ref(dstr):
    """Retourne le numero de semaine du plan pour une date ISO,
    en se calant sur l'ancre connue : 9 mars 2026 = lundi = S11."""
    from datetime import date
    y, m, d = map(int, dstr.split("-"))
    target = date(y, m, d)
    anchor = date(2026, 3, 9)  # lundi S11
    delta_weeks = (target - anchor).days // 7
    # ajuste si la date est avant lundi de sa semaine
    monday_of_target = target.fromordinal(target.toordinal() - target.weekday())
    delta_weeks = (monday_of_target - anchor).days // 7
    return 11 + delta_weeks


def check_week_dates():
    if not os.path.exists(DATA):
        return
    d = json.load(open(DATA, encoding="utf-8"))
    sbw = d.get("SBW", {})
    problems = []
    for wk, seances in sbw.items():
        try:
            wknum = int(wk)
        except ValueError:
            continue
        for s in seances:
            r = s.get("realise", {})
            dt = r.get("date")
            if not dt or not re.match(r"\d{4}-\d{2}-\d{2}", dt):
                continue
            expected = _iso_week_monday_ref(dt)
            if expected != wknum:
                problems.append(f"S{wk} contient une seance datee {dt} "
                                f"qui appartient a S{expected}")
    if problems:
        for p in problems[:5]:
            crit(f"L05 semaine : {p}")
    else:
        ok("L05 semaine : toutes les dates realise tombent dans la bonne semaine ISO")


# ─────────────────────────────────────────────────────────────
# L06 — data.json parse + compteurs attendus (30 semaines / 132 seances)
# ─────────────────────────────────────────────────────────────
def check_data_integrity():
    if not os.path.exists(DATA):
        return
    try:
        d = json.load(open(DATA, encoding="utf-8"))
    except Exception as e:
        crit(f"L06 data : data.json illisible — {e}")
        return
    n_sem = len(d.get("SEMAINES", []))
    n_sea = sum(len(v) for v in d.get("SBW", {}).values())
    if n_sem != 30:
        warn(f"L06 data : {n_sem} semaines (attendu 30)")
    if n_sea != 132:
        warn(f"L06 data : {n_sea} seances (attendu 132)")
    if n_sem == 30 and n_sea == 132:
        ok("L06 data : 30 semaines / 132 seances")


# ─────────────────────────────────────────────────────────────
# L07 — Aucun token GitHub en dur dans les fichiers pousses
# ─────────────────────────────────────────────────────────────
def check_no_token():
    for path in (GEN, APP):
        if not os.path.exists(path):
            continue
        src = open(path, encoding="utf-8").read()
        if re.search(r'github_pat_[A-Za-z0-9_]{20,}', src):
            crit(f"L07 secret : un token GitHub est present en dur dans {os.path.basename(path)}")
    if not any("L07" in c for c in CRIT):
        ok("L07 secret : aucun token en dur dans les sources")


# ─────────────────────────────────────────────────────────────
# L08 — HTML non vide + bien ferme
# ─────────────────────────────────────────────────────────────
def check_html_sane():
    if not os.path.exists(OUT_HTML):
        return
    html = open(OUT_HTML, encoding="utf-8").read()
    if len(html) < 400_000:
        warn(f"L08 html : taille suspecte ({len(html)} octets, attendu ~700k)")
    if not html.rstrip().endswith("</html>"):
        crit("L08 html : le fichier ne se termine pas par </html> (tronque ?)")
    if "\x00" in html:
        crit("L08 html : null byte detecte dans l'HTML")
    if not any("L08" in c for c in CRIT) and len(html) >= 400_000:
        ok(f"L08 html : sain ({len(html)} octets, ferme correctement)")


def main():
    check_pipeline_fresh()
    check_build_number()
    check_node()
    check_surrogates()
    check_week_dates()
    check_data_integrity()
    check_no_token()
    check_html_sane()

    print("\n" + "=" * 56)
    print("  PREFLIGHT — verification avant push (Running PWA)")
    print("=" * 56)
    for m in OK:
        print(f"  \u2713 {m}")
    for m in WARN:
        print(f"  \u26a0 {m}")
    for m in CRIT:
        print(f"  \u2717 {m}")
    print("=" * 56)
    if CRIT:
        print(f"  RESULTAT : {len(CRIT)} echec(s) critique(s) — NE PAS PUSHER")
        print("=" * 56)
        sys.exit(1)
    print(f"  RESULTAT : OK ({len(WARN)} avertissement(s)) — push autorise")
    print("=" * 56)
    sys.exit(0)


if __name__ == "__main__":
    main()
