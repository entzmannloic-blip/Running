# Refonte Running PWA — Plan d'implémentation

> **Pour les agents d'exécution :** SOUS-COMPÉTENCE REQUISE : `superpowers:executing-plans` (ou `superpowers:subagent-driven-development`). Les étapes utilisent des cases à cocher (`- [ ]`).

**Objectif :** Retirer le chat coach, alléger et fiabiliser l'app, et faire de chaque enrichissement de séance une petite modification vérifiée automatiquement.

**Architecture :** Les sources restent `src/` (`gen.py` → `data.json` → `assemble.py` → `index.html`). On rend le build portable (Windows, Linux, CI), on sort les données du paquet JavaScript vers `data/*.json` chargés au démarrage, on ajoute une vérification GitHub Actions, puis on traite accessibilité, cohérence et mode sombre.

**Stack :** Python 3 (build + `preflight.py`), Node 22 (`node --check`, `src/test.js`), Playwright + Chromium (tests runtime), GitHub Actions, GitHub Pages (hébergement statique, PWA ajoutée à l'écran d'accueil iOS via Safari, sans App Store).

**Spec :** décisions validées par Loïc dans la conversation du 8 octobre 2026 (section « Décisions validées » ci-dessous) ; audit : score Impeccable 11/20, corrigé en bas de ce fichier.

## Décisions validées
- Le chat coach intégré est retiré. Les conseils calculés localement (`_coachNudge`, `coachAvant`, `coachDebrief`, `COACH_THEORY`, champs « revue ») restent.
- Navigation à 4 onglets : Accueil · Séances · Cockpit · Courses (ids internes inchangés, dont `palmares`).
- Les enrichissements de séance sont faits par Claude directement sur GitHub. Claude peut fusionner automatiquement quand les contrôles sont verts et que la modification est limitée aux données.
- Le fichier unique n'est pas une contrainte : plusieurs fichiers sont acceptés.

## Contraintes globales
Chaque tâche les respecte implicitement.
- **Langue :** interface et messages en français.
- **Règle 3 de CLAUDE.md :** chaque push incrémente le numéro de build ET ajoute une entrée en tête de `CHANGELOG` dans `src/gen.py`.
- **Commits :** `feat(...)`, `fix:`, `data:`, `docs:` + `(build N)`.
- **Règle 7 :** jamais d'emoji en paire de surrogates dans `gen.py` (caractère littéral ou `\U0001F44D`).
- **Couleurs :** uniquement les tokens de `src/css.txt` (`--primary`, `--ok`, `--warn`, `--danger`, neutres). Les dégradés propres à chaque course restent tels quels.
- **localStorage :** les clés `log_{wk}_{id}`, `session_overrides`, `ck_{race}`, `meteo_cache`, `install_dismissed` doivent continuer à fonctionner à l'identique (aucune perte de séance loggée).
- **Mobile d'abord :** largeur de référence 390 px, cibles tactiles ≥ 44 px, `prefers-reduced-motion` respecté.
- **Aucun secret** dans le dépôt (le contrôle `check_no_token` doit rester vert).
- **Hébergement :** GitHub Pages, fichiers statiques seulement, `.nojekyll` conservé.
- **Contrôle avant tout push :** `preflight.py`, `node --check` et `test_regression.py` verts.

## Points de vigilance (Review Focus)
Chacun a son test dans la tâche indiquée.
1. **Réseau coupé ou lent au démarrage** : l'app affiche un message lisible, jamais un écran blanc (tâches 5 et 6).
2. **iPhone avec l'ancien cache `plan-v34`** : le téléphone migre vers la nouvelle version sans manipulation (tâche 6).
3. **Séances déjà loggées dans localStorage** : toujours affichées après chaque phase (tâches 3, 5 et 12).
4. **Semaines ISO et fin d'année** (31 déc., 1er janv.) : les tests de dates existants restent verts (tâches 1 et 5).
5. **Données vides** (semaine sans séance, course passée sans résultat, VO₂max sans records) : jamais de « NaN », « undefined » ou « 0 » trompeur (tâches 5 et 10).

## Structure des fichiers

