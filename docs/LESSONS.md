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
