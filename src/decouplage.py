"""
================================================================================
 DECOUPLAGE CARDIAQUE — procedure complete (recuperation, traitement, tests)
 Version d'algorithme : decoup-v1
================================================================================

POURQUOI CE FICHIER
-------------------
L'app est un fichier HTML statique : elle ne peut pas interroger Strava
elle-meme. Le calcul est donc fait ICI, une seule fois, au moment ou une seance
est loggee. Seul le RESULTAT (quelques nombres) est stocke dans gen.py.

Les streams bruts ne sont PAS conserves : ils resteraient trop volumineux.
Mais ils restent disponibles chez Strava indefiniment, donc tout l'historique
peut etre recalcule si l'algorithme evolue. C'est pour cela que le numero de
version est stocke avec chaque KPI ("algo":"decoup-v1") : sans lui, on
comparerait un jour des chiffres calcules differemment sans le savoir.

--------------------------------------------------------------------------------
 ETAPE 1 — ELIGIBILITE  (avant tout calcul)
--------------------------------------------------------------------------------
Filtres cumulatifs. Une seule condition non remplie => seance non eligible.

  a) Type de seance : EF / sortie longue / recuperation UNIQUEMENT.
     Exclus : seuil, VMA, cotes, fractionne, specifique, tempo.
     Raison : leur allure varie par construction, le rapport allure/FC n'a
     aucun sens sur ce type d'effort.
  b) Terrain : route. Les trails sont exclus (le relief pilote la FC).
  c) Denivele < ~15 m/km.
  d) Streams FC + vitesse disponibles.
  e) Fenetre exploitable >= 40 min APRES nettoyage (voir etape 4).
  f) Regime STABLE : pas de changement d'allure delibere en cours de sortie.
     Verifie automatiquement (changement_allure_structurel) par detection de
     point de rupture. Un ecart durable de plus de 30 s/km => la seance est
     marquee "non_representatif" et AUCUN chiffre n'est stocke.
     Cas reel : marathon ViaRhona du 23/07, 15 km seul a 5:36/km puis 23 km
     avec un partenaire a 6:21/km. Phases isolees : +1,5 % et +8,4 %.
     Ensemble : +16,9 %, soit "seance subie" alors que le ressenti etait
     excellent et le finish a 5:15/km. Sans ce garde-fou, la tendance aurait
     ete polluee par un artefact.

--------------------------------------------------------------------------------
 ETAPE 2 — RECUPERATION
--------------------------------------------------------------------------------
Strava MCP : get_activity_streams(activity_id, resolution=1000,
             streams=["time","heart_rate","velocity_smooth"])

  - resolution=1000 => environ un releve toutes les 5 s.
  - NE PAS utiliser resolution=100 : a cette grossierete, decaler la fenetre
    d'une minute fait basculer des points d'une moitie a l'autre et le verdict
    peut s'inverser (constate : 5,7 % vs 7,2 % sur la meme sortie).

--------------------------------------------------------------------------------
 ETAPE 3 — NETTOYAGE  (fonction clean puis lisse)
--------------------------------------------------------------------------------
  - Points a l'arret (vitesse < 0,5 m/s) : retires.
  - FC nulle ou absente : retiree.
  - Decrochages capteur : saut > 15 bpm entre deux points rapproches.
  - Trous temporels (feux rouges, pauses) : detectes via l'ecart median, la
    continuite est coupee. Un trou de 255 s a ete observe sur la recup du 20/7.
  - Lissage : mediane glissante sur 30 s (tue les pics parasites sans aplatir
    la tendance).

--------------------------------------------------------------------------------
 ETAPE 4 — FENETRE D'ANALYSE
--------------------------------------------------------------------------------
  DEBUT = 3 minutes (constante DEPART).
    Choix valide empiriquement par balayage de 1,5 a 15 min sur des sorties
    reelles : a 3 min, footings ET sorties longues passent le test de
    robustesse. Couper plus tard (8-10 min) detruit la fenetre des footings
    et rend le chiffre instable (ecart jusqu'a 3 pts).
    Effet de bord assume : inclure un reste de montee cardiaque decale
    legerement toutes les valeurs vers le haut. Ce biais etant applique
    identiquement partout, il ne fausse pas la TENDANCE, qui est le produit.

  FIN = detection automatique des lignes droites / fast finish (detect_fin).
    Indispensable : sur l'EF du 17/7, sans coupure la sortie affichait -0,46 %
    (donc "parfaite"), avec coupure +3,31 %. Les accelerations finales
    masquaient completement la derive reelle.

--------------------------------------------------------------------------------
 ETAPE 5 — CALCUL
--------------------------------------------------------------------------------
  Rapport allure/FC (vitesse / FC) point par point, puis PENTE de la droite de
  tendance sur toute la fenetre (decoup_regression).
  On prefere la regression a la comparaison "deux moities" : elle utilise tous
  les points et non deux moyennes, donc beaucoup moins sensible a l'endroit
  exact ou l'on coupe.
  On calcule aussi la derive brute en bpm : c'est la grandeur que le coureur
  lit sur sa montre, et quand les deux divergent c'est la qu'est l'information.

  ATTENDU (contextualisation) : base 6 %, +2 si duree > 2 h, +2 si temp > 25 C.
  C'est la position PAR RAPPORT a cet attendu qui fait le verdict, pas la
  valeur brute.

--------------------------------------------------------------------------------
 ETAPE 6 — BOUCLE DE VALIDATION  (les 4 tests)
--------------------------------------------------------------------------------
  Le KPI n'est stocke QUE si les quatre passent :

    1. ROBUSTESSE  : recalcul en decalant le depart dans la plage legitime
                     (2 a 5 min). Ecart max < 1,5 point.
                     On ne teste PAS en deca de 2 min : on serait encore dans
                     la montee cardiaque, ce n'est pas une fenetre valide.
    2. COUPURE FIN : recalcul en decalant la coupure des lignes droites de
                     +/-1 a 2 min. Ecart max < 1,5 point.
                     Remplace un ancien test "regression vs 2 moities" qui
                     echouait systematiquement : avec un depart a 3 min les
                     deux methodes divergent PAR CONSTRUCTION (la regression
                     pondere tous les points, les "2 moities" ecrasent en deux
                     moyennes). Comparer deux methodes arbitraires ne testait
                     rien d'utile ; la sensibilite a la coupure de fin, si.
    3. COUVERTURE  : >= 80 % des points survivent au nettoyage.
    4. PLAUSIBILITE: FC moyenne 90-185 bpm, allure 1,5-6,0 m/s.

  Si un seul echoue => qualite = "incertain" ou "non_calculable", et AUCUN
  chiffre n'est affiche dans l'app. Un indicateur qui se tait quand il ne sait
  pas vaut mieux qu'un indicateur qui parle tout le temps.

--------------------------------------------------------------------------------
 ETAPE 7 — STOCKAGE  (dans le bloc "realise" de la seance, gen.py)
--------------------------------------------------------------------------------
  "decouplage":{
     "pct": 0.43,          # decouplage en %, methode regression
     "bpm": 1.8,           # derive brute FC (2e moitie - 1re moitie)
     "fen_min": 72,        # duree de la fenetre analysee
     "temp": 22,           # temperature de la seance
     "attendu": 6,         # seuil contextualise
     "p1": "5:52/km", "fc1": 138,   # 1re moitie
     "p2": "5:44/km", "fc2": 140,   # 2e moitie
     "qualite": "fiable",  # fiable | incertain | non_calculable | non_representatif
     "algo": "decoup-v1"   # version — indispensable pour recalculer plus tard
  }

--------------------------------------------------------------------------------
 ECHELLE  (calibree sur les sorties reelles de Loic, juillet 2026)
--------------------------------------------------------------------------------
    < 3 %   Footing maitrise
    3 - 6 % Conforme
    6 - 9 % Sous tension
    > 9 %   Seance subie
  Ajustee par l'ecart a l'attendu (voir _decoupVerdict dans app.js).
  Calibration initiale sur 4 sorties : recup 20/7 +0,43 %, EF 15/7 +5,12 %,
  EF 17/7 +8,33 %, SL 16/7 +9,35 %. Amplitude 8,9 pts => l'indicateur
  discrimine reellement. A revoir apres ~10 sorties.
================================================================================
"""

