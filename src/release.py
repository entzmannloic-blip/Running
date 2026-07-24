#!/usr/bin/env python3
"""
================================================================================
 PORTE DE LIVRAISON — process obligatoire avant tout push
================================================================================

POURQUOI
--------
Deux incidents ont montre que la qualite ne peut pas reposer sur le jugement
de celui qui livre :

  * Build 118 : trois series (Z2, DC, FCZ) identifiees comme figees, corrigees
    partiellement, et livrees comme si le travail etait complet.
  * Build 129 : un correctif de la Forme du jour concu avec Loic, valide par
    lui, puis jamais implemente — la conversation avait derive et personne ne
    tenait la liste.

Dans les deux cas, un humain a decide que c'etait "fini". Ce script retire
cette decision : la livraison est bloquee tant que les quatre phases ne sont
pas vertes.

LES QUATRE PHASES
-----------------
  1. RECHERCHE      comprendre l'existant avant de modifier
                    -> registre des KPI : toute serie du Cockpit est declaree,
                       tout ce qui est declare LIVE est reellement recalcule
  2. EXPERIMENTATION valider la construction
                    -> gen.py + assemble.py dans le bon ordre, syntaxe JS
  3. TEST            prouver que c'est juste, pas seulement que ca s'affiche
                    -> preflight (chaine de build)
                    -> test_regression (l'app ne casse pas)
                    -> audit_cockpit (les CHIFFRES sont justes, 4 fenetres)
  4. LIVRAISON       pousser, puis verifier que c'est reellement en ligne
                    -> le push n'est autorise que si 1 a 3 sont verts
                    -> apres push, controle du deploiement GitHub Pages

REGLE
-----
Un seul echec = pas de push. Aucune exception, aucun "c'est mineur".

USAGE
-----
    python3 release.py            # verifie tout, n'ecrit rien
    python3 release.py --push     # verifie tout PUIS pousse si tout est vert
================================================================================
"""

import subprocess, sys, os, json, re, time

WORK = '/tmp'
OUT = '/mnt/user-data/outputs'
REPO = 'entzmannloic-blip/Running'


class Phase:
    def __init__(self, num, nom):
        self.num, self.nom = num, nom
        self.etapes = []

    def ajoute(self, libelle, ok, detail=""):
        self.etapes.append((libelle, ok, detail))
        return ok

    @property
    def vert(self):
        return all(ok for _, ok, _ in self.etapes)

    def afficher(self):
        print(f"\n{'─' * 62}\nPHASE {self.num} — {self.nom}")
        for lib, ok, det in self.etapes:
            print(f"  {'OK  ' if ok else 'ECHEC'}  {lib}" + (f"   {det}" if det else ""))


