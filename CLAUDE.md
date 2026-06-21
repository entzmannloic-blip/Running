# CLAUDE.md — Contexte Running PWA

> Ce fichier donne le contexte à Claude Code pour travailler sur ce repo.
> Documentation technique complète : `docs/TECHNICAL.md`

## Athlète
**Loïc Entzmann** — Chef de projet Lyon, trail runner + marathonien.
- FCmax : 192 bpm · Seuil marche : ~160 bpm · Poids : 84 kg · Cat. M0
- Objectifs 2026 : Trail Déraille 5 juillet (24km) · Marathon de Nice 8 novembre (3h45) · SaintExpress 28 novembre (45km nuit)

## Architecture
Single-file PWA · GitHub Pages · `entzmannloic-blip/Running`

**Pipeline build :**
```bash
python3 src/gen.py       # données → /tmp/data.json
python3 src/assemble.py  # assemble → /mnt/user-data/outputs/plan-entrainement.html
node --check src/app.js  # validation JS
cp /mnt/user-data/outputs/plan-entrainement.html index.html
# Push GitHub via API Python (voir docs/TECHNICAL.md §9)
```

## Règles de travail
1. **POC avant prod** — toute nouvelle feature passe par un artifact de validation
2. **Valider avec `node --check app.js`** avant tout push
3. **Ajouter le build dans `CHANGELOG` de gen.py** à chaque push (Build N → Build N+1)
4. **Toujours pousser `src/` + `index.html`** en même temps
5. **Mettre à jour les km chaussures** après chaque séance loggée via `Strava:get_gear`

## Fichiers clés
- `src/gen.py` — plan d'entraînement, séances, chaussures, dossiers, palmarès
- `src/app.js` — toute la logique JS (~2200 lignes)
- `src/css_extra.txt` — CSS additionnel features (~900 lignes)
- `src/body.html` — structure HTML (4 onglets + overlays)
- `src/assemble.py` — pipeline d'assemblage + liste des exports JS

## Variables importantes
- Build actuel : **40**
- Token GitHub expire : **10 septembre 2026** (à renouveler)
- Strava MCP : connecté (`https://mcp.strava.com/mcp`)

## Parc chaussures (gen.py → GEAR)
| Modèle | Km | Usage |
|--------|----|-------|
| HOKA Clifton 10 | 1103 | Décrassages courts (<10km) |
| ASICS Gel Pulse 16 | 225 | Footings faciles |
| Brooks Cascadia 19 | 196 | Trail |
| ASICS Novablast 5 J (jaune) | 502 | Training route principal |
| ASICS Novablast 5 V (vert) | 0 | Neuf, pour courses |
| ASICS Magic Speed 4 | 51 | AM/qualité seulement |

## Statique vs Dynamique
- **Dynamique** : ACWR (`_dynamicACWR()` EMA), score de forme, météo, logs, checklists, overrides
- **Statique (rebuild)** : plan, dossiers, chaussures, palmarès, Cockpit graphs (`_CK`)
- **⚠️ Bug connu** : graphes Cockpit ne reflètent pas les nouvelles séances → Sprint A.2

## Derniers builds
- **Build 40** : Coach in-app + auto-sync nudge + PMC CTL/ATL/TSB + ACWR dynamique EMA
- **Build 39** : Score de forme + aides ? Cockpit
- **Build 38** : Checklists Nice/SaintExpress + journal nutrition + iOS install
- **Build 37** : Palmarès + Cockpit + Déplacer/skipper
