#!/usr/bin/env python3
"""
================================================================================
 REGISTRE DES KPI DU COCKPIT — garantie structurelle anti-oubli
================================================================================

CE QUI S'EST REELLEMENT PASSE (a lire avant de modifier quoi que ce soit)
------------------------------------------------------------------------
Au build 118, un audit avait identifie que plusieurs series du Cockpit etaient
figees depuis mi-juin. La liste etablie a l'epoque comprenait bien :

    VOL, RE, ACWR, DPLUS, PACE, CAD, RUNS, STREAMS, Z2, DC, FCZ

Sept d'entre elles ont ete corrigees. Z2, DC et FCZ ne l'ont PAS ete, et le
compte rendu a presente le travail comme termine. Ce n'est donc pas un oubli
de diagnostic : le probleme etait identifie, et la correction partielle a ete
livree comme complete.

Douze builds plus tard, Loic a re-signale que le Cockpit n'etait pas a jour.

CAUSE RACINE
------------
Rien dans la chaine ne verifiait la COMPLETUDE de la correction. Un humain
decidait ce qui etait "fini". Ce fichier supprime cette decision humaine.

PRINCIPE
--------
Toute serie presente dans l'objet _CK doit etre declaree ici, avec un statut :

  LIVE    : recalculee a chaque chargement par _ckRebuild()
            -> le controle verifie qu'elle est effectivement ecrite dans le code
  STATIC  : figee volontairement (donnee historique immuable)
            -> le controle exige une justification ecrite
  DERIVED : construite a partir d'une autre serie deja verifiee

Si une serie apparait dans _CK sans etre declaree ici, le controle ECHOUE.
Si une serie declaree LIVE n'est pas ecrite par _ckRebuild, le controle ECHOUE.

Consequence : ajouter un indicateur au Cockpit sans l'inscrire au registre
casse la chaine de livraison. On ne peut plus en oublier un.
================================================================================
"""

import re, sys, json

APP = '/tmp/app.js'

# ------------------------------------------------------------------ registre
# cle : (statut, description, justification si STATIC)
REGISTRE = {
    'VOL':        ('LIVE',    'Volume hebdomadaire en km', None),
    'RE':         ('LIVE',    'Effort relatif hebdomadaire', None),
    'ACWR':       ('LIVE',    'Ratio charge aigue / chronique', None),
    'DPLUS':      ('LIVE',    'Denivele positif hebdomadaire', None),
    'PACE':       ('LIVE',    'Allure moyenne hebdomadaire (v)', None),
    'CAD':        ('LIVE',    'Cadence moyenne hebdomadaire', None),
    'Z2':         ('LIVE',    'Allure mediane des seances faciles', None),
    'DC':         ('LIVE',    'Derive cardiaque hebdo (reprend le KPI decouplage valide)', None),
    'FCZ':        ('LIVE',    'Repartition par intensite, bornes ZONES_FC officielles', None),
    'RUNS':       ('LIVE',    'Liste Analyse par sortie', None),

    'STREAMS':    ('STATIC',  'Donnees seconde par seconde en cache',
                   "Volumineuses, non regenerables sans appel Strava. Seules "
                   "quelques anciennes sorties en disposent ; l'absence est "
                   "geree proprement a l'affichage (message explicite)."),
    '_PACE_ORIG': ('DERIVED', 'Sauvegarde des sous-series ef/am/se de PACE',
                   None),
    '_ORIG':      ('DERIVED', 'Sauvegarde des series d origine pour la fusion '
                              'avec l historique pre-plan', None),
}

# Indicateurs hors _CK, rendus par une fonction dediee : la fonction doit exister
FONCTIONS_KPI = {
    '_effRender':    'Carte Efficience aerobie',
    '_heatRender':   'Carte Acclimatation chaleur',
    '_saisonRender': 'Carte Progression par saison',
    '_decoupRender': 'Carte Decouplage cardiaque',
    '_decoupBloc':   'Bloc decouplage dans la fiche de seance',
    'computeFormeScore': 'Score Forme du jour',
    '_ckSummary':    'Resume executif du Cockpit',
    '_ckRebuild':    'Moteur de recalcul des series',
}


def corps_ckrebuild(src):
    i = src.index('function _ckRebuild(){')
    j = src.index('\n}\n', i)
    return src[i:j]


def main():
    src = open(APP, encoding='utf-8').read()
    corps = corps_ckrebuild(src)
    ok, ko, pb = 0, 0, []

    def check(cond, msg):
        nonlocal ok, ko
        if cond:
            ok += 1
        else:
            ko += 1; pb.append(msg)

    # 1. toute serie de _CK doit etre declaree
    bloc = src[src.index('const _CK={'):]
    presentes = set(re.findall(r'^\s{2}([A-Z_][A-Z0-9_]*):', bloc[:6000], re.M))
    presentes |= set(re.findall(r'_CK\.([A-Za-z_][A-Za-z0-9_]*)\s*=', src))
    presentes = {p for p in presentes if not p.startswith('__')}

    for s in sorted(presentes):
        check(s in REGISTRE,
              f"serie _CK.{s} presente dans le code mais ABSENTE du registre "
              f"(ajoute-la avec son statut avant de livrer)")

    # 2. toute serie declaree LIVE doit etre ecrite par _ckRebuild
    for nom, (statut, desc, just) in REGISTRE.items():
        if statut == 'LIVE':
            ecrite = re.search(r'_CK\.' + re.escape(nom) + r'\s*\[', corps) or \
                     re.search(r'_CK\.' + re.escape(nom) + r'\s*=', corps)
            check(bool(ecrite),
                  f"_CK.{nom} est declaree LIVE ({desc}) mais n'est JAMAIS "
                  f"ecrite par _ckRebuild -> elle restera figee au build")
        elif statut == 'STATIC':
            check(bool(just),
                  f"_CK.{nom} est STATIC sans justification ecrite")

    # 3. les fonctions de rendu des indicateurs doivent exister
    for fn, desc in FONCTIONS_KPI.items():
        check(('function ' + fn + '(') in src,
              f"fonction {fn} introuvable ({desc})")

    # 4. _ckRebuild doit etre appele au chargement
    check('_ckRebuild();' in src.split('function _ckRebuild')[0] or
          re.search(r'hydrateOverrides\(\);\s*try\{_ckRebuild\(\)', src) is not None,
          "_ckRebuild n'est pas appele au chargement de l'app")

    print("REGISTRE KPI COCKPIT")
    print(f"  {len(presentes)} serie(s) detectee(s) dans le code, "
          f"{len(REGISTRE)} declaree(s) au registre")
    print(f"  RESULTAT : {ok} controle(s) OK, {ko} manquement(s)")
    for x in pb:
        print("     MANQUEMENT :", x)
    return 0 if ko == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
