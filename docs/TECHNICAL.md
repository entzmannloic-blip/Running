# Running PWA — Documentation Technique
> Build 40 · Juin 2026 · Loïc Entzmann

---

## 0. Protocole de travail — RÈGLES ABSOLUES

> Ces règles s'appliquent à tout intervenant (Claude, développeur humain) sans exception.

### Règle 1 — POC avant prod
**Toute nouvelle feature passe par un artifact de validation avant le push en production.**
1. Créer un POC HTML dans l'artifact (ou fichier local)
2. Le montrer à Loïc pour validation
3. Seulement après OK → intégrer dans `app.js` / `gen.py`

```
Brief → Artifact POC → OK Loïc → Code prod → node --check → Push
```

Ne jamais bypasser cette étape, même pour une feature "simple".

### Règle 2 — Checklist avant chaque push

```bash
# 1. Copier les sources vers /tmp
cp src/*.py src/*.js src/*.txt src/*.html /tmp/

# 2. Build
cd /tmp && python3 gen.py      # doit afficher "OK" et "Semaines: 30"
python3 assemble.py            # doit afficher "Écrit: XXX caractères"

# 3. Validation JS (BLOQUANT — ne jamais pusher si cette commande échoue)
node --check app.js            # doit retourner sans erreur

# 4. Tests fonctionnels
node test.js                   # doit afficher "Toutes les fonctions OK ✓"

# 5. Copier vers index.html
cp /mnt/user-data/outputs/plan-entrainement.html /home/claude/Running/index.html

# 6. Push (voir §9)
```

**Si `node --check` échoue → STOP. Corriger l'erreur avant tout push.**

### Règle 3 — CHANGELOG obligatoire
À chaque push en prod, **incrémenter le build et ajouter une entrée dans `CHANGELOG` de `gen.py`**.

```python
# Dans gen.py, CHANGELOG doit avoir le nouveau build EN PREMIER
CHANGELOG=[
  {"build": 41,             # ← Build incrémenté
   "date": "22 juin 2026",
   "sha": "xxxxxxxx",       # SHA du commit (rempli après push)
   "tag": "Nom du sprint",
   "items": [
     "Feature A — description courte",
     "Fix: Bug B — cause et correction",
   ]},
  {"build": 40, ...},       # Builds précédents conservés
  ...
]
```

Le badge "Build XX" en bas de l'app lit `CHANGELOG[0].build`. Si oublié → le badge affiche l'ancien numéro.

### Règle 4 — Fichiers à pousser
Toujours pousser `src/` ET `index.html` ensemble. Ne jamais pousser l'un sans l'autre.

| Ce qui change | Fichiers à pousser |
|--------------|-------------------|
| Plan / séances / données | `src/gen.py` + `index.html` |
| Feature JavaScript | `src/app.js` + `index.html` |
| Feature CSS | `src/css_extra.txt` + `index.html` |
| Structure HTML | `src/body.html` + `index.html` |
| Export de données (nouveau champ) | `src/assemble.py` + `src/gen.py` + `index.html` |
| Documentation uniquement | `docs/TECHNICAL.md` (sans index.html) |
| **Toute feature complète** | Tous les fichiers modifiés + `index.html` |

### Règle 5 — Mise à jour chaussures
**Après chaque séance loggée**, appeler `Strava:get_gear` et mettre à jour les km dans `gen.py` → rebuild → push. Ne pas attendre que Loïc le demande.

```python
# Dans gen.py, section GEAR
GEAR=[
  {"marque":"HOKA","modele":"Clifton 10","km": XXXX},  # ← mettre à jour
  ...
]
```

### Règle 6 — Convention des commits
Format : `type(scope): description courte (build N)`

Types :
- `feat` — nouvelle feature
- `fix` — correction de bug
- `feat(roadmap-X)` — sprint roadmap
- `docs` — documentation uniquement
- `log` — séance loggée (données athlète)
- `refactor` — amélioration sans feature visible

Exemples :
```
feat(roadmap-C): PMC Performance Management Chart CTL/ATL/TSB (build 40)
fix: ACWR dynamique via EMA — plus de valeur statique (build 40)
log S26-1: footing facile 11.2km FC 141 + Novablast V (build 41)
docs: documentation technique complete + CLAUDE.md
```

