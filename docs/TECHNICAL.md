# Running PWA — Documentation Technique Complète
> Version 2.0 · Build 40 · 21 juin 2026
> Application personnelle de coaching running pour Loïc Entzmann

---

## TABLE DES MATIÈRES

1. [Contexte & Philosophie](#1-contexte--philosophie)
2. [Profil Athlète](#2-profil-athlète)
3. [Architecture](#3-architecture)
4. [Environnement de développement](#4-environnement-de-développement)
5. [Pipeline de build — gen.py](#5-pipeline-de-build--genpy)
6. [Pipeline de build — assemble.py](#6-pipeline-de-build--assemblepy)
7. [JavaScript — app.js](#7-javascript--appjs)
8. [CSS — Design System](#8-css--design-system)
9. [Structure HTML — body.html](#9-structure-html--bodyhtml)
10. [Données — Statique vs Dynamique](#10-données--statique-vs-dynamique)
11. [localStorage — Schéma complet](#11-localstorage--schéma-complet)
12. [Strava Integration](#12-strava-integration)
13. [API Météo — Open-Meteo](#13-api-météo--open-meteo)
14. [Protocole de travail — RÈGLES](#14-protocole-de-travail--règles)
15. [Deploy — GitHub Pages](#15-deploy--github-pages)
16. [Playbook de maintenance](#16-playbook-de-maintenance)
17. [Feature Registry — Toutes les features](#17-feature-registry--toutes-les-features)
18. [Audit — Bugs identifiés et corrigés](#18-audit--bugs-identifiés-et-corrigés)
19. [Guide de réplication — Nouvel athlète](#19-guide-de-réplication--nouvel-athlète)
20. [Roadmap technique](#20-roadmap-technique)
21. [Glossaire](#21-glossaire)

---

## 1. Contexte & Philosophie

### Pourquoi cette app existe
Application de coaching running 100% personnalisée, construite **pour un seul athlète** par Claude (Anthropic) en pair-programming avec Loïc Entzmann. Elle remplace un ensemble d'outils génériques (Strava, Garmin Connect, TrainingPeaks) par un seul endroit où toutes les données de l'athlète convergent avec un contexte complet.

### Ce que les apps généralistes ne peuvent pas faire
Strava connaît les km. Garmin connaît le HRV. Cette app connaît Loïc :
- Son protocole nutritionnel exact (TA Electrolytes, Nduranz Cherry, Nduranz Amarena)
- La leçon de la Circaète (crise électrolytique, déshydratation)
- Ses chaussures avec les km exacts sur chaque paire
- Son historique de courses officielles avec bilans coach
- Son objectif Nice 3h45 et les allures cibles dérivées

### Philosophie technique
- **Single-file PWA** : tout dans un `index.html`. Zéro serveur, zéro DB, zéro framework.
- **Iteration rapide** : brief vocal → POC en chat → validation → push prod en quelques minutes
- **Claude comme co-pilot** : Claude lit les sources, fait les modifications, valide, push. Loïc approuve.
- **Strava MCP** : accès temps réel aux données Strava via le Model Context Protocol
- **localStorage first** : les données dynamiques (logs, checklists, overrides) restent sur l'appareil

### Stack
```
Python 3  →  gen.py (données)
Python 3  →  assemble.py (pipeline)
Vanilla JS  →  app.js (2244 lignes, 184 fonctions)
CSS         →  css.txt + css_extra.txt (904 lignes)
HTML        →  body.html (19 lignes, structure minimaliste)
GitHub Pages →  hosting
Strava MCP   →  données activités temps réel
Open-Meteo  →  météo Lyon (gratuit, sans clé)
```

---

## 2. Profil Athlète

> Ces constantes sont utilisées dans les calculs. À adapter pour un autre athlète.

### Identité
```python
NOM = "Loïc Entzmann"
AGE = 32  # M0 (30-34 ans)
POIDS = 84  # kg
VILLE = "Lyon"
COORDONNEES_METEO = (45.7676, 4.8344)  # Lyon Perrache
```

### Physiologie
```python
FC_MAX = 192          # bpm — mesurée
FC_SEUIL_MARCHE = 160 # bpm — au-dessus = on court, en dessous = marche trail OK
FC_Z2_MAX = 144       # bpm — plafond Zone 2 (FC_MAX × 0.75)
VO2MAX_ESTIME = 48    # ml/kg/min — estimé Garmin
```

### Zones FC (basées sur FCmax = 192)
| Zone | Nom | BPM | % FCmax | Allure typique |
|------|-----|-----|---------|----------------|
| Z1 | Récupération | < 134 | < 70% | ≥ 6:45/km |
| Z2 | Endurance fondamentale | 134–154 | 70–80% | 5:50–6:25/km |
| Z3 | Tempo / marathon | 154–167 | 80–87% | 5:05–5:30/km |
| Z4 | Seuil | 167–177 | 87–92% | 4:40–4:55/km |
| Z5 | VO2 / VMA | 177–192 | 92–100% | ≤ 4:20/km |

### Courses 2026
| Course | Date | Distance | D+ | Objectif |
|--------|------|----------|----|----------|
| Trail Déraille | 5 juillet 2026 | 24 km | +901 m | C — test nutrition |
| Marathon de Nice | 8 novembre 2026 | 42.195 km | +180 m | A — 3h45 (5:20/km) |
| SaintExpress | 28 novembre 2026 | 45 km | départ 23h | B — finisher nuit |

### Allures cibles
```python
ALLURES = {
  "EF_Z2":     "5:50–6:25/km",  # Endurance fondamentale (socle)
  "marathon":  "5:20/km",        # Objectif Nice 3h45
  "seuil_60":  "4:55/km",        # Seuil 60min
  "seuil_30":  "4:40/km",        # Seuil 30min
  "trail_montee": "9:00–10:00/km", # Trail montée technique
}
```

### Nutrition course
```python
NUTRITION_PROTOCOL = {
  "TA_Electrolytes": "350mg Na + 80mg K + 52mg Mg / comprimé",
  "Nduranz_Cherry":  "65mg caféine / gel",
  "Nduranz_Amarena": "130mg caféine / gel",
  "Aptonia":         "gels non-caféinés",

  # Protocole Déraille (24km)
  "deraille": {
    "départ":  "2 cpr TA dans les flasques + 1 gel Aptonia",
    "km_8":    "1 cpr TA au ravito + 1 gel Aptonia",
    "km_13":   "Nduranz Cherry 65mg",
    "km_20":   "Nduranz Coffee Amarena 130mg",
    "arrivée": "1 cpr TA immédiatement",
  },

  # Protocole Nice (42.195km)
  "nice": {
    "réveil_5h": "2 cpr TA",
    "km_0":      "1 gel Aptonia",
    "km_8":      "1 gel Aptonia",
    "km_16":     "1 gel Aptonia",
    "km_24":     "1 gel Aptonia",
    "km_32":     "Nduranz Cherry 65mg — anti-mur",
    "km_38":     "Nduranz Coffee Amarena 130mg — relance finale",
  }
}
```

### Parc chaussures
```python
GEAR = [
  {"marque":"HOKA",  "modele":"Clifton 10",       "km":1103, "usage":"Décrassages <10km seulement — fin de vie"},
  {"marque":"ASICS", "modele":"Gel Pulse 16",      "km":225,  "usage":"Footings faciles route"},
  {"marque":"Brooks","modele":"Cascadia 19",        "km":196,  "usage":"Trail exclusivement"},
  {"marque":"ASICS", "modele":"Novablast 5 J",      "km":502,  "usage":"Training route principal (jaune)"},
  {"marque":"ASICS", "modele":"Novablast 5 V",      "km":0,    "usage":"Courses, fraîches (vert)"},
  {"marque":"ASICS", "modele":"Magic Speed 4",      "km":51,   "usage":"Séances AM/qualité uniquement"},
]
# Convention Strava: "J" = jaunes, "V" = vertes
# gear_id Strava: Clifton=28498174, Pulse=28498182, Cascadia=28498287, NB J=28722452, Magic=29204843
```

---

## 3. Architecture

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────┐
│                   CLAUDE (AI maintainer)            │
│  • Reçoit briefings vocaux de Loïc                  │
│  • Lit/modifie les sources via outils               │
│  • Valide le build                                  │
│  • Push via GitHub API                              │
└──────────┬──────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│                   BUILD PIPELINE                      │
│                                                       │
│  src/gen.py  ──────→  /tmp/data.json                 │
│      ↓                     ↓                         │
│  src/app.js  ──────→  assemble.py  ──→  index.html   │
│  src/css*.txt ──────↗                                │
│  src/body.html ─────↗                                │
└──────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│              GitHub Pages (public)                   │
│   entzmannloic-blip.github.io/Running/index.html    │
└──────────────────────────────────────────────────────┘
           │
           ▼ (ouverture sur iPhone)
┌──────────────────────────────────────────────────────┐
│                    NAVIGATEUR                         │
│                                                       │
│  index.html (650 ko)                                 │
│      │                                               │
│      ├── Variables JS globales (gen.py data)         │
│      ├── hydrateLogs() ← localStorage                │
│      ├── hydrateOverrides() ← localStorage           │
│      ├── renderHeader() → météo, score forme         │
│      ├── renderPlan() → semaines, séances            │
│      └── Cockpit, Palmarès, Coach...                 │
│                                                       │
│  localStorage                                        │
│      ├── log_{wk}_{id} → séances loggées            │
│      ├── session_overrides → déplace/skips           │
│      ├── ck_{race} → checklists                     │
│      └── meteo_cache → météo 30min                  │
└──────────────────────────────────────────────────────┘
```

### Services externes
```
Open-Meteo API    https://api.open-meteo.com/v1/forecast
                  → Météo Lyon, gratuit, sans clé, forecast 10j

Strava MCP        https://mcp.strava.com/mcp
                  → Activités, streams FC/allure/altitude, gear
                  → Utilisé par Claude uniquement (pas depuis l'app)
                  → Auth : OAuth Strava via Claude.ai

GitHub API        https://api.github.com/repos/entzmannloic-blip/Running/
                  → Deploy des fichiers via fine-grained PAT
```

---

## 4. Environnement de développement

### Prérequis (environnement Claude)
- Python 3.10+ (gen.py, assemble.py)
- Node.js 22+ (validation JS)
- Accès réseau : api.github.com, api.open-meteo.com, mcp.strava.com
- Strava MCP connecté dans Claude.ai
- Token GitHub PAT (voir §15)

### Chemins importants
```
/home/claude/Running/          ← repo local
/home/claude/Running/src/      ← sources (à modifier)
/home/claude/Running/index.html← fichier déployé (généré)
/tmp/                          ← répertoire de build
/tmp/data.json                 ← données générées par gen.py
/mnt/user-data/outputs/        ← outputs de assemble.py
```

### Copie sources → /tmp (TOUJOURS faire avant build)
```bash
cp /home/claude/Running/src/*.py \
   /home/claude/Running/src/*.js \
   /home/claude/Running/src/*.txt \
   /home/claude/Running/src/*.html \
   /tmp/
```

### Commandes de validation
```bash
cd /tmp

# 1. Générer les données
python3 gen.py
# ✓ Attendu : "Semaines: 30 | Séances: 131\nOK"

# 2. Assembler l'HTML
python3 assemble.py
# ✓ Attendu : "Écrit: XXXXXX caractères"

# 3. Valider la syntaxe JS (BLOQUANT)
node --check app.js
# ✓ Attendu : aucun output (succès silencieux)
# ✗ Sinon : SyntaxError avec numéro de ligne → CORRIGER avant push

# 4. Tests fonctionnels
node test.js
# ✓ Attendu : "Toutes les fonctions de rendu s'exécutent sans erreur ✓"
```

---

## 5. Pipeline de build — gen.py

### Rôle
Génère `/tmp/data.json` contenant toutes les données statiques de l'app. C'est la source de vérité pour le plan d'entraînement.

### Structure du fichier (854 lignes)

#### Lignes 1–39 : Imports et constantes
```python
import json as _j
from datetime import date, timedelta

# Constantes athlète
FCmax = 192
POIDS = 84
SEUIL_MARCHE = 160

# Couleurs par type de séance
EF_COLOR = "#4ade80"    # Vert clair — Endurance fondamentale
AM_COLOR = "#3b82f6"    # Bleu — Allure marathon
ORANGE = "#f97316"      # Orange — Sortie longue
SEUIL_COLOR = "#8b5cf6" # Violet — Séance seuil
TRAIL_COLOR = "#0d9488" # Teal — Trail
RECUP_COLOR = "#94a3b8" # Gris — Récupération
```

#### Lignes 40–310 : Fonctions helper séances

```python
def ef(dist, dur, strides=False, opt=False, recovery=False, desc=None):
    """
    Crée une séance Endurance Fondamentale (Zone 2).
    
    Args:
        dist: Distance en km
        dur:  Durée en minutes
        strides: True = lignes droites à la fin (accélérations)
        opt:  True = séance optionnelle (ne compte pas pour l'adhérence)
        recovery: True = footing de récupération (style différent)
        desc: Description personnalisée (override)
    
    Returns: dict séance avec titre, sous-titre, métriques, cat='EF', accent=EF_COLOR
    """

def mp(dist, dur, blocs, km_each, desc, fill=78, warm_min=15, cool_min=10):
    """
    Crée une séance Allure Marathon avec blocs de qualité.
    
    Args:
        dist:    Distance totale en km
        dur:     Durée totale en minutes
        blocs:   Nombre de blocs AM
        km_each: Km par bloc
        desc:    Description du contenu
        fill:    FC cible pendant les blocs (défaut: 78% FCmax ≈ 150 bpm)
        warm_min/cool_min: Durée échauffement/récup
    
    Returns: dict séance avec segments détaillés, cat='AM', accent=AM_COLOR
    """

def longrun(dist, dur, mp_km=0, fuel=True, desc=None, heat=False):
    """
    Crée une séance Sortie Longue.
    
    Args:
        dist:   Distance totale km
        dur:    Durée minutes
        mp_km:  Km à allure marathon en fin (fast finish)
        fuel:   True = nutrition obligatoire (TA + gels)
        desc:   Description override
        heat:   True = étiquette canicule
    
    Returns: dict séance, cat='LONG', accent=ORANGE
    """
```

#### Lignes 311–549 : Construction du plan (fonction W)

```python
def W(n, ss):
    """
    Enregistre les séances d'une semaine.
    
    Args:
        n:  Numéro de semaine ISO (25, 26, ...)
        ss: Liste de séances [ef(...), mp(...), longrun(...)]
    
    Usage:
        W(25, [
            ef(10, 65, strides=True),           # s1 — lundi
            ef(9, 55),                           # s2 — mardi
            mp(12, 72, 1, 6, "Premier contact AM"), # s3 — mercredi
            longrun(18, 110, heat=True),         # s4 — jeudi
            ef(10, 65),                          # s5 — vendredi (opt)
        ])
    """
    WEEKS[n] = ss

# Le plan complet est défini ici, semaines S25 à S53
W(25, [...])  # Reprise & déblocage
W(26, [...])  # Allègement prépa Déraille
# ... jusqu'à S53 (Bilan 2027)
```

#### Lignes 550–567 : Métadonnées semaines (META + SEMAINES)

```python
# META : [(num, phase, theme, km, charge, repartition, objectif), ...]
META = [
  (25, "REPRISE", "Reprise & déblocage", 52, "Modérée", "4EF+1AM+1LONG", "..."),
  (26, "AFFÛTAGE", "Allègement + prépa Déraille", 35, "Légère", "3EF+1TRAIL", "..."),
  # ...
]

# SEMAINES est construit depuis META + peut recevoir des champs additionnels
SEMAINES = [{"num": n, "phase": p, "theme": t, "km": k, ...} for (...) in META]

# Ajout des revues coach (après coup)
_S25_REVUE = "<p>La semaine de reprise..."
for _s in SEMAINES:
    if _s["num"] == 25: _s["revue"] = _S25_REVUE
```

#### Lignes 568–577 : GEAR (chaussures)

```python
GEAR = [
  {"marque": "HOKA",   "modele": "Clifton 10",   "km": 1103},
  {"marque": "ASICS",  "modele": "Gel Pulse 16",  "km": 225},
  # ...
]
# Mise à jour manuelle après chaque séance loggée (via Strava:get_gear)
```

#### Lignes 578–741 : DOSSIERS (dossiers de course)

```python
DOSSIERS = {
  "deraille": {
    "titre":    "Trail Déraille — Lac des Sapins",
    "date":     "5 juillet 2026",
    "format":   "24 km · +901 m · départ ~9h",
    "objectif": "C — test nutrition et sensations",
    "terrain":  "Description du terrain...",
    "plan":     "4 étapes avec allures cibles...",
    "nutrition": "2 cpr TA départ, gels km 0/8...",
    "errors":   ["Ne pas partir trop vite", ...],
    "sources":  "Données organisateur + GPX",
  },
  "nice":        {...},
  "saintexpress": {...},
}
```

#### Lignes 742–810 : Données analytics

```python
MONTHLY = [  # 12 entrées, une par mois
  {"mois": "Jan.", "km": 112.4, "sorties": 14, ...},
  ...
]

SAISON2026 = {
  "km": 1361, "elev": 16222, "sorties": 108, "mois": 6
}

ACWR_DATA = {  # Obsolète — remplacé par _dynamicACWR() dans app.js
  "charge7j": 951, "charge28j": 2424, "acwr": 1.57,
  "interpretation": "..."
}

ALLURES_COURSE = [...]  # Table de référence allures/temps
ALLURES = [...]         # Description des zones d'allure
ZONES_FC = [...]        # Zones FC avec couleurs et BPM
```

#### Lignes 811–843 : Contenu éditorial

```python
REWINDS = [   # Diapositives de bilan hebdo
  {
    "id": "S25",
    "titre": "Ta semaine 25",
    "sous": "Reprise & déblocage · 15-19 juin",
    "slides": [
      {"bg": "linear-gradient(...)", "kicker": "LE VOLUME", "big": "56,6 km", "txt": "..."},
      # 10 slides par semaine
    ]
  },
  ...
]

JOURNAL = [   # Bilans textuels des semaines
  {"sem": "S25", "theme": "Reprise & déblocage", "texte": "<p>...HTML..."},
]

HEATMAP = {   # Km par date pour le calendrier annuel
  "2026-01-03": 10.1,
  "2026-01-05": 11.2,
  # ... toutes les sorties de l'année
}
```

#### Lignes 844–859 : CHANGELOG + PALMARES + export

```python
CHANGELOG = [   # Historique des builds (Build N en premier)
  {"build": 40, "date": "21 juin 2026", "sha": "...", "tag": "...", "items": [...]},
  ...
]

PALMARES = [    # Courses officielles terminées
  {
    "nom": "Trail - Circaète (Gypaète)",
    "date": "2026-06-06",
    "type": "trail",
    "distance": 29.8,
    "dplus": 1661,
    "temps": "4:57:38",
    "allure": "9:36",
    "classement_gen": 182,
    "cat": "M0",
    "fc_moy": 152, "fc_max": 178,
    "bilan": "HTML du bilan coach...",
    # ...
  },
  ...
]

# Export final vers /tmp/data.json
_j.dump({
  "PHASES": PHASES, "COUL": COUL,
  "SEMAINES": SEMAINES, "SBW": SEANCES_BY_WEEK,
  "GEAR": GEAR, "RACES": RACES,
  "DOSSIERS": DOSSIERS, "PALMARES": PALMARES,
  "CHANGELOG": CHANGELOG,
  # ... toutes les variables
}, open('/tmp/data.json', 'w'), ensure_ascii=False)
print("OK")
```

### SEANCES_BY_WEEK (SBW)
Structure clé pour l'affichage des séances :
```python
{
  "25": [  # Semaine 25
    {
      "id": 1,           # Index dans la semaine (1-based)
      "num": 1,          # Numéro affiché ("Séance 1")
      "titre": "Footing facile + lignes droites",
      "sous": "~65 min · rythme conversation",
      "type": "EF aérobie",
      "cat": "EF",       # EF | AM | LONG | SEUIL | TRAIL | RENFO
      "accent": "#4ade80", # Couleur de la barre latérale
      "rpe": 4,          # RPE planifié (1-10)
      "date": "2026-06-15", # Date ISO planifiée
      "opt": False,      # Séance optionnelle
      "chaussure": "ASICS Gel Pulse 16",
      "metriques": {
        "Distance": "10 km",
        "Durée": "65 min",
        "Allure cible": "5:50–6:10/km",
        "FC cible": "< 144 bpm (Z2)",
      },
      "description": "HTML de description détaillée...",
      "fit": None,       # URL du fichier .fit Garmin si généré
      "realise": {       # Injecté par hydrateLogs() depuis localStorage
        "statut": "fait",
        "km": 10.25,
        "temps": "1:00:12",
        "allure": "5:51/km",
        "fc_moy": 143,
        "fc_max": 173,
        "rpe_ressenti": 5,
        "nutrition": "TA Electrolytes",
        "revue": "HTML du bilan coach...",
      }
    },
    # ... autres séances de la semaine
  ],
  "26": [...],
  # ... jusqu'à la semaine 53
}
```

---

## 6. Pipeline de build — assemble.py

### Rôle (30 lignes, simple)
Lit `/tmp/data.json` + les sources (`app.js`, `css.txt`, `css_extra.txt`, `body.html`) et génère le fichier HTML final.

```python
import json, re

# 1. Lire data.json
data = json.load(open('/tmp/data.json'))

# 2. Générer les declarations JS globales
# Chaque clé devient une variable JS accessible globalement
DATA_JS = "".join(
    f"const {k}={json.dumps(data[v], ensure_ascii=False)};\n"
    for k, v in [
        ("PHASES", "PHASES"),
        ("SEMAINES", "SEMAINES"),
        ("SEANCES_BY_WEEK", "SBW"),
        ("GEAR", "GEAR"),
        ("RACES", "RACES"),
        ("DOSSIERS", "DOSSIERS"),
        ("PALMARES", "PALMARES"),
        ("CHANGELOG", "CHANGELOG"),
        ("ALLURES", "ALLURES"),
        ("MONTHLY", "MONTHLY"),
        # ... tous les champs nécessaires
    ]
)

# 3. Assembler le HTML final
html = f"""<!DOCTYPE html>
<html lang="fr">
<head>...</head>
<body>
{body_html}
<style>{css_base}{css_extra}</style>
<script>
{DATA_JS}
{app_js}
</script>
</body>
</html>"""
```

### ⚠️ IMPORTANT : Ajouter un nouveau champ
Si `gen.py` exporte un nouveau champ dans `data.json`, il faut **aussi l'ajouter dans `assemble.py`** :

```python
# Dans assemble.py, liste des exports :
("NOUVEAU_CHAMP", "NOUVEAU_CHAMP"),  # ← ajouter ici
```

Sinon la variable n'existera pas dans l'HTML et causera des erreurs JS silencieuses.

---

## 7. JavaScript — app.js

### Organisation générale (2244 lignes)

```
Lignes 1–50      : Fonctions utilitaires (isoWeek, findSeance, formatTime...)
Lignes 51–432    : Suivi perf (renderDash, renderCrystalBall...)
Lignes 433–640   : Cockpit data (_CK object hardcodé + streams Strava)
Lignes 641–840   : Checklists J-7 (CK_SECS, _ckRender, ckToggle...)
Lignes 841–930   : Fonctions générales (showTab, jumpToWeek, renderHeader...)
Lignes 931–1045  : Météo (renderMeteo, _meteoPaint...)
Lignes 1046–1300 : Coach + aides contextuelles (_dynamicACWR, computeFormeScore, _cReply...)
Lignes 1301–1415 : iOS install, version panel, forme help overlay
Lignes 1416–1600 : Cockpit rendering (renderCockpit, _pmcCompute, _ckBar, _ckLine...)
Lignes 1601–1800 : Palmarès (renderPalmares)
Lignes 1801–2000 : Plan (renderPlan, renderSeance, card de séance...)
Lignes 2001–2100 : Quick log (initQuickLog, soumettreQuickLog...)
Lignes 2101–2200 : Session overrides (openSM, confirmSMMove, confirmSMSkip...)
Lignes 2201–2244 : Démarrage (hydrateLogs, hydrateOverrides, init..., render...)
```

### Séquence de démarrage (ligne ~2230)
```javascript
hydrateLogs();          // Lit localStorage → enrichit SEANCES_BY_WEEK[wk][i].realise
hydrateOverrides();     // Lit session_overrides → déplace/skip les séances
initQuickLog();         // Injecte le bottom sheet de log dans le DOM
initCreneaux();         // Injecte le popup créneaux météo dans le DOM
initSessionMenu();      // Injecte le menu Déplacer/Skipper dans le DOM
initInstall();          // Injecte la bannière iOS install (si applicable)
initVersionPanel();     // Injecte le panel historique versions dans le DOM
initFormeHelp();        // Injecte l'overlay aide score de forme
initCkHelp();           // Injecte l'overlay aide Cockpit
initCoach();            // Injecte le FAB 🤖 + overlay Coach
renderHeader();         // Affiche : score forme + prochaine séance + météo + JR course
renderPlan();           // Affiche : toutes les semaines du plan
rwAuto();               // Déclenche le rewind auto si première ouverture de semaine
setTimeout(checkAutoSync, 800); // Détecte séances non loggées → nudge
```

### Fonctions critiques

#### `hydrateLogs()` — Ligne ~2201
```javascript
function hydrateLogs() {
  // Itère sur SEANCES_BY_WEEK
  // Pour chaque séance, cherche localStorage.getItem(`log_${wk}_${se.id}`)
  // Si trouvé, parse le JSON et l'injecte dans se.realise
  // Cela permet à renderPlan() d'afficher les séances comme "FAIT ✓"
}
```

#### `hydrateOverrides()` — Ligne ~2210
```javascript
function hydrateOverrides() {
  const ovs = JSON.parse(localStorage.getItem('session_overrides') || '{}');
  for (const [k, ov] of Object.entries(ovs)) {
    const [wk, id] = k.split('-', 2);
    const se = findSeance(wk, id);
    if (ov.action === 'move' && ov.newDate) se.date = ov.newDate;
    if (ov.action === 'skip') se.realise = { statut: 'skipped', reason: ov.reason };
  }
}
```

#### `_dynamicACWR()` — Calcul EMA (ligne ~1050)
```javascript
function _dynamicACWR() {
  // 1. Récupère la série RE hebdo depuis _CK.RE[12]
  // 2. Ajoute RE estimé de la semaine courante (depuis logs localStorage)
  //    Estimation : km × facteur selon catégorie (EF=7, AM=16, LONG=10, TRAIL=22)
  // 3. Calcule CTL/ATL via EMA :
  //    α_CTL = 1 - exp(-7/42)  ≈ 0.154  (42 jours)
  //    α_ATL = 1 - exp(-7/7)   ≈ 0.632  (7 jours)
  //    CTL[i] = (1-α_CTL) * CTL[i-1] + α_CTL * daily_RE
  //    ATL[i] = (1-α_ATL) * ATL[i-1] + α_ATL * daily_RE
  // 4. ACWR = ATL / CTL
  return acwr; // ex: 0.95
}
```

#### `computeFormeScore()` — Score composite (ligne ~1070)
```javascript
function computeFormeScore() {
  // ACWR (30%) — via _dynamicACWR(), EMA, dynamique
  // Adhérence (25%) — séances réalisées / planifiées, 2 dernières semaines
  // Z2 pace (25%) — tendance allure EF récent vs ancien
  // Fraîcheur (20%) — jours depuis dernière séance

  const score = Math.round(
    acwrScore * 0.30 +
    adherScore * 0.25 +
    z2Score   * 0.25 +
    freshScore * 0.20
  );

  return { score, trend, color, signal, components };
}
```

#### `_cReply(txt)` — Coach routing (ligne ~1110)
```javascript
function _cReply(txt) {
  // Routing par regex sur le texte utilisateur
  // Retourne une réponse contextualisée depuis les données de l'app
  const t = txt.toLowerCase();

  if (/cour[ui]|run/.test(t))    return handleRanToday();
  if (/fatigu|bless/.test(t))    return handleFatigue();
  if (/demain|prochain/.test(t)) return handleNextSession();
  if (/forme|score/.test(t))     return handleFormeDetail();
  if (/d[eé]raille|nice/.test(t)) return handleRace();
  if (/nutri|gel|électro/.test(t)) return handleNutrition();
  if (/m[eé]t[eé]o|chaud/.test(t)) return handleMeteo();
  if (/chaussure|shoe/.test(t))   return handleShoes();
  if (/allure|vitesse/.test(t))   return handlePace();
  if (/repos|r[eé]cup/.test(t))  return handleRecov();
  return defaultReply();
}
```

---

## 8. CSS — Design System

### Variables CSS (définies dans css.txt)
```css
:root {
  --texte:       /* Texte principal — noir en clair, blanc en nuit */
  --texte-deux:  /* Texte secondaire — gris moyen */
  --bg-card:     /* Fond des cartes — blanc en clair, bleu nuit en nuit */
  --bord-card:   /* Bordure des cartes */
  --gris-fond:   /* Fond gris très clair */
  --appbar-h:    /* Hauteur appbar calculée dynamiquement en JS */
}
```

### Mode nuit
Activé par la classe `.nuit` sur `<body>`. Chaque composant a ses variantes :
```css
body.nuit .mon-composant {
  background: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}
```

### Animations réutilisées
```css
@keyframes qlUp { /* Slide-up bottom sheets */
  from { transform: translateY(50px); opacity: 0; }
  to   { transform: none; opacity: 1; }
}

@keyframes qlFt { /* Fade-out toasts */
  0%   { opacity: 0; transform: translate(-50%, 8px); }
  12%  { opacity: 1; transform: translate(-50%, 0); }
  85%  { opacity: 1; }
  100% { opacity: 0; }
}
```

### Composants CSS principaux
| Classe | Composant | Fichier |
|--------|-----------|---------|
| `.seance-carte` | Carte de séance | css.txt |
| `.sc-fait` | Séance réalisée (fond vert) | css.txt |
| `.sc-skipped` | Séance passée (jaune rayé) | css_extra.txt |
| `.vdj` | Hero "Prochaine séance" | css.txt |
| `.vdj-adj` | Pastille ajustement allure T° | css_extra.txt |
| `.forme-bar` | Barre score de forme | css_extra.txt |
| `.forme-detail` | Détail 4 composantes | css_extra.txt |
| `.ck-card` | Carte Cockpit | css.txt |
| `.ck-help` | Bouton ? aide Cockpit | css_extra.txt |
| `.coach-fab` | FAB bouton 🤖 | css_extra.txt |
| `#coach-ov` | Overlay chat Coach | css_extra.txt |
| `.sm-btn` | Bouton ··· menu séance | css_extra.txt |
| `.as-bar` | Nudge auto-sync | css_extra.txt |
| `#canicule-banner` | Bannière canicule | css_extra.txt |
| `#install-banner` | Bannière iOS install | css_extra.txt |
| `#ver-ov` | Panel versionning | css_extra.txt |
| `#ck-help-ov` | Aide Cockpit plein écran | css_extra.txt |
| `#forme-help-ov` | Aide score forme plein écran | css_extra.txt |

### Palette de couleurs
```css
/* Sémantique */
#0d9488  /* teal — action principale, forme excellente, Z2 */
#22c55e  /* vert — fait, bonne forme */
#f59e0b  /* ambre — vigilance, ATL fatigue */
#ef4444  /* rouge — alerte, surcharge */
#8b5cf6  /* violet — SaintéLyon, séance seuil */
#3b82f6  /* bleu — allure marathon, AM */
#f97316  /* orange — sortie longue, volume */

/* Neutre */
#0f172a  /* fond principal nuit */
#1e293b  /* cartes nuit */
#334155  /* bordures nuit */
#64748b  /* texte secondaire */
#94a3b8  /* texte tertiaire */
```

---

## 9. Structure HTML — body.html

Minimaliste par design — 19 lignes. Tout le HTML dynamique est généré par JavaScript.

```html
<div id="appbar">
  <div id="cd-strip"><!-- Countdown courses injecté par renderHeader() --></div>
</div>

<div class="tabbar">
  <div class="tab actif" id="tab-plan"     onclick="showTab('plan')">Séances</div>
  <div class="tab"       id="tab-dash"     onclick="showTab('dash')">Suivi perf.</div>
  <div class="tab"       id="tab-cockpit"  onclick="showTab('cockpit')">Cockpit</div>
  <div class="tab"       id="tab-palmares" onclick="showTab('palmares')">Palmarès</div>
</div>

<div id="vue-plan">
  <div id="hero-plan"><!-- renderHeader() injecte ici --></div>
  <div id="plan-contenu"><!-- renderPlan() injecte ici --></div>
  <div id="maj-foot"><!-- Date MAJ + badge Build N --></div>
</div>

<div id="vue-dash"     style="display:none"><div id="dash-contenu"></div></div>
<div id="vue-cockpit"  style="display:none"><div id="cockpit-contenu"></div></div>
<div id="vue-palmares" style="display:none"><div id="palmares-contenu"></div></div>
```

---

## 10. Données — Statique vs Dynamique

### Décision d'architecture
Les données d'entraînement (plan, séances, dossiers) sont **délibérément statiques** — elles sont managées par Claude lors des sessions de travail. Ce n'est pas un bug, c'est un choix : la qualité du plan prime sur la fréquence de mise à jour automatique.

### Tableau complet

| Donnée | Statique / Dynamique | Source | Mise à jour |
|--------|---------------------|--------|-------------|
| Plan 30 semaines | 🔵 Statique | gen.py → SEMAINES | Rebuild manuel |
| Séances (131) | 🔵 Statique | gen.py → SBW | Rebuild manuel |
| Réalisé des séances | 🟢 Dynamique | localStorage | À chaque log |
| Overrides (déplace/skip) | 🟢 Dynamique | localStorage | À chaque action |
| Chaussures (km) | 🔵 Statique | gen.py → GEAR | Après chaque run |
| Courses (dates, dossiers) | 🔵 Statique | gen.py → RACES/DOSSIERS | Rebuild manuel |
| Palmarès | 🔵 Statique | gen.py → PALMARES | Après chaque course |
| Graphes Cockpit (_CK) | 🔵 Statique | app.js hardcodé | ⚠️ Sprint A.2 |
| ACWR Cockpit graph | 🔵 Statique | _CK.ACWR | ⚠️ Sprint A.2 |
| ACWR Score de forme | 🟢 Dynamique | _dynamicACWR() EMA | À chaque ouverture |
| Adhérence | 🟢 Dynamique | localStorage + SBW | À chaque log |
| Z2 pace trend | 🟢 Dynamique | realise.allure localStorage | À chaque log EF |
| Fraîcheur | 🟢 Dynamique | new Date() | À chaque ouverture |
| Météo | 🟢 Dynamique | Open-Meteo API | Toutes les 30min |
| Canicule auto | 🟢 Dynamique | meteo_cache.canicule_days | À chaque météo |
| Ajustement allure T° | 🟢 Dynamique | meteo_cache.temp | À chaque météo |
| Checklists | 🟢 Dynamique | localStorage ck_{race} | À chaque tap |
| Coach réponses | 🟢 Dynamique | Calcul JS depuis données | À chaque message |
| Score de forme | 🟢 Dynamique | computeFormeScore() | À chaque ouverture |
| PMC CTL/ATL/TSB | 🟡 Semi-dynamique | _CK.RE (historique) + logs (actuel) | Ouverture + log |
| Countdown courses | 🟢 Dynamique | new Date() vs RACES.date | À chaque ouverture |
| Rewinds | 🔵 Statique | gen.py → REWINDS | Rebuild manuel |

---

## 11. localStorage — Schéma complet

### Logs de séances
**Clé** : `log_{wkNum}_{seId}` (ex: `log_25_3`)
```json
{
  "statut": "fait",
  "km": 10.14,
  "temps": "53:10",
  "allure": "5:14/km",
  "fc_moy": 165,
  "fc_max": 181,
  "rpe_ressenti": 7,
  "nutrition": "TA Electrolytes, Nduranz Cherry",
  "commentaire": "",
  "pr": 0,
  "ach": 0,
  "revue": "<p>HTML du bilan coach...</p>"
}
```

### Overrides séances
**Clé** : `session_overrides`
```json
{
  "25-3": {
    "action": "skip",
    "reason": "Fatigue / récupération"
  },
  "26-1": {
    "action": "move",
    "newDate": "2026-06-23"
  }
}
```

### Checklists
**Clé** : `ck_{race}` (ex: `ck_deraille`, `ck_nice`, `ck_saintexpress`)
```json
{
  "dossard": true,
  "gilet": true,
  "cascadia": false,
  "tenue": false,
  "_o_equip": false,
  "_o_nutrition": true
}
```
Les clés `_o_{sectionId}` contrôlent si une section est ouverte (true) ou fermée (false).

### Cache météo
**Clé** : `meteo_cache`
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
  "hourly_today": [[7, 28.4], [8, 30.1]],
  "hourly_tomorrow": [[7, 29.0], [8, 31.5]]
}
```
TTL : 30 minutes (vérifié dans `renderMeteo()`)

### Autres clés
```
install_dismissed     → "1" si bannière iOS install fermée
as_{seId}            → "1" si nudge auto-sync dismissé pour cette séance
rw_seen              → JSON liste des IDs de rewinds vus
rw_mon               → "6" (mois du dernier rewind affiché)
```

---

## 12. Strava Integration

### Comment ça marche
Strava est intégré côté **Claude** via le Model Context Protocol (MCP), pas directement depuis l'app PWA (limitations OAuth en client public).

```
Loïc court → Strava enregistre l'activité → Claude appelle Strava MCP
→ Récupère données (km, FC, allure, streams) → Met à jour gen.py → Rebuild → Push
```

### Outils Strava disponibles (MCP)
```
Strava:list_activities(first, range_start) → Liste des activités récentes
Strava:get_activity_performance(activity_id) → Laps, métriques, FC
Strava:get_activity_streams(activity_id, resolution, streams)
  → Streams seconde par seconde : heart_rate, velocity_smooth, altitude, distance
Strava:get_gear(gear_types) → Km par paire de chaussures avec gear_id
Strava:get_athlete_profile() → Profil athlète
Strava:get_athlete_zones() → Zones FC/puissance
```

### Données streams Strava (dans _CK.STREAMS)
Les streams sont des arrays de 100 points (resolution="100") pour 4 activités :
```javascript
_CK.STREAMS = {
  '18967988695': {  // ID activité Strava
    hr:  [...100 valeurs FC],
    alt: [...100 valeurs altitude en m],
    v:   [...100 valeurs vitesse en m/s],
    km:  [...100 valeurs distance en km],
  },
  // 3 autres activités
}
```
Convertir vitesse en allure : `allure_s_per_km = 1000 / vitesse_m_per_s`

### Protocole après chaque séance
```
1. Appeler Strava:list_activities(first=2)
2. Identifier l'activité correspondante
3. Appeler Strava:get_activity_performance(id)
4. Extraire : km, temps, FC moy/max, allure moyenne
5. Appeler Strava:get_gear(gear_types=["Shoe"])
6. Mettre à jour GEAR.km dans gen.py
7. Créer/mettre à jour arr[i]["realise"] dans gen.py
8. Rebuild + push
```

---

## 13. API Météo — Open-Meteo

### Endpoint complet
```
GET https://api.open-meteo.com/v1/forecast
  ?latitude=45.7676
  &longitude=4.8344
  &current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,precipitation
  &hourly=temperature_2m,precipitation_probability
  &daily=temperature_2m_max
  &forecast_days=10
  &timezone=Europe%2FParis
```

**Gratuit, sans clé API, CORS OK depuis navigateur.**

### Logique métier
```javascript
// Canicule si >= 3 jours consécutifs > 28°C
let canicule_days = 0;
for (const tmax of j.daily.temperature_2m_max) {
  if (tmax > 28) canicule_days++;
  // Note : actuellement on compte tous les jours > 28°C, pas seulement consécutifs
}

// Ajustement allure selon T°
const T = Math.round(mc.temp);
const adj = T < 26 ? 10 : T < 30 ? 20 : T < 34 ? 30 : 40; // s/km

// Créneaux horaires : filtrage heures avec T° < 28°C
const good_slots = hourly_today.filter(([hour, temp]) => temp < 28);
```

---

## 14. Protocole de travail — RÈGLES

### Règle 1 — POC avant prod (SANS EXCEPTION)
```
Brief Loïc → Artifact POC → Validation Loïc → Code prod → node --check → Push
```
Même pour les "petites" features. Le POC prend 5 minutes, évite des push cassés.

### Règle 2 — Checklist avant push
```bash
cp /home/claude/Running/src/*.py src/*.js src/*.txt src/*.html /tmp/
cd /tmp
python3 gen.py          # → "OK"
python3 assemble.py     # → "Écrit: XXX caractères"
node --check app.js     # → silence (succès) ou STOP si erreur
node test.js            # → "Toutes les fonctions OK ✓"
cp /mnt/user-data/outputs/plan-entrainement.html /home/claude/Running/index.html
# → Push
```

### Règle 3 — CHANGELOG (OBLIGATOIRE)
Avant chaque push, ajouter dans `gen.py` :
```python
CHANGELOG = [
  {
    "build": N+1,                    # ← Build incrémenté
    "date": "JJ mois YYYY",
    "sha": "xxxxxxxx",               # SHA du commit (rempli après push)
    "tag": "Description courte",
    "items": [
      "feat: Description feature",
      "fix: Description correction — cause",
    ]
  },
  {"build": N, ...},  # Historique conservé
]
```

**Si oublié → le badge "Build XX" affiche l'ancien numéro.**

### Règle 4 — Fichiers à pousser
| Modification | Fichiers |
|-------------|---------|
| Séances / données | `src/gen.py` + `index.html` |
| Feature JS | `src/app.js` + `index.html` |
| Feature CSS | `src/css_extra.txt` + `index.html` |
| Nouveau champ exporté | `src/gen.py` + `src/assemble.py` + `index.html` |
| Docs uniquement | `docs/*.md` ou `CLAUDE.md` |
| Feature complète | Tous fichiers modifiés + `index.html` |

### Règle 5 — Chaussures (proactif)
Après chaque séance loggée, **sans attendre que Loïc le demande** :
```
Strava:get_gear → comparer avec GEAR actuel → si différence → mettre à jour gen.py → rebuild
```

### Règle 6 — Convention commits
```
feat(scope): description courte (build N)
fix: bug corrigé — cause et résolution (build N)
log S{wk}-{n}: description sortie km FC (build N)
docs: description
refactor: description
```

### Règle 7 — Token GitHub
```
Fine-grained PAT : portée entzmannloic-blip/Running Contents R/W
Expire : 10 septembre 2026
Renouveler : github.com/settings/tokens → Personal access tokens → Fine-grained tokens
```
Si compromis : révoquer immédiatement → nouveau token → mettre à jour `CLAUDE.md`.

### Règle 8 — Conflits SHA
```python
# TOUJOURS récupérer le SHA avant de modifier un fichier existant
st, meta = api('GET', f'https://api.github.com/repos/{REPO}/contents/{path}?ref=main')
sha = meta.get('sha') if st == 200 else None
body = {'message': MSG, 'content': b64_content, 'branch': 'main'}
if sha:
    body['sha'] = sha  # OBLIGATOIRE sinon 409 Conflict
api('PUT', url, body)
```

---

## 15. Deploy — GitHub Pages

### Configuration repo
```
Repo     : entzmannloic-blip/Running
Branche  : main
Source   : / (root) → index.html
URL      : https://entzmannloic-blip.github.io/Running/
```

### Script de push complet (Python)
```python
import os, json, base64, urllib.request, urllib.error

TOK = 'github_pat_XXXXX'  # Fine-grained PAT
REPO = 'entzmannloic-blip/Running'
MSG = 'feat: description courte (build N)'

def api(method, url, data=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode() if data else None,
        method=method
    )
    req.add_header('Authorization', 'Bearer ' + TOK)
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

# Pousser chaque fichier
for local, remote in [
    ('index.html',          'index.html'),
    ('src/gen.py',          'src/gen.py'),
    ('src/app.js',          'src/app.js'),
    ('src/css_extra.txt',   'src/css_extra.txt'),
    ('src/assemble.py',     'src/assemble.py'),
]:
    url = f'https://api.github.com/repos/{REPO}/contents/{remote}'
    # 1. Récupérer SHA actuel
    st, meta = api('GET', url + '?ref=main')
    sha = meta.get('sha') if st == 200 else None
    # 2. Préparer le contenu
    with open(local, 'rb') as f:
        content = base64.b64encode(f.read()).decode()
    # 3. Pousser
    body = {'message': MSG, 'content': content, 'branch': 'main'}
    if sha:
        body['sha'] = sha
    st2, res = api('PUT', url, body)
    commit_sha = res.get('commit', {}).get('sha', '')[:8]
    print(f'{remote} → {st2} {commit_sha}')
    # 4. Mettre à jour le SHA dans CHANGELOG
    # (après le premier push d'index.html, récupérer le SHA du commit)
```

---

## 16. Playbook de maintenance

### A. Logger une nouvelle séance

1. **Récupérer les données Strava**
```python
Strava:list_activities(first=2)  # Trouver l'activité
Strava:get_activity_performance(activity_id)  # Laps + métriques
```

2. **Mettre à jour gen.py**
```python
# Dans W(semaine, [...])
arr = WEEKS[semaine]
arr[index]["date"] = "2026-06-22"  # Date réelle si différente
arr[index]["realise"] = {
    "statut": "fait",
    "km": 11.2,
    "temps": "1:05:30",
    "allure": "5:51/km",
    "fc_moy": 141,
    "fc_max": 158,
    "rpe_ressenti": 4,
    "nutrition": "TA Electrolytes",
    "commentaire": "Sortie tranquille, bonnes sensations",
    "revue": "<p>Bilan coach HTML...</p>",
    "pr": 0,
    "ach": 0,
}
```

3. **Mettre à jour les km chaussures**
```python
Strava:get_gear(gear_types=["Shoe"])
# → Mettre à jour GEAR[i]["km"] dans gen.py
```

4. **Build + Push**
```bash
python3 gen.py && python3 assemble.py && node --check app.js
# → Push (voir §15)
```

### B. Ajouter un résultat de course au Palmarès

```python
PALMARES.insert(0, {  # Ajouter EN PREMIER
    "nom": "Marathon de Nice-Cannes",
    "alias": "Nice",
    "date": "2026-11-08",
    "lieu": "Nice → Cannes · France",
    "type": "marathon",
    "distance": 42.195,
    "dplus": 180,
    "dminus": 180,
    "temps": "3:42:15",         # Depuis le chip officiel
    "allure": "5:17",
    "classement_gen": 1234,     # Depuis les résultats officiels
    "classement_cat": 45,
    "total_finishers": 8500,
    "cat": "M0",
    "fc_moy": 158,              # Depuis Garmin/Strava
    "fc_max": 178,
    "cal": 3100,
    "chaussures": "Novablast 5 V",
    "meteo": "14°C · ensoleillé · vent faible",
    "statut": "termine",
    "strava_id": "XXXXXXXXXX",  # ID Strava de l'activité
    "accent": "#3b82f6",
    "bilan": "<p>Bilan coach détaillé en HTML...</p>",
})
```

### C. Ajouter un rewind hebdo

```python
REWINDS.insert(0, {  # EN PREMIER
    "id": "S26",
    "titre": "Ta semaine 26",
    "sous": "Allègement prépa Déraille · 22-28 juin",
    "slides": [
        {"bg": "linear-gradient(160deg,#0f172a,#1e3a5f)",
         "kicker": "REWIND · SEMAINE 26", "big": "🎬",
         "txt": "Semaine d'allègement avant la Déraille.<br>Tape pour avancer."},
        {"bg": "linear-gradient(160deg,#065f46,#022c22)",
         "kicker": "LE VOLUME", "big": "35 km",
         "txt": "Semaine légère par design. Les adaptations se font au repos."},
        # ... 10 slides total
        {"bg": "linear-gradient(160deg,#14532d,#052e16)",
         "kicker": "VERDICT DU COACH", "big": "A",
         "txt": "Prêt pour la Déraille. 💪"},
        {"bg": "linear-gradient(160deg,#b45309,#451a03)",
         "kicker": "LA SUITE", "big": "S27",
         "txt": "Race week ! Déraille le 5 juillet."},
    ]
})
```

### D. Mettre à jour les données Cockpit (_CK)

Les graphes Cockpit sont hardcodés dans `app.js` autour de la ligne 1415. Pour les mettre à jour :

```javascript
const _CK = {
  RE: {
    12: {
      w: [18, 19, 20, 21, 22, 23, 24, 25, 26], // ← Ajouter S26
      v: [380, 410, 450, 500, 420, 510, 696, 350, 248, 255, 210, 427, 220], // ← Ajouter RE S26
    },
    // Autres fenêtres : 2, 4, 8
  },
  ACWR: { ... },
  Z2: { ... },
  // ...
};
```

**Source des données** : Strava MCP via `Strava:list_activities` + calculs.

### E. Ajouter une nouvelle checklist de course

```javascript
// Dans app.js, objet CK_SECS
CK_SECS.nouvelle_course = [
  {
    id: 'equip',
    ico: '🎒',
    title: 'Équipement',
    items: [
      {id: 'dossard', label: 'Dossard récupéré', note: 'Note contextuelle'},
      // ...
    ]
  },
  // 5 sections : equip, nutrition, logistique, stratégie, recup
];
```

Et dans le DOSSIER correspondant (gen.py), s'assurer que le champ `"dossier": "id_course"` correspond.

---

## 17. Feature Registry — Toutes les features

### Onglet Séances
| Feature | Description | Fichier | Ligne approx |
|---------|-------------|---------|-------------|
| Plan semaines | Affichage de toutes les semaines S25-S53 | app.js | renderPlan() |
| Carte séance | Card avec type, métriques, tags, état | app.js | renderSeance() |
| Log self-service | Bouton ✓ → bottom sheet km/temps/RPE/nutrition | app.js | ouvrirQuickLog() |
| Journal nutrition | Chips TA/Gel/Cherry/Amarena dans log | app.js | qlNutr() |
| Déplacer séance | Bouton ··· → date picker → nouvelle date | app.js | openSMMove() |
| Skipper séance | Bouton ··· → 4 raisons → état jaune rayé | app.js | openSMSkip() |
| Auto-sync nudge | Détection séances non loggées au démarrage | app.js | checkAutoSync() |
| Fiche séance | Détail complet avec métriques, description | app.js | ouvrirSeance() |
| Dossier course | Dossier complet avec GPX, nutrition, plan | app.js | ouvrirDossier() |
| Checklist J-7 | Items interactifs avec progression | app.js | _ckRender() |
| Rewind hebdo | Slides animées bilan de semaine | app.js | renderRW() |

### Onglet Suivi perf.
| Feature | Description |
|---------|-------------|
| Boule de cristal | Projection marathon dynamique (Riegel + Z2) |
| Records personnels | PRs sur distances clés |
| Saison 2026 | KPIs globaux km/D+/sorties |
| Calendrier heatmap | Km par date toute l'année |
| Zones FC | Distribution par zone |

### Onglet Cockpit
| Feature | Description |
|---------|-------------|
| PMC CTL/ATL/TSB | Performance Management Chart |
| Volume hebdo | Km réel vs prévu avec tap-to-detail |
| Relative Effort | Charge Strava par semaine |
| ACWR | Risque blessure avec zones couleur |
| Dénivelé D+ | D+ hebdo |
| Z2 pace | Tendance allure EF |
| Découplage FC | Efficacité aérobie |
| Allures EF/AM/Seuil | 3 courbes superposées |
| Zones FC | Distribution dynamique |
| Cadence | SPM hebdo |
| Drill-down sortie | Modal avec streams seconde/seconde |
| Aides ? | Overlay explicatif pour chaque graphe |
| Toggle fenêtre | 2/4/8/12 semaines |

### Onglet Palmarès
| Feature | Description |
|---------|-------------|
| Timeline courses | 5 courses officielles triées par date |
| KPIs cumulés | Courses · km · D+ total |
| Bilan coach | Analyse HTML par course |
| Classements | Position / total finishers / catégorie |

### Hero (Onglet Séances)
| Feature | Description |
|---------|-------------|
| Score de forme | 0-100 dynamique avec 4 composantes |
| Aide ? score | Overlay explicatif plein écran |
| Prochaine séance | Titre + type + distance + allure ajustée |
| Ajustement allure T° | +10/20/30/40s/km selon météo |
| Bannière canicule | Auto si ≥3j >28°C prévus |
| Countdown courses | J-X pour les 3 courses de la saison |
| Widget météo | Conditions actuelles + créneaux + demain |
| Créneaux entraînement | Popup horaire si T°>28°C |

### Features globales
| Feature | Description |
|---------|-------------|
| Coach 🤖 | FAB + overlay chat avec 10 scénarios |
| iOS Install flow | Bannière + sheet 3 étapes pour PWA |
| Panel versionning | Build N + historique + SHA GitHub |
| Mode nuit | Toggle CSS sur body.nuit |
| Aides contextuelles | Overlay plein écran avec scrollTop=0 |

---

## 18. Audit — Bugs identifiés et corrigés

### Bug 1 — ACWR dict vs array (build 40)
**Symptôme** : Composante ACWR toujours ignorée dans le score de forme.
**Cause** : `ACWR_DATA` est un dictionnaire (`{"acwr": 1.57, ...}`), pas un array. La condition `ACWR_DATA.length` retourne `undefined` → falsy → bloc ignoré.
**Correction** : `_dynamicACWR()` utilisant EMA depuis `_CK.RE` + logs semaine courante.

### Bug 2 — Bouton ? Cockpit invisible (build 39)
**Symptôme** : Boutons d'aide non visibles dans le Cockpit.
**Cause** : CSS `color: rgba(255,255,255,.5)` — invisible sur fond blanc des cartes Cockpit.
**Correction** : Variables CSS `color: var(--texte-deux, #64748b)` — adapté clair et nuit.

### Bug 3 — Badge Build XX écrasé (build 38)
**Symptôme** : Badge "Build XX" absent du footer.
**Cause** : `initVersionPanel()` ajoutait le badge au DOM, puis `renderHeader()` appelé juste après écrasait `#maj-foot` avec `.innerHTML = _maj`.
**Correction** : Badge intégré directement dans la construction de `_maj` dans `renderHeader()`.

### Bug 4 — Palmarès vide (build 37)
**Symptôme** : Onglet Palmarès s'affiche vide.
**Cause** : `PALMARES` ajouté dans `gen.py` mais oublié dans la liste d'exports de `assemble.py`.
**Correction** : Ajout `("PALMARES", "PALMARES")` dans assemble.py.

### Bug 5 — Revue S25 non affichée (build 38)
**Symptôme** : Section "Revue du coach" affiche un placeholder dans la fiche semaine S25.
**Cause** : Le champ `revue` doit exister sur l'objet `SEMAINES[i]` — il n'était pas injecté.
**Correction** : `_S25_REVUE = "..."` puis `SEMAINES[25]["revue"] = _S25_REVUE` dans gen.py.

### Bug 6 — Fusion pmc/vol dans _CK_HELP (build 40)
**Symptôme** : SyntaxError `Missing initializer in const declaration` sur `re:`.
**Cause** : str_replace a fusionné la fermeture de `pmc:` avec l'ouverture de `vol:` — la clé `t:'Volume...'` était perdue.
**Correction** : str_replace ciblé pour restaurer la structure correcte.

---

## 19. Guide de réplication — Nouvel athlète

> Pour créer une instance identique de l'app pour un autre athlète (ex: Yannis).

### Étape 1 — Prérequis
- Compte GitHub
- Accès Claude avec Strava MCP connecté
- Fine-grained PAT GitHub sur le nouveau repo

### Étape 2 — Fork / nouveau repo
```bash
# Option A : Fork du repo existant
gh repo fork entzmannloic-blip/Running --clone --new-name "nouvel-athlete-Running"

# Option B : Nouveau repo from scratch
gh repo create "nouvel-athlete-Running" --public --clone
# Copier tous les fichiers src/ + CLAUDE.md + docs/
```

### Étape 3 — Adapter gen.py (athlète)

Modifier en haut de gen.py :
```python
# Profil athlète
FCmax = 190          # ← Adapter
POIDS = 72           # ← Adapter
NOM = "Prénom Nom"

# Zones FC (recalculer depuis FCmax)
Z2_MAX = int(FCmax * 0.75)  # Zone 2 max
SEUIL = int(FCmax * 0.87)   # Zone 4 min

# Coordonnées météo
METEO_LAT = 45.4347  # ← Adapter
METEO_LON = 4.39     # Saint-Étienne par exemple
```

### Étape 4 — Adapter le plan (WEEKS)

Supprimer toutes les lignes `W(n, [...])` et définir le nouveau plan :
```python
# Plan de la saison
W(1, [
    ef(10, 65, strides=True),     # EF + strides
    ef(8, 50),                     # EF
    mp(12, 75, 1, 5, "AM 5km"),   # Qualité
    longrun(16, 100),              # Sortie longue
])
W(2, [...])
# etc.
```

### Étape 5 — Adapter RACES et DOSSIERS

```python
RACES = [
    {"nom": "Semi-marathon de Lyon", "date": "2026-10-04", "dossier": "semi_lyon"},
    # ...
]

DOSSIERS = {
    "semi_lyon": {
        "titre": "Semi de Lyon",
        "date": "4 octobre 2026",
        "format": "21.1 km · Route · Départ 9h",
        "objectif": "A — 1h44",
        # ...
    }
}
```

### Étape 6 — Adapter GEAR

```python
GEAR = [
    {"marque": "ASICS", "modele": "Novablast 5", "km": 120},
    # ...
]
```

### Étape 7 — Adapter les checklists CK_SECS (app.js)

Les checklists sont dans `app.js` (`CK_SECS.{race_id}`). Adapter les items selon les besoins de l'athlète.

### Étape 8 — Adapter les zones FC (ZONES_FC)

```python
ZONES_FC = [
    {"z": "Z1", "nom": "Récupération", "bpm": f"< {int(FCmax*0.7)}", ...},
    {"z": "Z2", "nom": "Endurance", "bpm": f"{int(FCmax*0.7)}–{int(FCmax*0.8)}", ...},
    # etc.
]
```

### Étape 9 — Adapter le Coach (_cReply dans app.js)

Les réponses du Coach référencent des courses et protocoles spécifiques à Loïc. Adapter :
- Les noms de courses dans les regex
- Les protocoles nutritionnels
- Les allures cibles
- Le nom de l'athlète dans le message de bienvenue

### Étape 10 — Build + Deploy

```bash
# Dans CLAUDE.md, mettre à jour :
# - Nom athlète
# - Repo GitHub
# - Token

cp src/*.py src/*.js src/*.txt src/*.html /tmp/
cd /tmp && python3 gen.py && python3 assemble.py && node --check app.js
cp /mnt/user-data/outputs/plan-entrainement.html index.html
# Push vers GitHub
# Activer GitHub Pages sur le repo (Settings → Pages → Source: main branch)
```

### Checklist de réplication
- [ ] Repo GitHub créé et Pages activé
- [ ] gen.py : FCmax, poids, nom, coordonnées météo
- [ ] gen.py : Plan complet (semaines W(n, [...]))
- [ ] gen.py : RACES avec dates et IDs dossiers
- [ ] gen.py : DOSSIERS avec contenu complet
- [ ] gen.py : GEAR (chaussures)
- [ ] gen.py : PALMARES (courses terminées)
- [ ] gen.py : ZONES_FC (recalculées)
- [ ] gen.py : ACWR_DATA (valeurs initiales)
- [ ] app.js : CK_SECS (checklists par course)
- [ ] app.js : _CK (données Cockpit initiales)
- [ ] app.js : _cReply (Coach adapté)
- [ ] assemble.py : Tous les exports listés
- [ ] CLAUDE.md : Contexte athlète mis à jour
- [ ] Build validé (`node --check` → silence)
- [ ] Deploy testé (PWA accessible sur l'URL)

---

## 20. Roadmap technique

### Sprint A.2 — Auto-sync Strava (priorité haute)
**Problème** : Les graphes Cockpit (`_CK`) sont des snapshots statiques. Après log d'une séance, ils ne se mettent pas à jour.

**Solution envisagée** :
1. Cloudflare Worker comme proxy OAuth (Strava n'autorise pas PKCE public client)
2. Le Worker stocke les tokens Strava en KV
3. L'app PWA appelle le Worker pour récupérer les activités récentes
4. Les données `_CK` sont reconstruites côté client depuis ces activités

**Alternative simple (sans proxy)** :
- Déclencher le rebuild automatiquement via GitHub Actions après un hook Strava
- Strava envoie un webhook → GitHub Actions run → gen.py rebuild → push

### Sprint D — HRV & Readiness (octobre 2026)
Intégrer les données HRV du Garmin Fenix 6 Pro pour un score de récupération plus précis. Le Garmin expose ces données via Garmin Connect API (nécessite compte développeur) ou via export automatique.

### Sprint E — Pacing Strategy Nice (novembre 2026)
Générer un plan de course km par km pour Nice basé sur :
- CTL au moment du race
- Profil GPX du parcours (D+, segments clés)
- Météo prévue J-7
- Historique Semi de Paris (Riegel)
- Analyse du segment Antibes (km 25-28, +35m)

### Sprint F — Plan 2027 IA (décembre 2026)
Analyser l'intégralité de la saison 2026 (CTL/ATL, courses, nutrition, blessures) et générer une proposition de plan 2027.

### Limitation fondamentale — API key dans PWA
Le Coach in-app utilise actuellement des réponses pré-calculées (Option B) car appeler l'API Anthropic depuis une PWA publique nécessite une clé API visible dans le code. Solutions envisagées :
1. Cloudflare Worker proxy (stocke la clé côté serveur)
2. Clé dans localStorage (acceptable pour usage personnel)
3. Déploiement via Claude.ai Artifacts (la clé est gérée par Claude.ai)

---

## 21. Glossaire

| Terme | Définition |
|-------|------------|
| CTL | Chronic Training Load — charge chronique 42 jours (fitness) |
| ATL | Acute Training Load — charge aiguë 7 jours (fatigue) |
| TSB | Training Stress Balance — forme = CTL − ATL |
| ACWR | Acute:Chronic Workload Ratio = ATL/CTL (risque blessure) |
| EMA | Exponential Moving Average — moyenne mobile pondérée |
| RE | Relative Effort — score de charge Strava basé sur FC |
| Z2 | Zone 2 — endurance fondamentale, FC < 144 bpm pour Loïc |
| EF | Endurance Fondamentale — footing facile Z2 |
| AM | Allure Marathon — séance à allure cible marathon (5:20/km) |
| PMC | Performance Management Chart — graphe CTL/ATL/TSB |
| FC | Fréquence Cardiaque |
| FCmax | FC maximale (192 bpm pour Loïc) |
| SPM | Steps Per Minute — cadence de course |
| D+ | Dénivelé positif cumulé |
| PWA | Progressive Web App — app installable depuis navigateur |
| MCP | Model Context Protocol — protocole d'accès aux services externes par Claude |
| PAT | Personal Access Token — token d'authentification GitHub |
| SBW | SEANCES_BY_WEEK — dictionnaire séances par numéro de semaine |
| RPE | Rate of Perceived Exertion — effort perçu (1-10) |
| VDOT | Volume of oxygen — indicateur Daniels de condition physique |
| GCT | Ground Contact Time — temps de contact au sol (ms) |
| TSS | Training Stress Score — équivalent TrainingPeaks du RE |
| Heatmap | Carte de chaleur des sorties par jour de l'année |

---

*Documentation rédigée par Claude (Anthropic) · Build 40 · 21 juin 2026*
*App maintenue par : Loïc Entzmann (product owner) + Claude (développeur)*
*Repo : github.com/entzmannloic-blip/Running*