DEPART = 180          # debut de fenetre, en secondes
DUREE_MIN = 40        # fenetre exploitable minimale, en minutes
ALGO_VERSION = "decoup-v1"
SEUIL_ROBUSTESSE = 1.5
SEUIL_COUPURE_FIN = 1.5
SEUIL_COUVERTURE = 0.80


def clean(time, hr, vel):
    """Etape 3 : retire arrets, points immobiles et decrochages capteur."""
    n = len(time)
    pts = []
    for i in range(n):
        if hr[i] is None or vel[i] is None:
            continue
        if hr[i] <= 0 or vel[i] < 0.5:
            continue
        pts.append((time[i], hr[i], vel[i]))
    if len(pts) < 20:
        return [], 0.0
    dt = sorted(pts[i + 1][0] - pts[i][0] for i in range(len(pts) - 1))
    med_dt = dt[len(dt) // 2]
    seuil_trou = max(60, med_dt * 6)
    out = [pts[0]]
    for i in range(1, len(pts)):
        gap = pts[i][0] - pts[i - 1][0]
        dhr = abs(pts[i][1] - pts[i - 1][1])
        if gap <= seuil_trou and dhr > 15 and gap < med_dt * 3:
            continue            # decrochage capteur
        out.append(pts[i])
    brut = len([1 for i in range(n) if hr[i] and vel[i]])
    return out, len(out) / max(1, brut)


def lisse(pts, fenetre_s=30):
    """Mediane glissante : enleve les pics parasites sans aplatir la tendance."""
    res = []
    for t, h, v in pts:
        wh = sorted(p[1] for p in pts if abs(p[0] - t) <= fenetre_s / 2)
        wv = sorted(p[2] for p in pts if abs(p[0] - t) <= fenetre_s / 2)
        res.append((t, wh[len(wh) // 2], wv[len(wv) // 2]))
    return res


def detect_fin(pts, t_debut):
    """Etape 4 : repere le debut des lignes droites / fast finish."""
    if not pts:
        return None
    tmax = pts[-1][0]
    corps = [p for p in pts if t_debut <= p[0] <= t_debut + (tmax - t_debut) * 0.75]
    if len(corps) < 10:
        return tmax
    vs = sorted(p[2] for p in corps)
    seuil_rapide = vs[int(len(vs) * 0.75)] * 1.15
    queue = [p for p in pts if p[0] > t_debut + (tmax - t_debut) * 0.6]
    for i, (t, h, v) in enumerate(queue):
        suite = queue[i:i + 4]
        if len(suite) >= 3 and sum(1 for p in suite if p[2] > seuil_rapide) >= 2:
            return t
    return tmax


def changement_allure_structurel(pts, seuil_s_km=30):
    """
    Detecte un changement d'allure DELIBERE en cours de sortie (rejoindre un
    partenaire plus lent, changement de terrain...), qui n'est pas de la fatigue.

    Pourquoi c'est indispensable : le decouplage suppose un effort en regime
    stable. Sur le marathon ViaRhona du 23/07, Loic a couru 15 km seul a
    5:36/km puis 23 km avec Yannis a 6:21/km. Chaque phase prise isolement
    donne +1,5 % et +8,4 % (coherent), mais les deux ensemble donnent +16,9 % :
    l'indicateur lit le ralentissement social comme un effondrement.
    Les 4 tests de validation ne l'attrapent pas : ils mesurent la STABILITE du
    calcul, pas la VALIDITE de l'hypothese de regime stable.

    Methode : detection de POINT DE RUPTURE. On teste chaque instant candidat
    entre 20 % et 70 % de la fenetre, et on retient la plus grande difference
    d'allure mediane avant/apres. Une decoupe en tiers fixes ne suffit pas :
    sur le ViaRhona elle ne mesurait que 20 s/km au lieu des 45 reels, parce
    que les tiers ne coincidaient pas avec le changement de rythme.
    Le dernier tiers est exclu du balayage : un finish rapide est normal et
    deja traite par detect_fin.
    """
    if len(pts) < 30:
        return False, 0
    t0, t1 = pts[0][0], pts[-1][0]
    duree = t1 - t0
    med = lambda L: sorted(L)[len(L) // 2]
    pire = 0
    for frac in [x / 20.0 for x in range(4, 15)]:      # 20 % a 70 %
        tc = t0 + duree * frac
        av = [p[2] for p in pts if t0 <= p[0] < tc]
        ap = [p[2] for p in pts if tc <= p[0] <= t0 + duree * 0.85]
        if len(av) < 10 or len(ap) < 10:
            continue
        v1, v2 = med(av), med(ap)
        if v1 <= 0 or v2 <= 0:
            continue
        ecart = 1000 / v2 - 1000 / v1                 # s/km, positif = ralentissement
        if abs(ecart) > abs(pire):
            pire = ecart
    return abs(pire) > seuil_s_km, round(pire)


def decoup_regression(pts):
    """Etape 5 : pente de la droite de tendance du rapport vitesse/FC."""
    if len(pts) < 10:
        return None
    xs = [p[0] for p in pts]
    ys = [p[2] / p[1] for p in pts]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    pente = sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / den
    y0 = my + pente * (xs[0] - mx)
    y1 = my + pente * (xs[-1] - mx)
    return None if y0 == 0 else (y0 - y1) / y0 * 100


def decoup_moities(pts):
    """Methode classique, utilisee uniquement pour le test de concordance."""
    if len(pts) < 10:
        return None
    mid = (pts[0][0] + pts[-1][0]) / 2
    h1 = [p for p in pts if p[0] <= mid]
    h2 = [p for p in pts if p[0] > mid]
    if len(h1) < 5 or len(h2) < 5:
        return None
    ef = lambda L: (sum(p[2] for p in L) / len(L)) / (sum(p[1] for p in L) / len(L))
    e1, e2 = ef(h1), ef(h2)
    return (e1 - e2) / e1 * 100


def moities(pts):
    """Allures et FC des deux moities, pour l'affichage."""
    mid = (pts[0][0] + pts[-1][0]) / 2
    h1 = [p for p in pts if p[0] <= mid]
    h2 = [p for p in pts if p[0] > mid]
    m = lambda L, i: sum(p[i] for p in L) / len(L)
    return (pace_str(m(h1, 2)), round(m(h1, 1)),
            pace_str(m(h2, 2)), round(m(h2, 1)),
            m(h2, 1) - m(h1, 1))


def pace_str(v):
    if not v:
        return "?"
    s = 1000 / v
    return "%d:%02d/km" % (s // 60, s % 60)


def attendu(duree_min, temp):
    """Seuil contextualise : plus c'est long et chaud, plus on tolere."""
    a = 6
    if duree_min > 120:
        a += 2
    if temp is not None and temp > 25:
        a += 2
    return a


def analyse(streams, temp=None):
    """
    Procedure complete. Renvoie le dict a stocker dans "realise"."decouplage",
    ou un dict {"qualite": "non_calculable", "raison": ...}.
    """
    t, hr, vel = streams['time'], streams['heart_rate'], streams['velocity_smooth']
    pts, couv = clean(t, hr, vel)
    if not pts:
        return {"qualite": "non_calculable", "raison": "donnees insuffisantes",
                "algo": ALGO_VERSION}
    pts = lisse(pts)
    t_fin = detect_fin(pts, DEPART)
    fen = [p for p in pts if DEPART <= p[0] <= t_fin]
    if len(fen) < 15:
        return {"qualite": "non_calculable", "raison": "fenetre vide",
                "algo": ALGO_VERSION}
    duree = (fen[-1][0] - fen[0][0]) / 60
    if duree < DUREE_MIN:
        return {"qualite": "non_calculable",
                "raison": "fenetre trop courte (%.0f min < %d)" % (duree, DUREE_MIN),
                "algo": ALGO_VERSION}

    # Garde-fou : changement d'allure delibere => hypothese de regime stable violee
    change, ecart_s = changement_allure_structurel(fen)
    if change:
        return {"qualite": "non_representatif",
                "raison": "changement d'allure delibere en cours de sortie (%+d s/km au point "
                          "de rupture) : le decouplage suppose un effort en regime "
                          "stable" % ecart_s,
                "algo": ALGO_VERSION}

    d_reg = decoup_regression(fen)
    d_moi = decoup_moities(fen)
    p1, fc1, p2, fc2, dbpm = moities(fen)

    # ---------- ETAPE 6 : boucle de validation ----------
    tests = {}
    var = []
    for delta in (-60, 60, 120):        # 2 a 5 min : en deca on est encore dans la montee cardiaque
        sub = [p for p in pts if max(0, DEPART + delta) <= p[0] <= t_fin]
        if len(sub) > 15:
            v = decoup_regression(sub)
            if v is not None:
                var.append(v)
    if d_reg is not None and var:
        ecart = max(abs(v - d_reg) for v in var)
        tests['robustesse'] = (ecart < SEUIL_ROBUSTESSE, "ecart max %.2f pt" % ecart)
    else:
        tests['robustesse'] = (False, "variantes non calculables")

    varf = []
    for delta in (-120, -60, 60):       # sensibilite a la detection des lignes droites
        tf2 = t_fin + delta
        sub = [p for p in pts if DEPART <= p[0] <= tf2]
        if len(sub) > 15 and (sub[-1][0] - sub[0][0]) / 60 >= DUREE_MIN * 0.85:
            v = decoup_regression(sub)
            if v is not None:
                varf.append(v)
    if d_reg is not None and varf:
        ef_ = max(abs(v - d_reg) for v in varf)
        tests['coupure_fin'] = (ef_ < SEUIL_COUPURE_FIN, "ecart max %.2f pt" % ef_)
    else:
        tests['coupure_fin'] = (True, "coupure en fin de sortie, non testable")

    tests['couverture'] = (couv >= SEUIL_COUVERTURE, "%.0f%% conserves" % (couv * 100))

    hrs = [p[1] for p in fen]
    vs = [p[2] for p in fen]
    fc_moy, v_moy = sum(hrs) / len(hrs), sum(vs) / len(vs)
    tests['plausibilite'] = (90 <= fc_moy <= 185 and 1.5 <= v_moy <= 6.0,
                             "FC %.0f, %s" % (fc_moy, pace_str(v_moy)))

    tous_ok = all(ok for ok, _ in tests.values())
    res = {
        "pct": round(d_reg, 2), "bpm": round(dbpm, 1),
        "fen_min": round(duree), "temp": temp,
        "attendu": attendu(duree, temp),
        "p1": p1, "fc1": fc1, "p2": p2, "fc2": fc2,
        "qualite": "fiable" if tous_ok else "incertain",
        "algo": ALGO_VERSION,
        "tests": {k: ("OK" if ok else "ECHEC", msg) for k, (ok, msg) in tests.items()},
    }
    if not tous_ok:
        res["raison"] = "; ".join("%s: %s" % (k, msg)
                                  for k, (ok, msg) in tests.items() if not ok)
    return res


if __name__ == "__main__":
    import json, sys
    if len(sys.argv) < 2:
        print(__doc__)
        print("Usage: python3 decouplage.py streams.json [temperature]")
        sys.exit(0)
    temp = float(sys.argv[2]) if len(sys.argv) > 2 else None
    r = analyse(json.load(open(sys.argv[1])), temp)
    for k, v in r.items():
        print("  %-12s %s" % (k, v))