### Règle 7 — Token GitHub
Le token est un **fine-grained PAT** portée `entzmannloic-blip/Running` Contents R/W.
- **Expire : 10 septembre 2026**
- À renouveler sur `github.com/settings/tokens`
- ⚠️ Apparaît en clair dans les sessions Claude — ne jamais le partager publiquement
- Si compromis → révoquer immédiatement sur GitHub → générer nouveau → mettre à jour `CLAUDE.md`

### Règle 8 — Gestion des conflits GitHub
Toujours récupérer le SHA actuel avant de pousser un fichier :

```python
# GET le fichier pour récupérer son SHA
st, meta = api('GET', url + '?ref=main')
sha = meta.get('sha') if st == 200 else None

# PUT avec le SHA (sinon 409 Conflict)
body = {'message': MSG, 'content': b64_content, 'branch': 'main'}
if sha:
    body['sha'] = sha  # obligatoire si le fichier existe déjà
api('PUT', url, body)
```

Sans SHA sur un fichier existant → erreur 409 (conflit).


### Philosophie
Application single-file HTML déployée sur GitHub Pages. Pas de serveur, pas de base de données, pas de framework. Tout tient dans un seul `index.html` (~650 ko).

### Pipeline de build

```
src/gen.py          → génère /tmp/data.json    (données d'entraînement)
src/app.js          → logique JavaScript        (rendu, calculs, UI)
src/css.txt         → CSS de base
src/css_extra.txt   → CSS additionnel (~900 lignes)
src/body.html       → structure HTML (tabs, overlays)
src/assemble.py     → assemble tout → /mnt/user-data/outputs/plan-entrainement.html
```

```bash
# Build complet
python3 gen.py && python3 assemble.py && node --check app.js
cp /mnt/user-data/outputs/plan-entrainement.html index.html
# Push GitHub (voir section Deploy)
```

### Structure de fichiers

```
Running/
├── index.html          # Fichier déployé (généré, ne pas éditer directement)
├── src/
│   ├── gen.py          # Données athlète → data.json
│   ├── assemble.py     # Pipeline assemblage → index.html
│   ├── app.js          # Toute la logique JS (~2200 lignes)
│   ├── css.txt         # Design system de base
│   ├── css_extra.txt   # CSS additionnel features
│   └── body.html       # Squelette HTML
└── docs/
    └── TECHNICAL.md    # Ce fichier
```

---

## 2. Données : Statique vs Dynamique

### Données STATIQUES (gelées au build)
Définies dans `gen.py`, exportées en variables JS globales via `assemble.py`.
Toute modification nécessite un rebuild + push.

| Variable | Description | Taille |
|----------|-------------|--------|
| `SEMAINES` | Plan 30 semaines (S25–S53) avec thèmes, km, charges | ~30 entrées |
| `SEANCES_BY_WEEK` | Séances par semaine avec titres, allures, métriques, revues | ~131 séances |
| `DOSSIERS` | Dossiers de course (Déraille, Nice, SaintExpress) avec GPX, nutrition, checklist | 3 dossiers |
| `RACES` | Courses avec dates pour le countdown | 3 courses |
| `GEAR` | Parc chaussures avec km | 6 paires |
| `PALMARES` | Courses officielles terminées avec résultats | 5 courses |
| `REWINDS` | Diapositives de rewind hebdo | 2 semaines |
| `JOURNAL` | Bilan textuel des semaines | 2 entrées |
| `CHANGELOG` | Historique des builds | ~5 builds |
| `ACWR_DATA` | ACWR calculé au moment du build (obsolète — remplacé par `_dynamicACWR()`) | 1 dict |
| `MONTHLY` | Volumes mensuels | 12 mois |
| `SAISON2026` | Vue globale de la saison | 1 dict |

**Important :** Ces données ne se mettent pas à jour après qu'un utilisateur logue une séance. C'est un choix architectural (app personnelle, mises à jour manuelles via Claude + gen.py).

### Données DYNAMIQUES (localStorage)
Calculées en temps réel dans le navigateur, persistent entre sessions.

| Clé localStorage | Type | Description |
|-----------------|------|-------------|
| `log_{wkId}_{seId}` | JSON | Log d'une séance (km, temps, allure, RPE, nutrition) |
| `session_overrides` | JSON | Déplacements / skips de séances |
| `ck_{race}` | JSON | État checklist par course (ex: `ck_deraille`) |
| `meteo_cache` | JSON | Cache météo Open-Meteo (TTL 30min) |
| `install_dismissed` | string | `'1'` si bannière iOS install dismissée |
| `as_{seId}` | string | `'1'` si nudge auto-sync dismissé pour cette séance |
| `rw_seen` | JSON | Rewinder vus |
| `rw_mon` | string | Mois du dernier rewind affiché |

