# Sources du plan d'entraînement

Le pipeline à jour est décrit dans **../CLAUDE.md** ; l'enrichissement après une séance dans **../docs/ENRICHISSEMENT.md**.

```bash
python src/build.py            # depuis la racine du dépôt : gen.py → assemble.py → node --check → index.html, sw.js, data/*.json
python src/build.py --check    # vérifie que les fichiers committés sont ceux du build
```

| Fichier | Rôle |
|---|---|
| `gen.py` | données (plan, séances, chaussures, palmarès, CHANGELOG) → `data.json` |
| `datamap.py` | répartition des données dans `data/*.json` |
| `assemble.py` | page `index.html` (CSS + script de démarrage) et `data/*.json` |
| `app.js` | logique de l'application |
| `css.txt`, `css_extra.txt`, `body.html` | styles et structure de la page |
| `sw.js` | modèle du service worker (le build le complète) |
| `build.py`, `paths.py` | build portable et chemins |
| `strava_reference.json` | référentiel Strava des audits |
| `preflight.py`, `release.py` | copies de `scripts/` (à garder identiques) |

Le dossier `build/` (ignoré par Git) contient le dossier de travail et le site construit (`build/site/`).
