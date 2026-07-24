#!/usr/bin/env python3
"""
================================================================================
 AUDIT COCKPIT — controle automatise a lancer AVANT CHAQUE PUSH
================================================================================

POURQUOI CE FICHIER EXISTE
--------------------------
Le Cockpit sert a decider des seances. Une valeur figee ou fausse n'est pas un
detail cosmetique : elle fausse une decision d'entrainement.

Trois incidents ont motive cet audit :
  1. Heatmap, Journal et Analyse par sortie figes depuis mi-juin (build 118)
  2. Z2, DC (derive cardiaque) et FCZ (zones) jamais recalcules, et FCZ utilisait
     des bornes de zones contredisant la table officielle de l'app (build 130)
  3. Le correctif de la Forme du jour, concu puis jamais implemente, laissait le
     score a 87 au lendemain d'un marathon (build 129)

Le point commun : rien ne verifiait automatiquement que ce qui est AFFICHE
correspond aux donnees REELLES. preflight verifie la chaine de build,
test_regression verifie que l'app ne casse pas. Aucun des deux ne verifiait la
JUSTESSE des chiffres. C'est le role de ce fichier.

PRINCIPE
--------
On recalcule independamment, en Python et depuis data.json, la valeur attendue
de chaque serie pour chaque semaine effectivement loggee. On la compare a ce que
le JS produit dans le navigateur. Tout ecart est un echec.

Les semaines anterieures au plan (sans seance loggee) ne sont pas verifiables :
elles proviennent de l'historique Strava figé et sont conservees telles quelles.

USAGE
-----
    python3 audit_cockpit.py            # depuis /tmp apres gen.py + assemble.py
    -> code retour 0 si tout est conforme, 1 sinon
================================================================================
"""

import json, re, sys
import statistics as st

DATA = '/tmp/data.json'
HTML = '/mnt/user-data/outputs/plan-entrainement.html'
CURWK = 30                      # semaine courante du plan


# ---------------------------------------------------------------- utilitaires
def mins(t):
    """Duree d'une seance en minutes. Formats : 4h18, 1h28:33, 36:49."""
    if not t:
        return None
    m = re.match(r'^(\d+)h(\d+)?:?(\d+)?$', str(t).strip())
    if m:
        return int(m.group(1)) * 60 + int(m.group(2) or 0) + int(m.group(3) or 0) / 60
    m = re.match(r'^(\d+):(\d+)$', str(t).strip())
    if m:
        return int(m.group(1)) + int(m.group(2)) / 60
    return None


def pace_s(a):
    if not a:
        return None
    m = re.search(r'(\d+):(\d+)', a)
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def _fallback(r, champ, motif):
    """Champ structure, sinon repli sur le texte du commentaire (comme le JS)."""
    v = r.get(champ)
    if isinstance(v, (int, float)):
        return v
    m = re.search(motif, r.get('commentaire') or '')
    return int(m.group(1)) if m else None


def charge(s):
    """Effort relatif : champ 're' si present, sinon estimation par type."""
    r = s.get('realise') or {}
    if isinstance(r.get('re'), (int, float)):
        return r['re']
    km = r.get('km') or 0
    t = (s.get('type') or '').lower()
    c = 8
    if 'trail' in t:
        c = 25
    elif any(k in t for k in ('seuil', 'tempo', 'spécifiq', 'specifiq', 'marathon', 'vma', 'vitesse')):
        c = 13
    elif 'long' in t:
        c = 10
    elif 'récup' in t or 'recup' in t:
        c = 6
    return round(km * c)


def est_facile(s):
    """Seance d'endurance facile : compte pour l'allure Z2."""
    t = ((s.get('type') or '') + ' ' + (s.get('titre') or '')).lower()
    dur = re.search(r'seuil|vma|tempo|fractionn|c[ôo]tes|sp[ée]cifique|vitesse|intervalle', t)
    fac = s.get('cat') in ('EF', 'ef') or re.search(r'\bef\b|footing|a[ée]robie|r[ée]cup', t)
    return bool(fac) and not bool(dur)


# ------------------------------------------------------------ verite terrain
def charger():
    d = json.load(open(DATA))
    sems = {}
    for wk, ss in d['SBW'].items():
        faites = [s for s in ss
                  if (s.get('realise') or {}).get('statut') in ('fait', 'partiel')
                  and (s.get('realise') or {}).get('km')]
        if faites:
            sems[int(wk)] = faites
    return d, sems


