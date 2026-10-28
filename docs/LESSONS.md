# LESSONS.md — Journal des erreurs & garde-fous

> Ce fichier existe parce que Claude n'a pas de mémoire entre les sessions.
> Chaque erreur corrigée est consignée ici avec sa **cause racine** et son
> **garde-fou**, pour qu'elle ne se reproduise pas — par moi ou une autre session.
>
> **Règle d'or : avant tout push, lancer `python3 scripts/preflight.py` depuis /tmp.**
> Il encode mécaniquement les leçons L01→L08 ci-dessous. Un échec critique = ne pas pousser.
>
> Quand une nouvelle erreur survient : (1) la corriger, (2) l'ajouter ici, (3) si
> elle est mécanisable, ajouter un check dans preflight.py.

---

## Process de learning (à suivre à chaque correction)

1. **Reproduire** la cause exacte, pas juste le symptôme.
2. **Corriger** dans la source (`src/`), jamais dans l'output.
3. **Consigner** ici : symptôme → cause racine → garde-fou.
4. **Mécaniser** si possible : nouveau check dans `scripts/preflight.py`.
5. **Vérifier** que le preflight passe avant de pousser.

---

## L01 — Pipeline lancé depuis le mauvais répertoire → HTML périmé

**Symptôme.** Un build « poussé » contient en réalité l'ancien contenu (build 60/61
ont expédié du build 59). GitHub Pages peut même échouer au deploy sur un HTML incohérent.

**Cause racine.** `gen.py` écrit `/tmp/data.json` (chemin absolu), mais `assemble.py`
lit `data.json` depuis le **répertoire courant**. Si on lance `assemble.py` depuis
`/tmp/work`, il lit un `data.json` absent ou périmé → HTML stale.

**Garde-fou.**
- Toujours lancer `gen.py` **et** `assemble.py` depuis `/tmp` (pas un sous-dossier).
- `preflight.py` vérifie que `data.json` est postérieur à `gen.py`, et l'HTML postérieur à `data.json`.

---

## L02 — Numéro de build désynchronisé

**Symptôme.** Le badge « Build N » de l'app ne correspond pas au changelog qu'on croit avoir poussé.

**Cause racine.** Le badge vient de `gen.py → CHANGELOG[0].build`. Si on bumpe le
changelog mais qu'on ne régénère pas l'HTML (voir L01), l'HTML garde l'ancien numéro.

**Garde-fou.** `preflight.py` compare `CHANGELOG[0].build` de gen.py au `"build":N`
présent dans l'HTML de sortie. Mismatch = critique.

---

## L03 — str_replace casse la syntaxe JS

**Symptôme.** `app.js` ne se charge plus, page blanche.

**Cause racine.** Un `str_replace` sur du texte français (apostrophes, guillemets,
template literals imbriqués) introduit une erreur de syntaxe qui ne se voit pas à l'œil.

**Garde-fou.**
- `node --check app.js` après **chaque** édition de app.js.
- `preflight.py` relance `node --check` avant push.
- Préférer la concaténation ASCII + `\uXXXX` aux template literals pour le texte FR complexe.

---

## L04 — Emoji en surrogate-pair échappée casse le JS

**Symptôme.** Une fonction JS retourne `''` ou lève une exception silencieuse ;
`node --check` passe pourtant.

**Cause racine.** Un emoji écrit `'\ud83d\udccd'` (paire de substitution échappée)
depuis une source Python peut se retrouver mal encodé dans app.js.

**Garde-fou.**
- Dans le source Python : utiliser `\U0001F4CD` (codepoint unique, U majuscule) ou le caractère littéral.
- Dans app.js : utiliser `\u{1F4CD}` (accolades) ou le littéral.
- `preflight.py` interdit toute paire `\uD8xx\uDCxx` échappée en dur dans app.js.

---

## L05 — Mauvaise affectation date → semaine ISO

**Symptôme.** Une sortie du lundi 29 juin est rangée en S26 alors qu'elle est en S27
(erreur répétée plusieurs fois).

**Cause racine.** Supposer « dimanche = fin de semaine » sans vérifier le jour ISO réel.
Ancre fiable : **9 mars 2026 = lundi = S11**. Le lundi ouvre la semaine.