### Données MIXTES (statique + localStorage overlay)
`SEANCES_BY_WEEK` contient les plans de base. `hydrateLogs()` et `hydrateOverrides()` au démarrage enrichissent les séances avec les logs et overrides depuis localStorage.

```javascript
// Séquence de démarrage
hydrateLogs();        // Injecte realise: {statut, km, allure...} depuis localStorage
hydrateOverrides();   // Applique déplacements/skips depuis localStorage
initQuickLog();       // Initialise le formulaire de log
initCoach();          // Injecte le bouton coach et l'overlay
renderHeader();       // Affiche hero, score de forme, météo
renderPlan();         // Affiche toutes les semaines
```

---

## 3. Données Cockpit (`_CK`)

### Architecture
Le Cockpit utilise un objet `_CK` entièrement hardcodé dans `app.js` (lignes ~1415–1435). Il est généré manuellement depuis Strava et mis à jour lors des rebuilds.

```javascript
const _CK = {
  RE:   { 2: {...}, 4: {...}, 8: {...}, 12: {...} }, // Relative Effort par fenêtre
  ACWR: { 2: {...}, 4: {...}, 8: {...}, 12: {...} }, // ACWR historique
  Z2:   { 2: {...}, 4: {...}, 8: {...}, 12: {...} }, // Z2 pace EF
  VOL:  { 2: {...}, 4: {...}, 8: {...}, 12: {...} }, // Volume hebdo
  DP:   { 2: {...}, 4: {...}, 8: {...}, 12: {...} }, // Dénivelé D+
  DECOUPL: { ... },                                   // Découplage cardiaque
  PACE: { ... },                                      // Allures EF/AM/Seuil
  FC:   { ... },                                      // Zones FC
  CAD:  { ... },                                      // Cadence
  RUNS: [...],                                        // 4 sorties avec streams Strava
  STREAMS: { activityId: {hr, alt, v, km} }          // Données streams par activité
};
```

### Limitation connue
Les graphes Cockpit ne reflètent PAS les nouvelles séances loggées par l'utilisateur. Ils représentent un snapshot au moment du dernier rebuild. **C'est un bug architectural à corriger** en Sprint A.2 (auto-sync Strava).

### Exception : Score de forme (dynamique)
Le score de forme (`computeFormeScore()`) est une exception — il utilise `_CK.RE` pour l'historique ACWR mais calcule l'ACWR via EMA (`_dynamicACWR()`) qui inclut les séances loggées de la semaine courante.

---

## 4. Score de forme composite

### Formule
```
Score = ACWR × 0.30 + Adhérence × 0.25 + Z2_pace × 0.25 + Fraîcheur × 0.20
```

### ACWR (30%) — `_dynamicACWR()`
**Entièrement dynamique.** Utilise la méthode EMA (même que PMC) :
```javascript
α_CTL = 1 - exp(-7/42)  // ~0.154  (42 jours)
α_ATL = 1 - exp(-7/7)   // ~0.632  (7 jours)
CTL[i] = (1-α_CTL) * CTL[i-1] + α_CTL * weekly_RE[i]
ATL[i] = (1-α_ATL) * ATL[i-1] + α_ATL * weekly_RE[i]
ACWR   = ATL / CTL
```
Sources : `_CK.RE[12]` (historique) + séances loggées semaine courante (localStorage)

Zone | ACWR | Score
-----|------|------
Optimale | 0.8–1.3 | 100
Charge élevée | 1.3–1.5 | 58
Surcharge | >1.5 | 22
Légère sous-charge | 0.7–0.8 | 72
Sous-charge | <0.7 | 44

### Adhérence (25%)
Pourcentage de séances non-optionnelles réalisées sur les 2 dernières semaines. Source : `SEANCES_BY_WEEK` + logs localStorage.

### Z2 pace (25%)
Comparaison allure EF (FC<144) entre semaines récentes vs précédentes. Source : `realise.allure` des séances loggées avec cat=`EF`.

⚠️ **Format attendu** : `"5:56/km"` ou `"5:56"` — le parser extrait min:sec et convertit en secondes.

