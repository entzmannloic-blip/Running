---
name: Running — Plan d'entraînement
description: Blanc et orange, épuré, mobile d'abord, pour suivre une saison de course à pied.
colors:
  primary: "#F4561D"
  primary-deux: "#C2410C"
  primary-clair: "#FCCDB0"
  primary-fond: "#FFF1EA"
  primary-sombre: "#7C2D12"
  allure: ["#FCCDB0", "#F9A070", "#F4561D", "#C2410C", "#7C2D12"]
  zones: ["#FDE3D3", "#FBB089", "#F4561D", "#C2410C", "#7C2D12"]
  ok: "#16A34A"
  ok-deux: "#15703A"
  ok-fond: "#E8F6ED"
  warn: "#CA8A04"
  warn-deux: "#8F5A07"
  warn-fond: "#FDF5DB"
  danger: "#DC2626"
  danger-deux: "#B91C1C"
  danger-fond: "#FDECEC"
  ink: "#18181B"
  ink-2: "#52525B"
  ink-3: "#6B6B74"
  gris: "#A1A1AA"
  ligne-forte: "#D4D4D8"
  ligne: "#E7E7EA"
  paper: "#FFFFFF"
  page: "#F4F4F6"
typography:
  numbers:
    fontFamily: "'Barlow Semi Condensed' (embarquée, 700 et 800), repli police système"
    hero: "104px / 800 (chiffre héros du Rewind)"
    screen-title: "34px / 800"
    card-figure: "28px / 700, unité à 50 % en 600"
  text:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', Roboto, system-ui, sans-serif"
    card-title: "20px / 700"
    body: "16px / 400, interligne 1.45 à 1.55"
    label: "12px / 600, encre 3, au-dessus du chiffre"
rounded:
  sm: "8px"
  md: "12px"
  lg: "18px"
  button: "14px"
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
    rounded: "{rounded.lg}"
    padding: "18px"
    border: "aucune"
    shadow: "aucune"
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF (19px gras minimum)"
    rounded: "{rounded.button}"
    minHeight: "52px"
  button-secondary:
    backgroundColor: "{colors.paper}"
    border: "1.5px {colors.ligne} (intérieur)"
  chip:
    rounded: "{rounded.pill}"
    padding: "3px 10px"
    font: "12px / 650"
  nav-item-active:
    textColor: "{colors.primary-deux}"
    iconStroke: "{colors.primary}"
---

# Design System: Running — Plan d'entraînement

## Overview

