#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mesure_log.py — cout d'un log de seance, a partir d'un journal d'actions.

    python scripts/mesure_log.py docs/mesures/log-2026-10-27-avant.json
    python scripts/mesure_log.py AVANT.json APRES.json      # comparaison

Le journal est une liste d'actions : {"action", "lu", "ecrit", "nature"}.
- lu    : caracteres entres dans le contexte (resultat d'outil : reponse Strava, extrait de fichier, sortie de commande)
- ecrit : caracteres produits par Claude (contenu d'un fichier, d'une edition, d'une commande)
- nature: "nombres" (JSON de flux, ~2,2 car./token), "texte" (francais, ~3,5), "code" (~3,0)

Les tokens sont une estimation (meme methode avant et apres, c'est ce qui compte pour comparer).
Le nombre d'actions compte a part : chaque action relit tout le contexte, c'est le premier facteur
du cout reel en points de la fenetre de 5 heures.
"""
import json
import sys

RATIO = {"nombres": 2.2, "texte": 3.5, "code": 3.0}


def bilan(path):
    with open(path, encoding="utf-8") as f:
        journal = json.load(f)
    lu = sum(a.get("lu", 0) / RATIO[a.get("nature", "code")] for a in journal["actions"])
    ecrit = sum(a.get("ecrit", 0) / RATIO[a.get("nature", "code")] for a in journal["actions"])
    return {"titre": journal.get("titre", path), "actions": len(journal["actions"]),
            "tokens_lus": round(lu), "tokens_ecrits": round(ecrit), "tokens_total": round(lu + ecrit),
            "detail": journal["actions"]}


def affiche(b):
    print(f"{b['titre']}")
    print(f"  actions : {b['actions']} · tokens lus ~{b['tokens_lus']:,} · ecrits ~{b['tokens_ecrits']:,} · total ~{b['tokens_total']:,}".replace(",", " "))


def main(args):
    if not args:
        print(__doc__)
        return 2
    bs = [bilan(p) for p in args]
    for b in bs:
        affiche(b)
    if len(bs) == 2:
        a, n = bs
        for k in ("actions", "tokens_lus", "tokens_ecrits", "tokens_total"):
            d = (n[k] - a[k]) / a[k] * 100 if a[k] else 0
            print(f"  {k:14} {a[k]:>8} -> {n[k]:>8}  ({d:+.0f} %)")
        print("PORTE : " + ("OK, le log coute moins de tokens" if n["tokens_total"] < a["tokens_total"] else "ECHEC, le log ne coute pas moins"))
        return 0 if n["tokens_total"] < a["tokens_total"] else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