| Fichier | Rôle | Action |
|---|---|---|
| `src/build.py` | Commande unique de build (remplace la chaîne manuelle `/tmp`) | Créer (tâche 0) |
| `src/gen.py`, `src/assemble.py` | Données et assemblage | Modifier (0, 5) |
| `data/*.json` | Données chargées au démarrage | Créer (5) |
| `src/app.js`, `src/css_extra.txt`, `src/body.html` | Interface | Modifier (3, 4, 5, 9, 10, 11) |
| `sw.js`, `manifest.json` | PWA iOS | Modifier (6) |
| `.github/workflows/verify.yml` | Contrôles automatiques | Créer (7) |
| `docs/ENRICHISSEMENT.md` | Contrat d'enrichissement pour Claude | Créer (8) |
| `PRODUCT.md`, `DESIGN.md` | Contexte produit et design (Impeccable) | Créer (2) |
| `tests/` ou `scripts/` | Tests runtime, accessibilité, captures de référence | Modifier/créer (1, 3, 9) |

## Tâches

### Tâche 0 : Environnement et build portable
**Fichiers :** créer `src/build.py` ; modifier `src/assemble.py`, `scripts/preflight.py`, `src/preflight.py`, `scripts/test_regression.py` (chemins `/tmp` et `/mnt/user-data/...` en dur).
**Prérequis (action de Loïc) :** autoriser l'installation de Python 3 sur le PC, ou choisir de porter le build en Node.
**Interfaces :** produit la commande `python src/build.py` qui écrit `index.html` à la racine du dépôt, sans dossier système externe.
- [ ] Installer Python 3, puis Playwright et Chromium. Vérifier : `python --version` répond.
- [ ] Remplacer tous les chemins `/tmp` et `/mnt/user-data/outputs` par des chemins relatifs au dépôt (dossier de travail `build/` ignoré par Git).
- [ ] Forcer `encoding='utf-8'` et `newline='\n'` à chaque ouverture de fichier. Sans cela, Windows écrit en cp1252 et en CRLF, ce qui casse les emojis (règle 7) et l'égalité octet pour octet.
- [ ] Test : `python src/build.py` produit un `index.html` identique à celui du commit actuel (`git diff --exit-code index.html` ne renvoie rien).
- [ ] Vérifier : `python scripts/preflight.py` et `python scripts/test_regression.py` passent sur la base propre.
- [ ] Commit : `chore: build portable (build 225)`.

### Tâche 1 : Filet de sécurité
**Fichiers :** créer `tests/reference/` (captures), `scripts/capture_reference.py`.
**Interfaces :** produit 4 captures de référence (Accueil, Séances, Cockpit, Courses) à 390 px, avec un état de données figé.
- [ ] Étiqueter le dépôt : tag Git `pre-refonte` sur le commit actuel.
- [ ] Écrire `capture_reference.py` avec `localStorage` vide et une date figée, pour des images reproductibles.
- [ ] Test : relancer la capture deux fois sur la base propre donne des images identiques (pixels).
- [ ] Noter dans `docs/LESSONS.md` la procédure de retour arrière (`git revert` ou retour au tag).
- [ ] Commit : `test: captures de référence (build 226)`.

### Tâche 2 : Contexte produit et design
**Fichiers :** créer `PRODUCT.md`, `DESIGN.md`.
- [ ] Lancer `impeccable init` (PRODUCT.md : utilisateur, usage, ton) puis `impeccable document` (DESIGN.md : tokens, typo, composants, règle « une couleur primaire »).
- [ ] Le DESIGN.md fixe le vocabulaire des chiffres : « sorties de la semaine », « sorties depuis S24 », « sorties de la saison » (utilisé en tâche 10).
- [ ] Vérifier : le fichier cite les tokens réels de `src/css.txt`, pas des valeurs inventées.
- [ ] Commit : `docs: PRODUCT.md et DESIGN.md (build 227)`.

