---
name: Running — Plan d'entraînement
description: Le carnet de l'entraîneur, mobile d'abord, pour suivre une saison de course à pied.
colors:
  primary: "#0d9488"
  primary-deep: "#0f766e"
  primary-soft: "#99f6e4"
  primary-wash: "#f0fdfa"
  ok: "#16a34a"
  ok-deep: "#166534"
  ok-soft: "#bbf7d0"
  ok-wash: "#dcfce7"
  warn: "#f59e0b"
  warn-deep: "#b45309"
  warn-soft: "#fde68a"
  warn-wash: "#fef3c7"
  danger: "#ef4444"
  danger-deep: "#b91c1c"
  danger-soft: "#fecaca"
  danger-wash: "#fee2e2"
  slate: "#94a3b8"
  slate-line: "#e2e8f0"
  slate-wash: "#f8fafc"
  ink: "#1e293b"
  ink-2: "#475569"
  ink-3: "#5b6b80"
  paper: "#ffffff"
  page: "#f2f2f7"
typography:
  display:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "2rem"
    fontWeight: 800
    lineHeight: 1.12
  title:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "1.375rem"
    fontWeight: 700
  headline:
    fontFamily: "Georgia, 'Times New Roman', serif"
    fontSize: "1.0625rem"
    fontWeight: 700
    lineHeight: 1.22
  body:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  callout:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "0.875rem"
    fontWeight: 500
  caption:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 500
  data:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "0.75rem"
    fontWeight: 700
    letterSpacing: "0.1em"
rounded:
  sm: "8px"
  md: "12px"
  lg: "18px"
  pill: "99px"
spacing:
  sp-1: "4px"
  sp-2: "8px"
  sp-3: "12px"
  sp-4: "16px"
  sp-5: "20px"
  sp-6: "24px"
  sp-8: "32px"
  sp-10: "40px"
  sp-12: "48px"
components:
  card:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "16px"
  card-stat:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "18px 20px"
  chip-status:
    backgroundColor: "{colors.ok-soft}"
    textColor: "{colors.ok-deep}"
    rounded: "{rounded.pill}"
    padding: "4px 8px"
  nav-item:
    textColor: "{colors.ink-3}"
    padding: "4px 2px"
  nav-item-active:
    textColor: "{colors.primary}"
---

# Design System: Running — Plan d'entraînement

## Overview

**Creative North Star: "Le carnet de l'entraîneur"**

L'interface se lit comme le carnet d'un entraîneur : des cartes claires posées sur un fond slate très pâle, les chiffres d'abord, un seul teal d'accent. Les titres du plan sont en serif (Georgia) comme des titres de chapitre, tout le reste en police système pour la rapidité et la lisibilité sur iPhone. La densité est moyenne : on voit la décision du jour sans défiler, le détail est un tap plus loin.

La couleur travaille avec parcimonie : le teal est l'unique accent de marque ; vert, ambre et rouge sont réservés à l'état (réalisé, vigilance, danger) et ne servent jamais à décorer. Les dégradés propres à chaque course (dossiers) sont la seule exception assumée.

**Key Characteristics:**
- Un seul accent de marque (teal), états sémantiques à un sens chacun.
- Cartes blanches arrondies sur fond `slate-wash`, ombres douces et diffuses.
- Chiffres en gros et en gras, étiquettes en capitales espacées.
- Mobile d'abord (390 px), barre de navigation fixe en bas avec zone de sécurité iOS.
- Mouvement discret : fondu-montant des vues, appui qui rétrécit légèrement, tout sous `prefers-reduced-motion`.

## Colors

Palette retenue et sobre : un teal, trois états, un neutre slate.

