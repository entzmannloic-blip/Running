# -*- coding: utf-8 -*-
"""Quelles donnees vont dans quel fichier data/*.json.

Chaque fichier est un objet {NOM_GLOBAL: valeur}. Au demarrage, la page charge
plan, seances, historique et meta (en parallele) et copie chaque cle sur window,
sous le meme nom que les anciennes constantes `const X=...` : le code de
l'application ne change pas. changelog.json est charge a la demande.

Chaque entree : (nom_global, cle_dans_data.json).
"""
GROUPS = {
    "plan": [
        ("PHASES", "PHASES"), ("COUL", "COUL"), ("SEMAINES", "SEMAINES"), ("GEAR", "GEAR"),
        ("RACES", "RACES"), ("PROFIL", "PROFIL"), ("VIGILANCE", "VIGILANCE"), ("S24R", "S24R"),
        ("PROJ", "PROJ"), ("MAJ", "MAJ"), ("JOURNAL", "JOURNAL"), ("REWINDS", "REWINDS"),
        ("DOSSIERS", "DOSSIERS"), ("PALMARES", "PALMARES"),
    ],
    "seances": [("SEANCES_BY_WEEK", "SBW")],
    "historique": [
        ("RECORDS", "RECORDS"), ("HIST", "HIST"), ("POLAR", "POLAR"), ("ALLURES", "ALLURES"),
        ("ALLURES_COURSE", "ALLURES_COURSE"), ("MONTHLY", "MONTHLY"), ("SAISON2026", "SAISON2026"),
        ("SAISON_EFF", "SAISON_EFF"), ("ACWR_DATA", "ACWR_DATA"), ("RECORDS_PERF", "RECORDS_PERF"),
        ("ZONES_FC", "ZONES_FC"), ("HEATMAP", "HEATMAP"),
    ],
    "changelog": [("CHANGELOG", "CHANGELOG")],
}
# Fichiers charges au demarrage (meta est genere : derniere entree du changelog).
EAGER = ["plan", "seances", "historique", "meta"]
