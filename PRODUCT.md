# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Loïc Entzmann, coureur amateur (Lyon, 30-34 ans, 84 kg, FC max 192), seul utilisateur. Il consulte l'app sur son iPhone, installée sur l'écran d'accueil via Safari (pas d'App Store) : avant une sortie pour voir la séance du jour, après pour suivre sa charge, sa forme et ses courses. Aucun autre utilisateur n'est prévu.

## Product Purpose
Suivre une saison de course à pied du début à la fin : le plan semaine par semaine (S24 à S53), les séances réalisées, la charge d'entraînement, la forme du jour et les objectifs (Marathon de Nice le 8 novembre 2026 en 3h45, SaintExpress le 28 novembre). Réussir, c'est savoir en quelques secondes ce qu'il faut faire aujourd'hui, et comprendre si la charge est tenable.

## Positioning
Un plan écrit sur mesure avec Claude à partir des sorties réelles (pas un plan générique), un cockpit de charge et de forme (ACWR, forme du jour, VO₂max, polarisation) pour décider avant de partir, et un journal de saison (Rewinds, palmarès, records, dossiers de course) qui garde la mémoire. Aucune app de plan du commerce ne combine ces trois choses à partir de ses propres données Strava.

## Operating Context
Après chaque séance, Loïc l'envoie à Claude (projet Claude relié à Strava via MCP). Claude relit l'activité, enrichit les données de l'app (réalisé, revue, chaussures) puis ouvre une pull request sur le dépôt GitHub `entzmannloic-blip/Running`. L'app est publiée en statique sur GitHub Pages. Les données sont aujourd'hui générées par `src/gen.py` puis assemblées dans `index.html` ; l'app ne lit pas Strava en direct.

## Capabilities and Constraints
- Quatre vues : Accueil (séance du jour, forme, météo, progression, capital), Séances (plan par phase et par semaine), Cockpit (aujourd'hui, progression, analyse), Courses (à venir et passées, dossiers).
- Le chat « coach IA » intégré a été retiré (décision de Loïc, octobre 2026) : le coaching se fait dans Claude. Les conseils calculés localement restent.
- Hébergement statique uniquement (GitHub Pages), PWA iOS ; données personnelles locales en `localStorage`.
- Terminologie : séance, sortie, semaine du plan (S24…S53), ACWR (rapport charge aiguë/chronique), forme du jour (0-100), polarisation, J-X avant course.
- Décision ouverte : vocabulaire exact des compteurs de sorties (semaine, depuis S24, saison), à fixer dans DESIGN.md.

## Brand Commitments
Une seule couleur primaire (teal `#0d9488`), des états sémantiques (ok, avertissement, danger) à un sens chacun, une échelle typographique à 7 niveaux. Les dégradés propres à chaque course (dossiers) sont préservés volontairement.

## Evidence on Hand
Données réelles de Loïc dans `src/gen.py` et `src/hist.json` (plan, séances réalisées, records, palmarès, chaussures) et fichiers `fit/` des séances planifiées. Il n'existe ni témoignage, ni autre utilisateur : ne rien inventer de tel.

## Product Principles
- La décision du jour d'abord : séance, forme et alerte de charge se lisent avant tout le reste.
- Chaque chiffre a un seul sens et un libellé sans ambiguïté (sortie de la semaine, depuis S24, de la saison).
- Les données sont vraies ou absentes : jamais de valeur par défaut qui ressemble à une mesure.
- Un enrichissement de séance doit rester petit, relisable et vérifié automatiquement.
- L'app doit servir dehors, sur iPhone, avec un réseau médiocre.

## Accessibility & Inclusion
Standard visé : WCAG AA (contrastes 4,5:1, cibles tactiles de 44 px, zoom autorisé, `prefers-reduced-motion` respecté). Usage en extérieur, parfois en plein soleil ou à l'aube : lisibilité des chiffres et contrastes prioritaires.