def attendu(sems, n_weeks):
    """Valeurs attendues pour une fenetre de n semaines."""
    ws = list(range(CURWK - n_weeks + 1, CURWK + 1))
    out = {'w': ['S%d' % w for w in ws]}
    for cle in ('vol', 're', 'dplus', 'pace', 'cad', 'z2', 'dc'):
        out[cle] = []
    for w in ws:
        ss = sems.get(w)
        if not ss:
            for cle in ('vol', 're', 'dplus', 'pace', 'cad', 'z2', 'dc'):
                out[cle].append(None)
            continue
        R = lambda s: s['realise']
        out['vol'].append(round(sum(R(s).get('km', 0) for s in ss), 1))
        out['re'].append(sum(charge(s) for s in ss))
        out['dplus'].append(sum(_fallback(R(s), 'elevation_gain', r'D\+\s*(\d+)') or 0 for s in ss))

        pc = [p for p in (pace_s(R(s).get('allure')) for s in ss) if p]
        out['pace'].append(round(st.mean(pc)) if pc else None)

        cd = []
        for s in ss:
            c = _fallback(R(s), 'cadence', r'cadence\s+(\d+)')
            if c:
                cd.append(c * 2 if c < 120 else c)
        out['cad'].append(round(st.mean(cd)) if cd else None)

        ef = [p for p in (pace_s(R(s).get('allure')) for s in ss if est_facile(s)) if p]
        out['z2'].append(round(st.median(ef)) if ef else None)

        dc = [R(s)['decouplage']['pct'] for s in ss
              if R(s).get('decouplage') and R(s)['decouplage'].get('qualite') == 'fiable']
        out['dc'].append(round(st.median(dc), 2) if dc else None)
    return out


def zones_attendues(sems, n_weeks):
    """Repartition par intensite, bornes officielles ZONES_FC."""
    Z = {'Z1': 0, 'Z2': 0, 'Z3': 0, 'Z4+': 0}
    tot = 0
    for w in range(CURWK - n_weeks + 1, CURWK + 1):
        for s in sems.get(w, []):
            r = s['realise']
            fc, m = r.get('fc_moy'), mins(r.get('temps'))
            if not fc or not m:
                continue
            k = 'Z1' if fc < 134 else 'Z2' if fc < 154 else 'Z3' if fc < 167 else 'Z4+'
            Z[k] += m
            tot += m
    return None if not tot else {k: round(v / tot * 100) for k, v in Z.items()}


