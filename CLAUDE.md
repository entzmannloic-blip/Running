# CLAUDE.md — Contexte Running PWA

## ⚠ Learning — LIRE EN PREMIER
Ce projet apprend de ses erreurs. **Avant tout push**, lancer depuis /tmp :
```
python3 scripts/preflight.py
```
Il encode mécaniquement les erreurs passées (pipeline stale, build désync, syntaxe JS, emoji surrogate-pair, mauvaise semaine ISO, token en clair, HTML tronqué). Un échec critique = **ne pas pousser**.

Le détail de chaque leçon (cause racine + garde-fou) est dans **docs/LESSONS.md**. Quand une nouvelle erreur survient : la corriger, la consigner dans LESSONS.md, et si elle est mécanisable ajouter un check dans preflight.py.
> Ce fichier est lu en premier par Claude Code avant toute action sur ce repo.
> Documentation complète : docs/TECHNICAL.md

## Identité
**App** : Running PWA — coaching running personnel pour Loïc Entzmann
**Repo** : entzmannloic-blip/Running (GitHub Pages)
**Build actuel** : 51
**Token GitHub** : fine-grained PAT, expire 10 septembre 2026

## Athlète
- **Loïc Entzmann** · Lyon · M0 (30-34) · 84 kg
- FCmax 192 · Z2 max 144 bpm · Seuil marche ~160 bpm
- **Courses 2026** : Trail Déraille 5 juil (24km) · Marathon Nice 8 nov (objectif 3h45) · SaintExpress 28 nov (45km nuit)

## Règles absolues (voir docs/TECHNICAL.md §14 pour le détail)

1. **POC avant prod** — Toute feature visuelle = artifact POC → validation Loïc → code prod
2. **Checklist build** : `python3 gen.py && python3 assemble.py && node --check app.js`
   - `node --check` qui échoue = STOP, ne jamais push
3. **CHANGELOG obligatoire** — Incrémenter le build ET ajouter une entrée avant chaque push
4. **Fichiers** — Toujours pousser `src/` modifiés + `index.html` ensemble (commit atomique via Git Data API)
5. **Chaussures** — `Strava:get_gear` après chaque log de séance → update gen.py (km arrondi) → rebuild
6. **SHA** — Toujours GET le SHA/ref avant le commit (sinon 409 Conflict)
7. **⚠️ Emojis dans gen.py** — Ne jamais écrire un emoji via paire de surrogates (ex. `\uD83D\uDC4D`) en Python : `open('w')` tronque puis `.write()` lève UnicodeEncodeError → gen.py vidé. Utiliser le caractère littéral ou `\U0001F44D`. Si gen.py vidé : le restaurer depuis le dernier build poussé (`raw.githubusercontent.com/.../main/src/gen.py`).

## Pipeline build
```bash
cp src/gen.py src/app.js src/css.txt src/css_extra.txt src/body.html src/assemble.py src/hist.json /tmp/
cd /tmp && python3 gen.py && python3 assemble.py && node --check app.js
# sortie attendue gen.py : "Semaines: 30 | Séances: 131"
cp /mnt/user-data/outputs/plan-entrainement.html index.html
```

## Fichiers clés (compteurs au build 51)
- `src/gen.py` (~932 lignes) — données : plan, séances, chaussures, dossiers, palmarès, CHANGELOG
- `src/app.js` (~2274 lignes, 184 fonctions) — toute la logique JS
- `src/css.txt` (~161 lignes) — :root design tokens + base
- `src/css_extra.txt` (~972 lignes) — CSS features
- `src/body.html` (18 lignes) — structure HTML (vues + bottom bar)
- `src/assemble.py` (30 lignes) — pipeline + liste des exports JS

## ⭐ Navigation & IA actuelle (refonte builds 42→51 — IMPORTANT)
La nav a été entièrement refondue. **Plus de tabbar en haut** : une **bottom bar fixe** `#botbar` (frostée, safe-area).

