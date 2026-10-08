# CLAUDE.md — Contexte Running PWA

## ⚠ À lire en premier
1. **Enrichir après une séance** : suivre **docs/ENRICHISSEMENT.md** (circuit complet : Strava → `src/gen.py` → build → branche → PR → fusion). Une séance = une petite PR de données.
2. **Apprendre des erreurs** : avant tout push, lancer après le build `python scripts/preflight.py` (et `python scripts/release.py` pour la porte complète, **sans `--push`**). Un échec critique = **ne pas pousser**. Le détail de chaque leçon est dans **docs/LESSONS.md** ; quand une nouvelle erreur survient : la corriger, la consigner, et si elle est mécanisable ajouter un check à `scripts/preflight.py` (et sa copie `src/preflight.py`).
3. Documentation technique détaillée : docs/TECHNICAL.md (en partie historique : le pipeline à jour est décrit ici et dans ENRICHISSEMENT.md). Contexte produit : **PRODUCT.md** ; système de design : **DESIGN.md**.

## Identité
**App** : Running PWA — suivi de saison de course à pied pour Loïc Entzmann (installée sur l'écran d'accueil de l'iPhone via Safari, hors App Store)
**Repo** : entzmannloic-blip/Running (GitHub Pages) — le build publié se lit dans `data/meta.json`
**Accès GitHub** : `gh` connecté (compte `entzmannloic-blip`). Aucun token dans le dépôt.
**Coach IA intégré** : retiré (octobre 2026). Le coaching se fait dans Claude après chaque séance.

## Athlète
- **Loïc Entzmann** · Lyon · M0 (30-34) · 84 kg
- FCmax 192 · Z2 max 144 bpm · Seuil marche ~160 bpm
- **Courses 2026** : Trail Déraille 5 juil (24km) · Marathon Nice 8 nov (objectif 3h45) · SaintExpress 28 nov (45km nuit)

## Règles absolues (voir docs/TECHNICAL.md §14 pour le détail historique)

1. **POC avant prod** — Toute feature visuelle = artifact POC → validation Loïc → code prod
2. **Build** : `python src/build.py` (gen + assemble + `node --check`). Un échec = STOP, ne jamais pousser
3. **CHANGELOG obligatoire** — Incrémenter le build ET ajouter une entrée en tête de `CHANGELOG` dans `src/gen.py` avant chaque push
4. **Fichiers générés** — `index.html`, `sw.js` et `data/*.json` sont **produits par le build** : ne jamais les éditer à la main, toujours les committer avec les sources modifiées (le job `verify` refuse un décalage)
5. **Chaussures** — `Strava:get_gear` après chaque log de séance → `GEAR` dans gen.py (km arrondi) + `src/strava_reference.json` → rebuild
6. **Livraison par pull request** — branche depuis `main` à jour, PR, contrôle GitHub `verify` vert, fusion `--squash`. PR de données seulement (`python scripts/pr_scope.py origin/main...HEAD` → `DATA_ONLY`) : fusion sans relecture. Toute autre PR (app.js, CSS, scripts, workflows) : l'annoncer à Loïc avant de fusionner
7. **⚠️ Emojis dans gen.py** — Ne jamais écrire un emoji via paire de surrogates (ex. `👍`) en Python. Utiliser le caractère littéral ou `\U0001F44D`. Si gen.py est vidé : le restaurer depuis `git` (`git checkout -- src/gen.py` ou le dernier commit)

## Pipeline build (portable — Windows, Linux, CI)
Depuis la racine du dépôt :
```bash
python src/build.py            # build/ (copie de src/) → gen.py → assemble.py → node --check → écrit index.html, sw.js, data/*.json
python src/build.py --check    # n'écrit rien : échoue si les fichiers committés ≠ résultat du build (rejoue BUILT_ON)
python src/build.py --stage    # construit seulement build/site/ (tests)
python scripts/preflight.py    # contrôles statiques (après le build)
python scripts/validate_data.py     # format des data/*.json
python scripts/test_regression.py   # tests runtime (Playwright + Chromium)
python scripts/capture_reference.py --check   # captures de référence des 4 vues (local, après un changement d'interface)
python scripts/release.py      # porte complète (audits Strava, Cockpit…) — ne jamais ajouter --push
```
- Dossier de travail : `build/` (ignoré par Git), surchargeable par `RUNNING_WORK`. Chemins centralisés dans `src/paths.py`. Sous Windows, définir `PYTHONUTF8=1` pour lancer preflight et les tests à la main.
- **Reproductibilité** : `gen.py` calcule l'ACWR « à aujourd'hui » ; la date de build est enregistrée dans `data/meta.json` (`BUILT_ON`) et rejouée par `--check` (variable `RUNNING_TODAY`).
- Sortie attendue de gen.py : « Semaines: 30 | Séances: 137 ».
- Les copies `src/preflight.py` et `src/release.py` doivent rester identiques à `scripts/` (l'ancien `release.py` les référence) ; consolidation à prévoir.

## Fichiers clés
- `src/gen.py` — **données** : plan, séances, chaussures, dossiers, palmarès, CHANGELOG (génère `data.json`)
- `src/datamap.py` — quelles données vont dans quel fichier `data/*.json` (chargés au démarrage : plan, seances, historique, meta ; changelog à la demande)
- `src/assemble.py` — produit `site/index.html` (page + CSS + script de démarrage) et `site/data/*.json`
- `src/app.js` — toute la logique JS (servi tel quel à `src/app.js`)
- `src/css.txt` (tokens `:root` + base), `src/css_extra.txt` (CSS features), `src/body.html` (vues + barre de navigation)
- `src/sw.js` — **modèle** du service worker (`__BUILD__`, `__SHELL__` remplacés par le build)
- `src/build.py`, `src/paths.py` — build et chemins ; `src/strava_reference.json` — référentiel Strava lu par les audits
- `scripts/` — preflight, release, tests, audits ; `.github/workflows/verify.yml` — vérification automatique
- `tests/reference/` — captures de référence des 4 vues (390 px)

## ⭐ Navigation & IA actuelle
Une **bottom bar fixe** `#botbar` (frostée, marge de sécurité iOS), **4 items** (l'ordre + ids comptent pour `showTab`), étiquetée `aria-label`, `aria-current="page"` sur l'onglet actif :
```
Accueil · Séances · Cockpit · Courses
```
- **Accueil** (`#vue-accueil`, id `accueil`) — dashboard : héros prochaine séance, forme, alerte de charge, météo, progression, capital.
- **Séances** (`#vue-plan`, id `plan`) — le plan par phase et par semaine.
- **Cockpit** (`#vue-cockpit`, id `cockpit`) — analytique. `showTab('cockpit')` rend `renderCockpit()` ET `renderDash()`.
- **Courses** (`#vue-palmares`, id interne **toujours `palmares`**) — À venir (`RACES`) + Passées (`PALMARES`).

**Pièges :**
- ⚠️ L'onglet « Suivi » n'existe plus (dissous dans Cockpit) ; ne pas chercher `#vue-dash`.
- ⚠️ `showTab` liste `['accueil','plan','cockpit','palmares']`. Vue par défaut au chargement = Accueil.
- ⚠️ Le chat « Coach » a été supprimé. Restent les conseils calculés localement : `_coachNudge`, `coachAvant`, `coachDebrief`, `COACH_THEORY`.

## Chargement des données et PWA
- `index.html` charge `data/{plan,seances,historique,meta}.json` en parallèle puis `src/app.js` ; chaque fichier est un objet `{NOM: valeur}` copié sur `window` (les constantes gardent leurs noms : `SEMAINES`, `SEANCES_BY_WEEK`, `CHANGELOG`…). Échec réseau : message « Données indisponibles » + bouton Réessayer (`#boot-err`).
- `CHANGELOG` au démarrage = la dernière entrée seulement ; `loadChangelog()` charge la liste complète à l'ouverture du panneau de versions.
- `sw.js` (généré) : cache `plan-<build>`, pré-cache de tout le site, réseau d'abord avec repli cache après 3 s ou hors-ligne. `_checkNewVersion()` affiche le bandeau « Nouvelle version prête » au retour au premier plan.

## Design system
Voir **DESIGN.md** (« Le carnet de l'entraîneur ») et `src/css.txt :root`. **1 primaire** `--primary:#0d9488` (teal) ; états `--ok` `--warn` `--danger` ; neutres slate ; échelle typo `--t-display…--t-data`. Ne pas réintroduire de couleurs ad hoc. Dégradés par course (dossiers) préservés exprès. Mouvement : `.vue-in`, reveal au scroll, press-scale, haptique, tout sous `prefers-reduced-motion`.

## Données clés gen.py
- Plan : S25→S53 (30 semaines, 137 séances)
- Courses : `RACES` — Déraille, Nice, SaintExpress
- Chaussures : `GEAR` (6 paires, `gear_id` Strava ci-dessous) ; palmarès : `PALMARES`
- Séances loggées : `arr[i]["realise"]={...}` dans un bloc `if n==NN:` de la boucle des semaines (voir docs/ENRICHISSEMENT.md)

## Parc chaussures (gear_id Strava — les km actuels sont dans `GEAR`, `data/plan.json`)
| Modèle | Convention | gear_id Strava |
|--------|-----------|----------------|
| HOKA Clifton 10 | Décrassages ≤10 km | 28498174 |
| ASICS Gel Pulse 16 | Footings faciles | 28498182 |
| Brooks Cascadia 19 | Trail | 28498287 |
| ASICS Novablast 5 J | Training route (jaune) | 28722452 |
| ASICS Novablast 5 V | Courses (vert, neuf) | — |
| ASICS Magic Speed 4 | AM/qualité | 29204843 |

## Séquence de démarrage JS
```
boot (index.html) : fetch data/*.json → Object.assign(window) → charge src/app.js
app.js : hydrateLogs() → hydrateOverrides() → init*() → renderHeader() → renderPlan() → rwAuto() → checkAutoSync()
showTab(t) : haptique + bascule display + .actif + aria-current + render lazy + .vue-in + _revealScan()
```

## localStorage
```
runlog_v1          → séances loggées dans l'app (JSON, clés "{semaine}-{id}")
session_overrides  → déplace/skips (JSON)
ck_{course}        → checklists de course
meteo_cache, eff_temp_cache → caches (météo Lyon TTL 30 min, efficience)
dash_grp_{id}, rw_mon, rw_seen, wn_seen → préférences d'affichage (groupes repliés, rewinds, nouveautés)
install_dismissed  → bannière iOS
```
Sur iPhone, Safari et l'app de l'écran d'accueil ont des stockages séparés.

## Strava MCP (Claude uniquement, pas depuis l'app)
```
Strava:list_activities(first, range_start, range_end, ordering)
Strava:get_activity_performance(activity_id)   → FC moy/max, laps, segments, best efforts
Strava:get_activity_streams(activity_id, streams, resolution)
Strava:get_gear(gear_types=["Shoe"])           → peut exiger une approbation côté app
```

## Points de vigilance
- ⚠️ Graphes Cockpit (`_CK`) = snapshots statiques — ne se mettent pas à jour auto
- ⚠️ `ACWR_DATA` (gen.py) est un instantané daté du build ; l'app recalcule `_dynamicACWR()` en direct
- ⚠️ Nouvelle donnée dans gen.py = l'ajouter à `src/datamap.py` (sinon elle n'atteint pas l'app)
- ⚠️ Dette connue : échelle typo posée mais pas 100 % enforced sur le legacy ; graisses 700/800 dominantes ; `src/test.js` (test Node) en échec avant la refonte

## Estimations d'effort et suivi des tokens (préférence de Loïc)
Loïc s'en sert pour décider : c'est une règle à chaque demande, pas seulement pour les gros chantiers.

### 1. Avant : une estimation à chaque demande
- **Demande qui déclenche des actions** : tableau `étape | tokens | part en %` (cadrage, réalisation, vérification…), fourchettes et non valeurs uniques. Part en % = part de la conversation en cours (ou de la fenêtre de contexte si c'est un premier échange).
- **Demande minuscule** (quelques actions) : une seule ligne « Estimation : ~N tokens (x %) ».
- **État réel des limites du plan** (outil `get_usage` : fenêtre de 5 heures et hebdomadaire) et si l'étape tient dans ce qui reste.
- **Recommandation** : faire maintenant, attendre la remise à zéro de la fenêtre, ou découper. Ne jamais estimer en temps (heures, jours) ; dire que ce sont des ordres de grandeur.
- Pour un chantier de plus de quelques actions, attendre la réponse de Loïc avant de lancer.

### 2. Après : un compte rendu de dérive à chaque livraison
Relever `get_usage` au début (tokens du contexte, % de la fenêtre de 5 heures) et à la fin, et ajouter les tokens des sous-agents (annoncés dans leur retour). Puis, une fois la fonctionnalité livrée :

| Étape | Estimé | Réel | Écart |
|---|---|---|---|
| … | N à M | X | +x % / dans la fourchette / −x % |

Verdict en une phrase (dans la fourchette, ou dérive de +x % au total), **la cause principale de l'écart**, et ce qu'il faut corriger dans les prochaines estimations. Le % de fenêtre du plan est un entier : le dire quand l'écart est trop fin pour être mesuré.

### 3. Ne pas brûler de tokens pour rien (règles pour Claude)
- Chaque appel d'outil relit tout le contexte : plus la conversation est longue, plus chaque action coûte. Regrouper les commandes indépendantes en un seul appel.
- Ne jamais lire en entier les gros fichiers (`index.html`, `src/gen.py`, `src/app.js`, `data/*.json`, captures) : `grep`, `sed -n 'a,bp'`, `head`, `tail`.
- Filtrer les sorties de commande (`| tail -5`, `grep RESULTAT`) ; ne pas relire un fichier qu'on vient d'écrire ou d'éditer.
- Préférer le texte aux images (`get_page_text`, scripts d'audit) ; une capture seulement si le rendu visuel est le sujet, et à échelle réduite.
- Lancer les contrôles lourds (`release.py`, audits complets) une fois par phase, pas à chaque petite édition. Ne jamais surveiller la CI en boucle : l'Auto-fix réveille la session.
- Sous-agents : seulement quand ils protègent le contexte principal ou apportent un regard indépendant (relecture finale) ; leur coût s'ajoute (une relecture complète a coûté ~170 000 tokens).
- Modèle : Sonnet suffit pour exécuter un plan ; un modèle plus puissant seulement pour la relecture finale ou une décision d'architecture. Éviter le mode rapide sans besoin.
- Écrire un plan puis exécuter : ne pas redessiner en cours de route. Le plan et le journal (`docs/REFONTE-DECISIONS.md`) permettent de reprendre dans une conversation neuve.

### 4. Astuces pour Loïc
- **Une conversation par chantier.** Quand une phase est fusionnée, ouvrir une nouvelle conversation : Claude relit `CLAUDE.md` et repart avec un contexte léger. C'est le plus gros levier (cette refonte a fini à ~670 000 tokens de contexte : chaque action y coûtait cher).
- Commandes utiles dans Claude Code : `/context` (ce qui remplit la fenêtre), `/compact` (résumer à un moment naturel, entre deux phases), `/clear` (repartir de zéro).
- Demander l'estimation **avant** (c'est la règle) et lancer les gros chantiers juste après la remise à zéro de la fenêtre de 5 heures.
- Ne pas coller de gros fichiers ni de longues sorties dans le message : donner un chemin, Claude lit ce qu'il faut.
- Grouper les demandes liées dans un seul message plutôt que d'en enchaîner dix petites.
- Dire « mode économe » pour des réponses courtes et sans reformulation ; dire « pas de relecture indépendante » pour un petit changement.
- Une demande floue coûte plus cher qu'une demande précise : indiquer le fichier ou l'écran concerné.

## Convention commits et branches
```
feat(sprint-X): description (build N)
fix: bug — cause (build N)
data: log S{wk} seance {n} (Strava) (build N)      → branche data/S{wk}-{n}
docs: description
```