### Fraîcheur (20%)
Jours depuis la dernière séance loggée. Optimal : 1–2 jours.

### Couleurs
```
≥82 : teal    #0d9488   Excellent
68-81: vert   #22c55e   Bon
52-67: orange #f59e0b   Vigilance
<52 : rouge   #ef4444   Alerte
```

---

## 5. PMC — Performance Management Chart

### Calcul (`_pmcCompute()`)
Même EMA que le score de forme :
```javascript
// Pour chaque semaine dans _CK.RE[window]
CTL[i] = (1 - α_CTL) * CTL[i-1] + α_CTL * daily_RE
ATL[i] = (1 - α_ATL) * ATL[i-1] + α_ATL * daily_RE
TSB[i] = CTL[i] - ATL[i]  // Form = positif si frais, négatif si fatigué
```
`daily_RE = weekly_RE / 7`

### Valeurs attendues à S25
- CTL ~53 (fitness en légère baisse vs pic S19-S20)
- ATL ~51 (fatigue revenue à la normale après récup)
- TSB ~+2 (légèrement frais)

---

## 6. Fonctions JavaScript clés

### Démarrage
```javascript
hydrateLogs()           // Lit localStorage → enrichit SEANCES_BY_WEEK.realise
hydrateOverrides()      // Lit localStorage → applique déplacements/skips
initQuickLog()          // Injecte le sheet de log rapide dans le DOM
initCreneaux()          // Injecte le popup créneaux météo
initSessionMenu()       // Injecte le menu Déplacer/Skipper
initInstall()           // Bannière iOS install (si non-PWA)
initVersionPanel()      // Panel historique des builds
initFormeHelp()         // Overlay aide score de forme
initCkHelp()            // Overlay aide graphes Cockpit
initCoach()             // FAB 🤖 + overlay Coach
renderHeader()          // Hero: score forme + prochaine séance + météo
renderPlan()            // Toutes les semaines (lazy avec jumpToWeek)
checkAutoSync()         // Détecte séances non loggées → nudge
rwAuto()                // Déclenche le rewind si nécessaire
```

### Rendu plan
```javascript
renderPlan()            // Génère les cartes semaine + séance
renderHeader()          // Hero complet avec computeFormeScore()
ouvrirSeance(wk, id)    // Ouvre la fiche séance
ouvrirQuickLog(wk, id)  // Ouvre le formulaire de log rapide
soumettreQuickLog()     // Sauvegarde le log en localStorage
ouvrirDossier(id)       // Ouvre le dossier de course
renderChecklistHTML(id) // Génère HTML checklist J-7
_ckRender(race)         // Re-render checklist après toggle
```

### Cockpit
```javascript
renderCockpit()         // Génère le dashboard analytique complet
_ckBar()                // Graphe en barres (volume, D+, cadence)
_ckLine()               // Graphe en ligne avec zones (ACWR, Z2, découplage)
_ckOpenRun(i)           // Ouvre le drill-down d'une sortie avec streams
_pmcCompute(win)        // Calcule CTL/ATL/TSB
_pmcRender(win)         // Affiche le PMC
```

### Coach
```javascript
openCoach()             // Ouvre l'overlay chat
closeCoach()            // Ferme l'overlay chat
coachSend()             // Envoie un message (déclenche _cReply)
_cReply(txt)            // Routing keyword → handler → réponse contextuelle
_dynamicACWR()          // ACWR EMA depuis _CK.RE + logs semaine courante
computeFormeScore()     // Score composite 0-100 (toutes composantes)
```

---

## 7. Météo — Open-Meteo API

### Endpoint
```
GET https://api.open-meteo.com/v1/forecast
  ?latitude=45.7676&longitude=4.8344   (Lyon)
  &current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,precipitation
  &hourly=temperature_2m,precipitation_probability
  &daily=temperature_2m_max
  &forecast_days=10
  &timezone=Europe%2FParis
```

### Cache localStorage
Clé : `meteo_cache`
TTL : 30 minutes
```json
{
  "ts": 1718900000000,
  "temp": 31.2,
  "app": 29.8,
  "wind": 12.3,
  "code": 1,
  "precip": 0,
  "rain": false,
  "tomorrow_max": 34.1,
  "canicule_days": 8,
  "hourly_today": [[7, 28.4], [8, 30.1], ...],
  "hourly_tomorrow": [[7, 29.0], ...]
}
```