### Tâche 3 : Retrait du chat coach
**Fichiers :** modifier `src/app.js`, `src/css_extra.txt`, `src/body.html`, `scripts/test_regression.py`.
**À supprimer :** dans `app.js`, `_cFmt`, `_cReply`, `_cAddMsg`, `_cTypingShow`, `_cTypingHide`, `_cBuildSystemPrompt`, `_coachHistory`, `openCoach`, `closeCoach`, `coachSend`, `coachChip` ; le bouton « Coach » de la barre dans `body.html` ; les styles `.c-*`, `.coach-ov`, `.coach-msgs`, `.coach-chips`, `.coach-fab`, `.coach-grille`, `.coach-inp-row`, `.coach-msg`, `.coach-topbar`.
**À conserver :** `_coachNudge`, `coachAvant`, `coachDebrief`, `COACH_THEORY`.
**À rebrancher :** le bouton `.coach-nudge` (ligne ~766) et le lien « Ouvrir le coach » de la feuille de détail (lignes ~1090-1094) : le premier ouvre la feuille de détail, le second est retiré. Le gestionnaire de retour (ligne ~1577) n'a plus de cas coach.
- [ ] Test : le texte `api.anthropic.com` n'apparaît plus dans `index.html`.
- [ ] Test : `openCoach`, `coachSend` et `_cBuildSystemPrompt` n'existent plus ; `coachAvant` et `coachDebrief` existent toujours.
- [ ] Test : taper la puce de conseil sur l'accueil ouvre la feuille de détail, sans erreur console.
- [ ] Remplacer les tests T07 et T08 (coach ouvre, system prompt) par ces vérifications.
- [ ] Vérifier : preflight, `node --check`, `test_regression.py` verts.
- [ ] Commit : `refactor: retrait du chat coach, conseils locaux conservés (build 228)`.

### Tâche 4 : Navigation à 4 onglets
**Fichiers :** modifier `src/body.html`, `src/css_extra.txt`.
**Interfaces :** `showTab` garde `['accueil','plan','cockpit','palmares']` ; ids `tab-accueil`, `tab-plan`, `tab-cockpit`, `tab-palmares` inchangés.
- [ ] Barre à 4 boutons de largeur égale, bouton actif avec `aria-current="page"`.
- [ ] Test : chaque bouton mesure au moins 44×44 px à 390 px.
- [ ] Test : la navigation clavier (Tab, Entrée) atteint les 4 onglets dans l'ordre.
- [ ] Mettre à jour les captures de référence pour les 4 vues et vérifier que seule la barre a changé.
- [ ] Vérifier sur l'iPhone de Loïc : barre du bas dégagée de l'indicateur d'accueil.
- [ ] Commit : `feat(nav): 4 onglets (build 229)`.

### Tâche 5 : Données hors du paquet JavaScript
**Fichiers :** modifier `src/assemble.py`, `src/app.js`, `src/test.js`, `scripts/preflight.py` ; créer `data/*.json`.
**Décision de conception :** `SEANCES_BY_WEEK` est lu de façon synchrone à 37 endroits de `app.js`. On ne la charge donc pas à la demande : on la charge **avant** le démarrage, en un seul `await`. Gain réel : l'app sort du fichier et peut être mise en cache séparément, et un enrichissement ne modifie plus que `data/*.json`. Je ne promets pas un gain de poids : le transfert actuel est de 389 Ko compressés, pas 1,36 Mo.
**Interfaces :**
- `loadData(): Promise<void>` définit les constantes globales actuelles (mêmes noms) puis appelle le démarrage existant (`hydrateLogs()` en premier).
- `loadChangelog(): Promise<Array>` charge `data/changelog.json` seulement à l'ouverture du panneau « version » (ligne ~2304). Le dernier build et la date restent dans `data/meta.json` (lignes ~761, ~762, ~1212).
- [ ] Test : pour chaque constante, le contenu rechargé depuis `data/*.json` est identique à l'ancien `const X=...` (comparaison profonde).
- [ ] Test : si `fetch` des données échoue, un message « Données indisponibles, réessaie » s'affiche avec un bouton de relance, sans écran blanc.
- [ ] Test : séances loggées dans localStorage toujours visibles après le chargement asynchrone.
- [ ] Adapter `test.js` et `preflight.py` pour lire `data/*.json` (le numéro de build est lu dans `meta.json`).
- [ ] Mesurer et noter le poids compressé de la coque (HTML + JS + CSS) et des données, avant/après.
- [ ] Commit : `refactor(data): données en JSON, changelog à la demande (build 230)`.