**5 items de barre** (l'ordre + ids comptent pour `showTab`) :
```
Accueil · Séances · [Coach central] · Cockpit · Courses
```
- **Accueil** (`#vue-accueil`, id tab `accueil`) — dashboard : `#hero-plan` (héros prochaine séance, forme, course, météo, **#canicule-banner**, mini-courses) + `#accueil-annee` (bilan du plan). 2 raccourcis : le héros `.vdj` → `ouvrirSeance()`, la carte `.cw-link` → `jumpToWeek()`.
- **Séances** (`#vue-plan`, id `plan`) — le **plan seul** (`#main` + `#phases`), sans dashboard.
- **Coach** (centre, surélevé) — `openCoach()`. Message d'accueil contextuel priorisé : **canicule > charge (ACWR>1.4) > affûtage course ≤7j > marge**.
- **Cockpit** (`#vue-cockpit`, id `cockpit`) — analytique. `showTab('cockpit')` rend **`renderCockpit()` ET `renderDash()`** : `#cockpit-contenu` (PMC, allures, zones) + `#dash-contenu` (bilan/charge, ex-Suivi).
- **Courses** (`#vue-palmares`, id interne **toujours `palmares`**) — `renderPalmares()` = section **À venir** (depuis `RACES`, J-X + `ouvrirDossier`) + **Passées** (depuis `PALMARES`, résultats).

**Pièges à connaître :**
- ⚠️ L'onglet **« Suivi » n'existe plus** : il a été dissous. `renderDash()` existe encore mais est rendu **dans Cockpit** (`#dash-contenu` vit dans `#vue-cockpit`). Ne pas chercher `#vue-dash` (supprimé).
- ⚠️ L'onglet « Courses » garde l'**id interne `palmares`** (tab-palmares, vue-palmares, showTab('palmares')). Seuls le label et l'icône ont changé.
- ⚠️ `showTab` liste `['accueil','plan','cockpit','palmares']`.
- ⚠️ Vue par défaut au chargement = **Accueil** (vue-accueil visible, tab-accueil `.actif` dans body.html).

## Design system (build 42)
`css.txt :root` = tokens sémantiques. **1 primaire** `--primary:#0d9488` (teal) ; états `--ok` `--warn` `--danger` (+ variantes `-deux/-clair/-fond`) ; neutres slate (`--texte`, `--gris-*`) ; échelle typo `--t-display…--t-data` ; `--ombre`/`--ombre-lg` ; `--ease`. Les anciens noms de couleur (`--vert`, `--bleu`, `--orange`…) sont des **alias** vers les tokens. Ne pas réintroduire de couleurs ad-hoc. Identités dégradées par course (dossiers) = préservées exprès.

## Couche mouvement (build 47)
Transition de vue `.vue-in` (fondu-montant), reveal au scroll (`_revealScan()` / IntersectionObserver, filet de sécurité 4s), press-scale, pop d'icône active, haptique (`navigator.vibrate`). Tout sous `prefers-reduced-motion`.

## Données clés gen.py
- Plan : S25→S53 (30 semaines, 131 séances)
- Courses : `RACES[3]` — Déraille, Nice, SaintExpress (nom, date, dossier)
- Chaussures : `GEAR[6]` — voir tableau
- Palmarès : `PALMARES[5]` — 5 courses officielles passées
- Séances loggées : surcharge `arr[i]["realise"]={...}` dans un bloc `if n==NN:` de la boucle WEEKS (statut/km/temps/allure/fc_moy/fc_max/rpe_ressenti/commentaire/revue)

## Parc chaussures (build 51)
| Modèle | Km | Convention | gear_id Strava |
|--------|----|-----------|----------------|
| HOKA Clifton 10 | 1103 | Décrassages ≤10 km | 28498174 |
| ASICS Gel Pulse 16 | 225 | Footings faciles | 28498182 |
| Brooks Cascadia 19 | 196 | Trail | 28498287 |
| ASICS Novablast 5 J | 513 | Training route (jaune) | 28722452 |
| ASICS Novablast 5 V | 0 | Courses (vert, neuf) | — |
| ASICS Magic Speed 4 | 51 | AM/qualité | 29204843 |

## Séquence de démarrage JS
```
hydrateLogs() → hydrateOverrides() → init*() → renderHeader() → renderPlan() → rwAuto() → checkAutoSync()
showTab(t) : haptique + bascule display + .actif + render lazy + .vue-in + _revealScan()
```

## localStorage
```
log_{wk}_{id}      → séances loggées (JSON)
session_overrides  → déplace/skips (JSON)
ck_{race}          → checklists (JSON)
meteo_cache        → météo Lyon (TTL 30min)
install_dismissed  → bannière iOS
```

## Strava MCP (Claude uniquement, pas depuis l'app)
```
Strava:list_activities(first, range_start, range_end, ordering)
Strava:get_activity_performance(activity_id)   → FC moy/max, laps, segments, best efforts
Strava:get_activity_streams(activity_id, streams, resolution)
Strava:get_gear(gear_types=["Shoe"])           → peut exiger une approbation côté app
```

## Points de vigilance
- ⚠️ Graphes Cockpit (_CK) = snapshots statiques — ne se mettent pas à jour auto
- ⚠️ `ACWR_DATA` dans gen.py est obsolète — remplacé par `_dynamicACWR()` (EMA) dans app.js
- ⚠️ Token expire 10 sept. 2026 (penser à le révoquer après push — il transite en clair)
- ⚠️ Nouveau champ gen.py = aussi l'ajouter dans assemble.py
- ⚠️ Dette connue (audit) : échelle typo posée mais pas 100 % enforced sur le legacy ; graisses 700/800 encore dominantes ; reveal limité aux vues principales

## Convention commits
```
feat(sprint-X): description (build N)
fix: bug — cause (build N)
data: log S{wk} seance {n} (Strava) (build N)
docs: description
```