**Direction : « Blanc et orange »** (lot 5, maquette validée par Loïc le 28 octobre 2026 : https://claude.ai/artifact/WLQsCd4zauvFak3ECCUaMZ).

Une app de sport épurée, dans l'esprit de Strava : beaucoup de blanc, un seul accent orange, des chiffres en gros dans une police étroite et sportive, des étiquettes en petit au-dessus. Les cartes sont blanches, sans ombre ni bordure, posées sur un fond gris très pâle ; la fiche de séance et le Rewind sont sur fond blanc. Aucun emoji dans l'interface : des icônes au trait (les textes du coach gardent les leurs).

Densité moyenne : la décision du jour se lit sans défiler, le détail est un toucher plus loin. Ce qui compte le plus après une séance, l'analyse du coach, est en tête de l'Accueil.

**Key Characteristics:**
- Un seul accent de marque (orange), des états à un sens chacun (vert réalisé, ocre vigilance, rouge danger).
- Cartes blanches de 18 px de rayon sur fond `#F4F4F6`, séparateurs d'un pixel, pas d'ombres.
- Chiffres en Barlow Semi Condensed, étiquette au-dessus en 12 px semi-gras.
- Mobile d'abord (390 px), barre d'onglets givrée en bas avec zone de sécurité iOS.
- Mouvement du build 268 inchangé, tout coupé sous « réduire les animations ».

## Colors

### Primary
- **Orange vif** (`--primary`, #F4561D) : aplats, gros chiffres, graphes, boutons, icône de l'onglet actif. Texte blanc dessus à 19 px gras minimum (3,4:1, grand texte).
- **Orange encre** (`--primary-deux`, #C2410C) : liens, petits textes orange, étiquette de l'onglet actif (5,2:1 sur blanc). C'est aussi le fond des boutons à petit texte blanc (`--primary-fill`).
- **Lavis** (`--primary-fond`, #FFF1EA) : fonds de puces, d'encarts et d'anneaux. **Orange clair** (`--primary-clair`, #FCCDB0) : bordures et fonds doux. **Orange sombre** (`--primary-sombre`, #7C2D12) : extrémité des rampes.
- **Rampe d'allure** (`--allure-1` à `--allure-5`, du plus lent au plus rapide) : #FCCDB0, #F9A070, #F4561D, #C2410C, #7C2D12.
- **Zones cardiaques** (`--z1` à `--z5`) : #FDE3D3, #FBB089, #F4561D, #C2410C, #7C2D12.

### États (un sens chacun, jamais décoratifs)
Chaque état a un aplat (graphes, points), une encre (texte) et un fond (puces).
- **Réalisé, dans la cible** : aplat `--ok` #16A34A, texte `--ok-deux` #15703A sur `--ok-fond` #E8F6ED (5,5:1).
- **Vigilance, hors cible** : aplat `--warn` #CA8A04, texte `--warn-deux` #8F5A07 sur `--warn-fond` #FDF5DB (5,3:1). L'ocre remplace l'ambre, trop proche de l'orange.
- **Danger** (charge en surcharge, forme basse) : aplat `--danger` #DC2626, texte `--danger-deux` #B91C1C sur `--danger-fond` #FDECEC.

### Neutres (zinc, sans bleu)
- **Encre** #18181B (`--texte`) : texte principal et chiffres. **Encre 2** #52525B (`--texte-deux`) : texte secondaire (7:1 sur le fond). **Encre 3** #6B6B74 (`--texte-trois`) : étiquettes (5,3:1 sur blanc, 4,8:1 sur le fond).
- **Fond** #F4F4F6 (`--bg-page`, `--gris-fond`) : Accueil, Séances, Cockpit, Courses. **Papier** #FFFFFF (`--bg-card`) : cartes, fiche, Rewind.
- **Ligne** #E7E7EA (`--gris-clair`) : séparateurs d'un pixel. **Ligne forte** #D4D4D8 (`--ligne-forte`) : axes, points de repos. **Gris** #A1A1AA (`--gris`) : éléments inactifs.

### Named Rules
**The One Voice Rule.** L'orange est le seul accent de marque. Une couleur d'état n'est jamais utilisée pour décorer, et chaque état garde un seul sens.
**The Ink Rule.** Le petit texte orange est en orange encre ; l'orange vif est réservé aux aplats, aux graphes et au grand texte.
**The Numbers First Rule.** La valeur se lit avant son étiquette : étiquette en petit au-dessus, gros chiffre dessous.

## Typography

**Chiffres :** Barlow Semi Condensed (`--f-num`), graisses 700 et 800, sous-ensemble latin embarqué dans `src/fonts/` (~46 Ko, licence OFL), déclaré dans `src/css.txt`, pré-chargé dans la page et pré-caché par le service worker : disponible hors ligne. `font-variant-numeric: tabular-nums`, interligne 1.
**Texte :** police système (`--f-texte`). Plus de serif Georgia.

### Hierarchy
- **Chiffre héros** (Barlow 800, 104 px) : distance du Rewind.
- **Titre d'écran** (Barlow 800, 34 px) : la date de l'Accueil.
- **Chiffres de carte** (Barlow 700, 22 à 34 px) : unité à la moitié de la taille, en 600, encre 2.
- **Titre de carte** (système 700, 20 px) ; **titre de séance** (système 700, 22 à 28 px).
- **Texte courant** (système 400, 15 à 16 px, interligne 1.5).
- **Étiquette** (système 600, 12 px, encre 3) : au-dessus du chiffre, en casse normale.
- **Surtitre** (système 700, 13 px, capitales espacées de 0,08 em, orange encre) : en tête des images du Rewind et des sections de la fiche.
- L'échelle `--t-display … --t-data` reste pour le code existant ; toute nouvelle taille passe par cette hiérarchie.

## Layout

Colonne unique, largeur maximale 480 px pour les vues redessinées (Accueil), 1000 px pour les autres ; marges de 12 px autour des cartes de l'Accueil, 20 à 24 px dans la fiche et le Rewind ; 12 px entre les cartes. Espacement sur une base de 4 px (`--sp-1` à `--sp-12`). Référence de conception : iPhone 390 px.

## Elevation & Depth

À plat : pas d'ombre sur les cartes, la séparation vient du blanc sur le fond gris. Les séparateurs font un pixel (`--gris-clair`). Seules les feuilles et la fiche gardent une ombre douce (`--ombre-lg`) parce qu'elles passent au-dessus de la page. La barre d'onglets est givrée (blanc à 92 %, flou 18 px, filet d'un pixel en haut).

### Mouvement
Inchangé depuis le build 268. Trois durées et une seule courbe : **120 ms** pour une pression (`--d-press`), **240 ms** pour un changement d'état (`--d-etat`), **360 ms** pour un changement d'écran (`--d-ecran`), décélération exponentielle (`--ease`, `cubic-bezier(.25,1,.5,1)`), jamais de rebond ni d'élasticité. Tout mouvement et toute animation infinie ont une alternative sous `prefers-reduced-motion` (CSS et `_reduceMotion()` en JS) ; chaque effet a un repli quand le navigateur ne le gère pas, et le contenu n'est jamais masqué en attendant une animation.

- **Onglets** (barre du bas, `goTab`) : transition de vue, fondu et glissement de 8 px dans le sens de la barre ; barre et en-tête immobiles. Sans l'API (iOS < 18) : la même chose en CSS (`.vue-in`). Les appels de code à `showTab` changent de vue sans transition de vue (seul le repli `.vue-in` joue).
- **Carte → fiche** (`ouvrirCarte`, `fermerAnime`) : la carte de séance ou de semaine s'agrandit jusqu'à devenir la fiche et s'y referme. `fermer()` reste synchrone pour le code.
- **Apparitions au scroll** : en CSS (`animation-timeline: view()`, Safari 26), sur `opacity` et `translate` pour ne pas gêner l'enfoncement au toucher. Sans support : cartes visibles d'emblée.
- **Barre d'onglets** : se rétracte quand on descend, revient quand on remonte, en haut et en bas de page et au focus ; les défilements commandés par l'app ne la cachent pas (`_bbHold`). Fixe sous réduire les animations.
- **Graphes** : courbes tracées et barres qui montent à la première apparition, une fois par graphe (`_trace`) ; le profil d'une course se dessine au fil du scroll.
- **Chiffres clés** (forme et sa jauge, ACWR, J-N) : ils comptent jusqu'à leur valeur à leur première apparition, une fois par session (`_compte`).
- **Célébrations** rares et sobres : une coche ou un trait qui se dessine, jamais de confettis.
- **Rewind de séance** : récit plein écran sur fond blanc, orange seul accent, ocre pour le dépassement de cible. Les tracés de données durent des multiples de 360 ms (1,4 à 3,2 s) ; le point du relief rejoue la sortie au rythme réel. Défilement automatique (environ 38 s), sauf l'analyse du coach qui attend « Continuer ». Sous réduire les animations : chaque image s'affiche finie et on avance au toucher.
- **Toucher** : retour visuel seul (léger enfoncement, 97 %). Pas d'haptique : l'iPhone ne vibre pas pour une web app.

### Named Rules
**The Flat Card Rule.** Une carte se distingue par son blanc sur le fond gris, jamais par une ombre ou une bordure.

## Shapes

Rayons : 8 px (petits éléments), 12 px (encarts), 14 px (boutons), 18 px (cartes), pastille complète (99 px) pour les puces. Jauges et anneaux circulaires (forme du jour, VO₂max), trait de 7 px, fond en lavis orange.

## Components

### Cards / Containers
- Blanc, rayon 18 px, padding 18 px, ni ombre ni bordure, sur le fond `#F4F4F6`.
- Titre de carte en système 20 px gras, ou étiquette 12 px quand la carte porte un chiffre.

### Buttons
- **Principal** : aplat orange vif, texte blanc 19 px gras, 52 px de haut, rayon 14 px.
- **Secondaire** : blanc, filet intérieur de 1,5 px `--gris-clair`, texte encre.
- Appui : léger enfoncement (97 %, 120 ms).

### Chips
Pastille 26 px de haut, 12 px semi-gras : réalisé (vert sur fond vert), vigilance (ocre sur fond ocre), marque (orange encre sur lavis), neutre (encre 2 sur fond gris). Une coche au trait peut précéder le texte.

### Navigation
Barre fixe en bas, givrée, quatre onglets de largeur égale (Accueil, Séances, Cockpit, Courses), icône au trait 24 px et étiquette 11 px semi-gras ; actif : icône orange vif et étiquette orange encre ; inactif : encre 3. 48 px de haut minimum, marge basse = zone de sécurité iOS.

### Icônes
Au trait (SVG, trait de 2 px, extrémités arrondies, `currentColor`), 18 à 24 px. Aucun emoji dans l'interface ; les textes du coach (revues, analyses) gardent les leurs.

### Jauge / anneau
Anneau SVG (trait de 7 px, fond en lavis, arc orange vif) avec la valeur centrée en Barlow 800 : forme du jour, VO₂max. L'arc seul s'anime.

## Do's and Don'ts

### Do:
- **Do** utiliser les jetons de `src/css.txt` (`--primary`, `--primary-deux`, `--ok`, `--warn`, `--danger`, neutres) pour toute couleur.
- **Do** écrire les chiffres en `var(--f-num)` et leurs étiquettes au-dessus, en 12 px.
- **Do** garder les libellés de compteurs sans ambiguïté : « sorties de la semaine », « sorties depuis S24 », « sorties de la saison ».
- **Do** respecter `prefers-reduced-motion`, garder des cibles tactiles d'au moins 44 px et des contrastes AA (`scripts/audit_a11y.py`).
- **Do** laisser la zone de sécurité iOS libre autour de la barre de navigation.

### Don't:
- **Don't** écrire du petit texte en orange vif : orange encre.
- **Don't** ajouter une couleur ad hoc hors jetons (`scripts/audit_tokens.py` refuse une hausse) ; les dégradés propres à chaque course (dossiers) restent la seule exception.
- **Don't** utiliser une couleur d'état pour décorer, ni l'ambre (remplacé par l'ocre).
- **Don't** mettre d'ombre ou de bordure sur une carte, ni d'emoji dans l'interface.
- **Don't** réintroduire de mode sombre (retiré au build 242) ni de serif.
- **Don't** afficher une valeur par défaut qui ressemble à une mesure (0, NaN, undefined) quand la donnée manque.
