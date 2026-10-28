# P4, lot 1 — Rewind de séance : plan de production (28/10/2026)

Maquette validée : https://claude.ai/artifact/DeGZusg6KHNaEurD6gF9w8 (défilement automatique, tracés de 2 à 3 s,
moment fort = trophée Strava sinon km le plus rapide). Branche `p4/rewind-seance`, build 269.

## Données
1. `scripts/rewind_seance.py` : fichier d'entrée Strava (`strava/<id>-rewind.json` : list_activities avec tracé,
   get_activity_performance, get_activity_streams à ~150 points) → `src/rewind/<sem>-<n>.json` (flux ≤ 160 points,
   tracé projeté en mètres, tours, meilleurs efforts, trophées, cible appliquée si la séance a été remplacée).
   `log_seance.py --rewind` l'appelle à chaque log.
2. `src/build.py` copie `src/rewind/` ; `src/assemble.py` publie `data/rewind-<sem>-<n>.json` en y ajoutant les
   éléments du coach tirés de la revue (verdict, bien, à corriger, conseil), recopie la cible appliquée dans
   `realise.cible` et publie l'index `REWIND_SEANCE` dans `data/seances.json` (`src/datamap.py`).
3. Rattrapage : S44-2 et S43-8 seulement.

## Interface (src/app.js, src/css_extra.txt, préfixe `rs-`)
4. Rewind plein écran, 9 images (chiffres, tracé, relief, km par km, cœur, discipline, moment fort, analyse du
   coach terrain, progression), chargé à l'ouverture (`data/rewind-*.json` + textes).
5. Bouton « Revoir ma séance » dans la fiche (remplace l'ancien replay pour ces séances) ; annonce « Le coach a
   analysé ta séance » une fois sur l'Accueil ; « Où j'en suis » (5 courbes à verdict) depuis la fin du Rewind et
   le Cockpit.

## Contrôles
6. Tests de régression T23 (avec et sans transitions de vue, réduire les animations) ; `validate_data.py` contrôle
   les fichiers Rewind ; build, preflight, release.py verts ; une vérification indépendante (UX/UI et débogage).
7. Docs : ENRICHISSEMENT.md (nouvelle étape du log, convention de revue `data-coach`), CLAUDE.md.

## Journal
- 28/10 : push refusé depuis la session Claude (accès en écriture non accordé) : livraison par lot Git à appliquer.