**Garde-fou.**
- Toujours calculer le jour ISO d'une date avant de l'affecter à une semaine.
- `preflight.py` recalcule, pour chaque `realise.date`, la semaine attendue
  (via le lundi de la date, ancré sur 9 mars 2026 = S11) et signale tout décalage.

---

## L06 — Intégrité des données

**Garde-fou.** `preflight.py` vérifie que `data.json` parse et que les compteurs
attendus tiennent (**30 semaines / 131 séances** — la sortie normale de gen.py).
Un écart = avertissement à investiguer.

---

## L07 — Token GitHub en clair

**Symptôme.** Un PAT se retrouve committé dans une source.

**Garde-fou.**
- Le PAT ne vit que dans une variable d'environnement de session, jamais dans un fichier poussé.
- `preflight.py` refuse tout `github_pat_…` présent dans gen.py ou app.js.
- Rappeler à l'utilisateur de **révoquer le PAT** en fin de session.

---

## L08 — HTML de sortie corrompu / tronqué

**Garde-fou.** `preflight.py` vérifie : taille ≥ ~400 ko, fin en `</html>`, aucun null byte.

---

## L09 — Compteur J- de l'accueil : date lue en UTC et course passée à J-0

**Symptôme (build 222).** L'audit visuel V2 signale « Marathon de Nice » à J-32 ou J-33 selon la vue,
et la tuile « Prochaine course » affiche « J-0 Run In Lyon » trois jours après la course.

**Cause racine.** La tuile de l'accueil calculait `Math.ceil(new Date(r.date) - minuitLocal)` : `new Date('YYYY-MM-DD')`
est lu en **UTC**, donc décalé d'un jour en France, et `Math.max(0, …)` ramenait toute course passée à J-0.
Le bug était masqué tant que le container du gate tournait en UTC, il est apparu quand il a tourné en CEST.

**Garde-fou.** Tous les compteurs passent par `_joursAvant()` et ne gardent que `dn >= 0`. L'audit visuel V2 reste le détecteur.
Ne jamais soustraire `new Date('YYYY-MM-DD')` à une date locale. Une course dont la date est passée ne doit pas être « prochaine ».

---

## L10 — Séance « non réalisée » : flèche ambre illisible (contraste 1,93:1)

- **Symptôme** : le job `verify` échoue à l'étape Accessibilité (`C1`, `div.seance-fleche`, ambre sur fond ambre clair) dès qu'une séance de la semaine affichée est marquée `skipped`.
- **Cause racine** : le tiret « — » de la carte d'une séance sautée utilisait `var(--warn)` (#f59e0b) sur `--warn-fond`. Défaut latent, invisible tant qu'aucune séance sautée ne figurait dans la semaine auditée.
- **Garde-fou** : `var(--warn-deux)` (#b45309, ~4,9:1) pour tout texte sur fond ambre ; `python scripts/audit_a11y.py` en local avant la PR quand on marque une séance `skipped`. Le job `verify` ne donne pas ses logs : rejouer l'audit en local.

## L11 — Cockpit : un graphe figé sous de fausses étiquettes, une allure « facile » polluée (audit du 15/10)

- **Symptôme.** Le graphe « Allure par type » (EF / AM / Seuil) affichait les données de S15-S26 sous les étiquettes
  S31-S42 : `_ckRebuild` prenait la *fin* d'un tableau figé au lieu de recalculer. Et l'« allure Z2 » de S42 valait 5:14
  parce que deux séances étiquetées « EF aérobie » (12 et 13/10) avaient été courues à allure marathon, FC 161.
- **Cause.** Un instantané statique mélangé à des séries vivantes sans que rien ne compare les deux ; et le *type* de la
  séance (étiquette du plan) pris pour son *intensité réelle*.
- **Règle.** Une séance n'est « facile » que si sa FC moyenne est ≤ 154 (haut de Z2 dans `ZONES_FC`). Toute série du
  Cockpit se recalcule depuis `SEANCES_BY_WEEK` ; aucun tableau figé n'est recollé à des étiquettes de semaine.
- **Garde-fou mécanisé.** `debugCockpit()` (console) recalcule à part chaque série et liste les données périmées
  (séances « à faire » passées, découplage ancien, RPE ou FC manquants). Le test `T20` de `test_regression.py` échoue au
  moindre écart. À lancer aussi à la main après un log : `debugCockpit()` dans la console du navigateur (ordinateur).
- **Reste connu.** Le découplage cardiaque n'est plus calculé depuis le 06/08 (procédure `src/decouplage.py`, streams Strava).

## L12 — Tuile ACWR : une semaine de retard sur le résumé (27/10)

- **Symptôme.** La tuile ACWR du Cockpit affichait 0,67 alors que le résumé et la carte Charge affichaient 0,74 ;
  `T20` a échoué le 27/10, deux jours après le build 259.
- **Cause.** La tuile lisait la dernière valeur de la série hebdomadaire (S43 terminée), le reste calculait l'ACWR
  du jour. Les deux valeurs coïncident le jour du build, puis divergent.
- **Règle.** Un indicateur affiché à plusieurs endroits vient d'une seule fonction (`_acwrCompute()` pour l'ACWR du
  jour) ; une série hebdomadaire ne sert qu'à son graphe.