# --------------------------------------------------------------------- audit
def main():
    from playwright.sync_api import sync_playwright

    d, sems = charger()
    verifiables = sorted(sems)
    ok, ko, pb = 0, 0, []

    def cmp(nom, att, got, tol=0.01):
        nonlocal ok, ko
        if att is None:
            return
        if got is None:
            ko += 1; pb.append(f"{nom}: attendu {att}, obtenu None"); return
        if abs(att - got) <= tol * max(1, abs(att)):
            ok += 1
        else:
            ko += 1; pb.append(f"{nom}: attendu {att}, obtenu {got}")

    def check(nom, cond, det=""):
        nonlocal ok, ko
        if cond:
            ok += 1
        else:
            ko += 1; pb.append(f"{nom} {det}")

    def meteo(route):
        """L'API archive n'est pas joignable en test : on la simule pour
        verifier les cartes dans les conditions de production."""
        times, temps = [], []
        for mo in range(1, 13):
            for day in range(1, 29):
                times.append(f"2026-{mo:02d}-{day:02d}T18:00"); temps.append(24.0)
        route.fulfill(json={"hourly": {"time": times, "temperature_2m": temps}})

    print("AUDIT COCKPIT")
    print("Semaines verifiables (avec seances loggees) :",
          ", ".join("S%d" % w for w in verifiables), "\n")

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_page(viewport={"width": 390, "height": 844})
        errs = []
        p.on("pageerror", lambda e: errs.append(str(e)[:150]))
        p.route("**/archive-api.open-meteo.com/**", meteo)
        p.goto("file://" + HTML, wait_until="load", timeout=25000)
        p.wait_for_timeout(2000)
        if p.evaluate("document.getElementById('rwoverlay')"):
            p.evaluate("document.getElementById('rwoverlay').style.display='none'")
        p.evaluate("showTab('cockpit')")
        p.wait_for_timeout(2200)

        # --- 1. series numeriques, 4 fenetres
        for N in (2, 4, 8, 12):
            att = attendu(sems, N)
            app = p.evaluate(
                f"({{VOL:_CK.VOL[{N}],RE:_CK.RE[{N}],DPLUS:_CK.DPLUS[{N}],"
                f"PACE:_CK.PACE[{N}],CAD:_CK.CAD[{N}],Z2:_CK.Z2[{N}],"
                f"DC:_CK.DC[{N}],FCZ:_CK.FCZ[{N}]}})")
            for i, lab in enumerate(att['w']):
                wn = int(lab[1:])
                if wn not in verifiables:
                    continue
                if lab not in app['VOL']['w']:
                    ko += 1; pb.append(f"[{N}s] {lab} absente de l'app"); continue
                j = app['VOL']['w'].index(lab)
                cmp(f"[{N}s] {lab} volume",   att['vol'][i],   app['VOL']['a'][j])
                cmp(f"[{N}s] {lab} effort",   att['re'][i],    app['RE']['v'][j])
                cmp(f"[{N}s] {lab} D+",       att['dplus'][i], app['DPLUS']['v'][j])
                cmp(f"[{N}s] {lab} allure",   att['pace'][i],  app['PACE']['v'][j], 0.02)
                cmp(f"[{N}s] {lab} cadence",  att['cad'][i],   app['CAD']['v'][j])
                cmp(f"[{N}s] {lab} allure Z2", att['z2'][i],   app['Z2']['v'][j], 0.03)
                cmp(f"[{N}s] {lab} derive",   att['dc'][i],    app['DC']['v'][j], 0.02)
            za = zones_attendues(sems, N)
            if za:
                got = {x[0]: x[2] for x in app['FCZ']}
                for k, v in za.items():
                    cmp(f"[{N}s] zone {k}", v, got.get(k), 0.03)
            check(f"[{N}s] zones totalisent 100%", abs(sum(x[2] for x in app['FCZ']) - 100) <= 2)

        # --- 2. bascule reelle des fenetres + rendu des graphes
        GRAPHES = ['ckPMC', 'ckVol', 'ckRE', 'ckACWR', 'ckDP',
                   'ckZ2', 'ckDC', 'ckPACE', 'ckFC', 'ckCAD']
        JS = """(function(ids){var o={vides:[],win:_ckWin,lab:{}};
            ids.forEach(function(id){var e=document.getElementById(id);var h=e?e.innerHTML:'';
              if(!e||h.length<20||/NaN|undefined|Infinity/.test(h))o.vides.push(id);});
            ['ck-vol-sub','ck-fc-sub','ck-z2-val','ck-dc-val','ck-cad-val','ck-acwr-val'].forEach(
              function(id){var e=document.getElementById(id);o.lab[id]=e?e.textContent.trim():'ABSENT';});
            return o;})"""
        for N in (2, 4, 8, 12):
            p.evaluate("(function(w){var bs=document.querySelectorAll('.ck-tg');"
                       "for(var i=0;i<bs.length;i++){if(bs[i].textContent.trim().indexOf(String(w))===0)"
                       "{bs[i].click();return;}}})", N)
            p.wait_for_timeout(550)
            r = p.evaluate(JS, GRAPHES)
            check(f"[{N}s] 10 graphes rendus", not r['vides'], str(r['vides']))
            check(f"[{N}s] fenetre active coherente",
                  r['win'] == N and f"{N} sem" in r['lab']['ck-vol-sub'],
                  f"_ckWin={r['win']} sub='{r['lab']['ck-vol-sub']}'")
            check(f"[{N}s] aucune valeur NaN affichee",
                  not any('NaN' in str(v) or v == 'ABSENT' for v in r['lab'].values()),
                  str(r['lab']))

        # --- 3. cartes
        for eid, lbl in [('eff-body', 'efficience aerobie'),
                         ('heat-body', 'acclimatation chaleur'),
                         ('saison-body', 'progression saison'),
                         ('decoup-body', 'decouplage cardiaque')]:
            t = p.evaluate(f"(function(){{var e=document.getElementById('{eid}');"
                           f"return e?e.innerText.trim():'';}})()")
            check(f"carte {lbl}", len(t) > 15 and 'indisponible' not in t.lower(),
                  t.replace('\n', ' ')[:60])

        # --- 4. forme du jour
        f = p.evaluate("computeFormeScore()")
        check("forme : score dans [0,100]", 0 <= f['score'] <= 100, str(f['score']))
        check("forme : 4 composantes", len(f['components']) == 4)
        check("forme : fraicheur basee sur la fatigue reelle",
              '%' in (f['components'][0]['detail'] or ''),
              f['components'][0]['detail'])

        # --- 5. donnees historiques vivantes
        hm = p.evaluate("(function(){var d=Object.keys(HEATMAP).sort();"
                        "return d[d.length-1];})()")
        derniere = max((s['date'] for ss in sems.values() for s in ss if s.get('date')), default='')
        check("heatmap a jour", hm >= derniere, f"heatmap={hm} derniere seance={derniere}")
        jr = p.evaluate("JOURNAL.map(function(j){return j.sem;})")
        check("journal du coach a jour", len(jr) >= 5, str(jr))
        runs = p.evaluate("_CK.RUNS.length")
        check("analyse par sortie alimentee", runs >= 8, f"{runs} sorties")

        check("aucune erreur JS", not errs, str(errs))
        b.close()

    print(f"  RESULTAT : {ok} controle(s) OK, {ko} ecart(s)")
    for x in pb:
        print("     ECART :", x)
    return 0 if ko == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
