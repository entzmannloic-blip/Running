# Enrichir l'app après une séance — contrat pour Claude

> Document de référence pour le projet Claude. Mis à jour : 29 octobre 2026 (build 283, fond de carte et masquage du tracé du Rewind).

## Le circuit

```
Loïc court → Strava → il envoie la séance à Claude
→ Claude lit Strava (MCP) → recopie l'essentiel dans strava/<id>.json
→ python scripts/log_seance.py → Claude écrit la revue (src/textes/seances/S44-2.html)
→ python src/build.py → contrôles → branche + pull request → fusion → l'iPhone affiche « Nouvelle version prête »
```

Une séance enrichie = **une petite PR de données**. Ne plus ouvrir `src/gen.py` pour logger : le script s'en charge.

## 1. Lire Strava (outils MCP)

1. `Strava:list_activities(range_start, range_end)` sur la journée de la séance (une seule activité en retour).
2. `Strava:get_activity_performance(activity_id)` : FC moyenne et max, tours (laps).
3. `Strava:get_gear(gear_types=["Shoe"])` : kilométrage de la paire utilisée.
4. **Pour le Rewind de séance, à chaque séance** : `Strava:list_activities` avec `include_polyline=true` (le tracé), et `Strava:get_activity_streams(activity_id, resolution=150, streams=["time","distance","altitude","velocity_smooth","heart_rate"])`. Recopier ces réponses et celle de `get_activity_performance` (trophées, segments, meilleurs efforts, tours) dans `strava/<id>-rewind.json`, au format décrit en tête de `scripts/rewind_seance.py`.
5. **Seulement pour un footing, une sortie longue ou une récupération sur route** (D+ < ~15 m/km, 40 min ou plus) : `Strava:get_activity_streams(activity_id, resolution=1000, streams=["time","heart_rate","velocity_smooth"])`, pour le découplage. Jamais pour une séance d'intensité ni un trail : c'est le poste le plus coûteux du log.

## 2. Recopier l'essentiel dans `strava/<id>.json` (dossier ignoré par Git)

Champs Strava recopiés tels quels, et les tours sous forme compacte `[moving_time, distance, avg_hr, max_hr, elevation_gain]` :

```json
{"id":"20753555995","start_local":"2026-10-27T17:04:11","sport_type":"Run","gear_id":"28498174",
 "distance":10035.6,"moving_time":3510,"elapsed_time":3525,"elevation_gain":31,"relative_effort":86,
 "total_calories":754,"avg_cadence":85.9994,"pr_count":0,"achievement_count":0,"temperature":18.4,
 "average_heartrate":145.58,"max_heartrate":165,"gear_total_distance":1284244,
 "laps":[[340,1000,141.713,150,4.2],[347,1000,147.666,152,4.8]]}
```

`temperature` vient de `weather.temperature` de `list_activities` ; `gear_total_distance` du `get_gear` de la paire. Si les flux ont été demandés : les écrire tels quels dans `strava/<id>-streams.json`. Exemples complets : `tests/fixtures/strava/`.

## 3. Lancer le script

```bash
python scripts/log_seance.py S44-2 strava/20753555995.json [--streams strava/20753555995-streams.json]
       [--blocs "1-8:Footing facile:vert,9-10:Fin:orange"] [--titre "…" --sous "…"] [--rpe 5] [--statut partiel]
       --rewind strava/20753555995-rewind.json [--cible-allure 6:10- --cible-fc 145 --cible-source "…"]
```

Il écrit, sans rien inventer :
- `src/logs/S44-2.json` : le bloc `realise` (km, temps, allure, FC, effort relatif, cadence, D+, kcal, température, splits par km, terrain route ou trail, découplage, identifiant Strava) et les champs de la séance (chaussure, date si elle diffère du plan, titre et sous-titre si `--titre`/`--sous`, segments si `--blocs`) ;
- `src/strava_reference.json` : l'activité du jour (additionnée s'il y a déjà une sortie ce jour-là) et le kilométrage de la chaussure ;
- `GEAR` dans `src/gen.py` : le kilométrage de la chaussure ;
- une entrée de `CHANGELOG` (build + 1). `--sans-changelog` pour plusieurs séances dans un même build ;
- avec `--rewind` : `src/rewind/44-2.json` (flux réduit à 160 points, tracé masqué, tours, trophées). `--cible-*` seulement si la séance a été remplacée (ex. seuil remplacé par un footing) : la cible appliquée est gardée et sert au prévu face au réalisé. Rattrapage d'une séance déjà loguée : `python scripts/rewind_seance.py S44-2 strava/<id>-rewind.json`.

