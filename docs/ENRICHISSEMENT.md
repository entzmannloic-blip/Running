# Enrichir l'app après une séance — contrat pour Claude

> Document de référence pour le projet Claude. Mis à jour : octobre 2026 (build 265, chantier P2 « pipeline de log »).

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
4. **Seulement pour un footing, une sortie longue ou une récupération sur route** (D+ < ~15 m/km, 40 min ou plus) : `Strava:get_activity_streams(activity_id, resolution=1000, streams=["time","heart_rate","velocity_smooth"])`, pour le découplage. Jamais pour une séance d'intensité ni un trail : c'est le poste le plus coûteux du log.

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
```

Il écrit, sans rien inventer :
- `src/logs/S44-2.json` : le bloc `realise` (km, temps, allure, FC, effort relatif, cadence, D+, kcal, température, splits par km, terrain route ou trail, découplage, identifiant Strava) et les champs de la séance (chaussure, date si elle diffère du plan, titre et sous-titre si `--titre`/`--sous`, segments si `--blocs`) ;
- `src/strava_reference.json` : l'activité du jour (additionnée s'il y a déjà une sortie ce jour-là) et le kilométrage de la chaussure ;
- `GEAR` dans `src/gen.py` : le kilométrage de la chaussure ;
- une entrée de `CHANGELOG` (build + 1). `--sans-changelog` pour plusieurs séances dans un même build.

Il refuse de réécrire un log existant (`--force`) et de logger deux fois la même activité Strava. Le commentaire factuel est produit automatiquement ; `--commentaire` le remplace. Le découplage suit `src/decouplage.py` (seuls les `fiable` servent dans l'app).

## 4. Écrire les textes

- **La revue de la séance** : `src/textes/seances/S44-2.html` (HTML court : verdict, point à corriger, suite). C'est le seul texte à rédiger pour une séance.
- **La revue de la semaine**, quand elle est terminée : `src/textes/semaines/S44.html`.
- **Le Rewind de la semaine** (s'il y a eu au moins une course) : `src/textes/rewinds/S44.json`, 6 à 8 slides sur les chiffres mesurés (copier la structure d'un Rewind existant). Ils sont rangés par numéro de semaine : le plus récent est ouvert le lundi.
- Une séance non faite (`skipped`) ou une modification du plan se fait encore dans le bloc de la semaine de `src/gen.py` (voir les semaines précédentes).

## 5. Construire et contrôler en local

```bash
python src/build.py                 # régénère index.html, sw.js et data/*.json
python scripts/preflight.py         # contrôles statiques
python scripts/release.py           # porte complète — ne JAMAIS utiliser --push ; filtrer : | grep -i "phases\|echec"
```

`release.py` doit finir par « Phases 1 a 3 vertes ». Un échec = on corrige, on ne pousse pas.

## 6. Branche, commit, pull request, fusion

- Branche depuis `main` à jour : `data/S{sem}-{n}`. Fichiers : `src/logs/`, `src/textes/`, `src/gen.py`, `src/strava_reference.json`, `index.html`, `sw.js`, `data/*.json`. Ne pas committer `strava/`.
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