### Primary
- **Teal course** (#0d9488) : seul accent de marque. Onglet actif, liens d'action, barre de progression, accents de titres. Variantes : profond (#0f766e), doux (#99f6e4), fond (#f0fdfa).

### Secondary (états)
- **Vert réalisé** (#16a34a) : séance faite, tendance positive, statut « courante ». Variantes `ok-deep`, `ok-soft`, `ok-wash`.
- **Ambre vigilance** (#f59e0b) : attention, séance à surveiller, compte à rebours de course (texte en `warn-deep`).
- **Rouge danger** (#ef4444) : charge aiguë élevée, forme basse, alerte. Variantes `danger-deep`, `danger-soft`, `danger-wash`.

### Neutral
- **Encre** (#1e293b) texte principal ; **Encre 2** (#475569) texte secondaire ; **Encre 3** (#5b6b80) légendes et étiquettes.
- **Papier** (#ffffff) surface des cartes ; **Ardoise pâle** (#f8fafc) fond de l'app ; **Ligne** (#e2e8f0) bordures et séparateurs ; **Ardoise** (#94a3b8) éléments inactifs.

### Named Rules
**The One Voice Rule.** Le teal est le seul accent de marque. Une couleur d'état n'est jamais utilisée pour décorer, et chaque état garde un seul sens.
**The Numbers First Rule.** La valeur se lit avant son étiquette : gros chiffre, petite étiquette en capitales.

## Typography

**Display Font:** police système (`system-ui, -apple-system, 'Segoe UI'`)
**Body Font:** police système
**Headline (plan) :** Georgia avec repli `Times New Roman`, serif

**Character:** un contraste simple entre le serif des chapitres du plan (titres de phases, thèmes de semaine) et la sans-serif système des chiffres et du texte courant.

### Hierarchy
- **Display** (800, 2rem, 1.12) : gros chiffres de tête de vue (« Cockpit », compteurs).
- **Title** (700, 1.375rem) : titres de vue et de section.
- **Headline** (700, 1.0625rem, serif) : thèmes de semaine et noms de phase.
- **Body** (400, 1rem, 1.55) : texte courant.
- **Callout / Caption** (500, 0.875rem / 0.8125rem) : descriptions secondaires.
- **Data** (700, 0.75rem, espacement 0.1em, capitales) : étiquettes de chiffres. Échelle documentée à 7 niveaux ; la barre de navigation utilise 10,5 px, hors échelle.

### Named Rules
**The Seven Levels Rule.** Pas de taille hors de l'échelle `--t-display … --t-data`. Toute nouvelle taille est une dette.

## Layout

Colonne unique centrée, largeur maximale 1000 px, marge latérale de 16 px, 90 px de réserve en bas pour la barre de navigation. Espacement sur une base de 4 px (`sp-1` à `sp-12`). Les grilles de semaines passent en `auto-fill` à partir de 168 px. Points de rupture à 430, 520, 560 et 640 px ; la référence de conception est 390 px.

## Elevation & Depth

Hybride : surfaces à plat avec une bordure fine `slate-line`, ombres douces et diffuses au survol et pour les cartes principales. La barre de navigation est givrée (fond blanc à 86 %, flou 18 px).

### Shadow Vocabulary
- **Ombre carte** (`0 1px 2px rgba(15,23,42,.06), 0 4px 12px -6px rgba(15,23,42,.10)`) : état de repos des cartes.
- **Ombre levée** (`0 2px 6px rgba(15,23,42,.07), 0 18px 36px -14px rgba(15,23,42,.22)`) : survol et éléments en avant.

### Mouvement
Décélération exponentielle (`cubic-bezier(.25,1,.5,1)`), jamais de rebond ni d'élasticité. Tout mouvement et toute animation infinie ont une alternative sous `prefers-reduced-motion`.

### Named Rules
**The Quiet Shadow Rule.** L'ombre est diffuse et basse en opacité ; jamais de bord noir ni d'ombre dure.

## Shapes

Formes arrondies : 8 px (petits éléments), 12 px (cartes de semaine), 18 px (cartes de statistiques et feuilles), pastille complète (99 px) pour les puces d'état. Les jauges et anneaux sont circulaires (forme du jour, VO₂max).

## Components

### Cards / Containers
- **Corner Style:** 12 px (carte de semaine) à 18 px (carte de statistiques).
- **Background:** papier blanc sur fond ardoise pâle.
- **Shadow Strategy:** ombre carte au repos, ombre levée au survol.
- **Border:** 1 px `slate-line`.
- **Internal Padding:** 16 px, 18 px × 20 px pour les cartes de statistiques.

### Chips
- **Style:** pastille (99 px), fond doux de la couleur d'état, texte en variante profonde, 0,58 rem en capitales.
- **State:** courante (vert), ouverte (teal), verrouillée (gris avec bordure).

### Navigation
- Barre fixe en bas, givrée, quatre onglets à largeur égale (le chat coach est retiré), icône 24 px et étiquette ; actif en teal, inactif en encre 3 ; appui qui rétrécit à 94 %. Marge basse = zone de sécurité iOS.

### Jauge / anneau (composant signature)
Anneau ou demi-cercle SVG avec la valeur centrée en gros : forme du jour (rouge sous un seuil), VO₂max. Chaque jauge affiche directement sa valeur ; l'arc seul s'anime.

## Do's and Don'ts

### Do:
- **Do** utiliser les tokens de `src/css.txt` (`--primary`, `--ok`, `--warn`, `--danger`, neutres) pour toute couleur.
- **Do** garder les libellés de compteurs sans ambiguïté : « sorties de la semaine », « sorties depuis S24 », « sorties de la saison ».
- **Do** respecter `prefers-reduced-motion` et garder des cibles tactiles d'au moins 44 px.
- **Do** laisser la zone de sécurité iOS libre autour de la barre de navigation.

### Don't:
- **Don't** ajouter une couleur ad hoc hors tokens (les dégradés par course sont la seule exception).
- **Don't** utiliser une couleur d'état pour décorer.
- **Don't** introduire une taille de texte hors de l'échelle à 7 niveaux.
- **Don't** écrire un fond blanc ou une couleur de texte en dur : utiliser `--bg-card`, `--bg-page` et les jetons de texte.
- **Don't** afficher une valeur par défaut qui ressemble à une mesure (0, NaN, undefined) quand la donnée manque.