### Logique canicule
Si `canicule_days >= 3` → bannière orange affichée dans le hero.
Si `temp > 28°C` → chip créneaux horaires + ajustement allure.

---

## 8. localStorage — Schéma complet

### Logs de séances
```
log_{wkNum}_{seId}  →  JSON {
  statut: "fait",
  km: 10.03,
  temps: "59:30",
  allure: "5:56/km",
  fc_moy: 144,
  fc_max: 165,
  rpe_ressenti: 4,
  nutrition: "TA Electrolytes, Nduranz Cherry",
  commentaire: "",
  pr: 0,
  ach: 0,
  revue: "..."
}
```

### Overrides séances
```
session_overrides  →  JSON {
  "{wk}-{seId}": {
    action: "skip",          // ou "move"
    reason: "Fatigue / récupération",
    newDate: "2026-06-25"    // si action = "move"
  }
}
```

### Checklists courses
```
ck_deraille     →  JSON { "dossard": true, "gilet": false, ... }
ck_nice         →  JSON { ... }
ck_saintexpress →  JSON { ... }
```

### Sections ouvertes/fermées (checklists)
```
ck_{race}  →  inclut aussi { "_o_{sectionId}": false }  // section fermée
```

---

## 9. Deploy — Push GitHub

### Token
Fine-grained Personal Access Token, portée : `entzmannloic-blip/Running` Contents R/W.
**Expire : 10 septembre 2026** — à renouveler sur github.com/settings/tokens.

⚠️ **Le token apparaît en clair dans les sessions Claude — il doit être rotated régulièrement.**

### Script de push type
```python
import os, json, base64, urllib.request

TOK = 'github_pat_...'
REPO = 'entzmannloic-blip/Running'

def api(method, url, data=None):
    req = urllib.request.Request(url, ...)
    req.add_header('Authorization', 'Bearer ' + TOK)
    # ...

for local, remote in [('index.html','index.html'), ('src/app.js','src/app.js')]:
    # GET sha → PUT avec sha pour éviter conflicts
    url = f'https://api.github.com/repos/{REPO}/contents/{remote}'
    st, meta = api('GET', url + '?ref=main')
    sha = meta.get('sha')
    body = {'message': MSG, 'content': base64.b64encode(open(local,'rb').read()).decode(), 'branch': 'main'}
    if sha: body['sha'] = sha
    api('PUT', url, body)
```

### Fichiers poussés selon les changements
| Modification | Fichiers à pousser |
|-------------|-------------------|
| Nouvelle séance loggée | `src/gen.py` + `index.html` |
| Feature JS | `src/app.js` + `index.html` |
| Feature CSS | `src/css_extra.txt` + `index.html` |
| Nouveau dossier de course | `src/gen.py` + `index.html` |
| Chaussures mises à jour | `src/gen.py` + `index.html` |
| Ajout build au CHANGELOG | `src/gen.py` + `index.html` |

---

## 10. Audit — Valeurs statiques vs dynamiques

### ✅ Dynamiques (pas de rebuild nécessaire)
| Valeur | Méthode | Déclencheur |
|--------|---------|-------------|
| ACWR | `_dynamicACWR()` EMA | Ouverture app + log séance |
| Score de forme | `computeFormeScore()` | Ouverture app |
| Adhérence | Calcul sur `SEANCES_BY_WEEK` + localStorage | Log séance |
| Z2 pace trend | Calcul sur allures loggées | Log séance |
| Fraîcheur | `new Date()` vs dernière séance | Ouverture app |
| Météo | Open-Meteo API avec cache 30min | Ouverture app |
| Checklists | localStorage toggle | Tap item |
| Séances loggées | `hydrateLogs()` + localStorage | Démarrage |
| Overrides (déplace/skip) | `hydrateOverrides()` + localStorage | Démarrage |

### ⚠️ Statiques (rebuild requis)
| Valeur | Raison | Priorité fix |
|--------|--------|-------------|
| Graphes Cockpit (_CK) | Hardcodé dans app.js depuis Strava | Haute (Sprint A.2 auto-sync) |
| GEAR.km (chaussures) | Mis à jour manuellement | Basse (mise à jour régulière avec Claude) |
| SEMAINES / SEANCES_BY_WEEK | Structure du plan | N/A (par design) |
| PALMARES | Résultats officiels | N/A (par design) |
| DOSSIERS | Contenu des dossiers course | N/A (par design) |
| ACWR_DATA | Obsolète — remplacé par `_dynamicACWR()` | Fait |

