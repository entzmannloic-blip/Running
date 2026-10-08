# Journal des décisions — refonte d'octobre 2026

Registre tenu pendant l'exécution du plan `docs/superpowers/plans/2026-10-08-refonte-running.md` : chaque écart au plan ou arbitrage est une ligne « Ruling » avec son coût si c'était une erreur. « Final-minor » = point mineur de la relecture finale laissé pour plus tard. « pending » = action à faire par Loïc. Texte brut du registre (sans accents).

```
# SDD ledger — plan: docs/superpowers/plans/2026-10-08-refonte-running.md
Pre-flight: tasks 3,5 share app.js/assemble.py (sequential, no conflict); task 1 captures depend on task 0 build.
Env: Python 3.12.10 at %LOCALAPPDATA%/Programs/Python/Python312, playwright 1.63 + chromium installed (user-approved).
Task 0: Ruling: scripts/ et src/ gardent des copies identiques de preflight.py et release.py (assemble.py aussi) — l ancien release.py pousse les copies src/ — consolidation reportee a la tache 8 — cout si faux: une copie peut deriver
Task 0: Ruling: CLAUDE.md pipeline mis a jour des la tache 0 (prevu tache 8) — les instructions de Claude doivent rester exactes des la fusion de la phase A — cout: aucun
Task 0: Ruling: L06 preflight attend 131 seances, le plan en contient 137 (avertissement, non bloquant) — laisse tel quel — cout: bruit dans la sortie
Task 0: complete (commit d06ed79, tests: build --check identique + preflight OK + test_regression 16/16 sous Windows)
Task 1: Ruling: le pied de page (numero de build) est masque dans les captures — sinon la reference accueil change a chaque build — cout: une modification du pied de page passe inapercue
Task 1: complete (commit f816f89, tests: capture_reference --check 4/4 identique x3, preflight OK, regression 16/16)
Task 2: Ruling: pas de sidecar .impeccable/design.json (utile seulement au panneau live) — YAGNI — cout: panneau live sans composants rendus
Task 2: Ruling: nord creatif = Le carnet de l entraineur, positionnement = les 3 propositions, utilisateur = Loic seul (reponses de Loic)
Task 2: complete (commit c0af423, tests: tokens DESIGN.md presents dans css.txt, build 227, preflight OK, regression 16/16, captures 4/4)
Phase A: merged (PR 1, squash 3ab634c), Pages built, live = build 227
Task 3: Ruling: carte morte _nudgeCard (jamais inseree) supprimee avec le coach — code mort — cout: aucun
Task 3: Ruling: CSS .coach-nudge laisse en place (selecteurs groupes lignes ~1010-1018, 1141, 1395) — inoffensif — cout: quelques octets de CSS morts (a nettoyer en tache 10)
Task 3: complete (commit 79ed570, tests: test_regression 20/20 dont T07/T08/T08b RED puis GREEN, preflight OK, captures reecrites: barre a 4 onglets)
Task 4: Ruling: la barre a 4 onglets etait deja obtenue par la tache 3 (flex:1) — la tache 4 ajoute etiquette, aria-current et tests T14 — cout: aucun
Task 4: pending (action Loic): verification sur iPhone de la barre du bas (zone de securite) apres deploiement
Task 4: complete (commit f4f4167, tests: test_regression 27/27 dont T14 RED puis GREEN, captures 4/4)
Phase B: merged (PR 2, squash), live build 229
Task 5: Ruling: SEANCES_BY_WEEK charge au demarrage (37 usages synchrones), pas a la demande — decision du plan — cout: pas de gain de poids sur ce fichier
Task 5: Ruling: site/ en staging (index.html, data/, src/app.js, statiques) servi en http local par paths.html_url() — fetch et service worker exigent http, pas file:// — cout: les scripts de test dependent du serveur local
Task 5: Ruling: audit_cockpit.py (casse par ma tache 0) corrige ici — cout: aucun
Task 5: Mesure: premier chargement 305 Ko gzip (avant 389 Ko, -22 Task 5: Ruling: SEANCES_BY_WEEK charge au demarrage (37 usages synchrones), pas a la demande — decision du plan — cout: pas de gain de poids sur ce fichier
Task 5: Mesure: premier chargement 305 Ko gzip (avant 389 Ko, -22 pour cent), coque 152 Ko ; objectif plan <150 Ko non atteint pour la coque
Task 5: Final-minor (deferred): src/test.js (test Node) echoue deja avant la refonte (window.addEventListener)
Task 5: complete (commit 22949bd, tests: regression 35/35 dont T15 RED puis GREEN, release.py phases 1-3 vertes, captures 4/4, build --check 6 fichiers)
Task 6: Ruling: pas de viewport-fit=cover ni de marge haute ajoutes a l aveugle — le comportement des zones de securite sur le vrai iPhone ne peut pas etre teste en emulation, et le changer pourrait decaler l en-tete — cout: marge haute eventuelle a ajouter apres retour d une capture iPhone
Task 6: Ruling: pas de test automatique du repli apres 3 s (reseau lent) — Playwright n intercepte pas les requetes du service worker — a valider sur iPhone en 4G degradee — cout: logique de timeout non verifiee en test
Task 6: pending (action Loic): iPhone — ouvrir en mode avion, puis en 4G degradee ; verifier la barre du bas (indicateur d accueil) et le haut de page (barre d etat)
Task 6: complete (commit d58fa17, tests: regression 41/41 dont T16 RED puis GREEN, release.py phases 1-3 vertes, captures 4/4)
Task 7: Ruling: gen.py dependait de la date du jour (ACWR) -> build non reproductible, --check aurait echoue chaque lendemain — date de build enregistree dans data/meta.json (BUILT_ON) et rejouee par --check — cout: BUILT_ON ajoute a window par le boot (inoffensif)
Task 7: Ruling: perimetre fusion automatique = data/, fit/, src/gen.py, src/hist.json, index.html, sw.js (sw.js et index.html sont generes et verifies par build --check) ; le plan disait de prevenir pour sw.js mais il change a chaque build — cout: aucun, le check prouve qu il est genere
Task 7: Ruling: captures de reference non rejouees en CI (pixels dependants des polices Linux) — a lancer en local pour les changements d interface — cout: regressions visuelles detectees seulement en local
Task 7: pending (action Loic): activer fusion automatique + exiger le controle verify sur main — necessite le oui explicite de Loic (reglage du depot)
Task 7: complete-local (commit 3216480, tests: test_build OK, test_ci_tools OK, validate_data OK, regression 41/41) ; CI a confirmer sur la PR
Phase C: merged (PR 3 squash), CI verify verte, live
Task 8: Ruling: les cles localStorage reelles sont runlog_v1, session_overrides, ck_*, meteo_cache... (CLAUDE.md et le plan citaient log_{wk}_{id}, perime) — documentation corrigee — cout: aucun
Task 8: Ruling: referentiel Strava des audits extrait dans src/strava_reference.json (chaque log de seance modifiait 2 scripts d audit, hors perimetre de fusion automatique) — cout: les audits dependent d un fichier de plus
Task 8: pending: essai a blanc (seance fictive sur branche jetable) a faire apres fusion de la phase D
Task 8: complete-local (commit 991aba5, tests: release.py phases 1-3 vertes, test_ci_tools OK, test_build OK, validate_data OK, build --check 7 fichiers)
Phase D: merged (PR 4 squash), verify verte
Task 9: Ruling: pas d axe-core (telechargement/dependance non autorises par Loic) — audit maison scripts/audit_a11y.py (9 regles) — cout: moins de couverture qu axe (pas de verification ARIA fine, ordre de focus, etc.)
Task 9: Ruling: elements onclick non natifs rendus accessibles par un amelioration progressive (MutationObserver) plutot que reecrire des centaines de gabarits en button — cout: role/tabindex ajoutes apres rendu (1 frame)
Task 9: Ruling: seuil texte courant = 13 px (phrases > 40 car.), etiquettes = 12 px minimum — cout: quelques chaines passent a 13 px
Task 9: Ruling: jetons modifies --texte-trois (#64748b -> #5b6b80) et --ok-deux (#15803d -> #166534) pour atteindre 4,5:1 sur les fonds #f2f2f7 et teintes — cout: gris et verts de texte legerement plus fonces partout
Task 9: complete (commit 06ee19e, tests: audit_a11y 0 violation (RED 385 -> GREEN 0), regression 41/41, release.py phases 1-3 vertes, captures mises a jour)
Task 10: Ruling: le compteur de reference est « sorties avec kilometrage » (celui de l accueil, deja documente dans le code) ; Courses l adopte — cout: les seances de PPG/mobilite ne comptent pas dans Ta saison en chiffres
Task 10: Ruling: #fff, #1e293b en fond, degrades, ombres, SVG des graphiques restent en dur (pas de jeton equivalent sans casser le mode nuit) — cout: 278 couleurs restantes, documentees comme exceptions
Task 10: Ruling: mode nuit existant (body.nuit, 142 regles, bouton retire de la page) non touche ici — traite en tache 11
Task 10: complete (commit 7565f90, tests: regression 47/47 dont T17 RED puis GREEN, audit_tokens 585 -> 278, a11y 0, release.py phases 1-3 vertes, captures mises a jour)
Task 11: Ruling: l ancien mode nuit (body.nuit, 169 regles, bouton retire) etait casse avec l interface actuelle — reconstruit par jetons de surface plutot que reactive tel quel — cout: les 169 anciennes regles restent (certaines peuvent etre mortes)
Task 11: Ruling: teintes de remplissage (teal, vert, ambre, rouge) inchangees en sombre ; seuls surfaces, textes et variantes -deux/-fond changent — respecte sans nouvelle couleur de marque — cout: teal de texte actif = primary-deux plus clair
Task 11: Ruling: status bar iOS (black-translucent) et viewport-fit non modifies sans test sur appareil — cout: lisibilite de la barre d etat a verifier par Loic sur iPhone en clair et en sombre
Task 11: pending (action Loic): iPhone — bascule automatique clair/sombre avec le reglage iOS, barre d etat lisible
Task 11: Final-minor (deferred): toggleTheme() et reglages nuit historiques inutilises (a nettoyer)
Task 11: complete (commit 08fa526, tests: regression 54/54 dont T18 RED puis GREEN, a11y clair+sombre 0, tokens non croissant, release.py phases 1-3 vertes, captures 8/8)
Task 12: Ruling: detecteur Impeccable : 161 constats dont 101 advisories de systeme de design ; corriges = easing a rebond (9). Laisses en l etat (identite assumee) : bandes laterales de cartes de course, point pulse de fraicheur (coupe en reduced-motion), reflet infini du bouton Wrapped (coupe en reduced-motion), degrade de texte, lueur bleue, accent violet des rewinds — cout: warnings du detecteur persistants
Task 12: Ruling: pas de lancement des sous-commandes polish/critique complets (deux sous-agents isoles + captures live) — audit chiffre par scripts du depot + detecteur ; critique heuristique complete non rejouee — cout: pas de score de Nielsen mis a jour
Task 12: complete (commit 2362f24, tests: release.py phases 1-3 vertes, a11y clair+sombre 0, tokens non croissant, test_build/test_ci_tools/validate_data OK, build --check 7 fichiers, captures 8/8)
Final: Ruling: la relecture independante (opus) conclut « avec corrections » ; aucun Critical ; 4 Important traites en une passe — cout si faux: n/a
Final: fixed dark-mode illisible (partiel, Terminer/Rejouer, alerte chaleur, tableaux, boutons) — audit_a11y etendu aux feuilles/fiches/composants RED (13 sombre, 5 clair) -> GREEN 0, suite 58/58
Final: fixed fusion auto contournable par renommage — test renommage RED (DATA_ONLY) -> GREEN (--no-renames), suite OK
Final: fixed build non incremente non detecte — test_ci_tools RED (script absent) -> GREEN (check_build_increment + etape verify)
Final: fixed Review Focus 4 sans test — T19 fin d annee (le code etait deja correct : test de couverture, vert d emblee), suite 58/58
Final: minor (deferred): cache d execution du SW : cles ?v= differentes du precache, ignoreSearch retourne le precache, entree meta.json?t= a chaque retour au premier plan
Final: minor (deferred): precache sans cache:reload (risque de melange de versions)
Final: minor (deferred): placeholders __BUILD__/__SHELL__ remplaces aussi dans le commentaire d en-tete de sw.js
Final: minor (deferred): gestionnaire clavier global sans test de defaultPrevented (double activation possible), amelioration onclick non appliquee aux attributs ajoutes plus tard
Final: minor (deferred): ecran de chargement retire meme si app.js plante a l initialisation
Final: minor (deferred): CI non epinglee (playwright, actions par tag majeur)
Final: Ruling: l ancien contraste du bouton du bandeau de version est corrige au passage (--primary-fill) alors que le relecteur le classait Minor — cout: aucun
Final: complete (commit e18dee6, tests: release.py phases 1-3 vertes, regression 58/58, a11y clair+sombre 0, tokens, test_ci_tools, test_build, validate_data, build --check, captures 8/8)
Post-refonte: Ruling: mode sombre retire entierement a la demande de Loic (il n apportait rien) — build 242 — cout si faux: reconstruire par jetons (voir historique git builds 236-238)
```
