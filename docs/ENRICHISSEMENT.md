# Enrichir l'app après une séance — contrat pour Claude

> Document de référence pour le projet Claude. Il remplace les anciennes consignes de livraison (copie dans `/tmp`, push par l'API Git Data, token en clair). Mis à jour : octobre 2026 (build 232).

## Le circuit

```
Loïc court → Strava → il envoie la séance à Claude
→ Claude lit Strava (MCP) → modifie src/gen.py + src/strava_reference.json
→ python src/build.py → contrôles locaux → branche + pull request
→ GitHub vérifie (job « verify ») → fusion → GitHub Pages publie → l'iPhone affiche « Nouvelle version prête »
```

Une séance enrichie = **une petite PR de données**. Rien d'autre ne doit y figurer.

## 1. Lire Strava (outils MCP)

1. `Strava:list_activities(first=2)` : retrouver l'activité (date, distance).
2. `Strava:get_activity_performance(activity_id)` : km, temps, FC moyenne et max, tours (laps), meilleurs efforts.
3. `Strava:get_activity_streams(activity_id, streams, resolution)` : seulement si besoin d'analyse fine (dérive de FC, segments).
4. `Strava:get_gear(gear_types=["Shoe"])` : kilométrage de chaque paire (peut demander une approbation côté app).

## 2. Modifier `src/gen.py` (source des données)

- **La séance** : dans le bloc de sa semaine (`for n, arr in list(SEANCES_BY_WEEK.items()):` puis `if n==NN:`, avec `_SNN = {str(x["id"]): x for x in arr}`), renseigner `_SNN["<id>"]["realise"]={...}`. Copier la structure d'une séance déjà loggée de la **même semaine** ou de la semaine précédente. Champs courants de `realise` : `statut` (`fait`, `partiel`, `saute`), `km`, `temps` (`h:mm:ss`), `allure` (`m:ss/km`), `fc_moy`, `fc_max`, `re` (effort relatif Strava), `cadence`, `elevation_gain`, `kcal`, `rpe_ressenti`, `commentaire`, `revue` (HTML du bilan), `pr`, `ach`, `pr_detail`, `splits` (`[{"km","allure","fc"}]`).
- **Si la séance diffère du plan** : mettre aussi à jour `titre`, `sous`, `metriques`, `objectif`, `struct`, `segments`, `chaussure_realise`, et `date` si elle est différente.
- **Chaussures** : dans `GEAR`, mettre à jour `km` (arrondi) d'après `get_gear`.
- **Journal** : une entrée de `CHANGELOG` en tête, `build` = dernier + 1, `date`, `tag` court et `items` factuels (voir une entrée existante). Le numéro de build est vérifié par le preflight.
- Pas d'emoji écrit en paire de surrogates (`👍`) dans `gen.py` : caractère littéral ou `\U0001F44D` (voir `docs/LESSONS.md`).

## 3. Mettre à jour le référentiel Strava : `src/strava_reference.json`

Les audits comparent l'app à ce référentiel (« source de vérité » Strava). Trois blocs :
- `activites` : `"AAAA-MM-JJ": [km, effort_relatif, D+]` (ajouter la nouvelle sortie ; plusieurs sorties le même jour = totaux additionnés) ;
- `chaussures` : kilométrage Strava de chaque paire (mêmes valeurs que `GEAR` dans `gen.py`, à ±5 km) ;
- `mois` : totaux des mois **clos** `[km, sorties]`.

## 4. Construire et contrôler en local

```bash
python src/build.py                 # régénère index.html, sw.js et data/*.json
python scripts/preflight.py         # contrôles statiques (build, dates ISO, secrets…)
python scripts/validate_data.py     # format des données
python scripts/release.py           # porte complète (audits Strava, Cockpit, régression) — ne JAMAIS utiliser --push
```

`release.py` doit finir par « Phases 1 a 3 vertes ». Un échec = on corrige, on ne pousse pas. Sous Windows, définir `PYTHONUTF8=1` si on lance un script à la main.

## 5. Branche, commit, pull request

- Branche depuis `main` à jour : `data/S{sem}-{n}` (ex. `data/S41-3`).
- Fichiers attendus dans le commit : `src/gen.py`, `src/strava_reference.json`, `index.html`, `sw.js`, `data/*.json` (+ `fit/` si un fichier de séance change). Ils sont **générés** : ne jamais les éditer à la main.
- Message : `data: log S41 seance 3 vallonne 07/10 (Strava) (build 233)`.
- Ouvrir la PR vers `main`, titre identique, corps : ce qui est loggé (date, km, durée, chaussure) et les valeurs Strava utilisées.

## 6. Fusion

1. `python scripts/pr_scope.py origin/main...HEAD` doit répondre `DATA_ONLY`. Sinon c'est une PR de code : l'annoncer à Loïc avant de fusionner.
2. Le contrôle GitHub **`verify`** doit être vert (il rejoue le build, le preflight, le format des données, la reproductibilité et les tests de régression).
3. Si 1 et 2 sont vrais : fusion sans relecture, `gh pr merge --squash --delete-branch`. Loïc a autorisé la fusion automatique des PR de données.
4. Vérifier la publication : `gh api repos/entzmannloic-blip/Running/pages/builds/latest` (statut `built`) puis `https://entzmannloic-blip.github.io/Running/data/meta.json` (le build attendu).

## 7. Retour arrière

`git revert -m 1 <commit de fusion>` (ou `git revert <commit>` pour une fusion « squash »), nouvelle PR, même circuit. Le tag `pre-refonte` marque la version d'avant la refonte (build 224).

## Règles de sécurité

- **Aucun token dans le dépôt** (le preflight le vérifie). Le PAT mentionné dans les anciennes notes expirait le 10 septembre 2026 : l'accès se fait désormais par `gh` (connexion `entzmannloic-blip`). Ne jamais écrire un token dans un fichier, un message de commit ou une PR.
- Ne modifier ni `.github/`, ni `src/app.js`, ni le CSS dans une PR de données.
- Les chiffres viennent de Strava ou de Loïc : ne rien inventer. Si une valeur manque, laisser le champ absent plutôt que mettre un 0.