- **Garde-fou mécanisé.** Déjà en place : `debugCockpit()` et `T20` comparent la tuile à l'ACWR du jour. Ils ne
  pouvaient pas le voir le jour du build, où les deux valeurs étaient égales.

## L13 — CI rouge le lendemain d'un build : T15 et l'ACWR du jour (29/10)

- **Symptôme.** `verify` a échoué sur les PR #19 et #20 du lot 5 (builds faites après minuit, CI à 23 h UTC la
  veille) : « T15 données JSON identiques à data.json — différentes : ACWR_DATA ». Rejoué en local, T15 échouait aussi
  sur un build de la veille ouvert le lendemain.
- **Cause.** L'app recalcule en direct `ACWR_DATA.acwr`, `charge7j` et `charge28j` à la date du téléphone
  (`_acwrCompute()`, leçon L12) ; T15 les comparait aux valeurs figées du build. Égales le jour du build seulement :
  toute CI rejouée un autre jour (PR fusionnée le lendemain, fuseau UTC de GitHub autour de minuit) passait au rouge.
- **Règle.** Un test qui compare les données publiées aux données du build exclut ce que l'app recalcule en direct.
- **Garde-fou mécanisé.** T15 ignore ces trois champs ; les échecs de régression sortent en annotations GitHub
  (`::error`), lisibles par l'API quand les journaux de la CI ne le sont pas.

## Quirks Strava MCP (non mécanisables, à connaître)

- Les activités **privées** n'apparaissent pas dans `list_activities`, quelle que soit
  la plage. Après passage en public, attendre **2-5 min** que Strava propage.
- `get_gear` renvoie souvent « No approval received » → incrémenter les km stockés
  manuellement depuis le dernier compteur connu.
- `get_activity_performance` = source des splits FC/allure/pente pour les revues coach.
- Le **RE (Relative Effort)** est parsé du commentaire de séance (« RE 106 »). Bien
  l'inscrire au log pour que les KPI dynamiques (`_ckRebuild`) restent précis.

## Récupération après reset du container

Les fichiers de travail `/tmp` sont volatils. Pour repartir :
1. Récupérer `src/*` via l'API Contents GitHub (décoder le base64) dans `/tmp/work/`.
2. Copier `*.py *.txt *.js *.html *.json` vers `/tmp/` (les scripts lisent `/tmp`).
3. Rebuild depuis `/tmp`, lancer `preflight.py`, puis pousser.

## Déploiement GitHub Pages

- `raw.githubusercontent.com` a un cache agressif → vérifier via l'**API GitHub**
  (`/pages/builds/latest`, `/actions/runs`), pas via l'URL raw.
- Un deploy qui échoue se corrige souvent en **régénérant proprement** l'HTML
  (voir L01) puis en repoussant — pas en re-run (le PAT fine-grained n'a pas Actions).

## Retour arrière (refonte d'octobre 2026)

- Le tag Git `pre-refonte` marque la dernière version avant la refonte (build 224).
- Annuler une phase fusionnée : `git revert -m 1 <commit de fusion>` puis build + contrôles.
- Revenir à l'état d'avant la refonte (lecture seule) : `git checkout pre-refonte`.
- Les captures de référence des 4 vues sont dans `tests/reference/` ; `python scripts/capture_reference.py --check`
  signale tout changement visuel (à relancer après `python src/build.py`). Un changement voulu se valide en
  réécrivant les captures (`python scripts/capture_reference.py`) dans le même commit.