### Tâche 6 : Service worker et PWA iOS
**Fichiers :** modifier `sw.js`, `manifest.json`, `src/assemble.py` (balises dans le `<head>`).
**Constat de départ :** le worker actuel est « réseau d'abord » sans cache navigateur : la fraîcheur est bonne, mais tout est retéléchargé à chaque lancement.
- [ ] Relire `manifest.json` (352 octets) : `display: standalone`, icônes 192 et 512, `start_url` et `scope` corrects.
- [ ] Nom de cache dérivé du numéro de build (plus de `plan-v34` écrit à la main). Les anciens caches sont supprimés à l'activation.
- [ ] Stratégie : réseau d'abord avec délai de 3 secondes puis retour au cache, appliquée aussi à `data/*.json` ; tous les fichiers du dossier d'app sont pré-cachés à l'installation.
- [ ] Bandeau discret « Nouvelle version prête » quand un nouveau worker est installé.
- [ ] Marges de sécurité (`env(safe-area-inset-*)`) sur la barre du bas et le haut de page.
- [ ] Test : avec le réseau coupé après un premier chargement, l'app s'ouvre et affiche les données (Playwright, mode hors-ligne).
- [ ] Test : un cache `plan-v34` pré-installé est remplacé sans erreur après activation.
- [ ] Vérifier sur l'iPhone de Loïc : ouverture en mode avion, puis en 4G dégradée.
- [ ] Commit : `feat(pwa): cache versionné, hors-ligne, mise à jour visible (build 231)`.