### 🐛 Bugs identifiés et corrigés
1. **ACWR dict vs array** : `ACWR_DATA` est un dict, `ACWR_DATA.length` = undefined → composante ACWR toujours ignorée. **Corrigé** : `_dynamicACWR()` avec EMA.
2. **Couleur bouton ? Cockpit** : `color:rgba(255,255,255,.5)` invisible sur fond blanc. **Corrigé** : variables CSS `--texte-deux`.
3. **Badge Build XX** : `initVersionPanel()` injectait le badge, puis `renderHeader()` écrasait le footer. **Corrigé** : badge intégré dans `_maj` de `renderHeader()`.
4. **PALMARES vide** : variable non exportée dans `assemble.py`. **Corrigé** : ajout dans la liste des exports.
5. **Revue S25** : champ `revue` manquant dans `SEMAINES[25]` → placeholder affiché. **Corrigé** : injection via `_S25_REVUE`.

---

## 11. Design system CSS

### Variables CSS
```css
--texte          /* Texte principal */
--texte-deux     /* Texte secondaire */
--bg-card        /* Fond des cartes */
--bord-card      /* Bordure des cartes */
--gris-fond      /* Fond gris clair */
--appbar-h       /* Hauteur appbar (dynamique) */
```

### Mode nuit
Déclenché par `.body.nuit` (classe sur `<body>`). Chaque composant CSS a ses variantes nuit documentées en fin de bloc.

### Animations réutilisées
```css
@keyframes qlUp   /* Slide-up pour bottom sheets */
@keyframes qlFt   /* Fade-out pour toasts */
```

### Classes utilitaires
```
.seance-carte     Card séance
.ck-card          Card Cockpit
.vdj              Card "prochaine séance" hero
.forme-bar        Barre score de forme
.coach-fab        FAB bouton coach
.ck-help          Bouton aide ? (Cockpit)
.fb-help          Bouton aide ? (forme)
```

---

## 12. Roadmap technique

### Sprint A.2 — Auto-sync Strava (priorité haute)
**Problème** : les graphes Cockpit (`_CK`) sont statiques. Après chaque séance loggée, ils ne reflètent pas les nouvelles données.

**Solution envisagée** : à chaque ouverture de l'app, appeler l'API Strava (via un proxy ou OAuth PWA) pour récupérer les dernières activités et mettre à jour `_CK` dynamiquement.

**Contrainte** : nécessite un service proxy pour OAuth (Strava ne supporte pas PKCE public client nativement). Alternative : Cloudflare Worker avec token stocké en KV.

### Sprint D — HRV & Readiness (Garmin)
Intégrer les données de variabilité cardiaque nocturne du Garmin Fenix 6 Pro pour un score de récupération plus précis.

### Sprint E — Pacing strategy Nice
Générer un plan de course km par km pour le Marathon de Nice (8 nov.) basé sur la fitness CTL, le profil GPX et la météo prévue J-7.

---

## 13. Glossaire

| Terme | Définition |
|-------|------------|
| CTL | Chronic Training Load — fitness sur 42 jours |
| ATL | Acute Training Load — fatigue sur 7 jours |
| TSB | Training Stress Balance — forme = CTL - ATL |
| ACWR | Acute:Chronic Workload Ratio = ATL/CTL |
| EMA | Exponential Moving Average — moyenne mobile pondérée |
| RE | Relative Effort — score de charge Strava (basé sur FC) |
| Z2 | Zone 2 — effort aérobie FC < 144 bpm pour Loïc |
| EF | Endurance Fondamentale — footing facile Z2 |
| AM | Allure Marathon — séance à allure cible marathon |
| PMC | Performance Management Chart — graphe CTL/ATL/TSB |
| FC | Fréquence Cardiaque |
| FCmax | Fréquence cardiaque maximale (192 bpm pour Loïc) |
| SPM | Steps Per Minute — cadence de course |
| D+ | Dénivelé positif cumulé |
| PWA | Progressive Web App — app installable depuis le navigateur |

---

*Documentation générée par Claude · Build 40 · 21 juin 2026*
*Maintenu par : Loïc Entzmann + Claude (Anthropic)*