Il refuse de réécrire un log existant (`--force`) et de logger deux fois la même activité Strava. Le commentaire factuel est produit automatiquement ; `--commentaire` le remplace. Le découplage suit `src/decouplage.py` (seuls les `fiable` servent dans l'app).

## 4. Écrire les textes

- **La revue de la séance** : `src/textes/seances/S44-2.html` (HTML court). C'est le seul texte à rédiger pour une séance. Le Rewind en tire l'analyse du coach : écrire quatre paragraphes marqués `<p data-coach="verdict">`, `<p data-coach="bien">`, `<p data-coach="corriger">`, `<p data-coach="conseil">` (un intertitre en gras est permis au début). `validate_data.py` échoue si une séance qui a un Rewind n'a pas de verdict.
- **La revue de la semaine**, quand elle est terminée : `src/textes/semaines/S44.html`.
- **Le Rewind de la semaine** (s'il y a eu au moins une course) : `src/textes/rewinds/S44.json`, 6 à 8 slides sur les chiffres mesurés (copier la structure d'un Rewind existant). Ils sont rangés par numéro de semaine : le plus récent est ouvert le lundi.
- Une séance non faite (`skipped`) ou une modification du plan se fait encore dans le bloc de la semaine de `src/gen.py` (voir les semaines précédentes).

### Tracé du Rewind : masquage de 300 m et fond de carte (build 283)

L'app est **publique** (GitHub Pages) : le tracé publié ne doit pas montrer d'où part la séance.
- `scripts/rewind_seance.py` retire les **300 premiers et les 300 derniers mètres** (distance au sol le long du tracé ; le polyline réduit de Strava est environ 3 % plus court que la distance réelle, la coupe est donc faite sur la plus grande des deux mesures, jamais sous 300 m réels), puis projette le reste en **Web Mercator exact** (EPSG:3857, mètres) avec un **ancrage entier** `ancrage: {x, y}` : c'est ce qui permet de poser les tuiles sur les rues. Il écrit aussi `masque` (300) et `trace_d` (`[début, fin]` en mètres réels de la sortie, pour colorer chaque morceau avec la bonne allure). Sortie trop courte pour garder quelque chose : pas de tracé du tout, jamais un tracé non masqué.
- **Rien à faire de plus** pour une nouvelle séance : `log_seance.py --rewind` et `rewind_seance.py` appliquent le masquage. `validate_data.py` refuse un Rewind publié dont le tracé n'est pas masqué (ancrage, `masque` ≥ 300, `trace_d`).
- **Refaire le tracé d'un Rewind existant** (relire sa polyline dans Strava, `list_activities` avec `include_polyline=true` sur le jour de la séance, puis recopier `id`, `summary.distance` et `reduced_polyline` dans `strava/<id>-polyline.json`) : `python scripts/rewind_seance.py S44-2 strava/<id>-polyline.json --retrace`. Seuls `trace`, `ancrage`, `trace_d` et `masque` changent ; l'activité doit être celle du Rewind. Vérifier la recopie : projeter la polyline comme l'ancien code et comparer à l'ancien `trace` (les 4 Rewinds du build 283 l'ont été).
- **Fond de carte** (`fondCarte()` et `img2()` dans `src/app.js`) : tuiles OpenStreetMap (`tile.openstreetmap.org`, 256 px, zoom d'un cran plus fin pour rester net sur Retina), passées en gris clair par CSS (`.rs-fond`), attribution « © OpenStreetMap contributors » en lien vers openstreetmap.org/copyright (build 284 ; CARTO exige désormais une clé). Les tuiles ne sont demandées que quand l'image s'affiche (`charge()` appelé par `joue()`), jamais préchargées, conformément à la politique d'usage d'OSM ; ne pas retirer l'en-tête Referer. Le tracé coloré reste par-dessus avec son animation. **Réseau seulement** : hors connexion (`navigator.onLine`), ou si une tuile échoue, le tracé reste seul comme avant (une tuile n'entre dans la page qu'une fois chargée : pas de case vide, attribution cachée tant qu'aucune tuile ne s'est affichée). Les tuiles ne sont **jamais dans le pré-cache** du service worker (requêtes d'un autre domaine, non interceptées). Un Rewind ancien, sans `ancrage`, s'affiche sans fond de carte.
- Limites à connaître : le shell de la session n'atteint pas les serveurs de tuiles (le rendu se voit sur l'iPhone) ; les tests T32 de `test_regression.py` servent de fausses tuiles et vérifient l'alignement par un calcul indépendant.

## 5. Construire et contrôler en local

```bash
python src/build.py                 # régénère index.html, sw.js et data/*.json
python scripts/preflight.py         # contrôles statiques
python scripts/release.py           # porte complète — ne JAMAIS utiliser --push ; filtrer : | grep -i "phases\|echec"
```

`release.py` doit finir par « Phases 1 a 3 vertes ». Un échec = on corrige, on ne pousse pas.

## 6. Branche, commit, pull request, fusion

- Branche depuis `main` à jour : `data/S{sem}-{n}`. Fichiers : `src/logs/`, `src/rewind/`, `src/textes/`, `src/gen.py`, `src/strava_reference.json`, `index.html`, `sw.js`, `data/*.json`. Ne pas committer `strava/`.
- Message et titre de PR : `data: log S44 seance 2 footing 27/10 (Strava) (build 263)` ; corps : date, km, durée, chaussure, identifiant Strava.
- `python scripts/pr_scope.py origin/main...HEAD` doit répondre `DATA_ONLY`, puis contrôle GitHub `verify` vert : fusion sans relecture (`gh pr merge --squash --delete-branch`). Sinon c'est une PR de code : l'annoncer à Loïc.
- Vérifier la publication : `data/meta.json` publié porte le build attendu.

## 7. Retour arrière

`git revert <commit>` (fusion « squash »), nouvelle PR, même circuit. Pour une seule séance : supprimer `src/logs/S44-2.json` et sa revue, rebuild.

## Règles de sécurité

- **Aucun token dans le dépôt** (le preflight le vérifie). L'accès se fait par `gh`.
- Ne modifier ni `.github/`, ni `src/app.js`, ni le CSS dans une PR de données.
- Les chiffres viennent de Strava ou de Loïc : ne rien inventer. Si une valeur manque, laisser le champ absent plutôt que mettre un 0.
- Pas d'emoji écrit en paire de surrogates dans `gen.py` (voir `docs/LESSONS.md`).
- Le repo publié s'appelle `entzmannloic-blip/Running` (`Labfact/running` y redirige).