### Tâche 7 : Vérification automatique GitHub et fusion automatique
**Fichiers :** créer `.github/workflows/verify.yml`.
**Prérequis (réglages GitHub, à faire avec l'accord de Loïc) :** autoriser la fusion automatique sur le dépôt ; exiger le contrôle `verify` sur `main`. Vérifier d'abord que `gh auth status` est connecté.
- [ ] Le workflow, sur chaque PR et chaque push : build, `git diff --exit-code index.html` (l'`index.html` committé doit être celui que le build produit), preflight, `node --check`, `test_regression.py`, contrôle de format des `data/*.json`.
- [ ] Règle de fusion automatique documentée : seules les PR dont les fichiers modifiés sont dans `data/`, `src/gen.py`, `index.html` et `fit/`, avec contrôle vert, sont fusionnées sans relecture. Toute modification de `app.js`, du CSS, de `sw.js` ou du workflow est annoncée à Loïc avant fusion.
- [ ] Test : une PR volontairement incohérente (build non incrémenté) échoue ; une PR de données valide passe.
- [ ] Commit : `ci: vérification automatique (build 232)`.

### Tâche 8 : Contrat d'enrichissement
**Fichiers :** créer `docs/ENRICHISSEMENT.md` ; mettre à jour `CLAUDE.md`, `docs/TECHNICAL.md`, `src/README.md`.
- [ ] Décrire pas à pas, pour Claude : lire Strava (`list_activities`, `get_activity_performance`, `get_gear`), quels champs écrire (`realise` : statut, km, temps, allure, FC, RPE, commentaire, revue), mise à jour des chaussures, build, contrôles, branche `data/S{sem}-{n}`, PR, conditions de fusion automatique.
- [ ] Mettre à jour `CLAUDE.md` : build réel, nouvelle commande de build, plus de `/tmp`, plus de Git Data API manuelle si les PR la remplacent, suppression de la mention du coach et du « build 51 ».
- [ ] Rappeler dans le document la gestion du token : jamais dans le dépôt, expiré le 10 septembre 2026, à renouveler.
- [ ] Test : un essai à blanc (une séance fictive loggée sur une branche) traverse le processus entier et la PR passe les contrôles.
- [ ] Commit : `docs: contrat d'enrichissement (build 233)`.

### Tâche 9 : Accessibilité
**Fichiers :** modifier `src/body.html`, `src/app.js`, `src/css_extra.txt` ; créer `scripts/audit_a11y.py` (axe-core via Playwright).
- [ ] Un `h1` par vue, des `h2` par section, `<main>` et `<nav aria-label>` ; titres de semaine et de phase en vrais titres.
- [ ] Texte de 12 px (`--t-data`) relevé à 13 px au minimum pour tout ce qui se lit ; vérifier l'échelle typo documentée.
- [ ] Les statuts portés par un emoji reçoivent un équivalent texte (exemple : le rond rouge de l'alerte de charge).
- [ ] Cibles trop petites corrigées : lignes de courses à venir (37-38 px), libellé de build.
- [ ] Test : `audit_a11y.py` ne remonte aucune violation « serious » ou « critical » sur les 4 vues.
- [ ] Test : contraste de texte ≥ 4,5:1 sur les composants principaux.
- [ ] Commit : `feat(a11y): titres, landmarks, cibles, contrastes (build 234)`.

### Tâche 10 : Cohérence des chiffres et tokens
**Fichiers :** modifier `src/app.js`, `src/css_extra.txt`.
- [ ] Libellés alignés sur le vocabulaire de `DESIGN.md` : « 58 sorties » (accueil) et « 59 sorties » (Courses) deviennent des libellés distincts et explicites.
- [ ] Jauge VO₂max : l'arc s'anime, le nombre affiche directement sa valeur (plus de passage par « 0 »).
- [ ] Remplacer les couleurs hex ad-hoc par les tokens quand un token équivalent existe ; consigner les exceptions dans `DESIGN.md`.
- [ ] Test : un script de contrôle remonte le nombre de couleurs hex hors tokens et ne doit pas augmenter ; les cas de données vides (point de vigilance 5) n'affichent ni NaN ni « undefined ».
- [ ] Commit : `fix(coherence): libellés, jauge, tokens (build 235)`.

### Tâche 11 : Mode sombre
**Fichiers :** modifier `src/css.txt` (jeu de tokens sombre), `src/assemble.py` (deux balises `theme-color`).
- [ ] Jeu de tokens sombre sous `prefers-color-scheme: dark`, sans nouvelle couleur de marque (même teal primaire, états `ok/warn/danger` réajustés pour le contraste).
- [ ] Test : captures en clair et en sombre des 4 vues ; contraste vérifié sur le sombre.
- [ ] Vérifier sur l'iPhone de Loïc : bascule automatique avec le réglage iOS, barre d'état lisible.
- [ ] Commit : `feat(theme): mode sombre suivant iOS (build 236)`.

### Tâche 12 : Finition et nouvel audit
- [ ] `impeccable polish` sur les 4 vues, puis `impeccable audit` ; comparer au 11/20 de départ.
- [ ] Revue finale de toute la branche par un relecteur indépendant (modèle le plus capable disponible).
- [ ] Relancer les captures de référence et vérifier que seuls les changements voulus apparaissent.
- [ ] Commit : `chore: finition refonte (build 237)`.

## Organisation
- Une branche par phase : A (tâches 0-2), B (3-4), C (5-7), D (8), E (9-12).
- Les phases A, C (partie CI) et D sont fusionnées automatiquement quand les contrôles sont verts. Les phases B, C (app) et E modifient l'interface : je fusionne quand les contrôles sont verts et les captures conformes, puis Loïc valide sur son iPhone. En cas de problème, retour arrière par `git revert` ou par le tag `pre-refonte`.

## Corrections de l'audit initial
Trois points de l'audit de départ étaient inexacts ou incomplets, mesures faites après lecture du dépôt :
1. **Poids :** le transfert réel est de 389 Ko compressés (1,36 Mo n'est que la taille brute). La note Performance passe de 1 à 2. Le vrai coût est le retéléchargement à chaque lancement.
2. **Zoom :** le zoom n'est pas bloqué (aucun `maximum-scale` ni `user-scalable=no`). Ce point est retiré.
3. **Structure :** les sources étaient déjà séparées et un contrôle `preflight.py` existait. Il manquait surtout la vérification automatique côté GitHub.
