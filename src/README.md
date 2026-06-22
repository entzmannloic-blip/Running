# Pipeline de build du plan d'entraînement

Reprise dans une nouvelle conversation :
1. Récupérer src/* dans /tmp
2. `python3 gen.py`        → /tmp/data.json  (attendu : "Semaines: 30 | Séances: 131")
3. `python3 assemble.py`   → /mnt/user-data/outputs/plan-entrainement.html
4. `node --check app.js` (BLOQUANT) puis vérif Playwright (screenshots, viewport ~430px)
5. Pousser src/ modifiés + index.html via **Git Data API** (commit atomique : GET ref → GET commit → POST tree → POST commit → PATCH ref). Token = fine-grained PAT.

Marqueur de version : "Build N" dans le panneau version (incrémenter à chaque push + entrée CHANGELOG dans gen.py).
Fichiers .fit des séances : dossier fit/.

## État au build 51
Refonte UX/UI + IA complète (voir **CLAUDE.md** pour le détail navigation/pièges).
Nav = **bottom bar** `Accueil · Séances · [Coach] · Cockpit · Courses` (l'onglet Suivi a été dissous dans Cockpit ; Palmarès est devenu Courses, id interne `palmares`).
