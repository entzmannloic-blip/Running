# CLAUDE.md — Contexte Running PWA
> Ce fichier est lu en premier par Claude Code avant toute action sur ce repo.
> Documentation complète : docs/TECHNICAL.md (1657 lignes)

## Identité
**App** : Running PWA — coaching running personnel pour Loïc Entzmann
**Repo** : entzmannloic-blip/Running (GitHub Pages)
**Build actuel** : 40
**Token GitHub** : fine-grained PAT, expire 10 septembre 2026

## Athlète
- **Loïc Entzmann** · Lyon · M0 (30-34) · 84 kg
- FCmax 192 · Z2 max 144 bpm · Seuil marche ~160 bpm
- **Courses 2026** : Trail Déraille 5 juil (24km) · Marathon Nice 8 nov (objectif 3h45) · SaintExpress 28 nov (45km nuit)

## Règles absolues (voir docs/TECHNICAL.md §14 pour le détail)

1. **POC avant prod** — Toute feature = artifact POC → validation Loïc → code prod
2. **Checklist build** : `python3 gen.py && python3 assemble.py && node --check app.js`
   - `node --check` qui échoue = STOP, ne jamais push
3. **CHANGELOG obligatoire** — Incrémenter le build ET ajouter une entrée avant chaque push
4. **Fichiers** — Toujours pousser `src/` modifiés + `index.html` ensemble
5. **Chaussures** — `Strava:get_gear` après chaque log de séance → update gen.py → rebuild
6. **SHA** — Toujours GET le SHA avant PUT (sinon 409 Conflict)

## Pipeline build
```bash
cp /home/claude/Running/src/*.py *.js *.txt *.html /tmp/
cd /tmp && python3 gen.py && python3 assemble.py && node --check app.js
cp /mnt/user-data/outputs/plan-entrainement.html /home/claude/Running/index.html
```

## Fichiers clés
- `src/gen.py` (854 lignes) — données : plan, séances, chaussures, dossiers, palmarès
- `src/app.js` (2244 lignes) — toute la logique JS (184 fonctions)
- `src/css_extra.txt` (904 lignes) — CSS features
- `src/body.html` (19 lignes) — structure HTML minimaliste
- `src/assemble.py` (30 lignes) — pipeline + liste des exports JS

## Données clés gen.py
- Plan : S25→S53 (30 semaines, 131 séances)
- Courses : RACES[3] — Déraille, Nice, SaintExpress
- Chaussures : GEAR[5] — voir tableau ci-dessous
- Palmarès : PALMARES[5] — 5 courses officielles
- Builds : CHANGELOG[5] — 5 derniers builds

## Parc chaussures
| Modèle | Km | Convention |
|--------|----|-----------|
| HOKA Clifton 10 | 1103 | Décrassages seulement |
| ASICS Gel Pulse 16 | 225 | Footings faciles |
| Brooks Cascadia 19 | 196 | Trail |
| ASICS Novablast 5 J | 502 | Training route (jaune) |
| ASICS Novablast 5 V | 0 | Courses (vert, neuf) |
| ASICS Magic Speed 4 | 51 | AM/qualité |
| gear_id Strava | Clifton=28498174 · Pulse=28498182 · Cascadia=28498287 · NB J=28722452 · Magic=29204843 |

## Architecture JS clé
```
hydrateLogs() → hydrateOverrides() → initAll*() → renderHeader() → renderPlan() → checkAutoSync()
```

## localStorage
```
log_{wk}_{id}       → séances loggées (JSON)
session_overrides   → déplace/skips (JSON)
ck_{race}           → checklists (JSON)
meteo_cache         → météo Lyon (TTL 30min)
install_dismissed   → bannière iOS
```

## Strava MCP (Claude uniquement, pas depuis l'app)
```
Strava:list_activities(first=N)
Strava:get_activity_performance(activity_id)
Strava:get_activity_streams(activity_id, resolution, streams)
Strava:get_gear(gear_types=["Shoe"])
```

## Points de vigilance
- ⚠️ Graphes Cockpit (_CK) = snapshots statiques — ne se mettent pas à jour auto
- ⚠️ ACWR_DATA dans gen.py est obsolète — remplacé par _dynamicACWR() EMA dans app.js
- ⚠️ Token expire 10 sept. 2026
- ⚠️ Nouveau champ gen.py = aussi l'ajouter dans assemble.py

## Convention commits
```
feat(roadmap-X): description (build N)
fix: bug — cause (build N)
log S{wk}-{n}: km FC allure (build N)
docs: description
```