def run(cmd, cwd=WORK):
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def main():
    pousser = '--push' in sys.argv
    phases = []

    # ------------------------------------------------ PHASE 1 : RECHERCHE
    p1 = Phase(1, "RECHERCHE — l'existant est-il sous controle ?")
    rc, out = run(f'python3 {WORK}/kpi_registry.py')
    manques = [l.strip() for l in out.splitlines() if 'MANQUEMENT' in l]
    p1.ajoute("registre des KPI du Cockpit", rc == 0,
              "toutes les series declarees et reellement recalculees" if rc == 0
              else f"{len(manques)} manquement(s)")
    for m in manques:
        print("        " + m)
    phases.append(p1)

    # ------------------------------------------- PHASE 2 : EXPERIMENTATION
    p2 = Phase(2, "EXPERIMENTATION — la construction est-elle saine ?")
    rc, out = run('python3 gen.py')
    p2.ajoute("gen.py", rc == 0, out.strip().splitlines()[0] if out.strip() else "")
    rc, out = run('python3 assemble.py')
    p2.ajoute("assemble.py", rc == 0, out.strip().splitlines()[-1] if out.strip() else "")
    rc, _ = run('node --check app.js')
    p2.ajoute("syntaxe JavaScript", rc == 0)
    phases.append(p2)

    # -------------------------------------------------- PHASE 3 : TEST
    p3 = Phase(3, "TEST — les chiffres sont-ils justes ?")
    for script, libelle in [('preflight.py', "preflight (chaine de build)"),
                            ('test_regression.py', "regression (l'app ne casse pas)"),
                            ('audit_cockpit.py', "audit Cockpit (justesse des valeurs)")]:
        chemin = f'{WORK}/{script}'
        if not os.path.exists(chemin):
            p3.ajoute(libelle, False, "script introuvable")
            continue
        rc, out = run(f'python3 {chemin}')
        ligne = next((l.strip() for l in out.splitlines()
                      if 'RESULTAT' in l or 'RESULTAT' in l.upper()), '')
        bloquant = ('NE PAS PUSHER' in out) or ('ECHOUE' in out) or (rc != 0)
        p3.ajoute(libelle, not bloquant, ligne)
        for l in out.splitlines():
            if 'ECART' in l or 'MANQUEMENT' in l:
                print("        " + l.strip())
    phases.append(p3)

    for ph in phases:
        ph.afficher()

    tout_vert = all(ph.vert for ph in phases)
    print(f"\n{'═' * 62}")
    if not tout_vert:
        print("LIVRAISON BLOQUEE — corriger les echecs ci-dessus avant de pousser.")
        return 1
    print("Phases 1 a 3 vertes.")

    if not pousser:
        print("Mode verification seule. Relancer avec --push pour livrer.")
        return 0

    # ---------------------------------------------- PHASE 4 : LIVRAISON
    print(f"\n{'─' * 62}\nPHASE 4 — LIVRAISON")
    tok = os.environ.get('GH_TOKEN')
    if not tok:
        print("  ECHEC  GH_TOKEN absent de l'environnement")
        return 1

    import urllib.request, urllib.error
    API = f'https://api.github.com/repos/{REPO}'

    def req(m, u, b=None):
        r = urllib.request.Request(
            u, data=(json.dumps(b).encode() if b is not None else None), method=m,
            headers={'Authorization': f'Bearer {tok}',
                     'Accept': 'application/vnd.github+json',
                     'User-Agent': 'release', 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(r) as x:
                return x.status, json.load(x)
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.load(e)
            except Exception:
                return e.code, {}

    build = None
    m = re.search(r'"build":(\d+)', open(f'{WORK}/gen.py', encoding='utf-8').read())
    if m:
        build = m.group(1)

    fichiers = {'index.html': f'{OUT}/index.html'}
    for src, dst in [('gen.py', 'src/gen.py'), ('app.js', 'src/app.js'),
                     ('css_extra.txt', 'src/css_extra.txt'),
                     ('audit_cockpit.py', 'src/audit_cockpit.py'),
                     ('kpi_registry.py', 'src/kpi_registry.py'),
                     ('release.py', 'src/release.py'),
                     ('decouplage.py', 'src/decouplage.py')]:
        if os.path.exists(f'{WORK}/{src}'):
            fichiers[dst] = f'{WORK}/{src}'

    st, ref = req('GET', f'{API}/git/ref/heads/main')
    if st != 200:
        print("  ECHEC  lecture de la reference main"); return 1
    parent = ref['object']['sha']
    st, co = req('GET', f'{API}/git/commits/{parent}')
    tree = [{'path': p, 'mode': '100644', 'type': 'blob',
             'content': open(fp, encoding='utf-8').read()} for p, fp in fichiers.items()]
    st, tr = req('POST', f'{API}/git/trees', {'base_tree': co['tree']['sha'], 'tree': tree})
    if st != 201:
        print("  ECHEC  creation de l'arbre"); return 1
    st, nc = req('POST', f'{API}/git/commits',
                 {'message': f'release build {build} (4 phases vertes)',
                  'tree': tr['sha'], 'parents': [parent]})
    if st != 201:
        print("  ECHEC  creation du commit"); return 1
    st, _ = req('PATCH', f'{API}/git/refs/heads/main', {'sha': nc['sha']})
    if st != 200:
        print("  ECHEC  mise a jour de main"); return 1
    sha = nc['sha'][:8]
    print(f"  OK     push effectue — build {build} — commit {sha}")

    # controle du deploiement reel
    print("  ...    attente du deploiement GitHub Pages")
    deploye = False
    for _ in range(12):
        time.sleep(15)
        st, d = req('GET', f'{API}/pages/builds/latest')
        if st == 200 and d.get('commit', '').startswith(nc['sha'][:8]) \
           and d.get('status') == 'built':
            deploye = True
            break
    print(f"  {'OK    ' if deploye else 'ATTENTE'} deploiement GitHub Pages"
          + ("" if deploye else " — pousse mais pas encore reconstruit par Pages"))

    print(f"\n{'═' * 62}\nLIVRAISON TERMINEE — build {build} — commit {sha}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
