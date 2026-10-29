
import datetime as _dt
RACE_DATES={"Course — Objectif A":"2026-11-08","Course — Objectif B":"2026-11-28","Trail — Objectif C":"2026-07-05","Course — Objectif intermédiaire":"2026-10-04"}
def assign_days(arr):
    # Les jours suivent l'ordre des séances : séance 1 = premier jour, etc.
    # Sortie longue -> dimanche ; courses -> vraie date ; le reste réparti lundi->samedi dans l'ordre.
    days={}; slots=[0,1,2,3,4,5]; si=0
    for i,s in enumerate(arr):
        if "Objectif" in s["type"]:
            continue
        if "Sortie longue" in s["type"]:
            days[i]=6
        else:
            days[i]=slots[si%len(slots)]; si+=1
    return days
def date_for(arr,weeknum):
    dmap=assign_days(arr)
    for i,s in enumerate(arr):
        if s["type"] in RACE_DATES: s["date"]=RACE_DATES[s["type"]]
        else:
            d=dmap.get(i,1)
            s["date"]=_dt.date.fromisocalendar(2026,weeknum,d+1).isoformat()

# -*- coding: utf-8 -*-
import json, re

# --- Textes (revues de seance, revues de semaine, Rewinds) : fichiers de src/textes/ (voir docs/ENRICHISSEMENT.md)
import os as _os
_TEXTES = "textes"
_REVUE_FICHIER = "\x00revue:fichier"  # marqueur : la revue de cette seance est dans textes/seances/


def _lit_texte(*parts):
    with open(_os.path.join(_TEXTES, *parts), encoding="utf-8", newline="") as _f:
        return _f.read()


def _charge_revues_semaines(semaines):
    """textes/semaines/S43.html -> SEMAINES[...]["revue"]."""
    _par_num = {_s["num"]: _s for _s in semaines}
    for _nom in sorted(_os.listdir(_os.path.join(_TEXTES, "semaines"))):
        if _nom.endswith(".html"):
            _num = int(_nom[1:-5])
            if _num not in _par_num:
                raise SystemExit(f"textes/semaines/{_nom} : semaine inconnue")
            _par_num[_num]["revue"] = _lit_texte("semaines", _nom)


def _charge_revues_seances(sbw):
    """textes/seances/S44-2.html -> realise["revue"] de la seance 2 de la semaine 44."""
    _vus = set()
    for _nom in sorted(_os.listdir(_os.path.join(_TEXTES, "seances"))):
        if not _nom.endswith(".html"):
            continue
        _w, _i = _nom[1:-5].split("-", 1)
        _arr = sbw.get(int(_w), sbw.get(_w))
        _cible = [_x for _x in (_arr or []) if str(_x["id"]) == _i and _x.get("realise")]
        if len(_cible) != 1:
            raise SystemExit(f"textes/seances/{_nom} : seance introuvable ou sans bloc realise")
        _cible[0]["realise"]["revue"] = _lit_texte("seances", _nom)
        _vus.add((str(_w), _i))
    for _w, _arr in sbw.items():
        for _x in _arr:
            _r = _x.get("realise") or {}
            if _r.get("revue") == _REVUE_FICHIER and (str(_w), str(_x["id"])) not in _vus:
                raise SystemExit(f"S{_w}-{_x['id']} : revue attendue dans textes/seances/ mais fichier absent")


def _charge_rewinds():
    """textes/rewinds/S43.json -> REWINDS, tries par numero de semaine (rwAuto ouvre le dernier)."""
    _noms = [_n for _n in _os.listdir(_os.path.join(_TEXTES, "rewinds")) if _n.endswith(".json")]
    _noms.sort(key=lambda _n: int(_n[1:-5]))
    return [json.loads(_lit_texte("rewinds", _n)) for _n in _noms]

def _charge_logs(sbw):
    """logs/S44-2.json (scripts/log_seance.py) -> champs de la seance + bloc realise."""
    if not _os.path.isdir("logs"):
        return
    for _nom in sorted(_os.listdir("logs")):
        if not _nom.endswith(".json"):
            continue
        _w, _i = _nom[1:-5].split("-", 1)
        _cible = [_x for _x in sbw.get(int(_w), sbw.get(_w)) or [] if str(_x["id"]) == _i]
        if len(_cible) != 1:
            raise SystemExit(f"logs/{_nom} : seance introuvable dans le plan")
        _log = json.load(open(_os.path.join("logs", _nom), encoding="utf-8"))
        for _k, _v in _log.get("seance", {}).items():
            _cible[0][_k] = segs(_v) if _k == "segments" else _v
        _cible[0]["realise"] = _log["realise"]
# --- fin des textes

CSS=open('css.txt',encoding='utf-8').read()

P_REC="6:15-6:45/km"; P_EF="5:50-6:25/km"; P_AM="≈5:20/km"; P_SEUIL="≈4:50/km"; P_TRAIL="à l'effort"
P_S30="≈4:40/km"; P_S60="≈4:55/km"; F_S30="172-180"; F_S60="166-174"
F_REC="<140"; F_EF="135-150"; F_AM="152-163"; F_SEUIL="166-175"
GREEN="#16a34a";EF_COLOR="#16a34a";BLUE="#F4561D";ORANGE="#CA8A04";VIOLET="#6B6B74";RED="#DC2626";YELLOW="#A1A1AA";TEAL="#F4561D"

def segs(raw):
    t=0;out=[]
    for s in raw:
        s=dict(s); s['debut']=t; s['fin']=t+s['duree']; t+=s['duree']; out.append(s)
    return out
def mmss(sec): return f"{sec//60} min {sec%60:02d}" if sec%60 else f"{sec//60} min"

def ef(dist,dur,strides=False,opt=False,recovery=False,desc=None):
    if strides:
        d=dict(titre="Footing facile + lignes droites",type="EF + technique",sport="Course à pied",opt=opt,accent=EF_COLOR,fill=34,
          sous="EF facile et 6 lignes droites pour la vivacité.",
          metriques={"Distance":f"~{dist} km","Durée":f"~{dur} min","Allure":P_EF,"FC":F_EF,"RPE":"3-4","Type":"EF"},
          objectif="Volume aérobie <strong>vraiment facile</strong> + réveil neuromusculaire à moindre coût (lignes droites).",
          struct=[{"nom":"Échauffement","txt":"10 min footing très souple."},
                  {"nom":"Corps","txt":"Footing facile sur le plat (conversation possible)."},{"nom":"Lignes droites","txt":"6 répétitions : 100 m (≈20-25\") en accélération progressive relâchée, récupération 1 min marche/trot entre chaque. Jamais en sprint."},
                  {"nom":"Retour","txt":"5 min très souple."}],
          benefices="Entretien de la base aérobie, économie de course, fréquence gestuelle — sans fatigue.",
          vigilance="Lignes droites relâchées. Si le facile devient « moyen », tu retombes dans la zone grise.",
          legende=[{"c":GREEN,"l":"Facile / EF — RPE 3-4"},{"c":BLUE,"l":"Lignes droites — vif relâché"}],
          coach=[{"titre":"Le test de la parole","texte":"Si tu ne peux pas parler en phrases complètes, tu cours trop vite."}],
          segments=segs([{"nom":"Échauffement","role":"Mise en route.","duree":600,"couleur":"vert","bloc":"—","hauteur":30},
                  {"nom":"Footing facile","role":"EF, cœur de séance.","duree":(dur-22)*60,"couleur":"vert","bloc":"—","hauteur":42},
                  {"nom":"Ligne droite 1/6","role":"100 m en accélération progressive relâchée — jamais en sprint.","duree":22,"couleur":"bleu","bloc":"×6","hauteur":78},{"nom":"Récup 1","role":"1 min marche ou trot très lent.","duree":60,"couleur":"orange","bloc":"—","hauteur":26},{"nom":"Ligne droite 2/6","role":"100 m en accélération progressive relâchée — jamais en sprint.","duree":22,"couleur":"bleu","bloc":"×6","hauteur":78},{"nom":"Récup 2","role":"1 min marche ou trot très lent.","duree":60,"couleur":"orange","bloc":"—","hauteur":26},{"nom":"Ligne droite 3/6","role":"100 m en accélération progressive relâchée — jamais en sprint.","duree":22,"couleur":"bleu","bloc":"×6","hauteur":78},{"nom":"Récup 3","role":"1 min marche ou trot très lent.","duree":60,"couleur":"orange","bloc":"—","hauteur":26},{"nom":"Ligne droite 4/6","role":"100 m en accélération progressive relâchée — jamais en sprint.","duree":22,"couleur":"bleu","bloc":"×6","hauteur":78},{"nom":"Récup 4","role":"1 min marche ou trot très lent.","duree":60,"couleur":"orange","bloc":"—","hauteur":26},{"nom":"Ligne droite 5/6","role":"100 m en accélération progressive relâchée — jamais en sprint.","duree":22,"couleur":"bleu","bloc":"×6","hauteur":78},{"nom":"Récup 5","role":"1 min marche ou trot très lent.","duree":60,"couleur":"orange","bloc":"—","hauteur":26},{"nom":"Ligne droite 6/6","role":"100 m en accélération progressive relâchée — jamais en sprint.","duree":22,"couleur":"bleu","bloc":"×6","hauteur":78},{"nom":"Récup 6","role":"1 min marche ou trot très lent.","duree":60,"couleur":"orange","bloc":"—","hauteur":26},
                  {"nom":"Retour au calme","role":"Décompression.","duree":300,"couleur":"vert","bloc":"—","hauteur":28}]))
    elif recovery:
        d=dict(titre="Footing de récupération",type="Récupération active",sport="Course à pied",opt=opt,accent=EF_COLOR,fill=22,
          sous="Très facile, circulation, on efface la fatigue.",
          metriques={"Distance":f"~{dist} km","Durée":f"~{dur} min","Allure":P_REC,"FC":F_REC,"RPE":"2-3","Type":"Récup"},
          objectif="Footing très facile pour récupérer activement, sans aucun objectif de performance.",
          struct=[{"nom":"Corps","txt":"Footing lent et relâché, plat. Tu finis avec l'impression d'en avoir gardé largement sous le pied."},
                  {"nom":"Retour","txt":"Étirements doux, mobilité légère."}],
          benefices="Circulation, récupération, sans ajout de fatigue.",
          vigilance="Vraiment lent. Si tu n'as pas envie, marche ou repos : c'est la séance la plus sacrifiable.",
          legende=[{"c":GREEN,"l":"Récupération — RPE 2-3"}],
          coach=[{"titre":"Lent = utile","texte":"Une récup réussie est une récup qui ne ressemble pas à un entraînement."}])
    else:
        d=dict(titre="Footing facile",type="EF aérobie",sport="Course à pied",opt=opt,accent=EF_COLOR,fill=28,
          sous="Volume aérobie pur, plat, facile.",
          metriques={"Distance":f"~{dist} km","Durée":f"~{dur} min","Allure":P_EF,"FC":F_EF,"RPE":"3","Type":"EF"},
          objectif="Du volume aérobie facile sur le plat — le socle polarisé qui rend la qualité efficace.",
          struct=[{"nom":"Échauffement","txt":"10 min de montée d'allure douce."},
                  {"nom":"Corps","txt":"Footing continu facile et régulier, terrain plat, allure de conversation."},
                  {"nom":"Retour","txt":"Fin naturellement relâchée + étirements doux."}],
          benefices="Capillarisation, base aérobie, durabilité.",
          vigilance="Garde-la facile même en pleine forme — c'est là qu'on tue la zone grise.",
          legende=[{"c":GREEN,"l":"Facile / EF — RPE 3"}],
          coach=[{"titre":"Discipline de l'easy","texte":"Le facile te permet de pousser fort les jours de qualité. Lève le pied volontairement."}])
    if desc: d["sous"]=desc
    return d

def renfo(opt=False):
    return dict(titre="Renforcement + mobilité",type="PPG — dos, gainage, chaîne post.",sport="Renforcement",opt=opt,accent=YELLOW,fill=40,
      sous="Protéger le dos, bâtir l'économie de course.",
      metriques={"Durée":"~35 min","RPE":"5","Focus":"Dos + gainage","Type":"PPG"},
      objectif="Renforcer gainage et chaîne postérieure, mobiliser le dos, gagner en économie de course."+("" if opt else " <strong>Non négociable en phase de charge</strong> : c'est ta principale protection lombaire."),
      struct=[{"nom":"Échauffement","txt":"8 min mobilité hanches + colonne (chat-vache, ouverture de hanches)."},
              {"nom":"Corps","txt":"2-3 tours : gainage ventral 30-40 s, gainage latéral 30 s/côté, ponts fessiers 12-15, hip-hinge léger, excentrique mollet 12. Récup 30-45 s."},
              {"nom":"Retour","txt":"Mobilité lombaire + étirements fléchisseurs de hanche."}],
      benefices="Prévention du dos (ton risque n°1) et gain d'économie de course (méta-analyses du guide).",
      vigilance="Qualité d'exécution avant charge. Douleur lombaire → mobilité seule + kiné dans la boucle.",
      legende=[{"c":YELLOW,"l":"Renforcement — RPE 5"},{"c":GREEN,"l":"Mobilité — facile"}],
      coach=[{"titre":"Régularité > intensité","texte":"Deux fois 30 min valent mieux qu'une grosse séance isolée. C'est l'assiduité qui protège le dos."}])

def mobilite():
    return dict(titre="Mobilité (2ᵉ séance)",type="Mobilité",sport="Mobilité",opt=True,accent=GREEN,fill=18,
      sous="Courte séance d'entretien du dos, en plus du renfo.",
      metriques={"Durée":"~20 min","RPE":"2","Focus":"Dos / hanches","Type":"Mobilité"},
      objectif="2ᵉ touche de mobilité dans la semaine — tu as le temps, ton dos en profite. Optionnelle mais recommandée en charge.",
      struct=[{"nom":"Corps","txt":"Mobilité lombaire et hanches, étirements doux chaîne postérieure, respiration. Sans forcer."},
              {"nom":"Retour","txt":"Quelques minutes de relâchement."}],
      benefices="Entretien articulaire, prévention lombaire pendant la montée de charge.",
      vigilance="Aucune intensité. C'est de l'entretien, pas une séance.",
      legende=[{"c":GREEN,"l":"Mobilité — facile"}],
      coach=[{"titre":"Le temps est un atout","texte":"Tu as du temps en ce moment : convertis-le en récupération et prévention, pas seulement en kilomètres."}])

def pyr_hills(sec, fill=62):
    sets=[1,2,3,2,1]; reps=sum(sets); desc_rec=max(60,int(sec*1.1))
    raw=[{"nom":"Échauffement","role":"20 min progressifs jusqu'au pied de la côte + 3 lignes droites.","duree":1200,"couleur":"vert","bloc":"—","hauteur":32}]
    n=0
    for si,grp in enumerate(sets):
        for r in range(grp):
            n+=1
            raw.append({"nom":f"Montée {n}/{reps}","role":f"{sec}\" en montée, allure constante et propre.","duree":sec,"couleur":"bleu","bloc":f"S{si+1}","hauteur":86})
            raw.append({"nom":f"Descente {n}","role":"Descente rapide, on récupère en mouvement.","duree":desc_rec,"couleur":"orange","bloc":"↓","hauteur":34})
        if si<len(sets)-1:
            raw.append({"nom":"Transition","role":"Footing souple entre les blocs de la pyramide.","duree":90,"couleur":"vert","bloc":"—","hauteur":28})
    raw.append({"nom":"Retour au calme","role":"10 min souple sur le plat.","duree":600,"couleur":"vert","bloc":"—","hauteur":28})
    sg=segs(raw); tot=sg[-1]["fin"]
    return dict(titre=f"Côte pyramide 1-2-3-2-1 × {sec}\"",type="Côtes — force / économie",sport="Course à pied",opt=False,accent=ORANGE,fill=fill,
      sous="Structure pyramidale — construire et redescendre le volume intelligemment.",
      metriques={"Durée totale":mmss(tot),"Répétitions":f"{reps} (1-2-3-2-1)","Structure":"Pyramide","Allure":"vive constante","RPE":"7","Type":"Côtes"},
      objectif="Force spécifique de la foulée et économie de course par les côtes courtes — <strong>peu traumatique pour le dos</strong>, et utile aussi pour le D+ de la SaintExpress.",
      struct=[{"nom":"Échauffement","txt":"20 min facile jusqu'au pied d'une côte régulière (5-8 %) + 3 lignes droites."},
              {"nom":"Corps","txt":f"Pyramide : 1 puis 2 puis 3 puis 2 puis 1 montées de {sec}\" (9 au total), allure constante — pas à fond. Descente rapide entre chaque pour récupérer en mouvement, footing souple entre les blocs."},
              {"nom":"Retour","txt":"10 min de footing souple sur le plat."}],
      benefices="Force spécifique, raideur tendineuse utile, économie de course — un même geste répété proprement, sans l'impact de la vitesse sur plat.",
      vigilance="Monte tonique mais propre, jamais en sprint désuni. Ne surjoue pas le premier bloc : garde de la ressource pour le sommet de la pyramide (le bloc de 3).",
      legende=[{"c":GREEN,"l":"Facile / transition"},{"c":ORANGE,"l":"Montée — RPE 7-8"},{"c":BLUE,"l":"Descente — récup active"}],
      coach=[{"titre":"Comment monter","texte":"Allure constante et régulière, pas explosive. Appuis actifs, bras qui accompagnent, regard ouvert. La régularité prime sur la vitesse."},
             {"titre":"Comment descendre","texte":"Descente rapide : c'est là que tu récupères en mouvement. Laisse rouler, regarde loin, évite les freinages parasites — arrive en bas prêt à repartir."},
             {"titre":"Logique de séance","texte":"Le dur, c'est d'enchaîner les montées du bloc de 3 sans perdre la qualité. Construis intelligemment : ne te crame pas au début pour tenir le haut de la pyramide."}],
      segments=sg)

def hills(dist,dur,reps,sec,desc,fill=58):
    work=segs([{"nom":"Échauffement","role":"20 min progressifs jusqu'au pied de la côte.","duree":1200,"couleur":"vert","bloc":"—","hauteur":32}]+
      sum([[{"nom":f"Côte {i+1}/{reps}","role":f"{sec}\" en montée, tonique et propre.","duree":sec,"couleur":"bleu","bloc":f"×{reps}","hauteur":85},
            {"nom":f"Récup {i+1}","role":"Descente souple.","duree":max(60,sec),"couleur":"orange","bloc":"—","hauteur":30}] for i in range(reps)],[])+
      [{"nom":"Retour au calme","role":"10 min souple.","duree":600,"couleur":"vert","bloc":"—","hauteur":28}])
    return dict(titre=f"Côtes {reps}×{sec}\"",type="Côtes — force / économie",sport="Course à pied",opt=False,accent=ORANGE,fill=fill,
      sous=desc,metriques={"Distance":f"~{dist} km","Durée":f"~{dur} min","Allure":"vive en montée","FC":"montée haute","RPE":"7-8","Type":"Côtes"},
      objectif="Développer la force spécifique de la foulée et l'économie de course par les côtes courtes.",
      struct=[{"nom":"Échauffement","txt":"20 min facile jusqu'au pied d'une côte régulière (4-8 %)."},
              {"nom":"Corps","txt":f"{reps} × {sec}\" en montée : foulée courte, dynamique, poussée nette. Récup en redescendant souple."},
              {"nom":"Retour","txt":"10 min de footing souple sur le plat."}],
      benefices="Force spécifique, raideur tendineuse, économie de course — sans l'impact d'une séance de vitesse.",
      vigilance="Monte tonique mais propre. Descente relâchée pour épargner quadris et dos.",
      legende=[{"c":GREEN,"l":"Facile / récup"},{"c":ORANGE,"l":"Montée — RPE 7-8"}],
      coach=[{"titre":"Qualité constante","texte":"La dernière montée doit ressembler à la première."}],segments=work)

def thresh(dist,dur,reps,minutes,desc,recup=3,fill=70):
    s60=minutes>=10; pace=P_S60 if s60 else P_S30; fc=F_S60 if s60 else F_S30
    niv="Seuil 60" if s60 else "Seuil 30"; nd=("allure tenable ~60 min, proche semi" if s60 else "allure tenable ~30 min, proche 10 km")
    blk=[]
    for i in range(reps):
        blk.append({"nom":f"{niv} {i+1}/{reps}","role":f"{minutes} min à {niv.lower()} ({pace}).","duree":minutes*60,"couleur":"bleu","bloc":f"×{reps}","hauteur":88})
        if i<reps-1: blk.append({"nom":f"Récup {i+1}","role":f"{recup} min footing lent.","duree":recup*60,"couleur":"orange","bloc":"—","hauteur":30})
    work=segs([{"nom":"Échauffement","role":"20 min progressifs + 3 lignes droites.","duree":1200,"couleur":"vert","bloc":"—","hauteur":34}]+blk+[{"nom":"Retour au calme","role":"10 min souple.","duree":600,"couleur":"vert","bloc":"—","hauteur":28}])
    dur_reel=round(work[-1]["fin"]/60)  # durée recalculée depuis la vraie structure (fiabilise le "dur" saisi à la main)
    return dict(titre=f"{niv} — {reps}\u00d7{minutes} min",type="Seuil (puissance aérobie)",sport="Course à pied",opt=False,accent=VIOLET,fill=fill,
      sous=desc,metriques={"Distance":f"~{dist} km","Durée":f"~{dur_reel} min","Allure":pace,"FC":fc,"RPE":"7-8","Type":niv},
      objectif=f"Travail au <strong>{niv}</strong> ({nd}) : tenir une allure soutenue mais contrôlée. Le seuil 30 affûte le haut, le seuil 60 construit l'endurance de seuil — les deux nourrissent ta capacité à tenir l'allure marathon longtemps.",
      struct=[{"nom":"Échauffement","txt":"20 min facile + 3 lignes droites."},
              {"nom":"Corps","txt":f"{reps} \u00d7 {minutes} min à {niv.lower()} ({pace}), récup {recup} min footing lent entre les blocs. {nd[0].upper()+nd[1:]}."},
              {"nom":"Retour","txt":"10 min souple."}],
      benefices="Élévation du seuil lactique, capacité à tenir l'allure longtemps — la base de ta résistance sur marathon.",
      vigilance="Pars contrôlé : le dernier bloc à la même allure que le premier.",
      legende=[{"c":GREEN,"l":"Facile / récup"},{"c":VIOLET,"l":f"{niv} — RPE 7-8"}],
      coach=[{"titre":"Seuil 30 vs Seuil 60","texte":"Seuil 30 = ce que tu tiendrais ~30 min (vif, proche 10 km). Seuil 60 = ce que tu tiendrais ~1 h (proche semi). Deux intensités, deux effets complémentaires."},
             {"titre":"Régularité","texte":"Le seuil se court au métronome : mieux vaut un poil trop lent et régulier que trop vite et en perdition."}],segments=work)

def mp(dist,dur,blocs,km_each,desc,fill=78,warm_min=15,cool_min=10):
    blk=[]
    for i in range(blocs):
        blk.append({"nom":f"Bloc AM {i+1}/{blocs}","role":f"{km_each} km à allure marathon ({P_AM}).","duree":int(km_each*5.25*60),"couleur":"bleu","bloc":f"×{blocs}","hauteur":80})
        if i<blocs-1: blk.append({"nom":f"Récup {i+1}","role":"3 min footing.","duree":180,"couleur":"orange","bloc":"—","hauteur":30})
    work=segs([{"nom":"Échauffement","role":f"{warm_min} min facile.","duree":warm_min*60,"couleur":"vert","bloc":"—","hauteur":34}]+blk+[{"nom":"Retour au calme","role":f"{cool_min} min souple.","duree":cool_min*60,"couleur":"vert","bloc":"—","hauteur":28}])
    return dict(titre=f"Allure marathon {blocs}×{km_each} km",type="Spécifique marathon",sport="Course à pied",opt=False,accent=BLUE,fill=fill,
      sous=desc,metriques={"Distance":f"~{dist} km","Durée":f"~{dur} min","Allure":P_AM,"FC":F_AM,"RPE":"6-7","Type":"Allure marathon"},
      objectif="Ancrer l'allure marathon cible (~5:15/km) jusqu'à ce qu'elle devienne automatique et économique.",
      struct=[{"nom":"Échauffement","txt":f"{warm_min} min facile + 2 lignes droites."},
              {"nom":"Corps","txt":f"{blocs} × {km_each} km à allure marathon ({P_AM}), récup 3 min footing. Allure « juste », fluide."},
              {"nom":"Retour","txt":f"{cool_min} min souple + recharge hydrique."}],
      benefices="Automatisation de l'allure cible, efficacité à cette vitesse, confiance pour le jour J.",
      vigilance="L'allure marathon doit sembler confortable. Si elle est dure aujourd'hui, c'est un signal — on en parle.",
      legende=[{"c":GREEN,"l":"Facile / récup"},{"c":BLUE,"l":"Allure marathon — RPE 6-7"}],
      coach=[{"titre":"Le bon ressenti","texte":"À l'allure marathon tu dois pouvoir dire 3-4 mots. Plus aisé = trop lent, essoufflé = trop vite."}],segments=work)

def benchmark(fill=82):
    work=segs([{"nom":"Échauffement","role":"20 min progressifs + 4 lignes droites.","duree":1200,"couleur":"vert","bloc":"—","hauteur":34},
               {"nom":"10 km chrono","role":"Effort 10 km contrôlé : pars prudent, accélère sur le dernier tiers.","duree":2820,"couleur":"rouge","bloc":"TT","hauteur":92},
               {"nom":"Retour au calme","role":"10 min très souple.","duree":600,"couleur":"vert","bloc":"—","hauteur":28}])
    return dict(titre="Test 10 km — contre-la-montre",type="Test / recalibrage",sport="Course à pied",opt=False,accent=RED,fill=fill,
      sous="Benchmark : on mesure ta vraie forme et on recale toutes les allures.",
      metriques={"Distance":"10 km","Allure":"ton meilleur 10 km du jour","FC":"élevée","RPE":"9","Type":"Test"},
      objectif="<strong>Recalibrer tes allures cibles</strong> (marathon, seuil) sur ta forme réelle, et répéter le pacing + le carburant en condition. Idéalement sur un parcours plat et mesuré, ou un dossard local.",
      struct=[{"nom":"Échauffement","txt":"20 min facile + 4 lignes droites, bien préparé."},
              {"nom":"Corps","txt":"10 km à ton meilleur effort contrôlé. Pars prudent (1ᵉʳ km jamais le plus rapide), tiens, puis accélère sur les 3-4 derniers km si tu le peux."},
              {"nom":"Retour","txt":"10 min très souple."}],
      benefices="Une donnée fraîche qui remplace les projections de juin : on en déduit tes allures marathon et seuil exactes pour tout le bloc spécifique.",
      vigilance="Pas un jour de fatigue : place-le reposé. On débriefe le chrono ensemble pour ajuster les cibles.",
      legende=[{"c":GREEN,"l":"Facile / échauffement"},{"c":RED,"l":"10 km à fond contrôlé — RPE 9"}],
      coach=[{"titre":"Le pari de la patience","texte":"Le 10 km se gagne sur la deuxième moitié. Si le 1ᵉʳ km est ton plus rapide, tu as déjà perdu."},
             {"titre":"Ça recale tout","texte":"Ton chrono ici devient la référence : je réajuste allure marathon et seuil dessus. C'est ce qui rendra le bloc précis."}],segments=work)

def longrun(dist,dur,mp_km=0,fuel=True,desc=None,heat=False,fill=64):
    raw=[{"nom":"Échauffement","role":"15 min très souple — inclus dans le kilométrage total.","duree":900,"couleur":"vert","bloc":"—","hauteur":30}]
    base_min=dur-25-(int(mp_km*5.25) if mp_km else 0)
    if mp_km:
        raw.append({"nom":"Corps EF","role":"EF régulière, on prépare le bloc AM.","duree":base_min*60,"couleur":"vert","bloc":"1/2","hauteur":44})
        raw.append({"nom":f"Finish {mp_km} km AM","role":f"{mp_km} km à allure marathon ({P_AM}) sur fond de fatigue.","duree":int(mp_km*5.25*60),"couleur":"bleu","bloc":"AM","hauteur":78})
    elif fuel:
        raw.append({"nom":"Corps 1","role":"EF régulière. Boire toutes les 15-20 min (électrolytes).","duree":int(base_min*0.5)*60,"couleur":"vert","bloc":"1/2","hauteur":44})
        raw.append({"nom":"Gel ~1h","role":"Test gel, tolérance digestive.","duree":120,"couleur":"violet","bloc":"⛽","hauteur":62})
        raw.append({"nom":"Corps 2","role":"EF régulière, rester relâché.","duree":int(base_min*0.5)*60,"couleur":"vert","bloc":"2/2","hauteur":44})
    else:
        raw.append({"nom":"Corps","role":"EF régulière.","duree":base_min*60,"couleur":"vert","bloc":"—","hauteur":44})
    raw.append({"nom":"Retour au calme","role":"Marche + recharge.","duree":300,"couleur":"vert","bloc":"—","hauteur":28})
    vig="Pars volontairement lent : la longue se court sur la retenue. Fatigue marquée → réduis la distance mais ne supprime pas la séance. COURSE CONTINUE : pas d'arrêt prolongé, ravitaillement en marchant si besoin — c'est précisément ce que le marathon ViaRhôna (56 min d'arrêts) n'a pas entraîné, et ce qui manquera le jour J."
    if heat: vig+=" Été : par forte chaleur, cours à la FC/sensation (pas au chrono) et renforce l'hydratation/électrolytes."
    return dict(titre=("Sortie longue + allure marathon" if mp_km else "Sortie longue endurance"),type=("Sortie longue spécifique" if mp_km else "Sortie longue"),sport="Course à pied",opt=False,accent=(BLUE if mp_km else ORANGE),fill=fill,
      sous=desc or ("La séance clé — endurance + carburant."+(f" Finish {mp_km} km AM." if mp_km else "")),
      metriques={"Distance":f"~{dist} km tout compris","Durée":f"~{dur} min","Allure":(P_EF+" + AM" if mp_km else P_EF),"FC":(F_EF+" puis "+F_AM if mp_km else F_EF),"RPE":("5-6" if mp_km else "4-5"),"Type":"Longue"},
      objectif=(("Endurance + spécificité : "+f"{mp_km} km à allure marathon en fin de longue" if mp_km else "Reconstruire/entretenir l'endurance fondamentale")+", et roder le carburant. <strong>Séance clé, non optionnelle.</strong>"),
      struct=[{"nom":"Échauffement","txt":"15 min très souples."},
              {"nom":"Corps","txt":(f"{dist} km AU TOTAL : les {dist-mp_km} premiers en EF régulière, puis les {mp_km} DERNIERS à allure marathon ({P_AM}) sur fond de fatigue. Enchaînement direct, sans pause entre les deux." if mp_km else f"{dist} km à allure facile régulière, plat à légèrement vallonné.")+" Nutrition : boire toutes les 15-20 min, électrolytes dès le départ, 1 gel/30-40 min au-delà d'1h30."},
              {"nom":"Retour","txt":"Marche 5 min + étirements, recharge hydrique/électrolytes."}],
      benefices="Endurance, oxydation des graisses, résistance à la fatigue"+(", tenue de l'allure cible sur fin de course" if mp_km else "")+" — et rodage du carburant.",
      vigilance=vig,
      legende=[{"c":GREEN,"l":"Facile / EF"}]+([{"c":BLUE,"l":"Allure marathon"}] if (mp_km or fuel) else []),
      coach=([{"titre":"Le vrai repère : ta FC sur le bloc AM","texte":"Sur le marathon du 23/07 tu as tenu 5:15/km, mais à FC 163-167 — trop haut pour durer 3h45. L'objectif d'ici octobre est de tenir 5:20/km autour de 155-158. Si tu dépasses 165 sur le bloc, l'allure est encore trop rapide pour ton niveau du moment : ralentis à 5:25 et note-le. C'est cette FC, pas le chrono, qui dira si 3h45 est acquis."}] if mp_km else [])+[{"titre":"Le carburant, ta priorité","texte":"La longue est ton labo nutrition. Note ce que tu absorbes et ton ressenti — on cale la stratégie marathon dessus."}],
      segments=segs(raw))

def trailsess(dist,dur,desc,focus,fill=60):
    return dict(titre="Sortie trail — "+desc,type="Spécifique trail",sport="Trail",opt=False,accent=TEAL,fill=fill,
      sous=focus,metriques={"Distance":f"~{dist} km","Durée":f"~{dur} min","Allure":P_TRAIL,"FC":"à l'effort","RPE":"5-6","Type":"Trail"},
      objectif="Réveiller les qualités de trail (montée, descente technique, pied) avant la SaintExpress, sans chercher la performance.",
      struct=[{"nom":"Échauffement","txt":"15 min facile sur plat avant le relief."},
              {"nom":"Corps","txt":"Parcours vallonné : montées en marche active/course selon la pente, descentes travaillées (regard loin, cadence, relâchement). Une portion de nuit si possible."},
              {"nom":"Retour","txt":"Footing souple + étirements."}],
      benefices="Renforcement spécifique descente, aisance technique, adaptation au nocturne — spécifique SaintExpress.",
      vigilance="Descentes contrôlées (quadris + dos). La technique prime sur la vitesse.",
      legende=[{"c":GREEN,"l":"Facile"},{"c":TEAL,"l":"Trail / relief"}],
      coach=[{"titre":"La descente, c'est gratuit","texte":"On gagne du temps en descente sans coût cardiaque — à condition de l'avoir travaillée. Lâche les freins en sécurité."}])

def deraille_prep(dist,dur,fill=66):
    raw=[{"nom":"Échauffement","role":"15 min très souple sur plat avant le relief.","duree":900,"couleur":"vert","bloc":"—","hauteur":32},
         {"nom":"Tempo vallonné 1/3","role":"12 min à l'effort course (vallonné) — gère à la sensation, pas au chrono.","duree":720,"couleur":"bleu","bloc":"×3","hauteur":80},
         {"nom":"Récup 1","role":"3 min footing souple.","duree":180,"couleur":"orange","bloc":"—","hauteur":30},
         {"nom":"Gel test ~35 min","role":"1er gel + gorgées électrolytes — on rode le protocole Déraille.","duree":120,"couleur":"violet","bloc":"⛽","hauteur":60},
         {"nom":"Tempo vallonné 2/3","role":"12 min à l'effort course, relâché en descente.","duree":720,"couleur":"bleu","bloc":"×3","hauteur":80},
         {"nom":"Récup 2","role":"3 min footing souple.","duree":180,"couleur":"orange","bloc":"—","hauteur":30},
         {"nom":"Gel test ~70 min","role":"2e gel + électrolytes — vérifie la tolérance digestive à l'effort.","duree":120,"couleur":"violet","bloc":"⛽","hauteur":60},
         {"nom":"Tempo vallonné 3/3","role":"10 min à l'effort course, finis propre.","duree":600,"couleur":"bleu","bloc":"×3","hauteur":80},
         {"nom":"Retour au calme","role":"10 min souple + recharge.","duree":600,"couleur":"vert","bloc":"—","hauteur":28}]
    sg=segs(raw); tot=sg[-1]["fin"]
    return dict(titre="Prépa Déraille — tempo vallonné",type="Spécifique trail (vallonné)",sport="Trail",opt=False,accent=TEAL,fill=fill,
      sous="Répétition grandeur nature : effort course sur le relief + protocole carburant/électrolytes.",
      metriques={"Distance":f"~{dist} km","Durée":mmss(tot),"Allure":"à l'effort (vallonné)","FC":"jusqu'à Z3","RPE":"6","Type":"Spécifique trail"},
      objectif="Préparer les jambes au relief roulant de la Déraille <strong>et roder le protocole nutrition</strong> (gels + électrolytes) qui t'a manqué à La Circaète. C'est ta vraie répétition avant le 5 juillet.",
      struct=[{"nom":"Échauffement","txt":"15 min facile sur plat, sans forcer, avant d'attaquer le relief."},
              {"nom":"Corps","txt":"3 blocs (12-12-10 min) à l'effort course sur terrain vallonné, récup 3 min footing entre les deux premiers. <strong>À l'effort, pas au chrono</strong> : en montée tu lèves le pied, en descente tu relâches. Cale 1 gel + électrolytes vers la 35ᵉ puis la 70ᵉ minute, exactement comme le jour J."},
              {"nom":"Retour","txt":"10 min souple + recharge hydrique/électrolytes."}],
      benefices="Spécificité du relief roulant, gestion d'effort en montée/descente, et surtout rodage du carburant — l'estomac s'entraîne autant que les jambes.",
      vigilance="Le but n'est pas la vitesse mais la fluidité de l'effort et la digestion des gels. Si l'estomac proteste, note-le : on ajuste avant la course.",
      legende=[{"c":GREEN,"l":"Facile / récup"},{"c":TEAL,"l":"Effort course — RPE 6"},{"c":VIOLET,"l":"Gel / électrolytes"}],
      coach=[{"titre":"L'effort commande, pas la montre","texte":"Sur le vallonné, l'allure ne veut rien dire. Tu cales un effort « course soutenable » et tu laisses le terrain dicter la vitesse — c'est exactement la compétence à avoir le 5 juillet."},
             {"titre":"Le test qui compte vraiment","texte":"La Circaète est tombée sur l'électrolyte. Ici tu valides le protocole dans les jambes, pas sur le papier : 2 gels, électrolytes en continu, et tu observes."}],
      segments=sg)

def race(kind):
    if kind=="marathon":
        return dict(titre="MARATHON DE NICE",type="Course — Objectif A",sport="Course à pied",opt=False,accent=ORANGE,fill=100,
          sous="42,195 km · plat & roulant · cible 3h42 (~5:15/km).",
          metriques={"Distance":"42,195 km","Cible":"3h42","Allure":"5:15/km","FC":"152-163","RPE":"8-9","Type":"Marathon"},
          objectif="Concrétiser la prépa : <strong>partir prudent, négatif split, carburant carré</strong>. La course se gagne dans la patience des 30 premiers km.",
          struct=[{"nom":"Plan d'allure","txt":"km 0-10 : 5:18-5:20 (retenu, ça doit sembler facile). km 10-32 : 5:15. km 32-42 : si les sensations sont là, descends vers 5:10."},
                  {"nom":"Carburant","txt":"1 gel toutes les 35-40 min dès la 40ᵉ min, boire à chaque ravito, électrolytes réguliers. Exécute le plan testé en prépa, n'improvise pas."},
                  {"nom":"Mental","txt":"Découpe en 3 : croisière (0-32), travail (32-38), cœur (38-42). Le vrai marathon commence au 32ᵉ."}],
          benefices="L'aboutissement du bloc. Un marathon bien géré = un chrono ET une expérience qui servira la suite.",
          vigilance="Piège n°1 du premier marathon : partir trop vite parce qu'on se sent bien. Tiens l'allure cible sur la première moitié.",
          legende=[{"c":BLUE,"l":"Allure marathon"},{"c":ORANGE,"l":"Course"}],
          coach=[{"titre":"Discipline des 10 premiers km","texte":"Si à mi-course tu te dis « je me retiens trop », c'est gagné. Héroïque au 15ᵉ = tu paieras au 35ᵉ."},
                 {"titre":"Le carburant ne se négocie pas","texte":"Même sans faim/soif : tu manges et bois au plan. La défaillance se prévient une heure avant de la sentir."}])
    if kind=="deraille":
        return dict(titre="TRAIL DÉRAILLE — LAC DES SAPINS",type="Trail — Objectif C",sport="Trail",opt=False,accent=TEAL,fill=100,
          sous="24 km · ~900 m D+ · vallonné, roulant · course plaisir & test nutrition.",
          metriques={"Distance":"24,05 km","D+":"~900 m","Allure":"à l'effort","FC":"gérée","RPE":"6-7","Type":"Trail vallonné"},
          objectif="Course <strong>plaisir</strong> et laboratoire nutrition grandeur nature. Aucun enjeu chrono : on teste le protocole carburant/électrolytes sur 2h15-2h30 en conditions chaudes — la leçon de La Circaète appliquée.",
          struct=[{"nom":"Gestion","txt":"Pars dans ta zone de confort : sur 900 m D+ roulant, c'est l'effort qui se gère, pas l'allure. Marche les raidillons s'il y en a, relâche en descente. FC sous 160-165 sur les 5 premiers km, ne te fais pas emporter par le départ de masse."},
                  {"nom":"Carburant — LE point","txt":"Électrolytes dès le km 5 (pas km 15 comme à La Circaète), 1 gel toutes les 40-45 min dès la 40ᵉ minute. Bois à chaque ravito. En juillet, le froid ne masquera pas la soif : c'est la chaleur qui te piège, anticipe."},
                  {"nom":"Plaisir","txt":"C'est une course « pour voir » : beaujolais vert, sentiers techniques, bonne ambiance. Savoure, observe ton corps, ramène des données propres pour Nice."}],
          benefices="Un vrai test de ta gestion nutrition/électrolytes en course, sans l'enjeu d'un objectif — exactement le rodage qui manquait après La Circaète.",
          vigilance="Ton côté compétiteur va te chatouiller sur les sentiers : tiens la consigne « plaisir + test ». Une Déraille bien gérée nourrit Nice ; un forcing inutile entame ta reprise.",
          legende=[{"c":GREEN,"l":"Gestion / facile"},{"c":TEAL,"l":"Course trail — effort"}],
          coach=[{"titre":"La course est un entraînement déguisé","texte":"Tu n'es pas là pour un chrono mais pour valider ton estomac sous contrainte. Si tu finis sans coup de moins-bien électrolytique, c'est une victoire qui vaut de l'or pour Nice."},
                 {"titre":"Électrolytes : la leçon retenue","texte":"La Circaète est tombée là-dessus. Aujourd'hui tu prouves que le correctif fonctionne — dès le km 5, en continu, sans attendre la sensation."}])
    if kind=="runinlyon":
        return dict(titre="RUN IN LYON — SEMI-MARATHON",type="Course — Objectif intermédiaire",sport="Course à pied",opt=False,accent="#F4561D",fill=100,
          sous="21,097 km · départ 8h30 Bellecour · groupe 1h50 (5:13/km) · test grandeur nature de l'allure Nice.",
          metriques={"Distance":"21,097 km","Cible":"1h50 (groupe)","Allure":"5:13-5:20/km","FC":"Zone marathon","RPE":"6-7","Type":"Semi-marathon officiel"},
          objectif="Pas un objectif chrono en soi : <strong>un test grandeur nature de la discipline d'allure marathon</strong>, en dossard, en groupe, à 5 semaines de Nice. Courir calé sur deux amis visant 1h50 (5:13/km) plutôt que de gérer seul — exactement le mécanisme qui a fonctionné cette saison face à l'envie d'accélérer ou de doubler.",
          struct=[{"nom":"Consigne n°1","txt":"Coller au groupe 1h50 tant que l'effort reste maîtrisé. Si à un moment ça commence à tirer, les laisser filer plutôt que de forcer pour rester avec eux jusqu'au bout — l'objectif est de finir propre à allure marathon, pas de suivre le groupe coûte que coûte."},
                  {"nom":"Le vrai enjeu","txt":"Tenir 5:13-5:20/km sans dérive, dans l'ambiance d'une course officielle avec dossard et concurrents à doubler — le terrain exact où le réflexe d'accélération s'est déclenché le plus souvent cette saison (seuil du 02/09 notamment)."},
                  {"nom":"Carburant","txt":"1h50 ne nécessite pas de plan nutritionnel lourd : hydratation aux ravitos, un gel possible vers 45-50 min si besoin. L'enjeu est la discipline d'allure, pas le carburant."}],
          benefices="Le meilleur test possible avant Nice : l'allure marathon exacte, tenue sur 21 km, en conditions de course réelle (dossard, foule, concurrents), avec un repère humain fiable (le groupe 1h50).",
          vigilance="5:13/km est légèrement sous le bas de la fourchette (5:15-5:20). Si ça se sent bien les 10 premiers km, tant mieux — information utile pour Nice. Si ça commence à tirer, lâcher le groupe est la bonne décision, pas un échec.",
          legende=[{"c":BLUE,"l":"Allure marathon"},{"c":GREEN,"l":"Groupe 1h50"}],
          coach=[{"titre":"Le dossard change la donne, pour de vrai","texte":"Toute la saison a montré qu'une alerte technique seule ne suffit pas face à l'envie de doubler. Aujourd'hui le test se fait en conditions réelles de course, pas à l'entraînement — c'est la version la plus exigeante et la plus utile de ce test."},
                 {"titre":"Lâcher le groupe n'est pas un échec","texte":"Si l'allure de tes amis devient intenable, les laisser partir et finir à ton rythme est la décision d'un coureur qui gère sa course, pas d'un coureur qui abandonne."}])
    return dict(titre="SAINTEXPRESS 45 km",type="Course — Objectif B",sport="Trail nocturne",opt=False,accent=RED,fill=100,
      sous="45 km · 900 m D+ · nocturne, hivernal · au plaisir.",
      metriques={"Distance":"45 km","D+":"~900 m","Allure":P_TRAIL,"FC":"gérée","RPE":"7-8","Type":"Trail nuit"},
      objectif="Profiter, sur les acquis du marathon. <strong>Pas un deuxième objectif chrono</strong> : gestion, plaisir, expérience du nocturne hivernal.",
      struct=[{"nom":"Gestion","txt":"Pars très prudent — tu as un marathon dans les jambes (3 semaines). Marche les côtes raides, mange tôt, savoure la nuit."},
              {"nom":"Matériel","txt":"Frontale (+ piles), couches chaudes, gants, de quoi te couvrir aux ravitos. Froid/boue/gel possibles."},
              {"nom":"Carburant","txt":"Plus long que le marathon : mange dès le départ, solide + liquide, électrolytes en continu. Le froid masque la soif."}],
      benefices="Une belle aventure de fin de saison, l'expérience du trail nocturne, un test de ta gestion longue distance.",
      vigilance="Ton côté compétiteur va te tirer : garde la tête froide. Une SaintExpress « au plaisir » réussie vaut mieux qu'un forcing qui plombe ta fin d'année.",
      legende=[{"c":TEAL,"l":"Trail / gestion"},{"c":RED,"l":"Course nuit"}],
      coach=[{"titre":"Au plaisir, vraiment","texte":"Tu cours avec un ami : cale-toi sur le partage, pas sur le chrono. C'est le cadeau de fin de saison."}])

WEEKS={}
def W(n,ss): WEEKS[n]=ss
# Reprise
W(25,[ef(10,65,strides=True), ef(9,55), mp(12,72,1,6,"Premier contact sérieux avec l'allure marathon — 6 km à tenir proprement.",cool_min=25), longrun(18,110,heat=True,desc="Reconstruire l'endurance + roder le carburant."), ef(10,65)])
# Allègement + prépa Déraille (course plaisir B, 5 juillet)
W(26,[ef(11,66,strides=True), ef(9,55), deraille_prep(15,90), renfo(opt=True)])
# Semaine de course — Trail Déraille au Lac des Sapins (dim. 5 juillet)
W(27,[ef(8,48,strides=True), ef(7,45,recovery=True), ef(6,38,recovery=True), race("deraille")])
W(28,[ef(6,38,recovery=True), ef(8,50,recovery=True), ef(10,60), longrun(12,72,fuel=False,heat=True,desc="Sortie tranquille — pas de finish AM, juste du volume facile pour réactiver."), renfo(opt=True)])
W(29,[ef(11,66), thresh(12,68,2,8,"Découverte du seuil : 2 blocs courts, reprise progressive après la récup."), ef(10,60,strides=True), longrun(18,108,mp_km=5,heat=True,desc="Longue qui reprend du volume, avec 5 km à allure marathon en fin."), renfo(opt=False)])
W(30,[ef(12,72), thresh(13,75,3,8,"Seuil consolidé, 3 blocs."), pyr_hills(45), longrun(24,145,mp_km=6,heat=True), renfo(opt=False)])
W(31,[ef(11,66,strides=True), benchmark(), ef(10,60), longrun(20,120,heat=True,desc="Longue facile après le test."), renfo(opt=False)])
# Seuil & pré-USA
W(32,[mp(12,70,3,2,"3×2 km à 5:20/km : travail de RETENUE, ne jamais descendre sous 5:15.",fill=52,warm_min=18,cool_min=12), ef(8,48), ef(9,50,strides=True), longrun(16,95,heat=True), renfo(opt=False), mobilite()])
W(33,[ef(11,66), thresh(12,70,2,10,"Seuil allégé avant le pic."), ef(10,60,strides=True), longrun(18,108,heat=True,desc="Récup avant le gros bloc."), renfo(opt=True)])
W(34,[ef(12,72), thresh(14,82,3,12,"Pic seuil pré-voyage.",recup=3), ef(12,72), longrun(28,170,mp_km=12,heat=True,desc="Longue 28 km dont 12 à allure marathon — c'est le GATE de la séance reine : si elle passe bien, on validera 14 km AM en S42."), renfo(opt=False), mobilite()])
W(35,[ef(12,72,strides=True), thresh(11,66,2,8,"Seuil court, on lève le pied."), ef(10,60), longrun(18,108,heat=True,desc="On prépare le corps au déload du voyage."), renfo(opt=True)])
# USA
W(36,[ef(10,60,recovery=True), ef(10,62), ef(10,62), trailsess(12,90,"randos & sentiers US","Temps de pied en montagne, à l'effort libre.")])
W(37,[ef(9,55,recovery=True), ef(9,55), trailsess(12,90,"randos & sentiers US","Profiter du relief des parcs, sans structure."), ef(8,50)])
W(38,[ef(9,55,recovery=True), ef(9,55), ef(10,62), trailsess(10,75,"randos & sentiers US","Entretien aérobie, zéro pression.")])
W(39,[ef(8,50,recovery=True), ef(10,62), ef(11,66,strides=True), longrun(16,100,fuel=False,desc="Retour : remise en route, on réveille la longue.")])
# Bloc marathon (re-construction + 1 grosse qualité/sem + longues plafonnées)
W(40,[ef(11,66), thresh(13,72,2,10,"Relance DOUCE du seuil après le voyage.",recup=3), ef(6,35,opt=True,recovery=True,desc="Allégée sur decision de Loic : 3 jours de course d'affilee, fatigue signalee, Run In Lyon dimanche en cible allure marathon. Tres facile ou repos complet selon la sensation du matin."), race("runinlyon"), renfo(opt=False)])
W(41,[ef(12,72), mp(16,95,3,4,"3×4 km AM — LE gros stimulus spécifique de la semaine."), ef(12,72), longrun(26,150,fuel=True,desc="Longue en ENDURANCE pure (la qualité est déjà sur la séance AM)."), renfo(opt=False)])
W(42,[ef(12,72), ef(12,72,strides=True), ef(11,66), longrun(30,185,mp_km=14,desc="LA séance reine : 30 km dont 14 à allure marathon. Seul gros stimulus de la semaine — à valider selon S34."), renfo(opt=False), mobilite()])
W(43,[ef(12,72), mp(16,90,2,6,"2×6 km AM — dernier gros bloc spécifique."), ef(11,66,strides=True), longrun(22,130,desc="Dernière longue, en endurance, on commence à fraîchir."), renfo(opt=False)])
# Affûtage progressif
W(44,[ef(10,60), thresh(11,60,3,6,"Rappels de seuil courts : on garde le jus, le volume baisse."), ef(9,55,strides=True), longrun(16,95,mp_km=4,desc="Longue courte avec rappel d'allure."), renfo(opt=True)])
W(45,[ef(8,48,strides=True), mp(8,48,3,1,"Activation : 3×1 km AM, jambes vives."), ef(6,38,recovery=True), race("marathon")])
# Transition & bascule trail
W(46,[ef(5,35,recovery=True), ef(7,45,recovery=True), ef(8,50), renfo(opt=True)])
W(47,[ef(10,60), trailsess(14,110,"relief & descente","Réveil trail : montées/descentes, technique."), ef(11,66,strides=True), trailsess(18,140,"longue trail nocturne","Sortie longue trail, portion de nuit pour la SaintExpress.")])
# SaintExpress
W(48,[ef(8,50), trailsess(10,75,"activation nocturne","Mise en jambe trail + frontale, court."), ef(6,38,recovery=True), race("saintexpress")])
# Régénération
W(49,[ef(8,50,recovery=True), ef(10,62), ef(12,75,desc="Course libre, sans montre si tu veux.")])
W(50,[ef(10,62,strides=True), ef(11,66), ef(12,75), longrun(16,100,fuel=False,desc="On réveille doucement la longue.")])
W(51,[ef(11,66,strides=True), thresh(11,64,2,8,"Première qualité de la base d'hiver."), ef(12,72), longrun(18,108,fuel=False)])
W(52,[ef(10,62,recovery=True), ef(11,66,strides=True), ef(12,75), renfo(opt=True)])
W(53,[ef(9,55,recovery=True), ef(11,66), ef(12,75,desc="Bilan de saison, cap vers 2027.")])

def rpe_num(s):
    r=s["metriques"].get("RPE","")
    if not r or r=="course": return 8.0
    nums=[float(x) for x in re.findall(r"\d+\.?\d*", r)]
    return round(sum(nums)/len(nums),1) if nums else 5.0
CLASSIQUE={"EF aérobie","EF + technique","Récupération active","PPG — dos, gainage, chaîne post.","Mobilité","Sortie longue"}
def cat_of(s): return "classique" if s["type"] in CLASSIQUE else "specifique"

import re as _re
def _km(s):
    m=_re.search(r"(\d+)", s.get("metriques",{}).get("Distance",""))
    return int(m.group(1)) if m else 99
def assign_shoes(sessions, weeknum):
    # CLIF (HOKA Clifton 10) retiree de la rotation le 27/07 : delamination de
    # semelle, trou dans le mesh, mousse tassee -- constate sur photos. Avec la
    # gene plantaire de Loic, cette paire aggrave le risque au lieu de le
    # proteger. La retraite avait ete faite seance par seance (overrides
    # manuels), jamais a la racine : cette fonction continuait de la proposer
    # dans sa rotation EASY, et elle est ressortie sur la fiche du 06/08.
    # Deux Novablast 5 coexistent au parc : la J (709 km, en fin de zone) et
    # la V (56 km). "ASICS Novablast 5" sans suffixe etait donc ambigu et
    # prescrit tel quel sur 23 seances a venir : impossible de savoir laquelle
    # chausser. NOVA designe desormais explicitement la V, la paire recente.
    # (La constante CLIF portait par ailleurs un nom trompeur : elle n'a
    # jamais contenu de Clifton.)
    MAGIC="ASICS Magic Speed 4";NOVA="ASICS Novablast 5 V";CLIF="ASICS Novablast 5 V";GEL="ASICS Gel Pulse 16";CASC="Brooks Cascadia 19"
    n=len(sessions);cats=[]
    for s in sessions:
        t=s["type"]
        if any(k in t for k in ["Seuil","Spécifique marathon","Puissance aérobie","Test"]):cats.append("MAGIC")
        elif "Sortie longue" in t:cats.append("NOVA")
        elif ("trail" in t.lower()) or ("Objectif B" in t):cats.append("CASC")
        elif "Objectif A" in t:cats.append("MAGIC")
        elif ("PPG" in t) or ("Mobilité" in t):cats.append("NONE")
        else:cats.append("EASY")
    fixed=[{"MAGIC":MAGIC,"NOVA":NOVA,"CASC":CASC,"NONE":None}.get(c) for c in cats]
    forced={}
    if weeknum%3==0:
        elig=[i for i,c in enumerate(cats) if c=="EASY" and _km(sessions[i])<=10 and "Côtes" not in sessions[i]["type"]]
        if elig: forced[min(elig,key=lambda i:_km(sessions[i]))]=GEL
    best=[None]
    def rec(i,acc,last_rot):
        if i==n: best[0]=acc[:]; return True
        c=cats[i]; prev=acc[i-1] if i>0 else None
        if c!="EASY" or i in forced:
            sh=forced.get(i, fixed[i])
            if sh is not None and prev is not None and sh==prev: return False
            acc.append(sh)
            if rec(i+1,acc,last_rot): return True
            acc.pop(); return False
        order=[CLIF,NOVA] if last_rot!=CLIF else [NOVA,CLIF]
        for o in order:
            if prev is not None and o==prev: continue
            acc.append(o)
            if rec(i+1,acc,o): return True
            acc.pop()
        return False
    if not rec(0,[],None):
        acc=[];last=None
        for i,c in enumerate(cats):
            if c!="EASY": acc.append(fixed[i]); continue
            o=NOVA if last==CLIF else CLIF; acc.append(o); last=o
        best[0]=acc
    return best[0]
import re as _re2
def _duree_min(s):
    if s.get("segments"):
        return s["segments"][-1]["fin"]/60
    txt=" ".join(str(v) for v in s.get("metriques",{}).values())
    m=_re2.search(r"(\d+)\s*h\s*(\d+)?", txt)
    if m: return int(m.group(1))*60+int(m.group(2) or 0)
    m=_re2.search(r"~?(\d+)\s*min", txt)
    if m: return int(m.group(1))
    return 0
def nutrition_for(s):
    t=s["type"]; mins=_duree_min(s); titre=s.get("titre","")
    if "Objectif C" in t:
        return {"titre":"Protocole course Déraille — LE test grandeur nature","items":[
            ("💧 Hydratation","flasques pleines au départ, recharge à chaque ravito — ne jamais attendre la soif"),
            ("🧂 Électrolytes","dès le km 5 et en continu — c'est précisément ce qu'on corrige après La Circaète"),
            ("⚡ Gels","1 gel toutes les 40-45 min dès la 40ᵉ min, aux produits déjà testés (mêmes marques que Nice)"),
            ("🎯 Cible","50-70 g de glucides/h sur 2h15-2h30 — note tout, on en tire le protocole définitif de Nice")]}
    if "Prépa Déraille" in titre:
        return {"titre":"Répétition nutrition — avant la Déraille","items":[
            ("💧 Hydratation","emporte le gilet, bois toutes les 15-20 min sans attendre la soif"),
            ("🧂 Électrolytes","dans la flasque dès le départ — on installe l'automatisme qui a manqué à La Circaète"),
            ("⚡ Gels","1er gel vers 35 min, 2e vers 70 min — exactement les produits du jour J"),
            ("🎯 Cible","teste la tolérance digestive à l'effort : c'est la vraie raison de cette séance")]}
    if "Objectif A" in t:
        return {"titre":"Protocole course — rodé à l'identique en S42-S43","items":[
            ("💧 Hydratation","2-3 gorgées à chaque ravito (tous les 5 km), sans sauter le premier"),
            ("🧂 Électrolytes","pastille dans le bidon de départ + capsules si chaleur"),
            ("⚡ Gels","1 gel 15 min avant le départ, puis 1 toutes les 30-35 min dès le km 8"),
            ("🎯 Cible","60-90 g de glucides/heure — exactement ce qui a été validé à l'entraînement")]}
    if "Objectif B" in t:
        return {"titre":"Protocole trail nocturne","items":[
            ("💧 Hydratation","flasques pleines au départ, recharge à chaque ravito"),
            ("🧂 Électrolytes","systématique — la nuit masque la transpiration"),
            ("⚡ Carburant","mix gels + solide (45 km = trop long pour du 100 % gel)"),
            ("🎯 Cible","50-70 g/h, plus modeste qu'au marathon : l'intensité est plus basse")]}
    if "Sortie longue spécifique" in t or ("Spécifique marathon" in t and mins>=90):
        return {"titre":"Répétition générale nutrition course","items":[
            ("💧 Hydratation","bidons ou flasques, boire toutes les 15-20 min sans attendre la soif"),
            ("🧂 Électrolytes","oui — même protocole que prévu à Nice"),
            ("⚡ Gels","1er gel à 40-45 min, puis toutes les 30-35 min, aux mêmes marques que le jour J"),
            ("🎯 Cible","60-90 g de glucides/h — c'est un entraînement de l'estomac autant que des jambes")]}
    if "Sortie longue" in t and mins>=150:
        return {"titre":"Longue distance — protocole complet","items":[
            ("💧 Hydratation","emporter 500 ml minimum, plus si chaleur"),
            ("🧂 Électrolytes","recommandé au-delà de 2 h, indispensable l'été"),
            ("⚡ Gels","1er à 45 min, puis toutes les 35-40 min"),
            ("🎯 Cible","40-60 g de glucides/h — l'occasion de roder produits et tolérance digestive")]}
    if "Sortie longue" in t and mins>=90:
        return {"titre":"Sortie longue — les bonnes habitudes","items":[
            ("💧 Hydratation","emporter de l'eau (flasque ou ceinture), boire régulièrement"),
            ("🧂 Électrolytes","utile si chaleur ou si tu transpires beaucoup"),
            ("⚡ Gels","1 gel vers 50-60 min suffit à ce format"),
            ("🎯 Cible","30-45 g de glucides/h — on construit l'habitude, pas la performance")]}
    if "trail" in t.lower() and mins>=90:
        return {"titre":"Trail long — autonomie","items":[
            ("💧 Hydratation","flasques dans le gilet, prévoir point d'eau si > 2 h"),
            ("🧂 Électrolytes","oui — le D+ fait transpirer plus qu'il n'y paraît"),
            ("⚡ Carburant","gels + un solide (barre) pour tester en conditions SaintExpress"),
            ("🎯 Cible","40-60 g/h dès que la sortie dépasse 1h30")]}
    if mins>=90:
        return {"titre":"Séance exigeante > 1h30","items":[
            ("💧 Hydratation","emporter de l'eau, surtout par temps chaud"),
            ("🧂 Électrolytes","optionnel, utile si forte chaleur"),
            ("⚡ Gels","1 gel à mi-séance peut soutenir la qualité des derniers blocs"),
            ("🎯 Cible","20-40 g/h suffisent — l'eau reste l'essentiel")]}
    return None

SEANCES_BY_WEEK={}
for n,ss in WEEKS.items():
    arr=[]
    for i,s in enumerate(ss):
        s=dict(s); s["num"]=i+1; s["id"]=i+1; s["rpe"]=rpe_num(s); s["cat"]=cat_of(s); s["realise"]={"statut":"a_faire"}; arr.append(s)
    for s,sh in zip(arr, assign_shoes(arr,n)): s["chaussure"]=sh
    for s in arr: s["nutrition"]=nutrition_for(s)
    date_for(arr, n)
    if n==25:
        arr[3]["date"]="2026-06-18"   # sortie longue avancée au jeudi (départ vendredi chez parents)
        arr[4]["opt"]=True
        arr[4]["date"]="2026-06-19"   # couru vendredi 19 juin chez les parents (anticipé d'un jour)
        arr[4]["realise"]={"statut":"fait","km":10.03,"temps":"59:30","allure":"5:56/km","fc_moy":144,"fc_max":165,"re":79,"cadence":174,"elevation_gain":38,"rpe_ressenti":4,
          "commentaire":"10 km en 59:30 · départ 7h25 chez les parents · FC 144/165 · Clifton 10 · 0 PR.",
          "pr":0,"ach":0,
          "revue":_REVUE_FICHIER}

        arr[3]["realise"]={"statut":"fait","km":16.05,"temps":"1h28:33","allure":"5:31/km · dernier km 4:58","fc_moy":151,"fc_max":171,"re":156,"cadence":173,"elevation_gain":52,"rpe_ressenti":6,
          "commentaire":"16 km en 1h28m33 — 13,5 km à allure constante puis fast finish progressif (5:16 → 5:01 → 4:58/km). Départ 8h, canicule. TA 500ml + gel caféiné 50ᵉ min. 5 PRs.",
          "pr":5,"ach":6,"pr_detail":["You are my best view","Quais de Saône S-N","LY Joffre/Plessier tunnel côté Saône","LY Plessier/Joffre rive gauche","darse confluence nord"],
          "revue":_REVUE_FICHIER}

        _f={1:"fit/S25-1-footing-lignes.fit",2:"fit/S25-2-footing-facile.fit",3:"fit/S25-3-allure-marathon.fit",4:"fit/S25-4-sortie-longue.fit"}
        for s in arr: s["fit"]=_f.get(s["num"])
        arr[0]["realise"]={"statut":"fait","km":10.25,"temps":"1h00","allure":"5:51/km","fc_moy":143,"fc_max":173,"re":69,"cadence":171,"elevation_gain":43,"rpe_ressenti":3,
          "commentaire":"Footing facile 10 km en 1h + 6 lignes droites de 100 m (km 9-10 plus rapides).",
          "pr":0,"ach":2,"pr_detail":["Segment Pont de la Guillotière","Segment Antonin Poncet & Pont de la Gui"],
          "revue":_REVUE_FICHIER}
        arr[2]["realise"]={"statut":"fait","km":10.14,"temps":"54:10","allure":"5:14/km (bloc AM)","fc_moy":165,"fc_max":181,"re":169,"cadence":169,"elevation_gain":35,"rpe_ressenti":7,
          "commentaire":"6 km AM à 5:14/km de moyenne. Conditions extrêmes : midi, 30°C, gueule de bois. Séance écourtée à 10 km (vs 12 prévus) — décision sage. 4 PRs de segment au passage.",
          "pr":4,"ach":4,"pr_detail":["Pont Raymond Barre","Quai Rambaud S-N","darse Confluence","Dernier km Marathon de Lyon"],
          "revue":_REVUE_FICHIER}
        arr[1]["realise"]={"statut":"fait","km":10.14,"temps":"1h00","allure":"5:56/km","fc_moy":140,"fc_max":167,"re":58,"cadence":173,"elevation_gain":40,"rpe_ressenti":3,
          "commentaire":"Footing facile 10,1 km en 1h pile, allure régulière ~5:56/km le long des berges. Effort relatif 58 (plus bas que S25-1) — un vrai easy.",
          "pr":0,"ach":0,"pr_detail":[],
          "revue":_REVUE_FICHIER}
    elif 26<=n<=53:
        _FT={"Seuil (puissance aérobie)":"seuil","Spécifique marathon":"allure-marathon",
             "Sortie longue":"sortie-longue","Sortie longue spécifique":"sortie-longue",
             "Spécifique trail (vallonné)":"deraille",
             "Côtes — force / économie":"cotes","Test / recalibrage":"test-10km"}
        for s in arr:
            _sl=_FT.get(s["type"])
            if _sl: s["fit"]=f"fit/S{n}-{s['num']}-{_sl}.fit"
    if n==26:
        arr[0]["date"]="2026-06-22"
        arr[0]["chaussure"]="Novablast 5 J"
        arr[0]["realise"]={"statut":"fait","km":11.26,"temps":"1h06","allure":"5:53/km","fc_moy":148,"fc_max":169,"re":105,"cadence":172,"elevation_gain":43,"rpe_ressenti":3,"commentaire":"11,26 km en 1h06 + 6 lignes droites · départ 8h33 · FC 148/169 · cadence 172 · D+ 43 m · Novablast 5 J · chaleur modérée, ressenti facile après 2 jours de repos.","pr":0,"ach":0,"pr_detail":[],"revue":_REVUE_FICHIER}
        arr[1]["date"]="2026-06-25"
        arr[1]["chaussure"]="Novablast 5 J"
        arr[1]["realise"]={"statut":"fait","km":10.66,"temps":"1h02","allure":"5:47/km","fc_moy":148,"fc_max":161,"re":99,"cadence":87,"elevation_gain":20,"rpe_ressenti":5,"commentaire":"10,66 km en 1h02 \u00b7 d\u00e9part 8h00 \u00b7 FC 148/161 \u00b7 cadence 87 \u00b7 D+ 20 m \u00b7 Novablast 5 J \u00b7 canicule. Mardi et mercredi saut\u00e9s (chaleur).","pr":0,"ach":0,"pr_detail":[],"revue":_REVUE_FICHIER}
        arr[2]["realise"]={"statut":"echec","km":0,"temps":"—","allure":"—","fc_moy":0,"fc_max":0,"rpe_ressenti":0,"commentaire":"Annulée — canicule persistante toute la semaine (40°C jour, 30°C nuit). Aucun créneau exploitable pour une spécifique vallonnée de qualité.","pr":0,"ach":0,"pr_detail":[],"revue":_REVUE_FICHIER}
        # Renfo jamais realise : statut clarifie retroactivement pour qu'il ne
        # reste pas indefiniment en 'a faire' six semaines apres la date.
        arr[3]["realise"]={"statut":"skipped","km":0,"temps":"—","allure":"—","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,"commentaire":"Non réalisée — semaine de canicule persistante (40 °C le jour, 30 °C la nuit) ayant déjà coûté deux séances. Le renforcement n'a pas été rattrapé.","pr":0,"ach":0,"pr_detail":[],"revue":_REVUE_FICHIER}
    SEANCES_BY_WEEK[str(n)]=arr
    if n==27:
        arr[0]["date"]="2026-06-29"
        arr[0]["chaussure"]="Novablast 5 J"
        arr[0]["realise"]={"statut":"fait","km":13.01,"temps":"1h13:32","allure":"5:39/km","fc_moy":155,"fc_max":178,"re":149,"cadence":86,"elevation_gain":35,"rpe_ressenti":6,"commentaire":"13,01 km en 1h13:32 · soirée 19h52 · FC 155/178 · cadence 86 · D+ 35 m · RE 149 · 1046 kcal · Novablast 5 J · avec Edwige R · 30°C ressenti 30°C · 20 PRs Strava.","pr":20,"ach":20,"pr_detail":[],"revue":_REVUE_FICHIER}
        arr[1]["date"]="2026-06-30"
        arr[1]["chaussure"]="Magic Speed 4"
        arr[1]["realise"]={"statut":"partiel","km":6.54,"temps":"35:14","allure":"5:23/km","fc_moy":149,"fc_max":172,"re":60,"cadence":174,"elevation_gain":27,"rpe_ressenti":7,"commentaire":"Tempo 2×15min prévu — interrompu par un souci gastrique. 6,54 km courus : 4 km d'échauffement EF (FC 131-145) puis 2 km de tempo lancé à 4:53-4:54/km (FC 164-166) avant l'arrêt. Matin 9h31 · cadence 174/184 ppm · D+ 27 m · 24°C · Magic Speed 4 · 2 PRs (place nautique 4:26/km, berges Saône 4:53/km).","pr":2,"ach":3,"pr_detail":["Place nautique confluence 4:26/km","Berges Saône darse→Perrache 4:53/km"],"revue":_REVUE_FICHIER}
        arr[2]["date"]="2026-07-02"
        arr[2]["chaussure"]="Clifton 10"
        arr[2]["realise"]={"statut":"fait","km":10.55,"temps":"1h01","allure":"5:41/km","fc_moy":148,"fc_max":170,"re":96,"cadence":87,"elevation_gain":46,"rpe_ressenti":4,"commentaire":"10,55 km en 1h01 · matin 9h25 · FC 148/170 · cadence 87 · D+ 46 m · RE 96 · 827 kcal · Clifton 10 · 0 PR · berges Rhône-Confluence. J-3 Déraille.","pr":0,"ach":0,"pr_detail":[],"revue":_REVUE_FICHIER}
        arr[3]["date"]="2026-07-05"
        arr[3]["chaussure"]="Cascadia 19"
        arr[3]["realise"]={"statut":"fait","km":23.3,"temps":"2:52:48","allure":"7:12/km","fc_moy":168,"fc_max":181,"re":584,"cadence":150,"elevation_gain":957,"rpe_ressenti":8,"commentaire":"TRAIL DÉRAILLE · 23,3 km · D+ 957 m · 66e/gen · 11e/18 M0 · FC 168/181 (88% FCmax) · 2388 kcal · Cascadia 19 · chaleur intense · ~4h sommeil · 3 gels + 3L (1L électrolytes). Course de gestion réussie.","pr":0,"ach":1,"pr_detail":[],"revue":_REVUE_FICHIER}
        SEANCES_BY_WEEK[str(n)]=arr
    if n==28:
        arr[0]["date"]="2026-07-07"
        arr[0]["chaussure"]="Novablast 5 J"
        arr[0]["realise"]={"statut":"fait","km":11.03,"temps":"1h07","allure":"6:02/km","fc_moy":148,"fc_max":192,"re":106,"cadence":85,"elevation_gain":39,"rpe_ressenti":4,"commentaire":"11,03 km en 1h07 · matin 9h07 · FC 148/192 · cadence 85 · D+ 39 m · RE 106 · 880 kcal · Novablast 5 J · 6 PRs · avec Anis (Yannis). Km 1-9 calés sur lui (~6:20-6:30, FC 138-153, récup pure), puis gros dernier km solo à 4:14/km avec FC 184 (max 192 = FCmax). J+2 Déraille, aucune douleur, jambes légères.","pr":6,"ach":6,"pr_detail":["Finish km 11 à 4:14/km"],"revue":_REVUE_FICHIER}
        arr[1]["date"]="2026-07-08"
        arr[1]["chaussure"]="Clifton 10"
        arr[1]["realise"]={"statut":"fait","km":10.03,"temps":"1h02","allure":"6:12/km","fc_moy":140,"fc_max":163,"re":60,"cadence":87,"elevation_gain":22,"rpe_ressenti":3,"commentaire":"10,03 km en 1h02 (temps de mouvement) · matin 9h16 · FC 140/163 · cadence 87 · D+ 22 m · RE 60 · 775 kcal · Clifton 10 · 4 PRs · avec Yannis · forte chaleur (canicule persistante). Pause d'environ 18 min au km 5 (discussion), FC qui dérive légèrement en fin de sortie (153→163) par la chaleur, allure stable.","pr":4,"ach":4,"pr_detail":[],"revue":_REVUE_FICHIER}
        arr[2]["realise"]={"statut":"skipped","reason":"Sortie longue avancée au jeudi","km":0,"temps":"—","allure":"—","fc_moy":0,"fc_max":0,"rpe_ressenti":0,"commentaire":"EF aérobie sacrifiée — la sortie longue a été avancée au jeudi (à la place de vendredi), départ prévu 4 jours en montagne dès vendredi. Aucun créneau restant cette semaine.","pr":0,"ach":0,"pr_detail":[],"revue":_REVUE_FICHIER}
        arr[3]["date"]="2026-07-09"
        arr[3]["chaussure"]="Novablast 5 J"
        arr[3]["realise"]={"statut":"fait","km":18.16,"temps":"1h46","allure":"5:50/km","fc_moy":148,"fc_max":165,"re":171,"cadence":88,"elevation_gain":67,"rpe_ressenti":6,"commentaire":"18,16 km en 1h46 (temps de mouvement) · matin 8h53 · FC 148/165 · cadence 88 · D+ 67 m · RE 171 · 1410 kcal · Novablast 5 J · 5 PRs · avec Edwige. Sortie longue avancée au jeudi (au lieu de vendredi) car départ 4 jours en montagne (rando probable) dès demain. Allure très homogène (5:19 à 6:12/km selon les km), FC qui monte en fin de sortie (146→160) sur les 2 derniers km à allure inchangée. Hydratation : 1 flasque 500ml boisson d'effort électrolytes zéro calorie en démarrage, puis 2 flasques 500ml (1,5L total, ~850 ml/h) + 1 gel. Stratégie ressentie comme très efficace par forte chaleur.","pr":5,"ach":5,"pr_detail":[],"revue":_REVUE_FICHIER}
        arr[4]["type"]="Trail montagne — sortie plaisir"
        arr[4]["titre"]="Trail montagne avec les copains"
        arr[4]["sous"]="Format court, gros dénivelé · montée marchée, descente engagée"
        arr[4]["date"]="2026-07-11"
        arr[4]["chaussure"]="Cascadia 19"
        arr[4]["objectif"]="Sortie trail plaisir entre copains en montagne. Aucun objectif de performance : on monte tranquille en marchant, on lâche les jambes en descente, on profite du terrain et du dénivelé. Le genre de sortie qui construit l'endurance générale et le mental sans peser sur la charge structurée du plan."
        arr[4]["sport"]="Trail"
        arr[4]["cat"]="trail"
        arr[4]["rpe"]=4
        arr[4]["metriques"]={"Distance":"10,7 km","D+":"646 m","Durée":"2h07","Type":"Trail montagne"}
        arr[4]["sous"]="Format court, gros dénivelé · montée marchée, descente engagée"
        arr[4]["struct"]=[{"nom":"Montée","txt":"~2 km à pied, pente +13 à +16%. Marche efficace, on économise."},{"nom":"Traversée","txt":"Terrain ondulant, allure libre selon le groupe."},{"nom":"Descente","txt":"Fin de sortie engagée, pente jusqu'à -20%. Vivacité de pied, on lâche les jambes."}]
        arr[4]["legende"]=[{"c":"#16a34a","l":"Montée marchée / échauffement"},{"c":"#A1A1AA","l":"Descente active"}]
        arr[4]["benefices"]="Moteur aérobie (2h d'effort continu), force spécifique via le dénivelé, travail excentrique des quadriceps en descente, proprioception et vivacité de pied. Et surtout : plaisir et mental, le carburant d'une prépa longue."
        arr[4]["coach"]=[{"titre":"En montée","texte":"Marcher sur les fortes pentes n'est pas un aveu de faiblesse — c'est souvent plus efficace et moins coûteux que courir. Les meilleurs traileurs le font."},{"titre":"En descente","texte":"La descente technique est un vrai travail : elle muscle l'excentrique et affûte la proprioception, des qualités qu'un plan route ne développe jamais."}]
        arr[4]["vigilance"]="Après une descente chargée en dénivelé, surveille ton dos (ta vigilance connue) et tes quadriceps qui encaissent l'excentrique. Rien d'alarmant ici, mais reste à l'écoute les 48h suivantes."
        arr[4]["realise"]={"statut":"fait","km":10.70,"temps":"2h07","allure":"11:53/km","fc_moy":138,"fc_max":179,"re":118,"cadence":65,"elevation_gain":646,"rpe_ressenti":4,"commentaire":"10,70 km en 2h07 (temps de mouvement) \u00b7 matin 9h28 \u00b7 D+ 646 m \u00b7 FC 138/179 \u00b7 cadence 65 \u00b7 RE 118 \u00b7 1245 kcal \u00b7 Cascadia 19 \u00b7 avec les copains. Vrai profil trail montagne : mont\u00e9e raide march\u00e9e sur les 2 premiers km (pente +13 puis +16%, FC 134-150, cadence 54-56), terrain ondulant au milieu, puis descente active et engag\u00e9e sur la fin (pente jusqu'\u00e0 -20%, cadence qui monte \u00e0 82-84, vitesse jusqu'\u00e0 ~3:00/km, FC 165-179 sur les segments roulants). Sortie plaisir, tr\u00e8s bonnes sensations.","pr":0,"ach":1,"pr_detail":[],"revue":_REVUE_FICHIER}
        arr.append({"id":6,"num":28,"type":"Trail montagne — sortie plaisir","cat":"trail","sport":"Trail",
          "titre":"Petit Croisse Baulet avec les copains",
          "sous":"Trail montagne sous la chaleur \u00b7 grosse mont\u00e9e march\u00e9e, longue descente engag\u00e9e",
          "date":"2026-07-12","chaussure":"Cascadia 19","rpe":4,"accent":"#F4561D","opt":False,"fill":True,
          "metriques":{"Distance":"11,0 km","D+":"530 m","Dur\u00e9e":"2h35","Type":"Trail montagne"},
          "objectif":"Deuxi\u00e8me sortie trail plaisir du week-end, cette fois au Petit Croisse Baulet et en pleine chaleur de l'apr\u00e8s-midi. Toujours le m\u00eame esprit : on grimpe tranquille, on profite, on l\u00e2che les jambes en descente. Une belle mani\u00e8re de boucler la semaine de r\u00e9cup avec du d\u00e9nivel\u00e9 et du plaisir.",
          "struct":[{"nom":"Approche","txt":"Terrain roulant et l\u00e9g\u00e8re descente pour se mettre en jambes (km 1-4)."},{"nom":"La grosse mont\u00e9e","txt":"Mont\u00e9e du Petit Croisse Baulet : 257 m D+ sur ~1 km (pente ~24%), FC jusqu'\u00e0 176. March\u00e9e, forc\u00e9ment."},{"nom":"La descente","txt":"Longue descente engag\u00e9e (km 8-12, pente -14 \u00e0 -28%), cadence qui grimpe \u00e0 76-84, on d\u00e9roule."}],
          "legende":[{"c":"#16a34a","l":"Approche / mont\u00e9e march\u00e9e"},{"c":"#A1A1AA","l":"Descente active"}],
          "benefices":"Force sp\u00e9cifique (une mont\u00e9e \u00e0 24% !), travail excentrique en descente longue, endurance a\u00e9robie sur 2h35, et gestion de l'effort par forte chaleur \u2014 une comp\u00e9tence pr\u00e9cieuse \u00e0 l'approche de l'\u00e9t\u00e9.",
          "coach":[{"titre":"La chaleur","texte":"D\u00e9part \u00e0 13h en pleine chaleur : c'est exigeant. Ta FC moyenne reste pourtant basse (129, 67% FCmax) gr\u00e2ce \u00e0 la marche en mont\u00e9e \u2014 gestion intelligente. Pense hydratation et \u00e9lectrolytes comme sur tes sorties chaudes."},{"titre":"Deux trails en deux jours","texte":"Apr\u00e8s la sortie d'hier, un deuxi\u00e8me trail avec du D+ : le volume de d\u00e9nivel\u00e9 du week-end est cons\u00e9quent. Le corps encaisse car c'est \u00e0 intensit\u00e9 mod\u00e9r\u00e9e, mais accorde-toi une vraie r\u00e9cup d\u00e9but de semaine prochaine."}],
          "vigilance":"Deux sorties trail cons\u00e9cutives avec beaucoup de descente : tes quadriceps et ton dos ont travaill\u00e9. Priorise le repos ou un footing tr\u00e8s facile lundi-mardi. \u00c9coute les signaux.",
          "realise":{"statut":"fait","km":11.04,"temps":"2h35","allure":"14:00/km","fc_moy":129,"fc_max":176,"temp":30,"re":109,"cadence":125,"elevation_gain":530,"rpe_ressenti":4,"commentaire":"11,04 km en 2h35 (temps de mouvement) \u00b7 apr\u00e8s-midi 13h01 (grosse chaleur) \u00b7 D+ 530 m \u00b7 FC 129/176 \u00b7 cadence 62 \u00b7 RE 109 \u00b7 1240 kcal \u00b7 Cascadia 19 \u00b7 avec les copains. Temps fort : la mont\u00e9e du Petit Croisse Baulet (257 m D+ sur ~1 km, pente ~24%, FC 163-176, march\u00e9e). Longue descente engag\u00e9e sur la fin (km 8-12, pente -14 \u00e0 -28%, cadence 76-84, FC 145-165). FC moyenne basse (129) gr\u00e2ce \u00e0 la marche en mont\u00e9e malgr\u00e9 la chaleur. Deuxi\u00e8me trail du week-end.","pr":0,"ach":0,"pr_detail":[],
          "revue":_REVUE_FICHIER}})
        SEANCES_BY_WEEK[str(n)]=arr
    if n==29:
        arr[0]["date"]="2026-07-15"
        arr[3]["date"]="2026-07-16"
        arr[2]["date"]="2026-07-17"
        arr[2]["realise"]={"statut":"fait","km":10.30,"decouplage":{"pct":8.33,"bpm":1.9,"fen_min":49,"temp":28,"attendu":8,"p1":"5:53/km","fc1":144,"p2":"5:59/km","fc2":146,"qualite":"fiable","algo":"decoup-v1"},"temps":"1h00","allure":"5:51/km","fc_moy":147,"fc_max":172,"re":93,"cadence":87,"elevation_gain":33,"rpe_ressenti":5,"commentaire":"10,30 km en 1h00 · matin 9h49 · corps de sortie km 1-8 assez lent (6:00-6:14/km) mais FC déjà 144-149 · accélération sur les 2 derniers km au lieu des lignes droites prévues : km 9 en 5:15/km (FC 158), km 10 en 5:11/km (FC 165), pointe finale à 172 · cadence 87 (stable, n'a pas augmenté sur l'accélération) · RE 93 · 806 kcal · HOKA Clifton 10 (1124 km, fin de vie). Ressenti cardio anormalement haut par rapport à l'habitude, alors que la chaleur avait pourtant diminué.",
        "pr":0,"ach":2,"pr_detail":[],
        "revue":_REVUE_FICHIER}
        arr[1]["date"]="2026-07-19"
        arr[4]["date"]="2026-07-19"
        arr[1]["chaussure"]="Novablast 5 J"
        arr[1]["realise"]={"statut":"fait","km":10.03,"temps":"1h04","allure":"blocs 4:24 & 4:31/km","fc_moy":150,"fc_max":182,"re":96,"cadence":171,"elevation_gain":15,"rpe_ressenti":7,"commentaire":"Seuil 30 avec 2 amis, fait dimanche en derni\u00e8re s\u00e9ance de la semaine \u00b7 d\u00e9part 10h09 \u00b7 10,03 km \u00b7 \u00e9chauffement ~37 min \u00e0 FC 130-143, puis 2\u00d78 min seuil. BLOC 1 : 1808 m \u00e0 4:24/km, FC ~175 (max 182) \u2014 ressenti excellent, a l\u00e2ch\u00e9 Yannis. R\u00e9cup 3 min (FC redescend \u00e0 161). BLOC 2 : 1764 m \u00e0 4:31/km, FC ~175 (max 179) \u2014 volontairement un peu plus rapide, aucune difficult\u00e9. Arr\u00eat\u00e9 \u00e0 10 km (gros projet ViaRh\u00f4na cette semaine). RE 96, 10 records de segments, Novablast 5 J. Aucune douleur, s\u00e9ance ador\u00e9e.",
        "pr":10,"ach":10,"pr_detail":[],
        "revue":_REVUE_FICHIER}
        arr[4]["realise"]={"statut":"skipped","reason":"remplac\u00e9e par le seuil"}
        arr[3]["chaussure"]="Novablast 5 J"
        arr[3]["realise"]={"statut":"fait","km":23.04,"decouplage":{"pct":9.35,"bpm":7.9,"fen_min":125,"temp":31,"attendu":10,"p1":"5:39/km","fc1":146,"p2":"5:41/km","fc2":154,"qualite":"fiable","algo":"decoup-v1"},"temps":"2h10","allure":"5:39/km","fc_moy":150,"fc_max":179,"re":222,"cadence":177,"elevation_gain":67,"temp":28,"rpe_ressenti":7,"commentaire":"23,04 km en 2h10 (2h23 avec pauses ravito) \u00b7 d\u00e9part 9h37 sous canicule \u00b7 avec Edwige \u00b7 allure 5:39/km \u00b7 FC 150/179 \u00b7 cadence 177 spm \u00b7 RE 222 \u00b7 1715 kcal \u00b7 31 records de segments \u00b7 Novablast 5 J. Bloc seuil improvis\u00e9 au tunnel (km 14-15, frais) : GPS liss\u00e9 sous terre mais FC 162-179 confirme l'effort, km 15 en 5:08 (le plus rapide). Hydratation ~2,5 L : 500 ml \u00e9lectrolytes 0 kcal + 500 ml claire + 500 ml pastille sodium + 1 L d'eau. 2 gels caf\u00e9, le 2e vers 1h40-45 apr\u00e8s l\u00e9gers vertiges \u2014 pris un peu tard. Aucune douleur, bien revenu sur la fin, de la r\u00e9serve \u00e0 l'arriv\u00e9e.",
        "pr":31,"ach":31,"pr_detail":[],
        "revue":_REVUE_FICHIER}
        arr[0]["chaussure"]="Novablast 5 J"
        arr[0]["realise"]={"statut":"fait","km":10.35,"decouplage":{"pct":5.12,"bpm":2.5,"fen_min":58,"temp":30,"attendu":8,"p1":"5:45/km","fc1":146,"p2":"5:48/km","fc2":149,"qualite":"fiable","algo":"decoup-v1"},"temps":"1h00","allure":"5:48/km","fc_moy":147,"fc_max":161,"re":94,"cadence":175,"elevation_gain":31,"temp":30,"rpe_ressenti":5,"commentaire":"10,35 km en 1h00 \u00b7 d\u00e9part 19h44 sous forte chaleur \u00b7 allure 5:48/km tr\u00e8s r\u00e9guli\u00e8re (laps 5:48-5:56, km 2 en 5:28) \u00b7 FC 147/161 (76 % FCmax) \u00b7 cadence 175 spm \u00b7 RE 94 \u00b7 810 kcal \u00b7 plat (berges de Lyon, D+ 31 m) \u00b7 Novablast 5 J. Lundi-mardi en repos (montagne avec les amis, fatigue ressentie) \u2014 semaine d\u00e9marr\u00e9e mercredi volontairement. D\u00e9rive cardiaque mod\u00e9r\u00e9e en fin de sortie (140\u2192155), classique sous chaleur.","pr":0,"ach":0,"pr_detail":[],
        "revue":_REVUE_FICHIER}

    if n==30:
        # Restructuration de la semaine autour du projet ViaRhôna (Vienne -> St-Rambert-d’Albon, 40 km, entre amis)
        arr[4]["titre"]="ViaRhôna — Vienne → Saint-Rambert-d’Albon"
        arr[4]["type"]="Sortie longue — ultra-distance plaisir"
        arr[4]["sport"]="Course à pied"
        arr[4]["accent"]=BLUE
        arr[4]["fill"]=95
        arr[4]["cat"]="sortie-longue"
        arr[4]["date"]="2026-07-23"
        arr[4]["realise"]={"statut":"fait","km":42.52,"temps":"4h18","allure":"6:04/km","fc_moy":145,"fc_max":172,"re":367,"cadence":174,"elevation_gain":137,"temp":28,"rpe_ressenti":7,"commentaire":"MARATHON complet Vienne \u2192 Saint-Rambert-d'Albon \u00b7 d\u00e9part 7h07 \u00b7 42,52 km en 4h18 de mouvement (5h15 total, ~56 min d'arr\u00eats/ravitos) \u00b7 3269 kcal \u00b7 4 records. Parti SEUL (les amis ne sont pas venus) : 0-15 km \u00e0 5:36/km, FC 141,8 \u2014 tr\u00e8s \u00e0 l'aise. Yannis rejoint \u00e0 la gare de Saint-Clair : 15-38 km \u00e0 6:21/km, FC 145,4 (ralentissement VOLONTAIRE pour rester ensemble). Finish l\u00e2ch\u00e9 sur les 4 derniers km pour tester l'allure marathon : km 41 \u00e0 5:16/km et km 42 \u00e0 5:15/km, FC 163-167. Nutrition : 3 gels + 3 pastilles \u00e9lectrolytes + 1 Clif Bar, beaucoup bu \u2014 aucune perte d'\u00e9nergie ressentie, sensation de pouvoir continuer. Novablast 5 J. \u26a0\ufe0f Petite douleur sous le pied gauche apparue sur le dernier kilom\u00e8tre.",
        "pr":4,"ach":6,"pr_detail":[],
        "revue":_REVUE_FICHIER}
        arr[4]["chaussure"]="Novablast 5 J"
        arr[4]["sous"]="40 km en EF très cool avec Yannis (et peut-être Edwige), départ 7h le long de la ViaRhôna. Objectif plaisir, pas performance."
        arr[4]["metriques"]={"Distance":"~40 km","Durée":"~4h-4h30","Allure":"EF très facile","FC":"Zone 1-2 stricte","RPE":"5-6 (par la durée)","Type":"Ultra-distance plaisir"}
        arr[4]["objectif"]="De très loin ta plus longue sortie de la saison (près du double de ton record actuel). L’objectif n’est pas la performance mais l’expérience : tenir 4h+ en EF strict, entre amis, sur une piste roulante. <strong>Séance à traiter comme un vrai événement physiologique, pas comme un footing.</strong>"
        arr[4]["struct"]=[
          {"nom":"Départ (km 0-10)","txt":"Rester délibérément lent malgré les jambes fraîches et l’excitation du groupe — c’est ici que se joue la réussite des 30 derniers km."},
          {"nom":"Cœur de sortie (km 10-30)","txt":"Croisère EF strict, hydratation systématique toutes les 20-30 min, gel toutes les 40-45 min dès 45 min d’effort (leçon de la SL du 16/7)."},
          {"nom":"Fin (km 30-40)","txt":"Écoute des signaux (vertiges, jambes) ; ralentir encore si besoin, marcher si nécessaire — aucune honte, l’objectif est de finir bien, pas vite."}]
        arr[4]["legende"]=[{"c":GREEN,"l":"EF strict / Zone 1-2"}]
        arr[4]["benefices"]="Endurance fondamentale extrême, expérience logistique (nutrition/hydratation sur ultra-distance) directement transférable à la préparation SaintExpress 45 km, et un moment fort entre amis."
        arr[4]["coach"]=[
          {"titre":"Nutrition — vise large","texte":"Sur 4h+, environ 5 à 6 gels espacés de 40-45 min, plus si possible un peu de salé (biscuits apéritif) passé 2h30. La ViaRhôna traverse des villages (Condrieu, Sablons...) — repérez des points de ravito plutôt que tout porter."},
          {"titre":"Terrain plat — bonne nouvelle","texte":"Contrairement à tes trails, pas de descente qui martelèle les quadriceps. L’usure vient du temps passé debout, pas du dénivelé — la vigilance dos reste de mise sur la durée."},
          {"titre":"Le vrai risque : partir trop vite","texte":"À plusieurs, sur du plat, avec les jambes fraîches, l’envie d’accélérer est réelle. Tenir un rythme de conversation les 15-20 premiers km sécurise toute la suite."}]
        arr[4]["vigilance"]="Départ 7h malin contre la chaleur, mais vers 10h-11h (3-4h de course) ça peut recommencer à chauffer : électrolytes dès le départ. Prévoir large en hydratation (historique : ~2,5 L pour 2h10, donc 4-5 L probables sur 4h+). Aucune séance de qualité dans les 2 jours suivants — cette sortie EST la grosse charge de la semaine."
        arr[3]["titre"]="Footing de récupération post-ViaRhôna"
        arr[3]["type"]="Récupération active"
        arr[3]["sport"]="Course à pied"
        arr[3]["accent"]=GREEN
        arr[3]["fill"]=25
        arr[3]["cat"]="ef"
        arr[3]["date"]="2026-07-26"
        arr[3]["chaussure"]="Novablast 5 V"
        arr[3]["realise"]={"statut":"fait","km":10.13,"temps":"1h00","allure":"5:56/km","fc_moy":146,"fc_max":161,"re":83,"cadence":173,"elevation_gain":32,"temp":27,"rpe_ressenti":4,
        "decouplage":{"pct":11.56,"bpm":3.6,"fen_min":57,"temp":27,"attendu":8,"p1":"5:48/km","fc1":144,"p2":"6:02/km","fc2":147,"qualite":"fiable","algo":"decoup-v1"},
        "commentaire":"R\u00e9cup post-marathon \u00e0 J+3 \u00b7 d\u00e9part 16h40, fin de journ\u00e9e ~27\u00b0C (chaud sans \u00eatre caniculaire) \u00b7 10,13 km en 1h00 \u00e0 5:56/km. Objectif annonc\u00e9 : rester sous 140 bpm et \u00e9viter la zone grise. R\u00e9alis\u00e9 : FC moyenne 146 (max 161), 15,6 % du temps sous 140, 85 % sous 150, seulement 3,6 % au-dessus de 155. D\u00e9rive nette sur la seconde moiti\u00e9 : km 0-2 \u00e0 5:41/km FC 136,7 puis km 8-10 \u00e0 6:00/km FC 148 \u2014 il a RALENTI de 19 s/km pendant que la FC montait de 11 bpm. D\u00e9couplage 11,6 % (attendu ~8 %). Petite g\u00eane sous le pied gauche, sans douleur. Premi\u00e8re sortie avec la Novablast 5 V (paire r\u00e9serv\u00e9e Nice, d\u00e9but de rodage). Aucun record, RE 83.",
        "pr":0,"ach":0,"pr_detail":[],
        "revue":_REVUE_FICHIER}
        arr[3]["chaussure"]="Gel Pulse 16"
        arr[3]["sous"]="Très facile, courte. Le 40 km de jeudi est déjà ta séance longue de la semaine — ici on récupère, on ne construit pas."
        arr[3]["metriques"]={"Distance":"~8 km max","Durée":"~45 min","Allure":"Très facile","FC":"Zone 1","RPE":"2-3","Type":"Récupération"}
        arr[3]["objectif"]="Faire circuler le sang, rien de plus. Si les jambes sont encore lourdes 3 jours après le ViaRhôna, remplace par du repos complet ou de la marche — aucune culpabilité."
        arr[3]["struct"]=[{"nom":"Corps","txt":"6-8 km à allure de conversation, sur terrain plat. S’arrêter dès que ça tire quelque chose d’inhabituel."}]
        arr[3]["legende"]=[{"c":GREEN,"l":"Très facile"}]
        arr[3]["benefices"]="Récupération active post-ultra-distance : circulation, sans coût additionnel pour les fibres déjà sollicitées."
        arr[3]["coach"]=[{"titre":"La vraie séance de la semaine, c’était jeudi","texte":"Ne cherche pas à « rattraper » du volume ici. Le 40 km a déjà rempli très largement le quota de la semaine."}]
        arr[3]["vigilance"]="Douleur inhabituelle, gonflement, ou fatigue anormalement persistante → repos complet et on réévalue ensemble."
        arr[0]["titre"]="Footing de récupération"
        arr[0]["type"]="Récupération active"
        arr[0]["sport"]="Course à pied"
        arr[0]["accent"]=GREEN
        arr[0]["fill"]=25
        arr[0]["cat"]="ef"
        arr[0]["date"]="2026-07-20"
        arr[0]["chaussure"]="HOKA Clifton 10"
        arr[0]["realise"]={"statut":"fait","km":14.03,"decouplage":{"pct":0.43,"bpm":1.8,"fen_min":72,"temp":22,"attendu":6,"p1":"5:52/km","fc1":138,"p2":"5:44/km","fc2":140,"qualite":"fiable","algo":"decoup-v1"},"temps":"1h21","allure":"5:48/km","fc_moy":139,"fc_max":154,"re":78,"cadence":175,"elevation_gain":35,"rpe_ressenti":4,"commentaire":"Sortie de récup lundi (rallongée à 14 km car passage chez sa copine pour rapporter le portable) · départ 9h58 · météo nettement plus fraîche que les jours précédents, ressenti sans commune mesure avec la canicule. Objectif piloté au CARDIO (<140 bpm) plutôt qu'à l'allure : FC moyenne 139 (max 154) — objectif atteint. Allure 5:48/km qui en découle, régulière. km 1-3 à FC 128-138 puis stabilisation 137-145, dérive quasi nulle sur 1h20. Cadence 175 spm. RE 78, 6 records de segments, D+ 35m. Fatigue légère en début, vite dissipée, aucune douleur. Clifton 10 (fin de vie).",
        "pr":6,"ach":6,"pr_detail":[],
        "revue":_REVUE_FICHIER}
        arr[0]["chaussure"]="Gel Pulse 16"
        arr[0]["sous"]="Très facile, 30-40 min. Récupération du seuil de dimanche — ou repos complet si les jambes sont lourdes."
        arr[0]["metriques"]={"Distance":"~6-7 km","Durée":"30-40 min","Allure":"Très facile","FC":"Zone 1","RPE":"2-3","Type":"Récupération"}
        arr[0]["objectif"]="Faire circuler après le beau seuil de dimanche. Optionnel : gainage/dos pour préparer les lombaires aux 4h de jeudi. Aucune intensité."
        arr[0]["struct"]=[{"nom":"Corps","txt":"6-7 km à allure de conversation. Si fatigue résiduelle du seuil, remplace par du repos — sans culpabilité."}]
        arr[0]["legende"]=[{"c":GREEN,"l":"Très facile"}]
        arr[0]["benefices"]="Récupération active : circulation sanguine, assimilation du seuil, sans coût pour la fraîcheur de jeudi."
        arr[0]["coach"]=[{"titre":"On pense déjà à jeudi","texte":"Toute la semaine est organisée autour du 40 km. Dès aujourd'hui, on protège la fraîcheur — rien de dur avant l'ultra."}]
        arr[0]["vigilance"]="Si les jambes sont encore marquées par le seuil, le repos complet est le bon choix."
        arr[1]["titre"]="Séance de vitesse — 8×30 sec VMA"
        arr[1]["type"]="VMA / vitesse"
        arr[1]["sport"]="Course à pied"
        arr[1]["accent"]=RED
        arr[1]["fill"]=70
        arr[1]["cat"]="seuil"
        arr[1]["date"]="2026-07-21"
        arr[1]["chaussure"]="ASICS Magic Speed 4"
        arr[1]["sous"]="Séance de vitesse choisie par envie (hors logique de la semaine ViaRhôna). 8×30 sec en accélération progressive, récup 1'30."
        arr[1]["metriques"]={"Distance":"7,5 km","Durée":"36:49","Allure":"blocs 4:10 → 3:16/km","FC":"159 moy / 182 max","RPE":"7","Type":"VMA courte"}
        arr[1]["objectif"]="Stimulus de vitesse pure demandé par Loïc malgré le 40 km de jeudi. Structure 8×30 sec récup 1'30 pour travailler le neuromusculaire. Réalisée en negative split spontané, avec des récups plus actives que prévu."
        arr[1]["struct"]=[
          {"nom":"Échauffement","txt":"20 min / 3,98 km à 5:02/km, FC montant progressivement de 136 à 162."},
          {"nom":"8×30 sec","txt":"Intervalles à 4:10, 4:12, 4:11, 4:09, 4:05, 3:44, 3:41 puis 3:16/km — progression pyramidale, pointe finale à 3:16/km. FC de 160 à 182."},
          {"nom":"Récupérations","txt":"1'30 entre chaque, mais faites actives (~5:00/km, FC restée 160-163) — trop rapides pour une vraie récup neuromusculaire."}]
        arr[1]["legende"]=[{"c":RED,"l":"Intervalles VMA"},{"c":EF_COLOR,"l":"Échauffement / récup"}]
        arr[1]["benefices"]="Vitesse pure, recrutement des fibres rapides, pointe à 3:16/km (la plus rapide de la saison sur ce format). Bon ressenti, aucune douleur."
        arr[1]["coach"]=[{"titre":"Belle séance, mais attention à la fraîcheur","texte":"Progression pyramidale spontanée exemplaire (4:10 → 3:16/km). Point de vigilance : récups trop actives (FC jamais redescendue sous 160), la séance a viré VMA+tempo, plus dure que prévu. Surtout : c'est ta 2e qualité de la semaine avant le 40 km. Mercredi repos ABSOLU, et surveille la fraîcheur jeudi au réveil."}]
        arr[1]["vigilance"]="Deuxième séance de qualité avant le ViaRhôna : repos complet mercredi impératif, et le 40 km de jeudi devient une sortie à l'écoute si les jambes sont lourdes."
        arr[1]["realise"]={"statut":"fait","km":7.50,"temps":"36:49","allure":"blocs 4:10 → 3:16/km","fc_moy":159,"fc_max":182,"re":93,"cadence":173,"elevation_gain":35,"rpe_ressenti":7,"commentaire":"Séance de vitesse choisie par envie malgré la semaine ViaRhôna · départ 10h17 · Magic Speed 4 · 7,50 km, 8 records. Échauffement 20 min/3,98 km à 5:02/km (rapide, FC 136→162). Puis 8×30 sec récup 1'30 : intervalles à 4:10, 4:12, 4:11, 4:09, 4:05, 3:44, 3:41 puis 3:16/km — progression pyramidale en negative split, pointe finale à 3:16/km (la plus rapide de la saison). FC des intervalles montant de 160 à 175-182. Récups faites ACTIVES (~5:00/km, FC restée 160-163, trop rapides pour une vraie récup neuromusculaire) car Loïc avait la caisse. Séance qui vire donc VMA+tempo. Excellent ressenti, aucune douleur.",
        "pr":8,"ach":8,"pr_detail":["Pointe finale à 3:16/km"],
        "revue":_REVUE_FICHIER}
        arr[2]["titre"]="Repos complet"
        arr[2]["type"]="Repos"
        arr[2]["sport"]="Repos"
        arr[2]["accent"]=VIOLET
        arr[2]["fill"]=0
        arr[2]["cat"]="repos"
        arr[2]["opt"]=True
        arr[2]["date"]="2026-07-22"
        arr[2]["chaussure"]=None
        arr[2]["sous"]="Repos complet la veille du 40 km. Fraîcheur maximale pour profiter de l'ultra."
        arr[2]["metriques"]={"Distance":"—","Durée":"—","Allure":"—","FC":"—","RPE":"0","Type":"Repos"}
        arr[2]["objectif"]="Arriver frais au 40 km de jeudi. On retire les côtes prévues — du travail de force la veille d'un ultra plaisir serait une erreur. Hydrate-toi bien et prépare ta logistique nutrition."
        arr[2]["struct"]=[{"nom":"Repos","txt":"Rien de couru. Prépare gels, électrolytes et points de ravito pour demain. Couche-toi tôt."}]
        arr[2]["legende"]=[{"c":VIOLET,"l":"Repos"}]
        arr[2]["benefices"]="Fraîcheur maximale et pleins de glycogène avant le plus gros effort de la saison."
        arr[2]["coach"]=[{"titre":"La veille d'un ultra, on ne construit plus","texte":"Rien de ce que tu ferais aujourd'hui ne te rendrait plus fort jeudi — mais beaucoup de choses pourraient te fatiguer. Le repos est la meilleure séance possible ici."}]
        arr[2]["vigilance"]="Évite les journées debout épuisantes ; préserve tes jambes pour demain."

    if n==31:
        # Semaine reconstruite : absorption du marathon ViaRhona (23/07) sous dome de chaleur.
        # Meteo France annonce 36-38 C mercredi 29 et jeudi 30 -> la seule qualite est placee
        # mardi, dernier jour respirable. Le test 10 km prevu initialement est REPORTE :
        # un contre-la-montre maximal a J+5 d'un marathon mesurerait la fatigue, pas la forme.
        # Lundi
        arr[0]["titre"]="EF + 6×30 sec — séance avancée"
        arr[0]["type"]="VMA / vitesse"
        arr[0]["accent"]=RED
        arr[0]["fill"]=52
        arr[0]["cat"]="seuil"
        arr[0]["rpe"]=6.5
        arr[0]["realise"]={"statut":"fait","km":10.02,"temps":"56:06","allure":"5:36/km","fc_moy":148,"fc_max":188,"re":79,"cadence":175,"elevation_gain":39,"temp":29,"rpe_ressenti":6,
        "commentaire":"S\u00e9ance de qualit\u00e9 avanc\u00e9e du mardi au lundi \u00b7 d\u00e9part 11h07, ~29\u00b0C \u00b7 10,02 km. Structure : 6,12 km d'EF \u00e0 5:48/km (FC moyenne 140,8, 42 % des relev\u00e9s sous 140) puis 6\u00d730 sec r\u00e9cup 30 sec, puis 15 min de retour au calme. INTERVALLES en negative split parfait 6/6 : 4:22 \u2192 3:59 \u2192 3:52 \u2192 3:29 \u2192 3:20 \u2192 2:57/km. Pointe finale \u00e0 2:57/km, soit 19 s/km plus rapide que le meilleur intervalle du 21/07 (3:16). FC max 188 (plafond personnel 192). Redescente cardiaque difficile : sous 155 en 1 min mais pr\u00e8s de 8 min pour passer sous 150, FC rest\u00e9e entre 145 et 167 sur les 15 min de retour au calme. 5 records. Novablast 5 V (10 \u2192 20 km). G\u00eane au pied gauche toujours pr\u00e9sente, non douloureuse en courant.",
        "pr":5,"ach":5,"pr_detail":[],
        "revue":_REVUE_FICHIER}
        arr[0]["sport"]="Course à pied"
        arr[0]["date"]="2026-07-27"
        arr[0]["rpe"]=3.0
        arr[0]["chaussure"]="Gel Pulse 16"
        arr[0]["sous"]="Séance de qualité avancée du mardi : EF puis 6×30 sec. La canicule arrive mercredi, autant placer la vitesse au frais."
        arr[0]["metriques"]={"Distance":"~10 km","Durée":"~56 min","Allure":"EF 5:50/km + 6×30 sec","FC":"140 en EF, jusqu'à 188 sur les pointes","RPE":"6","Type":"VMA courte"}
        arr[0]["objectif"]="Entretenir la vivacité neuromusculaire — le système qui récupère le plus vite après un marathon. Échauffement long en EF pour protéger le pied, puis 6 accélérations courtes avec récupération complète."
        arr[0]["struct"]=[{"nom":"Échauffement","txt":"6 km d'EF progressive à ~5:50/km, FC sous 145."},{"nom":"6 × 30 sec","txt":"Accélérations progressives, récupération 30 sec entre chaque."},{"nom":"Retour au calme","txt":"15 min très faciles."}]
        arr[0]["legende"]=[{"c":GREEN,"l":"EF"},{"c":RED,"l":"30 sec"},{"c":VIOLET,"l":"Récup"}]
        arr[0]["benefices"]="Réveil neuromusculaire et économie de course, pour un coût métabolique modéré."
        arr[0]["coach"]=[{"titre":"Le pied commande","texte":"Premiers pas au réveil : si ça fait mal et que ça s'atténue en marchant, tu ne cours pas. C'est la signature d'une irritation de l'aponévrose plantaire, et elle se traite par le repos, pas en courant dessus."}]
        arr[0]["vigilance"]="Séance intense réalisée avec une gêne au pied encore présente : la suite de la semaine doit rester très facile."
        # Mardi — la seule qualite de la semaine
        arr[1]["titre"]="EF pilotée au cardio"
        arr[1]["type"]="EF aérobie"
        arr[1]["sport"]="Course à pied"
        arr[1]["accent"]=GREEN
        arr[1]["fill"]=26
        arr[1]["cat"]="ef"
        arr[1]["date"]="2026-07-28"
        arr[1]["rpe"]=3.5
        arr[1]["chaussure"]="HOKA Clifton 10"
        arr[1]["realise"]={"statut":"fait","km":10.03,"temps":"1h01","allure":"6:06/km","fc_moy":138,"fc_max":149,"re":49,"cadence":178,"elevation_gain":32,"temp":28,"rpe_ressenti":4,
        "decouplage":{"pct":2.98,"bpm":1.4,"fen_min":60,"temp":28,"attendu":8,"p1":"5:59/km","fc1":138,"p2":"5:59/km","fc2":139,"qualite":"fiable","algo":"decoup-v1"},
        "commentaire":"EF pilot\u00e9e au cardio \u00b7 d\u00e9part 9h09, ~28\u00b0C et air tr\u00e8s sec \u00b7 10,03 km en 1h01 \u00e0 6:06/km. OBJECTIF CARDIO PLEINEMENT ATTEINT : FC moyenne 138 (max 149), 66 % des relev\u00e9s sous 140 bpm, 100 % sous 150, ZERO seconde au-dessus de 150. D\u00e9couplage 2,98 % pour 8 % attendu \u2014 allure identique entre les deux moiti\u00e9s (5:59/km) avec seulement +1 bpm. RE 49, le plus bas depuis longtemps. G\u00eane au pied gauche d\u00e9crite comme un bleu ressenti \u00e0 chaque pas, sans emp\u00eacher de courir. Chauss\u00e9 en Clifton 10 (1148 km, paire en fin de vie).",
        "pr":0,"ach":0,"pr_detail":[],
        "revue":_REVUE_FICHIER}
        arr[1]["sous"]="10 km entièrement pilotés au cardio sous 140 bpm, par temps chaud et air très sec."
        arr[1]["metriques"]={"Distance":"10,03 km","Durée":"1h01","Allure":"6:06/km","FC":"138 moy · 149 max","RPE":"3-4","Type":"EF"}
        arr[1]["objectif"]="Sortie entièrement pilotée au cardio : rester sous 140 bpm quoi qu'il en coûte à l'allure. Par temps chaud et air sec, c'est la seule façon de faire de la vraie endurance sans basculer en zone grise."
        arr[1]["struct"]=[{"nom":"Corps","txt":"10 km à FC constante sous 140 bpm. L'allure est la conséquence, pas l'objectif."}]
        arr[1]["legende"]=[{"c":GREEN,"l":"EF pilotée FC"}]
        arr[1]["benefices"]="Endurance fondamentale pure, assimilation de la séance de vitesse de la veille, et validation du pilotage cardiaque par forte chaleur."
        arr[1]["coach"]=[{"titre":"Le cardio commande, l'allure suit","texte":"Accepter 6:06/km pour tenir 138 bpm par 28°C et air sec, c'est exactement la bonne décision. L'allure lente n'est pas une contre-performance : c'est le prix de la chaleur, et tu l'as payé au bon endroit."}]
        arr[1]["vigilance"]="Gêne au pied gauche décrite comme un bleu à chaque pas, ressentie en permanence. Chaussures usées utilisées ce jour-là : à ne plus reproduire."
        # Mercredi — canicule
        arr[2]["titre"]="Repos complet"
        arr[2]["type"]="Repos"
        arr[2]["sport"]="Repos"
        arr[2]["accent"]=VIOLET
        arr[2]["fill"]=0
        arr[2]["cat"]="repos"
        arr[2]["date"]="2026-07-29"
        arr[2]["rpe"]=2.5
        arr[2]["chaussure"]=None
        arr[2]["sous"]="Repos complet. Pic de canicule à 36-38°C et gêne au pied à surveiller : la meilleure séance du jour est de ne pas courir."
        arr[2]["metriques"]={"Distance":"—","Durée":"—","Allure":"—","FC":"—","RPE":"0","Type":"Repos"}
        arr[2]["objectif"]="Journée sans impact. Deux séances consécutives (vitesse lundi, 1h d'EF mardi) et une gêne au pied présente depuis six jours : le repos est ici la décision la plus productive."
        arr[2]["struct"]=[{"nom":"Repos","txt":"Rien de couru. Hydratation, marche légère, et surveillance du pied : test des premiers pas au réveil."}]
        arr[2]["legende"]=[{"c":VIOLET,"l":"Repos"}]
        arr[2]["benefices"]="Assimilation des deux séances précédentes et fenêtre de récupération pour le pied."
        arr[2]["coach"]=[{"titre":"Espace les sorties en Clifton 10","texte":"Tu as couru mardi avec la paire à 1148 km : semelle marquée, mesh usé, mousse tassée. Avec une gêne plantaire en cours, je te recommande de les réserver aux footings courts et de privilégier tes paires récentes sur les séances longues ou rapides. Tu en as trois disponibles."}]
        arr[2]["vigilance"]="Si la gêne au pied persiste après cette journée de repos complet, consulter avant la reprise. Six jours de gêne continue, c'est le seuil où l'attentisme devient risqué."
        arr[2]["realise"]={"statut":"fait","commentaire":"Repos complet respecté. Amélioration nette de la gêne au pied dès le lendemain."}
        # Samedi — sortie longue raccourcie
        arr[3]["titre"]="EF longue — reprise après 2 jours de repos"
        arr[3]["type"]="EF aérobie"
        arr[3]["sport"]="Course à pied"
        arr[3]["accent"]=BLUE
        arr[3]["fill"]=34
        arr[3]["cat"]="sortie-longue"
        arr[3]["date"]="2026-08-02"
        arr[3]["rpe"]=4.0
        arr[3]["chaussure"]="Novablast 5 V"
        arr[3]["realise"]={"statut":"fait","km":11.31,"temps":"58:31","allure":"5:10/km","fc_moy":154,"fc_max":166,"re":105,"cadence":173,"elevation_gain":36,"temp":24,"rpe_ressenti":5,
        "decouplage":{"pct":3.53,"bpm":7.1,"fen_min":60,"temp":24,"attendu":6,"p1":"5:11/km","fc1":150,"p2":"5:03/km","fc2":157,"qualite":"fiable","algo":"decoup-v1"},
        "commentaire":"Reprise apr\u00e8s 2 jours de repos complet (vendredi et samedi) pour laisser passer la douleur au pied \u00b7 d\u00e9part 7h44 pour \u00e9viter la chaleur \u00b7 11,31 km en 58:31 \u00e0 5:10/km. AUCUNE douleur au d\u00e9part, l\u00e9g\u00e8re g\u00eane ressentie en toute fin de sortie \u2014 arr\u00eat d\u00e9cid\u00e9 volontairement \u00e0 ce moment. DERIVE D'ALLURE MARQUEE, non intentionnelle : km 0-2 \u00e0 5:35/km (FC 135,8) puis acc\u00e9l\u00e9ration continue jusqu'\u00e0 4:55/km sur les km 10-12 (FC 160,6). R\u00e9partition FC : 32 % sous 150, 27 % entre 150-155, 26 % entre 155-160, 13 % entre 160-165. D\u00e9couplage 3,53 % pour 6 % attendu. RE 105, cadence 173. Novablast 5 V (34 \u2192 45 km).",
        "pr":0,"ach":1,"pr_detail":[],
        "revue":_REVUE_FICHIER}
        arr[3]["sous"]="Décalée au dimanche après deux jours de repos pour le pied. 11,3 km au frais, dérive d'allure assumée."
        arr[3]["metriques"]={"Distance":"11,31 km","Durée":"58:31","Allure":"5:10/km","FC":"154 moy · 166 max","RPE":"5","Type":"EF longue"}
        arr[3]["objectif"]="Reprise après deux jours de repos complet pour le pied. Sortie au frais, sans contrainte d'allure imposée — l'objectif était de vérifier que le pied tenait, pas de produire une performance."
        arr[3]["struct"]=[{"nom":"Corps","txt":"11,3 km continus, départ 7h44 par temps déjà chaud. Allure laissée libre, progressive du début à la fin."}]
        arr[3]["legende"]=[{"c":BLUE,"l":"EF longue"}]
        arr[3]["benefices"]="Test de tolérance du pied après repos, et première mesure de la FC produite à une allure proche de 5:10/km."
        arr[3]["coach"]=[{"titre":"Le vrai enseignement : ta dérive naturelle vers le haut","texte":"Tu as accéléré de 5:35 à 4:55/km sans le décider, avec une FC qui monte de 136 à 161. C'est exactement le mécanisme qui fait exploser un marathon parti trop vite. Le repérer maintenant, c'est précieux."}]
        arr[3]["vigilance"]="Gêne au pied réapparue en toute fin de sortie, sans douleur franche. Arrêt décidé au bon moment. Deux jours de repos avaient suffi à la faire disparaître au départ."
        # Jeudi — optionnel
        arr[4]["titre"]="Tunnel Croix-Rousse — blocs allure marathon"
        arr[4]["type"]="Spécifique marathon"
        arr[4]["sport"]="Course à pied"
        arr[4]["accent"]=BLUE
        arr[4]["fill"]=48
        arr[4]["cat"]="sortie-longue"
        arr[4]["date"]="2026-07-30"
        arr[4]["rpe"]=2.5
        arr[4]["chaussure"]="Novablast 5 V"
        arr[4]["realise"]={"statut":"fait","km":14.09,"temps":"1h16","allure":"5:26/km","fc_moy":158,"fc_max":172,"re":171,"cadence":173,"elevation_gain":42,"temp":26,"rpe_ressenti":7,
        "commentaire":"Tunnel de la Croix-Rousse \u00b7 d\u00e9part 9h57 \u00b7 14,09 km en 1h16. Structure : \u00e9chauffement 4,26 km \u00e0 5:45/km (FC 144,3), puis 4\u00d72 km \u00e0 allure marathon avec 2 min de r\u00e9cup entre chaque, GPS perdu sous le tunnel (rep\u00e8res uniquement via les intervalles manuels du Garmin). BLOC 1 : 4:54/km moy (splits tr\u00e8s irr\u00e9guliers 5:34 puis 4:15, sur-correction apr\u00e8s d\u00e9part trop prudent) FC 161,6. BLOC 2 : 5:29/km (5:31 et 5:28, tr\u00e8s r\u00e9gulier mais jug\u00e9 trop lent) FC 152,3. BLOC 3 : 5:05/km (5:41 puis 4:29, \u00e0 nouveau irr\u00e9gulier) FC 163,2. BLOC 4 : 5:07/km (5:07 et 5:06, le mieux ex\u00e9cut\u00e9) FC 165,5. RE 171. Douleur au pied gauche r\u00e9apparue apr\u00e8s 10-12 km (aucune douleur avant) \u2014 boucle de retour \u00e9court\u00e9e par pr\u00e9caution, retour direct sans terminer le parcours pr\u00e9vu. Novablast 5 V (20 \u2192 34 km).",
        "pr":8,"ach":8,"pr_detail":[],
        "revue":_REVUE_FICHIER}
        arr[4]["sous"]="Échauffement puis 4×2 km à allure marathon dans le tunnel de la Croix-Rousse (frais), récup 2 min entre chaque."
        arr[4]["metriques"]={"Distance":"14,09 km","Durée":"1h16","Allure":"4×2 km entre 4:54 et 5:29/km","FC":"152-165 sur les blocs","RPE":"7","Type":"Allure marathon"}
        arr[4]["objectif"]="Premier vrai test de l'allure marathon (5:20/km) en conditions réelles, à l'abri de la canicule. Le tunnel offre la fraîcheur mais pas de signal GPS : le repère devient la sensation et la FC, pas l'allure affichée en direct."
        arr[4]["struct"]=[{"nom":"Échauffement","txt":"4,26 km en EF à 5:45/km."},{"nom":"4 × 2 km","txt":"Dans le tunnel, à sensation d'allure marathon. Récupération 2 min en trot très lent entre chaque bloc."},{"nom":"Retour au calme","txt":"Terminé écourté sur gêne au pied réapparue — bonne décision de ne pas boucler la boucle prévue."}]
        arr[4]["legende"]=[{"c":GREEN,"l":"Échauffement"},{"c":BLUE,"l":"Bloc AM"},{"c":VIOLET,"l":"Récup"}]
        arr[4]["benefices"]="Premier repère chiffré du couple allure/FC à allure marathon, indispensable pour suivre la progression vers Nice."
        arr[4]["coach"]=[{"titre":"Le vrai repère : bloc 4 (5:07/km à FC 165,5)","texte":"C'est ton bloc le mieux exécuté, allures très régulières (5:07 puis 5:06). À FC 165, tu produis 5:07/km \u2014 plus vite que sur le marathon (5:15 à FC 163-167). C'est un signal encourageant de progression, même s'il reste au-dessus de ta cible FC (155-158)."},{"titre":"Le bloc 2 est le plus instructif","texte":"À FC 152,3 (dans ta cible), tu as produit 5:29/km. C'est l'information la plus fiable de la séance : elle situe précisément où tu en es aujourd'hui à FC cible, sans l'a-coup du repère GPS perdu."}]
        arr[4]["vigilance"]="Douleur au pied réapparue après 10-12 km, sur une séance à allure soutenue \u2014 contrairement aux EF faciles qui ne la déclenchent pas. C'est une information utile : le pied tolère l'endurance mais pas encore l'allure marathon prolongée. Repos complet demain, décision sur la suite en fonction de la douleur."

    if n==32:
        # Semaine reconstruite sur les enseignements de S31, puis reorganisee
        # a la demande de Loic : allure marathon remplacee par un fractionne
        # 8x400m (le 03/08 est saute, Loic ne court pas ce jour-la), longue
        # avancee au samedi. Ordre final : fractionne / EF / EF+lignes droites
        # / sortie longue, PPG+mobilite groupees vendredi, repos dimanche.

        # Construction du fractionne AVEC segments (le champ qui dessine la
        # barre de deroule) : c'est precisement ce qui manquait sur l'ancienne
        # seance VMA du 30/07, corrige au build 143 pour l'allure marathon,
        # applique ici des le depart pour ne pas reproduire le trou.
        _fr_raw=[{"nom":"Échauffement","role":"20 min progressif + 3 lignes droites.","duree":1200,"couleur":"vert","bloc":"—","hauteur":30}]
        for _i in range(8):
            _fr_raw.append({"nom":f"400 m #{_i+1}","role":"3:45-3:50/km (~1min30 au 400 m).","duree":90,"couleur":"rouge","bloc":f"×8","hauteur":88})
            if _i<7:
                _fr_raw.append({"nom":"Récup","role":"1min30 en trot VRAIMENT lent — FC doit redescendre.","duree":90,"couleur":"orange","bloc":"↓","hauteur":30})
        _fr_raw.append({"nom":"Retour au calme","role":"10 min très facile.","duree":600,"couleur":"vert","bloc":"—","hauteur":28})
        _fr_seg=segs(_fr_raw)

        arr[0]["date"]="2026-08-04"
        arr[0]["titre"]="Fractionné 8×400 m"
        arr[0]["type"]="VMA / vitesse"
        arr[0]["sport"]="Course à pied"
        arr[0]["accent"]=RED
        arr[0]["fill"]=58
        arr[0]["cat"]="seuil"
        arr[0]["rpe"]=6.5
        arr[0]["chaussure"]="ASICS Magic Speed 4"
        arr[0]["sous"]="8×400 m à 3:45-3:50/km, récup 1min30 en trot lent. Remplace l'allure marathon initialement prévue — décision de Loïc, ta vitesse (92/99 sur le radar) n'est pas le point faible, mais la séance est jouable en isolé."
        arr[0]["metriques"]={"Distance":"~9 km","Durée":"~50 min","Allure":"3:45-3:50/km sur le 400 m","FC":"170-180 en fin de série","RPE":"7","Type":"VMA"}
        arr[0]["objectif"]="Stimulus VO2max classique. L'allure se situe entre ton seuil (4:24-4:31/km) et ta pointe absolue (2:57/km) : assez rapide pour être productif, assez modéré pour répéter 8 fois sans s'effondrer."
        arr[0]["struct"]=[
          {"nom":"Échauffement","txt":"20 min progressif + 3 lignes droites."},
          {"nom":"8 × 400 m","txt":"3:45-3:50/km, récupération 1min30 en trot RÉELLEMENT lent — pas en marche rapide, pas à 5:00/km. Laisse le cardio redescendre franchement entre les répétitions."},
          {"nom":"Retour au calme","txt":"10 min très facile."}]
        arr[0]["legende"]=[{"c":GREEN,"l":"Échauffement / récup"},{"c":RED,"l":"400 m"},{"c":ORANGE,"l":"Récup active"}]
        arr[0]["benefices"]="Puissance aérobie maximale et économie de course à haute vitesse."
        arr[0]["coach"]=[
          {"titre":"La récup doit être un vrai trot lent","texte":"Le 21/07, tes récups à 5:00/km avaient fait dériver la séance vers du tempo au lieu d'une VMA propre. Ici, marche ou trot très lent entre chaque 400 — c'est ce qui fait la différence entre 8 répétitions productives et une séance qui tourne à l'épreuve d'endurance."},
          {"titre":"Ce n'est pas ta priorité du moment, et c'est assumé","texte":"Ton radar situe ta vitesse à 92/99 contre 42/99 pour l'allure marathon. Cette séance ne fait pas progresser ce qui te limite pour Nice — mais une séance isolée ne casse rien, tant qu'elle ne s'empile pas avec une autre séance dure."}]
        arr[0]["vigilance"]="Si le pied se manifeste pendant l'échauffement, tu bascules en EF et tu gardes cette séance pour plus tard."
        arr[0]["segments"]=_fr_seg

        arr[0]["realise"]={"statut":"partiel","km":10.05,"temps":"1h01","allure":"5:03/km (phase finale)","fc_moy":158,"fc_max":182,"re":123,"cadence":173,"elevation_gain":39,"temp":31,"rpe_ressenti":8,
        "commentaire":"Fractionn\u00e9 8\u00d7400m en canicule (vigilance orange active) \u00b7 d\u00e9part 8h52, ~31\u00b0C ressentis \u00b7 10,05 km, 1h01 total dont 11 min de pauses non pr\u00e9vues (temps de mouvement 50,8 min). \u00c9chauffement d\u00e9j\u00e0 chaud : 2,72 km \u00e0 FC 165 en fin. SEULEMENT 6 R\u00c9P\u00c9TITIONS SUR 8 r\u00e9alis\u00e9es : allures produites 3:30-3:57/km (dans la cible voire plus rapide), mais r\u00e9cup\u00e9ration impossible entre les blocs \u2014 FC rest\u00e9e coll\u00e9e \u00e0 175-180 m\u00eame en phase de r\u00e9cup, obligeant \u00e0 des pauses suppl\u00e9mentaires de ~2-3 min (4 pauses d\u00e9tect\u00e9es). A termin\u00e9 les 10 km en allure tempo mod\u00e9r\u00e9e (5:03/km) pour FC moyenne 166 \u2014 co\u00fbt cardiaque d'un seuil pour une allure tempo. AUCUNE douleur au pied, y compris en fin de s\u00e9ance et en r\u00e9cup\u00e9ration. Magic Speed 4.",
        "pr":9,"ach":9,"pr_detail":[],
        "revue":_REVUE_FICHIER}
        # Mercredi : EF simple (reprend le contenu de l'ancien lundi, decale)
        arr[1]["date"]="2026-08-05"
        arr[1]["titre"]="Footing facile"
        arr[1]["chaussure"]="Clifton 10"
        arr[1]["sous"]="45-50 min très faciles, FC sous 145."
        arr[1]["objectif"]="Volume aérobie pur, sans intensité — le lendemain du fractionné."
        arr[1]["vigilance"]="Canicule toujours active (vigilance orange). Départ 6h30 maximum, FC seule pilote — ignore l'allure. Si la gêne au pied est présente dès les premiers pas du matin, cette séance saute."
        arr[1]["realise"]={"statut":"fait","km":10.04,"temps":"1h00","allure":"6:01/km","fc_moy":134,"fc_max":166,"re":34,"cadence":173,"elevation_gain":37,"temp":25,"rpe_ressenti":4,
        "decouplage":{"pct":4.29,"bpm":1.9,"fen_min":44,"temp":25,"attendu":6,"p1":"5:55/km","fc1":133,"p2":"5:58/km","fc2":135,"qualite":"incertain","algo":"decoup-v1"},
        "commentaire":"EF tr\u00e8s facile \u00b7 d\u00e9part 8h16, ~25\u00b0C (moins chaud que la veille) \u00b7 10,04 km en 1h00 \u00e0 6:01/km, FC moyenne 134. Corps de sortie tr\u00e8s stable (9,67 km \u00e0 5:59/km, FC 88-150). SPRINT FINAL de 336 m (confirme le ressenti \"300 derniers m\u00e8tres\") : 4:42/km moyenne, pointe \u00e0 3:36/km, FC mont\u00e9e \u00e0 166 \u2014 test du pied r\u00e9ussi, aucune g\u00eane. Fatigue musculaire ressentie malgr\u00e9 l'allure facile, attribu\u00e9e au fractionn\u00e9 interrompu de la veille en canicule. Chauss\u00e9 en Novablast 5 J (la 5 V \u00e9tait pr\u00e9vue, \u00e9cart mineur sans cons\u00e9quence, les deux paires sont saines).",
        "pr":0,"ach":0,"pr_detail":[],
        "revue":_REVUE_FICHIER}

        # Jeudi : EF + lignes droites (decale du mercredi)
        arr[2]["date"]="2026-08-06"
        arr[2]["realise"]={"statut":"fait","km":10.09,"temps":"1h00","allure":"5:56/km","fc_moy":140,"fc_max":170,"re":56,"cadence":175,"elevation_gain":36,"temp":26,"rpe_ressenti":4,
        "decouplage":{"pct":-0.61,"bpm":-1.2,"fen_min":43,"temp":26,"attendu":8,"p1":"6:06/km","fc1":138,"p2":"6:08/km","fc2":137,"qualite":"incertain","algo":"decoup-v1"},
        "commentaire":"EF + 6\u00d7100 m, r\u00e9cup 30 sec active \u00b7 d\u00e9part 9h15, ~26\u00b0C \u00b7 10,09 km en 1h00. CORPS EF (9,46 km) tr\u00e8s ma\u00eetris\u00e9 : profil en 3 tiers 6:09 \u2192 6:13 \u2192 5:51/km avec FC 137 \u2192 137 \u2192 141 \u2014 mont\u00e9e en r\u00e9gime progressive et quasi gratuite en co\u00fbt cardiaque (le \"diesel\" d\u00e9crit). D\u00e9couplage -0,61 % (quasi nul, sens n\u00e9gatif) pour 8 % attendu \u2014 aucune d\u00e9rive. Sur les 6\u00d7100 m : accel\u00e9rations ressenties comme naturelles et non forc\u00e9es, progressives, dernier r\u00e9p\u00e9t\u00e9 volontairement moins vite que l'avant-dernier par prudence (3\u00e8me sortie de la semaine). Deux segments confirm\u00e9s dans les donn\u00e9es \u00e0 3:42-3:46/km, FC 162-168. RPE bas (4/10) pour une s\u00e9ance incluant des accel\u00e9rations. ZERO douleur au pied. Chauss\u00e9 en HOKA Clifton 10 (paire la plus us\u00e9e du parc).",
        "pr":1,"ach":1,"pr_detail":[],
        "revue":_REVUE_FICHIER}

        # Vendredi : repos initialement prevu, mais Loic est sorti courir --
        # sortie non planifiee, travail volontaire de retenue cardiaque (cible max 135 bpm).
        arr[4]["date"]="2026-08-07"
        arr[4]["titre"]="Sortie non planifiée — retenue cardiaque"
        arr[4]["type"]="EF retenue"
        arr[4]["sport"]="Course à pied"
        arr[4]["accent"]=EF_COLOR
        arr[4]["fill"]=30
        arr[4]["cat"]="classique"
        arr[4]["rpe"]=3
        arr[4]["chaussure"]="ASICS Novablast 5 V"
        arr[4]["sous"]="Repos initialement prévu, remplacé par une sortie décidée sur le moment : cible personnelle FC moyenne ≤135 bpm, sans contrainte d'allure."
        arr[4]["objectif"]="Test volontaire de retenue cardiaque pure — pas une séance du plan, une initiative personnelle pour travailler exactement le point faible identifié sur le radar (allure marathon 42/99)."
        arr[4]["struct"]=[{"nom":"Corps","txt":"Footing piloté au cardio, cible FC moyenne ≤135 bpm, allure laissée libre en conséquence."}]
        arr[4]["legende"]=[{"c":EF_COLOR,"l":"EF piloté FC — RPE 3"}]
        arr[4]["benefices"]="Discipline de retenue cardiaque, base aérobie, travail direct du point faible du profil (allure marathon)."
        arr[4]["coach"]=[{"titre":"4e jour consécutif, décision perso","texte":"Ni la séance ni le jour n'étaient au plan — c'est une initiative de Loïc, pas une consigne. Pris en compte comme tel dans le calcul de charge de la semaine."}]
        arr[4]["vigilance"]="4e sortie consécutive : c'est un signal de charge à surveiller sur les jours suivants, même si le pied est resté silencieux et l'intensité très faible."
        arr[4]["realise"]={"statut":"fait","km":10.09,"temps":"1h00","allure":"5:58/km","fc_moy":132,"fc_max":149,"re":28,"cadence":176,"elevation_gain":43,"rpe_ressenti":3,
        "commentaire":"Sortie non planifi\u00e9e (repos initialement pr\u00e9vu) \u00b7 d\u00e9part 7h49, matin frais \u00b7 10,09 km en 1h00 (moving), 5:58/km, FC moyenne 132 (cible \u00e9tait \u2264135), FC max 149. 4e sortie cons\u00e9cutive. Cadence 176. Tr\u00e8s peu transpir\u00e9 malgr\u00e9 la canicule ambiante \u2014 attribu\u00e9 \u00e0 l'heure matinale. ~1L d'eau bu pendant la sortie. AUCUNE douleur au pied. Loïc vise de passer sous 130 bpm mais peine \u00e0 le faire sans d\u00e9passer 6:00/km. ASICS Novablast 5 V (paire r\u00e9serv\u00e9e Nice, toujours en rodage, ~56 km).",
        "pr":0,"ach":0,"pr_detail":[],
        "revue":_REVUE_FICHIER}

        # Samedi : sortie longue (avancee du dimanche, a la demande de Loic)
        arr[3]["date"]="2026-08-08"
        arr[3]["sous"]="16 km continus en EF, sans bloc allure marathon. On rallonge la durée avant de rajouter de l'intensité."
        arr[3]["objectif"]="Réduite de 26 à 16 km et sans bloc allure marathon. Raison : le pied n'a pas encore dépassé une heure de course sans se manifester. On teste d'abord la durée en EF pure, on recombinera durée et allure marathon en S33 si tout va bien."
        arr[3]["coach"]=[{"titre":"La durée avant l'intensité","texte":"Ton pied se réveille sur l'allure soutenue prolongée, pas sur l'EF facile. On vérifie donc qu'il encaisse 1h35 en EF avant de recombiner les deux contraintes."}]
        arr[3]["vigilance"]="Canicule toujours active. Départ à l'aube non négociable (6h30 max), électrolytes dès le départ. Si la gêne apparaît, tu rentres — même à 10 km. Cette séance est un test de tolérance, pas un objectif kilométrique."
        # arr[5] (Mobilité) devient le 2e jour de repos, samedi
        arr[5]["date"]="2026-08-08"
        arr[5]["titre"]="Repos complet (2)"
        arr[5]["type"]="Repos"
        arr[5]["chaussure"]=None
        arr[5]["sous"]="Deuxième jour de repos avant la boucle de Saint-Étienne de demain."
        arr[5]["objectif"]="Fraîcheur maximale avant un effort vallonné et technique : 27 km, 650 m D+, descentes techniques à Rochetaillée."
        arr[5]["vigilance"]="Aucune sollicitation. Prépare l'itinéraire, l'hydratation et les chaussures adaptées au terrain."

        # arr[3] (Sortie longue) devient la boucle de Saint-Étienne, dimanche
        arr[3]["date"]="2026-08-09"
        arr[3]["titre"]="Boucle de Saint-Étienne — trail vallonné"
        arr[3]["type"]="Sortie longue"
        arr[3]["sport"]="Trail"
        arr[3]["accent"]=BLUE
        arr[3]["fill"]=72
        arr[3]["cat"]="sortie-longue"
        arr[3]["rpe"]=6.0
        arr[3]["chaussure"]="ASICS Novablast 5 J"
        arr[3]["sous"]="Remplace la sortie longue initialement prévue (16 km plat) — projet perso, boucle vallonnée autour de Saint-Étienne."
        arr[3]["metriques"]={"Distance":"~27 km","Durée":"~3h-3h30","Allure":"EF trail, libre","FC":"< 155 bpm","D+":"~650 m","RPE":"5-6","Type":"Trail vallonné"}
        arr[3]["objectif"]="Sortie plaisir et exploration, plus longue et plus technique que le plan initial. Bon test grandeur nature pour SaintExpress (45 km, novembre) : gestion de l'effort sur la durée, terrain varié, descentes techniques."
        arr[3]["struct"]=[
          {"nom":"Itinéraire","txt":"La Terrasse → Parc de Montaud → Crêt de Sixte-Soleils → Bellevue → Rochetaillée → Terrenoire → Geoffroy-Guichard → La Terrasse."},
          {"nom":"Corps","txt":"Allure libre, entièrement pilotée au ressenti et à la FC. Marche autorisée et même recommandée dans les portions raides — c'est la norme en trail, pas un échec."},
          {"nom":"Descentes techniques","txt":"Rochetaillée et le retour côté Terrenoire sont les portions les plus exigeantes pour les quadriceps et pour l'appui du pied. Ralentis si besoin, la sécurité prime sur le chrono."}]
        arr[3]["legende"]=[{"c":BLUE,"l":"Trail vallonné"}]
        arr[3]["benefices"]="Volume et dénivelé spécifiques trail, en vue de SaintExpress. Gestion de l'effort sur terrain varié et sur la durée."
        arr[3]["coach"]=[
          {"titre":"Deux vigilances, un projet qui reste le tien","texte":"650 m de D+ en descentes techniques sollicite fortement les quadriceps — ta vigilance historique. Et le pied n'a pas encore été testé sur terrain instable avec appuis de travers. Aucune des deux ne remet en cause le projet : elles demandent juste d'écouter le corps en descente."},
          {"titre":"Le repère simple","texte":"Si le pied ou les quadriceps parlent fort dans la descente de Rochetaillée, coupe par le chemin le plus court plutôt que de boucler la totale. Une sortie écourtée reste une excellente sortie."}]
        arr[3]["vigilance"]="Chaussures à accroche (Cascadia) recommandées pour la stabilité en descente. Hydratation et un peu de nutrition pour 3h+ d'effort. Écoute les quadriceps et le pied en descente technique."

        arr[3]["realise"]={"statut":"fait","km":27.01,"temps":"3h16 (3h48 total)","allure":"7:16/km","fc_moy":145,"fc_max":176,"re":246,"cadence":164,"elevation_gain":662,"rpe_ressenti":6,
        "commentaire":"Boucle verte de Saint-Etienne avec Didier (beau-pere, arret au 20e) et Yannis (arret au 23e) - depart 8h16. 27,01 km, 662 m D+, 3h16 de mouvement (3h48 ecoulees), allure moyenne 7:16/km, FC moyenne 145, FC max 176, effort relatif 246, 2196 kcal. Sortie plaisir / famille assumee : montees volontairement tres lentes pour rester avec le groupe. Fin difficile ressentie vers le km 24-25 (plein soleil, grosse chaleur), puis regain sur les derniers kilometres. ZERO douleur au pied, y compris a l'arrivee apres 27 km et 662 m D+. Porte en ASICS Novablast 5 J (route) et non en Cascadia 19 (trail) comme prevu au plan.",
        "pr":0,"ach":1,"pr_detail":[],
        "revue":_REVUE_FICHIER}

META=[
(24,'reprise','Récupération',28,'Légère','—',"Absorber La Circaète : repos actif, footings très faciles, mobilité du dos."),
(25,'reprise','Reprise & déblocage',52,'Modérée','≈ 85 % facile · 15 % qualité légère',"Relancer une structure : ré-ancrer le vrai easy, vivacité, premier contact allure marathon, longue + carburant."),
(26,'general','Allègement + prépa Déraille',35,'Allégée','≈ 78 % facile · 22 % spécifique',"Volume réduit, une séance spécifique vallonnée avec répétition nutrition : on prépare la Déraille sans entamer la reprise."),
(27,'general','Semaine course — Déraille',45,'Course','—',"Affûtage court (3 footings) + Trail Déraille au Lac des Sapins le 5 juillet. Objectif C, plaisir & test nutrition. (21 km allégés + 24 km course.)"),
(28,'general','Récupération post-Déraille',36,'Récup','100 % facile · récupération active',"Semaine de récupération après le Trail Déraille — footings très faciles, zéro intensité. Le bloc seuil est décalé à S30 pour laisser les jambes assimiler le D+ et la chaleur. La récup n'est pas du temps perdu : c'est là que les adaptations se construisent."),
(29,'general','Seuil découverte',62,'Soutenue','≈ 80 % facile · 20 % qualité',"Reprise progressive après la semaine de récup : premier vrai contact avec le seuil (2 blocs courts) + longue qui reprend du volume avec finish AM."),
(30,'general','Semaine ViaRhôna',72,'Soutenue','≈ 92 % facile · 8 % rythme léger',"Semaine organisée autour du projet ViaRhôna 40 km (jeudi). Une seule touche de rythme (lignes droites mardi), repos la veille, récup après. Seuil et côtes retirés : le 40 km EST la charge de la semaine."),
(31,'general','Absorption marathon · canicule',45,'Légère','≈ 88 % facile · une touche de vitesse',"Semaine d'absorption du marathon ViaRhôna sous dôme de chaleur (36-38°C mercredi et jeudi). Qualité faite dès le lundi (6×30 en negative split), mardi devenu repos. Test 10 km reporté : un contre-la-montre à J+5 d'un marathon mesurerait la fatigue, pas la forme."),
(32,'seuil','Reprise progressive · retenue à 5:20',52,'Modérée','≈ 88 % facile · travail de retenue',"Semaine bouclée à 5 sorties (dont 2 non planifiées) pour 67,3 km, 817 m D+ et un effort relatif cumulé de 487 — la plus grosse semaine depuis celle de ViaRhôna. Le pied est ressorti SILENCIEUX de tout, y compris des 27 km / 662 m D+ de dimanche : le dossier ouvert le 23/07 est clos. Deux enseignements opposés : vendredi, retenue parfaite (132 bpm tenus sur 10 km avec une cible chiffrée) ; dimanche, dérive complète sur les 6 derniers km (7:15 → 5:07/km, FC 139 → 166) dès que le cadre social a disparu. La leçon tient en une phrase : ta retenue existe quand elle est chiffrée, elle disparaît quand elle est laissée au ressenti."),
(33,'seuil','Allègement',64,'Légère','≈ 85 % facile · 15 % qualité',"Récupération avant le pic pré-USA — et première semaine où la retenue devient une consigne chiffrée sur CHAQUE sortie, pas seulement sur les séances de qualité. Après une S32 à 5 sorties dont un gros trail (effort relatif 246), le lundi est un vrai repos, non négociable. Le seuil 2×10 reste, la longue 18 km se court plafonnée en FC — l'objectif n'est pas le chrono, c'est de finir sans avoir accéléré."),
(34,'seuil','Pic pré-USA',82,'Élevée','≈ 78 % facile · 22 % qualité',"Plus gros bloc avant le voyage : seuil + longue 28 km dont 12 AM (gate de la reine)."),
(35,'seuil','Transition voyage',66,'Modérée','≈ 82 % facile · 18 % qualité',"On lève le pied, on prépare le corps au déload du voyage."),
(36,'usa','USA — maintien',42,'Légère','100 % facile',"Voyage : footings faciles + randos. Entretien, zéro structure."),
(37,'usa','USA — maintien',38,'Légère','100 % facile',"Courir quand c'est possible, temps de pied en montagne."),
(38,'usa','USA — maintien',38,'Légère','100 % facile',"Garder le moteur chaud sans chercher la progression."),
(39,'usa','Retour & réacclim.',45,'Légère','≈ 95 % facile',"Retour le 26/09 : absorber le décalage, réveiller la longue."),
(40,'marathon','Re-construction post-USA',64,'Soutenue','≈ 82 % facile · 18 % qualité',"Ré-entrée PROGRESSIVE : seuil doux + longue 20 km dont 6 AM. On ne saute pas direct au pic."),
(41,'marathon','Allure marathon',76,'Élevée','≈ 80 % facile · 20 % qualité',"Une seule grosse séance : 3×4 km AM. Longue en endurance pure."),
(42,'marathon','Pic — séance reine',88,'Maximale','≈ 82 % facile · 18 % qualité',"Pic à ton plafond : longue reine 30 km dont 14 AM, seul gros stimulus."),
(43,'marathon','Dernier gros bloc',76,'Élevée','≈ 80 % facile · 20 % qualité',"Dernière grosse spécifique (2×6 km AM), longue en endurance, on commence à fraîchir."),
(44,'affutage','Affûtage 1',54,'Modérée','≈ 80 % facile · 20 % qualité',"Décharge nette + une seule séance d'intensité (seuil 30, conditionnel) : on évacue la fatigue."),
(45,'affutage','Semaine course',58,'Course','—',"Affûtage final + Marathon de Nice le 8 nov. Objectif A. (16 km décharge + 42 km course.)"),
(46,'transition','Récup marathon',22,'Légère','100 % facile',"Récupération marathon très progressive : footings très faciles, mobilité."),
(47,'transition','Rappels trail',55,'Modérée','≈ 80 % facile · 20 % trail',"Réveil trail : descente, nocturne — sert aussi le D+ de la SaintExpress."),
(48,'saintexpress','Semaine SaintExpress',60,'Course','—',"Mise en jambe + SaintExpress 45 km (28-29 nov). Objectif B, au plaisir. (15 km + 45 km course.)"),
(49,'regen','Coupure active',30,'Légère','100 % facile',"Récupération de fin de saison : course libre."),
(50,'regen','Reprise libre',42,'Légère','≈ 95 % facile',"Footings plaisir, on réécoute le corps."),
(51,'regen','Base d\'hiver',50,'Modérée','≈ 85 % facile · 15 % qualité',"Remise en route de la base aérobie + première qualité."),
(52,'regen','Fêtes — entretien',38,'Légère','100 % facile',"Entretien léger pendant les fêtes."),
(53,'regen','Bilan & 2027',30,'Légère','≈ 95 % facile',"Clôture de saison, bilan, pistes 2027."),
]
SEMAINES=[{"num":n,"phase":p,"theme":t,"km":k,"statut":"ouverte","charge":c,"repartition":r,"objectif":o} for (n,p,t,k,c,r,o) in META]
# Revues de semaine post-bilan

# ── S33 : semaine en cours ────────────────────────────────────────────
# Loic a decale d'un jour : lundi laisse en repos (recuperation du trail
# de dimanche encore incomplete), et le mardi consacre a un footing
# cardio-plafonne plutot qu'au seuil, qui glisse au jeudi.
for n, arr in list(SEANCES_BY_WEEK.items()):
    if n != "33":
        continue
    arr[0]["realise"]={"statut":"skipped","km":0,"temps":"—","allure":"—","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Repos choisi. Sensations encore lourdes 24 h après le trail de 27 km — décision de laisser un jour de plus.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}
    arr[1]["titre"]="Footing facile — cardio plafonné"
    arr[1]["type"]="EF aérobie"
    arr[1]["date"]="2026-08-11"
    arr[1]["chaussure"]="Clifton 10"
    arr[1]["objectif"]="Footing de reprise à FC plafonnée à 140 bpm. Le seuil 2×10 est décalé au jeudi."
    arr[1]["realise"]={"statut":"fait","km":10.07,"temps":"1h02","allure":"6:09/km","fc_moy":138,"fc_max":152,"re":53,
      "cadence":175,"elevation_gain":29,"kcal":756,"rpe_ressenti":3,
      "commentaire":"Objectif 140 bpm annoncé avant le départ. Fatigue musculaire nette sur les 6 premiers kilomètres, puis les jambes se sont dépliées. Aucune recherche de chrono, aucune accélération. Zéro douleur au pied.",
      "pr":0,"ach":1,"pr_detail":[],
      "splits":[{"km":1,"allure":"6:18","fc":129},{"km":2,"allure":"6:03","fc":137},{"km":3,"allure":"6:12","fc":141},
                {"km":4,"allure":"6:08","fc":139},{"km":5,"allure":"6:15","fc":139},{"km":6,"allure":"6:13","fc":137},
                {"km":7,"allure":"6:09","fc":138},{"km":8,"allure":"6:05","fc":143},{"km":9,"allure":"6:07","fc":142},
                {"km":10,"allure":"6:03","fc":140}],
      "revue":_REVUE_FICHIER}
    # Contrainte annoncee par Loic : depart pour La Rochelle mercredi 12,
    # retour a Lyon dimanche 16 en fin de journee apres 6h30 de route.
    # Trois creneaux disponibles : mercredi matin avant le depart, une
    # sortie sur place, et eventuellement un deverrouillage au retour.
    # ARBITRAGE : le seuil 2x10 est sacrifie, pas la sortie longue. Le
    # seuil est deja une force (79/99) ; l'allure marathon est le point
    # faible (42/99) et l'objectif est a 12 semaines. On fusionne donc
    # longue et travail specifique dans la seance de La Rochelle.
    arr[2]["date"]="2026-08-12"
    arr[2]["chaussure"]="Novablast 5 J"
    arr[2]["realise"]={"statut":"fait","km":10.2,"temps":"59:16","allure":"5:49/km","fc_moy":140,"fc_max":186,"re":61,
      "cadence":175,"elevation_gain":36,"kcal":774,"rpe_ressenti":5,
      "commentaire":"EF puis 6x100 m avec 30 s de récup, en cherchant le negative split. Séance du matin avant le départ pour La Rochelle. Novablast 5 J.",
      "pr":5,"ach":5,"pr_detail":[],
      "splits":[{"km":1,"allure":"6:24","fc":131},{"km":2,"allure":"6:07","fc":133},{"km":3,"allure":"5:57","fc":142},
                {"km":4,"allure":"5:58","fc":139},{"km":5,"allure":"6:08","fc":139},{"km":6,"allure":"5:45","fc":141},
                {"km":7,"allure":"5:57","fc":124},{"km":8,"allure":"5:51","fc":140},{"km":9,"allure":"5:50","fc":146}],
      "revue":_REVUE_FICHIER}
    arr[2]["sous"]="Avant la route — jambes déverrouillées."
    arr[2]["objectif"]="Footing court avec lignes droites, <strong>le matin avant les 6h30 de voiture</strong>. Rouler les jambes avant une longue position assise vaut mieux que partir raide. FC plafond 145."
    arr[3]["date"]="2026-08-14"
    arr[3]["chaussure"]="Novablast 5 V"
    arr[3]["titre"]="Longue + bloc allure marathon"
    arr[3]["sous"]="La Rochelle — la séance clé de la semaine."
    arr[3]["metriques"]={"Distance":"15 km","Durée":"~90 min","Allure":"6:00-6:15 puis 5:20/km","FC":"135-150 puis 148-160","RPE":"5-6","Type":"Longue + spécifique"}
    arr[3]["objectif"]="<strong>La séance à ne pas manquer cette semaine.</strong> Longue et travail d'allure marathon fusionnés : c'est le meilleur rendement possible sur trois créneaux. Terrain plat en bord de mer, idéal pour tenir une allure régulière. <strong>Le nombre à annoncer avant de partir : 5:20/km sur le bloc.</strong>"
    arr[3]["struct"]=[
      {"nom":"Échauffement","txt":"5 km très souples à 6:00-6:15/km, FC sous 145. Ne rien précipiter, surtout sur une jambe qui a voyagé la veille."},
      {"nom":"Bloc spécifique","txt":"<strong>5 à 6 km à 5:20/km</strong>, FC cible 148-160. Régularité avant tout : chaque kilomètre doit tomber entre 5:18 et 5:24. <strong>Descendre sous 5:15, c'est rater la séance</strong>, même en se sentant bien."},
      {"nom":"Retour au calme","txt":"4 à 5 km à allure facile, FC redescendue sous 145."},
      {"nom":"Conditions","txt":"Partir tôt : en août sur la côte, la chaleur monte vite et l'humidité est plus forte qu'à Lyon. Boire toutes les 15-20 min, électrolytes dès le départ."}]
    # Le graphique de structure lit 'segments', PAS 'struct'. Les deux
    # champs decrivent la meme seance et doivent etre reconstruits ensemble :
    # laisser les anciens segments de la longue 18 km affichait un contenu
    # qui n'avait plus rien a voir avec la seance prescrite.
    # Decoupage : 5 km d'echauffement (~31 min a 6:10), bloc de 5,5 km a
    # 5:20 (~29 min), 4,5 km de retour au calme (~28 min) = ~88 min.
    arr[3]["segments"]=[
      {"nom":"Échauffement","role":"5 km très souples à 6:00-6:15/km, FC sous 145.","duree":1860,"couleur":"vert","bloc":"—","hauteur":32,"debut":0,"fin":1860},
      {"nom":"Bloc allure marathon","role":"5 à 6 km à 5:20/km, FC 148-160. Chaque km entre 5:18 et 5:24.","duree":1760,"couleur":"orange","bloc":"🎯","hauteur":72,"debut":1860,"fin":3620},
      {"nom":"Retour au calme","role":"4 à 5 km à allure facile, FC redescendue sous 145.","duree":1680,"couleur":"vert","bloc":"—","hauteur":30,"debut":3620,"fin":5300}]
    arr[3]["date"]="2026-08-13"
    arr[3]["chaussure"]="ASICS Novablast 5 V"
    arr[3]["realise"]={"statut":"fait","km":11.36,"temps":"1h01:58","allure":"5:27/km","fc_moy":155,"fc_max":171,"re":128,
      "cadence":174,"elevation_gain":52,"kcal":887,"rpe_ressenti":6,
      "commentaire":"La Rochelle, terrain inconnu, bord de mer. Départ tôt mais déjà chaud. ~5h30 de sommeil après 7h de route la veille. Échauffement 2,27 km, bloc 6 km à allure marathon, retour au calme 3,09 km. Aucune douleur au pied ni aux jambes, fatigue générale ressentie.",
      "pr":0,"ach":0,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:54","fc":136},{"km":2,"allure":"5:26","fc":144},{"km":3,"allure":"5:20","fc":151},
                {"km":4,"allure":"5:15","fc":154},{"km":5,"allure":"5:11","fc":164},{"km":6,"allure":"5:19","fc":158},
                {"km":7,"allure":"5:22","fc":161},{"km":8,"allure":"5:13","fc":165},{"km":9,"allure":"5:42","fc":161},
                {"km":10,"allure":"5:34","fc":158},{"km":11,"allure":"5:38","fc":159}],
      "revue":_REVUE_FICHIER}
    # Samedi 15/08 : sortie non planifiee, ajoutee a la semaine. Loic a pu
    # s'eclipser le matin, sous la pluie, et a volontairement ecourte pour
    # ne pas hypothequer la journee. Le deverrouillage du dimanche reste
    # au programme, optionnel.
    import copy as _copy
    _sam=_copy.deepcopy(arr[4])
    _sam["id"]=6
    _sam["date"]="2026-08-15"
    _sam["titre"]="Sortie non planifiée — footing de liaison"
    _sam["type"]="EF aérobie"
    _sam["sous"]="La Rochelle, sous la pluie — écourtée volontairement."
    _sam["opt"]=False
    _sam["chaussure"]="ASICS Novablast 5 V"
    _sam["metriques"]={"Distance":"8 km","Durée":"48 min","Allure":"5:59/km","FC":"< 145","RPE":"3","Type":"Liaison"}
    _sam["objectif"]="Footing de liaison non planifié, écourté sur décision de Loïc pour préserver la journée et la récupération."
    _sam["struct"]=[{"nom":"Corps","txt":"8 km à allure facile, FC contenue sous 145. Aucune intensité recherchée."}]
    _sam["segments"]=[{"nom":"Footing de liaison","role":"8 km à allure facile, FC sous 145.","duree":2888,"couleur":"vert","bloc":"—","hauteur":32,"debut":0,"fin":2888}]
    _sam["realise"]={"statut":"fait","km":8.04,"temps":"48:08","allure":"5:59/km","fc_moy":139,"fc_max":152,"re":50,
      "cadence":175,"elevation_gain":39,"kcal":617,"rpe_ressenti":3,
      "commentaire":"La Rochelle sous la pluie, chaleur persistante. Nuits courtes (6-7 h) depuis le début du séjour. Fatigue générale marquée, aucune douleur. Séance volontairement écourtée pour préserver la journée.",
      "pr":2,"ach":2,"pr_detail":[],
      "splits":[{"km":1,"allure":"6:14","fc":130},{"km":2,"allure":"5:40","fc":134},{"km":3,"allure":"5:51","fc":145},
                {"km":4,"allure":"5:59","fc":147},{"km":5,"allure":"6:11","fc":136},{"km":6,"allure":"5:59","fc":140},
                {"km":7,"allure":"6:00","fc":141},{"km":8,"allure":"5:58","fc":141}],
      "revue":_REVUE_FICHIER}
    arr.append(_sam)
    arr[4]["date"]="2026-08-16"
    arr[4]["chaussure"]="ASICS Novablast 5 V"
    arr[4]["realise"]={"statut":"skipped","km":0,"temps":"—","allure":"—","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Non réalisée — retour de La Rochelle, 6h30 de route. Déverrouillage explicitement optionnel.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}

    # ── S34 : lundi decale, mardi requalifie ─────────────────────────────
    # Loic n'a pas couru lundi (chaleur + mauvaise nuit) et est sorti mardi
    # soir avec une amie. Objectif annonce : tenir 5:20. Realise : 5:09 de
    # moyenne. La seance prevue mardi etait un seuil 3x12 ; ce qui a ete
    # couru est un tempo continu, plus proche du seuil que de l'allure
    # marathon. On requalifie la fiche plutot que de la faire passer pour
    # une seance d'allure marathon reussie.
for n, arr in list(SEANCES_BY_WEEK.items()):
    if n != "34":
        continue
    arr[0]["realise"]={"statut":"skipped","km":0,"temps":"—","allure":"—","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Non réalisée — chaleur trop forte le matin et mauvaise nuit. Sortie reportée au mardi soir.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}
    arr[1]["titre"]="Tempo continu — sortie avec Edwige"
    arr[1]["type"]="Tempo / seuil"
    arr[1]["sous"]="Lyon, en soirée — objectif annoncé 5:20."
    arr[1]["chaussure"]="ASICS Novablast 5 J"
    arr[1]["metriques"]={"Distance":"12 km","Durée":"62 min","Allure":"5:09/km","FC":"162 moy / 182 max","RPE":"6-7","Type":"Tempo continu"}
    arr[1]["realise"]={"statut":"fait","km":12.04,"temps":"1h02:11","allure":"5:09/km","fc_moy":162,"fc_max":182,"re":173,
      "cadence":171,"elevation_gain":22,"kcal":917,"rpe_ressenti":6,
      "commentaire":"Sortie du soir avec une amie, plus frais que le matin. Objectif annoncé : tenir l'allure marathon 5:20. Sensations bonnes du début à la fin, aucune douleur. Effet des deux jours de repos nettement ressenti.",
      "pr":45,"ach":45,"pr_detail":[],
      "splits":[{"km":1,"allure":"4:58","fc":148},{"km":2,"allure":"4:53","fc":160},{"km":3,"allure":"5:15","fc":157},
                {"km":4,"allure":"5:21","fc":160},{"km":5,"allure":"5:29","fc":158},{"km":6,"allure":"5:24","fc":162},
                {"km":7,"allure":"5:12","fc":165},{"km":8,"allure":"5:11","fc":167},{"km":9,"allure":"5:25","fc":167},
                {"km":10,"allure":"5:08","fc":168},{"km":11,"allure":"5:04","fc":166},{"km":12,"allure":"4:34","fc":166}],
      "revue":_REVUE_FICHIER}

    _S={str(x["id"]):x for x in arr}
    # Le graphique de mardi montrait encore le seuil 3x12 prescrit, alors
    # que la seance realisee est un tempo continu de 12 km. On resynchronise
    # segments avec ce qui a reellement ete couru.
    _S2=[x for x in arr if x["id"]==2][0]
    _S2["segments"]=[
      {"nom":"Mise en route","role":"2 km, montee en allure progressive.","duree":600,"couleur":"vert","bloc":"\u2014","hauteur":30,"debut":0,"fin":600},
      {"nom":"Tempo continu","role":"10 km \u00e0 5:09/km de moyenne, FC 162.","duree":3131,"couleur":"rouge","bloc":"\u2014","hauteur":76,"debut":600,"fin":3731}]
    # ── Restructuration de la fin de S34 (demandee par Loic) ─────────────
    # Contrainte : la longue passe au SAMEDI 22/08 (indisponible dimanche).
    # Arbitrage : mardi a deja coute 173 d'effort relatif, donc la seance
    # de vitesse de mercredi est ramenee a un format NEUROMUSCULAIRE court
    # (8x30 s, recup complete) au lieu d'un fractionne classique, et jeudi
    # perd ses lignes droites. Objectif : proteger la longue, qui est la
    # seance la plus importante des trois prochaines semaines.
    # ACWR projete au 22/08 : 1,26 (contre 1,31 avec un fractionne classique).

    # MERCREDI 19/08 — 100 m chronometres, 2 blocs
    _S["3"]["date"]="2026-08-19"
    _S["3"]["titre"]="Vitesse chronométrée — 2×(4×100 m)"
    _S["3"]["type"]="Neuromusculaire"
    _S["3"]["sous"]="Un temps a tenir, pas une allure a sentir."
    _S["3"]["chaussure"]="ASICS Magic Speed 4"
    _S["3"]["metriques"]={"Distance":"~9 km","Dur\u00e9e":"~46 min","Allure":"22,0 s / 100 m (16,4 km/h)","FC":"< 175, retour < 130","RPE":"4-5","Type":"Vitesse chronom\u00e9tr\u00e9e"}
    _S["3"]["objectif"]="M\u00eame principe que mercredi dernier \u2014 qualit\u00e9 sans casse musculaire \u2014 mais avec une cible <strong>chronom\u00e9tr\u00e9e sur 100 m</strong> plutot qu'une allure au ressenti. <strong>La note de la s\u00e9ance n'est pas la vitesse, c'est le nombre de r\u00e9p\u00e9titions tomb\u00e9es entre 21,5 et 22,5 s.</strong> Deux blocs de 4, s\u00e9par\u00e9s par 4 minutes de r\u00e9cup\u00e9ration compl\u00e8te : le second bloc doit \u00eatre aussi propre que le premier, pas plus rapide. <strong>Plafond d\u2019effort relatif : 90.</strong>"
    _S["3"]["struct"]=[
      {"nom":"\u00c9chauffement","txt":"20 min en endurance fondamentale, FC sous 140. Le tempo de mardi dernier (effort relatif 173) laisse encore des traces \u2014 rien ne presse."},
      {"nom":"Bloc 1 \u2014 4\u00d7100 m","txt":"4 r\u00e9p\u00e9titions de 100 m chronom\u00e9tr\u00e9es, <strong>cible 22,0 secondes</strong> (16,4 km/h). R\u00e9cup\u00e9ration 90 s en marche entre chaque."},
      {"nom":"R\u00e9cup\u00e9ration inter-blocs","txt":"<strong>4 minutes compl\u00e8tes</strong>, marche ou trot tr\u00e8s lent. FC sous 120 avant de repartir. C\u2019est ce qui permet au second bloc de partir aussi frais que le premier."},
      {"nom":"Bloc 2 \u2014 4\u00d7100 m","txt":"4 r\u00e9p\u00e9titions identiques, <strong>toujours 22,0 secondes</strong>. Le pi\u00e8ge : ce bloc semblera plus facile parce que tu es vraiment r\u00e9cup\u00e9r\u00e9 \u2014 la tentation sera d\u2019aller plus vite. R\u00e9sister \u00e0 cette tentation EST l\u2019exercice."},
      {"nom":"Retour au calme","txt":"10 min tr\u00e8s souple, FC redescendue sous 140."},
      {"nom":"Pourquoi 22 s et pas 30","txt":"Un temps sur 100 m se v\u00e9rifie au dixi\u00e8me de seconde \u00e0 chaque r\u00e9p\u00e9tition \u2014 contrairement \u00e0 une allure GPS sur 30 s, trop bruit\u00e9e pour \u00eatre fiable. Tu sauras 8 fois dans la s\u00e9ance si tu as tenu ta consigne, exactement l\u2019exercice qui te manque sur les sorties longues."}]
    _S["3"]["segments"]=[
      {"nom":"\u00c9chauffement","role":"20 min EF, FC sous 140.","duree":1200,"couleur":"vert","bloc":"\u2014","hauteur":30,"debut":0,"fin":1200},
      {"nom":"Bloc 1 \u2014 4\u00d7100 m","role":"4\u00d7100 m \u00e0 22,0 s, r\u00e9cup 90 s marche.","duree":358,"couleur":"rouge","bloc":"4\u00d7","hauteur":80,"debut":1200,"fin":1558},
      {"nom":"R\u00e9cup\u00e9ration inter-blocs","role":"4 min compl\u00e8tes, FC sous 120 avant de repartir.","duree":240,"couleur":"vert","bloc":"\u2014","hauteur":26,"debut":1558,"fin":1798},
      {"nom":"Bloc 2 \u2014 4\u00d7100 m","role":"4\u00d7100 m \u00e0 22,0 s, m\u00eame cible que le bloc 1.","duree":358,"couleur":"rouge","bloc":"4\u00d7","hauteur":80,"debut":1798,"fin":2156},
      {"nom":"Retour au calme","role":"10 min tr\u00e8s souple.","duree":600,"couleur":"vert","bloc":"\u2014","hauteur":28,"debut":2156,"fin":2756}]
    _S["3"]["vigilance"]="Si tu te r\u00e9veilles avec des jambes lourdes ou apr\u00e8s une nuit courte, <strong>remplace par une EF facile sans discuter</strong>. Samedi vaut dix fois cette s\u00e9ance."
    # Graphique resynchronise avec les temps REELLEMENT couru (chrono, pas la
    # cible). Durees derivees des laps Strava : echauffement+corps EF avant
    # le premier sprint, blocs de sprint aux temps mesures, retour au calme.
    _S["3"]["segments"]=[
      {"nom":"\u00c9chauffement + EF","role":"~4,8 km \u00e0 allure tr\u00e8s facile avec une amie.","duree":1709,"couleur":"vert","bloc":"\u2014","hauteur":24,"debut":0,"fin":1709},
      {"nom":"Bloc 1 \u2014 4\u00d7100 m","role":"4\u00d7100 m \u00e0 15-16 s (bien sous la cible de 22 s), r\u00e9cup 90 s.","duree":332,"couleur":"rouge","bloc":"4\u00d7","hauteur":82,"debut":1709,"fin":2041},
      {"nom":"R\u00e9cup\u00e9ration inter-blocs","role":"4 min exactement.","duree":240,"couleur":"vert","bloc":"\u2014","hauteur":26,"debut":2041,"fin":2281},
      {"nom":"Bloc 2 \u2014 4\u00d7100 m","role":"4\u00d7100 m \u00e0 16-19 s, plus lent et plus co\u00fbteux que le bloc 1.","duree":340,"couleur":"rouge","bloc":"4\u00d7","hauteur":68,"debut":2281,"fin":2621},
      {"nom":"Retour au calme","role":"Fin de sortie \u00e0 allure facile.","duree":222,"couleur":"vert","bloc":"\u2014","hauteur":22,"debut":2621,"fin":2843}]
    _S["3"]["realise"]={"statut":"fait","km":7.02,"temps":"47:23","allure":"6:45/km","fc_moy":137,"fc_max":182,"re":38,
      "cadence":86,"elevation_gain":27,"kcal":551,"rpe_ressenti":5,
      "commentaire":"Sortie avec une amie qui ne court pas beaucoup, allure tres facile d'ou seulement 7 km. Les 2x4x100 m ont neanmoins ete faits. Ressenti tres net de fatigue et de \u00ab tirage \u00bb sur le second bloc.",
      "pr":1,"ach":2,"pr_detail":[],
      "revue":_REVUE_FICHIER}


    # JEUDI 20/08 — EF simple, sans lignes droites
    _S["6"]["date"]="2026-08-20"
    _S["6"]["titre"]="Footing facile \u2014 sans lignes droites"
    _S["6"]["type"]="EF a\u00e9robie"
    _S["6"]["sous"]="Digestion \u2014 la vitesse a d\u00e9j\u00e0 \u00e9t\u00e9 faite mercredi."
    _S["6"]["chaussure"]="ASICS Novablast 5 V"
    _S["6"]["opt"]=False
    _S["6"]["metriques"]={"Distance":"10 km","Dur\u00e9e":"~62 min","Allure":"6:00-6:20/km","FC":"< 145","RPE":"3","Type":"EF"}
    _S["6"]["objectif"]="Footing de digestion, <strong>sans aucune acc\u00e9l\u00e9ration</strong>. Les lignes droites initialement pr\u00e9vues ici ont \u00e9t\u00e9 retir\u00e9es : la touche de vitesse est faite mercredi, en remettre jeudi compromettrait la longue."
    _S["6"]["struct"]=[
      {"nom":"Corps","txt":"10 km \u00e0 allure facile, FC plafonn\u00e9e \u00e0 145. Aucune ligne droite, aucune acc\u00e9l\u00e9ration, m\u00eame si les sensations sont bonnes."}]
    _S["6"]["segments"]=[
      {"nom":"Footing facile","role":"10 km, FC sous 145, sans acc\u00e9l\u00e9ration.","duree":3720,"couleur":"vert","bloc":"\u2014","hauteur":32,"debut":0,"fin":3720}]

    # VENDREDI 21/08 — repos complet
    _S["5"]["date"]="2026-08-21"
    _S["5"]["titre"]="Repos complet"
    _S["5"]["type"]="Repos"
    _S["5"]["sous"]="Non n\u00e9gociable avant la longue."
    _S["5"]["opt"]=False
    _S["5"]["metriques"]={"Dur\u00e9e":"\u2014","RPE":"0","Focus":"R\u00e9cup\u00e9ration","Type":"Repos"}
    _S["5"]["objectif"]="Repos complet. <strong>Tu as constat\u00e9 toi-m\u00eame que deux jours de repos transforment ton \u00e9tat de forme</strong> \u2014 celui-ci conditionne directement la qualit\u00e9 de samedi."
    _S["5"]["struct"]=[{"nom":"Consigne","txt":"Aucune course. Mobilit\u00e9 douce et sommeil si possible : c\u2019est la r\u00e9cup\u00e9ration, pas l\u2019entra\u00eenement, qui est ton facteur limitant en ce moment."}]
    _S["5"]["segments"]=[]

    # ── LOGS REELS : mercredi, jeudi, vendredi, samedi ────────────────────
    _S["3"]["realise"]={"statut":"fait","km":7.02,"temps":"47:23","allure":"6:45/km","fc_moy":137,"fc_max":182,"re":38,
      "cadence":86,"elevation_gain":27,"kcal":551,"rpe_ressenti":5,
      "commentaire":"Sortie avec une amie qui ne court pas beaucoup, allure tr\u00e8s facile d'o\u00f9 seulement 7 km. Les 2x4x100 m ont n\u00e9anmoins \u00e9t\u00e9 faits. Ressenti tr\u00e8s net de fatigue et de \u00ab tirage \u00bb sur le second bloc.",
      "pr":1,"ach":2,"pr_detail":[],
      "revue":_REVUE_FICHIER}

    _S["6"]["realise"]={"statut":"skipped","km":0,"temps":"\u2014","allure":"\u2014","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Non r\u00e9alis\u00e9e \u2014 courbatures et fatigue nette apr\u00e8s le 2x4x100m de mercredi. D\u00e9cision de rester sage avant la longue de samedi.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}

    _S["5"]["realise"]={"statut":"skipped","km":0,"temps":"\u2014","allure":"\u2014","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Non r\u00e9alis\u00e9e \u2014 courbatures encore pr\u00e9sentes. Deuxi\u00e8me jour de repos cons\u00e9cutif, priorit\u00e9 donn\u00e9e \u00e0 la fra\u00eecheur pour la longue de samedi.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}


    _S["4"]["realise"]={"statut":"fait","km":25.05,"temps":"2h03:35","allure":"4:56/km","fc_moy":166,"fc_max":183,"re":394,
      "cadence":177,"elevation_gain":59,"kcal":1878,"rpe_ressenti":8,
      "commentaire":"Lyon-Vaise -> Tr\u00e9voux par la voie bleue, 25 km (pas 29,5 \u2014 arr\u00eat \u00e0 Tr\u00e9voux, pas de prolongation \u00e0 Quincieux). Objectif annonc\u00e9 : \u00e9chauffement ~5:40, bloc 12 km \u00e0 5:20, retour au calme ~5:40. R\u00e9alis\u00e9 : jamais respect\u00e9, allure quasi constante 4:45-5:14/km du 1er au dernier km. Deux arr\u00eats ravitaillement (Fontaines-sur-Sa\u00f4ne ~79s, Neuville-sur-Sa\u00f4ne ~98s), tous deux bien g\u00e9r\u00e9s c\u00f4t\u00e9 nutrition/hydratation.",
      "pr":15,"ach":18,
      "pr_detail":["Record 1/2 marathon effectif : 1h46:18 (5:02/km) sur les 21,1 premiers km \u2014 6 min plus rapide que le PB officiel de 1h52:39"],
      "splits":[
        {"km":"1-5","allure":"4:59","fc":157},
        {"km":"6-10","allure":"4:58","fc":163},
        {"km":"11-15","allure":"4:52","fc":167},
        {"km":"16-20","allure":"4:49","fc":171},
        {"km":"21-25","allure":"5:01","fc":171}],
      "revue": _REVUE_FICHIER}
    

    # SAMEDI 22/08 — la longue, avancee d'un jour
    _S["4"]["date"]="2026-08-22"
    _S["4"]["sous"]="La s\u00e9ance la plus importante des trois prochaines semaines."
    _S["4"]["chaussure"]="ASICS Novablast 5 V"
    _S["4"]["metriques"]={"Distance":"28 km","Dur\u00e9e":"~170 min","Allure":"6:00-6:20 puis 5:20/km","FC":"135-150 puis 148-160","RPE":"6","Type":"Longue + sp\u00e9cifique"}
    _S["4"]["objectif"]="<strong>28 km dont 12 \u00e0 allure marathon.</strong> C\u2019est exactement ce que tu as r\u00e9ussi le 13 ao\u00fbt \u00e0 La Rochelle, mais deux fois plus longtemps. <strong>La consigne tient en une phrase : montre au kilom\u00e8tre 1, et montre au kilom\u00e8tre 2.</strong> Mardi, les deux premiers sont partis 25 secondes trop vite avant tout contr\u00f4le."
    _S["4"]["struct"]=[
      {"nom":"\u00c9chauffement","txt":"8 km \u00e0 6:00-6:20/km, FC sous 150. Tr\u00e8s progressif."},
      {"nom":"Bloc allure marathon","txt":"<strong>12 km \u00e0 5:20/km</strong>, FC 148-160. Chaque kilom\u00e8tre entre 5:18 et 5:24. <strong>Si la chaleur est forte, d\u00e9coupe en 2\u00d76 km</strong> avec 1 km facile au milieu \u2014 mieux vaut deux blocs propres qu\u2019un bloc qui d\u00e9rive."},
      {"nom":"Retour au calme","txt":"8 km \u00e0 allure facile, FC redescendue sous 150."},
      {"nom":"Nutrition","txt":"C\u2019est ton laboratoire avant Nice : boire toutes les 15-20 min, \u00e9lectrolytes d\u00e8s le d\u00e9part, 1 gel toutes les 30-40 min au-del\u00e0 d\u2019une heure. Note ce que tu absorbes et ton ressenti."},
      {"nom":"Conditions","txt":"<strong>Partir t\u00f4t</strong> \u2014 canicule en cours. Si la temp\u00e9rature d\u00e9passe nettement les conditions de course, l\u2019allure cible prime sur la distance : mieux vaut 24 km propres que 28 km d\u00e9grad\u00e9s."}]
    _S["4"]["segments"]=[
      {"nom":"\u00c9chauffement","role":"8 km \u00e0 6:00-6:20/km, FC sous 150.","duree":2940,"couleur":"vert","bloc":"\u2014","hauteur":32,"debut":0,"fin":2940},
      {"nom":"Bloc allure marathon","role":"12 km \u00e0 5:20/km, FC 148-160.","duree":3840,"couleur":"orange","bloc":"\u1f3af","hauteur":74,"debut":2940,"fin":6780},
      {"nom":"Retour au calme","role":"8 km facile, FC sous 150.","duree":2940,"couleur":"vert","bloc":"\u2014","hauteur":30,"debut":6780,"fin":9720}]

    # Graphique RESYNCHRONISE avec le REEL couru (les lignes ci-dessus
    # restent la prescription, struct/objectif ne changent pas). Ceci doit
    # rester la DERNIERE affectation de _S["4"]["segments"] dans ce bloc.
    _S["4"]["segments"]=[
      {"nom":"km 1-5 (4:59/km)","role":"Prescrit 5:40-6:00 \u2014 couru bien au-dessus.","duree":1493,"couleur":"rouge","bloc":"\u2014","hauteur":50,"debut":0,"fin":1493},
      {"nom":"km 6-10 (4:58/km)","role":"Prescrit 5:40-6:00 \u2014 arr\u00eat Fontaines-sur-Sa\u00f4ne inclus.","duree":1489,"couleur":"rouge","bloc":"\u2014","hauteur":51,"debut":1493,"fin":2982},
      {"nom":"km 11-15 (4:52/km)","role":"Prescrit 5:20 (bloc AM) \u2014 arr\u00eat Neuville inclus.","duree":1462,"couleur":"orange","bloc":"AM","hauteur":58,"debut":2982,"fin":4444},
      {"nom":"km 16-20 (4:49/km)","role":"Prescrit 5:20 (bloc AM) \u2014 tranche la plus rapide de la sortie.","duree":1443,"couleur":"rouge","bloc":"AM","hauteur":62,"debut":4444,"fin":5887},
      {"nom":"km 21-25 (5:01/km)","role":"Prescrit 5:40-6:00 \u2014 l\u00e9ger rel\u00e2chement en fin de parcours.","duree":1503,"couleur":"orange","bloc":"\u2014","hauteur":48,"debut":5887,"fin":7390}]
    break
    arr[4]["titre"]="Déverrouillage retour de route"
    arr[4]["type"]="EF aérobie"
    arr[4]["opt"]=True
    arr[4]["sous"]="Optionnel — seulement si l'envie est là."
    arr[4]["metriques"]={"Distance":"6-8 km","Durée":"~45 min","Allure":"6:10-6:30/km","FC":"< 140","RPE":"2-3","Type":"Déverrouillage"}
    arr[4]["objectif"]="Après 6h30 de voiture, l'objectif est de <strong>débloquer les jambes, pas de s'entraîner</strong>. Très facile, FC sous 140. <strong>Si la fatigue du trajet domine, une marche de 20 minutes fait le même travail</strong> — ne force pas cette séance, elle ne vaut pas une semaine suivante entamée."
    arr[4]["struct"]=[
      {"nom":"Corps","txt":"6 à 8 km à allure très facile, FC plafonnée à 140. Aucune ligne droite, aucune accélération."},
      {"nom":"Alternative","txt":"20 à 30 min de marche + mobilité hanches et chaîne postérieure si les jambes sont trop lourdes."}]




# ── S35 : restructuree sur 3 jours (contraintes familiales) ──────────
# Loic ne peut pas courir avant jeudi. Lundi saute (fatigue post-25 km),
# mardi et mercredi indisponibles. Restent jeudi 27, vendredi 28,
# samedi 29. Le volume passe de 66 km cibles a ~36 km reels.
# ARBITRAGE : sur 3 jours consecutifs apres une semaine a 605 de charge,
# on ne cumule pas deux seances dures. Une seule qualite (le seuil), une
# longue allegee, et un footing de liaison entre les deux.
for n, arr in list(SEANCES_BY_WEEK.items()):
    if n != "35":
        continue
    _S = {str(x["id"]): x for x in arr}

    # LUNDI 24/08 - saute
    _S["1"]["realise"]={"statut":"skipped","km":0,"temps":"\u2014","allure":"\u2014","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Non r\u00e9alis\u00e9e \u2014 fatigue persistante apr\u00e8s les 25 km de samedi (charge 394) et la sortie v\u00e9lo de dimanche.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}

    # MARDI 25/08 - indisponible, devient repos
    _S["2"]["date"]="2026-08-25"
    _S["2"]["titre"]="Repos \u2014 indisponible"
    _S["2"]["type"]="Repos"
    _S["2"]["sous"]="Contraintes familiales."
    _S["2"]["metriques"]={"Dur\u00e9e":"\u2014","RPE":"0","Focus":"R\u00e9cup\u00e9ration","Type":"Repos"}
    _S["2"]["objectif"]="Jour sans course. La r\u00e9cup\u00e9ration se poursuit apr\u00e8s une semaine \u00e0 605 de charge."
    _S["2"]["struct"]=[{"nom":"Consigne","txt":"Aucune course. Sommeil et mobilit\u00e9 douce si possible."}]
    _S["2"]["segments"]=[]
    _S["2"]["realise"]={"statut":"skipped","km":0,"temps":"\u2014","allure":"\u2014","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Indisponible \u2014 contraintes familiales.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}

    # MERCREDI 26/08 - indisponible
    _S["3"]["date"]="2026-08-26"
    _S["3"]["titre"]="Repos \u2014 indisponible"
    _S["3"]["type"]="Repos"
    _S["3"]["sous"]="Contraintes familiales."
    _S["3"]["metriques"]={"Dur\u00e9e":"\u2014","RPE":"0","Focus":"R\u00e9cup\u00e9ration","Type":"Repos"}
    _S["3"]["objectif"]="Jour sans course."
    _S["3"]["struct"]=[{"nom":"Consigne","txt":"Aucune course."}]
    _S["3"]["segments"]=[]
    _S["3"]["realise"]={"statut":"skipped","km":0,"temps":"\u2014","allure":"\u2014","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Indisponible \u2014 contraintes familiales. Randonn\u00e9e de 7 km et 449 m de D+ effectu\u00e9e a la place (hors perimetre course).",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}

    # JEUDI 27/08 - reprise en douceur (etait le renfo)
    _S["5"]["date"]="2026-08-27"
    _S["5"]["titre"]="Footing de reprise"
    _S["5"]["type"]="EF a\u00e9robie"
    _S["5"]["sous"]="Premi\u00e8re sortie depuis samedi \u2014 rien \u00e0 prouver."
    _S["5"]["opt"]=False
    _S["5"]["chaussure"]="ASICS Novablast 5 V"
    _S["5"]["metriques"]={"Distance":"10 km","Dur\u00e9e":"~62 min","Allure":"6:00-6:20/km","FC":"< 145","RPE":"3","Type":"EF"}
    _S["5"]["objectif"]="Reprise apr\u00e8s 5 jours sans courir. <strong>FC plafonn\u00e9e \u00e0 145, aucune ligne droite, aucune acc\u00e9l\u00e9ration.</strong> Le seuil est demain : cette sortie sert \u00e0 r\u00e9veiller la foul\u00e9e, pas \u00e0 tester la forme."
    _S["5"]["struct"]=[
      {"nom":"Corps","txt":"10 km \u00e0 allure facile, FC sous 145. Apr\u00e8s 5 jours d'arr\u00eat, les jambes seront fra\u00eeches et l'envie d'acc\u00e9l\u00e9rer forte \u2014 c'est exactement le moment de tenir le plafond."}]
    _S["5"]["segments"]=[
      {"nom":"Footing de reprise","role":"10 km, FC sous 145, sans acc\u00e9l\u00e9ration.","duree":3720,"couleur":"vert","bloc":"\u2014","hauteur":32,"debut":0,"fin":3720}]

    # VENDREDI 28/08 - le seuil, seule seance de qualite
    _S["4"]["date"]="2026-08-28"
    _S["4"]["titre"]="Seuil 30 \u2014 2\u00d78 min"
    _S["4"]["type"]="Seuil (puissance a\u00e9robie)"
    _S["4"]["sous"]="La seule s\u00e9ance de qualit\u00e9 de la semaine."
    _S["4"]["chaussure"]="ASICS Magic Speed 4"
    _S["4"]["metriques"]={"Distance":"~11 km","Dur\u00e9e":"~66 min","Allure":"4:40/km sur les blocs","FC":"167-177","RPE":"6-7","Type":"Seuil"}
    _S["4"]["objectif"]="2\u00d78 min \u00e0 <strong>4:40/km</strong>, r\u00e9cup\u00e9ration 3 min en trot. <strong>Le chiffre prime sur la sensation</strong> \u2014 c'est la consigne prioritaire depuis samedi. Alerte d'allure recommand\u00e9e sur la Fenix : seuil bas \u00e0 4:35/km."
    _S["4"]["struct"]=[
      {"nom":"\u00c9chauffement","txt":"20 min en endurance fondamentale, FC sous 145."},
      {"nom":"Bloc 1","txt":"<strong>8 min \u00e0 4:40/km</strong>, FC 167-177. Chaque kilom\u00e8tre entre 4:37 et 4:43."},
      {"nom":"R\u00e9cup\u00e9ration","txt":"3 min en trot tr\u00e8s lent, FC redescendue sous 150."},
      {"nom":"Bloc 2","txt":"<strong>8 min \u00e0 4:40/km</strong>, m\u00eame cible. Le pi\u00e8ge : ce bloc semblera plus facile apr\u00e8s la r\u00e9cup \u2014 ne pas acc\u00e9l\u00e9rer."},
      {"nom":"Retour au calme","txt":"12 min tr\u00e8s souple."}]
    _S["4"]["segments"]=[
      {"nom":"\u00c9chauffement","role":"20 min EF, FC sous 145.","duree":1200,"couleur":"vert","bloc":"\u2014","hauteur":30,"debut":0,"fin":1200},
      {"nom":"Bloc 1 \u2014 8 min","role":"8 min \u00e0 4:40/km, FC 167-177.","duree":480,"couleur":"orange","bloc":"1/2","hauteur":72,"debut":1200,"fin":1680},
      {"nom":"R\u00e9cup\u00e9ration","role":"3 min trot, FC sous 150.","duree":180,"couleur":"vert","bloc":"\u2014","hauteur":26,"debut":1680,"fin":1860},
      {"nom":"Bloc 2 \u2014 8 min","role":"8 min \u00e0 4:40/km, m\u00eame cible.","duree":480,"couleur":"orange","bloc":"2/2","hauteur":72,"debut":1860,"fin":2340},
      {"nom":"Retour au calme","role":"12 min tr\u00e8s souple.","duree":720,"couleur":"vert","bloc":"\u2014","hauteur":28,"debut":2340,"fin":3060}]

    # SAMEDI 29/08 - longue allegee (etait dimanche 30)
    arr.append(dict(_S["5"]))
    _new = arr[-1]
    _new["id"] = 6
    _new["date"]="2026-08-29"
    _new["titre"]="Sortie longue \u2014 all\u00e9g\u00e9e"
    _new["type"]="Sortie longue"
    _new["sous"]="Volume r\u00e9duit : 3e jour cons\u00e9cutif."
    _new["chaussure"]="ASICS Novablast 5 V"
    _new["metriques"]={"Distance":"15 km","Dur\u00e9e":"~92 min","Allure":"6:00-6:20/km","FC":"135-150","RPE":"4-5","Type":"Longue"}
    _new["objectif"]="Longue ramen\u00e9e de 18 \u00e0 15 km : c'est le <strong>troisi\u00e8me jour cons\u00e9cutif</strong>, apr\u00e8s un seuil la veille. Allure libre mais facile, FC sous 150. <strong>Aucun bloc \u00e0 allure marathon cette semaine</strong> \u2014 le prochain est pr\u00e9vu en S40, sur des jambes fra\u00eeches."
    _new["struct"]=[
      {"nom":"Corps","txt":"15 km \u00e0 allure facile r\u00e9guli\u00e8re, FC 135-150. Si les jambes sont lourdes apr\u00e8s le seuil de la veille, raccourcir \u00e0 12 km sans h\u00e9siter."},
      {"nom":"Nutrition","txt":"Boire toutes les 15-20 min, 1 gel au-del\u00e0 d'une heure."}]
    _new["segments"]=[
      {"nom":"Sortie longue","role":"15 km facile, FC 135-150.","duree":5520,"couleur":"vert","bloc":"\u2014","hauteur":36,"debut":0,"fin":5520}]
    # SAMEDI 29/08 - longue non realisee
    _new["realise"]={"statut":"skipped","km":0,"temps":"\u2014","allure":"\u2014","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Non r\u00e9alis\u00e9e. Aucune activit\u00e9 enregistr\u00e9e le 29 ni le 30/08.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}

    # JEUDI 27/08 - footing de reprise, cible non tenue
    _S["5"]["chaussure"]="ASICS Novablast 5 V"
    _S["5"]["realise"]={"statut":"fait","km":12.04,"temps":"1h06:54","allure":"5:33/km","fc_moy":156,"fc_max":171,"re":151,
      "cadence":173,"elevation_gain":50,"kcal":953,"rpe_ressenti":5,
      "commentaire":"Sortie du soir, chaleur. Cible : 10 km \u00e0 6:00-6:20/km, FC plafond 145. R\u00e9alis\u00e9 : 12 km \u00e0 5:33/km, FC moyenne 156. Aucune douleur, pas de jambes lourdes malgr\u00e9 1150 m de D+ en randonn\u00e9e les deux jours pr\u00e9c\u00e9dents. Quelques courbatures l\u00e9g\u00e8res.",
      "pr":1,"ach":1,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:29","fc":123},{"km":2,"allure":"5:30","fc":155},{"km":3,"allure":"5:31","fc":159},
                {"km":4,"allure":"5:32","fc":163},{"km":5,"allure":"5:23","fc":160},{"km":6,"allure":"5:23","fc":153},
                {"km":7,"allure":"5:43","fc":157},{"km":8,"allure":"5:48","fc":156},{"km":9,"allure":"5:44","fc":157},
                {"km":10,"allure":"5:37","fc":160},{"km":11,"allure":"5:17","fc":166},{"km":12,"allure":"5:39","fc":163}],
      "revue":_REVUE_FICHIER}
    _S["5"]["segments"]=[
      {"nom":"Footing (cible non tenue)","role":"12 km \u00e0 5:33/km au lieu de 6:00-6:20, FC 156 au lieu de <145.","duree":4014,"couleur":"orange","bloc":"\u2014","hauteur":48,"debut":0,"fin":4014}]

    # VENDREDI 28/08 - seuil ajuste apres le cout de jeudi
    _S["4"]["metriques"]={"Distance":"~11 km","Dur\u00e9e":"~66 min","Allure":"4:45/km sur les blocs","FC":"167-177","RPE":"6-7","Type":"Seuil"}
    _S["4"]["objectif"]="2\u00d78 min \u00e0 <strong>4:45/km</strong> (assoupli de 4:40 apr\u00e8s le co\u00fbt de jeudi : effort relatif 151 sur un footing pr\u00e9vu \u00e0 60), r\u00e9cup\u00e9ration <strong>3 min 30</strong>. <strong>ALERTE D'ALLURE OBLIGATOIRE sur la Fenix, seuil bas \u00e0 4:40/km.</strong> Sur les trois derni\u00e8res s\u00e9ances \u00e0 cible chiffr\u00e9e, la volont\u00e9 seule a \u00e9chou\u00e9 trois fois \u2014 il faut un signal ext\u00e9rieur."
    _S["4"]["struct"]=[
      {"nom":"\u00c9chauffement","txt":"20 min en endurance fondamentale, FC sous 145. Sans exception cette fois."},
      {"nom":"Bloc 1","txt":"<strong>8 min \u00e0 4:45/km</strong>, FC 167-177. Chaque kilom\u00e8tre entre 4:42 et 4:48."},
      {"nom":"R\u00e9cup\u00e9ration","txt":"<strong>3 min 30</strong> en trot tr\u00e8s lent, FC redescendue sous 150."},
      {"nom":"Bloc 2","txt":"<strong>8 min \u00e0 4:45/km</strong>, m\u00eame cible. Ne pas acc\u00e9l\u00e9rer sous pr\u00e9texte que \u00e7a passe."},
      {"nom":"Retour au calme","txt":"12 min tr\u00e8s souple."},
      {"nom":"R\u00e9glage montre","txt":"Fenix 6 Pro : Profils d'activit\u00e9 \u2192 Course \u00e0 pied \u2192 Alertes \u2192 Allure \u2192 seuil bas 4:40/km. Elle vibrera si tu passes en dessous."}]
    _S["4"]["segments"]=[
      {"nom":"\u00c9chauffement","role":"20 min EF, FC sous 145.","duree":1200,"couleur":"vert","bloc":"\u2014","hauteur":30,"debut":0,"fin":1200},
      {"nom":"Bloc 1 \u2014 8 min","role":"8 min \u00e0 4:45/km, FC 167-177.","duree":480,"couleur":"orange","bloc":"1/2","hauteur":72,"debut":1200,"fin":1680},
      {"nom":"R\u00e9cup\u00e9ration","role":"3 min 30 trot, FC sous 150.","duree":210,"couleur":"vert","bloc":"\u2014","hauteur":26,"debut":1680,"fin":1890},
      {"nom":"Bloc 2 \u2014 8 min","role":"8 min \u00e0 4:45/km, m\u00eame cible.","duree":480,"couleur":"orange","bloc":"2/2","hauteur":72,"debut":1890,"fin":2370},
      {"nom":"Retour au calme","role":"12 min tr\u00e8s souple.","duree":720,"couleur":"vert","bloc":"\u2014","hauteur":28,"debut":2370,"fin":3090}]

    _S["4"]["chaussure"]="ASICS Magic Speed 4"
    _S["4"]["realise"]={"statut":"fait","km":10.03,"temps":"53:37","allure":"5:21/km","fc_moy":157,"fc_max":185,"re":125,
      "cadence":175,"elevation_gain":39,"kcal":759,"rpe_ressenti":7,
      "commentaire":"2x8 min seuil. Cible 4:45/km : bloc 1 a 4:39, bloc 2 a 4:42. Echauffement 3,63 km a 5:48/km respecte. Chaleur forte, nuit courte, 3e jour consecutif. Sensation difficile mais execution propre. 12 records personnels sur segments.",
      "pr":12,"ach":12,"pr_detail":[],
      "splits":[{"km":"\u00c9chauffement","allure":"5:48","fc":143},
                {"km":"Bloc 1 (8 min)","allure":"4:39","fc":168},
                {"km":"R\u00e9cup 3 min","allure":"5:54","fc":163},
                {"km":"Bloc 2 (8 min)","allure":"4:42","fc":171},
                {"km":"Retour au calme","allure":"5:21","fc":159}],
      "revue":_REVUE_FICHIER}
    _S["4"]["segments"]=[
      {"nom":"\u00c9chauffement","role":"3,63 km \u00e0 5:48/km, FC 143.","duree":1263,"couleur":"vert","bloc":"\u2014","hauteur":30,"debut":0,"fin":1263},
      {"nom":"Bloc 1 \u2014 8 min","role":"4:39/km pour une cible \u00e0 4:45, FC 168.","duree":480,"couleur":"orange","bloc":"1/2","hauteur":74,"debut":1263,"fin":1743},
      {"nom":"R\u00e9cup\u00e9ration","role":"3 min \u00e0 5:54/km.","duree":180,"couleur":"vert","bloc":"\u2014","hauteur":26,"debut":1743,"fin":1923},
      {"nom":"Bloc 2 \u2014 8 min","role":"4:42/km, FC 171 \u2014 pas d'acc\u00e9l\u00e9ration sur le second bloc.","duree":480,"couleur":"orange","bloc":"2/2","hauteur":74,"debut":1923,"fin":2403},
      {"nom":"R\u00e9cup\u00e9ration","role":"3 min.","duree":180,"couleur":"vert","bloc":"\u2014","hauteur":26,"debut":2403,"fin":2583},
      {"nom":"Retour au calme","role":"1,98 km \u00e0 5:21/km.","duree":634,"couleur":"vert","bloc":"\u2014","hauteur":28,"debut":2583,"fin":3217}]
    break






# ── S36 : semaine de depart aux USA (vendredi 04/09) ─────────────────
# Loic court lundi a jeudi, puis prend l'avion vendredi (9 h de decalage
# vers San Francisco). Contexte : deux semaines tres allegees derriere
# (39,7 puis 22,1 km, la plus petite de la preparation), mais un seuil
# propre vendredi dernier (4:39 et 4:42 pour une cible a 4:45).
# ACWR reel au 31/08 : 0,67 -- la longue du 22/08 est sortie de la
# fenetre 7 jours. La marge existe, on peut relancer.
# ARBITRAGE : le seuil passe au MERCREDI et non au jeudi, pour laisser
# deux jours entre la seance dure et le vol. Jeudi devient un simple
# deverrouillage avant 11 h d'avion.
for n, arr in list(SEANCES_BY_WEEK.items()):
    if n != "36":
        continue
    _S = {str(x["id"]): x for x in arr}

    # LUNDI 31/08 - relance
    _S["1"]["titre"]="Footing de relance"
    _S["1"]["sous"]="Premi\u00e8re s\u00e9ance de la semaine \u2014 sans forcer."
    _S["1"]["chaussure"]="ASICS Novablast 5 V"
    _S["1"]["metriques"]={"Distance":"10 km","Dur\u00e9e":"~62 min","Allure":"6:00-6:20/km","FC":"< 145","RPE":"3","Type":"EF"}
    _S["1"]["objectif"]="Relance apr\u00e8s deux semaines tr\u00e8s all\u00e9g\u00e9es et un seuil vendredi. <strong>FC plafonn\u00e9e \u00e0 145</strong>, aucune acc\u00e9l\u00e9ration. L'ACWR est \u00e0 0,67 : la marge existe, mais elle ne s'utilise pas d\u00e8s le premier jour."
    _S["1"]["struct"]=[
      {"nom":"Corps","txt":"10 km \u00e0 allure facile, FC sous 145. Apr\u00e8s 2 jours sans courir, les jambes seront fra\u00eeches \u2014 c'est exactement le moment de tenir le plafond."}]
    _S["1"]["segments"]=[
      {"nom":"Footing de relance","role":"10 km, FC sous 145.","duree":3720,"couleur":"vert","bloc":"\u2014","hauteur":32,"debut":0,"fin":3720}]
    _S["1"]["chaussure"]="HOKA Clifton 10"
    _S["1"]["realise"]={"statut":"fait","km":10.26,"temps":"1h00:27","allure":"5:54/km","fc_moy":142,"fc_max":160,"re":74,
      "cadence":173,"elevation_gain":40,"kcal":776,"rpe_ressenti":3,
      "commentaire":"Footing de relance, cible FC plafond 145. R\u00e9alis\u00e9 : FC moyenne 142,4, deux km seulement au-dessus de 145. Grosse sensation de fra\u00eecheur, h\u00e9sitation \u00e0 partir sur 16 km, finalement tenu \u00e0 10 km pour pr\u00e9server les 4 s\u00e9ances de la semaine. Aucune douleur.",
      "pr":0,"ach":0,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:54","fc":140},{"km":2,"allure":"5:39","fc":141},{"km":3,"allure":"5:58","fc":146},
                {"km":4,"allure":"5:53","fc":143},{"km":5,"allure":"5:58","fc":140},{"km":6,"allure":"5:50","fc":144},
                {"km":7,"allure":"5:59","fc":140},{"km":8,"allure":"5:56","fc":142},{"km":9,"allure":"5:51","fc":146},
                {"km":10,"allure":"6:02","fc":142}],
      "revue":_REVUE_FICHIER}
    _S["1"]["segments"]=[
      {"nom":"Footing de relance","role":"10,26 km \u00e0 5:54/km, FC 142 pour un plafond \u00e0 145.","duree":3627,"couleur":"vert","bloc":"\u2014","hauteur":32,"debut":0,"fin":3627}]

    # MARDI 01/09 - EF + lignes droites
    _S["2"]["titre"]="Footing + 6 lignes droites"
    _S["2"]["sous"]="Entretien de la foul\u00e9e avant le seuil."
    _S["2"]["chaussure"]="ASICS Novablast 5 V"
    _S["2"]["metriques"]={"Distance":"10 km","Dur\u00e9e":"~64 min","Allure":"6:00-6:20/km","FC":"< 148","RPE":"3-4","Type":"EF + technique"}
    _S["2"]["objectif"]="Footing facile suivi de <strong>6 lignes droites de 20 secondes</strong>, r\u00e9cup\u00e9ration compl\u00e8te en marche. Objectif : r\u00e9veiller la fr\u00e9quence de foul\u00e9e avant le seuil de demain, sans co\u00fbt."
    _S["2"]["struct"]=[
      {"nom":"Corps","txt":"9 km \u00e0 allure facile, FC sous 148."},
      {"nom":"Lignes droites","txt":"6\u00d720 secondes en acc\u00e9l\u00e9ration progressive, r\u00e9cup\u00e9ration 60 s en marche. <strong>Rel\u00e2ch\u00e9, pas de sprint</strong> \u2014 la vitesse maximale n'apporte rien ici."},
      {"nom":"Retour au calme","txt":"5 min tr\u00e8s souple."}]
    _S["2"]["segments"]=[
      {"nom":"Footing facile","role":"9 km, FC sous 148.","duree":3300,"couleur":"vert","bloc":"\u2014","hauteur":32,"debut":0,"fin":3300},
      {"nom":"6\u00d720 s","role":"Lignes droites rel\u00e2ch\u00e9es, r\u00e9cup 60 s marche.","duree":480,"couleur":"orange","bloc":"6\u00d7","hauteur":58,"debut":3300,"fin":3780},
      {"nom":"Retour au calme","role":"5 min souple.","duree":300,"couleur":"vert","bloc":"\u2014","hauteur":26,"debut":3780,"fin":4080}]
    _S["2"]["chaussure"]="ASICS Novablast 5 J"
    _S["2"]["realise"]={"statut":"fait","km":11.03,"temps":"1h01:29","allure":"5:34/km","fc_moy":144,"fc_max":181,"re":80,
      "cadence":174,"elevation_gain":34,"kcal":818,"rpe_ressenti":4,
      "commentaire":"Footing 9 km + 6x20s lignes droites. FC plafond 148 tenu (moy 140,3). Sensation de fraicheur nette, meilleure qu'hier. Accélération identifiée par Loic lui-meme sur les 2 dernieres lignes droites (110 m et 120 m parcourus en 22 s contre 96-102 sur les 4 premieres).",
      "pr":1,"ach":2,"pr_detail":[],
      "splits":[{"km":"Footing (moy)","allure":"5:46","fc":140},
                {"km":"LD1","allure":"3:49","fc":150},{"km":"LD2","allure":"3:44","fc":163},
                {"km":"LD3","allure":"3:36","fc":165},{"km":"LD4","allure":"3:44","fc":167},
                {"km":"LD5","allure":"3:20","fc":166},{"km":"LD6","allure":"3:04","fc":169}],
      "revue":_REVUE_FICHIER}
    _S["2"]["segments"]=[
      {"nom":"Footing facile (140 bpm moy.)","role":"9 km, FC sous 148, dérive concentrée sur le 1er et le dernier km.","duree":3300,"couleur":"vert","bloc":"\u2014","hauteur":32,"debut":0,"fin":3300},
      {"nom":"6\u00d720 s (LD5-6 accélérées)","role":"4 premières stables (96-102 m), LD5 et LD6 accélérées (110 et 120 m).","duree":480,"couleur":"orange","bloc":"6\u00d7","hauteur":58,"debut":3300,"fin":3780},
      {"nom":"Retour au calme","role":"5 min souple.","duree":300,"couleur":"vert","bloc":"\u2014","hauteur":26,"debut":3780,"fin":4080}]

    # MERCREDI 02/09 - LE SEUIL, seance cle
    _S["3"]["titre"]="Seuil 2\u00d710 min"
    _S["3"]["type"]="Seuil (puissance a\u00e9robie)"
    _S["3"]["sous"]="La s\u00e9ance cl\u00e9 de la semaine."
    _S["3"]["chaussure"]="ASICS Magic Speed 4"
    _S["3"]["metriques"]={"Distance":"~12 km","Dur\u00e9e":"~70 min","Allure":"4:45/km sur les blocs","FC":"167-177","RPE":"6-7","Type":"Seuil"}
    _S["3"]["objectif"]="2\u00d710 min \u00e0 <strong>4:45/km</strong>, r\u00e9cup\u00e9ration 3 min 30. Allong\u00e9 de 8 \u00e0 10 min car le seuil du 28/08 a \u00e9t\u00e9 tenu proprement (4:39 et 4:42 pour une cible \u00e0 4:45). <strong>M\u00eame cible d'allure, et ALERTE SUR LA FENIX \u00e0 4:40/km.</strong> Plac\u00e9 mercredi pour laisser deux jours avant le vol de vendredi."
    _S["3"]["struct"]=[
      {"nom":"\u00c9chauffement","txt":"20 min en endurance fondamentale, FC sous 145."},
      {"nom":"Bloc 1","txt":"<strong>10 min \u00e0 4:45/km</strong>, FC 167-177. Chaque kilom\u00e8tre entre 4:42 et 4:48."},
      {"nom":"R\u00e9cup\u00e9ration","txt":"3 min 30 en trot tr\u00e8s lent, FC redescendue sous 150."},
      {"nom":"Bloc 2","txt":"<strong>10 min \u00e0 4:45/km</strong>, m\u00eame cible. Le bloc 2 du 28/08 \u00e9tait plus lent que le bloc 1 \u2014 refais exactement pareil."},
      {"nom":"Retour au calme","txt":"12 min tr\u00e8s souple."},
      {"nom":"R\u00e9glage montre","txt":"Fenix 6 Pro : Profils d'activit\u00e9 \u2192 Course \u00e0 pied \u2192 Alertes \u2192 Allure \u2192 seuil bas 4:40/km."}]
    _S["3"]["segments"]=[
      {"nom":"\u00c9chauffement","role":"20 min EF, FC sous 145.","duree":1200,"couleur":"vert","bloc":"\u2014","hauteur":30,"debut":0,"fin":1200},
      {"nom":"Bloc 1 \u2014 10 min","role":"10 min \u00e0 4:45/km, FC 167-177.","duree":600,"couleur":"orange","bloc":"1/2","hauteur":74,"debut":1200,"fin":1800},
      {"nom":"R\u00e9cup\u00e9ration","role":"3 min 30 trot, FC sous 150.","duree":210,"couleur":"vert","bloc":"\u2014","hauteur":26,"debut":1800,"fin":2010},
      {"nom":"Bloc 2 \u2014 10 min","role":"10 min \u00e0 4:45/km, m\u00eame cible.","duree":600,"couleur":"orange","bloc":"2/2","hauteur":74,"debut":2010,"fin":2610},
      {"nom":"Retour au calme","role":"12 min tr\u00e8s souple.","duree":720,"couleur":"vert","bloc":"\u2014","hauteur":28,"debut":2610,"fin":3330}]

    _S["3"]["chaussure"]="ASICS Magic Speed 4"
    _S["3"]["realise"]={"statut":"fait","km":8.59,"temps":"42:51","allure":"4:59/km","fc_moy":167,"fc_max":181,"re":137,
      "cadence":87,"elevation_gain":27,"kcal":658,"rpe_ressenti":6,
      "commentaire":"Seuil 2x10 min, cible 4:45/km. Bloc 1 a 4:31/km (1er km a 4:13, alerte Fenix armee a 4:40 ignoree consciemment pour doubler en groupe dense, musique -- 2e km revenu a 4:45 pile, correction interne de 32 s). Bloc 2 tenu a 4:38 puis 4:42, amplitude 5 s. Seance coupee a 8,59 km au lieu de ~12 km prevus, decision assumee pour preserver la 4e seance de la semaine avant le vol. Aucune douleur, chaleur seulement.",
      "pr":12,"ach":12,"pr_detail":[],
      "splits":[{"km":"Echauffement","allure":"5:14","fc":None},
                {"km":"Bloc 1 (alerte ignoree puis corrigee)","allure":"4:31","fc":None},
                {"km":"Recuperation","allure":"6:09","fc":None},
                {"km":"Bloc 2 (tenu)","allure":"4:40","fc":None}],
      "note_splits":"FC moyenne disponible uniquement au niveau de la seance entiere (167 bpm) -- pas de detail par bloc verifie aupres de Strava pour cette seance, contrairement aux precedentes.",
      "revue":_REVUE_FICHIER}
    _S["3"]["segments"]=[
      {"nom":"Echauffement","role":"15 min, 2,87 km, 5:14/km.","duree":900,"couleur":"vert","bloc":"\u2014","hauteur":30,"debut":0,"fin":900},
      {"nom":"Bloc 1 (alerte ignoree puis corrigee)","role":"10 min, 4:31/km moy -- 1er km a 4:13 (alerte ignoree), 2e km revenu a 4:45.","duree":600,"couleur":"orange","bloc":"1/2","hauteur":74,"debut":900,"fin":1500},
      {"nom":"Recuperation","role":"3 min 30, 6:09/km.","duree":210,"couleur":"vert","bloc":"\u2014","hauteur":26,"debut":1500,"fin":1710},
      {"nom":"Bloc 2 (tenu)","role":"10 min, 4:40/km moy, amplitude 5 s.","duree":600,"couleur":"orange","bloc":"2/2","hauteur":74,"debut":1710,"fin":2310},
      {"nom":"Retour au calme","role":"4 min 21, arret a 8,59 km.","duree":261,"couleur":"vert","bloc":"\u2014","hauteur":28,"debut":2310,"fin":2571}]

    # JEUDI 03/09 - deverrouillage avant le vol
    _S["4"]["titre"]="D\u00e9verrouillage avant le vol"
    _S["4"]["type"]="EF a\u00e9robie"
    _S["4"]["sous"]="Court et facile \u2014 11 h d'avion demain."
    _S["4"]["chaussure"]="ASICS Novablast 5 V"
    _S["4"]["metriques"]={"Distance":"8 km","Dur\u00e9e":"~50 min","Allure":"6:10-6:30/km","FC":"< 140","RPE":"2-3","Type":"D\u00e9verrouillage"}
    _S["4"]["objectif"]="<strong>Ce n'est pas une s\u00e9ance d'entra\u00eenement</strong>, c'est du d\u00e9verrouillage avant un long vol. 8 km tr\u00e8s faciles, FC sous 140, aucune acc\u00e9l\u00e9ration. Bouger la veille d'un vol long-courrier limite la raideur et aide au d\u00e9calage."
    _S["4"]["struct"]=[
      {"nom":"Corps","txt":"8 km \u00e0 allure tr\u00e8s facile, FC plafonn\u00e9e \u00e0 140. Si les jambes sont lourdes apr\u00e8s le seuil de la veille, r\u00e9duire \u00e0 6 km sans h\u00e9siter."},
      {"nom":"Apr\u00e8s la s\u00e9ance","txt":"\u00c9tirements doux et hydratation. Le vol de demain d\u00e9shydrate fortement."}]
    _S["4"]["segments"]=[
      {"nom":"D\u00e9verrouillage","role":"8 km tr\u00e8s facile, FC sous 140.","duree":3000,"couleur":"vert","bloc":"\u2014","hauteur":28,"debut":0,"fin":3000}]

    _S["4"]["chaussure_realise"]="ASICS Novablast 5 J"
    _S["4"]["realise"]={"statut":"fait","km":12.08,"temps":"1:08:34","allure":"5:41/km","fc_moy":143,"fc_max":160,"re":88,
      "cadence":88,"elevation_gain":25,"kcal":891,"rpe_ressenti":4,
      "commentaire":"Prevu : 8 km deverrouillage, 6:10-6:30/km, FC<140. Realise : 12,08 km a 5:41/km avec une amie (essai delibere de suivre plutot que de mener, pour ne pas accelerer). FC 143 moy/160 max, au-dessus du plafond vise mais sans derive brutale -- le km le plus lent (6:06/km) est au milieu du parcours, la seule acceleration nette est en toute fin de course (finish choisi, pas involontaire). Jambes lourdes au debut malgre FC basse (133-139), signature de fatigue musculaire locale (4e seance consecutive), pas cardio. Aucune douleur. Chaussure reelle Novablast 5 J (plan prevoyait Novablast 5 V).",
      "pr":7,"ach":7,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:23","fc":133},{"km":2,"allure":"5:18","fc":139},{"km":3,"allure":"5:40","fc":137},
                {"km":4,"allure":"5:34","fc":143},{"km":5,"allure":"5:54","fc":141},{"km":6,"allure":"5:48","fc":146},
                {"km":7,"allure":"5:46","fc":148},{"km":8,"allure":"5:53","fc":142},{"km":9,"allure":"6:06","fc":138},
                {"km":10,"allure":"5:37","fc":147},{"km":11,"allure":"5:34","fc":150},{"km":12,"allure":"5:31","fc":150}],
      "revue":_REVUE_FICHIER}

    # DIMANCHE 06/09 - optionnel, San Francisco
    import copy as _copy
    _sf = _copy.deepcopy(_S["4"])
    _sf.pop("realise", None)
    _sf.pop("chaussure_realise", None)
    _sf["id"] = 5
    _sf["date"] = "2026-09-06"
    _sf["titre"] = "San Francisco \u2014 optionnel"
    _sf["sous"] = "Seulement si le corps suit \u2014 J+2 apr\u00e8s 9 h de d\u00e9calage."
    _sf["opt"] = True
    _sf["metriques"]={"Distance":"5-7 km","Dur\u00e9e":"30-40 min","Allure":"libre","FC":"< 140","RPE":"2","Type":"Optionnel"}
    _sf["objectif"]="<strong>Ne rien planifier.</strong> Tu seras \u00e0 J+2 apr\u00e8s 9 heures de d\u00e9calage, dans le sens le plus difficile pour le sommeil. Si tu te r\u00e9veilles t\u00f4t et que tu te sens bien : 30 \u00e0 40 min tr\u00e8s faciles le matin, la lumi\u00e8re du jour et l'activit\u00e9 douce aident \u00e0 recaler l'horloge. <strong>Si tu es cass\u00e9, ne cours pas</strong> \u2014 une bonne acclimatation vaut plus que cette s\u00e9ance."
    _sf["struct"]=[
      {"nom":"Si tu te sens bien","txt":"30 \u00e0 40 min tr\u00e8s faciles, le matin de pr\u00e9f\u00e9rence, FC sous 140. Allure totalement libre."},
      {"nom":"Si tu es fatigu\u00e9","txt":"Marche au soleil pendant 30 min. C'est aussi efficace sur le d\u00e9calage et \u00e7a ne co\u00fbte rien."}]
    _sf["segments"]=[
      {"nom":"Golden Gate Park","role":"Terrain plat a legerement vallonne, prise de rythme.","duree":900,"couleur":"vert","bloc":"\u2014","hauteur":30,"debut":0,"fin":900},
      {"nom":"Montees (Sea Cliff / Hellman Hollow)","role":"Sections raides, FC jusqu'a 172-180.","duree":1600,"couleur":"orange","bloc":"\u2014","hauteur":60,"debut":900,"fin":2500},
      {"nom":"Lands End Trail (sentier, escaliers)","role":"Technique, cadence ralentie dans les marches.","duree":1600,"couleur":"orange","bloc":"\u2014","hauteur":50,"debut":2500,"fin":4100},
      {"nom":"Retour","role":"Terrain plus roulant, fin en aisance.","duree":454,"couleur":"vert","bloc":"\u2014","hauteur":30,"debut":4100,"fin":4554}]
    _sf["chaussure_realise"]="ASICS Novablast 5 V"
    _sf["realise"]={"statut":"fait","km":14.28,"temps":"1:15:54","allure":"5:19/km","fc_moy":154,"fc_max":180,"re":161,
      "cadence":85,"elevation_gain":220,"kcal":1072,"rpe_ressenti":5,
      "commentaire":"Prevu : 5-7 km tres facile, FC<140, seulement si le corps suit a J+2 de decalage. Realise : 14,28 km (75:54 de mouvement, 95:57 total avec ~20 min d'arrets photos) a 5:19/km moyen, dans Golden Gate Park et Lands End Trail, D+220m. Terrain tres vallonne (escaliers, sentiers techniques) qui explique la variation d'allure 4:44-6:03/km et la FC moyenne 154 (max 180 sur la cote la plus raide, 93% FCmax, bref). Aucune douleur, jambes legeres, ressenti plaisir pur -- jet lag digere plus vite que prevu.",
      "pr":0,"ach":1,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:13","fc":107},{"km":2,"allure":"4:45","fc":155},{"km":3,"allure":"4:57","fc":158},
                {"km":4,"allure":"6:03","fc":150},{"km":5,"allure":"5:33","fc":152},{"km":6,"allure":"5:56","fc":157},
                {"km":7,"allure":"6:01","fc":157},{"km":8,"allure":"5:35","fc":155},{"km":9,"allure":"5:54","fc":149},
                {"km":10,"allure":"5:05","fc":153},{"km":11,"allure":"4:57","fc":156},{"km":12,"allure":"4:44","fc":165},
                {"km":13,"allure":"5:02","fc":172},{"km":14,"allure":"4:44","fc":165}],
      "revue":_REVUE_FICHIER}
    arr.append(_sf)
    break

for n, arr in list(SEANCES_BY_WEEK.items()):
    if n != "39":
        continue
    _S39 = {str(x["id"]): x for x in arr}
    _S39["3"]["chaussure_realise"]="ASICS Novablast 5 V"
    _S39["3"]["segments"]=[
      {"nom":"Reprise (Venice Beach)","role":"Premiers kilometres, cadence qui monte.","duree":900,"couleur":"vert","bloc":"\u2014","hauteur":30,"debut":0,"fin":900},
      {"nom":"Boardwalk vers Santa Monica","role":"Arrets frequents (foule, jetee) -- une section quasi marchee.","duree":1700,"couleur":"orange","bloc":"\u2014","hauteur":55,"debut":900,"fin":2600},
      {"nom":"Retour vers Venice","role":"FC elevee et stable, 168-180.","duree":1673,"couleur":"orange","bloc":"\u2014","hauteur":65,"debut":2600,"fin":4273},
      {"nom":"Fin de sortie","role":"Derniers kilometres, FC pres du maximum sur les relances.","duree":281,"couleur":"rouge","bloc":"\u2014","hauteur":75,"debut":4273,"fin":4554}]
    _S39["3"]["realise"]={"statut":"fait","km":11.63,"temps":"56:13","allure":"4:50/km","fc_moy":168,"fc_max":190,"re":177,
      "cadence":86,"elevation_gain":26,"kcal":872,"rpe_ressenti":6,
      "commentaire":"Prevu : footing facile + lignes droites, 5:50-6:25/km, FC 135-150. Realise : premiere course depuis 17 jours (uniquement randonnee dans les parcs nationaux US pendant le road trip), sortie decouverte a la sensation a Venice Beach / Santa Monica, 11,63 km en 56:13 de course (89:17 au total, ~33 min d'arrets lies a la foule sur la jetee). Allure 4:50/km, tres eloignee de la cible et proche de l'allure seuil recente, mais FC moyenne 168 et pic a 190 (2 bpm sous FCmax 192) -- effort cardiovasculaire quasi maximal sans que le ressenti (plaisir, jambes correctes) ne l'ait signale. Lecture : 17 jours sans course specifique ont fait reculer l'economie de course, pas la forme generale (la randonnee entretient le cardio et les jambes autrement). Aucune douleur.",
      "pr":0,"ach":0,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:11","fc":145},{"km":2,"allure":"4:52","fc":161},{"km":3,"allure":"4:58","fc":148},
                {"km":4,"allure":"4:45","fc":167},{"km":5,"allure":"4:39","fc":179},{"km":6,"allure":"4:51","fc":177},
                {"km":7,"allure":"4:51","fc":168},{"km":8,"allure":"4:39","fc":172},{"km":9,"allure":"4:47","fc":179},
                {"km":10,"allure":"4:59","fc":176},{"km":11,"allure":"4:47","fc":172},{"km":12,"allure":"4:37","fc":172}],
      "revue":_REVUE_FICHIER}
    break

for n, arr in list(SEANCES_BY_WEEK.items()):
    if n not in ("37", "38", "39"):
        continue
    _SUS = {str(x["id"]): x for x in arr}
    _reason_hike = "Road trip USA : randonnee dans les parcs nationaux (Zion, Bryce, Grand Canyon) a la place de la course. Choix assume, pas un oubli."
    if n == "37":
        for sid in ("1", "2", "3", "4"):
            _SUS[sid]["realise"] = {"statut": "skipped", "reason": "Road trip USA (randonnee)", "km": 0,
                "temps": "\u2014", "allure": "\u2014", "fc_moy": 0, "fc_max": 0, "re": 0, "rpe_ressenti": 0,
                "commentaire": _reason_hike, "pr": 0, "ach": 0, "pr_detail": []}
    if n == "38":
        for sid in ("1", "2", "3", "4"):
            _SUS[sid]["realise"] = {"statut": "skipped", "reason": "Road trip USA (randonnee)", "km": 0,
                "temps": "\u2014", "allure": "\u2014", "fc_moy": 0, "fc_max": 0, "re": 0, "rpe_ressenti": 0,
                "commentaire": _reason_hike, "pr": 0, "ach": 0, "pr_detail": []}
    if n == "39":
        for sid in ("1", "2"):
            _SUS[sid]["realise"] = {"statut": "skipped", "reason": "Road trip USA (randonnee)", "km": 0,
                "temps": "\u2014", "allure": "\u2014", "fc_moy": 0, "fc_max": 0, "re": 0, "rpe_ressenti": 0,
                "commentaire": _reason_hike, "pr": 0, "ach": 0, "pr_detail": []}
        _SUS["4"]["chaussure_realise"]="ASICS Novablast 5 J"
        _SUS["4"]["realise"]={"statut":"fait","km":10.2,"temps":"55:07","allure":"5:24/km","fc_moy":156,"fc_max":177,"re":121,
          "cadence":86,"elevation_gain":38,"kcal":789,"rpe_ressenti":6,
          "commentaire":"Prevu : sortie longue de remise en route, 16 km, 5:50-6:25/km, FC 135-150. Realise : retour de vacances (rentre la veille), fatigue et jet lag assumes, seance tenue mais raccourcie a 10,2 km. Derive cardiaque continue et progressive du debut a la fin : FC 144 au km1, 165 au km10, 174 sur le dernier segment ; allure 5:45/km en ouverture, 5:03/km en cloture. Troisieme signal du meme diagnostic apres San Francisco et Venice Beach : l'organisme a besoin de plusieurs seances propres pour retrouver son efficacite de course apres 3 semaines quasi sans courir (2 sorties reelles sur la periode, le reste en randonnee). Aucune douleur. Bilan chiffre de la periode : environ 12 seances prevues sur S37-S39, 2 seulement courues.",
          "pr":0,"ach":1,"pr_detail":[],
          "splits":[{"km":1,"allure":"5:45","fc":144},{"km":2,"allure":"5:35","fc":151},{"km":3,"allure":"5:27","fc":154},
                    {"km":4,"allure":"5:29","fc":151},{"km":5,"allure":"5:23","fc":155},{"km":6,"allure":"5:32","fc":155},
                    {"km":7,"allure":"5:11","fc":159},{"km":8,"allure":"5:20","fc":162},{"km":9,"allure":"5:16","fc":164},
                    {"km":10,"allure":"5:03","fc":165}],
          "revue":_REVUE_FICHIER}

for n, arr in list(SEANCES_BY_WEEK.items()):
    if n != "40":
        continue
    _S40 = {str(x["id"]): x for x in arr}
    _S40["5"]["realise"]={"statut":"skipped","reason":"Journee difficile (dette de sommeil)","km":0,
      "temps":"\u2014","allure":"\u2014","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Non faite -- Loic etait trop mal jeudi (debut de la serie de nuits courtes) et a prefere une journee tranquille plutot que de forcer le renforcement.",
      "pr":0,"ach":0,"pr_detail":[]}
    _S40["4"]["chaussure_realise"]="ASICS Novablast 5 V"
    _S40["4"]["realise"]={"statut":"fait","km":21.3,"temps":"1:52:30","allure":"5:20/km","fc_moy":177,"fc_max":189,"re":470,
      "cadence":86,"elevation_gain":71,"kcal":1767,"rpe_ressenti":9,
      "commentaire":"Run In Lyon semi, couru malade apres 5 nuits a 3-4h de sommeil. Cible : groupe 1h50 (5:13/km) avec deux amis. Depart seul (partenaire arrete pour refaire ses lacets) : km 1-9 a 5:05/km moyen (4:52 au km3), km 1-10 a 5:06 puis km 11-20 a 5:33, soit un split positif de 27 s/km. FC 171 des le km2, 173-182 jusqu'au km17 (pic 189 au km7), 15 a 20 bpm au-dessus de la zone marathon 152-163. Explosion progressive a partir du km17 (5:31, puis 5:50, 5:52, 6:06), final remis en route. Temps declare par Loic : 1h52:30 (identique, a la seconde, au meilleur effort semi calcule par Strava -- chrono officiel de la puce a recouper sur la page resultats de l'organisateur). Distance GPS 21,30 km, 1:53:29 de mouvement. A allure comparable (km 3-10), FC 178 le 04/10 contre 162 le 22/08 pour un rythme meme legerement plus lent (5:03 contre 4:58) : environ +15 bpm, melange de maladie, de sommeil et de reprise apres coupure. Aucune douleur signalee, maladie a surveiller.",
      "pr":37,"ach":37,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:28","fc":163},{"km":2,"allure":"5:08","fc":171},{"km":3,"allure":"4:52","fc":173},
                {"km":4,"allure":"5:04","fc":175},{"km":5,"allure":"4:54","fc":177},{"km":6,"allure":"5:04","fc":177},
                {"km":7,"allure":"5:06","fc":181},{"km":8,"allure":"4:57","fc":178},{"km":9,"allure":"5:09","fc":180},
                {"km":10,"allure":"5:18","fc":179},{"km":11,"allure":"5:20","fc":179},{"km":12,"allure":"5:32","fc":177},
                {"km":13,"allure":"5:23","fc":177},{"km":14,"allure":"5:19","fc":177},{"km":15,"allure":"5:17","fc":178},
                {"km":16,"allure":"5:19","fc":180},{"km":17,"allure":"5:31","fc":182},{"km":18,"allure":"5:50","fc":176},
                {"km":19,"allure":"5:52","fc":177},{"km":20,"allure":"6:06","fc":174},{"km":21,"allure":"5:36","fc":176}],
      "revue":_REVUE_FICHIER}
    _S40["1"]["chaussure_realise"]="ASICS Novablast 5 V"
    _S40["1"]["realise"]={"statut":"fait","km":13.04,"temps":"1:19:23","allure":"6:05/km","fc_moy":143,"fc_max":182,"re":92,
      "cadence":86,"elevation_gain":22,"kcal":982,"rpe_ressenti":5,
      "commentaire":"Prevu : footing facile, 11 km, 5:50-6:25/km, FC 135-150. Realise avec Yannis, 13,04 km. Du km3 au km11 (~8km), allure 6:14-6:36/km et FC 134-141 -- exactement dans le cadre, stable, premier signal encourageant depuis le retour des USA (pas de derive continue contrairement a SF/Venice/retour). Coup de collier sur les 2 derniers km (5:46 puis 5:02/km, FC 170 puis pic a 182 = 95% FCmax), vraisemblablement partage avec Yannis -- pas une derive, un final assume. Aucune douleur.",
      "pr":6,"ach":6,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:28","fc":142},{"km":2,"allure":"5:27","fc":158},{"km":3,"allure":"6:14","fc":136},
                {"km":4,"allure":"6:27","fc":137},{"km":5,"allure":"6:28","fc":141},{"km":6,"allure":"6:21","fc":141},
                {"km":7,"allure":"6:25","fc":134},{"km":8,"allure":"6:36","fc":135},{"km":9,"allure":"6:16","fc":139},
                {"km":10,"allure":"6:20","fc":140},{"km":11,"allure":"6:22","fc":140},{"km":12,"allure":"5:46","fc":149},
                {"km":13,"allure":"5:02","fc":170}],
      "revue":_REVUE_FICHIER}
    _S40["2"]["chaussure_realise"]="ASICS Novablast 5 J"
    _S40["2"]["realise"]={"statut":"fait","km":12.03,"temps":"1:10:26","allure":"5:51/km","fc_moy":158,"fc_max":187,"re":171,
      "cadence":86,"elevation_gain":147,"kcal":988,"rpe_ressenti":7,
      "commentaire":"Prevu : seuil 2x10 min, ~4:50/km, FC 166-175. Realise : seuil non fait, remplace par une sortie continue et vallonnee avec Edwige (Quai des Etroits, montee de Choulans, Chemin Neuf, D+147m). FC moyenne 158, pics a 187 sur les passages a plus de 4%. 3e jour de course consecutif, effort reel (RE171) superieur aux deux jours precedents. Fatigue signalee par Loic apres la seance. Aucune douleur.",
      "pr":13,"ach":13,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:31","fc":139},{"km":2,"allure":"5:34","fc":154},{"km":3,"allure":"5:49","fc":145},
                {"km":4,"allure":"5:50","fc":147},{"km":5,"allure":"5:54","fc":149},{"km":6,"allure":"6:39","fc":160},
                {"km":7,"allure":"6:25","fc":166},{"km":8,"allure":"5:45","fc":164},{"km":9,"allure":"5:53","fc":168},
                {"km":10,"allure":"5:50","fc":173},{"km":11,"allure":"5:32","fc":163},{"km":12,"allure":"5:35","fc":169}],
      "revue":_REVUE_FICHIER}
    _S40["3"]["chaussure_realise"]="HOKA Clifton 10"
    _S40["3"]["realise"]={"statut":"fait","km":18.04,"temps":"1:57:15","allure":"6:30/km","fc_moy":137,"fc_max":157,"re":93,
      "cadence":86,"elevation_gain":47,"kcal":1347,"rpe_ressenti":4,
      "commentaire":"Prevu : 6 km optionnelle, tres facile ou repos, apres 3 jours de course consecutifs et fatigue signalee. Realise : sortie longue de 18,04 km non planifiee, decidee sur bonne sensation apres une tres bonne nuit. Discipline remarquable : FC quasi jamais au-dessus de 143 sur l'ensemble (plafond 140 vise, un seul pic isole a 157), allure stable a 6:30/km, effort relatif 93 seulement. Meilleure execution technique depuis le retour des USA (aucune derive, aucun coup de collier). Point de vigilance assume par Loic lui-meme : timing sous-optimal a 4 jours du Run In Lyon (allure marathon visee dimanche), sur une semaine deja chargee (3 jours consecutifs avant). Aucune douleur.",
      "pr":1,"ach":1,"pr_detail":[],
      "splits":[{"km":1,"allure":"6:39","fc":124},{"km":2,"allure":"6:31","fc":137},{"km":3,"allure":"6:32","fc":136},
                {"km":4,"allure":"6:41","fc":135},{"km":5,"allure":"6:29","fc":138},{"km":6,"allure":"6:34","fc":135},
                {"km":7,"allure":"6:42","fc":135},{"km":8,"allure":"6:37","fc":138},{"km":9,"allure":"6:29","fc":143},
                {"km":10,"allure":"6:38","fc":142},{"km":11,"allure":"6:33","fc":137},{"km":12,"allure":"6:39","fc":139},
                {"km":13,"allure":"6:42","fc":137},{"km":14,"allure":"6:25","fc":140},{"km":15,"allure":"6:29","fc":136},
                {"km":16,"allure":"6:38","fc":134},{"km":17,"allure":"6:14","fc":142},{"km":18,"allure":"6:16","fc":144}],
      "revue":_REVUE_FICHIER}
    arr.append({
      "id":6,"date":"2026-10-03","titre":"Activation avant Run In Lyon (non planifiee)","type":"Activation","sport":"Course à pied","opt":False,
      "accent":"#F4561D","fill":20,
      "sous":"Footing avec Yannis et Manon la veille du semi -- revele une FC anormalement elevee, probablement liee a 5 nuits de sommeil tres court.",
      "metriques":{"Distance":"7,04 km","Durée":"42 min","Allure":"libre","FC":"153 moy / 179 max","RPE":"5","Type":"Activation"},
      "objectif":"Prévu comme un footing très tranquille avant course avec les partenaires du semi. Devenu, de facto, un revelateur du cout cardiaque de la dette de sommeil accumulee depuis le debut de semaine.",
      "struct":[{"nom":"Corps","txt":"Footing avec Yannis et Manon, allure easy mais FC déjà élevée pour le rythme (150-156 bpm)."},
                {"nom":"Test de fin","txt":"Légère accélération volontaire sur le dernier kilomètre (5:10/km) -- FC montee a 174 de moyenne, pic 179. Reponse cardiaque disproportionnee par rapport a l'effort."}],
      "benefices":"A permis de mesurer concretement l'effet de la dette de sommeil avant la course, plutot que de le decouvrir en course.",
      "vigilance":"Aucune conclusion de fitness a tirer de cette séance -- c'est un signal de fatigue/sommeil, pas de forme. A reevaluer à la sensation des les premiers kilomètres du Run In Lyon.",
      "legende":[{"c":"#F4561D","l":"Activation"},{"c":"#dc2626","l":"FC anormalement elevee"}],
      "coach":[{"titre":"Le coeur paie avant les jambes","texte":"5 nuits a 3-4h de sommeil se voient d'abord sur la FC, avant meme que les jambes ne protestent. Ce n'est pas une question de forme, c'est une question de recuperation."},
               {"titre":"Pour demain","texte":"Caler sur le groupe 1h50 si le corps repond ; si la FC s'envole des les premiers kilometres, lacher le groupe et finir a la sensation est la bonne decision, pas un echec. Un chrono degrade demain n'invalide rien pour Nice."}],
      "segments":[{"nom":"Footing","role":"FC deja elevee (150-156) pour une allure easy, terrain plat.","duree":2170,"couleur":"vert","bloc":"\u2014","hauteur":40,"debut":0,"fin":2170},
                  {"nom":"Acceleration finale (test)","role":"5:10/km, FC 174 moy / 179 max -- reponse disproportionnee.","duree":310,"couleur":"rouge","bloc":"\u2014","hauteur":85,"debut":2170,"fin":2480}],
      "chaussure_realise":"ASICS Novablast 5 J",
      "realise":{"statut":"fait","km":7.04,"temps":"42:11","allure":"5:59/km","fc_moy":153,"fc_max":179,"re":82,
        "cadence":85,"elevation_gain":15,"kcal":564,"rpe_ressenti":5,
        "commentaire":"Footing d'activation non planifie avec Yannis et Manon (partenaires du Run In Lyon), veille du semi. 5e nuit de suite a 3-4h de sommeil (4h07 la nuit precedente). FC anormalement elevee pour l'allure (150-156 pour 5:40-6:20/km, terrain plat). Test d'acceleration volontaire sur le dernier km : 5:10/km pour FC 174 moy/179 max -- reponse cardiaque disproportionnee, confirmant le ressenti de Loic. Aucune douleur. Pas de conclusion de fitness a tirer, signal de dette de sommeil pure.",
        "pr":2,"ach":2,"pr_detail":[],
        "splits":[{"km":1,"allure":"5:56","fc":150},{"km":2,"allure":"5:47","fc":154},{"km":3,"allure":"6:51","fc":137},
                  {"km":4,"allure":"6:14","fc":153},{"km":5,"allure":"6:20","fc":151},{"km":6,"allure":"5:41","fc":156},
                  {"km":7,"allure":"5:10","fc":174}],
        "revue":_REVUE_FICHIER}
    })
    arr.append({
      "id":7,"date":"2026-10-04","titre":"Run/marche avec Perrine (15 x 1 min / 1 min)","type":"R\u00e9cup\u00e9ration active","sport":"Course \u00e0 pied","opt":True,
      "accent":"#6B6B74","fill":10,
      "sous":"Sortie du soir du semi, en run/marche avec Perrine : aucun enjeu d'entrainement.",
      "metriques":{"Distance":"3,78 km","Dur\u00e9e":"36 min","Allure":"libre","FC":"111 moy / 137 max","RPE":"2","Type":"R\u00e9cup"},
      "objectif":"Sortie sociale non planifiee, le soir du semi : 15 fois 1 min de course et 1 min de marche. Aucun objectif de performance.",
      "struct":[{"nom":"Corps","txt":"15 x (1 min de course, 1 min de marche), puis 5 min de marche."}],
      "benefices":"Remise en jambes douce le soir d'un effort maximal, partagee avec Perrine.",
      "vigilance":"Aucune : charge negligeable (effort relatif 7).",
      "legende":[{"c":"#16a34a","l":"Course"},{"c":"#A1A1AA","l":"Marche"}],
      "coach":[{"titre":"Rien a corriger","texte":"3,8 km a FC 111 en moyenne le soir d'un semi couru a FC 177 : c'est de la recuperation, pas de l'entrainement."}],
      "segments":[{"nom":"Run/marche 15 x 1 min / 1 min","role":"3,78 km, FC 111 moy / 137 max.","duree":2150,"couleur":"vert","bloc":"\u2014","hauteur":24,"debut":0,"fin":2150}],
      "chaussure_realise":"ASICS Gel Pulse 16",
      "realise":{"statut":"fait","km":3.78,"temps":"35:50","allure":"9:28/km","fc_moy":111,"fc_max":137,"re":7,
        "cadence":73,"elevation_gain":13,"kcal":267,"rpe_ressenti":2,
        "commentaire":"Sortie du soir du semi (18h35) avec Perrine : 15 x 1 min de course / 1 min de marche, 3,78 km en 35:50, FC 111 moy / 137 max, effort relatif 7. Aucun enjeu. Ajoutee au log pour que les totaux (semaine, mois, saison) correspondent a Strava.",
        "pr":0,"ach":0,"pr_detail":[]}
    })

for n, arr in list(SEANCES_BY_WEEK.items()):
    if n != "41":
        continue
    _S41 = {str(x["id"]): x for x in arr}
    _S41["1"]["titre"]="Footing de recuperation"
    _S41["1"]["sous"]="Lendemain de semi : on laisse le corps digerer, sans forcer."
    _S41["1"]["metriques"]={"Distance":"8 km","Durée":"~50 min","Allure":"5:50-6:25/km","FC":"135-150","RPE":"2-3","Type":"Récup"}
    _S41["1"]["struct"]=[{"nom":"Corps","txt":"8 km très faciles, FC sous 150. Lendemain de semi : la séance sert à décrasser, pas à construire."}]
    _S41["1"]["segments"]=[{"nom":"Footing de récup","role":"8,04 km à 6:09/km, FC 142.","duree":2963,"couleur":"vert","bloc":"—","hauteur":30,"debut":0,"fin":2963}]
    _S41["1"]["chaussure_realise"]="ASICS Novablast 5 J"
    _S41["1"]["realise"]={"statut":"fait","decouplage":{"pct":10.97,"bpm":3.0,"fen_min":43,"temp":19,"attendu":6,"p1":"6:02/km","fc1":141,"p2":"6:12/km","fc2":144,"qualite":"incertain","algo":"decoup-v1"},"temp":19,"km":8.04,"temps":"49:23","allure":"6:09/km","fc_moy":142,"fc_max":159,"re":59,
      "cadence":87,"elevation_gain":34,"kcal":621,"rpe_ressenti":3,
      "commentaire":"Prevu : footing facile 12 km, 5:50-6:25/km, FC 135-150. Realise : 8,04 km de recuperation au lendemain du semi (decision de Loic, plus court que prevu). 6:09/km pour FC 142 moy / 159 max : dans le cadre. A allure quasi identique, 11 bpm de moins que l'activation du 03/10 (5:59/km pour 153) et meme niveau que le footing du 28/09 (6:05 pour 143), donc retour a la ligne de base d'avant la maladie. FC 134 au km1, 149 au km8, en phase avec une allure qui passe de 6:23 a 5:58. Aucune douleur.",
      "pr":0,"ach":0,"pr_detail":[],
      "splits":[{"km":1,"allure":"6:23","fc":134},{"km":2,"allure":"6:17","fc":138},{"km":3,"allure":"5:48","fc":143},
                {"km":4,"allure":"6:07","fc":143},{"km":5,"allure":"6:13","fc":143},{"km":6,"allure":"6:22","fc":142},
                {"km":7,"allure":"6:03","fc":145},{"km":8,"allure":"5:58","fc":149}],
      "revue":_REVUE_FICHIER}
    _S41["2"]["chaussure_realise"]="ASICS Novablast 5 J"
    _S41["2"]["segments"]=[
      {"nom":"Échauffement","role":"2,63 km à 5:59 puis 5:31 et 5:34/km, FC 147-155.","duree":900,"couleur":"vert","bloc":"—","hauteur":34},
      {"nom":"Bloc AM 1/3","role":"4 km à 5:18/km, FC 159.","duree":1270,"couleur":"bleu","bloc":"×3","hauteur":80},
      {"nom":"Récup 1","role":"523 m à 5:44/km, FC 152.","duree":179,"couleur":"orange","bloc":"—","hauteur":30},
      {"nom":"Bloc AM 2/3","role":"4 km à 5:18/km, FC 159.","duree":1272,"couleur":"bleu","bloc":"×3","hauteur":80},
      {"nom":"Récup 2","role":"522 m à 5:45/km, FC 151 (arrêt d'environ 100 s).","duree":281,"couleur":"orange","bloc":"—","hauteur":30},
      {"nom":"Bloc AM 3/3","role":"4 km à 5:18/km, FC 162.","duree":1293,"couleur":"bleu","bloc":"×3","hauteur":80},
      {"nom":"Final","role":"380 m à 4:54/km, FC 170 moy / 176 max, sans retour au calme.","duree":112,"couleur":"rouge","bloc":"—","hauteur":58}]
    _S41["2"]["segments"]=segs(_S41["2"]["segments"])
    _S41["2"]["realise"]={"statut":"fait","km":16.05,"temps":"1:26:31","allure":"5:23/km","fc_moy":158,"fc_max":176,"re":199,
      "cadence":86,"elevation_gain":31,"kcal":1244,"rpe_ressenti":6,
      "commentaire":"Prevu : 3x4 km a allure marathon (cible 5:20, fenetre 5:15-5:25), recup 3 min, FC 152-163. Realise : echauffement 2,63 km (15:00), puis blocs a 5:18, 5:18, 5:18/km de moyenne (FC 159, 159, 162), soit 12 km dont 11 dans la fenetre, un seul a 5:12 ; ecart total de 13 s/km sur 12 km. Derive cardiaque de +3 bpm entre bloc 1 et bloc 3 a allure identique. Deux km a 165 et 164, d'un a deux bpm au-dessus du plafond 163. Recups a 5:44-5:45/km (FC 151-152), la seconde de 4:41 (arret ~100 s). Termine par 380 m a 4:54/km (FC 176 max), sans retour au calme enregistre. 4e sortie d'affilee depuis samedi, 2 jours apres le semi. Aucune douleur.",
      "pr":27,"ach":27,"pr_detail":[],
      "splits":[{"km":"Ech.1","allure":"5:59","fc":147},{"km":"Ech.2","allure":"5:31","fc":153},{"km":"Ech.3","allure":"5:34","fc":155},
                {"km":"B1-1","allure":"5:18","fc":159},{"km":"B1-2","allure":"5:17","fc":159},{"km":"B1-3","allure":"5:15","fc":158},{"km":"B1-4","allure":"5:21","fc":158},
                {"km":"R1","allure":"5:44","fc":152},
                {"km":"B2-1","allure":"5:21","fc":156},{"km":"B2-2","allure":"5:12","fc":160},{"km":"B2-3","allure":"5:17","fc":158},{"km":"B2-4","allure":"5:23","fc":160},
                {"km":"R2","allure":"5:45","fc":151},
                {"km":"B3-1","allure":"5:16","fc":160},{"km":"B3-2","allure":"5:16","fc":165},{"km":"B3-3","allure":"5:17","fc":164},{"km":"B3-4","allure":"5:25","fc":159},
                {"km":"Final","allure":"4:54","fc":170}],
      "revue":_REVUE_FICHIER}
    _S41["3"]["titre"]="Vallonne chill (Fourviere, Signal)"
    _S41["3"]["sous"]="Remplace le footing plat : une sortie vallonnee a l'effort, sous la pluie."
    _S41["3"]["metriques"]={"Distance":"~15 km","Dur\u00e9e":"~90 min","Allure":"\u00e0 l'effort","FC":"135-155","RPE":"3-4","Type":"Vallonn\u00e9"}
    _S41["3"]["objectif"]="Décision de Loïc : une séance de dénivelé dans la semaine plutôt que le footing plat. Rester à l'effort facile : on laisse l'allure payer la pente, la FC sert de juge."
    _S41["3"]["struct"]=[{"nom":"Corps","txt":"Sortie vallonnee (Fourviere, Saint-Irenee, Signal), effort facile. Allure libre, FC visee sous 155 en montee et sous 145 sur le plat."}]
    _S41["3"]["segments"]=[
      {"nom":"Mise en route","role":"3 km plats \u00e0 6:03-6:12/km, FC 133-141.","duree":1101,"couleur":"vert","bloc":"\u2014","hauteur":32},
      {"nom":"Premi\u00e8res mont\u00e9es","role":"3 km, D+ ~141 m (4 \u00e0 6 %, escaliers), 6:14 \u00e0 6:38/km, FC 145-158, pic 180.","duree":1205,"couleur":"orange","bloc":"\u2014","hauteur":62},
      {"nom":"Plateau et descente","role":"3 km, 6:10 \u00e0 5:46/km, FC 135-148.","duree":1105,"couleur":"vert","bloc":"\u2014","hauteur":36},
      {"nom":"2e mont\u00e9e","role":"1 km \u00e0 6:14/km, D+ 49 m, FC 157, pic 178.","duree":374,"couleur":"orange","bloc":"\u2014","hauteur":62},
      {"nom":"Descentes","role":"2 km \u00e0 5:38 puis 5:18/km (pente jusqu'\u00e0 -8,6 %), FC 142-147.","duree":656,"couleur":"vert","bloc":"\u2014","hauteur":34},
      {"nom":"Retour plat","role":"3 km \u00e0 5:34-5:40/km, FC 145-153.","duree":1146,"couleur":"vert","bloc":"\u2014","hauteur":38}]
    _S41["3"]["segments"]=segs(_S41["3"]["segments"])
    _S41["3"]["chaussure_realise"]="HOKA Clifton 10"
    _S41["3"]["realise"]={"statut":"fait","km":15.06,"temps":"1:30:06","allure":"5:59/km","fc_moy":146,"fc_max":180,"re":119,
      "cadence":86,"elevation_gain":242,"kcal":1149,"rpe_ressenti":4,
      "commentaire":"Prevu : footing facile 12 km plat, 5:50-6:25/km, FC 135-150. Realise : sortie vallonnee de 15,06 km sous la pluie (decision de Loic de faire une seance de denivele dans la semaine), D+ 242 m. FC moyenne 146 : dans la zone d'un footing facile malgre le relief. Plat et descente a 133-142, montees a 4-6 % a 156-158 pour 6:23-6:38/km. Deux raidillons d'environ 70 s a 175 bpm (Decourtray, finish Fourviere) et un pic a 180 sur le chemin du Signal (escaliers, cadence 50-57). Descentes rapides (5:38 a -8,6 %, 5:18) pour un cout cardiaque de 142-147. 5e jour de course d'affilee depuis samedi, 3e sortie en 3 jours. Aucune douleur signalee.",
      "pr":3,"ach":3,"pr_detail":[],
      "splits":[{"km":1,"allure":"6:07","fc":133},{"km":2,"allure":"6:03","fc":134},{"km":3,"allure":"6:12","fc":141},
                {"km":4,"allure":"6:14","fc":145},{"km":5,"allure":"6:23","fc":156},{"km":6,"allure":"6:38","fc":158},
                {"km":7,"allure":"6:10","fc":148},{"km":8,"allure":"6:09","fc":140},{"km":9,"allure":"5:46","fc":135},
                {"km":10,"allure":"6:14","fc":157},{"km":11,"allure":"5:38","fc":142},{"km":12,"allure":"5:18","fc":147},
                {"km":13,"allure":"5:40","fc":153},{"km":14,"allure":"5:34","fc":145},{"km":15,"allure":"5:35","fc":151}],
      "revue":_REVUE_FICHIER}
    _S41["4"]["date"]="2026-10-09"
    _S41["4"]["sous"]="Longue en ENDURANCE pure, avancee au vendredi 9 octobre (week-end indisponible)."
    _S41["4"]["segments"]=segs([
      {"nom":"Km 1-10","role":"10 km a 5:40/km, FC 145 (137 au km 1).","duree":3400,"couleur":"vert","bloc":"\u2014","hauteur":36},
      {"nom":"Km 11-20","role":"10 km a 5:40/km, FC 150.","duree":3404,"couleur":"vert","bloc":"\u2014","hauteur":40},
      {"nom":"Km 21-30","role":"10,13 km a 5:37/km, FC 152, pointes a 162-167 en cote ; derniers km a 5:22, 5:26 puis 5:11.","duree":3410,"couleur":"orange","bloc":"\u2014","hauteur":46}])
    _S41["4"]["chaussure_realise"]="ASICS Novablast 5 J"
    _S41["4"]["realise"]={"statut":"fait","decouplage":{"pct":6.77,"bpm":4.1,"fen_min":161,"temp":16,"attendu":8,"p1":"5:36/km","fc1":147,"p2":"5:40/km","fc2":151,"qualite":"fiable","algo":"decoup-v1"},"temp":16,"km":30.13,"temps":"2:50:14","allure":"5:39/km","fc_moy":149,"fc_max":167,"re":281,
      "cadence":88,"elevation_gain":100,"kcal":2277,"rpe_ressenti":5,
      "commentaire":"Prevu : longue endurance ~26 km, 5:50-6:25/km, FC 135-150, dimanche 11/10. Realise le vendredi 09/10 (week-end indisponible) : 30,13 km en 2:50:14 de deplacement (2:56:38 ecoulees, 7 arrets pour 6 min 24 s en tout, dont 1 min 48 au km 7 et 1 min 13 au km 27). 5:39/km pour FC 149 moy / 167 max, D+ 100 m. Allure quasi constante par tranche de 10 km (5:40, 5:40, 5:37) avec une FC de 145, 150 puis 152 : derive de +7 bpm, soit une perte de 4 % du rapport vitesse/FC. Allure 11 s/km au-dessus de la borne rapide du plan et FC moyenne sur le plafond de 150 (11 km au-dessus). Trois derniers km a 5:22, 5:26 et 5:11. Plus longue sortie routiere de la saison (precedente : 25 km le 22/08). Veille : repos (08/10), apres 5 jours de course d'affilee. Aucune douleur signalee.",
      "pr":26,"ach":27,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:53","fc":137},{"km":2,"allure":"5:46","fc":143},{"km":3,"allure":"5:35","fc":147},{"km":4,"allure":"5:44","fc":146},{"km":5,"allure":"5:34","fc":147},{"km":6,"allure":"5:49","fc":147},{"km":7,"allure":"5:47","fc":142},{"km":8,"allure":"5:40","fc":144},{"km":9,"allure":"5:24","fc":148},{"km":10,"allure":"5:28","fc":149},{"km":11,"allure":"5:38","fc":148},{"km":12,"allure":"5:52","fc":144},{"km":13,"allure":"5:31","fc":152},{"km":14,"allure":"5:43","fc":153},{"km":15,"allure":"5:24","fc":152},{"km":16,"allure":"5:26","fc":156},{"km":17,"allure":"5:42","fc":148},{"km":18,"allure":"5:37","fc":149},{"km":19,"allure":"5:47","fc":147},{"km":20,"allure":"6:04","fc":148},{"km":21,"allure":"5:42","fc":153},{"km":22,"allure":"5:44","fc":158},{"km":23,"allure":"5:27","fc":157},{"km":24,"allure":"5:51","fc":152},{"km":25,"allure":"5:41","fc":151},{"km":26,"allure":"5:43","fc":148},{"km":27,"allure":"6:07","fc":144},{"km":28,"allure":"5:22","fc":150},{"km":29,"allure":"5:26","fc":151},{"km":30,"allure":"5:11","fc":156}],
      "revue":_REVUE_FICHIER}
    _S41["5"]["realise"]={"statut":"skipped","reason":"Journee de repos le 08/10","km":0,"temps":"\u2014","allure":"\u2014","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Non realisee : journee de repos le 08/10, entre le vallonne du 07/10 et la longue du 09/10.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}


for n, arr in list(SEANCES_BY_WEEK.items()):
    if n != "42":
        continue
    _S42 = {str(x["id"]): x for x in arr}
    _S42["1"]["titre"]="Allure marathon 10 km (remplace le footing)"
    _S42["1"]["sous"]="Footing facile prévu remplacé par 10 km à allure marathon, cible 5:20/km."
    _S42["1"]["metriques"]={"Distance":"10 km","Durée":"~52 min","Allure":"≈5:20/km","FC":"152-163","RPE":"6","Type":"Allure marathon"}
    _S42["1"]["objectif"]="Tenir 5:20/km en continu, sans descendre sous 5:15 : la difficulté est de ne pas dépasser la cible, pas de l'atteindre."
    _S42["1"]["struct"]=[{"nom":"Corps","txt":"10 km continus à 5:20/km, FC dans la fenêtre 152-163. Pas de relance avant la fin."}]
    _S42["1"]["segments"]=segs([
      {"nom":"Km 1-2","role":"2 km à 5:07 puis 5:14/km, FC 155-159 : départ trop vif.","duree":621,"couleur":"orange","bloc":"—","hauteur":50},
      {"nom":"Km 3-6","role":"4 km à 5:17, 5:22, 5:17, 5:16/km, FC 158-164 : la cible tenue.","duree":1272,"couleur":"bleu","bloc":"—","hauteur":80},
      {"nom":"Km 7-10","role":"4 km à 5:06, 5:09, 5:11 puis 4:52/km, FC 161-168, pic 177.","duree":1234,"couleur":"rouge","bloc":"—","hauteur":62}])
    _S42["1"]["chaussure_realise"]="HOKA Clifton 10"
    _S42["1"]["realise"]={"statut":"fait","km":10.05,"temps":"52:07","allure":"5:11/km","fc_moy":161,"fc_max":177,"re":137,
      "cadence":88,"elevation_gain":26,"kcal":773,"rpe_ressenti":6,
      "commentaire":"Prévu : footing facile 12 km, 5:50-6:25/km, FC 135-150. Réalisé : 10,05 km à allure marathon (cible 5:20/km) en 52:07, 5:11/km, FC 161 moy / 177 max, D+ 26 m, RE 137, Clifton 10. Km 3 à 6 tenus à 5:16-5:22 (FC 158-164) ; départ à 5:07-5:14 et finish à 5:06, 5:09, 5:11 puis 4:52 (FC 168). Cinq derniers km à 5:07 contre 5:15 pour les cinq premiers.",
      "pr":8,"ach":8,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:07","fc":155},{"km":2,"allure":"5:14","fc":159},{"km":3,"allure":"5:17","fc":164},
                {"km":4,"allure":"5:22","fc":159},{"km":5,"allure":"5:17","fc":159},{"km":6,"allure":"5:16","fc":158},
                {"km":7,"allure":"5:06","fc":161},{"km":8,"allure":"5:09","fc":164},{"km":9,"allure":"5:11","fc":166},
                {"km":10,"allure":"4:52","fc":168}],
      "revue":_REVUE_FICHIER}

    _S42["2"]["chaussure_realise"]="ASICS Novablast 5 J"
    _S42["2"]["segments"]=segs([
      {"nom":"Km 1-3","role":"3 km a 5:17/km, FC 142 puis 154-155.","duree":951,"couleur":"vert","bloc":"\u2014","hauteur":50},
      {"nom":"Montee Chemin Neuf","role":"2 km a 6:27 et 6:09/km, pente 6 %, D+ 124 m, FC 163-169, pic 178.","duree":756,"couleur":"orange","bloc":"\u2014","hauteur":72},
      {"nom":"Plateau et descentes","role":"4 km entre 4:49 et 5:36/km (descentes a -5,5 %), FC 156-161.","duree":960,"couleur":"bleu","bloc":"\u2014","hauteur":58},
      {"nom":"Km 10-15","role":"6 km a 4:52/km (4:44 a 4:58), FC 163-167, sur les quais du Rhone.","duree":1062,"couleur":"rouge","bloc":"\u2014","hauteur":78}])
    _S42["2"]["realise"]={"statut":"fait","decouplage":{"qualite":"non_representatif","temp":21,"algo":"decoup-v1"},"temp":21,"km":15.04,"temps":"1:18:49","allure":"5:14/km","fc_moy":161,"fc_max":178,"re":206,
      "cadence":88,"elevation_gain":165,"kcal":1163,"rpe_ressenti":7,
      "commentaire":"Prevu : footing facile + 6 lignes droites, ~12 km, 5:50-6:25/km, FC 135-150. Realise : sortie vallonnee de 15,04 km (Fourviere, Chemin Neuf, tunnel de la Croix-Rousse) en 1:18:49, 5:14/km, FC 161 moy / 178 max, D+ 165 m. Km 1 a 5:24 (FC 142), 5:08 des le km 2 (FC 154). Montee du Chemin Neuf aux km 4-5 (pente 6 %) a 6:27 et 6:09, FC 163-169, pic 178. Descentes a 4:49 et 5:36 (-5,5 %). Les 6 derniers km sont a 4:52 de moyenne (4:44 a 4:58) avec FC 163-167 : un tempo, 28 s/km plus vite que l'allure marathon. 3 km de plus que prevu, effort relatif 206 pour environ 65 attendus, lendemain des 10 km a allure marathon. Aucune douleur signalee.",
      "pr":22,"ach":22,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:24","fc":142},{"km":2,"allure":"5:08","fc":154},{"km":3,"allure":"5:19","fc":155},{"km":4,"allure":"6:27","fc":163},{"km":5,"allure":"6:09","fc":169},{"km":6,"allure":"5:26","fc":159},{"km":7,"allure":"4:49","fc":156},{"km":8,"allure":"5:36","fc":158},{"km":9,"allure":"5:09","fc":161},{"km":10,"allure":"4:52","fc":163},{"km":11,"allure":"4:51","fc":165},{"km":12,"allure":"4:58","fc":165},{"km":13,"allure":"4:44","fc":166},{"km":14,"allure":"4:52","fc":166},{"km":15,"allure":"4:54","fc":167}],
      "revue":_REVUE_FICHIER}
    _S42["3"]["chaussure_realise"]="HOKA Clifton 10"
    _S42["3"]["segments"]=segs([
      {"nom":"Km 1-4","role":"4 km a 5:53/km, FC 142-146.","duree":1412,"couleur":"vert","bloc":"\u2014","hauteur":40},
      {"nom":"Montee du Signal","role":"3 km a 6:09, 6:13 puis 6:42/km, D+ 133 m, FC 154-164, pic 182 dans les marches.","duree":1144,"couleur":"orange","bloc":"\u2014","hauteur":72},
      {"nom":"Plateau et descentes","role":"4 km a 5:51, 5:40, 5:21 puis 5:35/km (jusqu'a -6,7 %), FC 144-147.","duree":1387,"couleur":"vert","bloc":"\u2014","hauteur":44},
      {"nom":"Retour","role":"2 km a 5:35 et 5:34/km, FC 159 puis 153.","duree":678,"couleur":"bleu","bloc":"\u2014","hauteur":54}])
    _S42["3"]["realise"]={"statut":"fait","decouplage":{"pct":12.92,"bpm":10.2,"fen_min":54,"temp":23,"attendu":6,"p1":"5:58/km","fc1":146,"p2":"6:12/km","fc2":156,"qualite":"incertain","algo":"decoup-v1"},"temp":23,"km":13.04,"temps":"1:17:01","allure":"5:54/km","fc_moy":151,"fc_max":182,"re":137,
      "cadence":88,"elevation_gain":185,"kcal":1030,"rpe_ressenti":5,
      "commentaire":"Prevu : footing facile ~11 km, 5:50-6:25/km, FC 135-150. Realise avec Yannis (titre Strava) : 13,04 km vallonnes (Fourviere, Chemin du Signal, descentes du Gourguillon) en 1:17:01 de deplacement (1:20:10 ecoulees, ~3 min d'arret), 5:54/km, FC 151 moy / 182 max, D+ 185 m. Km 1-4 a 5:53 de moyenne (FC 142-146), dans le cadre. Montee du Signal aux km 5-7 (D+ 133 m) a 6:09, 6:13 puis 6:42, FC 154 -> 164, pic 182 dans les marches. Descentes a 5:51, 5:40 et 5:21 (jusqu'a -6,7 %) pour FC 144-147. Deux derniers km a 5:35 et 5:34 (FC 159, 153). 3e jour de course d'affilee (12, 13 et 14/10), 2 km de plus que prevu, effort relatif 137 pour environ 65 attendus. Aucune douleur signalee.",
      "pr":7,"ach":7,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:26","fc":142},{"km":2,"allure":"5:59","fc":142},{"km":3,"allure":"6:00","fc":143},{"km":4,"allure":"6:07","fc":146},{"km":5,"allure":"6:09","fc":154},{"km":6,"allure":"6:13","fc":161},{"km":7,"allure":"6:42","fc":164},{"km":8,"allure":"6:15","fc":153},{"km":9,"allure":"5:51","fc":147},{"km":10,"allure":"5:40","fc":144},{"km":11,"allure":"5:21","fc":146},{"km":12,"allure":"5:35","fc":159},{"km":13,"allure":"5:34","fc":153}],
      "revue":_REVUE_FICHIER}
    _S42["4"]["date"]="2026-10-15"
    _S42["4"]["sous"]="Longue specifique avancee au jeudi 15 octobre : 15 km faciles puis 15 km a allure marathon."
    _S42["4"]["segments"]=segs([
      {"nom":"Km 1-7 en solo","role":"7 km a 5:35/km, FC 146.","duree":2345,"couleur":"vert","bloc":"\u2014","hauteur":40},
      {"nom":"Km 8-15 a deux","role":"8 km a 5:35/km, FC 150, rejoint par une amie.","duree":2683,"couleur":"vert","bloc":"\u2014","hauteur":44},
      {"nom":"Bloc AM km 16-25","role":"10 km a 5:12/km en deplacement, 5:25 ecoules avec 2 arrets, FC 160.","duree":3123,"couleur":"bleu","bloc":"AM","hauteur":72},
      {"nom":"Finish km 26-30","role":"5 km a 5:10/km, FC 165, pic 171.","duree":1548,"couleur":"orange","bloc":"AM","hauteur":78}])
    _S42["4"]["chaussure_realise"]="ASICS Novablast 5 V"
    _S42["4"]["realise"]={"statut":"fait","decouplage":{"qualite":"non_representatif","temp":12,"algo":"decoup-v1"},"temp":12,"km":30.06,"temps":"2:41:56","allure":"5:23/km","fc_moy":155,"fc_max":171,"re":342,
      "cadence":90,"elevation_gain":74,"kcal":2269,"rpe_ressenti":6,
      "commentaire":"Prevu : longue 30 km, 16 EF puis 14 AM (5:20/km, FC 152-163). Realise le jeudi 15/10 (avancee de 3 jours) : 30,06 km en 2:41:56 de deplacement, 5:23/km, FC 155 moy / 171 max, D+ 74 m, Novablast 5 V. Km 1-15 faciles a 5:35/km (FC 148), rejointe par une amie du km 8 au km 30 : FC 146 en solo, 150 a deux a meme allure. Km 16-30 a allure marathon : 5:11/km en deplacement, 5:20 ecoules (2 arrets aux km 21 et 25, 122 s), FC 161,5 ; 9 km sous la fenetre 5:15-5:25, aucun au-dessus, plus vif 4:53 (km 19). Rapport vitesse/FC de 20,1 a 19,5 entre les km 16-19 et 27-30 (-3 %) : pas de decouplage aerobie net. 4e jour de course d'affilee (RE 137, 206, 137, 342). Nutrition : petit-dejeuner 1h30 avant (banane, proteines, cafe), 1 electrolyte Fort Endurance juste avant le depart, 3 gels a 45 min, 1h30 et 2h15 (le 3e a eu du mal a passer), environ 1,5 L bu en tout. RPE 6 ressenti (Loic).",
      "pr":54,"ach":55,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:33","fc":146},{"km":2,"allure":"5:34","fc":147},{"km":3,"allure":"5:39","fc":148},{"km":4,"allure":"5:39","fc":145},{"km":5,"allure":"5:36","fc":146},{"km":6,"allure":"5:34","fc":144},{"km":7,"allure":"5:30","fc":149},{"km":8,"allure":"5:41","fc":150},{"km":9,"allure":"5:36","fc":153},{"km":10,"allure":"5:24","fc":152},{"km":11,"allure":"5:32","fc":151},{"km":12,"allure":"5:35","fc":149},{"km":13,"allure":"5:33","fc":147},{"km":14,"allure":"5:39","fc":149},{"km":15,"allure":"5:43","fc":152},{"km":16,"allure":"5:20","fc":159},{"km":17,"allure":"5:19","fc":159},{"km":18,"allure":"5:08","fc":165},{"km":19,"allure":"4:53","fc":160},{"km":20,"allure":"5:14","fc":159},{"km":21,"allure":"5:16","fc":158},{"km":22,"allure":"5:18","fc":159},{"km":23,"allure":"5:07","fc":161},{"km":24,"allure":"5:15","fc":157},{"km":25,"allure":"5:13","fc":161},{"km":26,"allure":"5:10","fc":164},{"km":27,"allure":"5:08","fc":165},{"km":28,"allure":"5:15","fc":166},{"km":29,"allure":"5:09","fc":165},{"km":30,"allure":"5:06","fc":166}],
      "revue":_REVUE_FICHIER}
    _S42["5"]["realise"]={"statut":"skipped","reason":"Repos assumé après la longue du 15/10","km":0,"temps":"\u2014","allure":"\u2014","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Non réalisée : repos assumé après la longue de 30 km du 15/10, pas de rattrapage.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}
    _S42["6"]["realise"]={"statut":"skipped","reason":"Repos assumé après la longue du 15/10","km":0,"temps":"\u2014","allure":"\u2014","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Non réalisée : mobilité non faite le 16/10, pas de rattrapage.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}
    arr.append({
      "id":7,"date":"2026-10-17","titre":"Footing de recuperation (non planifie)","type":"Récupération active","sport":"Course à pied","opt":False,
      "accent":"#16a34a","fill":22,
      "sous":"Footing facile deux jours apres la longue de 30 km, ajoute au plan : seule intention, aider la recuperation.",
      "metriques":{"Distance":"11,14 km","Durée":"1h08","Allure":"6:07/km","FC":"137 moy / 176 max","RPE":"3","Type":"Récupération"},
      "objectif":"Faire circuler le sang sans coût de fatigue, deux jours après la longue spécifique du 15/10 et en pleine semaine de charge élevée.",
      "struct":[{"nom":"Corps","txt":"Footing facile, FC 135-145, allure 6:10-6:30/km, terrain plat. Aucune relance."}],
      "benefices":"Récupération active après un 30 km, entretien de l'économie de course sans fatigue ajoutée.",
      "vigilance":"Partir plus lentement que ce que les jambes proposent : les 10 premières minutes décident du reste de la sortie.",
      "legende":[{"c":"#16a34a","l":"Facile"},{"c":"#CA8A04","l":"Départ trop vif"}],
      "coach":[{"titre":"Le départ décide","texte":"Les 4 premiers km sont partis à 5:35-5:57 pour une FC de 138-149 ; dès le km 5, 6:17 à 134. Le même footing partait à 6:15 dès le début aurait coûté encore moins."}],
      "segments":segs([{"nom":"Départ trop vif","role":"4 km à 5:51/km, FC 138-149 (149 au km 3).","duree":1403,"couleur":"orange","bloc":"\u2014","hauteur":58},
                  {"nom":"Allure de récupération","role":"7 km à 6:17/km, FC 132-136.","duree":2682,"couleur":"vert","bloc":"\u2014","hauteur":36}]),
      "chaussure_realise":"HOKA Clifton 10",
      "realise":{"statut":"fait","decouplage":{"pct":-1.89,"bpm":-7.7,"fen_min":60,"temp":16,"attendu":6,"p1":"6:01/km","fc1":141,"p2":"6:16/km","fc2":134,"qualite":"fiable","algo":"decoup-v1"},"temp":16,"km":11.14,"temps":"1:08:04","allure":"6:07/km","fc_moy":137,"fc_max":176,"re":49,
        "cadence":88,"elevation_gain":26,"kcal":854,"rpe_ressenti":3,
        "commentaire":"Footing de recuperation non planifie du samedi 17/10, 2 jours apres la longue de 30 km, jambes lourdes mais aucune douleur. 11,14 km en 1:08:04 de deplacement, 6:07/km, FC 137 moy / 176 max (pic isole au km 3), D+ 26 m, Clifton 10. Km 1-4 trop vifs (5:55, 5:56, 5:35, 5:57, FC 138-149) puis 6:17/km a FC 134 du km 5 au km 11. A allure egale (6:06-6:13), FC 134-135 contre 142-143 le 05/10 : cardio recupere. RPE 3 estime par Claude.",
        "pr":2,"ach":2,"pr_detail":[],
        "splits":[{"km":1,"allure":"5:55","fc":138},{"km":2,"allure":"5:56","fc":142},{"km":3,"allure":"5:35","fc":149},{"km":4,"allure":"5:57","fc":144},{"km":5,"allure":"6:24","fc":136},{"km":6,"allure":"6:35","fc":132},{"km":7,"allure":"6:17","fc":133},{"km":8,"allure":"6:17","fc":133},{"km":9,"allure":"6:06","fc":134},{"km":10,"allure":"6:13","fc":135},{"km":11,"allure":"6:06","fc":135}],
        "revue":_REVUE_FICHIER}
    })

for n, arr in list(SEANCES_BY_WEEK.items()):
    if n != "43":
        continue
    _S43 = {str(x["id"]): x for x in arr}
    _S43["1"]["realise"]={"statut":"skipped","reason":"Pluie le 19/10","km":0,"temps":"\u2014","allure":"\u2014","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Non réalisée : pluie soutenue à Lyon le lundi 19/10, pas de rattrapage.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}
    _S43["2"]["date"]="2026-10-21"
    _S43["2"]["titre"]="Allure marathon 11 km (decalee a mercredi, continue)"
    _S43["2"]["sous"]="2x6 km annules mardi (pluie) : 11 km continus a allure marathon le mercredi 21/10, cible 5:20/km."
    _S43["2"]["metriques"]={"Distance":"11 km","Durée":"~58 min","Allure":"≈5:20/km","FC":"152-163","RPE":"6","Type":"Allure marathon"}
    _S43["2"]["objectif"]="Tenir 5:20/km en continu, sans descendre sous 5:15 : dernier rappel du rythme avant l'affutage."
    _S43["2"]["struct"]=[{"nom":"Corps","txt":"11 km continus a 5:20/km, FC dans la fenetre 152-163. Pas de relance avant la fin."}]
    _S43["2"]["segments"]=segs([
      {"nom":"Km 1-2","role":"5:11 puis 5:09/km, FC 143 -> 156 : depart direct a allure marathon, sans echauffement separe.","duree":620,"couleur":"orange","bloc":"\u2014","hauteur":55},
      {"nom":"Km 3-8","role":"6 km a 5:22, 5:18, 5:12, 5:15, 5:15, 5:13/km, FC 153-159 : le coeur du bloc, regulier.","duree":1895,"couleur":"bleu","bloc":"\u2014","hauteur":80},
      {"nom":"Km 9-11","role":"5:05, 5:11 puis 5:22/km (arret d'environ 22 s), FC 157-160 : pas de finish emballe.","duree":940,"couleur":"bleu","bloc":"\u2014","hauteur":80}])
    _S43["2"]["chaussure_realise"]="HOKA Clifton 10"
    _S43["2"]["realise"]={"statut":"fait","km":11.01,"temps":"57:35","allure":"5:14/km","fc_moy":156,"fc_max":167,"re":122,
      "cadence":86,"elevation_gain":30,"kcal":824,"rpe_ressenti":6,
      "commentaire":"Prevu : allure marathon 2x6 km le mardi 20/10, annule par la pluie. Realise le mercredi 21/10 : 11,01 km continus en 57:35, 5:14/km, FC 156 moy / 167 max, D+ 30 m, RE 122, Clifton 10, pluie. Regulier (5:05 a 5:22, ecart-type 5 s/km), pas de finish emballe. FC mesuree a la montre seule, sans ceinture (a prendre avec reserve). Fatigue plus marquee que d'habitude apres la longue du 15/10 ; pause volontaire dimanche, puis pluie lundi et mardi, qui ont fait du bien au physique et au mental. Le RPE est une estimation.",
      "pr":3,"ach":3,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:11","fc":143},{"km":2,"allure":"5:09","fc":156},{"km":3,"allure":"5:22","fc":153},{"km":4,"allure":"5:18","fc":158},
                {"km":5,"allure":"5:12","fc":159},{"km":6,"allure":"5:15","fc":156},{"km":7,"allure":"5:15","fc":159},{"km":8,"allure":"5:13","fc":158},
                {"km":9,"allure":"5:05","fc":160},{"km":10,"allure":"5:11","fc":160},{"km":11,"allure":"5:22","fc":157}],
      "revue":_REVUE_FICHIER}
    _S43["3"]["realise"]={"statut":"skipped","reason":"Remplacee par l'allure marathon du 21/10","km":0,"temps":"\u2014","allure":"\u2014","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Non realisee : remplacee par les 11 km a allure marathon du meme jour.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}
    _S43["5"]["realise"]={"statut":"skipped","reason":"Jour de voyage dans le sud, course du soir a la place","km":0,"temps":"\u2014","allure":"\u2014","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Non realisee : arrivee dans le sud le 22/10 (visite de maison l'apres-midi), course du soir a la place. Pas de rattrapage.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}
    _S43["4"]["date"]="2026-10-24"
    _S43["4"]["sport"]="Trail"
    _S43["4"]["titre"]="Trail dans l'Estérel (longue du dimanche avancée au samedi)"
    _S43["4"]["sous"]="Sortie longue remplacée par un trail de 20 km avec ton beau-père dans l'Estérel, samedi 24/10."
    _S43["4"]["metriques"]={"Distance":"20 km","Durée":"2h23","Allure":"7:09/km (trail)","FC":"142 moy / 181 max","RPE":"5","Type":"Trail"}
    _S43["4"]["objectif"]="Durée sur les jambes en endurance, sans chercher d'allure : la fenêtre cardiaque (135-150) et le plaisir passent avant la vitesse."
    _S43["4"]["struct"]=[{"nom":"Corps","txt":"20 km de sentiers dans l'Estérel, 642 m de D+, FC 135-150 en moyenne, pauses libres."}]
    _S43["4"]["segments"]=segs([
      {"nom":"Km 1-8","role":"7:13 à 11:08/km selon la pente, FC 129-151 : montées et sentiers en endurance, pauses photo.","duree":3936,"couleur":"vert","bloc":"\u2014","hauteur":40},
      {"nom":"Km 9-12","role":"5:55 à 6:35/km sur le plat, FC 135-141 : roulant et facile.","duree":1499,"couleur":"vert","bloc":"\u2014","hauteur":40},
      {"nom":"Km 13-20","role":"6:08 à 7:08/km avec +33 à +81 m par km, FC 141-166, pic 181 au km 18 : les montées finales.","duree":3158,"couleur":"orange","bloc":"\u2014","hauteur":75}])
    _S43["4"]["chaussure_realise"]="ASICS Novablast 5 J"
    _S43["4"]["realise"]={"statut":"fait","km":20.03,"temps":"2:23:13","allure":"7:09/km","fc_moy":142,"fc_max":181,"re":158,
      "cadence":84,"elevation_gain":642,"kcal":1655,"rpe_ressenti":5,
      "commentaire":"Prevu : longue 22 km en endurance le dimanche 25/10. Realise le samedi 24/10 : trail de 20,03 km dans l'Esterel avec son beau-pere, 2:23:13 de deplacement (2:49:36 ecoulees, 26 min d'arrets), 7:09/km, FC 142 moy / 181 max, D+ 642 m, RE 158, Novablast 5 J selon Strava. Km 1-12 a FC 137 de moyenne, km 13-20 a 151 (montees finales de +33 a +81 m par km, pic 181 au km 18). Descentes soutenues (jusqu'a -6 % de pente moyenne sur un km). Le RPE est une estimation.",
      "pr":0,"ach":0,"pr_detail":[],
      "splits":[{"km":1,"allure":"7:13","fc":131},{"km":2,"allure":"7:19","fc":131},{"km":3,"allure":"9:13","fc":142},{"km":4,"allure":"7:59","fc":151},{"km":5,"allure":"7:04","fc":137},{"km":6,"allure":"11:08","fc":134},{"km":7,"allure":"7:19","fc":141},{"km":8,"allure":"8:21","fc":129},{"km":9,"allure":"5:55","fc":135},{"km":10,"allure":"6:31","fc":135},{"km":11,"allure":"5:58","fc":138},{"km":12,"allure":"6:35","fc":141},{"km":13,"allure":"6:37","fc":150},{"km":14,"allure":"7:08","fc":145},{"km":15,"allure":"6:45","fc":149},{"km":16,"allure":"6:40","fc":153},{"km":17,"allure":"6:08","fc":141},{"km":18,"allure":"6:32","fc":166},{"km":19,"allure":"6:41","fc":147},{"km":20,"allure":"5:56","fc":155}],
      "revue":_REVUE_FICHIER}
    arr.append({
      "id":6,"date":"2026-10-22","titre":"Sortie au feeling allure marathon (non planifie)","type":"Allure marathon","sport":"Course à pied","opt":False,
      "accent":"#F4561D","fill":40,
      "sous":"Sortie du soir dans le sud (Fréjus - Saint-Raphaël), au feeling, en visant l'allure marathon.",
      "metriques":{"Distance":"10,02 km","Durée":"52 min","Allure":"5:08/km","FC":"158 moy / 172 max","RPE":"6","Type":"Allure marathon"},
      "objectif":"Entretenir la sensation de l'allure marathon pendant le déplacement, sans chercher de charge supplémentaire.",
      "struct":[{"nom":"Corps","txt":"10 km au feeling visant 5:20/km, FC dans la fenêtre 152-163. Arrêts aux feux possibles."}],
      "benefices":"Garde le rythme sans séance structurée pendant un déplacement familial.",
      "vigilance":"Viser 5:20, pas moins : les relances après un arrêt font vite passer sous 5:00.",
      "legende":[{"c":"#CA8A04","l":"Au-dessus du rythme cible"}],
      "coach":[{"titre":"Les relances après les arrêts","texte":"Trois arrêts (3 min 51 s en tout) ont chacun été suivis d'une relance, à 4:45 au km 2 et 4:59 au km 6. L'allure de 5:08 est celle des moments où tu cours ; la moyenne réelle, arrêts compris, est de 5:31."}],
      "segments":segs([{"nom":"Km 1-5","role":"5:17, 4:45, 5:07, 5:10, 5:30/km (moyenne 5:10), FC 150-162 : relances après arrêts, côte au km 5 (pic 172).","duree":1549,"couleur":"orange","bloc":"\u2014","hauteur":70},
                  {"nom":"Km 6-10","role":"4:59, 5:07, 5:17, 5:07, 5:07/km (moyenne 5:07), FC 159-161 : plus régulier, toujours sous la cible.","duree":1543,"couleur":"orange","bloc":"\u2014","hauteur":72}]),
      "chaussure_realise":"ASICS Novablast 5 J",
      "realise":{"statut":"fait","km":10.02,"temps":"51:32","allure":"5:08/km","fc_moy":158,"fc_max":172,"re":120,
        "cadence":87,"elevation_gain":28,"kcal":756,"rpe_ressenti":6,
        "commentaire":"Sortie du soir non planifiee a Frejus - Saint-Raphael (jeudi 22/10, arrivee dans le sud), au feeling en visant l'allure marathon. 10,02 km en 51:32 de deplacement (55:23 ecoulees, 3 min 51 s d'arrets), 5:08/km, FC 158 moy / 172 max (cote du km 5), D+ 28 m, RE 120, Novablast 5 J. Km 1-10 : 5:17, 4:45, 5:07, 5:10, 5:30, 4:59, 5:07, 5:17, 5:07, 5:07. Allure 12 s/km sous la cible. Le RPE est une estimation.",
        "pr":0,"ach":0,"pr_detail":[],
        "splits":[{"km":1,"allure":"5:17","fc":150},{"km":2,"allure":"4:45","fc":161},{"km":3,"allure":"5:07","fc":155},{"km":4,"allure":"5:10","fc":157},{"km":5,"allure":"5:30","fc":162},{"km":6,"allure":"4:59","fc":160},{"km":7,"allure":"5:07","fc":159},{"km":8,"allure":"5:17","fc":161},{"km":9,"allure":"5:07","fc":160},{"km":10,"allure":"5:07","fc":159}],
        "revue":_REVUE_FICHIER}
    })
    arr.append({
      "id":7,"date":"2026-10-25","titre":"Sortie du matin a bonne allure (non planifie)","type":"Allure soutenue","sport":"Course à pied","opt":False,
      "accent":"#F4561D","fill":35,
      "sous":"Sortie du dimanche matin dans le sud (Fréjus), au feeling, le lendemain du trail de l'Estérel.",
      "metriques":{"Distance":"9,70 km","Durée":"50 min","Allure":"5:07/km","FC":"151 moy / 164 max","RPE":"5","Type":"Allure soutenue"},
      "objectif":"Vérifier les jambes après le trail et entretenir la sensation de course, sans charge supplémentaire.",
      "struct":[{"nom":"Corps","txt":"Sortie à la sensation, FC 150 environ, sans objectif d'allure. Pas d'accélération finale."}],
      "benefices":"Confirme que les jambes sont libres après la charge de descente du trail.",
      "vigilance":"Une bonne sensation à deux semaines de la course n'est pas un feu vert pour accélérer : l'allure marathon reste 5:20.",
      "legende":[{"c":"#F4561D","l":"Allure soutenue"},{"c":"#CA8A04","l":"Accélération progressive"}],
      "coach":[{"titre":"Une sortie qui accélère","texte":"De 5:11 sur les premiers km à 4:56 sur le dernier tiers, la FC passe de 137 à 161. Même réflexe que les autres sorties : à Nice, la bonne sensation du km 5 est le moment de rester derrière le meneur."}],
      "segments":segs([{"nom":"Km 1-5","role":"5:11, 5:14, 5:05, 5:08, 5:06/km (moyenne 5:09), FC 137-150, pause d'environ 5 min au km 5.","duree":1544,"couleur":"bleu","bloc":"\u2014","hauteur":60},
                  {"nom":"Km 6-9,7","role":"5:14, 5:10, 5:00, 4:59 puis 4:56/km (moyenne 5:04), FC 152-161, pic 164 : accélération progressive.","duree":1432,"couleur":"orange","bloc":"\u2014","hauteur":72}]),
      "chaussure_realise":"ASICS Novablast 5 J",
      "realise":{"statut":"fait","km":9.70,"temps":"49:36","allure":"5:07/km","fc_moy":151,"fc_max":164,"re":87,
        "cadence":86,"elevation_gain":27,"kcal":698,"rpe_ressenti":5,
        "commentaire":"Sortie non planifiee du dimanche 25/10 au matin a Frejus, le lendemain du trail de l'Esterel, sur bonne sensation. 9,70 km en 49:36 de deplacement (55:01 ecoulees, pause d'environ 5 min au km 5), 5:07/km, FC 151 moy / 164 max, D+ 27 m, RE 87, Novablast 5 J, 5 PR de segments. Progressive : 5:11, 5:14, 5:05, 5:08, 5:06, 5:14, 5:10, 5:00, 4:59 puis 4:56/km sur le dernier 0,7 km (FC 137 -> 161). Allure 13 s/km sous la cible marathon. Le RPE est une estimation.",
        "pr":5,"ach":6,"pr_detail":[],
        "splits":[{"km":1,"allure":"5:11","fc":137},{"km":2,"allure":"5:14","fc":147},{"km":3,"allure":"5:05","fc":149},{"km":4,"allure":"5:08","fc":150},{"km":5,"allure":"5:06","fc":144},{"km":6,"allure":"5:14","fc":152},{"km":7,"allure":"5:10","fc":155},{"km":8,"allure":"5:00","fc":157},{"km":9,"allure":"4:59","fc":158},{"km":10,"allure":"4:56","fc":161}],
        "revue":_REVUE_FICHIER}
    })
    arr.append({
      "id":8,"date":"2026-10-25","titre":"Sortie chill avec Perrine (non planifie)","type":"Récupération active","sport":"Course à pied","opt":False,
      "accent":"#16a34a","fill":12,
      "sous":"Course-marche avec Perrine après la sortie du matin : 2 minutes de course, 1 minute de marche.",
      "metriques":{"Distance":"3,79 km","Durée":"33 min","Allure":"8:37/km","FC":"122 moy / 141 max","RPE":"2","Type":"Récupération"},
      "objectif":"Courir ensemble, sans objectif de performance.",
      "struct":[{"nom":"Corps","txt":"Alternance de 2 minutes de course et 1 minute de marche, au rythme de Perrine."}],
      "benefices":"Récupération active et sortie partagée, sans charge ajoutée.",
      "vigilance":"Aucune : profiter.",
      "legende":[{"c":"#16a34a","l":"Facile"}],
      "coach":[{"titre":"Course-marche","texte":"Phases de course à environ 7:25/km pour une FC de 125 à 133, phases de marche à 115-120. Effort relatif de 9 : aucun coût."}],
      "segments":segs([{"nom":"Course-marche","role":"2 min de course (environ 7:25/km, FC 125-133) puis 1 min de marche, en boucle.","duree":1961,"couleur":"vert","bloc":"\u2014","hauteur":25}]),
      "chaussure_realise":"ASICS Novablast 5 J",
      "realise":{"statut":"fait","km":3.79,"temps":"32:41","allure":"8:37/km","fc_moy":122,"fc_max":141,"re":9,
        "cadence":78,"elevation_gain":14,"kcal":291,"rpe_ressenti":2,
        "commentaire":"Sortie chill avec Perrine le dimanche 25/10 vers 10h, apres la sortie du matin. 3,79 km en 32:41 de deplacement, alternance de 2 min de course (environ 7:25/km, FC 125-133) et 1 min de marche, 8:37/km au total, FC 122 moy / 141 max, D+ 14 m, RE 9, Novablast 5 J. Le RPE est une estimation.",
        "pr":3,"ach":3,"pr_detail":[],
        "splits":[],
        "revue":_REVUE_FICHIER}
    })

for n, arr in list(SEANCES_BY_WEEK.items()):
    if n != "44":
        continue
    _S44 = {str(x["id"]): x for x in arr}
    _S44["1"]["sous"]="Footing vraiment facile, plat ou en bosses douces (100-200 m de D+ au plus)."
    _S44["1"]["metriques"]=dict(_S44["1"]["metriques"], FC="135-145")
    _S44["1"]["vigilance"]="FC 145 maximum, 6:10/km ou plus lent, ceinture cardiaque si possible. Si les cuisses tirent après le trail du 24/10 : terrain plat, ou repos. Montees à l'effort (marche autorisee), descentes relachees, aucune descente raide."
    _S44["2"]["sous"]="Derniere seance d'intensite avant Nice : on garde le jus, le volume baisse."
    _S44["2"]["struct"]=[{"nom":"Échauffement","txt":"20 min facile + 3 lignes droites."},
      {"nom":"Corps","txt":"3 × 6 min à seuil 30 (4:40-4:45/km, pas plus vite), récup 3 min footing très lent entre les blocs. Arrêt après 2 blocs si le 3e est dur."},
      {"nom":"Retour","txt":"10 min souple."}]
    _S44["2"]["vigilance"]="Séance conditionnelle : seulement si les jambes sont libres lundi, sinon footing facile. Le dernier bloc a la même allure que le premier. 11 km au total au maximum. Ceinture cardiaque : FC 172-180 en repere, pas en cible. Aucune autre séance dure avant Nice."
    _S44["3"]["metriques"]=dict(_S44["3"]["metriques"], FC="135-145")
    _S44["3"]["vigilance"]="Lignes droites relâchées, jamais en sprint. Si le trail du 24/10 laisse des courbatures : terrain plat. D+ léger toléré (150 m au plus) jusqu'à ce mercredi ; plus aucune descente soutenue ensuite."
    _S44["4"]["vigilance"]=_S44["4"]["vigilance"]+" Les 4 derniers km : 5:17 à 5:23/km, pas plus vite. La bonne sensation du km 5 se retrouve a Nice : rester derrière le meneur 3h45. Terrain plat, aucun dénivelé."
    _S44["1"]["realise"]={"statut":"skipped","reason":"Aucune sortie enregistrée sur Strava le 26/10","km":0,"temps":"\u2014","allure":"\u2014","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,
      "commentaire":"Non réalisée : aucune activité Strava le lundi 26/10. Pas de rattrapage.",
      "pr":0,"ach":0,"pr_detail":[],
      "revue":_REVUE_FICHIER}
    _S44["2"]["titre"]="Footing facile (seuil remplacé)"
    _S44["2"]["sous"]="Séance conditionnelle : le seuil 3×6 min a laissé place à un footing facile de 10 km sur les quais."
    _S44["2"]["chaussure_realise"]="HOKA Clifton 10"
    _S44["2"]["realise"]={"statut":"fait","decouplage":{"pct":0.85,"bpm":-1.1,"fen_min":45,"temp":18,"attendu":6,"p1":"5:54/km","fc1":146,"p2":"5:54/km","fc2":145,"qualite":"incertain","algo":"decoup-v1"},"temp":18,"km":10.04,"temps":"58:30","allure":"5:50/km","fc_moy":146,"fc_max":165,"re":86,
      "cadence":86,"elevation_gain":31,"kcal":754,
      "commentaire":"Prevu : seuil 3x6 min si les jambes etaient libres, sinon footing facile. Realise : footing de 10,04 km sur les quais (Rhone, Confluence, Saone) en 58:30 de deplacement, 5:50/km, FC 146 moy / 165 max, D+ 31 m, 18 °C. Km 1-8 entre 5:40 et 6:06 (FC 142-149), km 9 a 5:31 (FC 151, pic 165 sur le pont de la Guillotiere), km 10 a 5:40 (FC 143).",
      "pr":0,"ach":0,"pr_detail":[],
      "splits":[{"km":1,"allure":"5:40","fc":142},{"km":2,"allure":"5:47","fc":148},{"km":3,"allure":"5:59","fc":149},{"km":4,"allure":"5:55","fc":144},{"km":5,"allure":"6:00","fc":145},{"km":6,"allure":"5:50","fc":146},{"km":7,"allure":"5:49","fc":146},{"km":8,"allure":"6:06","fc":144},{"km":9,"allure":"5:31","fc":151},{"km":10,"allure":"5:40","fc":143}],
      "revue":_REVUE_FICHIER}






_charge_logs(SEANCES_BY_WEEK)
_charge_revues_semaines(SEMAINES)

PHASES=[
 {"id":'reprise',"nom":'Reprise',"c":GREEN,"sem":'S24 – S25',"role":"Digérer La Circaète puis relancer en douceur en corrigeant la zone grise."},
 {"id":'general',"nom":'Développement général & aérobie',"c":BLUE,"sem":'S26 – S31',"role":"Volume, polarisation, côtes en pyramide (force/économie), seuil, et benchmark 10 km pour recaler les allures."},
 {"id":'seuil',"nom":'Seuil & spécifique (pré-USA)',"c":VIOLET,"sem":'S32 – S35',"role":"Front-loader le seuil et l'allure marathon avant le voyage."},
 {"id":'usa',"nom":'Maintien — Road trip USA',"c":'#A1A1AA',"sem":'S36 – S39',"role":"Deload bien placé : courir quand possible, randos = temps de pied."},
 {"id":'marathon',"nom":'Bloc spécifique marathon',"c":ORANGE,"sem":'S40 – S43',"role":"Ré-entrée progressive, une grosse séance spécifique par semaine, pic à 88 km avec la séance reine."},
 {"id":'affutage',"nom":'Affûtage marathon',"c":YELLOW,"sem":'S44 – S45',"role":"Décharge progressive (Bosquet) : volume en baisse, intensité courte maintenue, fraîcheur pour le 8 nov."},
 {"id":'transition',"nom":'Transition & bascule trail',"c":TEAL,"sem":'S46 – S47',"role":"Récup marathon progressive puis réveil des jambes de trail."},
 {"id":'saintexpress',"nom":'SaintExpress 45 km',"c":RED,"sem":'S48',"role":"Objectif B sur les acquis : nocturne, hivernal, au plaisir."},
 {"id":'regen',"nom":'Régénération fin de saison',"c":'#A1A1AA',"sem":'S49 – S53',"role":"Décompression, course libre, entretien de la base, cap vers 2027."},
]
COUL={p["id"]:p["c"] for p in PHASES}
# ═══════════════════════════════════════════════════════════════════
# GEAR — kilometrage du parc chaussures
# ═══════════════════════════════════════════════════════════════════
# ATTENTION, LIMITE CONNUE : ces valeurs sont RECOPIEES DE STRAVA a la
# main. Contrairement a MONTHLY ou ACWR_DATA, elles ne peuvent PAS etre
# recalculees depuis SEANCES_BY_WEEK : les chaussures sont aussi portees
# sur des activites hors perimetre course (randonnees, velo) qui, elles,
# comptent bien dans le total Strava. Exemple : la Cascadia 19 a pris
# 18 km sur les randonnees du Cantal des 25 et 26/08, invisibles ici.
#
# CONSEQUENCE : ce bloc DERIVE mecaniquement et doit etre resynchronise
# depuis Strava. Derive constatee le 28/08/2026 : Novablast 5 V a -31 km,
# Cascadia 19 a -18 km, Clifton 10 a -7 km.
# Le controle E2 d'audit_data confronte desormais ces valeurs au parc
# Strava et alerte des que l'ecart depasse 5 km.
# Derniere resynchronisation : 28/08/2026.
GEAR=[
  {"marque":"HOKA","modele":"Clifton 10","km":1284},
  {"marque":"ASICS","modele":"Novablast 5 J","km":887},
  {"marque":"ASICS","modele":"Novablast 5 V","km":202},
  {"marque":"ASICS","modele":"Gel Pulse 16","km":240},
  {"marque":"Brooks","modele":"Cascadia 19","km":259},
  {"marque":"ASICS","modele":"Magic Speed 4","km":93},
]
RACES=[{"nom":"Run In Lyon — Semi","date":"2026-10-04","dossier":"runinlyon"},{"nom":"Marathon de Nice","date":"2026-11-08","dossier":"nice"},{"nom":"SaintExpress","date":"2026-11-28","dossier":"saintexpress"}]

# ===== DOSSIERS DE COURSE (modale au clic sur le badge) =====
DOSSIERS={
 "nice":{
  "nom":"Marathon des Alpes-Maritimes Nice-Cannes",
  "soustitre":"Promenade des Anglais, Nice → Boulevard de la Croisette, Cannes",
  "date":"Dimanche 8 novembre 2026",
  "depart":"Départ 8 h 00 · Promenade des Anglais (Nice) · Sas 3h45 disponible",
  "format":"42,195 km · Point-à-point · Label FFA & World Athletics · ~15 000 coureurs",
  "accent":"#CA8A04",
  "stats":[["42,195","km"],["+70","D+ (m)"],["35","alt. max (m)"],["3 h 45","objectif"],["5:20/km","allure cible"]],
  "intro":"Le 2ᵉ plus grand marathon de France après Paris. <strong>42,195 km quasi plats le long de la Méditerranée</strong>, de la Promenade des Anglais à la Croisette — vue mer permanente, palmiers, soleil de novembre. Route intégralement bitumée, D+ de seulement ~70 m : pas de dénivelé à gérer, pas de marche prévue. Tout l'enjeu est <strong>la gestion d'allure sur la durée</strong>. C'est ton Objectif A de la saison.",
  "phrase":"3 h 45, soit <strong>5 min 20 / km</strong> du départ à l'arrivée. Le lièvre 3h45 est disponible — reste derrière lui jusqu'au km 35-36, puis décide selon tes jambes. Le seul piège : partir trop vite dans l'euphorie du départ.",
  "profil":"Profil réel GPX officiel (marathon06.com). Course quasi plate au niveau de la mer. Deux légères ondulations : une petite bosse vers le km 15-18 (Cagnes / Villeneuve-Loubet, ~12 m) et <strong>la seule vraie bosse du parcours vers le km 25-28 (Antibes, ~35 m)</strong>. Cette montée est modeste mais peut surprendre à mi-course si tu n'es pas calé à l'effort. Retour au niveau de la mer à partir de Juan-les-Pins.",
  "profil_dist":42.195,
  "profil_pts":[11,8,9,10,14,8,9,9,9,5,6,11,11,9,5,4,4,6,7,7,3,2,5,5,4,5,4,6,12,12,10,7,4,10,7,10,11,6,4,5,3,4,3,3,4,6,3,5,5,4,3,8,15,13,7,12,6,6,6,7,7,9,9,16,7,10,7,28,33,28,19,11,6,5,4,4,5,5,5,12,8,8,10,5,2,3,4,5,3,13,16,15,22,17,19,15,14,6,5,5,8,7,3,7,4,10,7,6,4],
  "segments":[
    {"t":"1 · Nice — Saint-Laurent","km":"km 0 → 8","faire":"Départ Promenade des Anglais. Jambes fraîches, foule, adrénaline : <strong>le piège du marathon</strong>. Cible : 5:25/km au moins sur les 5 premiers km. Place-toi derrière le lièvre 3h45 dès le sas : c'est lui qui fixe l'allure, pas la foule."},
    {"t":"2 · Cagnes — Villeneuve-Loubet","km":"km 8 → 18","faire":"La Marina Baie des Anges vers le km 15. Légère ondulation, rien de méchant. <strong>Mi-course approche : gère à l'effort</strong>, pas au chrono. Si tu passes la demi à moins de 1h52, tu risques de payer après le km 30."},
    {"t":"3 · Antibes — Juan-les-Pins","km":"km 20 → 30","faire":"La seule vraie bosse (km 25-28, ~35 m) — prends-la sans accélérer. Autour du km 20-21 tu franchis la demi-distance : moment de recalibrer. <strong>Le seuil critique du « mur » est entre le km 30 et 35</strong> — si tu arrives là fatigué, c'est que tu es parti trop vite."},
    {"t":"4 · Golfe-Juan → Cannes","km":"km 30 → 42","faire":"C'est ici que la course se joue. Reste avec le lièvre jusqu'au km 35-36, puis décide : si les jambes répondent, accélère et double les gens qui ont cramé. Si tu souffres : raccourcis légèrement la foulée, cadence haute, gel, et accroche-toi. La Croisette arrive — les marches rouges du Festival, c'est l'arrivée."}],
  "plan":[
    {"n":"1","tag":"CONSERVATEUR","c":"#CA8A04","titre":"Sortie de Nice — freiner l'ego","txt":"8h00 sur la Promenade des Anglais avec 15 000 coureurs. Les km 1-5 sont les plus dangereux du marathon : jambes fraîches, euphorie, public, faux-plats. Cible <strong>5:25 / km</strong> minimum sur les 5 premiers. Si tu passes le km 5 sous 26:30, tu es trop rapide.","fuel":"Gel dès 40 min de course (km 8 environ) sans attendre la faim. Ravito km 5 : eau."},
    {"n":"2","tag":"GÉRER","c":"#C2410C","titre":"La longue ligne droite côtière","txt":"Km 8 à 20 : tenir le 5:20/km sans forcer. La côte Méditerranée est magnifique, ça peut aller vite — surveille ton allure. Passage de la demi vers 1h52 à 1h53 : si tu es en avance, lève le pied. Marathon = compétition contre soi-même, pas contre les coureurs autour.","fuel":"Gel km 16 environ. Ravitos km 10, 15, 20 : eau + boisson sucrée si dispo. Commence l'électrolyte."},
    {"n":"3","tag":"VIGILANCE","c":"#dc2626","titre":"Antibes & le mur (km 25-35)","txt":"<strong>La section décisive.</strong> La bosse d'Antibes (km 25-28, max 35 m) peut faire accélérer le cœur si tu n'es pas attentif — régule. Puis km 30 : c'est là que les glucides s'épuisent et que les jambes commencent à parler. Ton mental et ton carburant doivent tenir. Cadence haute, foulée courte.","fuel":"Gel km 24 et gel km 32 — <strong>celui du km 32 est le plus important du marathon</strong>. Le caféiné ici si tu en as un."},
    {"n":"4","tag":"POUSSER","c":"#CA8A04","titre":"La Croisette — vider le réservoir","txt":"Km 35-42 : si tu as bien géré, tu doubles du monde sur les derniers km. La Croisette de Cannes approche avec les marches rouges du Festival et le public. Laisse parler les émotions, accélère si tes jambes suivent. <strong>3h45 c'est à ta portée : ne lâche rien.</strong>","fuel":"Dernier gel km 37-38 si tu en as encore. Sinon eau seule pour les 5 derniers km."}],
  "nutrition":{
   "avant":"<strong>J-3 à J-1 :</strong> ↑ glucides légèrement (+ 20-30 %), 1 comprimé TA dans 500 ml d'eau/jour. <strong>Veille :</strong> dîner pâtes/riz, coucher tôt. <strong>Matin de course</strong> (réveil ~5h, départ 8h) : 2 comprimés TA dans 500 ml d'eau dès le lever — priorité absolue. Petit-dej 3h avant : flocons d'avoine + banane + miel + café. Répète-le avant la longue du 1er novembre (le 15/10 : banane, protéines et café 1h30 avant). <strong>15-20 min avant le départ :</strong> 1 gel non-caféiné (amorce le moteur glycolytique).",
   "intro":"Marathon = moteur glycolytique sur 3h45. L'apport glucidique doit être continu et anticipé — sans gel régulier, le mur du km 30 est inévitable. Les <strong>comprimés TA</strong> (350 mg Na/cpr) couvrent les électrolytes en pré-course, des <strong>gels non-caféinés</strong> assurent le débit de base (3 à acheter, ex. Aptonia Decathlon ~1 €/pièce), les <strong>Nduranz caféinés</strong> interviennent uniquement sur les deux moments critiques. <strong>Pas de BCAA dans ce plan.</strong>",
   "items":[
     ["TA Energy Electrolytes Tropical","350 mg Na · 80 mg K · 52 mg Mg / cpr","PRÉ-COURSE — 2 cpr dans 500 ml dès le réveil. 1 cpr en poche → à dissoudre dans un gobelet ravito km 20-25."],
     ["Gel non-caféiné (Aptonia ou équiv.)","~25-45 g glucides · 0 mg caféine","BASE — km 8, km 16, km 24 : débit régulier anti-mur (+ 1 avant le départ)"],
     ["Nduranz NRGY 45 — Cherry","45 g glucides · 65 mg caféine","ARME 1 — km 32 : le gel le plus important du marathon (anti-mur, pic caféine en 35 min)"],
     ["Nduranz NRGY 45 — Coffee Amarena","45 g glucides · 130 mg caféine","ARME 2 — km 38 : finale Croisette, vide le réservoir"]],
   "note":"Cible : <strong>50-60 g glucides/h</strong>. La boisson STC Nutrition des ravitos (~30-40 g glucides/500 ml) complète les gels — bois systématiquement à chaque table. Caféine total en course : 195 mg — raisonnable sur 3h45. Ne jamais forcer un gel si l'estomac est tendu : eau seule et reprendre au prochain ravito. <strong>Test du 15/10 (30 km) :</strong> gels à 45 min, 1h30 et 2h15, le 3e plus difficile à avaler ; environ 1,5 L bu, sans doute un peu juste. Pour Nice : prends chaque gel avec de l'eau à un ravito, bois à chaque table, et teste les Nduranz caféinés sur la longue du 1er novembre.",
   "apres":"<strong>Dans les 15 min :</strong> 1 comprimé TA dans 500 ml d'eau (priorité). <strong>Dans l'heure :</strong> repas protéiné complet (protéines + glucides). <strong>Le soir :</strong> vigilance crampes nocturnes → 1 dernier comprimé TA dans l'eau au coucher. Le dossard TER est valable toute la journée pour rentrer à Nice depuis Cannes."},
  "hydra":"<strong>Électrolytes pré-course :</strong> 2 comprimés TA dans 500 ml dès le réveil (5h). La course est en novembre (~12-16°C) : la soif est modérée mais les ravitos tous les 5 km sont obligatoires — ne saute aucune table. Tu peux glisser 1 comprimé TA dans ta poche et le dissoudre dans un gobelet d'eau à un ravito (km 20-25). Post-course : 1 comprimé TA dans 500 ml immédiatement à l'arrivée.",
  "zones":[
   ["Zone marathon","152 – 163","Ta FC mesurée à allure marathon : 159 à 5:18/km le 06/10, 161 à 5:11/km sur la longue du 15/10. Au-dessus de 163 dans les 15 premiers km : tu pars trop vite."],
   ["Dérive normale","163 – 167","Après le km 30, la FC monte même à allure constante (165 sur les 5 derniers km de la longue du 15/10). Normal : maintiens l'effort, pas la FC."],
   ["Danger","&gt; 167","Au-dessus de 167 (ton seuil) avant le km 30 : freine. Au-delà du km 35 avec le mur enclenché : encaisse et maintiens."]],
  "terrain":"Route bitumée 100%, large et sécurisée, traversant 7 communes. <strong>Chaussures :</strong> les Novablast 5 V, rodées sur la longue de 30 km du 15/10 (202 km au compteur) : porte-les encore sur la longue du 1er novembre, puis garde-les pour le jour J. Pas les Clifton 10, à 1 274 km : leur mousse est en fin de vie. Oublie les Cascadia : route uniquement. <strong>Tenue :</strong> novembre en Côte d'Azur, départ 8h00 → 10-14°C. Bras longs au départ (ou brassière + bras jetables), tu enlèveras au km 5-10. <strong>Vent :</strong> côtier donc potentiellement présent. Si vent de face, colle à un groupe.",
  "pratique":[
   ["🚉 Logistique retour","Ton dossard = billet TER Nice-Cannes valable le jour J. Prévois où tu récupères tes affaires (service transfert de sacs disponible)."],
   ["👟 Lièvre 3h45","Cherche le groupe 3h45 dans ton sas. Reste avec eux jusqu'au km 35-36 — c'est ton GPS vivant — puis décide selon tes jambes."],
   ["🏅 Dossard","Retrait au Running Expo, Nice, les jours précédant la course. Aucun dossard le matin du départ."],
   ["🌡️ Météo novembre","Typiquement 10-16°C en matinée sur Nice. Conditions idéales pour un marathon — profite-en."],
   ["📸 Photos","Service photo officiel sur le parcours. Souris au km 25 — tu seras encore frais."]],
  "erreurs":[
   "Partir trop vite — c'est l'erreur n°1 sur ce parcours. Tout le monde part trop vite sur les 5 premiers km.",
   "Passer la demi sous 1h50 : si tu es à 1h48 à mi-course, tu vas payer cher entre le km 30 et 35.",
   "Sauter des gels ou des ravitos en se sentant bien — c'est justement quand tu te sens bien qu'il faut manger.",
   "Courir vite sur la bosse d'Antibes (km 25-28) : c'est une montée douce, pas une occasion de déborder.",
   "Attendre la sensation de soif pour boire : bois à chaque ravito, même une gorgée.",
   "Trop se fier à la FC en début de course : l'adrénaline du départ fait monter la FC même au repos. Pilote à l'allure."],
  "sources":"Profil GPX officiel MAM 2026 (marathon06.com/2026/dl/MAM2026_parcours.gpx). D+ officiel ~70 m. Infos ravitaillements et lièvres : marathon06.com, finishers.com. Zones FC recalées le 27/10 sur ta FC mesurée à allure marathon (06/10 et 15/10). Météo : moyennes historiques Nice novembre (Météo-France)."},
 "saintexpress":{
  "nom":"SaintExpress 45 km",
  "soustitre":"Sainte-Catherine (757 m) → Lyon · Halle Tony Garnier · Monts du Lyonnais",
  "date":"Samedi 28 novembre 2026 — départ 23 h 00",
  "depart":"Départ nocturne 23 h 00 · Sainte-Catherine (757 m) · 4 000 coureurs",
  "format":"45 km · 900 m D+ · 1 400 m D− · SaintéLyon depuis 2010 · maratrail nocturne",
  "accent":"#F4561D",
  "stats":[["45","km"],["+900","D+ (m)"],["−1 400","D− (m)"],["757","alt. départ (m)"],["6 h 00–7 h","cible réaliste"]],
  "intro":"Course emblématique de la SaintéLyon, depuis 2010. <strong>45 km de nuit complète</strong> dans les Monts du Lyonnais, de Sainte-Catherine à la Halle Tony Garnier de Lyon. Ce qui définit la SaintExpress : plus de descentes que de montées (1 400 m de D− pour 900 m de D+), un terrain <strong>60 % chemins / 40 % bitume</strong>, et une nuit de fin novembre. <strong>Bonne nouvelle : tu connais déjà les 18 derniers km.</strong> Ton relais SaintéLyon (Soucieu → Lyon) te donne une base de terrain réelle sur la seconde moitié — les aqueducs, les faubourgs, la Halle Tony Garnier. L'inconnu se concentre sur les <strong>27 premiers km</strong> (Sainte-Catherine → Soucieu), qui sont aussi les plus techniques.",
  "phrase":"<strong>Course plaisir, objectif B — cible 6h00 à 7h00.</strong> Référence terrain réelle : ton relais Soucieu → Lyon en 2h27 (6:28/km, 22 km, 459 m D+). Sur la SaintExpress complète, après 27 km inconnus de nuit, compte 7:30-8:00/km sur cette même section. Pas de chrono à aller chercher — tu arrives 20 jours après Nice. L'objectif : finir debout, bien équipé.",
  "profil":"Surprenant : le D+ ne tombe pas que dans la première moitié. Ton relais Soucieu → Lyon avait déjà <strong>459 m de D+</strong> sur 22 km — les aqueducs et le terrain roulant de Chaponost y contribuent largement. Les 900 m de D+ de la SaintExpress se répartissent donc presque équitablement entre les deux sections. La première section (Sainte-Catherine → Soucieu, ~km 0-27) est <strong>la plus technique</strong> : pistes forestières pentues, monotraces, descentes raides. Après Soucieu, tu bascules sur terrain connu mais avec déjà 27 km dans les jambes.",
  "profil_dist":45.0,
  "profil_pts":[757,783,810,824,802,778,748,720,695,718,742,724,698,720,695,670,688,712,685,660,678,695,670,648,625,640,658,635,610,628,614,598,575,590,610,598,575,558,542,560,578,555,535,518,498,480,462,478,492,470,452,435,420,408,392,375,362,378,365,350,362,348,335,320,308,322,335,318,302,288,275,262,250,238,248,260,270,255,240,228,215,205,215,228,242,258,272,280,268,252,235,218,200,188,180,175],
  "segments":[
    {"t":"1 · Sainte-Catherine → Saint-Genou","km":"km 0 → 14","faire":"<strong>Terrain inconnu</strong> — la section la plus technique et accidentée du parcours. Départ nocturne sur pistes forestières pentues, monotraces. Ne jamais forcer : gérer la frontale, les appuis, la descente de nuit. FC ≤ 160 sur les montées. Ton seul repère ici, c'est l'effort."},
    {"t":"2 · Saint-Genou → Soucieu-en-Jarrest","km":"km 14 → 27","faire":"<strong>Terrain inconnu</strong> — section intermédiaire encore technique, descentes importantes. Les quads accumulent. Foulée courte, cadence haute. À l'arrivée à Soucieu : <strong>tu entres en terrain connu.</strong> Mentalement, c'est un point de bascule fort."},
    {"t":"3 · Soucieu → Chaponost","km":"km 27 → 38","faire":"<strong>Terrain connu</strong> — tu es déjà passé par là sur ton relais. Le profil devient plus roulant. Tu sais ce qui t'attend, tu peux gérer à l'effort plutôt qu'à la découverte. Creux circadien probable vers 2h du matin : caféine Cherry ici."},
    {"t":"4 · Aqueducs → Lyon","km":"km 38 → 45","faire":"<strong>Terrain connu</strong> — tu connais la montée des aqueducs de Beaunant, tu sais qu'elle est dure sur jambes fatiguées. Marche-la franchement. Ensuite la descente finale, les faubourgs, la Halle Tony Garnier : c'est ton terrain, tu rentres à la maison. Vide le réservoir."}],
  "plan":[
    {"n":"1","tag":"TERRAIN INCONNU","c":"#F4561D","titre":"km 0-27 — découverte et prudence","txt":"Les 27 premiers km sont du terrain inédit pour toi. Pas de repère, pas d'anticipation possible — tu gères à l'effort, à la sensation et à la frontale. <strong>Plus conservateur que d'habitude</strong>, surtout sur les descentes techniques de nuit. L'objectif est d'arriver à Soucieu avec des jambes.","fuel":"Gel non-caféiné à 20 min avant départ. Flasques TA. Gel km 7 et km 14 (ravito Saint-Genou)."},
    {"n":"2","tag":"TERRAIN CONNU","c":"#16a34a","titre":"km 27-45 — tu rentres à la maison","txt":"À Soucieu, tu bascules sur ton terrain de relais. <strong>Tu sais ce qui t'attend</strong> : le rythme, les aqueducs, les faubourgs. C'est un avantage mental énorme à 2h du matin. Pas d'accélération brutale, mais tu peux relâcher l'hyper-vigilance et gérer à l'instinct.","fuel":"Nduranz Cherry (65 mg) au départ de Soucieu (~km 27). Coffee Amarena (130 mg) avant les aqueducs (~km 38)."},
    {"n":"3","tag":"QUADS FIRST","c":"#dc2626","titre":"Préserver les quads — 1400 m de D−","txt":"Course de descente avant tout. <strong>1400 m de descente sur terrain technique de nuit</strong> : foulée courte, appuis rapides, regard 3-4 m devant la frontale. La différence entre bien et mal gérer les descentes, c'est 1h sur le chrono final.","fuel":"Hydratation régulière. Ne jamais attendre la soif dans le froid."},
    {"n":"4","tag":"VIGILANCE NUIT","c":"#C2410C","titre":"Creux circadien 1h-3h du matin","txt":"Entre 1h et 3h du matin, même toi qui as déjà couru de nuit, la vigilance baisse. <strong>C'est là que les chutes arrivent.</strong> La caféine Cherry à Soucieu (~km 27, vers 1h30-2h du matin selon ton allure) est calculée pour couvrir exactement ce creux.","fuel":"Nduranz Cherry (65 mg) à Soucieu → pic en 30-35 min = plein creux nocturne couvert."}],
  "nutrition":{
   "avant":"<strong>Après-midi (15h-16h) :</strong> repas glucidique léger (pâtes, riz, facile à digérer). Nap de 1h-2h si possible — c'est du capital pour la nuit. <strong>Dîner/pre-race (19h30-20h) :</strong> repas normal mais pas lourd — 3h avant le départ, c'est le timing parfait. 1 comprimé TA dans 500 ml d'eau. <strong>22h00-22h30 :</strong> encas léger (banane, barre de céréales, tartine) + café si tu tolères. Gilet HDV5 : 2 comprimés TA dans les flasques (~600 ml). <strong>22h40 :</strong> 1 gel non-caféiné (amorce).",
   "intro":"Même architecture qu'à la Déraille — TA pour les électrolytes, gels non-caféinés pour le débit de base, Nduranz caféinés pour les moments critiques — mais sur <strong>5h30-7h de nuit</strong>, la caféine joue un rôle supplémentaire : la <strong>vigilance nocturne</strong>. C'est elle qui t'empêche de trébucher sur les appuis de 2h du matin.",
   "items":[
     ["TA Energy Electrolytes Tropical","350 mg Na · 80 mg K · 52 mg Mg / cpr","ÉLECTROLYTES — 2 cpr dans les flasques départ + 1 cpr à chaque ravito (TA est partenaire de la SaintéLyon !)"],
     ["Gel non-caféiné (Aptonia ou équiv.)","~25-45 g glucides · 0 mg caféine","BASE — 1 avant le départ + 1 tous les 60-70 min en première moitié (km 7, km 14, km 21)"],
     ["Nduranz NRGY 45 — Cherry","45 g glucides · 65 mg caféine","VEILLE NOCTURNE — vers 1h du matin (creux circadien, km ~30)"],
     ["Nduranz NRGY 45 — Coffee Amarena","45 g glucides · 130 mg caféine","FINALE — km 38-40 (avant les aqueducs) · arrivée à Lyon"]],
   "note":"Cible : <strong>40-50 g glucides/h</strong> (intensité moindre que la Déraille). Sur 5h30-7h, tu consommes 5-7 gels. <strong>Checkpoint critique :</strong> les ravitos TA (Saint-Genou ~km 14, Soucieu ~km 27) servent aussi de la boisson chaude — prends-en systématiquement, c'est chaud et ça recharge l'élan mental. Le gel Coffee Amarena avant les aqueducs (km 38) = pic caféine en pleine montée finale.",
   "apres":"<strong>À l'arrivée Lyon (entre 4h30 et 6h du matin) :</strong> 1 comprimé TA dans 500 ml d'eau. Repas d'arrivée proposé par l'organisation (soupe, sandwiches). <strong>Le lendemain :</strong> récupération prioritaire — tu arrives 20 jours après Nice, les jambes auront encaissé deux gros efforts en moins d'un mois. 48-72h de repos complet, pas de footing récup avant 4-5 jours."},
  "hydra":"<strong>Froid de novembre</strong> : la sensation de soif sera atténuée par le froid — c'est un piège. Boire à chaque ravito même sans soif. 2 comprimés TA dans les flasques au départ (~600 ml). Recharger systématiquement à chaque ravito avec 1 comprimé TA supplémentaire. Attention au gel des flasques si T° < 2°C — garde-les sous ta veste ou dans les poches internes du gilet. TA Energy est partenaire officiel de la SaintéLyon : leurs boissons seront probablement proposées aux ravitos.",
  "zones":[
   ["Confort nocturne","130 – 152","L'allure de référence pour la majeure partie du parcours. Sur terrain technique de nuit, cette zone est ta zone de survie."],
   ["Montées","152 – 162","FC plafond 160 sur les montées — si tu dépasses, marche. La fatigue nocturne augmente la FC à intensité équivalente."],
   ["Danger","&gt; 162","Avant km 30 de nuit = risque d'explosion. Passé les aqueducs sur les derniers km, tu peux déborder si les jambes suivent."]],
  "terrain":"<strong>60 % chemins, 40 % bitume</strong> — le mix change plusieurs fois dans la course. Les premiers 27 km sont les plus techniques : single trails forestiers, descentes raides, possibles racines et cailloux glissants. Après Soucieu : plus de routes et chemins larges. <strong>Chaussures :</strong> une paire polyvalente trail-route est recommandée (ni trop trail pur ni route pur). Tes Cascadia 19 peuvent convenir mais s'useront vite sur le bitume — à toi de voir. <strong>Verglas :</strong> si T° < 0°C, des microspikes légers peuvent être utiles sur la première section.",
  "pratique":[
   ["🚌 Navette","Navettes officielles organisées vers Sainte-Catherine (depuis Lyon). Retrait des dossards : Halle Tony Garnier, vendredi 27/samedi 28 novembre."],
   ["🔦 Frontale","Obligatoire. Prévoir <strong>batterie pleine + batteries de rechange</strong> (ou deuxième frontale). La nuit commence à 23h et tu arrives au lever du jour."],
   ["🧥 Froid","Gants obligatoires, base-layer thermique, softshell ou coupe-vent. En novembre dans les Monts du Lyonnais, vise 0-8°C. Couverture de survie obligatoire."],
   ["🎒 Matériel obligatoire","Frontale, couverture de survie, sifflet, réserve alimentaire, téléphone. Vérifie le règlement officiel."],
   ["🏁 Arrivée","Halle Tony Garnier, Lyon. Repas d'arrivée pour tous les finishers. Prévoir quelqu'un pour t'attendre ou de quoi rentrer entre 4h et 6h du matin."]],
  "erreurs":[
   "Partir trop vite dans l'euphorie du départ — l'énergie du soir est trompeuse, et les 27 premiers km sont inconnus.",
   "Sous-estimer les descentes de nuit sur terrain inconnu (km 0-27) : même avec une bonne frontale, les appuis sont moins sûrs qu'en terrain connu.",
   "Surestimer ses jambes à Soucieu parce qu'on est en terrain connu — 27 km de descente nocturne t'auront quand même bien entamé les quads.",
   "Vouloir performer 20 jours après Nice — cette course se court en plaisir, pas en chrono.",
   "Sauter les ravitos sans boire parce qu'on n'a pas soif : le froid masque la soif, la déshydratation arrive quand même.",
   "Sous-estimer le froid : même à 5°C en novembre, 6h de course de nuit en sueur ça refroidit vite à chaque arrêt."],
  "sources":"Données : saintelyon.com (45 km, D+ 900 m, D- 1400 m, départ 23h00 Sainte-Catherine). Profil représentatif construit d'après l'architecture connue du tracé (GPX 2026 à venir sur le site officiel). Description du terrain : pacing-trail.fr, thepostrace.com. TA Energy est partenaire officiel de la SaintéLyon — leur boisson sera disponible aux ravitos."},
 "deraille":{
  "nom":"Le Trail qui Déraille",
  "soustitre":"Lac des Sapins — Cublize (69), Beaujolais Vert",
  "date":"Dimanche 5 juillet 2026",
  "depart":"Départ ≈ 8 h 30 – 9 h 00 · Salle des sports de Cublize",
  "format":"24 km solo · 5ᵉ manche du Trail Tour Beaujolais · organisé par Y’A.C.A. Courir",
  "accent":"#F4561D",
  "stats":[["24,06","km"],["+901","D+ (m)"],["−901","D− (m)"],["897","sommet (m)"],["2 h 30–3 h","cible plaisir"]],
  "intro":"Boucle dans le Beaujolais Vert autour du Lac des Sapins. Sur le papier « roulant », mais le profil est plus sérieux qu'il n'y paraît : <strong>901 m de D+ concentrés en deux montées</strong>, départ et arrivée au lac (447 m), point culminant à 897 m. Single en forêt, quelques passages techniques (cailloux, racines) entre sapins et genêts. Rien d'alpin comme La Circaète, mais une vraie gestion d'effort à tenir.",
  "phrase":"Course <strong>plaisir</strong>, et surtout ton laboratoire nutrition. Le seul vrai objectif : <strong>électrolytes dès le départ</strong> et zéro trou de carburant sur 2 h 30. La leçon de La Circaète, appliquée — pas un chrono à aller chercher.",
  "profil":"Tout le D+ tombe en deux temps. <strong>Montée 1 (km 2 → 8)</strong> : la grosse ascension d'entrée, +~360 m jusqu'à ~810 m. <strong>Plateau ondulé (km 8 → 12)</strong> avec un creux net vers le km 11-12. <strong>Montée 2 (km 12 → 16)</strong> : remontée jusqu'au sommet à 897 m — le crux, sur jambes déjà entamées. Puis <strong>longue descente finale (km 16 → 22)</strong>, ~−415 m roulante, et retour au lac. La faute classique : cramer la Montée 1 et exploser sur la remontée du km 13.",
  "profil_dist":24.06,
  "profil_pts":[447,449,449,449,499,519,534,544,506,530,566,595,617,614,660,688,713,740,765,758,734,727,747,772,789,837,836,786,777,777,796,798,797,841,819,802,776,772,776,777,723,697,772,818,833,864,893,878,845,843,843,870,865,861,834,780,725,716,725,696,663,637,613,584,578,556,562,544,525,523,507,474,461,441,446,449,450,448,440,442,447,447],
  "segments":[
    {"t":"1 · Départ &amp; Montée 1","km":"km 0 → 8","faire":"Faux-plat de départ au lac (km 0-2), puis LA grosse montée : ~+360 m jusqu'au km 8. Marche active sur les raidillons, FC ≤ 160. Tu dois te sentir trop sage — personne ne gagne sa course ici."},
    {"t":"2 · Plateau ondulé","km":"km 8 → 12","faire":"Replat d'altitude vallonné (~800 m) avec un creux net vers le km 11-12. Relâche, roule, et surtout mange/bois : c'est le moment de faire le plein avant la remontée."},
    {"t":"3 · Montée 2 — le crux","km":"km 12 → 16","faire":"Remontée jusqu'au sommet 897 m sur jambes déjà entamées. Le juge de paix. Marche assumée, petits pas, accepte la lenteur. Caféine juste avant."},
    {"t":"4 · Descente finale","km":"km 16 → 22","faire":"Longue descente roulante, ~−415 m. Contrôlé en haut (jambes cuites), puis plein gaz sur le roulant : ton feu vert pour te faire plaisir et doubler du monde."},
    {"t":"5 · Retour au lac","km":"km 22 → 24","faire":"Faux-plat final le long du lac. Vide le réservoir sur les derniers hectomètres, savoure l'arrivée."}],
  "plan":[
    {"n":"1","tag":"CONSERVATEUR","c":"#16a34a","titre":"Montée 1 — freiner l'ego","txt":"La grosse montée d'entrée (km 2-8, +360 m), jambes fraîches : le piège classique. Marche active aux raidillons, FC plafond 160. Tu dois te sentir presque trop sage. Tout se joue ici en négatif : trop vite = explosion au km 13.","fuel":"Électrolytes dès le km 5 — pas au km 15 comme à La Circaète."},
    {"n":"2","tag":"FAIRE LE PLEIN","c":"#C2410C","titre":"Plateau — manger &amp; rouler","txt":"Replat ondulé d'altitude (km 8-12) avec un creux vers le km 11. Relâche, foulée courte cadence haute, profite de cette accalmie pour t'alimenter avant la remontée. Vitesse gratuite, pas forcée.","fuel":"1 gel ici, et recharge l'eau à fond au ravito du plateau."},
    {"n":"3","tag":"VIGILANCE","c":"#dc2626","titre":"Crux — survivre, marcher, manger","txt":"Remontée au sommet 897 m (km 12-16) sur jambes entamées. C'est ici que les gens explosent — à cause de la Montée 1 surcuite. Marche assumée, petits pas, on survit, on ne brille pas.","fuel":"Gel caféiné Nduranz juste avant : la caféine culmine en plein crux."},
    {"n":"4","tag":"POUSSER","c":"#F4561D","titre":"Descente finale — lâcher les chevaux","txt":"Longue descente roulante (km 16-22, −415 m). Contrôlé en haut le temps de te remettre en jambes, puis plein gaz sur le roulant et le retour au lac. Si tu as été discipliné avant, tu doubles du monde et tu finis en plaisir.","fuel":"Dernier gel si besoin pour la relance."}],
  "nutrition":{
    "avant":"<strong>Veille :</strong> dîner riche en glucides (pâtes, riz), bonne hydratation, 1 comprimé TA dans 500 ml d'eau. <strong>Matin de course :</strong> petit-dej 2h30 avant le départ (flocons d'avoine + banane + miel + café). <strong>1h avant :</strong> 1 comprimé TA dans 500 ml eau — gourde du matin. Gilet HDV5 : dissoudre <strong>2 comprimés TA dans tes flasques</strong> (~600 ml totaux) avant de partir.",
    "intro":"Stratégie à 2 couches : les <strong>comprimés TA Electrolytes</strong> (350 mg sodium/comprimé) couvrent l'hydratation en continu dans ton gilet, les <strong>Nduranz</strong> apportent glucides et caféine aux moments clés. Des <strong>gels non-caféinés</strong> (2 à acheter, ex. Aptonia Decathlon ~1 €/pièce) assurent le débit glucidique de base. <strong>Pas de BCAA dans ce plan.</strong>",
    "items":[
      ["TA Energy Electrolytes Tropical","350 mg Na · 80 mg K · 52 mg Mg / cpr","ÉLECTROLYTES — 2 cpr dans les flasques au départ + 1 cpr rechargé au ravito intermédiaire"],
      ["Gel non-caféiné (Aptonia ou équiv.)","~25-45 g glucides · 0 mg caféine","BASE — 1 gel à 20 min avant le départ, 1 gel km 8-10 (premier tiers)"],
      ["Nduranz NRGY 45 — Cherry","45 g glucides · 65 mg caféine","ARME 1 — km 13-14 (entrée du crux, montée 2 km 12-16) · pic caféine en plein crux"],
      ["Nduranz NRGY 45 — Coffee Amarena","45 g glucides · 130 mg caféine","ARME 2 — km 20-21 (descente finale) · relance et arrivée"]],
    "note":"Cible : <strong>~50 g glucides/h</strong> sur 2h15-2h45. <strong>Timing caféine :</strong> Cherry (65 mg, pic ~35 min) au km 13 = en plein crux km 15-16. Coffee Amarena (130 mg) au km 20 couvre la descente finale et l'arrivée. Caféine totale en course : 195 mg (hors café du matin). Chaque gel avec quelques gorgées d'eau des flasques TA.",
    "apres":"<strong>Dans les 15 min :</strong> 1 comprimé TA dans 500 ml d'eau — priorité absolue (lien direct avec l'incident Circaète). <strong>Dans l'heure :</strong> repas protéiné (œufs, charcuterie, fromage, riz). Éviter l'alcool les 2h suivant la course."},
  "hydra":"<strong>3 ravitaillements</strong> sur le parcours (solide : fruits, fruits secs, gâteaux ; liquide : eau, jus, soda). Juillet = chaleur garantie : vise <strong>400-500 ml/h</strong> depuis les flasques TA + recharge à chaque ravito. Dissoudre 1 comprimé TA supplémentaire dans la flasque rechargée. <strong>Règle absolue :</strong> électrolytes dès le km 5, ne jamais attendre la soif — c'est la leçon de La Circaète appliquée.",
  "zones":[
    ["Endurance fond.","134 – 154","Croisière : faux-plats, descentes courues, plat roulant"],
    ["Tempo / bascule","154 – 167","Montées : plafond 160. Au-delà → marche active, laisse la FC redescendre"],
    ["Seuil +","&gt; 167","Réservé à la relance finale, jamais avant"]],
  "terrain":"Single en forêt (terre, herbe, racines), roulant par endroits, avec des passages plus techniques sur cailloux et sentes étroites — pieds légers, regard devant. Rien d'alpin : on reste dans les collines boisées du Beaujolais Vert. <strong>Chaussures :</strong> tes Cascadia 19, bonne accroche pour le terrain sec et caillouteux de juillet.",
  "pratique":[
    ["🅿️ Départ / arrivée","Salle des sports de Cublize — parking, vestiaires, douches sur place"],
    ["🥾 Bâtons","Autorisés. Utiles sur les raidillons, mais optionnels vu le D+ modéré"],
    ["🏊 Après la course","Lac des Sapins : baignade possible — récup' active idéale par temps chaud"],
    ["🎒 Matériel","Gilet HDV5 + flasques, électrolytes, 5-6 gels, casquette/visière (chaleur), crème anti-frottements"]],
  "erreurs":[
    "Partir trop vite sur l'enthousiasme du départ de masse — le relief te le fera payer plus tard.",
    "Attendre d'avoir soif pour boire : en juillet, c'est déjà trop tard.",
    "Oublier les électrolytes dès le départ — l'erreur exacte de La Circaète.",
    "Vouloir performer : c'est une course plaisir et un test, pas un objectif chrono.",
    "Courir tous les raidillons : la marche active est plus économique et te garde des jambes.",
    "Zapper un ravito : recharge l'eau systématiquement, même si tu te sens bien."],
  "sources":"Données : trace GPX officielle du 24 km (tracedetrail.fr/trace/327465) — 24,06 km, sommet 897 m, départ/arrivée 447 m. D+ officiel 901 m (le GPS lit souvent ~1040 m, normal). Trail Tour Beaujolais, organisateur Y’A.C.A. Courir. Zones FC basées sur tes repères (FCmax ~192, bascule marche ~160) — ne remplacent pas un avis médical."},
 "runinlyon":{
  "nom":"Run In Lyon by Harmonie Mutuelle — Semi-Marathon",
  "soustitre":"Place Bellecour → Terreaux, quais de Saône et du Rhône, Parc de la Tête d'Or → retour Bellecour",
  "date":"Dimanche 4 octobre 2026",
  "depart":"Départ 8h30 (à reconfirmer au retrait de dossard) · Place Bellecour, Lyon",
  "format":"21,097 km · Route 100% · Label FFA Argent · ~30 000 coureurs cumulés sur les 4 courses (5 km, 10 km, semi, marathon)",
  "accent":"#F4561D",
  "stats":[["21,097","km"],["1h50","cible (groupe)"],["5:13-5:20/km","allure visée"],["5","semaines avant Nice"]],
  "intro":"<strong>Course officielle utilisée comme test grandeur nature de l'allure marathon</strong>, 5 semaines avant Nice. Parcours urbain compact entre Terreaux, les quais de Saône et du Rhône et le Parc de la Tête d'Or, avec arrivée place Bellecour. Tu la cours avec deux amis visant 1h50 (5:13/km) — l'objectif n'est pas la performance mais <strong>la discipline d'allure en conditions de course réelle</strong> : dossard, concurrents à doubler, ambiance de départ de masse.",
  "phrase":"1h50 sur 21,1 km, soit <strong>5:13/km</strong> — légèrement sous ta fourchette basse (5:15-5:20/km visés pour Nice), mais dans un mouchoir de poche. Cale-toi sur le groupe tant que l'effort reste maîtrisé ; s'il commence à tirer, laisse-le filer plutôt que de forcer.",
  "profil":"Parcours urbain, globalement plat à légèrement vallonné (quais, ponts, quelques faux-plats). Pas de profil GPX officiel du semi vérifié pour l'édition 2026 à ce stade — se fier au ressenti d'effort plutôt qu'à un relief anticipé dans le détail.",
  "segments":[
    {"t":"1 · Bellecour — Terreaux","km":"km 0 → 5","faire":"Départ dense, presqu'île. Laisser le groupe 1h50 trouver son rythme sans se laisser emporter par l'excitation du départ — les premiers hectomètres sont toujours plus rapides que prévu dans la foule."},
    {"t":"2 · Quais de Saône / Rhône","km":"km 5 → 14","faire":"Section la plus roulante, bords de fleuve. C'est là que la discipline se joue vraiment : rester calé sur le groupe, résister à l'envie de doubler les coureurs plus lents autour — exactement le déclencheur identifié cette saison."},
    {"t":"3 · Parc de la Tête d'Or","km":"km 14 → 18","faire":"Cadre agréable, léger relâchement mental possible. Vérifier l'allure au kilomètre plutôt qu'à la sensation : c'est souvent ici qu'une dérive commence sans s'en rendre compte."},
    {"t":"4 · Retour vers Bellecour","km":"km 18 → 21,1","faire":"Si le groupe est toujours tenable, finir avec lui. Si l'effort est devenu intenable, ralentir et finir propre plutôt que de cramer les 2 derniers kilomètres — l'info utile pour Nice, c'est la tenue de l'allure, pas le chrono final."}],
  "plan":[
    {"n":"1","tag":"CONTRÔLE","c":"#F4561D","titre":"Départ Bellecour — ne pas s'emballer","txt":"Dossard, foule, adrénaline : le piège classique du départ de course. Se placer près du groupe 1h50 dès le départ pour ne pas avoir à les rattraper en forçant sur les 2 premiers km.","fuel":"Rien de spécifique — bien hydraté avant le départ suffit sur 1h50."},
    {"n":"2","tag":"TENIR","c":"#F4561D","titre":"Quais — le vrai test","txt":"Km 5 à 14 : rester calé sur le groupe, résister à l'envie de doubler. C'est la section la plus longue et la plus exposée au déclencheur identifié cette saison (l'envie de doubler en ambiance de course).","fuel":"Eau aux ravitos si besoin, pas d'enjeu nutritionnel sur ce format."},
    {"n":"3","tag":"DÉCISION","c":"#dc2626","titre":"Tête d'Or — vérifier, pas deviner","txt":"Si l'allure du groupe commence à coûter cher (FC qui s'envole, jambes qui protestent), c'est le moment de décider consciemment de lâcher plutôt que de s'accrocher par fierté.","fuel":"—"},
    {"n":"4","tag":"FINIR PROPRE","c":"#16a34a","titre":"Retour Bellecour","txt":"Terminer à l'allure qui reste gérable, avec le groupe ou sans. Un semi fini propre à 5:20/km vaut mieux qu'un semi fini cassé à 5:05/km en moyenne.","fuel":"—"}],
  "zones":[
   ["Zone marathon (cible)","152 – 163","L'allure 5:13-5:20/km doit rester dans cette plage si la forme du jour est bonne."],
   ["Dérive à surveiller","163 – 172","Signal que l'allure du groupe coûte plus cher que prévu — vérifier consciemment plutôt que d'ignorer."],
   ["Décroche","&gt; 172","Lâcher le groupe et finir à son propre rythme plutôt que de forcer jusqu'à l'arrivée."]],
  "nutrition":{
   "avant":"<strong>Veille :</strong> repas normal, pas de charge glucidique particulière pour 1h50. <strong>Matin de course</strong> (départ 8h30) : petit-déjeuner habituel 2h-2h30 avant, rien de nouveau à tester ce jour-là.",
   "intro":"Sur 1h50, la nutrition n'est pas le facteur limitant — contrairement à un marathon ou un trail long, l'enjeu de cette course est la discipline d'allure, pas le carburant. Hydratation aux ravitos suffit largement.",
   "items":[
     ["Eau (ravitos course)","selon soif","Boire aux points de ravitaillement si besoin, sans excès sur un format aussi court."],
     ["Gel (optionnel)","~25 g glucides","Un seul si besoin vers 45-50 min, uniquement si tu en ressens l'envie — pas indispensable sur 1h50."]],
   "note":"Rien à sur-préparer ici : l'attention doit rester sur l'allure et le groupe, pas sur le protocole nutritionnel.",
   "apres":"Hydratation normale et repas habituel — pas de protocole de récupération spécifique nécessaire pour ce format."},
  "hydra":"Boire aux ravitos si besoin. Sur 1h50, la déshydratation n'est pas un risque réel sauf forte chaleur inhabituelle début octobre — vérifier la météo la veille.",
  "terrain":"Route 100% goudronnée, en ville, large et sécurisée. Chaussures de route habituelles (Novablast). Pas d'enjeu météo particulier à 5 semaines de la course — vérifier la prévision la veille.",
  "pratique":[
   ["🏅 Dossard","Retrait au préalable (Village Run In Lyon) — vérifier le lieu et les horaires de retrait sur le site officiel avant le week-end de course."],
   ["👥 Groupe 1h50","Objectif du groupe : 5:13/km. Se placer avec eux dans le sas de départ dès le début pour ne pas avoir à les rejoindre en courant trop vite."],
   ["🚇 Arrivée Bellecour","Comme pour le 10 km et le marathon, arrivée place Bellecour — repérer un point de retrouvailles avant le départ."]],
  "erreurs":[
   "Partir plus vite que le groupe dans l'euphorie du départ, puis devoir freiner artificiellement.",
   "S'accrocher au groupe par fierté alors que l'effort devient intenable — l'objectif est l'allure marathon tenue, pas le classement.",
   "Piloter uniquement à la sensation dans le Parc de la Tête d'Or, là où une dérive peut commencer sans s'en rendre compte.",
   "Traiter cette course comme un objectif chrono alors que c'est un test de discipline d'allure pour Nice."],
  "sources":"Date, distance (21,097 km) et lieu de départ/arrivée (Place Bellecour) confirmés via lyon.fr, marathons.com et campus.coach (édition 2026, 4 octobre). Tracé général du semi (Terreaux, quais, Tête d'Or) basé sur la description éditoriale de l'édition 2025 (marathons.com) — non reconfirmé sur plan officiel 2026 précis à ce stade. Horaire de départ (8h30) rapporté par werun.world, a reconfirmer a l'approche de la course. Aucun profil GPX officiel du semi verifie pour cette fiche."}
}
print("Semaines:",len(SEANCES_BY_WEEK)+1,"| Séances:",sum(len(v) for v in SEANCES_BY_WEEK.values()))
import json as _j
_hist=_j.load(open('hist.json',encoding='utf-8'))

# ═══════════════════════════════════════════════════════════════════
# HIST — volumes hebdomadaires (graphiques de progression du Cockpit)
# ═══════════════════════════════════════════════════════════════════
# hist.json est un fichier externe qui n'a plus ete mis a jour depuis
# juillet : il s'arretait a S28 et contenait des valeurs fausses sur
# S25 (52 au lieu de 56,6), S27 (30,1 au lieu de 53,4) et S28 (11 au
# lieu de 61). Le Cockpit affichait donc 357 km sur 8 semaines contre
# 418 reels -- 15 % d'ecart.
# QUATRIEME bloc a deriver pour la meme raison. Meme correctif : les
# semaines couvertes par SEANCES_BY_WEEK sont desormais CALCULEES,
# hist.json ne sert plus que pour l'historique anterieur a S25.
def _hist_recalc(base):
    _agg = {}
    for _w, _a in SEANCES_BY_WEEK.items():
        for _s in _a:
            _r = _s.get("realise") or {}
            if _r.get("statut") not in ("fait", "partiel") or not (_r.get("km") or 0):
                continue
            _k = _agg.setdefault(int(_w), {"km": 0.0, "re": 0})
            _k["km"] += _r["km"]
            _k["re"] += _r.get("re") or 0
    # on conserve les semaines historiques non couvertes par SBW
    _out = [h for h in base if h["sem"] not in {f"S{w}" for w in _agg}]
    for _w in sorted(_agg):
        _v = _agg[_w]
        _out.append({"sem": f"S{_w}", "km": round(_v["km"], 1),
                     "re": _v["re"], "easy_pace": None})
    return _out

_hist["HIST"] = _hist_recalc(_hist["HIST"])
print("HIST recalcule :", len(_hist["HIST"]), "semaines")

# Allure de TRAVAIL des seances de qualite (blocs seuls, hors echauffement et recups).
# marathonEquiv() projette l'allure marathon a partir de ce champ s'il existe ; sinon
# il retombe sur realise.allure, qui est souvent la moyenne de TOUTE la seance
# (echauffement + recups compris) et fausse alors la projection (build 224).
_ALLURE_TRAVAIL={("29","2"):"4:28/km",("31","5"):"5:09/km",("35","4"):"4:41/km",
                 ("36","3"):"4:36/km",("41","2"):"5:18/km"}
for _w,_i in _ALLURE_TRAVAIL:
    for _s in SEANCES_BY_WEEK.get(_w,[]):
        if str(_s["id"])==_i and _s.get("realise"):
            _s["realise"]["allure_travail"]=_ALLURE_TRAVAIL[(_w,_i)]
# Seuil du 29/09 remplace par une sortie vallonnee continue (pas de bloc seuil) :
# ne doit pas nourrir la projection marathon.
for _s in SEANCES_BY_WEEK.get("40",[]):
    if str(_s["id"])=="2" and _s.get("realise"):
        _s["realise"]["hors_projection"]=True

# POLAR -- repartition d'intensite CALCULEE (etait un instantane fige 8/43/43/5).
def _polar_calc():
    QUAL=("Seuil","Sp\u00e9cifique","sp\u00e9cifique","Test","Course","VMA","Tempo","C\u00f4tes","Cotes")
    c={"tres_facile":0.0,"ef":0.0,"gris":0.0,"qualite":0.0}; n=0; first=None
    for _w,_a in SEANCES_BY_WEEK.items():
        for _s in _a:
            _r=_s.get("realise") or {}
            if _r.get("statut") not in ("fait","partiel") or not _r.get("km") or _s.get("sport")!="Course \u00e0 pied":
                continue
            km=float(_r["km"]); n+=1
            if first is None or _s["date"]<first: first=_s["date"]
            if any(k in _s.get("type","") for k in QUAL):
                c["qualite"]+=km; continue
            sp=[x for x in (_r.get("splits") or []) if isinstance(x.get("km"),(int,float)) and x.get("fc")]
            if len(sp)>=3:
                for x in sp:
                    f=x["fc"]; c["tres_facile" if f<134 else "ef" if f<=154 else "gris"]+=km/len(sp)
            elif _r.get("fc_moy"):
                f=_r["fc_moy"]; c["tres_facile" if f<134 else "ef" if f<=154 else "gris"]+=km
    T=sum(c.values()) or 1.0
    pc={k:int(round(v/T*100)) for k,v in c.items()}
    # arrondis : la somme doit faire 100
    pc["ef"]+=100-sum(pc.values())
    mois=["janvier","f\u00e9vrier","mars","avril","mai","juin","juillet","ao\u00fbt","septembre","octobre","novembre","d\u00e9cembre"]
    y,m,dd=first.split("-")
    pc["periode"]=f"depuis le {int(dd)} {mois[int(m)-1]} ({n} sorties, {round(T)} km)"
    pc["methode"]=("Calcul\u00e9 sur tes s\u00e9ances logu\u00e9es. S\u00e9ances de qualit\u00e9 (seuil, allure marathon, vitesse, course) "
                   "compt\u00e9es enti\u00e8res ; les autres class\u00e9es kilom\u00e8tre par kilom\u00e8tre selon la FC : "
                   "moins de 134 tr\u00e8s facile, 134 \u00e0 154 EF, au-dessus zone grise.")
    return pc
_hist["POLAR"]=_polar_calc()
print("POLAR calcule :",_hist["POLAR"])
# ═══════════════════════════════════════════════════════════════════
# MONTHLY / SAISON2026 — SOURCE UNIQUE DE VERITE
# ═══════════════════════════════════════════════════════════════════
# Historique : ces blocs etaient saisis A LA MAIN. Le mois d'aout est
# reste fige au 09/08 (79 km, 6 sorties) pendant que 15 sorties et
# 184 km avaient ete courus -- un ecart de 105 km sur les totaux de
# saison, invisible parce qu'aucun controle ne confrontait MONTHLY
# aux seances reellement loguees.
# C'est le TROISIEME KPI a deriver pour la meme raison (apres l'ACWR
# fige a 0,69, puis fausse par erreur de fenetre). Meme correctif :
# le mois en cours est desormais CALCULE depuis SEANCES_BY_WEEK.
# Les mois anterieurs restent des constantes verifiees activite par
# activite sur Strava (janvier a juillet, controle en juin 2026).
_MOIS_CLOS = [
  {"m":"Jan","km":224,"elev":1342,"sorties":19,"re":2431},
  {"m":"Fév","km":227,"elev":1674,"sorties":21,"re":2229},
  {"m":"Mar","km":342,"elev":2962,"sorties":25,"re":2978},
  {"m":"Avr","km":283,"elev":2254,"sorties":23,"re":2265},
  {"m":"Mai","km":202,"elev":5978,"sorties":15,"re":2171},
  {"m":"Juin","km":190,"elev":2382,"sorties":15,"re":2100},
  {"m":"Juil","km":257,"elev":2805,"sorties":18,"re":2669},
]
_LIB_MOIS = {1:"Jan",2:"Fév",3:"Mar",4:"Avr",5:"Mai",6:"Juin",
             7:"Juil",8:"Août",9:"Sep",10:"Oct",11:"Nov",12:"Déc"}

def _mois_courants():
    """Agrege les seances loguees par mois, a partir d'aout 2026."""
    import datetime as _d
    acc = {}
    for _w, _a in SEANCES_BY_WEEK.items():
        for _s in _a:
            _r = _s.get("realise") or {}
            if _r.get("statut") not in ("fait", "partiel") or not _s.get("date"):
                continue
            _dt = _d.date.fromisoformat(_s["date"])
            if _dt.year != 2026 or _dt.month < 8:
                continue
            _k = acc.setdefault(_dt.month, {"km":0.0,"elev":0,"sorties":0,"re":0})
            _k["km"]      += _r.get("km") or 0
            _k["elev"]    += _r.get("elevation_gain") or 0
            _k["sorties"] += 1
            _k["re"]      += _r.get("re") or 0
    return [{"m":_LIB_MOIS[_m], "km":round(_v["km"]), "elev":round(_v["elev"]),
             "sorties":_v["sorties"], "re":_v["re"]}
            for _m, _v in sorted(acc.items())]

MONTHLY = _MOIS_CLOS + _mois_courants()

_TOT_KM  = sum(_m["km"] for _m in MONTHLY)
_TOT_EL  = sum(_m["elev"] for _m in MONTHLY)
_TOT_SO  = sum(_m["sorties"] for _m in MONTHLY)
SAISON2026 = {"annee":2026, "km":_TOT_KM, "elev":_TOT_EL, "sorties":_TOT_SO, "mois":len(MONTHLY),
  "note":"Course à pied uniquement (Run + Trail) · randonnées, raquettes et vélo exclus · mois en cours recalculé automatiquement à chaque build"}
# Records Strava (pr_count, Run + Trail) du 1er janvier au 14 juin 2026, AVANT le plan de preparation
# (releves sur Strava le 15/10/2026 : 109 sorties, 1537 records). Le plan en ajoute ensuite, seance par
# seance, via realise.pr. 109 + 63 sorties du plan = 172 = SAISON2026["sorties"] (controle croise).
SAISON2026["pr_avant_plan"] = 1537
SAISON2026["pr_top_avant_plan"] = [
  {"d":"2026-03-18","t":"Course à pied dans l'après-midi","km":10.36,"al":"4:38/km","pr":85},
  {"d":"2026-05-20","t":"Course à pied le matin","km":10.03,"al":"4:43/km","pr":69},
  {"d":"2026-03-10","t":"Course à pied rejoint par Perrine au parc","km":16.04,"al":"6:03/km","pr":61},
  {"d":"2026-03-24","t":"Course à pied rejoint par Perrine au parc","km":30.11,"al":"5:42/km","pr":56},
  {"d":"2026-01-21","t":"Course à pied dans l'après-midi","km":21.13,"al":"5:35/km","pr":44},
  {"d":"2026-03-09","t":"Course à pied le matin","km":17.02,"al":"5:55/km","pr":42},
]
print("MONTHLY calcule :", _TOT_KM, "km |", _TOT_SO, "sorties |", _TOT_EL, "m")

# Progression d'efficience aérobie par saison — points d'ancrage réels (cardio Strava, EF route, allure ramenée à 145 bpm).
# Hiver/Printemps figés (données historiques). Été enrichi par les séances loggées avec température.
SAISON_EFF={
  "unite":"allure équivalente à 145 bpm (FC corrigée de la dérive thermique)",
  "ref_bpm":145,
  "points":[
    {"saison":"Hiver","mois":"fév 26","pace_s":347,"eff":1.1934,"n":3,"corr":False,
     "detail":"3 EF route de février (10-16-23/2), FC 141-148, conditions fraîches — aucune correction nécessaire."},
    {"saison":"Printemps","mois":"avr 26","pace_s":336,"eff":1.2328,"n":3,"corr":False,
     "detail":"3 EF route d'avril (15-24-27/4), FC 139-146, conditions douces."},
    {"saison":"Été","mois":"juil 26","pace_s":322,"eff":1.2845,"n":2,"corr":True,
     "detail":"2 EF route de juillet (15-17/7) sous 26-30°C, FC brute 147 corrigée de la dérive thermique (~11-15 bpm)."},
    {"saison":"Automne","mois":"oct 26","pace_s":352,"eff":1.1763,"n":3,"corr":False,
     "detail":"3 sorties faciles d'octobre sur route (05, 09 et 17/10), FC 137-149, 16-19 °C : récupération post-semi, longue de 30 km, récupération post-longue. Aucune correction nécessaire."},
  ],
  "note":"À FC égale, l'efficience de cet automne (352 s/km à 145 bpm) est comparable à celle de février (347 s/km) : pas de gain mesuré depuis l'hiver sur les sorties faciles. Printemps (336) et été (322, corrigé de la chaleur par estimation) paraissaient plus rapides ; l'été est une estimation, et les sorties d'octobre suivent le semi et une longue de 30 km, donc des jambes fatiguées. Échantillon de 2-3 sorties par saison — valeurs à ± quelques secondes."
}
# ═══════════════════════════════════════════════════════════════════
# ACWR — SOURCE UNIQUE DE VERITE
# ═══════════════════════════════════════════════════════════════════
# Historique : ce bloc etait saisi A LA MAIN. Il a ete trouve fige a 0.69
# pendant quatre semaines, puis faux (1.02 au lieu de 0.97) a cause d'une
# erreur de fenetre lors d'un calcul manuel. Toute valeur recopiee finit
# par mentir : elle est desormais CALCULEE depuis les seances loguees,
# avec exactement la meme definition que _dynamicACWR() cote navigateur
# (fenetre glissante 7 / 28 jours, et non semaines calendaires).
# FRAICHEUR DU COCKPIT : chaque carte declare sa source et la date de sa donnee
# (affichee "a jour au ..." ; scripts/preflight.py avertit au-dela de 14 jours).
def _dates_realisees(pred):
    return sorted(x["date"] for _a in SEANCES_BY_WEEK.values() for x in _a
                  if x.get("date") and pred(x.get("realise") or {}, x))
# Repos facultatifs passes : sans sortie ce jour-la, ils sont clos automatiquement (respectes) a chaque build.
import datetime as _dtm, os as _osm
_auj = _dtm.date.fromisoformat(_osm.environ['RUNNING_TODAY']) if _osm.environ.get('RUNNING_TODAY') else _dtm.date.today()
for _a in SEANCES_BY_WEEK.values():
    for _x in _a:
        _r = _x.get("realise") or {}
        if (_x.get("type") == "Repos" and _x.get("date") and _x["date"] < _auj.isoformat()
                and _r.get("statut") in (None, "a_faire")
                and not any(_y.get("date") == _x["date"] and ((_y.get("realise") or {}).get("km") or 0) > 0
                            for _b in SEANCES_BY_WEEK.values() for _y in _b)):
            _x["realise"] = {"statut": "fait", "km": 0, "repos_auto": True,
                             "commentaire": "Repos respecté (clos automatiquement : aucune sortie ce jour-là)."}
_last_fait = _dates_realisees(lambda r, x: r.get("statut") in ("fait", "partiel") and (r.get("km") or 0) > 0)[-1]
_last_dc = _dates_realisees(lambda r, x: (r.get("decouplage") or {}).get("qualite") == "fiable")[-1]
_last_easy = _dates_realisees(lambda r, x: r.get("statut") == "fait" and (r.get("km") or 0) > 0
                              and ((x.get("type") or "").startswith("EF") or (x.get("type") or "").startswith("Récup")))[-1]
COCKPIT_SOURCES = [
    {"carte": "CTL · ATL · TSB", "source": "séances loguées", "date": _last_fait},
    {"carte": "ACWR", "source": "séances loguées", "date": _last_fait},
    {"carte": "Z2 pace", "source": "séances faciles loguées", "date": _last_easy},
    {"carte": "Découplage cardiaque", "source": "dérive calculée au log (flux Strava, fiable)", "date": _last_dc},
    {"carte": "Progression allure par type", "source": "séances loguées", "date": _last_fait},
    {"carte": "Zones FC", "source": "séances loguées", "date": _last_fait},
    {"carte": "Cadence", "source": "séances loguées", "date": _last_fait},
    {"carte": "Progression par saison", "source": "SAISON_EFF (dernier point : octobre)", "date": "2026-10-17"},
    {"carte": "Performances", "source": "RECORDS_PERF (meilleurs efforts Strava)", "date": "2026-08-22"},
]
def _acwr_compute():
    import datetime as _dt
    faits=[]
    for _w,_arr in SEANCES_BY_WEEK.items():
        for _s in _arr:
            _r=_s.get("realise") or {}
            if _r.get("statut") in ("fait","partiel") and _s.get("date"):
                faits.append((_dt.date.fromisoformat(_s["date"]), _r.get("re") or 0))
    if not faits:
        return {"charge7j":0,"charge28j":0,"acwr":None,"ref":None}
    # La reference est AUJOURD'HUI, pas la derniere seance loguee : sinon la
    # valeur figee au build se decale de celle recalculee en direct par
    # l'app des qu'un jour passe sans courir (constate le 25/08 : 1,29 fige
    # contre 1,04 reel). La fenetre glissante doit suivre le calendrier.
    import os as _os
    # RUNNING_TODAY (AAAA-MM-JJ) fixe la date du build : build.py --check rejoue la date enregistree
    # dans data/meta.json (BUILT_ON), ce qui rend le build reproductible d'un jour a l'autre.
    _today=_dt.date.fromisoformat(_os.environ['RUNNING_TODAY']) if _os.environ.get('RUNNING_TODAY') else _dt.date.today()
    _ref=max(_today, max(d for d,_ in faits))
    c7 =sum(re for d,re in faits if 0<=(_ref-d).days<=6)
    c28=sum(re for d,re in faits if 0<=(_ref-d).days<=27)
    _a=round(c7/(c28/4),2) if c28 else None
    return {"charge7j":c7,"charge28j":c28,"acwr":_a,"ref":_ref.isoformat()}

_ACW=_acwr_compute()

def _acwr_zone(a):
    if a is None:            return "Données insuffisantes pour calculer le ratio."
    if a < 0.8:              return "Sous-charge : la charge récente est nettement inférieure à ton habitude. Utile en récupération ou en affûtage, à surveiller si ce n'est pas voulu."
    if a <= 1.3:             return "Zone optimale : la charge récente est cohérente avec ton habitude des quatre dernières semaines. C'est le ratio dans lequel les adaptations se construisent avec le risque de blessure le plus bas."
    if a <= 1.5:             return "Charge élevée : tu montes plus vite que ton corps ne s'adapte. Tolérable ponctuellement, risque si cela dure."
    return "Surcharge : ratio associé a une hausse nette du risque de blessure. Allège sans attendre."

ACWR_DATA={"charge7j":_ACW["charge7j"],"charge28j":_ACW["charge28j"],"acwr":_ACW["acwr"],
  "ref":_ACW["ref"],
  "interpretation":_acwr_zone(_ACW["acwr"])+" Charge aiguë "+str(_ACW["charge7j"])+" sur 7 jours, chronique "+str(_ACW["charge28j"])+" sur 28 jours (soit "+str(round(_ACW["charge28j"]/4))+" par semaine), calculé au "+str(_ACW["ref"])+"."}
print("ACWR calcule :", ACWR_DATA["charge7j"], "/", ACWR_DATA["charge28j"], "=>", ACWR_DATA["acwr"], "(ref", ACWR_DATA["ref"] + ")")
RECORDS_PERF=[
  {"dist":"5 km","record":"22:52","record_sub":"meilleur effort Strava","actuel":"4:47/km","actuel_sub":"meilleur effort embarqué 2026 vérifié (22/08)","temps_rec":"22:52","temps_act":"23:57"},
  {"dist":"10 km","record":"46:14","record_sub":"meilleur effort Strava","actuel":"4:54/km","actuel_sub":"meilleur effort embarqué 2026 vérifié (22/08)","temps_rec":"46:14","temps_act":"49:00"},
  {"dist":"Semi 21,1","record":"1h46:18","record_sub":"effort embarqué du 22/08 (hors course)","actuel":"5:02/km","actuel_sub":"allure du record officieux","temps_rec":"1h46:18","temps_act":"1h46:18","ref_course":"1h52:30","ref_course_sub":"Run In Lyon 2026 · course, couru malade"},
]
# Seule ligne non derivee : l'objectif. Les autres distances et le marathon projete sont calcules par l'app (projection en direct).
ALLURES_COURSE=[{"d":"Marathon objectif","temps":"3h45","allure":"5:20/km"}]
ALLURES=[{"nom":"Seuil 30","val":"≈4:40/km","sub":"~30 min · proche 10 km"},{"nom":"Seuil 60","val":"≈4:55/km","sub":"~60 min · proche semi"},{"nom":"Allure marathon","val":"≈5:18/km","sub":"bloc de 14 km du 15/10 : 5:11/km en déplacement, FC 161 · cible Nice 3h45 = 5:20"},{"nom":"Endurance facile","val":"5:50-6:25/km","sub":"le socle"},{"nom":"VMA courte","val":"≈4:15/km","sub":"plafond aérobie"}]
ZONES_FC=[{"z":"Z1","nom":"Récupération","bpm":"< 134","pct":"< 70%","col":"#FDE3D3","allure":"≥ 6:45/km"},{"z":"Z2","nom":"Endurance fondamentale","bpm":"134-154","pct":"70-80%","col":"#16a34a","allure":"5:50-6:25/km"},{"z":"Z3","nom":"Tempo / marathon","bpm":"154-167","pct":"80-87%","col":"#CA8A04","allure":"5:05-5:30/km"},{"z":"Z4","nom":"Seuil","bpm":"167-177","pct":"87-92%","col":"#C2410C","allure":"4:40-4:55/km"},{"z":"Z5","nom":"VO2 / VMA","bpm":"177-192","pct":"92-100%","col":"#DC2626","allure":"≤ 4:20/km"}]
REPLAY={"nom": "Petit Croisse Baulet", "date": "2026-07-12", "km": 11.04, "dplus": 530, "temps": "2h35", "alt": [1910, 1893, 1882, 1866, 1859, 1850, 1840, 1827, 1815, 1808, 1815, 1818, 1820, 1825, 1808, 1800, 1789, 1779, 1765, 1753, 1740, 1731, 1732, 1738, 1748, 1771, 1800, 1828, 1845, 1834, 1814, 1793, 1780, 1797, 1781, 1760, 1746, 1732, 1718, 1745, 1758, 1771, 1764, 1764, 1750, 1735, 1727, 1746, 1768, 1763, 1748, 1728, 1731, 1724, 1737, 1742, 1757, 1783, 1806, 1834, 1864, 1897, 1919, 1945, 1973, 2000, 1982, 1953, 1918, 1887, 1851, 1817, 1788, 1766, 1745, 1742, 1727, 1700, 1669, 1644, 1622, 1601, 1571, 1546, 1520, 1490, 1453, 1423, 1388, 1353, 1324, 1299, 1290, 1283, 1271, 1261, 1251, 1241, 1236, 1230], "dist": [0, 111, 223, 335, 446, 558, 669, 780, 892, 1003, 1115, 1226, 1338, 1449, 1561, 1673, 1784, 1895, 2008, 2118, 2230, 2342, 2454, 2564, 2676, 2788, 2899, 3011, 3123, 3234, 3345, 3457, 3569, 3680, 3792, 3903, 4015, 4126, 4238, 4349, 4460, 4572, 4683, 4795, 4906, 5018, 5130, 5241, 5352, 5464, 5575, 5687, 5799, 5910, 6022, 6134, 6245, 6357, 6468, 6580, 6691, 6802, 6914, 7025, 7136, 7248, 7361, 7471, 7583, 7694, 7806, 7917, 8030, 8140, 8252, 8362, 8475, 8586, 8698, 8810, 8920, 9031, 9144, 9255, 9368, 9478, 9590, 9702, 9813, 9924, 10036, 10148, 10259, 10371, 10482, 10596, 10706, 10816, 10930, 11040], "hr": [91, 93, 90, 93, 85, 87, 87, 84, 87, 93, 118, 93, 99, 121, 92, 87, 90, 83, 85, 82, 84, 89, 84, 99, 116, 152, 157, 160, 113, 101, 98, 106, 120, 111, 107, 101, 106, 115, 106, 158, 150, 141, 120, 122, 137, 136, 122, 164, 155, 125, 131, 140, 140, 125, 148, 136, 154, 163, 169, 168, 172, 172, 162, 162, 162, 137, 142, 148, 142, 141, 140, 142, 146, 133, 141, 158, 154, 142, 144, 146, 145, 150, 140, 141, 146, 138, 156, 149, 157, 144, 144, 140, 143, 153, 156, 162, 165, 164, 166, 166], "pace": [None, 25.25, 15.72, 11.74, 17.01, 12.44, 18.12, None, 16.67, 16.34, 14.37, 11.42, 12.25, 15.72, 13.23, 14.88, 13.23, 18.94, 15.15, 13.44, 12.44, 18.94, 17.73, 14.37, 10.16, 13.02, 17.01, 13.66, 24.51, 16.03, 18.52, 5.67, 21.37, 18.94, 17.73, 11.74, 11.57, 24.51, 9.8, 26.88, 13.89, 8.5, 11.74, 11.74, 6.72, 6.61, 9.47, 15.15, 18.12, 8.42, 8.33, 5.63, 8.59, 11.42, 14.12, 9.36, 13.23, 13.02, 11.74, 16.03, 24.51, 18.12, 25.25, None, 18.52, 9.36, 6.83, 12.44, 17.01, 10.96, 11.57, 15.43, 8.33, 10.96, 7.86, 7.25, 7.72, 8.87, 12.25, 7.65, 10.68, 6.41, 9.26, 7.65, 9.58, 10.16, 7.79, 10.96, 11.11, 19.38, 6.22, 15.72, 5.48, 3.97, 3.82, 4.39, 4.03, 3.75, 4.11, 4.48], "altMin": 1230, "altMax": 2000, "hrMax": 172}
PROFIL={"prenom":"Loïc","ville":"Lyon","cible_marathon":"3h45","cible_semi":"~1h44","fcmax":192,"poids":84}
PROJ={"base":13200,"goal":13500,"gmin":12600,"gmax":14400,
      "base_label":"forme de départ (réf. semi 1h52:39 + 16 km progressif du 9 juin à 4:50/km)",
      "mp_goal":"5:20/km"}
RECORDS=[{"label":"Semi 2022","val":"1h53","sub":"référence"},{"label":"Semi projeté","val":"~1h44","sub":"forme actuelle"},{"label":"Marathon visé","val":"3h45","sub":"objectif Nice"}]
VIGILANCE=[{"t":"Dos / lombaires","d":"surveiller en montée de charge"},{"t":"Carburant & électrolytes","d":"protocole validé canicule : électrolytes zéro cal. dès le départ + ~850 ml/h + 1 gel par heure — à combiner avec glucides si sortie > 2h"}]
S24_REALISE={"km":36.4,"runs":[
 {"iso":"2026-06-09","date":"Mar. 9","titre":"Footing 16 km — finish progressif","desc":"1h26 · 5:22/km · FC 153 (max 171) · charge 164 · Novablast 5","tag":"Endurance",
  "pr":2,"ach":11,"pr_detail":["Meilleur effort 2 km","Meilleur effort 1 mile"],
  "metriques":{"Distance":"16,0 km","Temps":"1h26","Allure":"5:22/km","FC moy / max":"153 / 171","D+":"54 m","Charge":"164","Cadence":"173 ppm","Calories":"1 205"},
  "chaussure":"ASICS Novablast 5 V",
  "splits":[[353,138],[351,142],[347,147],[324,153],[331,150],[327,151],[315,153],[326,154],[331,151],[318,154],[319,159],[332,155],[287,158],[302,160],[295,163],[290,164]],
  "lecture":"Les kilomètres racontent tout : départ à 5:53/km (FC 138, Z2 propre), puis une accélération continue jusqu'à <strong>4:50/km sur le dernier km, FC 164</strong> — la frontière Z3/Z4. Ce n'était pas un footing « un peu vif » : c'était un progressif qui finit au tempo, avec 11 records de segments au passage. La montée de FC est un choix d'allure, pas une dérive cardiaque.",
  "revue":"Belle séance… qui n'avait rien à faire là. À J+3 de la Circaète (1662 m de D+, effondrement électrolytique), finir 4 km entre 4:47 et 5:02/km, c'est de la qualité déguisée en endurance — le réflexe zone grise dans sa forme la plus pure : pas un footing trop rapide, mais un footing qui <em>devient</em> une séance. La bonne nouvelle : tenir ces allures à J+3 avec cette aisance confirme une récupération express et un moteur en forme. La consigne pour la suite : un footing a une allure de début ET une allure de fin — et c'est la même."},
 {"iso":"2026-06-10","date":"Mer. 10","titre":"Footing de récupération 10 km","desc":"1h03 · 6:06/km · FC 137 (max 155) · charge 47 · Clifton 10","tag":"Récupération",
  "metriques":{"Distance":"10,3 km","Temps":"1h03","Allure":"6:06/km","FC moy / max":"137 / 155","D+":"45 m","Charge":"47","Cadence":"172 ppm","Calories":"767"},
  "chaussure":"HOKA Clifton 10",
  "splits":[[374,136],[348,135],[376,138],[370,136],[373,141],[374,134],[371,136],[376,134],[360,136],[342,143]],
  "lecture":"Le contre-exemple parfait de la veille : 10 km entre 6:00 et 6:16/km, et surtout une <strong>FC clouée à 134-138 du premier au dernier kilomètre</strong> — zéro dérive sur une heure. C'est la signature d'une vraie récupération : l'effort ne s'accumule pas, il s'évacue.",
  "revue":"Rien à redire — c'est le modèle du genre, à encadrer. Quand tu te demanderas à quoi ressemble un footing de récup réussi pendant la prépa, reviens regarder cette sortie : allure stable, FC plate, charge 47. Exactement ce qu'on veut 4 jours après une course. Seule micro-remarque : le dernier km à 5:42 — l'envie d'accélérer en fin de sortie est ton tic, surveille-le."},
 {"iso":"2026-06-12","date":"Ven. 12","titre":"Footing de récupération 10 km — coupé volontairement","desc":"58:53 · 5:52/km · FC 137 (max 155) · charge 44 · Novablast 5","tag":"Récupération",
  "metriques":{"Distance":"10,0 km","Temps":"58:53","Allure":"5:52/km","FC moy / max":"137 / 155","D+":"37 m","Charge":"44","Cadence":"172 ppm","Calories":"755"},
  "chaussure":"ASICS Novablast 5 V",
  "splits":[[362,130],[351,133],[357,139],[359,135],[362,135],[349,136],[346,138],[335,140],[350,141],[343,141]],
  "lecture":"Allure régulière entre 5:35 et 6:02/km, FC qui glisse doucement de 130 à 141 — une dérive de +11 bpm sur une heure, parfaitement normale et même basse. Cadence stable à 172 ppm du début à la fin. Le 8e km à 5:35 est le seul moment où ça frémit.",
  "revue":"La séance compte moins que la décision : parti pour 13-15 km en se sentant très bien, tu as coupé à 10. <strong>S'arrêter parce que ça va bien, c'est la compétence n°1 du coureur qui dure</strong> — et celle qui te manquait mardi. Allure au bord intérieur de la cible (5:52 pour un plancher à 5:55), mais la FC à 137 valide l'effort. Trois jours, trois enseignements : mardi le piège, mercredi le modèle, vendredi la maturité."}],
 "revue":"<strong>Semaine de récup exemplaire : 3 sorties, 36,4 km, tout à plat, zéro intensité structurée.</strong> Mardi, le 16 km a fini en progressif jusqu'à 4:50/km (FC 164) — le réflexe zone grise dans sa version la plus sournoise : la séance qui dérive. Mercredi et vendredi : deux 10 km modèles (FC plate à 137). Le signal fort de la semaine, c'est vendredi : parti pour 13-15 km en se sentant très bien, tu as coupé à 10. <strong>S'arrêter parce qu'on se sent bien, c'est la maturité d'entraînement qu'on cherche.</strong> Zéro douleur dos, zéro douleur jambes : récupération en avance. Tu abordes la S25 dans des conditions idéales."}
REWINDS=_charge_rewinds()
JOURNAL=[{"sem":"S24","theme":"Récupération post-Circaète","texte":S24_REALISE["revue"]},
{"sem":"S25","theme":"Reprise & déblocage","texte":"<p>La semaine de reprise que tu devais faire. Pas celle que tu espérais peut-être, mais celle qu'il fallait — et tu l'as exécutée proprement.</p><p><strong>Ce qui ressort avant tout : la gestion de la chaleur.</strong> Quatre séances sur cinq démarrées entre 7h25 et 8h30. L'écart entre la s3 (FC 165/181, subi à midi) et les quatre autres (FC 140-151, maîtrisé) dit tout. Ce n'est pas une variable de confort, c'est une variable de performance.</p><p><strong>La progression dans la semaine est nette.</strong> S1/S2 très faciles (FC 140-143). S3 qualité en milieu de semaine, 6 km à 5:14/km tenus. S4 sortie longue avec fast finish à <strong>4:58/km sur le dernier kilomètre</strong> — sub-5 min au 4e jour consécutif en canicule. S5 bonus parfait, FC 144 en plein cœur de la Z2, rien dépensé.</p><p><strong>Ce que cette semaine confirme pour la Déraille (J-16) :</strong> tu n'es pas en reprise, tu es en forme. La Z2 pace à 5:56/km avec FC 140-144, c'est ton moteur aérobie qui tourne. Le fast finish montre que la résistance à la fatigue est là. S26 allégée par conception — laisse-la être légère.</p>"}]
# À partir de S26, JOURNAL se construit automatiquement depuis SEMAINES[n]["revue"] — plus jamais à mettre à jour ici.
for _sw in SEMAINES:
    if _sw["num"]>=26 and _sw.get("revue"):
        JOURNAL.append({"sem":f"S{_sw['num']}","theme":_sw.get("theme","") or "","texte":_sw["revue"]})
HEATMAP_HISTORIQUE={"2026-01-03": 10.1, "2026-01-05": 11.2, "2026-01-06": 13.0, "2026-01-10": 21.6, "2026-01-12": 10.0, "2026-01-13": 11.3, "2026-01-14": 11.0, "2026-01-15": 14.1, "2026-01-16": 4.0, "2026-01-17": 11.1, "2026-01-20": 11.0, "2026-01-21": 21.1, "2026-01-22": 10.0, "2026-01-23": 3.5, "2026-01-26": 10.3, "2026-01-27": 11.5, "2026-01-28": 10.0, "2026-01-29": 18.2, "2026-01-31": 11.0, "2026-02-02": 14.0, "2026-02-03": 21.2, "2026-02-05": 8.9, "2026-02-06": 11.1, "2026-02-07": 12.1, "2026-02-08": 4.2, "2026-02-09": 20.4, "2026-02-10": 10.2, "2026-02-11": 11.8, "2026-02-16": 10.2, "2026-02-17": 20.0, "2026-02-18": 10.0, "2026-02-20": 10.6, "2026-02-21": 10.0, "2026-02-22": 11.8, "2026-02-23": 10.1, "2026-02-24": 2.5, "2026-02-25": 10.0, "2026-02-26": 12.5, "2026-02-27": 5.0, "2026-03-01": 4.4, "2026-03-02": 11.3, "2026-03-03": 18.0, "2026-03-04": 20.4, "2026-03-05": 17.1, "2026-03-07": 21.2, "2026-03-09": 17.0, "2026-03-10": 16.0, "2026-03-11": 10.0, "2026-03-12": 17.2, "2026-03-15": 4.2, "2026-03-16": 18.1, "2026-03-17": 13.0, "2026-03-18": 14.2, "2026-03-19": 21.2, "2026-03-20": 10.5, "2026-03-23": 13.0, "2026-03-24": 30.1, "2026-03-26": 15.0, "2026-03-27": 10.0, "2026-03-29": 15.0, "2026-03-30": 12.0, "2026-03-31": 13.0, "2026-04-01": 10.0, "2026-04-03": 14.3, "2026-04-04": 21.2, "2026-04-06": 18.6, "2026-04-07": 15.0, "2026-04-09": 24.7, "2026-04-10": 12.0, "2026-04-13": 18.0, "2026-04-14": 14.5, "2026-04-15": 15.1, "2026-04-16": 11.0, "2026-04-18": 30.1, "2026-04-19": 3.8, "2026-04-20": 13.0, "2026-04-21": 17.0, "2026-04-22": 16.0, "2026-04-24": 10.3, "2026-04-26": 4.0, "2026-04-27": 10.7, "2026-04-30": 3.6, "2026-05-01": 42.4, "2026-05-04": 13.0, "2026-05-06": 10.5, "2026-05-08": 11.1, "2026-05-09": 11.1, "2026-05-16": 8.4, "2026-05-18": 17.0, "2026-05-20": 10.0, "2026-05-21": 21.2, "2026-05-22": 22.2, "2026-05-27": 4.6, "2026-05-28": 4.0, "2026-05-29": 16.6, "2026-05-31": 10.0, "2026-06-01": 14.0, "2026-06-02": 12.0, "2026-06-06": 29.8, "2026-06-09": 16.0, "2026-06-10": 10.3, "2026-06-12": 10.0}
# HEATMAP final = baseline historique (pré-plan, figée) fusionnée avec les vraies dates loggées dans SEANCES_BY_WEEK.
# Recalculée à chaque génération : jamais besoin d'y retoucher à la main.
HEATMAP=dict(HEATMAP_HISTORIQUE)
for _wk,_ss in SEANCES_BY_WEEK.items():
    for _se in _ss:
        _r=_se.get("realise") or {}
        if _r.get("statut") in ("fait","partiel") and _r.get("km") and _se.get("date"):
            HEATMAP[_se["date"]]=HEATMAP.get(_se["date"],0)+_r["km"]
CHANGELOG=[
  {"build":282,"date":"29 octobre 2026","sha":"","tag":"Log S44 seance 5 : 10 km un peu plus vite que l'allure marathon (renforcement remplacé) du 29/10","items":[
    "SEANCE : S44 seance 5 loggee depuis Strava : 10 km un peu plus vite que l'allure marathon (renforcement remplacé), 10,02 km en 52:02 (5:12/km), FC 150/172, D+ 36 m, 11 °C, Novablast 5 J.",
    "CHAUSSURES : Novablast 5 J a 887 km."]},
  {"build":281,"date":"29 octobre 2026","sha":"","tag":"Rewind de séance : deux corrections après le premier test sur l'iPhone","items":[
    "LE CŒUR : la courbe de FC sous la cible était tracée presque en blanc (reste du fond sombre) et semblait coupée ; elle est maintenant grise, en entier, avec la partie au-dessus de la cible en ocre et une légende « Ta FC ».",
    "L'ANALYSE DU COACH : seul le texte défile, avec un fondu en haut et en bas ; « Précédent » et « Continuer » restent toujours visibles en bas, hors de la zone qui défile (sur iPhone, un toucher pendant l'élan du défilement ne déclenchait pas le bouton) ; « Lire la revue complète » passe à la fin du texte.",
    "TA PROGRESSION : le point de la séance du jour, blanc sur blanc, est orange."]},
  {"build":280,"date":"29 octobre 2026","sha":"","tag":"Blanc et orange : corrections de la relecture indépendante","items":[
    "ACCUEIL : le conseil du jour (affûtage avant une course, surcharge, relance) réapparaît dans la carte Forme ; « Ton année » prend l'année des données.",
    "FICHE D'UNE SÉANCE FAITE : lecture vocale et théorie de la séance rétablies.",
    "FICHES : vraie boîte de dialogue (le focus va dans la fiche, le fond est inerte, le focus revient au bouton d'origine à la fermeture).",
    "CHIFFRES À LA FRANÇAISE : km et ACWR du Cockpit avec une virgule ; effort de la semaine identique à la fiche, masqué s'il manque (plus de « undefined »).",
    "ACCESSIBILITÉ : onglets du Cockpit complets (panneaux, flèches du clavier), cibles tactiles de 44 px, croix de l'aide nommée ; Échap ferme le Rewind de semaine ; dernier emoji d'interface retiré."]},
  {"build":279,"date":"29 octobre 2026","sha":"","tag":"Blanc et orange (8/8) : panneaux et finitions","items":[
    "PANNEAUX : météo, records de la saison, versions, aides du Cockpit, théorie, menu et log rapide aux jetons ; croix de fermeture rétablies ; icônes météo au trait.",
    "PLUS D'EMOJI dans l'interface (trophées et cadenas au trait, chips météo « vent » et « pluie », menus) ; les textes du coach gardent les leurs.",
    "COULEURS : plus de violet, de lime ni de bleu (projection marathon, boîte du coach, lecture vocale, calendrier, zones cardiaques en rampe orange, accents des courses).",
    "Aides du Cockpit sans noms de couleurs périmés ; code mort de l'ancien Accueil retiré."]},
  {"build":278,"date":"29 octobre 2026","sha":"","tag":"Blanc et orange (7/8) : Courses, dossiers et Rewinds de semaine","items":[
    "COURSES : titre de la vue, « Ta saison en chiffres », courses à venir (J-N, dossier de course), courses passées (totaux en grand, temps et allure, puces, chaussures, bilan à déplier) ; plus de liseré de couleur ni d'emoji.",
    "DOSSIER DE COURSE : sections blanches comme la fiche (chiffres, profil, déroulé, plan d'exécution, nutrition, zones, terrain, erreurs, checklist J-7), un seul accent orange.",
    "REWIND DE SEMAINE et SAISON EN CHIFFRES sur fond blanc, icônes au trait, bouton « Terminer » orange."]},
  {"build":277,"date":"29 octobre 2026","sha":"","tag":"Blanc et orange (6/8) : Cockpit","items":[
    "COCKPIT : titre et quatre onglets (Aujourd'hui, Progression, Records, Analyse).",
    "AUJOURD'HUI comme la maquette : forme du jour en grand anneau et ses quatre indicateurs, carte Charge (ACWR du jour, zone et repère sur la barre), VO2max estimée, les N dernières semaines (distance, effort relatif, cadence et kilomètres par semaine sur 12 semaines), dernière sortie analysée.",
    "PROGRESSION : « Où j'en suis » en ligne (5 courbes, verdict et mini-courbe, détail à un toucher), profil de coureur affiché d'emblée en clair (plus de sceau ni d'animation en boucle), progression par saison en orange.",
    "RECORDS : 5 km, 10 km et semi, meilleurs temps 2026, et les records de la saison à un toucher. ANALYSE : les graphes et le tableau de bord, groupes avec icônes au trait.",
    "Plus d'emoji dans le Cockpit ; valeurs en virgule décimale."]},
  {"build":276,"date":"29 octobre 2026","sha":"","tag":"Blanc et orange (5/8) : Séances et fiches","items":[
    "SÉANCES : titre de la vue, phases sans pastille de couleur, semaines en cartes blanches (volume en grand, progression des séances en orange, semaine en cours entourée).",
    "FICHE DE LA SEMAINE : chiffres (volume prévu, réalisé, séances faites), objectif, séances en liste avec le jour, bilan du coach ; « Revoir la semaine ».",
    "FICHE D'UNE SÉANCE À FAIRE : même grammaire que la fiche faite : chiffres prévus, chaussure conseillée, « Télécharger pour la montre », objectif, déroulé et frise, conseils du coach, nutrition, le réalisé à logger ; l'analyse du coach s'affiche aussi pour une séance sautée.",
    "Revues du coach en texte simple ; records de la séance sobres ; lecture vocale, théorie et bouton « Semaine en cours » sans emoji."]},
  {"build":275,"date":"29 octobre 2026","sha":"","tag":"Blanc et orange (4/4) : Rewind de séance sur fond blanc","items":[
    "REWIND DE SÉANCE : fond blanc, encre noire, orange seul accent, ocre pour le dépassement de cible ; barre de progression orange.",
    "IMAGE 1 : le titre et sa note séparés, la distance en très grand, les six chiffres en deux colonnes sans cadres, « Aller à l'analyse du coach » en bouton.",
    "TRACÉ : plus le trait est foncé, plus tu allais vite ; départ en rond creux, arrivée en point plein. L'ancien replay des sorties d'avant le Rewind passe aussi au blanc."]},
  {"build":274,"date":"28 octobre 2026","sha":"","tag":"Blanc et orange (3/4) : fiche de séance","items":[
    "FICHE D'UNE SÉANCE FAITE : le réalisé d'abord (chiffres en grille, chaussure, « Revoir ma séance »), puis l'analyse du coach : prévu face au réalisé calculé, verdict, ce qui est bien, à corriger, pour la suite, revue complète à un toucher.",
    "FICHE : le tracé coloré selon l'allure (plus foncé, plus rapide), l'allure km par km sur la bande grise de la cible, le cœur avec le temps par zone et la dérive, puis la séance prévue.",
    "Rampe d'allure orange, du plus lent (clair) au plus rapide (foncé) ; plus d'emoji dans le formulaire du réalisé."]},
  {"build":273,"date":"28 octobre 2026","sha":"","tag":"Blanc et orange (2/4) : Accueil et barre d'onglets","items":[
    "ACCUEIL : l'analyse du coach sur ta dernière séance en tête (chiffres, verdict, prévu face au réalisé, « Lire l'analyse » et « Revoir »), puis la prochaine séance, la météo, la forme du jour, la semaine en cours jour par jour, les courses et ton année.",
    "ACCUEIL : cartes blanches sans ombre, chiffres en Barlow, icônes au trait à la place des emojis ; le compteur de records est retiré.",
    "BARRE D'ONGLETS : givrée, onglet actif en orange."]},
  {"build":272,"date":"28 octobre 2026","sha":"","tag":"Blanc et orange (1/4) : couleurs et police des chiffres","items":[
    "COULEURS : l'orange remplace le teal dans toute l'app (orange vif pour les aplats et les graphes, orange encre pour le petit texte) ; neutres gris sans bleu ; l'ocre remplace l'ambre pour la vigilance.",
    "CHIFFRES : police Barlow Semi Condensed, embarquée dans l'app (disponible hors ligne) ; plus de serif Georgia.",
    "DESIGN.md et PRODUCT.md réécrits pour la direction blanc et orange."]},
  {"build":271,"date":"28 octobre 2026","sha":"","tag":"Log S44 seance 3 : Footing avec Yannis (lignes droites non faites) du 28/10","items":[
    "SEANCE : S44 seance 3 loggee depuis Strava : Footing avec Yannis (lignes droites non faites), 11,03 km en 1:05:17 (5:55/km), FC 148/163, D+ 42 m, 15 °C, Gel Pulse 16.",
    "CHAUSSURES : Gel Pulse 16 a 240 km."]},
  {"build":270,"date":"28 octobre 2026","sha":"","tag":"Rewind de séance : correctifs","items":[
    "FICHE : le bouton « Revoir ma séance » est en haut de la fiche.",
    "ANALYSE DU COACH : tout le contenu s'affiche d'emblée et défile sur iPhone (plus rien de coupé sous le prévu face au réalisé)."]},
  {"build":269,"date":"28 octobre 2026","sha":"","tag":"P4 Rewind de séance","items":[
    "REWIND DE SÉANCE : bouton « Revoir ma séance » dans la fiche ; 9 images plein écran (chiffres, tracé et relief colorés par l'allure, allure km par km, cœur sur tes zones, discipline d'allure et série en cours, moment fort, analyse du coach terrain, progression), défilement automatique, l'analyse du coach attend « Continuer ».",
    "ANALYSE DU COACH : prévu face au réalisé calculé (distance, allure, FC), verdict, ce qui est bien, à corriger et conseil repris de la revue, revue complète à un toucher.",
    "OÙ J'EN SUIS : 5 courbes à verdict calculé (allure facile, efficacité à 145 bpm, dérive des sorties longues, discipline d'allure, volume et charge), depuis la fin du Rewind et le Cockpit.",
    "ACCUEIL : annonce « Le coach a analysé ta séance », une fois par séance. Rewind disponible pour S44-2 et S43-8 ; les prochaines séances l'auront à chaque log."]},
  {"build":268,"date":"27 octobre 2026","sha":"","tag":"P3 Système de mouvement","items":[
    "ONGLETS : transition de vue depuis la barre (fondu et glissement de 8 px dans le sens de la barre, barre et en-tête immobiles) ; sans transition de vue (iOS < 18), même mouvement en CSS.",
    "FICHES : la carte de séance ou de semaine s'agrandit jusqu'à devenir sa fiche et s'y referme au retour.",
    "SCROLL : les cartes apparaissent en CSS (Safari 26) à la place du script ; la barre d'onglets se rétracte quand on descend et revient quand on remonte.",
    "GRAPHES : les courbes du Cockpit se tracent et les barres montent à leur première apparition ; le profil de course se dessine au fil du scroll.",
    "CHIFFRES : forme, ACWR et J-N comptent jusqu'à leur valeur à leur première apparition.",
    "CÉLÉBRATIONS : une coche ou un trait qui se dessine ; plus de confettis ni de rebond.",
    "TOUCHER : retour visuel seul ; tout le code de vibration est retiré (l'iPhone ne vibre pas pour une web app).",
    "CORRECTION : la légende du profil de Nice annonçait « sommet 897 m vers le km 15 » (valeurs d'un trail) ; elle est calculée depuis le profil, avec des graduations jusqu'au km 40.",
    "DURÉES : 120, 240 et 360 ms, décélération exponentielle ; tout est coupé sous « réduire les animations »."]},
  {"build":267,"date":"27 octobre 2026","sha":"","tag":"P2 Pipeline de log : textes chargés à l'ouverture d'une fiche","items":[
    "CHARGEMENT : les revues de séance et de semaine, les splits et les diapositives des Rewinds ne sont plus lus au démarrage : data/textes.json est chargé à la première ouverture d'une fiche ou d'un Rewind (et mis en cache hors-ligne par le service worker).",
    "POIDS : premier chargement de 336 à 261 Ko compressés (−22 %).",
    "AUCUN CHANGEMENT VISIBLE : captures des 4 vues identiques au pixel près."]},
  {"build":266,"date":"27 octobre 2026","sha":"","tag":"P2 Pipeline de log : nouveau circuit documenté et mesuré","items":[
    "DOC : docs/ENRICHISSEMENT.md décrit le nouveau circuit (Strava → fichier d'entrée → scripts/log_seance.py → revue → build).",
    "MESURE : la même séance (footing du 27/10) coûte 19 400 tokens au lieu de 25 400 (−24 %) et 12 actions au lieu de 19 ; sans découplage, environ −45 %.",
    "SÉCURITÉ : le script ne compte plus deux fois une sortie déjà présente dans la référence Strava."]},
  {"build":265,"date":"27 octobre 2026","sha":"","tag":"P2 Pipeline de log (2/3) : script Strava vers log de séance","items":[
    "LOG : scripts/log_seance.py transforme les réponses Strava (recopiées en fichier) en log de séance : splits, segments, température, chaussure, dénivelé, terrain route ou trail, découplage. Il met aussi à jour la référence Strava, GEAR et le CHANGELOG.",
    "LOGS : les nouvelles séances loggées vivent dans src/logs/ (un fichier par séance), chargées par gen.py ; les séances déjà loggées restent dans gen.py.",
    "TESTS : le script retrouve à l'identique les valeurs de trois séances loggées à la main (footing du 27/10 avec découplage, allure marathon du 21/10, trail du 24/10).",
    "AUCUN CHANGEMENT VISIBLE."]},
  {"build":264,"date":"27 octobre 2026","sha":"","tag":"P2 Pipeline de log (1/3) : textes hors de gen.py","items":[
    "TEXTES : les 88 revues de séance, 17 revues de semaine et 18 Rewinds quittent gen.py pour src/textes/ (un fichier par séance, par semaine ou par Rewind). gen.py passe de 800 à 555 Ko.",
    "AUCUN CHANGEMENT VISIBLE : les fichiers publiés sont identiques à l'octet près à ceux du build 263."]},
  {"build":263,"date":"27 octobre 2026","sha":"","tag":"Log S44 séance 2 : footing du 27/10 (seuil remplacé)","items":[
    "SÉANCE : S44 séance 2 loggée depuis Strava : footing de 10,04 km en 58:30 (5:50/km), FC 146/165, D+ 31 m, 18 °C, Clifton 10. Le seuil conditionnel a été remplacé par un footing facile.",
    "CHAUSSURES : Clifton 10 à 1284 km."]},
  {"build":262,"date":"27 octobre 2026","sha":"","tag":"P1 Données justes (2/2) : tendances, efficience, projection unique, fraîcheur du Cockpit, Z2 unique","items":[
    "COCKPIT : les pourcentages de tendance des tuiles (km, effort, cadence) comparent les N dernières semaines complètes aux N précédentes ; une semaine sans course compte pour 0, la semaine en cours est exclue (8 semaines : -13 % de volume, +1 % d'effort).",
    "EFFICIENCE : les sorties à fort dénivelé (15 m/km ou plus), en course-marche ou à allure de marche n'entrent plus dans le calcul ; le message de recul n'invoque la chaleur qu'en saison chaude.",
    "PROGRESSION PAR SAISON : la carte n'affiche plus « plus rapide depuis l'hiver » quand le gain n'existe pas (automne comparable à février) ; elle reprend la note de la donnée.",
    "ACCLIMATATION CHALEUR : carte masquée hors saison chaude (octobre à mai).",
    "PERFORMANCES : le semi Run In Lyon 2026 (1h52:30, couru malade) est la référence de course ; la colonne « Projeté aujourd'hui », les allures de course et le marathon projeté (accueil, objectifs) viennent tous de la même projection en direct (~3h41 aujourd'hui).",
    "VOCABULAIRE : « 2026 en chiffres » (depuis le 1er janvier) distinct de « ta saison en chiffres » (depuis la S24) ; le total de km en 2026 vient d'une seule source (2 266 km).",
    "JOURS DE REPOS : un repos facultatif passé sans sortie ce jour-là est clos automatiquement (22/07 et 08/08).",
    "FRAÎCHEUR : chaque carte du Cockpit affiche sa source et « à jour au … » (en orange au-delà de 14 jours) ; le preflight avertit au-delà de 14 jours et refuse les codes \\u00e9 visibles et les mots français sans accent dans les textes affichés.",
    "ZONE Z2 UNIQUE : 134-154 bpm partout, footings prescrits à FC ≤ 150 (l'ancien plafond de 144 est retiré de l'app et de CLAUDE.md).",
    "RUN IN LYON : mention « à recouper » remplacée par ce que Strava confirme (1:53:29 pour 21,30 km GPS, soit 1:52:30 ramené à 21,1 km).",
  ]},
  {"build":261,"date":"27 octobre 2026","sha":"","tag":"P1 Données justes (1/2) : dérive cardiaque recalculée, Rewinds S36-S43, textes corrigés, efficience d'automne","items":[
    "DÉRIVE CARDIAQUE : recalculée avec les flux Strava sur les six dernières sorties faciles ou longues (procédure decoup-v1) : 2 fiables (longue du 09/10 à 6,8 %, footing du 17/10 à -1,9 %), 2 incertaines (05/10, 14/10), 2 non représentatives (changement d'allure volontaire : 13/10, 15/10). Seules les fiables sont utilisées.",
    "TEMPÉRATURE : la température Strava est enregistrée avec chaque sortie recalculée (realise.temp), pour la correction thermique de l'efficience.",
    "REWINDS : S36, S39, S40, S41, S42 et S43 créés (chiffres mesurés). S37 et S38 n'ont aucune course : pas de Rewind.",
    "EFFICIENCE : point d'automne ajouté (352 s/km à 145 bpm) ; la conclusion 'plus rapide depuis l'hiver' est retirée : l'automne est comparable à février (347 s/km).",
    "TEXTES : codes \\u00e9 visibles dans les revues S31, S33, S35 corrigés ; revue S34, interprétation de l'ACWR et séances non faites des S42-S43 remises avec leurs accents.",
    "OUTILS : le bouton du Rewind passe à 44 px de haut (cible tactile, l'audit d'accessibilité échouait dès qu'un Rewind existe pour la semaine) ; test_build.py dérive ses dates de BUILT_ON au lieu d'une date figée (le test échouait depuis le log du 25/10).",
    "ALLURES : l'allure marathon est datée du bloc de 14 km du 15/10 (5:11/km en déplacement, FC 161) ; mention 'à recaler après le test 10 km (S31)' retirée de la vigilance.",
  ]},
  {"build":260,"date":"27 octobre 2026","sha":"","tag":"P0 avant Nice : dossier Nice recalé (chaussures, zones de FC, lièvre) et trail du 24/10 reclassé","items":[
    "DOSSIER NICE : chaussures Novablast 5 V (rodées sur les 30 km du 15/10) au lieu des Clifton 10 (1 274 km).",
    "DOSSIER NICE : zones de FC recalées sur ta FC mesurée à allure marathon (159-161) : zone 152-163, dérive 163-167, danger au-dessus de 167 (avant : 134-152, 152-162, 162).",
    "DOSSIER NICE : lièvre 3h45 suivi jusqu'au km 35-36, la stratégie décidée en S34 (avant : km 30).",
    "DOSSIER NICE : enseignements du test nutrition du 15/10 ajoutés (3e gel difficile, environ 1,5 L bu, gels caféinés à tester le 01/11).",
    "SÉANCE : trail de l'Estérel du 24/10 classé en trail : il sort du calcul d'efficience route de la S43.",
    "SÉANCE : footing du lundi 26/10 passé en non fait (aucune activité Strava ce jour-là).",
    "COCKPIT : la tuile ACWR affiche l'ACWR du jour (0,74), comme le résumé et la carte Charge ; elle affichait la dernière semaine complète (0,67).",
  ]},
  {"build":259,"date":"25 octobre 2026","sha":"","tag":"S44 : consignes d'affutage ajustees (seuil conditionnel, D+ leger, longue plate)","items":[
    "PLAN : S44 (affutage) ajustee : footings a FC 145 maximum avec D+ leger toleré jusqu'a mercredi, seuil 30 du mardi conditionnel (4:40-4:45/km, arret apres 2 blocs, ceinture) comme derniere seance d'intensite, longue du 01/11 plate avec 4 km a 5:17-5:23 derriere le meneur 3h45.",
    "PLAN : les semaines 47 et 48 (trail et sortie nocturne avant la SaintExpress) sont deja en place apres Nice ; aucune modification.",
  ]},
  {"build":258,"date":"25 octobre 2026","sha":"","tag":"S43-7/8 : sortie progressive 9,7 km a 5:07/km + course-marche avec Perrine","items":[
    "SEANCE : sortie du dimanche matin non planifiee : 9,70 km en 49:36, 5:07/km (de 5:11 a 4:56), FC 151 moy / 164 max, D+ 27 m, effort relatif 87, Novablast 5 J ; le lendemain du trail de l'Esterel.",
    "SEANCE : sortie chill avec Perrine : 3,79 km en 32:41, course-marche 2 min / 1 min, FC 122 moy, effort relatif 9.",
    "ANALYSE : jambes libres après le trail (charge de descente sans conséquence visible), mais allure 13 s/km sous la cible marathon et final en accélération ; consigne pour Nice : rester derriere le meneur au km 5.",
    "SEMAINE : revue de la S43 mise a jour : 5 sorties, 54,6 km, charge 496, verdict B+.",
    "CHAUSSURES : Novablast 5 J 863 -> 877 km (Strava).",
    "A VALIDER : les RPE 5 et 2 sont des estimations de Claude, a ajuster par Loic ; la FC est a prendre avec reserve si la ceinture n'etait pas portee.",
  ]},
  {"build":257,"date":"25 octobre 2026","sha":"","tag":"S43-4 : trail Esterel 20 km, D+ 642 m, FC 142 (longue avancee)","items":[
    "SEANCE : trail de 20,03 km dans l'Esterel avec ton beau-pere, samedi 24/10, a la place de la longue du 25/10 : 2:23:13 en deplacement (2:49:36 ecoulees), 7:09/km, FC 142 moy / 181 max, D+ 642 m, effort relatif 158.",
    "ANALYSE : endurance cardiaque dans la fenetre (km 1-12 a FC 137), fin plus engagee (km 13-20 a FC 151, pic 181 au km 18) et charge de descente a surveiller a 15 jours de Nice.",
    "SEMAINE : revue de la S43 ajoutee : 3 sorties, 41,1 km, charge 400, verdict B+.",
    "CHAUSSURES : Novablast 5 J 843 -> 863 km (Strava ; a corriger si c'etaient les Cascadia 19).",
    "A VALIDER : le RPE 5 est une estimation de Claude, a ajuster par Loic.",
  ]},
  {"build":256,"date":"22 octobre 2026","sha":"","tag":"S43-6 : sortie au feeling allure marathon 10 km a 5:08/km, FC 158","items":[
    "SEANCE : sortie du soir non planifiee dans le sud (Frejus - Saint-Raphael) : 10,02 km en 51:32 de deplacement, 5:08/km, FC 158 moy / 172 max, D+ 28 m, effort relatif 120, Novablast 5 J.",
    "ANALYSE : cardio dans la fenetre marathon mais allure 12 s/km sous la cible, irreguliere (3 min 51 s d'arrets, relances a 4:45 et 4:59). Plus de seance qualite avant Nice.",
    "PLAN : renforcement du 22/10 passe en non realise (jour de voyage), sans rattrapage.",
    "CHAUSSURES : Novablast 5 J 833 -> 843 km (Strava).",
    "A VALIDER : le RPE 6 est une estimation de Claude, a ajuster par Loic ; la FC est a prendre avec reserve si la ceinture n'etait pas portee.",
  ]},
  {"build":255,"date":"21 octobre 2026","sha":"","tag":"S43-2 : analyse ajustee (FC montre seule, ressenti de fatigue)","items":[
    "ANALYSE : la FC de la sortie du 21/10 vient de la montre seule (sans ceinture) : la comparaison de FC avec le 12/10 et le calcul de derive sont signales comme a prendre avec reserve ; l'allure reguliere reste la mesure fiable.",
    "RESSENTI : fatigue plus marquee que d'habitude apres la longue de 30 km ; la pause de dimanche a mardi a fait du bien (physique et mental). Ajoute aux revues de la seance du 21/10 et de la S42.",
  ]},
  {"build":254,"date":"21 octobre 2026","sha":"","tag":"S43-2 : allure marathon 11 km a 5:14/km, FC 156 (decalee a mercredi)","items":[
    "SEANCE : allure marathon du mardi 20/10 (2x6 km, annulee par la pluie) realisee le mercredi 21/10 en 11 km continus : 11,01 km en 57:35, 5:14/km, FC 156 moy / 167 max, D+ 30 m, effort relatif 122, Clifton 10.",
    "ANALYSE : tres reguliere (5:05 a 5:22, pas de finish emballe) ; FC mesuree a la montre seule (sans ceinture), donc a prendre avec reserve.",
    "PLAN : footing du 19/10 (pluie) et footing + lignes droites du 21/10 (remplace par l'allure marathon) passes en non realises, sans rattrapage.",
    "SEMAINE : revue de la S42 (pic) ajoutee : 5 sorties, 79,3 km, charge 871, verdict B+.",
    "CHAUSSURES : Clifton 10 1263 -> 1274 km (Strava).",
    "RESSENTI : fatigue plus marquee que d'habitude apres la longue de 30 km, pause volontaire dimanche puis pluie lundi et mardi : le repos a fait du bien (physique et mental). Ajoute a la revue.",
    "A VALIDER : le RPE 6 est une estimation de Claude, a ajuster par Loic.",
  ]},
  {"build":253,"date":"17 octobre 2026","sha":"","tag":"S42-7 : footing de recuperation 11,14 km a 6:07/km, FC 137","items":[
    "SEANCE : footing de recuperation non planifie du 17/10, 2 jours apres la longue : 11,14 km en 1:08:04, 6:07/km, FC 137 moy / 176 max (pic isole), D+ 26 m, effort relatif 49, Clifton 10.",
    "ANALYSE : 4 premiers km trop vifs (5:51, FC 143) puis 6:17 a FC 134 ; a allure egale la FC est 8 battements sous le footing de recuperation du 05/10 : le cardio a recupere.",
    "CHAUSSURES : Clifton 10 1252 -> 1263 km (Strava).",
    "A VALIDER : le RPE 3 est une estimation de Claude, a ajuster par Loic.",
  ]},
  {"build":252,"date":"15 octobre 2026","sha":"","tag":"Ton capital : toute la saison depuis le 1er janvier","items":[
    "CORRIGE : 'Ton capital' ne comptait que depuis le debut de la prepa (15 juin : 830 km, 63 sorties). Il couvre maintenant l'annee depuis le 1er janvier : 2201 km, 172 sorties, 22185 m de D+ (SAISON2026, verifie sur Strava).",
    "AJOUTE : records Strava du 1er janvier au 14 juin (1537, releves sur Strava) ajoutes aux records du plan : total 1972. La fiche Records suit et liste aussi les meilleures seances d'avant la prepa.",
    "CORRIGE : le recit etait fige sur 'Lyon -> Barcelone' (532 km) ; jalons ajoutes jusqu'a Le Caire (Munich, Rome, Madrid, Berlin, Lisbonne, Athenes, Istanbul, Helsinki, Moscou, Reykjavik). A 2201 km : Helsinki, prochain Moscou.",
    "CORRIGE : la phrase 'Plus que X km pour l'aller-retour' s'affichait quel que soit le jalon suivant ; elle nomme maintenant la destination. Le compteur de semaines devient un compteur de sorties.",
    "VERIFIE : debugCockpit() controle ces chiffres (km, sorties, records, Everest) contre les donnees.",
  ]},
  {"build":251,"date":"15 octobre 2026","sha":"","tag":"Audit du Cockpit : graphe d'allure par type corrige, allure facile fiabilisee, debugCockpit()","items":[
    "AUDIT : volume, charge, D+, cadence, ACWR (hebdo et du jour), zones FC et fatigue recalcules a part depuis les donnees brutes : tous concordent avec l'ecran.",
    "CORRIGE : le graphe d'allure par type (EF / AM / Seuil) affichait des donnees de S15-S26 sous les etiquettes S31-S42 ; il est recalcule semaine par semaine.",
    "CORRIGE : l'allure facile (Z2) et l'efficience ne retiennent plus que les seances a FC moyenne <= 154 ; S42 passait a 5:14 a cause de deux seances courues a allure marathon (5:54 reel).",
    "AJOUTE : debugCockpit() dans la console (recalcul independant, ecarts, donnees perimees) et test T20 de regression.",
    "CONNU : le decouplage cardiaque n'a plus ete calcule depuis le 06/08 ; la carte 'Derniere sortie analysee' est perimee.",
  ]},
  {"build":250,"date":"15 octobre 2026","sha":"","tag":"S42-4 : nutrition de la longue notee","items":[
    "DONNEE : nutrition de la longue du 15/10 ajoutee : 3 gels (45 min, 1h30, 2h15, le 3e difficile), 1 electrolyte Fort Endurance au depart, environ 1,5 L, petit-dejeuner banane/proteines/cafe 1h30 avant.",
    "ANALYSE : en dessous de la cible 60-90 g de glucides/h et de la consigne de boire toutes les 15-20 min ; a travailler avant Nice (gel supporte au-dela de 2h).",
  ]},
  {"build":249,"date":"15 octobre 2026","sha":"","tag":"S42-4 : RPE corrige a 6","items":[
    "DONNEE : RPE ressenti de la longue du 15/10 corrige de 7 (estimation) a 6 (ressenti de Loic).",
  ]},
  {"build":248,"date":"15 octobre 2026","sha":"","tag":"S42-4 : longue 30 km dont 15 a allure marathon, 5:20 ecoule, FC 161","items":[
    "SEANCE : S42-4 du 15/10 (longue avancee de 3 jours), 30,06 km en 2:41:56, FC 155 moy / 171 max, D+ 74 m, effort relatif 342, Novablast 5 V.",
    "ANALYSE : 15 km faciles a 5:35 (FC 148) puis 15 km AM a 5:20 ecoule (5:11 en deplacement, FC 161,5) ; rapport vitesse/FC -3 %, pas de decouplage net ; amie du km 8 au km 30.",
    "CHAUSSURES : Novablast 5 V 172 -> 202 km (Strava).",
    "A VALIDER : le RPE 7 est une estimation de Claude, a ajuster par Loic.",
  ]},
  {"build":247,"date":"14 octobre 2026","sha":"","tag":"S42-3 : vallonne avec Yannis, 13,04 km a 5:54/km, FC 151","items":[
    "SEANCE : S42-3 du 14/10, footing facile prevu (11 km) remplace par un vallonne de 13,04 km en 1:17:01, 5:54/km, FC 151 moy / 182 max, D+ 185 m, effort relatif 137, Clifton 10.",
    "ANALYSE : km 1-4 a 5:53 (FC 142-146) dans le cadre ; montee du Signal a 6:09-6:42 (FC 154-164, pic 182) ; descentes a 144-147 ; 480 de charge sur les 3 derniers jours.",
    "CHAUSSURES : Clifton 10 1239 -> 1252 km (Strava).",
    "A VALIDER : le RPE 5 est une estimation de Claude, a ajuster par Loic.",
  ]},
  {"build":246,"date":"14 octobre 2026","sha":"","tag":"S42-2 : vallonne du 13/10 avec 6 km finaux a 4:52, 5:14/km, FC 161","items":[
    "SEANCE : S42-2 du 13/10, footing + lignes droites prevu (12 km) remplace par un vallonne de 15,04 km en 1:18:49, 5:14/km, FC 161 moy / 178 max, D+ 165 m, effort relatif 206, Novablast 5 J.",
    "ANALYSE : montee du Chemin Neuf a 6:27 et 6:09 (FC 163-169, pic 178) ; 6 derniers km a 4:52 de moyenne, FC 163-167, soit un tempo de 28 s/km plus vite que l'allure marathon ; 343 de charge en 48 h avec le 12/10.",
    "CHAUSSURES : Novablast 5 J 818 -> 833 km (Strava).",
    "A VALIDER : le RPE 7 est une estimation de Claude, a ajuster par Loic.",
  ]},
  {"build":245,"date":"12 octobre 2026","sha":"","tag":"S42-1 : footing remplace par 10 km a allure marathon, 5:11/km, FC 161","items":[
    "SEANCE : S42-1 du 12/10, footing facile prevu (12 km) remplace par 10,05 km a allure marathon en 52:07, 5:11/km, FC 161 moy / 177 max, D+ 26 m, effort relatif 137, Clifton 10.",
    "ANALYSE : km 3 a 6 a 5:16-5:22 (cible 5:20) ; depart a 5:07-5:14 et finish a 4:52 ; cinq derniers km a 5:07 contre 5:15 pour les cinq premiers, FC 159 -> 163.",
    "CHAUSSURES : Clifton 10 1229 -> 1239 km (Strava).",
    "A VALIDER : le RPE 6 est une estimation de Claude, a ajuster par Loic.",
    "REVUE : revue de semaine S41 ajoutee (elle manquait, le controle B1 de audit_data la reclamait).",
  ]},
  {"build":244,"date":"9 octobre 2026","sha":"","tag":"S41-4 : longue avancee au vendredi, 30,13 km a 5:39/km, FC 149","items":[
    "SEANCE : sortie longue S41-4 deplacee du dimanche 11/10 au vendredi 09/10 (week-end indisponible), 30,13 km en 2:50:14, 5:39/km, FC 149 moy / 167 max, D+ 100 m, effort relatif 281, Novablast 5 J.",
    "ANALYSE : allure constante par tranche de 10 km (5:40, 5:40, 5:37) avec derive de FC de +7 bpm ; allure 11 s/km au-dessus de la borne rapide du plan (5:50-6:25) ; 7 arrets pour 6 min 24 s.",
    "CHAUSSURES : Novablast 5 J 788 -> 818 km (Strava).",
    "A VALIDER : le RPE 5 est une estimation de Claude, a ajuster par Loic.",
    "SEANCE : renforcement PPG du 08/10 marque non realise (journee de repos indiquee par Loic).",
    "CORRECTIF : fleche des seances non realisees en --warn-deux (contraste 1,93:1 -> 4,9:1), detecte par l audit d accessibilite.",
  ]},
  {"build":243,"date":"8 octobre 2026","sha":"","tag":"CLAUDE.md : estimations en points de la limite de session","items":[
    "DOCUMENTATION : les estimations et comptes rendus sont exprimes en points de la limite de session de 5 heures (celle affichee a l ecran), et non en part de la fenetre de contexte."
  ]},
  {"build":242,"date":"8 octobre 2026","sha":"","tag":"Mode sombre retire : l app reste toujours blanche","items":[
    "MODE SOMBRE RETIRE (demande de Loic, il n apportait rien) : environ 170 regles CSS, le demarrage qui suivait le reglage du telephone, la couleur de barre sombre, les tests, l audit et les captures sombres. Un iPhone regle en sombre n a plus aucun effet sur l app.",
    "TEST : T18 verifie que l app reste blanche meme avec un telephone en mode sombre."
  ]},
  {"build":241,"date":"8 octobre 2026","sha":"","tag":"CLAUDE.md : estimation a chaque demande, compte rendu de derive, astuces tokens","items":[
    "DOCUMENTATION : CLAUDE.md demande une estimation a chaque demande, un compte rendu estime contre reel apres chaque livraison, des regles pour ne pas depenser de tokens inutilement et des astuces pour Loic."
  ]},
  {"build":240,"date":"8 octobre 2026","sha":"","tag":"CLAUDE.md : preference d estimation d effort","items":[
    "DOCUMENTATION : CLAUDE.md demande, avant toute tache importante, une estimation par etape (tokens et part en pour cent), l etat des limites du plan et une recommandation."
  ]},
  {"build":239,"date":"8 octobre 2026","sha":"","tag":"Journal des decisions de la refonte","items":[
    "DOCUMENTATION : docs/REFONTE-DECISIONS.md conserve le registre des arbitrages de la refonte (ecarts au plan, couts, points mineurs laisses, actions en attente)."
  ]},
  {"build":238,"date":"8 octobre 2026","sha":"","tag":"Corrections de la relecture finale : mode sombre des fiches, fusion automatique plus sure, build qui doit augmenter","items":[
    "MODE SOMBRE : texte illisible corrige sur la pastille Partiel, les boutons Terminer et Rejouer, l alerte chaleur, les tableaux des fiches, les boutons de fiche ; l audit d accessibilite couvre desormais les feuilles de semaine, les fiches de seance et les composants rares en clair et en sombre.",
    "ACCESSIBILITE DES FICHES : contrastes, cibles de 44 px, texte courant a 13 px, niveau de titre des sections Prevu et Realise.",
    "FUSION AUTOMATIQUE : un fichier renomme vers data/ ne passe plus pour une modification de donnees (git diff sans detection de renommage). Chaque PR doit augmenter le numero de build (check_build_increment dans le job verify).",
    "TESTS : semaine ISO a la fin de l annee (31 decembre, 1er et 4 janvier 2027)."
  ]},
  {"build":237,"date":"8 octobre 2026","sha":"","tag":"Finition de la refonte : mouvement sans rebond, documentation et audit final","items":[
    "MOUVEMENT : les 9 courbes d easing a rebond (overshoot) sont remplacees par une decelaration exponentielle ; les animations infinies restent coupees sous prefers-reduced-motion.",
    "DOCUMENTATION : DESIGN.md synchronise avec les jetons finaux (texte, vert, page, mode sombre, mouvement) ; docs/AUDIT-2026-10.md compare l audit avant et apres (11/20 puis 15/20)."
  ]},
  {"build":236,"date":"8 octobre 2026","sha":"","tag":"Mode sombre qui suit le reglage du telephone","items":[
    "MODE SOMBRE : l app suit le reglage iOS (clair ou sombre), en direct et des l ecran de chargement. Memes teintes de marque ; surfaces, neutres de texte et variantes de texte redefinis par jetons (--bg-page, --bg-card, --bord-card).",
    "REPARATION : l ancien mode nuit, inactif depuis la disparition de son bouton, laissait des cartes blanches avec du texte clair ; surfaces et degrades pastel reconstruits.",
    "CONTROLE : audit_a11y.py --dark verifie les contrastes en mode sombre ; captures de reference claires et sombres."
  ]},
  {"build":235,"date":"8 octobre 2026","sha":"","tag":"Coherence des chiffres, jauge VO2max stable, couleurs ramenees aux jetons","items":[
    "COMPTEUR DE SORTIES : l accueil et Courses affichaient 58 et 59 pour la meme chose (une seance de PPG sans kilometrage etait comptee d un cote seulement). Meme definition partout, et libelle precis : sorties du plan.",
    "JAUGE VO2MAX : la valeur s affiche d emblee, seul l arc s anime ; plus de passage par 0 sur un chiffre de sante.",
    "COULEURS : 585 couleurs hexadecimales hors jetons ramenees a 278 (-52 pour cent) ; un controle (audit_tokens) interdit toute hausse. Remplacement par propriete (texte et fonds ont des jetons differents), regles du mode nuit preservees.",
    "DONNEES VIDES : test qui charge l app sans aucune seance realisee ni palmares et verifie l absence de NaN, undefined et d erreur JavaScript sur les 4 vues."
  ]},
  {"build":234,"date":"8 octobre 2026","sha":"","tag":"Accessibilite : titres, reperes, clavier, cibles tactiles, texte lisible, contrastes","items":[
    "STRUCTURE : un titre h1 par vue, repere main et lien d evitement fonctionnel, phases et semaines en vrais titres (h2/h3) ; les elements cliquables non natifs sont atteignables au clavier (tabindex, role button, Entree et Espace).",
    "LISIBILITE : plus aucun texte sous 12 px (les 19 tailles inferieures sont ramenees au jeton --t-data), texte courant a 13 px minimum.",
    "CONTRASTES AA : texte en variantes profondes (--texte-trois, --primary-deux, --ok-deux, --danger-deux) ; cibles tactiles de 44 px (calendrier, filtres, bascules, aide VO2max).",
    "AUDIT : scripts/audit_a11y.py (sans dependance) rejoue 9 regles sur les 4 vues et tourne dans le job verify."
  ]},
  {"build":233,"date":"8 octobre 2026","sha":"","tag":"Contrat d enrichissement : un seul fichier de reference Strava, documentation a jour","items":[
    "ENRICHISSEMENT : docs/ENRICHISSEMENT.md decrit le circuit complet (Strava, gen.py, build, branche, PR, fusion) pour le projet Claude ; CLAUDE.md, TECHNICAL.md et src/README.md mis a jour.",
    "REFERENTIEL STRAVA : les valeurs de reference des audits (activites, chaussures, mois) vivent dans src/strava_reference.json au lieu d etre recopiees dans deux scripts ; une seance loggee ne modifie plus le code des audits."
  ]},
  {"build":232,"date":"8 octobre 2026","sha":"","tag":"Build reproductible et verification automatique GitHub","items":[
    "BUILD REPRODUCTIBLE : gen.py calculait l ACWR a la date du jour ; la date de build est maintenant enregistree dans data/meta.json (BUILT_ON) et rejouee par build.py --check, qui ne casse donc plus le lendemain.",
    "VERIFICATION AUTOMATIQUE : un workflow GitHub (verify) rejoue le build, le preflight, la validation des donnees et les tests de regression sur chaque pull request et chaque push sur main."
  ]},
  {"build":231,"date":"8 octobre 2026","sha":"","tag":"PWA iPhone : cache versionne, hors-ligne, bandeau de nouvelle version","items":[
    "SERVICE WORKER : le cache porte le numero de build (plus de plan-v34 ecrit a la main), tous les fichiers du site sont pre-caches ; reseau d abord avec repli sur le cache apres 3 s ou hors-ligne.",
    "NOUVELLE VERSION : au retour au premier plan, l app compare son build a data/meta.json et propose Actualiser (utile : la PWA reste en memoire plusieurs jours sur iPhone).",
    "MANIFESTE : portee et langue ajoutees."
  ]},
  {"build":230,"date":"8 octobre 2026","sha":"","tag":"Donnees hors de la page : data/*.json charges au demarrage, historique des versions a la demande","items":[
    "DONNEES EN JSON : plan, seances, historique et meta sont des fichiers data/*.json charges en parallele au demarrage ; l application (src/app.js) ne change pas, les constantes gardent leurs noms. La page index.html ne contient plus les donnees.",
    "HISTORIQUE DES VERSIONS : la liste complete (200 Ko) n est plus construite au demarrage mais chargee a la premiere ouverture du panneau.",
    "ECHEC RESEAU : si les donnees ne se chargent pas, un message lisible et un bouton Reessayer remplacent l ecran blanc."
  ]},
  {"build":229,"date":"8 octobre 2026","sha":"","tag":"Barre de navigation a 4 onglets, accessible au clavier et aux lecteurs d ecran","items":[
    "NAVIGATION : 4 onglets (Accueil, Seances, Cockpit, Courses) de largeur egale ; la barre est etiquetee et l onglet actif porte aria-current.",
    "TESTS : cibles tactiles de 44 px minimum, ordre de tabulation et ouverture a la touche Entree verifies."
  ]},
  {"build":228,"date":"8 octobre 2026","sha":"","tag":"Retrait du chat coach integre : le coaching se fait dans Claude","items":[
    "RETRAIT DU CHAT COACH : overlay, saisie, appel a l API et bouton central de la barre de navigation supprimes (environ 15 Ko de JavaScript et le CSS associe). Le coaching se fait dans Claude apres chaque seance.",
    "CONSERVE : les conseils calcules localement (puce de conseil du jour, coachAvant, coachDebrief, theorie par type de seance). La feuille de conseil n a plus de lien vers le chat."
  ]},
  {"build":227,"date":"8 octobre 2026","sha":"","tag":"PRODUCT.md et DESIGN.md : contexte produit et systeme de design documentes","items":[
    "PRODUCT.md : utilisateur, positionnement (plan sur mesure avec Claude, cockpit charge et forme, journal de saison), contexte d exploitation et principes.",
    "DESIGN.md : Le carnet de l entraineur, tokens reels de css.txt, regles nommees (One Voice, Seven Levels, Quiet Shadow)."
  ]},
  {"build":226,"date":"8 octobre 2026","sha":"","tag":"Captures de reference des 4 vues et procedure de retour arriere","items":[
    "CAPTURES DE REFERENCE : scripts/capture_reference.py produit 4 images reproductibles (date figee, meteo bloquee, animations reduites) dans tests/reference/ ; --check detecte tout changement visuel.",
    "RETOUR ARRIERE : tag Git pre-refonte (build 224) et procedure ecrite dans docs/LESSONS.md."
  ]},
  {"build":225,"date":"8 octobre 2026","sha":"","tag":"Build portable : une seule commande, plus de dependance au dossier /tmp","items":[
    "BUILD PORTABLE : python src/build.py construit index.html depuis la racine du depot, sous Windows comme sous Linux. Les chemins /tmp et /mnt/user-data sont remplaces par un module commun src/paths.py (dossier de travail build/, ignore par Git).",
    "CONTROLE : python src/build.py --check echoue si index.html n est pas exactement le resultat du build. preflight.py et test_regression.py passent sous Windows (16/16)."
  ]},
  {"build":224,"date":"8 octobre 2026","sha":"","tag":"Passe complete du Cockpit : projection, ACWR, polarisation, compteurs et totaux remis d'aplomb","items":[
    "PROJECTION MARATHON (boule de cristal) : 3h56 -> 3h41. Ce n'est pas un changement de forme, c'est la correction de ses entrees. Elle lisait realise.allure, souvent la moyenne de TOUTE la seance (echauffement et recups compris), et comptait la sortie vallonnee du 29/09 (5:51/km) comme une seance de seuil, soit un point a 4h21. Nouveau champ realise.allure_travail (allure des blocs seuls) pour 19/07 (4:28), 30/07 (5:09), 28/08 (4:41), 02/09 (4:36) et 06/10 (5:18), et realise.hors_projection pour le 29/09. A lire avec prudence : le seul 06/10 donne un equivalent marathon de 3h47, le reste est tire vers le bas par les seuils.",
    "ACWR DU BANDEAU : le tuile du haut affichait 1,00 « maitrise » pendant que l'alerte juste a cote disait 2,35. La courbe hebdomadaire utilisait une moyenne exponentielle par semaine (et prenait la semaine en cours, incomplete, pour une semaine pleine). Elle utilise maintenant la meme definition que partout ailleurs (charge 7 jours / moyenne 28 jours), prise a la fin de chaque semaine, et a aujourd'hui pour la semaine en cours.",
    "POLARISATION (donut + verdict) : c'etait un instantane fige 8/43/43/5 « sur les 6 derniers mois » avec le verdict « 43 % de zone grise, probleme n°1 ». Il est maintenant calcule sur les seances loguees depuis le 15 juin : voir la methode affichee sous le graphique. Les chiffres changent beaucoup (zone grise 7 % contre 43 %) en partie parce que la methode et la periode ne sont plus les memes ; l'ancien chiffre n'a pas pu etre reproduit. A valider par Loic.",
    "SEMAINE S40 : le footing du soir du 04/10 avec Perrine (3,78 km, run/marche 15 x 1 min / 1 min, FC 111, RE 7) est logue. S40 passe a 6 sorties, 75,2 km, charge 915, comme sur Strava ; octobre et la saison s'alignent aussi. L'audit de reconciliation sait maintenant additionner deux seances d'une meme date.",
    "COMPTEURS DE COURSES : la tuile « J avant Deraille » affichait J-0 (elle lisait en realite Run In Lyon, premiere course de la liste). Elle montre maintenant le semi Run In Lyon comme fait, et Nice et SaintExpress sont lus par nom plutot que par position.",
    "ALLURE MARATHON (liste des allures) : 5:15 -> 5:18/km, avec sa source (3x4 km du 06/10, FC 159), et le libelle « cible Nice 3h42 » corrige en « cible Nice 3h45 = 5:20 ».",
    "PETITS ECARTS : date « MAJ » figee au 5 octobre, maintenant lue dans le CHANGELOG ; pied du calendrier qui affichait « build 37 » ; texte « aligne sur Strava (108 activites) » devenu dynamique (166).",
    "NON MODIFIE VOLONTAIREMENT : projections de forme saisies a la main (semi ~1h44, marathon projete ~3h38-3h42, tableau Riegel), radar de profil, VO2max (records inchanges), carte « Derniere sortie analysee » (decouplage non recalcule depuis le 02/08, il faut les flux Strava de chaque seance) et rewinds hebdomadaires S36 a S40."
  ]},
  {"build":223,"date":"7 octobre 2026","sha":"","tag":"S41-3 : vallonne sous la pluie logue, 15 km D+ 242 m a FC 146","items":[
    "SEANCE LOGUEE S41-3 (07/10, footing prevu remplace par un vallonne) : 15,06 km, 1:30:06, 5:59/km, FC 146 moy / 180 max, RE 119, D+ 242 m, Clifton 10. Decision de Loic de faire une seance de denivele dans la semaine. Titre, sous-titre, metriques, structure et segments de la fiche mis a jour pour le format reel ; les 15 km Strava sont saisis tels quels.",
    "A RETENIR : FC dans la zone d'un footing facile malgre le relief (plat et descente a 133-142, montees a 4-6 % a 156-158), allure adaptee a la pente (6:38 en montee, 5:18 en descente). Deux raidillons d'environ 70 s a 175 bpm et un pic a 180 dans les escaliers du Signal. Descentes rapides : attente de raideur des quadriceps avant la longue de dimanche.",
    "CONTEXTE CHARGE : 5e jour de course d'affilee depuis samedi, 3e sortie en 3 jours, 15 km au lieu des 12 prevus. Semaine S41 a 39,2 km sur 76 prevus a ce stade.",
    "GEAR : Clifton 10 1214 -> 1229 km (releve Strava 1228,97). Autres paires inchangees. Reconciliation Strava etendue a la date 07/10.",
    "RPE : 4 saisi par lecture de 'vallonne chill', pas une valeur donnee par Loic. A ajuster s'il le souhaite."
  ]},
  {"build":222,"date":"7 octobre 2026","sha":"","tag":"S41 : recup post-semi et 3x4 km allure marathon logues, 12 km a 5:18 avec 13 s d'ecart","items":[
    "SEANCE LOGUEE S41-1 (05/10, recup) : 8,04 km a 6:09/km, FC 142 moy / 159 max, RE 59, Novablast 5 J. Plus court que les 12 km prevus (decision de Loic au lendemain du semi). Titre, sous-titre, metriques et segments de la seance mis a jour pour refleter le format reel. A allure quasi identique, FC 11 bpm plus basse que l'activation du 03/10 (153) et meme niveau que le 28/09 (143).",
    "SEANCE LOGUEE S41-2 (06/10, 3x4 km allure marathon) : 16,05 km, 1:26:31, FC 158 moy / 176 max, RE 199, Novablast 5 J (la Magic Speed 4 etait prevue). Blocs a 5:18, 5:18, 5:18/km (FC 159, 159, 162), 12 km dont 11 dans la fenetre 5:15-5:25, un seul a 5:12. Ecart de 13 s/km sur 12 km, contre un split positif de 27 s/km au semi. Derive de +3 bpm entre bloc 1 et bloc 3 a allure identique. Les 18 laps Strava sont saisis tels quels (echauffement, 3 blocs de 4 km, 2 recups, final de 380 m). Les segments de la fiche sont remplaces par les durees reelles.",
    "POINTS A CONNAITRE : (1) recups a 5:44-5:45/km, FC 151-152, la seconde de 4:41 (arret ~100 s) ; (2) la seance se termine par 380 m a 4:54/km (FC 176 max), sans retour au calme enregistre ; (3) RPE saisis a 3 (recup) et 6 (AM) par lecture des mots de Loic ('footing facile', 'tenu assez facilement'), pas par une valeur qu'il a donnee. A ajuster s'il le souhaite.",
    "BUG CORRIGE (accueil) : la tuile « Prochaine course » affichait J-0 pour Run In Lyon apres la course (compteur clampe a 0, course passee jamais exclue) et le compteur Nice divergeait d'un jour des autres vues (date lue en UTC). Les courses passees sont exclues et tous les compteurs utilisent _joursAvant. Verifie au gate visuel : plus d'ecart (Nice J-32, SaintExpress J-52). Detail dans docs/LESSONS.md L09.",
    "GEAR : Novablast 5 J 764 -> 788 km (releve Strava, 787,8). Autres paires inchangees. Reconciliation Strava etendue aux dates 05/10 et 06/10.",
    "NON MODIFIE : le footing du soir du 04/10 avec Perrine (3,78 km en 15 x 1 min de course / 1 min de marche, RE 7, Gel Pulse 16) n'est pas logue dans l'app ; la semaine S40 reste donc a 71,5 km contre 75,2 km sur Strava. Radar de profil et projections de forme laisses en l'etat : une seule seance propre ne justifie pas de les bouger avant S42."
  ]},
  {"build":221,"date":"5 octobre 2026","sha":"","tag":"Temps du semi renseigne, palmares complete, comparaison chiffree avec la forme du 22/08","items":[
    "TEMPS DU SEMI : Loic donne 1h52:30. Renseigne dans la seance (S40-4) et dans une nouvelle ligne PALMARES (Run In Lyon semi, 04/10/2026, 5:20/km, FC 177/189, Novablast 5 V). A RECOUPER : ce chrono est identique, a la seconde, au meilleur effort semi calcule par Strava (6750 s) ; le chrono officiel de la puce peut differer de quelques secondes a une minute (21,30 km parcourus en GPS pour 21,0975 officiels). A corriger si la page resultats de l'organisateur dit autre chose.",
    "CORRECTION D'UNE ERREUR DE LIBELLE : 1h52:39 etait presente comme 'PB officiel' de Paris 2022 (dans mes messages et dans trois textes d'histoire de l'app). Le palmares donne 1:53:21 en chrono reel pour Paris ; 1h52:39 est le meilleur effort Strava de cette course. Les deux comparaisons restent favorables si 1:52:30 est confirme (51 s en chrono officiel, 9 s en meilleur effort Strava). Les trois textes d'histoire ne sont pas modifies ici.",
    "TEXTE PERIME CORRIGE : la fiche Paris 2022 portait encore 'objectif 1:44 au Semi de Lyon 4 oct. 2026 = -9 min en 4 ans'. Elle indique maintenant l'objectif et le resultat reel (1:52:30, couru malade).",
    "COMPARAISON CHIFFREE AJOUTEE A LA REVUE : sur les km 3 a 10, 5:03/km pour une FC de 178 le 04/10 contre 4:58/km pour 162 le 22/08, soit environ 15 bpm de plus pour un rythme meme legerement plus lent. Ce chiffre melange maladie, sommeil et reprise apres coupure : il ne permet pas de repartir la part de chacun.",
    "NON MODIFIE VOLONTAIREMENT : les projections de forme (semi ~1h44, marathon ~3h38-3h42) restent en l'etat, une course disputee malade n'etant pas une mesure propre. Elles seront rejugees apres la seance S42 sur un corps gueri."
  ]},
  {"build":220,"date":"5 octobre 2026","sha":"","tag":"Run In Lyon logue : semi couru malade, parti seul trop vite, split positif de 27 s/km","items":[
    "SEANCE LOGUEE (S40-4, dimanche 04/10) : Run In Lyon semi, 21,30 km GPS en 1:53:29 de mouvement (1h52:30 sur 21,1 km selon le meilleur effort semi Strava), allure moyenne 5:20/km, FC 177/189, effort relatif 470, cadence 86, D+71, Novablast 5 V. Temps officiel non communique a ce stade.",
    "DEPART SEUL : le partenaire de course a du s'arreter refaire ses lacets, Loic est parti sans repere humain. Km 1-10 a 5:06/km, km 11-20 a 5:33/km, soit un split positif de 27 s/km (4 min 29). Contre-epreuve du mecanisme observe cette saison : l'ancrage humain fonctionne, son absence se paie en moins de 3 km.",
    "COUT CARDIAQUE : FC 171 des le km 2, 173-182 jusqu'au km 17 (pic 189 au km 7), soit 15 a 20 bpm au-dessus de la zone marathon 152-163. Course disputee malade apres 5 nuits a 3-4h de sommeil. Explosion progressive a partir du km 17 (5:31 puis 5:50, 5:52, 6:06).",
    "LECTURE RETENUE : course confondue (maladie + sommeil + depart trop rapide), non lisible comme test d'allure marathon -- elle ne valide ni n'invalide 3h45. La strategie arretee pour Nice (meneur d'allure officiel jusqu'au 35e-36e km) en sort renforcee.",
    "REVUE HEBDOMADAIRE S40 ECRITE (S40 close, evite le bug B1 deja vu sur S36 et S39). Jeudi 01/10 marque 'skipped'. PALMARES et records non modifies tant que le temps officiel n'est pas confirme.",
    "KPI RECALCULES AUTOMATIQUEMENT. GEAR resynchronise sur Strava : Novablast 5 V 151 -> 172 km, Gel Pulse 16 225 -> 229 km (les deux copies). Referentiel de reconciliation etendu a la seance du jour."
  ]},
  {"build":219,"date":"3 octobre 2026","sha":"","tag":"Activation veille de course : la FC revele une dette de sommeil, pas un probleme de forme","items":[
    "SEANCE LOGUEE (S40, nouvel id 6, non planifiee) : footing d'activation avec Yannis et Manon, veille du Run In Lyon. 7,04 km en 42:11, allure moyenne 5:59/km, FC 153/179, effort relatif 82, cadence 85, Novablast 5 J.",
    "SIGNAL FORT A J-1 D'UNE COURSE OBJECTIF : 5e nuit de suite a 3-4h de sommeil (4h07 la veille). Test d'acceleration volontaire sur le dernier km (5:10/km) a produit une FC de 174 moyenne / 179 max -- reponse cardiaque disproportionnee pour l'effort, confirmant le ressenti de Loic. Le reste de la sortie tournait deja haut (150-156 bpm) pour une allure easy sur terrain plat.",
    "LECTURE RETENUE : signal de dette de sommeil, pas de fitness. Aucune conclusion a tirer sur la capacite marathon a partir de cette seance. Decision pour le Run In Lyon de demain : caler sur le groupe 1h50 si le corps repond, lacher sans hesiter si la FC s'envole anormalement tot -- un chrono degrade lie a cette semaine de sommeil n'invalidera rien pour Nice.",
    "KPI RECALCULES AUTOMATIQUEMENT. GEAR Novablast 5 J resynchronise sur Strava : 757 -> 764 km (les deux copies). Referentiel de reconciliation etendu a la seance du jour."
  ]},
  {"build":218,"date":"30 septembre 2026","sha":"","tag":"Meilleure execution technique depuis le retour USA, mais au mauvais moment du cycle","items":[
    "SEANCE LOGUEE (S40-3, mercredi) : sortie non planifiee, 18,04 km en 1:57:15, allure moyenne 6:30/km, FC 137/157, effort relatif 93, cadence 86, HOKA Clifton 10. Prevu : 6 km optionnelle ou repos.",
    "EXECUTION LA PLUS DISCIPLINEE DEPUIS LE RETOUR : FC quasi jamais au-dessus de 143 sur l'ensemble des 18 km (plafond 140 vise, un seul pic isole a 157), allure stable. Aucune derive progressive (contrairement a SF/Venice/retour), aucun coup de collier de fin (contrairement a Yannis), aucun remplacement non maitrise (contrairement a Edwige).",
    "POINT DE VIGILANCE ASSUME PAR LOIC LUI-MEME : timing sous-optimal. Sortie longue non planifiee a 4 jours du Run In Lyon (allure marathon visee dimanche), sur une semaine deja chargee (3 jours consecutifs avant, ACWR deja eleve). Decidee sur bonne sensation apres une tres bonne nuit -- une sensation fraiche a l'instant T ne garantit pas la fraicheur 4 jours plus tard.",
    "KPI RECALCULES AUTOMATIQUEMENT. GEAR Clifton 10 resynchronise sur Strava : 1196 -> 1214 km (les deux copies). Referentiel de reconciliation etendu a la seance du jour."
  ]},
  {"build":217,"date":"29 septembre 2026","sha":"","tag":"Run In Lyon integre comme course officielle : nouveau dossard, nouvelle fiche, semaine allegee","items":[
    "NOUVELLE COURSE : le 4 octobre 2026 (S40-4) passe de sortie longue planifiee a Run In Lyon, semi-marathon officiel (21,097 km), couru avec deux amis visant 1h50 (5:13/km) comme test grandeur nature de l'allure marathon avant Nice.",
    "Fiche complete ajoutee a DOSSIERS (a l'image de Nice et SaintExpress) : parcours (Bellecour, Terreaux, quais de Saone et du Rhone, Parc de la Tete d'Or), plan d'execution par segment, zones FC specifiques, nutrition adaptee au format court. Informations verifiees en ligne (date, distance, lieu de depart), sources citees, limites signalees honnetement (trace GPX du semi et horaire exact non reconfirmes pour l'edition 2026).",
    "NOUVEAU CAS race('runinlyon') ajoute a la fonction de generation des seances de course, sur le meme modele que marathon/deraille/saintexpress. RACE_DATES etendu pour que le moteur de planification respecte la vraie date (04/10) plutot que le cycle rotatif habituel.",
    "SEMAINE S40 ALLEGEE en consequence : la seance du mercredi (S40-3) perd ses lignes droites, passe a 6 km optionnelle avec le contexte ecrit noir sur blanc (3 jours de course consecutifs, fatigue signalee, course cible dimanche).",
    "BUG ATTRAPE AVANT PUSH, PAS APRES : le rendu de fiche de course (ouvrirDossier) plantait sur l'absence du bloc nutrition, jamais teste avec un dossier sans cette section jusqu'ici. Verifie dans un vrai navigateur (Playwright) avant push, conformement a la convention etablie -- corrige en completant honnetement le bloc nutrition plutot que de modifier la fonction partagee par les 3 autres dossiers sous pression de temps."
  ]},
  {"build":216,"date":"29 septembre 2026","sha":"","tag":"Seuil non fait, sortie vallonnee a la place : 3e jour consecutif, fatigue signalee, ACWR eleve","items":[
    "SEANCE LOGUEE (S40-2, mardi) : seuil 2x10 min prevu non realise, remplace par une sortie continue et vallonnee avec Edwige, 12,03 km en 1:10:26, allure moyenne 5:51/km, FC 158/187, effort relatif 171, cadence 86, D+147m, Novablast 5 J.",
    "CONTEXTE A RETENIR : 3e jour de course consecutif (dimanche retour, lundi avec Yannis, aujourd'hui), effort reel (RE171) superieur aux deux jours precedents, sur une base encore fraichement reconstruite apres 3 semaines de coupure USA. Fatigue signalee par Loic lui-meme apres la seance -- coherent avec les chiffres. Aucune douleur.",
    "ACWR EN ZONE ELEVEE : charge aigue construite sur une charge chronique encore basse. Recommandation coach : alleger la suite immediate (S40-3, mercredi) plutot que d'enchainer une 4e journee a charge normale.",
    "KPI RECALCULES AUTOMATIQUEMENT. GEAR Novablast 5 J resynchronise sur Strava : 745 -> 757 km (les deux copies). Referentiel de reconciliation etendu a la seance du jour."
  ]},
  {"build":215,"date":"28 septembre 2026","sha":"","tag":"Premier signal encourageant post-USA : FC stable sur le coeur de seance avec Yannis","items":[
    "SEANCE LOGUEE (S40-1, lundi) : 13,04 km en 1:19:23, allure moyenne 6:05/km, FC 143/182, effort relatif 92, cadence 86, Novablast 5 V, avec Yannis.",
    "PREMIER SIGNAL ENCOURAGEANT DEPUIS LE RETOUR : du km3 au km11 (~8 km), allure 6:14-6:36/km et FC 134-141 -- stable, dans le cadre prevu, sans la derive progressive observee sur les 3 dernieres sorties (San Francisco, Venice Beach, retour de vacances). Coup de collier assume sur les 2 derniers km (5:46 puis 5:02/km, FC jusqu'a 182 = 95% FCmax), vraisemblablement partage avec Yannis -- pas une derive, un final choisi. Aucune douleur.",
    "KPI RECALCULES AUTOMATIQUEMENT. GEAR Novablast 5 V resynchronise sur Strava : 138 -> 151 km (les deux copies). Referentiel de reconciliation etendu a la seance du jour."
  ]},
  {"build":214,"date":"27 septembre 2026","sha":"","tag":"Retour de vacances logue : troisieme signal convergent de derive cardiaque post-coupure","items":[
    "SEANCE LOGUEE (S39-4, dimanche) : 10,2 km en 55:07, allure moyenne 5:24/km, FC 156/177, effort relatif 121, cadence 86, Novablast 5 J. Seance de remise en route prevue a 16 km, raccourcie sur fatigue de voyage et jet lag assumes -- decision de couper plutot que de forcer, jugee bonne.",
    "DERIVE CARDIAQUE PROGRESSIVE ET CONTINUE sur l'integralite de la sortie : FC 144 au km1, 165 au km10, 174 sur le dernier segment ; allure 5:45/km en ouverture, 5:03/km en cloture. Troisieme signal convergent du meme diagnostic apres San Francisco (economie de course reduite) et Venice Beach (FC quasi maximale) : l'organisme a besoin de plusieurs seances propres pour retrouver son efficacite apres 3 semaines quasi sans courir.",
    "BILAN CHIFFRE DE LA PERIODE USA (S37-S39) : environ 12 seances prevues, 2 seulement courues (SF 06/09, Venice 23/09) avant celle-ci. Le reste en randonnee dans les parcs nationaux. Nice (8 novembre) est dans 6 semaines.",
    "KPI RECALCULES AUTOMATIQUEMENT. GEAR Novablast 5 J resynchronise sur Strava : 734 -> 745 km (les deux copies). Referentiel de reconciliation etendu a la seance du jour."
  ]},
  {"build":213,"date":"23 septembre 2026","sha":"","tag":"Bug structurel des fenetres Cockpit corrige : les semaines sans course etaient sautees, pas comptees a zero","items":[
    "DECOUVERT EN LOGUANT LA SEANCE DE VENICE BEACH : l'audit Cockpit a echoue avec 14 ecarts sur la repartition des zones FC. Investigation menee jusqu'au bout plutot que de corriger les chiffres en surface.",
    "CAUSE RACINE : la fonction lastN() d'app.js construisait les fenetres '2/4/8/12 semaines' en prenant les N DERNIERES semaines *avec des donnees*, sautant silencieusement toute semaine sans seance loguee. Avec S37 et S38 entierement non courues (road trip USA, uniquement de la randonnee), une fenetre affichee '2 semaines' recouvrait en realite S36+S39 -- 4 semaines calendaires reelles, sans le signaler. Premier trou de plusieurs semaines consecutives depuis le debut du suivi ; le defaut etait probablement latent depuis toujours, jamais revele avant.",
    "CORRIGE STRUCTURELLEMENT : lastN(n) retourne desormais n semaines ISO strictement consecutives se terminant a la derniere semaine reellement loggee -- une semaine sans course y contribue pour 0, elle n'est jamais sautee. Toutes les fenetres du Cockpit (volume, effort, D+, allure, cadence, decouplage, zones FC) en beneficient, pas seulement les zones FC ou l'ecart etait visible.",
    "EFFET DE BORD DECOUVERT ET CORRIGE : le graphe Decouplage cardiaque se rendait vide (silencieux) des qu'aucune donnee fiable n'existait sur la periode, indiscernable d'un bug. _ckLine() affiche desormais explicitement 'Pas de donnee fiable sur cette periode' au lieu de laisser le SVG dans un etat vide ambigu.",
    "SEANCE LOGUEE (S39-3, mardi) : reprise a Venice Beach / Santa Monica apres 17 jours sans course (voir detail dans le journal de bord). 10 seances passees du road trip (S37, S38, S39-1, S39-2) marquees explicitement 'skipped' avec le contexte reel (randonnee dans les parcs nationaux) au lieu de rester 'a_faire' de maniere ambigue -- corrige le bug [A2] de audit_data.py.",
    "REVUE HEBDOMADAIRE MANQUANTE ECRITE : S36 avait ses 5 seances loguees avec revues individuelles mais aucune synthese hebdomadaire (bug [B1] de audit_data.py, presente depuis le build 211). Synthese ecrite : le contraste entre l'alerte Fenix ignoree du mercredi et la discipline tenue grace a une partenaire de course le jeudi, avec le lien direct vers la strategie du meneur d'allure a Nice.",
    "KPI RECALCULES AUTOMATIQUEMENT. GEAR Novablast 5 V resynchronise sur Strava : 126 -> 138 km (les deux copies, audit_reconciliation.py ET audit_data.py). Referentiel de reconciliation etendu a la seance du jour."
  ]},
  {"build":212,"date":"23 septembre 2026","sha":"","tag":"Reprise a Venice Beach / Santa Monica apres 17 jours sans course : effort cardiaque quasi maximal sous couvert de plaisir","items":[
    "SEANCE LOGUEE (S39-3, mardi) : 11,63 km en 56:13 de course (89:17 au total, ~33 min d'arrets lies a la foule sur le boardwalk), allure moyenne 4:50/km, FC 168/190 (2 bpm sous FCmax 192), effort relatif 177, cadence 86, Novablast 5 V. Premiere course depuis le 06/09 (San Francisco) -- 17 jours sans courir, uniquement de la randonnee dans les parcs nationaux US (Zion, Bryce, Grand Canyon).",
    "ECART MAJEUR AU PLAN (footing facile + lignes droites, 5:50-6:25/km, FC 135-150) mais PAS de la meme nature que les ecarts de discipline habituels : la FC (168 moyenne, pic 190) montre un effort cardiovasculaire quasi maximal que le ressenti (plaisir, jambes correctes) n'a pas signale. Lecture retenue : la coupure de 17 jours a fait reculer l'economie de course specifique sans affecter la forme generale -- la randonnee entretient le cardio et les jambes autrement que la course.",
    "POINT DE VIGILANCE POUR LA SUITE : ~6 semaines restantes avant Nice (8 novembre). Marge suffisante pour rebatir un calibrage FC/allure, mais pas de seconde coupure de cette duree sans plan de retour explicite. Aucune douleur signalee.",
    "KPI RECALCULES AUTOMATIQUEMENT. GEAR Novablast 5 V resynchronise sur Strava : 126 -> 138 km. Referentiel de reconciliation etendu a la seance du jour (audit_reconciliation.py ET audit_data.py, les deux copies)."
  ]},
  {"build":211,"date":"6 septembre 2026","sha":"","tag":"Seance optionnelle San Francisco loguee : jet lag digere, largement au-dela du cadre pose","items":[
    "SEANCE LOGUEE (S36-5, dimanche, optionnelle) : 14,28 km en 1:15:54 de mouvement, allure moyenne 5:19/km, FC 154/180, effort relatif 161, cadence 85, D+220 m, Novablast 5 V. Golden Gate Park + Lands End Trail.",
    "Ecart large au cadre pose (5-7 km / 30-40 min / FC<140) mais assume positivement : le cadre n'avait vocation qu'a proteger si le corps ne suivait pas a J+2 de decalage. Il a suivi, largement -- aucune douleur, jambes legeres, plaisir plutot qu'effort.",
    "Variation d'allure (4:44 a 6:03/km) et FC moyenne 154 expliquees par le relief (220 m D+ sur 14 km, escaliers et sentiers techniques de Lands End) plutot que par une derive de discipline -- coherent avec une sortie non structuree, pilotee au relief et a la sensation.",
    "KPI RECALCULES AUTOMATIQUEMENT. GEAR Novablast 5 V resynchronise sur Strava : 112 -> 126 km. Referentiel de reconciliation etendu a la seance du 06/09."
  ]},
  {"build":210,"date":"3 septembre 2026","sha":"","tag":"Trou structurel corrige : release.py ne poussait jamais scripts/*.py","items":[
    "DECOUVERT EN VERIFIANT LE BUILD 209 : le manifeste de push de release.py ne listait que index.html et les fichiers src/. Tous les scripts sous scripts/ (audit_data.py, audit_reconciliation.py, audit_kpi.py, audit_dette.py, audit_runtime.py, audit_seances.py, audit_visuel.py, test_regression.py, test_race.py) tournaient depuis WORK en local -- gate vert a chaque build -- sans jamais etre synchronises sur GitHub.",
    "CONSEQUENCE CONCRETE : le referentiel de reconciliation (audit_reconciliation.py) mis a jour aux builds 207, 208 et 209 pour les seances du 02/09 et 03/09 est reste perime sur le repo reel pendant 3 builds, malgre 'reconciliation Strava : 0 ecart, 59 controles' affiche a chaque gate -- ce resultat etait vrai en local, pas sur le depot.",
    "CORRIGE STRUCTURELLEMENT : le manifeste de push inclut desormais tous les scripts/*.py existants dans WORK, pas seulement les fichiers src/. Ce build synchronise en meme temps le contenu des builds 207-209 qui n'etait jamais arrive sur GitHub.",
    "Meme categorie que le bug GEAR de audit_data.py trouve dans ce meme build 209 : les deux venaient du meme angle mort -- des fichiers modifies et verifies en local, jamais confrontes a l'etat reel du depot avant aujourd'hui."
  ]},
  {"build":209,"date":"3 septembre 2026","sha":"","tag":"Passe complete KPI demandee par Loic : deux ecarts reels trouves et corriges","items":[
    "DEMANDE : verification complete de tous les KPI, graphiques et donnees. Resultat : GEAR (6 paires) 100% conforme a Strava. PALMARES a jour (aucune course depuis Deraille/Circaete, Nice et SaintExpress restent a venir). MAJ (date affichee en pied d'app) etait figee au 2 septembre malgre le build 208 du 3 -- corrigee.",
    "RECORDS_PERF CORRIGE, PAS SEULEMENT SIGNALE COMME NON VERIFIE : les champs 'meilleur effort 2026' (5 km et 10 km) affichaient encore l'allure exacte des records officiels (4:35 et 4:37/km), un reliquat jamais recalcule, deja repere au build ~180 mais laisse en l'etat. Verification sur les streams Strava de la sortie du 22/08 (record de semi) : meilleur 5 km embarque reel = 23:57 (4:47/km), meilleur 10 km embarque reel = 49:00 (4:54/km) -- nettement plus lents que ce qui etait affiche. Valeurs remplacees par ces chiffres verifies, avec mention explicite qu'un scan exhaustif des ~150 seances n'a pas ete fait et pourrait reveler un effort plus rapide ailleurs.",
    "DUPLICATION DE REFERENTIEL DECOUVERTE : audit_data.py maintient sa PROPRE copie codee en dur du kilometrage Strava des chaussures (STRAVA_GEAR), independante du referentiel d'audit_reconciliation.py (GEAR_STRAVA) cense faire foi. Cette copie etait perimee (Clifton 1186 au lieu de 1196, Novablast 5 J 711 au lieu de 734, Magic Speed 4 85 au lieu de 93), et generait 3 faux ecarts [E2] a chaque audit. Resynchronisee dans ce build, mais la duplication structurelle elle-meme n'est pas resolue -- meme categorie que les phases 4-5 deja differees a l'apres-Nice (reduction de la surface de saisie manuelle).",
    "Reste ouvert et assume, sans changement : Clifton 10 a 1196 km, au-dela de la zone de remplacement 700-900 km (deja connu, decision de Loic de les garder en rotation)."
  ]},
  {"build":208,"date":"3 septembre 2026","sha":"","tag":"Deverrouillage logue : 12 km avec une amie, aucune derive detectee","items":[
    "SEANCE LOGUEE (S36-4, jeudi) : 12,08 km en 1:08:34, allure moyenne 5:41/km, FC 143/160, effort relatif 88, cadence 88, Novablast 5 J. Ecart au plan assume : prevu 8 km a 6:10-6:30/km FC<140, realise plus long et plus rapide -- sortie sociale avec une amie plutot que deverrouillage strict.",
    "AUCUNE DERIVE INVOLONTAIRE DETECTEE sur 68 minutes : le km le plus lent (6:06/km) est au milieu du parcours, pas au debut ; la seule acceleration nette est en toute fin de course, rapportee par Loic lui-meme comme un choix (il se sentait fort). FC monte progressivement de 133 a 150 sans a-coup.",
    "POINT COACH : contraste direct avec le seuil de la veille (build 207) ou l'alerte Fenix n'a pas suffi face a l'envie de doubler. Ici, courir cale sur une partenaire a tenu la discipline d'allure du debut a la fin -- premier indice concret que le repere humain fonctionne mieux qu'un signal technique seul pour ce declencheur.",
    "Jambes lourdes en debut de course malgre FC basse (133-139) : signature de fatigue musculaire locale (4e seance consecutive de la semaine), pas cardio. Aucune douleur.",
    "Chaussure reelle Novablast 5 J, plan prevoyait Novablast 5 V -- ecart mineur note.",
    "SEMAINE S36 BOUCLEE A 4/4 SEANCES avant le vol de demain, aucune douleur sur la semaine.",
    "KPI RECALCULES AUTOMATIQUEMENT. GEAR Novablast 5 J resynchronise sur Strava : 722 -> 734 km. Referentiel de reconciliation etendu a la seance du jour.",
    "BUG CORRIGE AVANT LIVRAISON (introduit dans ce meme build) : la seance optionnelle du 06/09 (San Francisco) est generee par deepcopy de la seance du jeudi -- elle heritait donc du bloc 'realise' tout juste ajoute, se marquant 'faite' avec 12,08 km avant meme d'avoir eu lieu. Detecte par la reference ACWR recalee au 06/09 au lieu d'aujourd'hui. Corrige par un pop() du realise/chaussure_realise juste apres le deepcopy."
  ]},
  {"build":207,"date":"2 septembre 2026","sha":"","tag":"Seuil 2x10 logue : bloc 2 tenu, bloc 1 -- alerte Fenix ignoree consciemment","items":[
    "SEANCE LOGUEE : 8,59 km en 42:51, allure moyenne 4:59/km, FC 167/181, effort relatif 137, cadence 87, Magic Speed 4. Structure : echauffement 15 min puis seuil 2x10 min cible 4:45/km, recuperation 3 min 30.",
    "BLOC 1 A 4:31/KM (cible 4:45) : 1er km couru a 4:13, soit 32 s sous la cible. ALERTE FENIX ARMEE A 4:40/KM ET IGNOREE CONSCIEMMENT -- signale par Loic lui-meme : musique dans les oreilles, berges denses, envie de doubler. Ce n'est PAS le mecanisme habituel de derive par sensation ou terrain, deja documente a plusieurs reprises cette saison : c'est un declencheur social identifie, en connaissance de cause.",
    "CORRECTION INTERNE AU BLOC : le 2e km du bloc 1 revient a 4:45/km pile, 32 s de correction sans consigne exterieure. Bloc 2 tenu a 4:38 puis 4:42, amplitude 5 s, cadence stable. Une fois le declencheur retire (plus personne a doubler), la regulation redevient fine.",
    "POINT COACH : lien direct avec la strategie de Nice (coller au meneur d'allure 3h45 jusqu'au 35e-36e km, au milieu de 15 000 coureurs). Si l'envie de doubler declenche le meme reflexe en course, elle s'exprimera precisement dans les conditions ou la strategie est censee proteger. Piste retenue : tester une seance en groupe dense, consigne unique ne doubler personne, pour verifier si un repere exterieur humain protege mieux qu'une alerte vibrante seule.",
    "SEANCE COUPEE A 8,59 KM (vs ~12 km prevus), decision assumee pour preserver la 4e seance de la semaine avant le vol de vendredi. Aucune douleur, chaleur seulement.",
    "KPI RECALCULES AUTOMATIQUEMENT. GEAR Magic Speed 4 resynchronise sur Strava : 85 -> 93 km. Referentiel de reconciliation etendu a la seance du jour."
  ]},
  {"build":206,"date":"1er septembre 2026","sha":"","tag":"Footing + lignes droites logue : cible tenue, acceleration finale identifiee par Loic","items":[
    "SEANCE LOGUEE : 11,03 km en 1h01:29, allure moyenne 5:34/km, FC 144/181, effort relatif 80, cadence 174, Novablast 5 J. Structure : 9 km footing FC plafond 148, 6x20 s lignes droites, retour au calme.",
    "FOOTING TENU : FC moyenne 140,3 pour un plafond a 148. Derive de +11,7 bpm sur 9 km, concentree sur le premier et le dernier kilometre -- le corps de seance (km 3 a 8) reste plat entre 136,9 et 142,9. Comparaison avec la veille : 142,4 bpm pour 5:54/km le 31/08, contre 140,3 bpm pour 5:46/km aujourd'hui -- plus vite pour moins de pulsations sur la 2e seance consecutive.",
    "LIGNES DROITES : les 4 premieres remarquablement stables (96, 98, 102, 98 m parcourus en 22 s). Les 2 dernieres accelerees : 110 m puis 120 m, soit 25% de distance en plus que la premiere dans le meme temps, cadence 88,8 -> 93,1. ACCELERATION IDENTIFIEE PAR LOIC LUI-MEME avant toute analyse -- ressenti confirme par les donnees.",
    "MEME SCHEMA QUE D'HABITUDE, sans conséquence ici : tenue des premieres repetitions puis relâchement en fin de serie, déjà observe le 19/08 (100 m), le 22/08 (longue) et le 27/08 (footing). Effort relatif 80 : aucun cout pour le seuil de demain.",
    "Verdict A-. KPI recalcules automatiquement : ACWR 0,81 -> 1,02, saison 1920 -> 1931 km, Novablast 5 J 711 -> 722 km. Referentiel de reconciliation etendu a 57 controles, tous conformes."
  ]},
  {"build":205,"date":"31 aout 2026","sha":"","tag":"Rewind : trois semaines manquantes, S32 s'ouvrait en semaine 36","items":[
    "SIGNALE PAR LOIC : « j'ai bien le rewind mais il dit n'importe quoi ». Constat verifie : le dernier Rewind existant etait celui de S32, alors qu'on est en semaine 36. L'ouverture automatique du lundi presentait donc le recapitulatif d'il y a un mois.",
    "CAUSE : les Rewinds de S33, S34 et S35 n'avaient jamais ete crees. Le mecanisme rwAuto ouvre REWINDS[length-1], soit le dernier element du tableau -- il presentait fidelement le seul recap disponible, qui datait.",
    "TROIS REWINDS CREES, 8 slides chacun, construits sur les donnees mesurees : S33 (La Rochelle, premier bloc allure marathon reussi a 11 s d'amplitude), S34 (record officieux de semi a 1h46:18 ET deriveuse de 25 km), S35 (la plus petite semaine, mais la serie de trois echecs cassee sur le seuil).",
    "BUG D'ORDRE CORRIGE : mes trois nouveaux blocs ayant ete inseres AVANT S32, celui-ci restait en derniere position et continuait d'etre ouvert automatiquement. S32 replace en ordre chronologique. Le dernier element est desormais S35.",
    "BUG D'ENCODAGE CORRIGE AU PASSAGE : j'avais ecrit les emojis en paires de substitution UTF-16 (\\ud83c\\udfac), invalides en UTF-8 -- le build echouait a l'ecriture du JSON. Remplaces par les emojis litteraux, conformement a la regle L04 du preflight qui existait deja pour ce motif.",
    "VERIFIE DANS LE NAVIGATEUR : l'ouverture automatique du lundi presente bien S35, et les quatre Rewinds S32 a S35 s'ouvrent depuis leur semaine respective avec le bon contenu. Zero erreur JS."
  ]},
  {"build":204,"date":"31 aout 2026","sha":"","tag":"HIST perime depuis juillet + faux positif de mon propre audit","items":[
    "EN LOGUANT LA SEANCE, le gate a bloque sur un ecart Cockpit de 15 %. Deux problemes distincts derriere, un vrai et un faux.",
    "VRAI PROBLEME -- HIST PERIME : le fichier externe hist.json alimente les graphiques de progression du Cockpit et n'avait plus ete mis a jour depuis juillet. Il s'arretait a S28 et contenait des valeurs fausses : S25 a 52 km au lieu de 56,6, S27 a 30,1 au lieu de 53,4, S28 a 11 au lieu de 61. QUATRIEME bloc a deriver pour la meme raison. Rendu auto-calcule depuis SEANCES_BY_WEEK ; hist.json ne sert plus que pour l'historique anterieur a S25.",
    "FAUX POSITIF DE MON PROPRE AUDIT : l'ecart de 15 % venait de mon controle, pas de l'app. Le Cockpit raisonne en SEMAINES ISO (S29 a S36 pour sa fenetre 8), mon audit comparait a une fenetre calendaire de 8x7 jours -- decalee d'une semaine. Le Cockpit affichait 357 km et avait raison. Controle aligne sur les memes semaines ISO : 357 vs 357.",
    "SEANCE DU 31/08 LOGUEE : 10,26 km en 1h00:27 a 5:54/km, FC 142,4 pour un plafond a 145, effort relatif 74, Clifton 10. Deux km seulement au-dessus de 145. Deuxieme seance a cible tenue d'affilee apres le seuil du 28/08.",
    "POINT COACH : Loic a hesite a partir sur 16 km et ne l'a pas fait, pour preserver les 4 seances de la semaine. C'est exactement la decision qu'il ne prenait pas le 22 aout, ou la meme sensation de fraicheur avait produit 25 km a 4:54 au lieu de 5:20.",
    "KPI RECALCULES : ACWR 0,67 -> 0,81. Saison 1920 km / 152 sorties. Clifton 10 : 1186 -> 1196 km. Referentiel de reconciliation etendu a la seance du jour, 56 controles conformes."
  ]},
  {"build":203,"date":"31 aout 2026","sha":"","tag":"Footing de relance logue + KPI recalcules","items":[
    "SEANCE LOGUEE : 10,26 km en 1h00:27 a 5:54/km, FC moyenne 142,4 pour un plafond fixe a 145, FC max 160, effort relatif 74, cadence 173. Clifton 10.",
    "CIBLE TENUE : deux kilometres seulement au-dessus de 145 (146,0 et 145,5), et de tres peu. Amplitude d'allure 23 s/km. DEUXIEME SEANCE A CIBLE TENUE D'AFFILEE apres le seuil du 28/08. Contraste avec le 27/08 : meme consigne de plafond a 145, realise a 156.",
    "LE POINT LE PLUS IMPORTANT N'EST PAS DANS LES CHIFFRES : Loic a hesite a partir sur 16 km et ne l'a pas fait, pour preserver les 4 seances de la semaine. C'est exactement la decision qu'il ne prenait pas le 22 aout, ou la meme sensation de fraicheur avait produit 25 km a 4:54 au lieu de 5:20.",
    "FRUSTRATION DU MOIS D'AOUT ADRESSEE : elle reposait sur un chiffre faux. L'app affichait 79 km (bug corrige au build 198), le reel est 184 km sur 15 sorties. Et juin, donne a 82 km, en valait 190 (bug corrige au build 202). Sur trois mois : juin 190, juillet 257, aout 184 -- aucun mois faible.",
    "KPI RECALCULES : ACWR 0,67 -> 0,81 (aigu 350, chronique 1734). Saison 1909 -> 1920 km, 151 -> 152 sorties. Clifton 10 : 1186 -> 1196 km.",
    "REFERENTIEL DE RECONCILIATION MIS A JOUR avec la seance du 31/08 : le controle passe a 56 verifications, toutes conformes."
  ]},
  {"build":202,"date":"31 aout 2026","sha":"","tag":"JUIN etait faux de 108 km -- trouve par Loic, angle mort de mon propre correctif","items":[
    "SIGNALE PAR LOIC : « je ne crois pas avoir fait que 82 km en juin ». Verification faite directement sur Strava : il avait raison, et l'ecart est massif.",
    "JUIN 2026 REEL : 190,38 km sur 15 sorties et 2382 m de denivele, dont le Trail des Gypaetes (29,8 km, 1662 m D+). MONTHLY affichait 82 km sur 5 sorties. ECART DE 108 KM ET 10 SORTIES.",
    "POURQUOI MON CORRECTIF DE LA VEILLE NE L'A PAS VU -- et c'est le point important : au build 198 j'ai rendu MONTHLY auto-calcule POUR LE MOIS EN COURS UNIQUEMENT, en presumant que janvier a juillet etaient fiables parce qu'ils avaient ete « verifies en juin ». Je n'ai pas reverifie cette hypothese. Le controle generique du build 201 avait le meme angle mort : son referentiel ne couvrait que les seances loguees, et aucun mois clos n'etait confronte a Strava.",
    "JUILLET VERIFIE ET CONFORME : 256,80 km / 18 sorties contre 257 / 18 affiches. Le probleme etait isole sur juin.",
    "VALEURS CORRIGEES : juin 82 -> 190 km, 5 -> 15 sorties, 2012 -> 2382 m. Saison 1801 -> 1909 km, 141 -> 151 sorties, 20233 -> 20603 m.",
    "CONTROLE A3 AJOUTE a audit_reconciliation.py : les totaux de CHAQUE mois clos (janvier a juillet) sont desormais confrontes a un referentiel Strava, tolerance 3 km. Le controle passe de 48 a 55 verifications. Contre-teste : en refigeant juin a 82 km, l'ecart de 108 km est detecte et bloque la livraison.",
    "LECON, sans la minimiser : j'ai livre la veille un correctif de dette technique en concluant que l'historique etait « certifie conforme ». Il ne l'etait que sur le perimetre que j'avais choisi de verifier. Presumer qu'une donnee est fiable parce qu'elle a ete verifiee une fois par le passe est exactement l'erreur qui a produit les six derives precedentes."
  ]},
  {"build":201,"date":"31 aout 2026","sha":"","tag":"Dette technique : reconciliation integrale Strava + controle generique","items":[
    "PHASE 1 -- RECONCILIATION INTEGRALE, jamais faite jusqu'ici. Les 42 seances loguees (15/06 au 28/08) ont ete confrontees une par une aux activites Strava correspondantes, sur km, effort relatif et denivele.",
    "RESULTAT : 41 seances conformes sur 42, au centieme de kilometre pres. UN SEUL ECART trouve -- effort relatif du 30/06 saisi a 85 au lieu de 60. Corrige. L'historique est desormais certifie conforme a Strava sur l'integralite de la periode.",
    "PHASE 3 -- CONTROLE GENERIQUE (scripts/audit_reconciliation.py), branche en 9e position du gate. Il remplace la logique d'empilement qui avait echoue : jusqu'ici chaque garde-fou etait ecrit APRES coup et ne couvrait que le cas deja rencontre. Le controle d'ACWR ne detectait pas une derive de GEAR, celui de MONTHLY ne voyait pas un record perime.",
    "LA REGLE GENERALE EST DESORMAIS POSEE : toute valeur mesurable presente a la fois dans l'app et dans Strava doit concorder, quelle qu'elle soit. Le controle compare l'integralite des champs numeriques de chaque seance, plus le parc chaussures. 48 controles a ce jour.",
    "CONTROLE A0 -- LE PLUS IMPORTANT : toute seance loguee SANS reference Strava est signalee comme ecart. Sans lui, il suffirait d'oublier d'ajouter une ligne au referentiel pour qu'une seance echappe silencieusement a toute verification -- precisement le mode de defaillance qui a permis aux cinq derives precedentes de passer inapercues.",
    "CONTRE-TESTE SUR LES TROIS MODES DE DEFAILLANCE CONNUS : valeur de seance faussee (detectee), GEAR derive de 31 km (detecte), seance loguee sans reference (detectee). Les trois font echouer le gate.",
    "RESTE A FAIRE, non traite ici et assume : la phase 2 (verification de PALMARES, RECORDS_PERF 5/10 km, MONTHLY janvier-juillet contre Strava) et les phases 4-5 (reduction structurelle de la surface de saisie manuelle, actuellement 434 valeurs numeriques dans gen.py). Ces phases previennent, elles ne corrigent rien -- elles peuvent attendre l'apres-Nice."
  ]},
  {"build":200,"date":"31 aout 2026","sha":"","tag":"S35 cloturee + S36 structuree autour du depart aux USA","items":[
    "S35 CLOTUREE : 2 seances sur 6, 22,1 km pour 66 cibles, charge 276. La plus petite semaine de la preparation. Longue du 29/08 marquee sautee (aucune activite Strava le 29 ni le 30). Revue de semaine ecrite.",
    "CE QUI SAUVE LA SEMAINE : le seuil du 28/08, tenu a 4 secondes de la cible (4:39 et 4:42 pour 4:45), avec un bloc 2 plus lent que le bloc 1. La serie de trois echecs de discipline (-11, -26, -33 s/km) est cassee.",
    "S36 STRUCTUREE SUR 4 JOURS avant le vol du vendredi 04/09 vers San Francisco. Lundi footing de relance 10 km FC<145, mardi footing + 6 lignes droites, mercredi SEUIL 2x10 min a 4:45/km, jeudi deverrouillage 8 km FC<140.",
    "ARBITRAGE : le seuil est place MERCREDI et non jeudi, pour laisser deux jours entre la seance dure et 11 h d'avion. Il passe de 2x8 a 2x10 min car celui du 28/08 a ete tenu proprement -- meme cible d'allure, alerte Fenix maintenue a 4:40/km.",
    "SEANCE OPTIONNELLE AJOUTEE le dimanche 06/09 a San Francisco, explicitement marquee comme non planifiee : J+2 apres 9 h de decalage. Consigne : 30-40 min tres faciles le matin si le corps suit, marche au soleil sinon. Une bonne acclimatation vaut plus que cette seance.",
    "ACWR RETOMBE A 0,67 (contre 1,52 affiche au 28/08) : la longue de 25 km du 22/08 est sortie de la fenetre 7 jours. Projection avec les 4 seances de la semaine : 0,96 jeudi, zone optimale. Aucun risque de charge.",
    "Volume previsionnel S36 : environ 38 km sur 4 jours, contre 42 cibles. Coherent."
  ]},
  {"build":199,"date":"28 aout 2026","sha":"","tag":"Suite de l'audit : GEAR derive de 31 km + record semi perime","items":[
    "APRES LE BUG D'AOUT (build 198), j'ai cherche si D'AUTRES KPI saisis a la main avaient derive plutot que de repondre que tout etait corrige. Deux nouveaux ecarts trouves.",
    "GEAR DERIVE, confronte au parc Strava reel : Novablast 5 V a 81 km dans l'app contre 112 sur Strava (-31 km), Cascadia 19 a 241 contre 259 (-18 km), Clifton 10 a 1179 contre 1186 (-7 km). Resynchronise.",
    "POURQUOI GEAR NE PEUT PAS ETRE AUTO-CALCULE, contrairement a MONTHLY : les chaussures sont aussi portees en randonnee et a velo, activites hors perimetre course qui comptent pourtant dans le total Strava. La Cascadia 19 a par exemple pris 18 km sur les randonnees du Cantal des 25 et 26/08, invisibles dans SEANCES_BY_WEEK. Ce bloc doit donc rester une recopie manuelle -- mais surveillee.",
    "CONTROLE E2 AJOUTE dans audit_data.py : chaque paire est confrontee a un referentiel Strava, alerte des que l'ecart depasse 5 km. Contre-test realise : en refigeant la Novablast 5 V a 81 km, le controle detecte les -31 km.",
    "RECORD SEMI PERIME dans RECORDS_PERF : il affichait encore 1h52:39 alors que l'effort embarque du 22/08 vaut 1h46:18 (5:02/km sur les 21,1 premiers km). Mis a jour, avec la mention explicite qu'il s'agit d'un effort hors course.",
    "BLOCS VERIFIES ET JUGES NON EXPOSES A LA DERIVE : RECORDS (records officiels), PROJ (cible fixe 3h45), SAISON_EFF (points d'ancrage historiques), ZONES_FC (derive de FCmax), PROFIL, PALMARES (historique fige), VIGILANCE (textuel). HEATMAP est deja calcule depuis SEANCES_BY_WEEK.",
    "LIMITE ASSUMEE ET NON RESOLUE : les champs 'meilleur effort 2026' de RECORDS_PERF sur 5 et 10 km affichent les memes valeurs que les records officiels, ce qui est probablement un reliquat de mise en place. Verifier cela demanderait de rescanner tous les efforts embarques de l'annee -- non fait ici, signale pour ne pas le presenter comme verifie."
  ]},
  {"build":198,"date":"28 aout 2026","sha":"","tag":"AUDIT : le mois d'aout etait fige au 09/08 -- 105 km manquants","items":[
    "AUDIT COMPLET DEMANDE PAR LOIC. Methode : plutot que relancer les controles existants (tous verts, donc sans valeur probante), les donnees de l'app ont ete CONFRONTEES A STRAVA seance par seance sur 5 semaines.",
    "RESULTAT DE LA CONFRONTATION : 18 seances sur 18 exactes, au centieme de kilometre et a l'unite d'effort relatif pres. Randonnees (Puy Mary, Plomb du Cantal) et sortie velo correctement exclues des KPI course. Total aout : 184,44 km cote app, 184,44 km cote Strava, ecart nul.",
    "MAIS UN BUG TROUVE, ET IL ETAIT INVISIBLE : le mois d'aout dans MONTHLY etait fige au 09/08 avec 79 km et 6 sorties, alors que 184 km et 15 sorties avaient ete courus. Ecart de 105 km et 9 sorties, propage a SAISON2026 (1696 km affiches au lieu de 1801) et a tous les totaux de saison.",
    "POURQUOI AUCUN CONTROLE NE L'A VU : audit_kpi verifiait que MONTHLY et SAISON2026 concordent ENTRE EUX. Ils concordaient parfaitement -- sur des donnees fausses toutes les deux. Aucun controle ne confrontait MONTHLY aux seances reellement loguees.",
    "TROISIEME KPI A DERIVER POUR LA MEME RAISON, apres l'ACWR fige a 0,69 puis fausse par erreur de fenetre. Meme correctif applique : MONTHLY n'est plus saisi a la main pour le mois en cours, il est CALCULE depuis SEANCES_BY_WEEK a chaque build. Les mois de janvier a juillet restent des constantes, verifiees activite par activite sur Strava.",
    "VALEURS CORRIGEES : aout 79 -> 184 km, 6 -> 15 sorties, 853 -> 1206 m. Saison 1696 -> 1801 km, 132 -> 141 sorties, 19880 -> 20233 m.",
    "GARDE-FOU AJOUTE dans audit_kpi.py : chaque mois a partir d'aout est desormais confronte aux seances loguees, avec une tolerance de 2 km. Contre-test realise : en refigeant aout a 79 km, l'audit detecte l'ecart de 105 km et bloque la livraison.",
    "VERIFIE PAR AILLEURS : ACWR recalcule independamment (670/1765 = 1,52) identique a la valeur stockee, volumes hebdomadaires S31 a S35 coherents, aucune activite non-course dans les KPI."
  ]},
  {"build":197,"date":"28 aout 2026","sha":"","tag":"Seuil 2x8 logue : la serie de 3 cibles manquees est cassee","items":[
    "SEANCE LOGUEE : 10,03 km en 53:37, FC 157/185, effort relatif 125, cadence 175, Magic Speed 4. Structure : echauffement 3,63 km a 5:48/km, 2x8 min avec 3 min de recuperation, retour au calme 1,98 km. 12 records personnels sur segments.",
    "OBJECTIF TENU A 4 SECONDES PRES. Cible 4:45/km : bloc 1 a 4:39, bloc 2 a 4:42. Amplitude interne aux blocs de 7 s/km seulement (4:36 a 4:43). Point le plus notable : le bloc 2 est LEGEREMENT PLUS LENT que le bloc 1 -- aucune acceleration apres la recuperation, alors que c'etait le piege explicitement annonce dans la fiche.",
    "LA SERIE DE TROIS ECHECS EST CASSEE : -11 s/km le 18/08, -26 le 22/08, -33 le 27/08, puis -4 s/km aujourd'hui. L'echauffement a 5:48/km a lui aussi ete respecte, alors que c'est precisement la que ca derapait les fois precedentes. Resultat obtenu par forte chaleur, apres une nuit courte, en troisieme jour consecutif.",
    "RESSENTI DIFFICILE RAPPORTE PAR LOIC, coherent avec les donnees mais sans lien avec la qualite d'execution : FC max 185 (96 % de FCmax), effort relatif 125, et un footing a 151 la veille. Cout normal d'une seance dure bien menee dans de mauvaises conditions.",
    "ACWR A 1,52, EN ZONE DE SURCHARGE -- MAIS C'EST UN ARTEFACT DE CALENDRIER, pas un signal de fatigue. La longue de 25 km du 22/08 (charge 394) represente a elle seule 59 % de la fenetre 7 jours actuelle. Elle en sort demain : le ratio retombe mecaniquement a 0,63 sans que rien ne change. Projection verifiee pour la longue de samedi : 0,82 a 12 km, 0,87 a 15 km, 0,92 a 18 km. Aucune de ces options ne pose de probleme de charge.",
    "Chaussure Magic Speed 4 mise a jour : 75 -> 85 km. Forme du jour a 46, coherente avec le cumul de la semaine.",
    "VERIFICATION DES KPI DEMANDEE PAR LOIC : ACWR identique entre valeur stockee et calcul runtime (1,52), 22 SVG rendus sur les 4 vues sans aucun vide, 7 gradients sans doublon, 4 fenetres Cockpit sans crash, zero erreur JS. Les 4 audits statiques passent a 0 bug."
  ]},
  {"build":196,"date":"27 aout 2026","sha":"","tag":"Jeudi logue : 3e cible chiffree non tenue d'affilee + ACWR a 1,33","items":[
    "SEANCE LOGUEE : 12,04 km en 1h06:54 a 5:33/km, FC 156/171, effort relatif 151, cadence 173. Cible prescrite : 10 km a 6:00-6:20/km, FC plafond 145, effort attendu ~60.",
    "L'AUTODIAGNOSTIC DE LOIC EST JUSTE SUR LE CONSTAT MAIS INVERSE LA CAUSE. Il attribue la FC haute a la chaleur ; les donnees montrent que c'est l'allure qui l'a produite. Preuve dans le kilometre 1 : 123 bpm au demarrage, puis 155, 159, 163. La FC n'etait pas haute au depart -- elle est montee parce que l'allure etait 30 a 45 s/km trop rapide. La chaleur contribue, elle n'explique pas l'essentiel.",
    "TROISIEME SEANCE CONSECUTIVE A CIBLE NON TENUE : tempo du 18/08, longue du 22/08, footing du 27/08. Aggravation notable : cette fois la cible n'etait pas une allure difficile a percevoir, mais un PLAFOND DE FC -- le type de consigne tenu parfaitement debut aout (132 bpm le 07/08, 138 le 11/08).",
    "POINT POSITIF REEL : apres 1150 m de denivele en randonnee mardi et mercredi, aucune douleur, aucune jambe lourde, cadence stable a 86-87 sur les 12 km. La capacite de recuperation n'est pas en cause -- le probleme est bien decisionnel.",
    "SEUIL DE VENDREDI ASSOUPLI en consequence : 4:45/km au lieu de 4:40, recuperation portee de 3 a 3 min 30. ALERTE D'ALLURE DESORMAIS PRESCRITE comme obligatoire sur la Fenix 6 Pro (seuil bas 4:40/km) : sur trois seances consecutives, la volonte seule a echoue trois fois.",
    "MERCREDI 26/08 marque saute (indisponibilite, randonnee de 7 km et 449 m D+ effectuee a la place, hors perimetre course).",
    "ACWR A 1,33 -- AU-DESSUS DU SEUIL DE RISQUE de 1,3, consequence directe du surcout de jeudi (151 au lieu de 60 attendu). Forme du jour redescendue a 59.",
    "VERIFICATION COMPLETE DES GRAPHIQUES ET KPI demandee par Loic : 22 SVG rendus sur les 4 vues, aucun vide, 7 gradients sans doublon, les 4 fenetres Cockpit sans crash, ACWR coherent entre valeur figee et calcul runtime, zero erreur JS. Les 4 audits statiques passent : 0 bug, 0 incoherence, 0 dette, 0 ecart KPI."
  ]},
  {"build":195,"date":"25 aout 2026","sha":"","tag":"S35 restructuree sur 3 jours + ACWR recale sur le calendrier","items":[
    "LUNDI 24/08 MARQUE SAUTE sur fatigue persistante apres les 25 km de samedi (charge 394) et la sortie velo de dimanche. Verifie sur Strava : aucune activite ce jour.",
    "MARDI ET MERCREDI passes en repos : indisponibilite pour contraintes familiales. S35 se joue donc sur JEUDI, VENDREDI, SAMEDI uniquement.",
    "ARBITRAGE : sur 3 jours consecutifs apres une semaine a 605 de charge, on ne cumule pas deux seances dures. Jeudi = footing de reprise FC plafonnee 145 (5 jours sans courir, les jambes seront fraiches et l'envie d'accelerer forte). Vendredi = seuil 2x8 min a 4:40/km, seule qualite de la semaine. Samedi = longue RAMENEE DE 18 A 15 KM, troisieme jour consecutif apres un seuil.",
    "AUCUN BLOC ALLURE MARATHON cette semaine : le prochain est prevu en S40, sur des jambes fraiches. Apres l'echec de discipline du 22/08, mieux vaut ne pas retenter dans une semaine tronquee.",
    "Volume S35 : environ 36 km reels contre 66 cibles. Ecart assume, coherent avec les contraintes.",
    "CORRECTIF ACWR : la reference etait calee sur la derniere seance loguee, pas sur le calendrier. Des qu'un jour passait sans courir, la valeur figee au build divergeait de celle recalculee en direct par l'app (constate le 25/08 : 1,29 fige contre 1,04 reel). La fenetre glissante 7/28 jours suit desormais la date du jour, dans gen.py comme dans audit_kpi.py. La bonne valeur est 1,04."
  ]},
  {"build":194,"date":"24 aout 2026","sha":"","tag":"Correctif : la materialite du build 193 etait invisible sur iPhone","items":[
    "SIGNALE PAR LOIC : apres la livraison du build 193, aucune difference perceptible sur telephone. Le CSS etait pourtant bien deploye et verifie.",
    "CAUSE REELLE : sur iOS et WebKit, la pseudo-classe CSS :active NE SE DECLENCHE PAS lors d'un appui tactile tant qu'aucun ecouteur touchstart n'existe sur le document. Comportement historique de WebKit que j'aurais du anticiper : toute la couche de materialite fonctionnait au clic en navigateur, et restait totalement inerte au doigt.",
    "CORRECTIF : ajout d'un ecouteur touchstart vide et passif sur document. Il n'intercepte rien, ne modifie aucun comportement, ne change aucune UX -- il ouvre uniquement le droit aux etats :active sur mobile.",
    "AMPLITUDE PORTEE DE 3 A 5 PX : a 3 px l'enfoncement etait trop discret pour etre percu au doigt sur un ecran de telephone. Ajout de will-change:transform pour fluidifier le rendu.",
    "SPECIFICITE RENFORCEE : les cartes portent aussi la classe .rv-show (animation de reveal) qui declare transform:none, et l'app possedait deja une regle .sem-carte:active en transform:scale(.975). Les selecteurs de la couche ont ete doubles pour passer devant proprement, sans recourir a !important.",
    "VERIFIE PAR INSPECTION DU MOTEUR DE RENDU (CDP, etat :active force) : transform calcule au repos = matrix(1,0,0,1,0,0), en appui = matrix(1,0,0,1,0,5). La regle s'applique. Mes tests precedents a la souris echouaient simplement parce que l'appui simule etait trop bref pour capturer l'etat transitoire -- le CSS n'a jamais ete en cause.",
    "UX toujours strictement inchangee : aucune structure, navigation, fonctionnalite ou donnee touchee."
  ]},
  {"build":193,"date":"24 aout 2026","sha":"","tag":"Couche de materialite tactile (UI seule, UX inchangee)","items":[
    "DEMANDE DE LOIC : reprendre le langage d'interactions physiques de yui540 (surfaces qui s'enfoncent, ressort au relachement) en CONSERVANT le systeme de couleurs semantiques, qui porte du sens dans cette app -- rouge sur les ecarts d'allure, teal sur les cibles tenues, ambre sur la vigilance. Pas de monochrome.",
    "CONTRAINTE EXPLICITE RESPECTEE : UI SEULEMENT. Aucune structure, navigation, fonctionnalite ou donnee n'a ete modifiee. La couche est purement additive en CSS, ciblee sur les classes deja pressables de l'app.",
    "PRINCIPE : chaque surface pressable repose sur une ombre portee de 3 px. A l'appui elle descend et l'ombre se resorbe -- l'objet touche le fond. Au relachement, un ressort (cubic-bezier 1.56) la fait legerement depasser avant stabilisation.",
    "ELEMENTS TRAITES : cartes de semaine et de seance, tuiles de course, widget du jour, tuile Capital, selecteurs du Cockpit, chips de navigation, cellules de calendrier, barre d'onglets. Les petits controles basculent lateralement de 2 degres a l'appui, les grandes cartes s'enfoncent a plat.",
    "ACCESSIBILITE : prefers-reduced-motion respecte -- toute la couche est neutralisee pour les utilisateurs qui l'ont active.",
    "VERIFICATION DE NON-REGRESSION UX, avant/apres : nombre d'elements interactifs identique sur les 4 vues, longueur de texte identique, hauteur de page identique, ouverture de semaine et de fiche fonctionnelles, zero erreur JS. Audit visuel 0 defaut, audit runtime 0 anomalie.",
    "NOTE : un POC d'accueil en grille bento a ete produit en parallele (fichier isole, hors app) pour evaluer une refonte plus profonde. Il reste gele jusqu'apres Nice, conformement a l'arbitrage pris -- seule la couche de materialite, sans risque structurel, est livree ici."
  ]},
  {"build":192,"date":"22 aout 2026","sha":"","tag":"Sortie longue Vaise-Trevoux loguee (25 km) + correctif graphique fiche vide","items":[
    "SEANCE LOGUEE : Lyon-Vaise -> Trevoux par la voie bleue, 25,05 km en 2h03:35, allure moyenne 4:56/km, FC 166/183, effort relatif 394 -- la charge la plus haute de la saison, devant le trail de 27 km (246).",
    "DERIVE D'ALLURE LA PLUS LONGUE DEPUIS LE DEBUT DU SUIVI : les 5 tranches de 5 km (4:59, 4:58, 4:52, 4:49, 5:01) sont toutes tres en dessous des cibles prescrites (5:40-6:00 puis 5:20). Contrairement aux derives precedentes (1 a 2 km), celle-ci a dure l'integralite des 25 km.",
    "RECORD PERSONNEL OFFICIEUX DE DEMI-MARATHON dans la foulee : 1h46:18 (5:02/km) sur les 21,1 premiers km, 6 minutes plus rapide que le PB officiel (1h52:39).",
    "NUTRITION ET HYDRATATION : deux arrets aux fontaines prevues (Fontaines-sur-Saone, Neuville-sur-Saone), tous deux bien geres malgre un imprevu (fontaine absente) au second. Aucune douleur sur l'ensemble du parcours.",
    "Mercredi (2x4x100m) loguee retroactivement : 7,02 km, effort relatif 38, verdict B- (0/8 repetitions dans la cible malgre un chrono explicite). Jeudi et vendredi marques en repos (courbatures post-mercredi). Chaussure Novablast 5 V mise a jour (56 -> 81 km).",
    "ACWR recalcule automatiquement par gen.py : 0,84 -> 1,29 (aigu 605, chronique 1871), juste sous le seuil de risque de 1,3.",
    "BUG CORRIGE (trouve par l'audit runtime) : ouvrir une fiche de seance avec un tableau 'segments' VIDE (cas du repos du vendredi) faisait planter le graphique de structure -- initBarre() lisait segments[segments.length-1] sur un tableau vide. Garde ajoutee a l'appel et dans la fonction elle-meme.",
    "INCIDENT DE SESSION DOCUMENTE : une reinitialisation de l'environnement de travail a cause une confusion sur la structure du plan S34, menant a un premier correctif errone (jamais livre). Diagnostic final : gen.py source etait a jour (build 191, correctement synchronise via les push precedents) ; l'erreur venait d'une mauvaise lecture des index de tableau de ma part, pas d'un fichier perime. Corrige en reappliquant les logs directement dans gen.py, verifie par les 8 controles du gate avant livraison."
  ]},
  {"build":191,"date":"20 aout 2026","sha":"","tag":"Phase 0 UX : bugs visibles corriges + audit visuel au gate","items":[
    "PREMIER AUDIT REALISE EN REGARDANT L'APPLICATION, captures d'ecran a l'appui, et non en lisant son code. Le rendu visuel etait le dernier axe non couvert : six defauts trouves en quatre captures, dont deux bugs de donnees qu'aucun des sept controles automatiques n'avait detectes.",
    "BUG 1 CORRIGE -- l'accueil affichait « U0001F3C1 NICE » au lieu du drapeau a damier. La sequence etait ecrite avec un U MAJUSCULE, syntaxe Python que JavaScript ne reconnait pas et laisse telle quelle. Remplace par l'emoji litteral.",
    "BUG 2 CORRIGE -- le compte a rebours divergeait entre les vues : J-80 sur l'accueil, J-81 sur Courses, pour la meme course. TROIS formules coexistaient, dont une comparant a `new Date()` non remis a minuit, ce qui comptait les heures ecoulees dans la journee comme un jour entier. Fonction unique _joursAvant() : 8 formules remplacees, J-80 partout.",
    "BUG 3 CORRIGE -- l'onglet Seances ne se positionnait sur la semaine en cours qu'a la PREMIERE ouverture ; toute visite suivante repartait en haut du plan, soit en avril, avec environ 1200 px a faire defiler. Le saut est desormais systematique. Verifie : 1re et 2e visite arrivent toutes deux sur la semaine du jour.",
    "BUG 4 CORRIGE -- le bouton flottant « En cours » masquait du contenu (constate : « Bloc specifique marathon » recouvert). Il compensait le defaut precedent ; celui-ci etant corrige, le bouton est desactive.",
    "NOUVEL AUDIT scripts/audit_visuel.py, branche en phase 3 du gate (8e controle, 15 s). Il verifie ce qu'aucun autre ne verifiait : sequences d'echappement affichees telles quelles, coherence des compteurs entre vues, debordement horizontal, cibles tactiles sous 44 px, textes sous le plancher de lisibilite, elements fixes masquant du contenu, collisions de texte.",
    "DEUX FAUX POSITIFS DE MON PROPRE AUDIT CORRIGES avant mise en service : le Cockpit etait signale en debordement alors que sa barre d'onglets a un defilement horizontal voulu, et le bouton flottant etait signale comme masquant sur toutes les vues alors qu'il y est en opacity 0. Les detecteurs tiennent desormais compte de overflow-x et de l'opacite.",
    "CONTRE-TEST : en reinjectant l'emoji casse, le gate detecte et bloque. Il attrape donc exactement le defaut qui etait parti en production.",
    "ETAT : 0 defaut visible. 9 ameliorations restantes documentees (cibles tactiles, tailles de police, chevauchement d'un badge) -- elles relevent de la refonte, pas de la correction, et sont gelees jusqu'apres Nice."
  ]},
  {"build":190,"date":"19 aout 2026","sha":"","tag":"Radar : 8e axe DISCIPLINE D'ALLURE et ponderation Nice revue","items":[
    "CONSTAT A L'ORIGINE : le radar mesurait sept qualites de coureur, mais l'objectif de Loic n'est pas d'etre complet, c'est de courir 3h45 a Nice. Trois axes sur sept ne servaient pas cet objectif, et surtout il manquait la mesure de ce qui decide reellement d'un marathon.",
    "L'axe ALLURE MARATHON mesure la CAPACITE a produire 5:20 au bon cout cardiaque. Cette capacite est acquise : prouvee le 13/08 avec un bloc de 6 km a 5:17 et 11 s/km d'amplitude. Ce n'est donc plus la contrainte. La contrainte, c'est de refuser d'aller plus vite -- et rien ne le mesurait.",
    "NOUVEL AXE DISCIPLINE D'ALLURE : ecart absolu moyen entre l'allure cible fixee et l'allure realisee, sur les seances a cible chiffree. Bareme 0 s d'ecart = 99, 30 s = 1. Valeur actuelle 48/99, ecart moyen 16 s/km, 3 seances tenues sur 5. Les trois echecs sont documentes : tempo du 18/08 (5:09 pour 5:20) et 8x100 m du 19/08 (aucune des 8 repetitions a la cible).",
    "PONDERATION NICE REVUE. Discipline d'allure 25 %, Allure marathon 22 %, Endurance 20 %, Durabilite 16 %, Seuil 10 %, Constance 7 %. VITESSE PASSE A 0 % (etait 5 %) : un score eleve n'aide pas sur 42 km, et le valoriser entretiendrait exactement le reflexe qu'on cherche a corriger. L'axe reste affiche, il n'entre plus dans la note Nice.",
    "RADAR RECALCULE SUR DONNEES A JOUR : Vitesse 92, Montagne 89 (957 m D+ max), Endurance 83 (43 km max, 54 km/sem contre 59 au precedent calcul), Seuil 79, Durabilite 76, Constance 55 (etait 68, penalisee par la variabilite de volume de 24 % liee aux deplacements), Discipline d'allure 48, Allure marathon 44. General 71, note Nice ponderee 62.",
    "Aide de la carte mise a jour : sept qualites devient huit, avec l'explication du nouvel axe."
  ]},
  {"build":189,"date":"19 aout 2026","sha":"","tag":"Mercredi loguee : 8 repetitions sous la cible, aucune a 22,0 s","items":[
    "SEANCE LOGUEE : 7,02 km en 47:23, FC moyenne 137/182 max, effort relatif 38, cadence 86. Sortie a allure tres facile avec une amie (d'ou le faible kilometrage), incluant les 2x4x100 m prevus. Tableau complet des 8 repetitions integre dans la revue (temps, vitesse, ecart a la cible, FC, cadence, par bloc).",
    "RESULTAT PEDAGOGIQUE : aucune des 8 repetitions n'a touche la cible de 22,0 s. Toutes couru sous la cible (donc plus vite), entre 15 et 19 s selon les repetitions, soit 3 a 7 secondes plus vite que demande. La plus rapide (15 s, 24 km/h) est quasiment le maximum absolu de Loic. Meme avec un chrono explicite et verifiable au dixieme -- contrairement a une allure GPS bruitee -- l'instinct d'acceleration a domine.",
    "SIGNAL DE FATIGUE NET ENTRE LES DEUX BLOCS : moyenne 15,75 s sur le bloc 1 contre 17,75 s sur le bloc 2 (plus lent de 2 s), FC 146 -> 164 (+18 bpm) pour une vitesse moindre, cadence 99,4 -> 92,6. Signature classique de fatigue neuromusculaire, coherente avec le tempo de la veille (effort relatif 173) pas totalement digere.",
    "POINT POSITIF NOTABLE : adherence quasi parfaite sur les temps de recuperation -- 90, 89, 90 s sur les recups intra-bloc (cible 90) et 240 s pile sur la recuperation inter-blocs. La competence de tenir un chiffre existe, elle s'exprime sur la recuperation et pas encore sur l'effort.",
    "Verdict B-. Graphique de structure resynchronise avec les temps REELLEMENT courus (segments bases sur les laps Strava exacts, pas sur la prescription) : total 47 min 23 s, identique au temps mesure. Verifie dans le navigateur apres ouverture de la fiche : 5 segments corrects, tableau de 8 repetitions rendu (14 lignes), fiche marquee FAIT, zero erreur JS.",
    "ACWR recalcule automatiquement : 0,91 -> 0,84."
  ]},
  {"build":188,"date":"18 aout 2026","sha":"","tag":"Mercredi : vitesse chronometree en 2 blocs de 4x100 m","items":[
    "SEANCE DE MERCREDI REMPLACEE, apres discussion approfondie avec Loic sur trois formats successifs (8x30s, 2x(5x30s), puis 2x(4x100m) chronometres). Format retenu : deux blocs de 4x100 m a 22,0 secondes (16,4 km/h), separes par 4 minutes de recuperation complete.",
    "RAISON DU CHOIX : a duree de repetition egale, un temps chronometre sur 100 m se verifie au dixieme de seconde a chaque effort, contre une allure GPS sur 30 s bruitee de 10 a 15 s/km. La seance donne donc 8 retours d'information sur la capacite a tenir un chiffre impose, exactement la competence travaillee depuis le 09/08. Cout mesure : 176 s de course a haute vitesse sur le plat, contre 300 s pour le format 2x(5x30s) envisage un temps -- soit 41 % de moins pour un objectif pedagogique superieur.",
    "STRUCT ET SEGMENTS RECONSTRUITS ENSEMBLE, avec des durees calculees pour etre exactement coherentes : echauffement 1200 s, bloc 1 358 s, recuperation inter-blocs 240 s, bloc 2 358 s, retour au calme 600 s. Total graphique 45 min 56 s pour une fiche annoncant ~46 min.",
    "VERIFIE DANS LE NAVIGATEUR, pas seulement dans les donnees : audit_seances renvoie 0 bug sur cette fiche, et les 5 segments ont ete inspectes directement dans le DOM apres ouverture de la carte -- couleurs, hauteurs et titres corrects, les deux blocs de sprint affichant la meme hauteur (coherent avec la consigne \u00ab meme cible sur les deux blocs \u00bb)."
  ]},
  {"build":187,"date":"18 aout 2026","sha":"","tag":"S34 restructuree : vitesse courte, repos, longue avancee au samedi","items":[
    "CONTRAINTE : Loic ne peut pas courir dimanche, la sortie longue passe au SAMEDI 22/08. Il souhaite par ailleurs conserver une seance de vitesse mercredi malgre le cout du tempo de mardi (effort relatif 173).",
    "ARBITRAGE : la seance de vitesse est conservee mais ramenee a un format NEUROMUSCULAIRE court -- 8x30 s avec recuperation complete de 90 s -- au lieu d'un fractionne classique. Le travail court avec recuperation complete developpe la vitesse sans produire de lactate ni de casse musculaire. Allures calibrees sur une VMA estimee a 14,1 km/h (a partir du PB 5 km de 22:52 couru a environ 93 % de VMA) : 4:03/km sur les repetitions 1-2, 3:51/km sur les 3 a 6, 3:41/km sur les 7-8. Plafond d'effort relatif fixe a 90.",
    "CONTREPARTIE : le footing du jeudi PERD ses lignes droites. La touche de vitesse est faite mercredi ; en remettre jeudi compromettrait la longue.",
    "VENDREDI passe en repos complet (la seance de renforcement est remplacee). Loic a constate lui-meme que deux jours de repos transforment son etat de forme ; celui-ci conditionne directement la qualite du samedi.",
    "SAMEDI 22/08 -- 28 km dont 12 a allure marathon, avance d'un jour. Consigne principale reprise de l'analyse de mardi : montre au kilometre 1 ET au kilometre 2, pas au 5. Option ajoutee : decouper le bloc en 2x6 km si la chaleur est forte, et privilegier l'allure sur la distance (24 km propres valent mieux que 28 km degrades).",
    "ACWR projete au 22/08 : 1,26 avec ce format, contre 1,31 avec un fractionne classique et 1,23 sans aucune vitesse. Reste sous le seuil de 1,3.",
    "GARDE-FOU ACTIVE : le graphique de structure du mardi affichait encore le seuil 3x12 prescrit alors que la seance realisee etait un tempo continu. Resynchronise -- c'est exactement le defaut corrige au build 181, et l'audit A8 le surveille desormais sur les seances a venir.",
    "CORRECTION EN COURS DE ROUTE : la premiere version de la restructuration ciblait les seances par index de tableau et a ecrase la sortie longue. Reprise en ciblant par identifiant. Verifie apres correction : les six seances de S34 sont correctes et l'audit seances renvoie 0 bug."
  ]},
  {"build":186,"date":"18 aout 2026","sha":"","tag":"S34 : tempo continu requalifie + cloture de S33","items":[
    "LUNDI 17/08 marque en report : chaleur matinale et mauvaise nuit, sortie decalee au mardi soir.",
    "MARDI 18/08 LOGUE : 12,04 km en 1h02:11 a 5:09/km, FC 162/182, effort relatif 173, cadence 171. Sortie du soir accompagnee. 45 records personnels sur segments.",
    "SEANCE REQUALIFIEE EN TEMPO CONTINU. Objectif annonce par Loic : tenir l'allure marathon a 5:20. Realise : 5:09 de moyenne, soit 11 secondes au kilometre plus vite, avec 7 kilometres sur 12 sous 5:15, un depart a 4:58 puis 4:53 et un dernier kilometre a 4:34. Amplitude 55 s/km, contre 11 s/km sur le bloc reussi du 13/08. Ce n'est pas une seance d'allure marathon ratee, c'est une bonne seance de seuil : la fiche est requalifiee en consequence, la semaine prevoyait justement un seuil 3x12 ce jour-la.",
    "POINT COACH CENTRAL : Loic percoit la seance comme reussie a 5:20. L'ecart entre la perception et la mesure est precisement le mecanisme identifie comme axe de travail prioritaire (Allure Marathon 42/99 au profil). Consigne pour la longue de dimanche : regarder la montre aux kilometres 1 ET 2, pas au 5 -- aujourd'hui les deux premiers sont partis 25 secondes trop vite avant tout controle.",
    "Cardiaque : 162 de moyenne pour une cible marathon a 148-160, derive de 148 a 168, pic a 182 (95 % de FCmax). La chaleur joue mais n'explique pas 11 s/km. Effort relatif 173, le plus eleve depuis le trail du 09/08.",
    "CLOTURE DE S33 : deverrouillage du dimanche marque saute (retour de La Rochelle, seance explicitement optionnelle), et revue de semaine ecrite. Bilan S33 : 4 seances, 39,7 km pour 52 prevus, charge 292, zero douleur, et la premiere seance d'allure marathon reussie de la preparation.",
    "ACWR recalcule : 1,13 -> 0,91."
  ]},
  {"build":185,"date":"15 aout 2026","sha":"","tag":"Correction : les Clifton 10 n'ont jamais quitte la rotation","items":[
    "CORRECTION APPORTEE PAR LOIC : les Clifton 10 restent dans sa rotation, simplement moins utilisees. Elles n'ont jamais ete retirees. Le flag Strava (retired=false) etait donc juste ; c'est mon interpretation qui etait fausse.",
    "PORTEE DE L'ERREUR : je ne me suis pas contente d'une donnee inexacte, j'ai qualifie sur cette base des choix de Loic comme des ECARTS. La revue du 05/08 parlait d'une paire « attrapee par reflexe » et suggerait de la sortir de la maison ; la revue de S32 comptait deux « ecarts materiels » ; une slide du Rewind S32 affichait « LES DEUX ECARTS ». Un seul de ces ecarts existait reellement, celui des Novablast route sur 662 m de sentier technique.",
    "TEXTES CORRIGES : revue du 28/07, revue du 05/08, revue de S32, slide du Rewind S32, conseil coach de S31. Le fond technique est conserve -- 1179 km reste un kilometrage eleve et l'amorti est entame -- mais formule comme une RECOMMANDATION (garder cette paire pour les footings courts, privilegier les paires recentes sur les seances longues ou rapides) et non comme un constat de retrait deja acte.",
    "Le commentaire de la seance du 05/08 portait aussi la mention « paire retiree de la rotation le 27/07 pour delamination » : corrige en « paire la plus usee du parc ».",
    "AUDIT : liste RETIREES videe a nouveau, cette fois pour la bonne raison. Le controle d'usure E1 reste actif et continue de signaler les 1179 km -- l'usure est un fait mesurable, le statut de rotation est une decision qui appartient a Loic.",
    "ALLER-RETOUR ASSUME : j'ai vide cette liste au build 179 en me fiant a Strava, l'ai retablie au build 184 en me fiant a une revue que j'avais moi-meme ecrite, et la revide ici sur la seule source qui fait autorite -- Loic. Une donnee que je deduis de mes propres ecrits anterieurs n'est pas une source."
  ]},
  {"build":184,"date":"15 aout 2026","sha":"","tag":"Samedi : sortie de liaison ecourtee, et un signal de forme","items":[
    "SEANCE NON PLANIFIEE AJOUTEE (samedi 15/08, La Rochelle sous la pluie) : 8,04 km en 48:08 a 5:59/km, FC 139/152, effort relatif 50, cadence 175, 39 m D+. Ecourtee volontairement par Loic pour preserver la journee et la recuperation. Deux records personnels sur segments.",
    "LECTURE CARDIAQUE -- LE POINT IMPORTANT : FC moyenne 139 pour 5:59/km, contre 138 bpm pour 6:09/km mardi. Soit 11 secondes au kilometre plus vite pour une pulsation de plus. Derive nulle sur la sortie : 138,8 bpm sur les 4 premiers kilometres, 139,6 sur les 4 derniers a allure identique.",
    "CONCLUSION COACH : la fatigue rapportee par Loic est reelle mais son origine n'est pas l'entrainement. Six a sept heures de sommeil par nuit depuis le debut du sejour, 7 heures de voiture mercredi, chaleur et humidite continues. Le moteur repond bien ; c'est la recuperation qui est entamee. Distinction importante : cela se corrige en dormant, pas en reduisant la charge.",
    "RESERVE MINEURE : amplitude d'allure de 34 s/km avec un 2e kilometre a 5:40. Sans consequence sur un footing de liaison, mais c'est le meme reflexe recurrent -- le corps part quand il se sent bien, meme un jour de fatigue.",
    "BILAN S33 A CE STADE : 4 seances, 39,7 km pour 52 cibles (-24 %), charge 292. Semaine allegee assumee, coherente avec le deplacement. ACWR 1,13.",
    "REGRESSION CORRIGEE (introduite par moi au build 179) : j'avais vide la liste RETIREES d'audit_data en me fiant au flag Strava (retired=false partout), alors que les Clifton 10 avaient ete retirees de la rotation le 27/07 sur decision coach, pour delamination de semelle. Le controle A5 cessait donc de signaler toute prescription de paire retiree. Liste retablie, et le controle d'usure E1 s'applique desormais aussi aux paires retirees -- l'usure est un fait, independant du statut."
  ]},
  {"build":183,"date":"13 aout 2026","sha":"","tag":"La Rochelle : premiere seance d'allure marathon reussie","items":[
    "SEANCE LOGUEE (jeudi 13/08, avancee d'un jour) : 11,36 km en 1h01:58 a 5:27/km de moyenne, FC 155/171, effort relatif 128, cadence 174, 52 m D+. Novablast 5 V. Structure : echauffement 2,27 km, bloc 6 km a allure marathon, retour au calme 3,09 km.",
    "BLOC ALLURE MARATHON -- 5:20,9 / 5:15,3 / 5:11,2 / 5:18,9 / 5:22,2 / 5:12,7. Moyenne 5:17/km pour une cible a 5:20, ecart moyen absolu 4,2 secondes, AMPLITUDE 11 SECONDES. Pour situer : 128 s/km sur la fin du trail de dimanche, 15 s/km sur l'EF plafonnee de mardi. Meilleure regularite obtenue sur allure specifique que sur un footing deux jours plus tot, et sur un terrain inconnu.",
    "RESERVE : trois kilometres sous 5:15 (le 3e a 5:11, le 6e a 5:13). L'exercice reste reussi mais le schema est reconnaissable -- acceleration quand la sensation est bonne, et dernier kilometre le plus rapide du bloc.",
    "SIGNAL CARDIAQUE, plus parlant que l'allure : FC de 151 a 165 sur les 6 km, soit +13,5 bpm A ALLURE CONSTANTE. Les trois derniers kilometres sont 2 secondes plus lents que les trois premiers mais 5 pulsations plus hauts. Cible 148-160 depassee sur la fin.",
    "CONTEXTE EXPLICATIF : environ 5h30 de sommeil, 7 heures de voiture la veille, chaleur et humidite cotieres, troisieme seance en trois jours. Decouplage limite a 2,5 %, donc reponse physiologique saine. Mais effort relatif 128 contre 53 mardi et 61 mercredi.",
    "PIED : aucune douleur sur une seance a 5:17 de moyenne, terrain inconnu. Meilleure confirmation depuis la reprise.",
    "ACWR recalcule automatiquement : 0,87 -> 1,06 (aigu 516, chronique 1943). Retour en haut de zone optimale, coherent avec le cout de la seance.",
    "DECISION : repos vendredi valide. Le deverrouillage de dimanche reste optionnel -- si l'organisation familiale ne le permet pas, la semaine est deja reussie a trois seances."
  ]},
  {"build":182,"date":"12 aout 2026","sha":"","tag":"Audit des 132 seances : chaussure ambigue et ordre d'affichage","items":[
    "AUDIT COMPLET DEMANDE PAR LOIC apres le bug du graphique. Nouveau script scripts/audit_seances.py : il confronte entre elles les differentes descriptions d'une meme seance (titre, metriques, struct, segments, chaussure, realise) sur les 132 fiches, selon 8 axes.",
    "BUG 1 -- CHAUSSURE AMBIGUE SUR 23 SEANCES A VENIR. La constante NOVA valait « ASICS Novablast 5 », sans suffixe, alors que DEUX Novablast 5 coexistent au parc : la J (709 km, en fin de zone de remplacement) et la V (56 km). Le plan prescrivait donc une paire impossible a identifier, de S34 a S53. NOVA designe desormais explicitement la V. Au passage, la constante CLIF portait un nom trompeur : elle n'a jamais contenu de Clifton.",
    "BUG 2 -- ORDRE D'AFFICHAGE NON CHRONOLOGIQUE, sur 12 semaines. Les seances etaient affichees dans leur ordre de stockage, qui suit la construction du plan et non le calendrier. Sur S42, la sortie longue du 18/10 apparaissait AVANT le renforcement du 15/10 ; sur S32, le trail du 09/08 avant les seances des 07 et 08. Tri par date ajoute a l'affichage, sans modifier le stockage.",
    "Le numero affiche suivait lui aussi l'index de stockage : apres tri, la semaine 42 affichait « seance 5, 6, 4 ». Il reflete desormais la position chronologique reelle. Verification : 17 fiches ouvertes une par une apres tri, toutes correctes, zero erreur JS.",
    "VERIFIE ET SAIN : chainage des segments (aucun trou ni chevauchement sur les 132 fiches), coherence distance/duree/allure, champs essentiels presents, coherence type de seance et FC cible.",
    "SIGNALE SANS CORRECTION : 11 seances de renforcement sans chaussure prescrite (normal, ce sont des seances a domicile) et 5 seances passees ou le realise depasse largement le prescrit -- ce sont des faits d'entrainement, pas des defauts de donnees."
  ]},
  {"build":181,"date":"12 aout 2026","sha":"","tag":"Graphique de structure desynchronise (signale par Loic)","items":[
    "BUG SIGNALE PAR LOIC SUR CAPTURES D'ECRAN : la fiche de la longue du 14/08 decrit un bloc allure marathon, mais le graphique « Structure de la seance » n'affichait que deux blocs verts, sans bloc orange, et un total de 104 minutes pour une seance annoncee a 90.",
    "CAUSE : la fiche a DEUX descriptions de la meme seance. 'struct' est le texte lu par l'utilisateur, 'segments' alimente le graphique. En restructurant S33 au build 178, j'ai mis a jour titre, metriques, objectif et struct -- mais pas segments. Le graphique continuait donc d'afficher la longue de 18 km qu'il remplacait, test de gel compris.",
    "CORRECTIF : segments reconstruits en coherence avec la seance reelle -- echauffement 31 min (vert), bloc allure marathon 29 min (ORANGE, hauteur 72 pour le distinguer visuellement), retour au calme 28 min (vert). Total 88 min contre ~90 annonces.",
    "GARDE-FOU A8 AJOUTE dans audit_data.py : pour toute seance A VENIR, le total du graphique est confronte a la duree annoncee (tolerance 15 min), et tout bloc specifique decrit dans struct doit exister dans segments. Les seances passees sont exclues du controle : leurs segments documentent legitimement la prescription d'origine.",
    "Contre-test realise : en reinjectant les anciens segments, l'audit detecte bien « la fiche decrit un bloc Bloc specifique absent du graphique de structure » et bloque la livraison.",
    "Note de methode : deux champs decrivant la meme realite sans lien structurel, c'est exactement le schema qui avait produit les deux bugs d'ACWR. Le controle automatique remplace ici la vigilance manuelle."
  ]},
  {"build":180,"date":"12 aout 2026","sha":"","tag":"S33 mercredi : EF + 6x100 m en negative split","items":[
    "SEANCE LOGUEE : 10,2 km en 59:16 a 5:49/km, FC moyenne 140, FC max 186, effort relatif 61, cadence 175, 36 m D+. Novablast 5 J. Cinq records personnels sur segments.",
    "NEGATIVE SPLIT REUSSI sur les 6 lignes droites de 100 m : 23 s, 21 s, 22 s, 19 s, 19 s, 16 s. Soit 30 % de gain entre la premiere et la derniere, avec une seule rupture d'une seconde sur la ligne 3. Sur six repetitions menees a la sensation, c'est un controle d'allure remarquable.",
    "POINTE FINALE A 24,3 KM/H (2:28/km), la plus rapide de la saison -- a comparer aux 3:16/km du 21 juillet et aux 2:57/km du 27 juillet.",
    "POINT TECHNIQUE POSITIF : la cadence monte a 94 sur la derniere ligne contre 85-88 sur le reste de la seance. L'acceleration se fait par la frequence et non par l'amplitude de foulee -- mecanisme le plus economique et le moins traumatisant pour le pied. Rien a corriger.",
    "VIGILANCE : FC max 186, soit 97 % de FCmax, sur une seance etiquetee footing. Sans gravite sur 16 secondes, mais l'effort relatif passe a 61 contre 53 la veille a volume identique. La seance etait une EF avec un vrai travail neuromusculaire au bout.",
    "AMPLITUDE D'ALLURE SUR LA PARTIE EF : 39 s/km (5:45 a 6:24) contre 15 s/km mardi. Coherent avec une seance qui preparait des accelerations, mais c'est le schema a surveiller : vendredi, sur le bloc a 5:20, cette amplitude devra retomber sous 6 secondes.",
    "ACWR recalcule automatiquement : 0,81 -> 0,87 (aigu 444, chronique 2037). Novablast 5 J portee a 709 km."
  ]},
  {"build":179,"date":"11 aout 2026","sha":"","tag":"Chaussure corrigee + alerte usure Clifton 10","items":[
    "CORRECTION SIGNALEE PAR LOIC : la seance du 11/08 a ete courue avec les HOKA Clifton 10, et non les Novablast 5 V. Strava avait conserve la chaussure par defaut. Corrige.",
    "CE QUE CETTE CORRECTION A REVELE : les Clifton 10 affichent 1179 km, tres au-dela de la zone de remplacement (700-900 km). A ce kilometrage la mousse d'amorti ne restitue plus grand-chose et les contraintes remontent dans le pied, la cheville et le tibia. Loic sort precisement d'un dossier pied. Elles ne sont pas en cause sur cette seance (zero douleur, effort relatif 53) mais n'ont plus leur place sur une recuperation, encore moins sur une longue.",
    "Kilometrages du parc realignes sur Strava : Clifton 10 a 1179 km, Novablast 5 J a 699 km (etait 689).",
    "Les trois seances a venir de S33 prescrivent desormais explicitement la Novablast 5 V (56 km), y compris pour le deplacement a La Rochelle.",
    "BUG D'AUDIT CORRIGE, et il masquait le probleme : audit_data classait les Clifton 10 comme « retirees » alors que Strava indique retired=false sur toutes les paires. Or le controle d'usure E1 exclut justement les paires retirees -- cette classification erronee neutralisait donc l'alerte sur la paire la plus usee du parc. Liste RETIREES videe ; l'audit remonte maintenant correctement le risque.",
    "Rappel de methode : c'est encore une observation de Loic qui a declenche la decouverte. Un audit ne trouve que ce qu'on lui a appris a chercher."
  ]},
  {"build":178,"date":"11 aout 2026","sha":"","tag":"S33 restructuree autour du deplacement a La Rochelle","items":[
    "CONTRAINTE : depart pour La Rochelle mercredi 12, retour a Lyon dimanche 16 en fin de journee apres 6h30 de route. Trois creneaux exploitables : mercredi matin avant le depart, une sortie sur place, un eventuel deverrouillage au retour.",
    "ARBITRAGE ASSUME : le seuil 2x10 est sacrifie, pas la sortie longue. Le seuil est deja une force du profil (79/99) alors que l'allure marathon en est le point faible (42/99), et Nice est a 12 semaines. Une semaine sans seuil ne coute rien ; une semaine sans travail specifique marathon, si.",
    "MERCREDI 12 : footing court avec lignes droites le matin, AVANT la route. Rouler les jambes avant une longue position assise vaut mieux que partir raide. FC plafond 145.",
    "VENDREDI 14, LA ROCHELLE — seance cle : 15 km dont un bloc de 5 a 6 km a 5:20/km, encadre de footing facile. Longue et travail specifique fusionnes, meilleur rendement possible sur trois creneaux. Terrain plat en bord de mer, ideal pour la regularite. Consigne chiffree : chaque kilometre du bloc entre 5:18 et 5:24, et descendre sous 5:15 revient a rater la seance meme en se sentant bien.",
    "DIMANCHE 16 : deverrouillage optionnel de 6 a 8 km, FC sous 140, uniquement si l'envie est la. Apres 6h30 de voiture, l'objectif est de debloquer les jambes, pas de s'entrainer. Une marche de 20 a 30 minutes fait le meme travail si la fatigue du trajet domine.",
    "Volume previsionnel de la semaine ramene autour de 45 km contre 52 prevus, avec ACWR a 0,81 : la marge existe, elle n'appelle pas a compenser."
  ]},
  {"build":177,"date":"11 aout 2026","sha":"","tag":"S33 : repos du lundi et footing cardio-plafonne du mardi","items":[
    "LUNDI 10/08 marque en repos choisi. Le repos etait deja au programme ; Loic l'a confirme sur ses sensations, la recuperation du trail de dimanche etant encore incomplete.",
    "MARDI 11/08 logue : footing 10,07 km en 1h02 a 6:09/km, FC moyenne 138 pour un plafond annonce a 140, FC max 152, effort relatif 53, cadence 175, 29 m D+. Zero douleur au pied. Le seuil 2x10 initialement prevu ce jour glisse au jeudi 13.",
    "ANALYSE. L'amplitude d'allure est de 15 secondes au kilometre (6:18 au plus lent, 6:03 au plus rapide). Dimanche, sur la fin du trail, elle etait de 128 secondes. C'est la premiere sortie de la semaine ou la retenue tient de bout en bout, et elle tient parce qu'un nombre avait ete annonce avant le depart.",
    "La perception de Loic (lourdeur sur 6 km puis deliement) est confirmee par la mecanique et nuancee par le cardio : FC 136,8 sur les km 1-6 contre 140,4 sur les km 7-10. Au depart, les jambes travaillaient contre une raideur post-trail a faible cout cardiaque (km 1 a 6:18 pour 129 bpm) ; ensuite l'allure progresse et la FC monte par derive normale, accentuee par les 14 m de D+ des km 8 et 9.",
    "ACWR RECALCULE AUTOMATIQUEMENT : 0,97 -> 0,81 (aigu 417, chronique 2070 soit 518 par semaine, reference au 11/08). Premiere validation en conditions reelles de la source unique de verite mise en place au build 174 : aucune saisie manuelle, aucune occasion de se tromper de fenetre.",
    "CORRECTIF AU PASSAGE : l'interpretation generee contenait une nuance contextuelle figee sur S32 (« 2 sorties non planifiees sur 5, trail de dimanche »), devenue fausse des le premier log suivant. Retiree -- une interpretation calculee ne doit contenir que ce qui se recalcule."
  ]},
  {"build":176,"date":"10 aout 2026","sha":"","tag":"Forme du jour faussee : durees de seance illisibles","items":[
    "BUG SIGNALE PAR LOIC, ET IL AVAIT RAISON. Au lendemain d'un trail de 27 km et 662 m D+, la forme du jour affichait 91/100 avec une fraicheur qualifiee de « Frais (75 % de ta mediane) ». Invraisemblable -- et effectivement faux.",
    "CAUSE : _sessionMin() ne savait lire que les formats h:mm et mm:ss. La charge sRPE (RPE x duree) retombait alors SILENCIEUSEMENT sur une estimation par l'effort relatif (RE x 1,8), tres inferieure. Deux seances etaient concernees : le trail du 09/08, dont le temps avait ete saisi « 3h16 (3h48 total) », compte 443 au lieu de 1176 ; et le Trail Deraille du 05/07, en « 2:52:48 », compte 1051 au lieu de 1382.",
    "CONSEQUENCE : la fatigue residuelle etait sous-evaluee, donc la fraicheur surevaluee, donc la forme du jour gonflee. Aucun message d'erreur, aucun plantage -- le KPI mentait proprement.",
    "CORRECTIF : _sessionMin() accepte desormais un complement entre parentheses ainsi que le format h:mm:ss, en plus des formats existants. Apres correction, la charge du 09/08 passe de 443 a 1176, le ratio de fatigue de 0,75 a 1,33, la fraicheur de 82 (« Frais ») a 49 (« Fatigue elevee, recup en cours »), et la forme du jour de 91 a 80.",
    "GARDE-FOU AJOUTE dans audit_kpi.py : toute duree de seance non parsable est desormais signalee comme un ecart bloquant. Contre-test realise avec un temps volontairement illisible : l'audit le detecte et sort en erreur.",
    "LECON. Mes audits verifiaient que la forme etait bien comprise entre 0 et 100 et qu'elle exposait ses composantes -- jamais qu'elle etait PLAUSIBLE. Un KPI peut etre parfaitement forme et completement faux. C'est Loic qui l'a vu, pas les sept controles du gate."
  ]},
  {"build":175,"date":"10 aout 2026","sha":"","tag":"Audits branches au gate · Rewinds S28-S31 · dette a zero","items":[
    "1. LES QUATRE AUDITS SONT DESORMAIS DANS LA PORTE DE RELEASE. audit_data, audit_kpi, audit_dette et audit_runtime tournent a chaque livraison en phase 3, aux cotes de preflight, test_regression et audit_cockpit. Un audit qu'il faut penser a lancer ne sert a rien : il devait etre structurel.",
    "audit_runtime a recu un mode --rapide pour le gate (echantillon de fiches, delais reduits) : 31 s au lieu de 87 s. Le mode complet, sans argument, reste la reference a lancer periodiquement.",
    "CODES DE SORTIE CALIBRES : audit_kpi et audit_runtime bloquent sur toute anomalie ; audit_data bloque sur les BUG mais pas sur les INFO (veille) ; audit_dette bloque sur les incoherences visibles par l'utilisateur mais pas sur la dette, qui est un signal et non un motif de refus. Contre-test realise : ACWR force a 1,55 et objectif marathon remis a 3h42 -> les deux audits sortent bien en erreur.",
    "2. REWINDS S28 A S31 CREES -- ils manquaient depuis le 5 juillet. 8 slides chacun, construits sur les donnees mesurees et les revues coach existantes : S28 (recuperation a 61 km et 1176 m de D+ en deux jours, verdict A-), S29 (seuil 30 a 4:24/km pour une cible a 4:40, verdict A), S30 (marathon ViaRhona, km 41-42 a 5:16 sur des jambes de 40 km, verdict A), S31 (absorption -39 %, et premiere identification de la derive 5:35 -> 4:55, verdict A-).",
    "Les neuf Rewinds sont desormais accessibles depuis leur semaine et verifies un par un : bouton present, ouverture correcte, bon Rewind affiche. S32 reste en fin de tableau pour l'ouverture automatique du lundi.",
    "3. DETTE RAMENEE A ZERO. Le champ REPLAY (2518 octets exportes, jamais lus par app.js qui utilise un _REPLAY_DATA code en dur) est retire de l'export et de l'injection. Les 7 acces localStorage non proteges passent par trois helpers tolerants a l'echec (_lsGet / _lsSet / _lsDel) : l'app peut perdre sa persistance, plus jamais son fonctionnement.",
    "Seance de renforcement du 25/06 marquee 'sautee' : restee en 'a faire' pendant six semaines, elle etait le dernier BUG signale par audit_data, qui affiche maintenant zero."
  ]},
  {"build":174,"date":"10 aout 2026","sha":"","tag":"ACWR : source unique de verite (fin de la cause racine)","items":[
    "CAUSE RACINE TRAITEE. L'ACWR avait ete trouve fige a 0,69 pendant quatre semaines, puis faux a 1,02 par erreur de fenetre lors d'un calcul manuel. Le diagnostic complet a revele non pas deux mais TROIS sources, et DEUX definitions differentes : ACWR_DATA saisi a la main dans gen.py ; _ckRebuild qui recalculait sur les 4 dernieres semaines LOGUEES ; _dynamicACWR sur fenetre glissante 7/28 jours.",
    "PROBLEME DE FOND DE L'ANCIENNE DEFINITION PAR SEMAINES LOGUEES : elle sautait les semaines sans seance, pouvait donc couvrir bien plus de 28 jours, et restait bloquee sur la derniere semaine loguee tant qu'aucune seance de la semaine en cours n'etait enregistree. Deux chiffres differents pouvaient etre affiches a deux endroits de l'app.",
    "CORRECTIF 1 -- gen.py ne saisit plus l'ACWR : il le CALCULE depuis les seances loguees via _acwr_compute(), avec exactement la definition standard (fenetre glissante 7/28 jours). L'interpretation textuelle est generee par zone. Plus aucune valeur recopiee a la main, donc plus aucune erreur de recopie possible.",
    "CORRECTIF 2 -- app.js expose une fonction unique _acwrCompute(), utilisee a la fois par _dynamicACWR() et par _ckRebuild(). Une seule logique, un seul chiffre.",
    "CORRECTIF 3 -- ACWR_DATA expose desormais un champ 'ref' (date de la derniere seance prise en compte). audit_kpi verifie sa fraicheur et alerte si une seance plus recente existe : le mode de defaillance 'valeur figee non detectee' devient structurellement impossible a rater.",
    "VERIFIE : les quatre voies (gen.py au build, _acwrCompute, _dynamicACWR, ACWR_DATA apres _ckRebuild) renvoient toutes 0,97 / 487 / 2017. Simulation de robustesse : le ratio redescend a 0,69 apres trois jours sans courir et remonte a 0,90 avec un seuil loge — la fenetre glissante reagit, l'ancienne definition serait restee bloquee."
  ]},
  {"build":173,"date":"10 aout 2026","sha":"","tag":"Audit dette technique : objectif marathon corrige + garde-fou sur les textes","items":[
    "NOUVEL AXE D'AUDIT (scripts/audit_dette.py). Les audits existants couvraient le runtime, la justesse des KPI et la coherence des donnees. Aucun ne cherchait la dette : champs morts, code mort, valeurs contradictoires entre sections.",
    "INCOHERENCE METIER CORRIGEE, visible dans l'app : la carte Records annoncait « Marathon vise : 3h42 » alors que l'objectif declare de Loic pour Nice est 3h45 (PROFIL.cible_marathon). Deux chiffres differents pour le meme objectif selon l'ecran consulte. Aligne sur 3h45. La projection de forme (~3h38-3h42) reste disponible separement dans PROFIL.marathon_projete.",
    "GARDE-FOU AJOUTE dans audit_kpi.py : les CHIFFRES CITES DANS LES TEXTES sont desormais confrontes aux KPI. C'est exactement le trou par lequel le bug de l'ACWR etait passe -- la valeur figee avait ete corrigee mais les revues et slides continuaient d'annoncer l'ancien chiffre. Un texte qui contredit un KPI est un KPI faux.",
    "Le controle ne s'applique qu'aux textes COURANTS : une revue passee cite legitimement l'ACWR de son epoque (S28 a 1,10, S29 a 1,00), ce n'est pas une incoherence. Contre-test realise : en reinjectant 1,02 dans la revue S32, l'audit le detecte.",
    "DETTE ASSUMEE ET DOCUMENTEE, non corrigee ici : le champ REPLAY est exporte (2518 octets) mais jamais lu par app.js, qui utilise un _REPLAY_DATA code en dur ; 7 acces localStorage restent sans try/catch explicite (impact faible sur iOS moderne, ou le stockage fonctionne en navigation privee) ; ACWR_DATA reste fige dans gen.py tout en etant ecrase au runtime par _ckRebuild, ce qui cree deux sources de verite pour le meme chiffre."
  ]},
  {"build":172,"date":"10 aout 2026","sha":"","tag":"ACWR FAUX corrige (1,02 -> 0,97) + champ effort manquant","items":[
    "AUDIT KPI DEDIE CREE (scripts/audit_kpi.py). Les scripts existants verifiaient que les KPI s'AFFICHENT et ne plantent pas ; aucun ne verifiait qu'ils sont JUSTES. Ce nouvel audit refait chaque calcul independamment depuis les seances loguees, puis le confronte a ce que l'app produit dans le navigateur. Il a immediatement trouve deux erreurs, toutes deux introduites par moi.",
    "ERREUR 1 -- ACWR FAUX. Au build 166 j'avais calcule la fenetre 28 jours avec une expression fautive (aout[1:]) qui EXCLUAIT la sortie du 02/08 (effort relatif 105). La charge chronique affichait donc 1912 au lieu de 2017, et l'ACWR 1,02 au lieu de 0,97. Corrige : charge28j 2017, moyenne 504/semaine, ACWR 0,97. Interpretation, revue S32 et slide du Rewind mises a jour en coherence.",
    "ERREUR 2 -- CHAMP EFFORT MANQUANT. La sortie du 07/08 avait ete loguee sans champ 're' (effort relatif 28). Elle etait donc invisible pour tout KPI recalcule depuis les seances, alors qu'elle comptait dans les totaux saisis a la main -- exactement le type d'incoherence silencieuse qui rend deux chiffres inconciliables. Champ ajoute.",
    "Le vrai enseignement : l'ACWR reste le KPI le plus fragile de l'app. Il avait deja ete trouve fige a 0,69 pendant quatre semaines ; il etait cette fois faux par erreur de fenetre. audit_kpi.py est desormais le garde-fou structurel contre ces deux modes de defaillance.",
    "Verifie apres correction : recalcul independant et valeur affichee concordent sur charge 7j (487), charge 28j (2017) et ACWR (0,97)."
  ]},
  {"build":171,"date":"10 aout 2026","sha":"","tag":"Les trois derniers bugs de l'audit corriges","items":[
    "BUG-04 CORRIGE (Rewinds inaccessibles). Le bouton 'Lance le Rewind' n'existait que dans le bloc special de la S24 et etait code en dur sur rwOpen('S24') : les Rewinds S25, S26, S27 et S32 n'etaient atteignables que par l'ouverture automatique du lundi. Le bouton est desormais rendu dans la vue generique de semaine, conditionne a l'existence d'un Rewind pour cette semaine. Verifie : present sur S24/S25/S26/S27/S32, absent sur S30 et S33, et le clic ouvre bien le Rewind de la bonne semaine.",
    "BUG-05 CORRIGE (degrades SVG). L'id du degrade valait 'g'+couleur : deux graphiques de meme teinte generaient deux <linearGradient> partageant le meme id, et url(#id) resolvait toujours vers le premier. Un compteur global (_gradSeq) rend chaque id unique. Verifie sur le Cockpit : 7 degrades, zero doublon.",
    "RISQUE-01 CORRIGE (_ckRenderAll). La fonction lisait D.VOL[W].a sans verifier que la fenetre W existait, et levait 'Cannot read properties of undefined' sur toute valeur autre que 2/4/8/12. Une garde retombe desormais sur la fenetre disponible la plus proche. Verifie sur 2, 4, 8, 12, 26, 52 et 999 : aucun crash.",
    "OUTILLAGE D'AUDIT FIABILISE. Deux faux positifs de mes propres scripts corriges : audit_data ne detectait pas les boutons rwOpen construits dynamiquement, et audit_runtime comparait la semaine courante a une valeur figee (32) au lieu de la calculer — il signalait donc a tort une anomalie au passage en S33.",
    "ETAT APRES CORRECTIFS : audit runtime a 0 anomalie sur 30 semaines, 132 séances, 5 Rewinds et toutes les fenetres Cockpit ; audit statique a 1 seul point restant (une séance du 25/06 jamais loguee, sans conséquence)."
  ]},
  {"build":170,"date":"9 aout 2026","sha":"","tag":"Correction de la race condition d'ouverture + suite de tests rendue fiable","items":[
    "BUG-01 CORRIGE (ecran blanc). fermer() planifiait contenu.innerHTML='' dans un setTimeout de 300 ms. En rouvrant une fiche avant l'echeance, ce vidage differe s'appliquait a la NOUVELLE vue, qui s'affichait vide. Mesure avant correctif : echec systematique de 0 a 290 ms de delai.",
    "Correctif : le timer est desormais memorise dans _viderTimer et annule par clearTimeout des qu'une nouvelle vue s'ouvre (ouvrir()) ou qu'une fermeture est relancee. Verification apres correctif : 10 delais testes de 0 a 500 ms, 10 succes, y compris le cas 0 ms qui echouait toujours.",
    "BUG-02 CORRIGE (test complaisant). test_regression T02 testait les onglets 'seances' et 'courses', qui N'EXISTENT PAS -- les identifiants reels sont 'plan' et 'palmares'. showTab() masque alors toutes les vues sans lever d'erreur, et le test passait quand meme car il mesurait document.body, dont la seule barre de navigation (104 caracteres) franchissait le seuil de 50. Deux vues sur quatre n'etaient donc pas reellement testees depuis l'origine.",
    "Correctif : T02 cible desormais #vue-<id>, verifie que la vue est effectivement VISIBLE (display != none) et exige plus de 200 caracteres de contenu propre. Contre-test effectue : reinjecte avec les anciens noms fautifs, le test durci echoue bien sur 'seances' et 'courses' -- il attrape donc le defaut qu'il laissait passer.",
    "Reste en attente d'arbitrage : Rewinds S25/S26/S27/S32 sans bouton d'ouverture, ids de gradient SVG dupliques quand deux graphiques partagent une couleur, et _ckRenderAll qui leve sur les fenetres 26 et 52 semaines (inatteignables depuis l'UI actuelle)."
  ]},
  {"build":169,"date":"9 aout 2026","sha":"","tag":"Audit complet : MONTHLY purge du non-running","items":[
    "AUDIT ACTIF DEMANDE PAR LOIC. Trois scripts ajoutes dans scripts/ : audit_data.py (coherence donnees + code), audit_runtime.py (ouverture exhaustive des 30 semaines, 132 seances, 5 Rewinds, toutes fenetres Cockpit), test_race.py (reproduction ciblee).",
    "BUG D1 RESOLU A LA SOURCE. MONTHLY totalisait 1745 km / 138 sorties contre 1696 / 132 dans SAISON2026. Verification activite par activite sur Strava (janvier a mai) : MONTHLY incluait des activites NON-RUNNING.",
    "Janvier corrige : 234 km / 21 sorties -> 224 km / 19 sorties (1 randonnee 3,3 km + 1 sortie raquettes 6,0 km retirees). Elev 1579 -> 1342 m, RE 502 -> 2431 (l'ancien RE etait par ailleurs manifestement faux).",
    "Mai corrige : 241 km / 19 sorties -> 202 km / 15 sorties (4 randonnees retirees, 38,7 km et 1878 m). Elev 7856 -> 5978 m, RE 2139 -> 2171.",
    "Fevrier, mars et avril verifies exacts au 0,2 km pres (velo deja correctement exclu) -- aucune correction necessaire.",
    "Reconciliation totale : MONTHLY et SAISON2026 tombent desormais tous deux sur 1696 km / 132 sorties / 19880 m. Note de perimetre explicitee : course a pied uniquement, randonnees/raquettes/velo exclus.",
    "BUGS IDENTIFIES ET NON ENCORE CORRIGES (en attente d'arbitrage de Loic) : race condition fermer/rouvrir sous 300 ms qui vide la vue ; test_regression T02 qui teste deux onglets inexistants ('seances' et 'courses' au lieu de 'plan' et 'palmares') ; Rewinds S25/S26/S27/S32 sans bouton d'ouverture ; ids de gradient SVG dupliques ; _ckRenderAll qui leve sur les fenetres 26 et 52 semaines."
  ]},
  {"build":168,"date":"9 aout 2026","sha":"","tag":"LA revue de semaine S32 -- au bon endroit cette fois","items":[
    "DEUXIEME CORRECTION DE MA PROPRE ERREUR. Au build 166 j'avais modifie la description META en croyant faire la revue. Au build 167 j'ai fait le Rewind (slides). Ni l'un ni l'autre n'etait la revue de semaine. Loic a du me le signaler deux fois avec une capture d'ecran.",
    "La vraie revue de semaine est le champ _SxxREVUE attache a SEMAINES, rendu en bas de la vue semaine sous le titre 'Revue du coach -- bilan de la semaine'. Le mecanisme existait pour S25 a S31 ; seule S32 manquait, laissant le placeholder 'Revue de la semaine a venir' affiche alors que la semaine etait bouclee.",
    "_S32_REVUE ecrite et affectee : volume et charge vs prevu (67,3 km realises contre 52 cibles, +29%), adherence (2 sorties sur 5 hors plan, fractionne 6/8), signaux (pied clos, ACWR 1,02, deux ecarts chaussures), et decision pour S33 (repos lundi non negociable, longue plafonnee en FC, un nombre annonce avant chaque sortie).",
    "Axe central de la revue : l'opposition vendredi/dimanche a 48h d'ecart -- 132 bpm tenus avec une cible chiffree, 7:15 -> 5:07/km sans cible."
  ]},
  {"build":167,"date":"9 aout 2026","sha":"","tag":"Revue de semaine S32 (Rewind) -- manquante depuis S27","items":[
    "MANQUE SIGNALE PAR LOIC, ET IL AVAIT RAISON : au build 166 j'avais mis a jour la description META de S32 en croyant faire la revue de semaine. La vraie revue de semaine est le Rewind (parcours de slides), et il n'en existait plus depuis S27 (5 juillet).",
    "Rewind S32 cree : 12 slides sur donnees mesurees -- 67,3 km, 817 m D+, 7h07 de mouvement, 5194 kcal, ~61 000 battements, ACWR 1,02.",
    "Slides construites autour de l'opposition centrale de la semaine : vendredi 132 bpm avec cible chiffree annoncee, dimanche 7:15 -> 5:07/km sans cible. Verdict coach B+ (physique excellent, discipline de plan perfectible : 2 sorties sur 5 hors plan, 2 erreurs de chaussures).",
    "CORRECTIF D'ORDONNANCEMENT : rwAuto() ouvre REWINDS[length-1], donc le dernier element du tableau. Le Rewind S32 a ete place en FIN de tableau -- insere ailleurs, l'ouverture automatique du lundi matin aurait ressorti S27.",
    "TROU RESTANT ASSUME : les Rewinds S28, S29, S30 et S31 n'existent toujours pas. Non comble ici pour ne pas fabriquer des revues retrospectives sans le ressenti de Loic sur ces semaines."
  ]},
  {"build":166,"date":"9 aout 2026","sha":"","tag":"Boucle de Saint-Etienne loguee + KPI agreges reactualises","items":[
    "Sortie longue du 09/08 loguee avec donnees Strava reelles (activite 19665718937) : 27,01 km, 662 m D+, 3h16 de mouvement, allure 7:16/km, FC 145/176, effort relatif 246.",
    "Enseignement principal extrait des laps : derive non decidee sur les 6 derniers kilometres (7:15 -> 5:57 -> 5:42 -> 5:42 -> 5:28 -> 5:07/km, FC 139 -> 166) apres le depart des accompagnants. Contraste direct avec la sortie du 07/08 ou une cible chiffree avait tenu la FC a 132 sur 10 km.",
    "Chaussure de la seance corrigee : Novablast 5 J (route) reellement portee, alors que le plan prescrivait Cascadia 19 (trail).",
    "Parc chaussures reactualise sur donnees Strava : Novablast 5 J 689 km (+28), Novablast 5 V 56 km, Magic Speed 4 75 km.",
    "KPI AGREGES REACTUALISES -- ils dataient de S28 et etaient donc perimes de quatre semaines. MONTHLY complete avec juillet (257 km, 2805 m, 18 sorties, RE 2669) et aout au 09 (79 km, 853 m, 6 sorties, RE 592). Total saison porte a 1696 km / 19880 m / 132 sorties.",
    "ACWR recalcule sur donnees reelles : 1.02 (aigu 7j 487, chronique 28j 1912 soit 478/semaine) contre 0.69 affiche jusqu'ici. Passage de la zone de sous-charge a la zone optimale.",
    "Revue de semaine S32 reecrite sur chiffres mesures (5 sorties, 67,3 km, 817 m D+, RE 487) et cadrage S33 oriente sur la retenue chiffree systematique."
  ]},
  {"build":165,"date":"7 aout 2026","sha":"","tag":"Sortie non planifiee du vendredi S32 loguee (retenue cardiaque)","items":[
    "Vendredi 7/08 etait au plan en repos complet (2e jour avant la boucle de Saint-Etienne dimanche). Loic est neanmoins sorti courir : sortie personnelle de retenue cardiaque, cible FC moyenne <=135 bpm, hors plan.",
    "Donnees reelles recuperees via Strava (activite 19636720206) : 10,09 km en 1h00, 5:58/km, FC moyenne 132 (max 149), cadence 176, Novablast 5 V. Zero douleur au pied, 4e sortie consecutive.",
    "Analyse coach : bande FC tres resserree (124-136 bpm) sur toute la sortie, aucune derive -- signe que le travail de retenue a bien fonctionne. Passer sous 130 bpm en restant sous 6:00/km demandera des mois de fond aerobie, pas un effort de volonte ponctuel.",
    "Vigilance ajoutee : 4e jour consecutif avant un effort vallonne exigeant dimanche (27 km, 650 m D+), avec un seul jour de repos (samedi) en tampon. Le repos de samedi devient non negociable."
  ]},
  {"build":164,"date":"6 aout 2026","sha":"","tag":"Correctif deploiement : ajout de .nojekyll","items":[
    "Signale par Loic : le build 163 n apparaissait pas dans l app malgre un push reussi. Diagnostic : le commit etait bien sur main, mais le build GitHub Pages avait ECHOUE (Page build failed, duree 0 ms) -- l app servait donc encore le build 162",
    "Cause structurelle : aucun fichier .nojekyll dans le depot. GitHub Pages lancait donc un traitement Jekyll sur un site qui n en est pas un (app statique en un seul fichier HTML), avec le risque d echec que cela comporte",
    ".nojekyll ajoute a la racine et inscrit au manifeste de release.py pour qu il soit pousse a chaque livraison",
    "PIEGE DE VERIFICATION corrige au passage : index.html depasse 1 Mo, et l API GitHub Contents renvoie alors un contenu VIDE sans lever d erreur. Mes verifications post-push passaient par ce chemin et ne voyaient plus rien. Il faut utiliser l en-tete Accept: application/vnd.github.raw"
  ]},
  {"build":163,"date":"6 aout 2026","sha":"","tag":"Records cliquables avec celebration, conseil coach sans acronyme","items":[
    "Signale par Loic : le chiffre 128 records etait affiche sans etre cliquable -- impressionnant mais abstrait, et frustrant puisqu on veut savoir CE QUE c est",
    "NOUVELLE FEUILLE RECORDS : le total en grand avec degrade teal-or, les 3 references chronometrees (5 km 22:52, 10 km 46:14, semi 1h52:39) en tuiles, puis les 6 seances les plus prolifiques avec date, distance et allure",
    "ANIMATION DE CELEBRATION : 26 particules colorees en gerbe a l ouverture. Un record se celebre, il ne se consulte pas comme un releve bancaire. Desactivee si prefers-reduced-motion",
    "CONSEIL COACH : affichait Charge basse (ACWR 0,55), un acronyme brut sans aucun sens sur un ecran d accueil. Il affiche desormais la partie de phrase qui dit QUOI FAIRE -- De la marge pour ajouter du volume si la forme suit -- la metrique restant dans le Cockpit ou elle a sa place",
    "Verifie sans debordement ni troncature sur iPhone SE, 14 et Pro Max"
  ]},
  {"build":162,"date":"6 aout 2026","sha":"","tag":"EF+6x100m loggee, week-end reorganise pour la boucle de Saint-Etienne","items":[
    "EF du 06/08 : corps de sortie en 3 tiers tres parlant, 6:09 puis 6:13 puis 5:51/km pour FC 137/137/141 -- acceleration quasi gratuite en cout cardiaque, exactement le schema diesel decrit",
    "Decouplage -0,61 % (quasi nul, sens negatif) pour 8 % attendu : aucune derive sur le corps EF",
    "2 des 6 acclerations de 100m confirmees dans les donnees a 3:42-3:46/km, FC 162-168 -- la resolution de mesure ne permet pas de confirmer les 4 autres, mais le ressenti decrit (naturel, non force, dernier leve le pied) est coherent avec les donnees disponibles",
    "ZERO douleur au pied sur une seance incluant des accelerations : le test le plus concret depuis la reprise",
    "SIGNALE : la seance a ete couru en Clifton 10, paire retiree de la rotation le 27/07. L app ne les propose plus depuis le build 151, mais rien n empeche de les enfiler physiquement. Aucune consequence aujourd hui, mais rappel fait dans la fiche",
    "WEEK-END REORGANISE a la demande de Loic : vendredi et samedi passent en repos complet, la sortie longue plate de 16 km initialement prevue est remplacee dimanche par un projet perso -- boucle de Saint-Etienne, 27 km, 650 m D+, tres vallonnee et technique (Rochetaillee, Terrenoire)",
    "Avis de coach donne : deux jours de repos avant un effort presque double en charge est une bonne sequence. Deux reserves signalees sans remettre en cause le projet : sollicitation quadriceps en descentes techniques (vigilance historique), et pied non encore teste sur terrain instable a appuis irreguliers",
    "Chaussure conseillee : Cascadia 19 (accroche) plutot que Novablast pour la stabilite en descente",
    "Clifton 10 -> 1168 km"
  ]},
  {"build":161,"date":"6 aout 2026","sha":"","tag":"Accueil : puce marge supprimee, carte du jour densifiee","items":[
    "PUCE MARGE INCOMPREHENSIBLE : le conseil complet disait Charge basse (ACWR 0,55), de la marge pour ajouter du volume. Compresse en un mot, marge perdait son sujet -- marge de quoi ? L idee du mot d etat ne marchait que pour recup ou aff\u00fbtage, pas pour les conseils nuances",
    "Les 2 puces sont supprimees : S32 le plan dupliquait le widget Prepa juste dessous, et le conseil merite mieux qu une pastille de 65 px. Il redevient une PHRASE sous la carte du jour, cliquable pour le detail -- modele des suggestions Siri",
    "CARTE DU JOUR : la chaussure occupait une pastille entiere pour trois mots alors qu elle n appelle aucune action. Elle rejoint la ligne d infos (EF, 9 km, Novablast 5 V)",
    "DEUX ALERTES METEO REDONDANTES fusionnees : 32 degres demain pars avant 8h30, puis 32 degres allure +30s/km. Meme temperature affichee deux fois. La meteo n appelle qu une decision -- quand partir et a quelle allure -- donc une seule ligne : 32 degres, avant 8h30, +30s/km",
    "Le mot demain est retire quand la seance est aujourd hui : incoherence de temporalite corrigee",
    "Principe retenu : une information merite son propre conteneur seulement si elle appelle une action distincte"
  ]},
  {"build":160,"date":"6 aout 2026","sha":"","tag":"Widget Ton capital : la zone de fierte qui manquait","items":[
    "Retour de Loic : les corrections precedentes etaient de la maintenance, pas la reflexion demandee sur un ecran POSITIF et FINI. Il avait raison",
    "Inventaire de la matiere emotionnelle presente dans les donnees et jamais exploitee : 127 records personnels battus (jamais celebres nulle part), 3250 m de denivele cumule soit 37 % de l Everest, 8 semaines sans interruption noyees dans une micro-stat",
    "Et surtout : Lyon-Nice fait 298 km a vol d oiseau. Loic en a deja couru 386. Il a parcouru la distance de sa course avant meme de la courir -- aucun ecran ne le lui disait",
    "NOUVEAU WIDGET : 3 chiffres de fierte (km, records, semaines avec flamme) puis deux recits. Le jalon geographique est centre sur NICE, la destination du 8 novembre, pas sur des villes au hasard -- une progression coherente avec l objectif",
    "Registre chromatique volontairement plus chaud (ambre) que le reste de l app : le teal est la couleur de l action, l ambre celle de l accomplissement",
    "Les stats brutes quittent le widget Prepa, qui se recentre sur la progression et les echeances",
    "Principe retenu : un chiffre devient motivant quand il devient une image"
  ]},
  {"build":159,"date":"6 aout 2026","sha":"","tag":"Accueil : anneau propre, doublons canicule supprimes, parcours de prepa","items":[
    "ANNEAU DE FORME : le libelle forme etait pose a y=42 dans un bouton de 58 px et chevauchait le trace -- d ou l aspect sale. Aucun anneau du marche (Apple Watch, Whoop, Garmin) ne met de texte secondaire a l interieur. Le chiffre est desormais seul, centre au pixel (dx=0, dy=0), sur un anneau de 62 px a bouts arrondis",
    "CANICULE EN DOUBLE : la banniere separee est desactivee a la source. Le widget meteo porte deja l alerte chaleur, et le comptage Xj a plus de 33 degres etait un doublon anxiogene sans valeur d action",
    "BARRE SEANCE NON LOGGEE supprimee : 81 px pour redire ce que la carte du jour affiche deja juste au-dessus, avec le meme bouton d action",
    "PARCOURS DE PREPARATION : la barre de progression nue ne racontait rien. Elle porte maintenant ses deux reperes (S24 debut, drapeau Nice) et un curseur de position -- elle se lit comme un chemin parcouru, pas comme un pourcentage abstrait",
    "Resultat : 794 -> 707 px sur iPhone 14, aucun debordement sur les 3 formats",
    "BUG ATTRAPE PAR LA PORTE DE LIVRAISON : ma desactivation initiale de la banniere laissait des references orphelines (_canElOld) dans deux autres fonctions, cassant le harnais de test. Le push a ete bloque, corrige, puis relance"
  ]},
  {"build":158,"date":"6 aout 2026","sha":"","tag":"Trois corrections signalees par Loic sur l accueil","items":[
    "BUG DU CERCLE VIDE : l anneau de forme apparaissait vert et vide, incomprehensible. Le score etait pourtant present (78) mais ECRIT EN BLANC sur une carte devenue blanche -- reste d une epoque ou la carte du jour avait un fond sombre. Toute la bague est reprise pour un fond clair : contraste passe de 1:1 (invisible) a 14,6:1",
    "AMBIGUITE DU POURCENTAGE : 38% de ta preparation ne disait pas s il s agissait de la semaine ou du plan complet. Libelle desormais explicite : du plan, S24 vers Nice",
    "CARTE DU JOUR TROP GRANDE : 169 px pour peu d information. Densifiee a 135 px (titre 18 px, anneau 58 px, marges resserrees)",
    "REDONDANCE trouvee au passage : deux alertes temperature s empilaient en disant presque la meme chose (32 degres demain pars avant 8h30, puis 32 degres allure cible +30s/km). Fusionnees en une seule ligne",
    "Resultat : 906 -> 794 px sur iPhone 14, aucun debordement ni troncature sur les 3 formats"
  ]},
  {"build":157,"date":"6 aout 2026","sha":"","tag":"Accueil : widgets riches facon iOS au lieu de micro-puces","items":[
    "Reference donnee par Loic : l ecran verrouille d iPhone. Le widget meteo iOS contient temperature, alerte, previsions horaires ET 4 jours -- beaucoup d information, sans sensation de surcharge, parce qu il est organise en ZONES INTERNES separees par des filets avec un seul chiffre dominant",
    "Mes puces de 65 px faisaient l inverse : elles cachaient tout derriere un tap. On passe de 5 micro-puces a 2 widgets riches",
    "WIDGET METEO : temperature en 38 px, icone contextuelle, alerte chaleur integree, et une ligne de 6 creneaux horaires avec le plus frais mis en evidence -- l information utile pour choisir son heure de sortie",
    "WIDGET PREPA : pourcentage de progression en grand, barre S24 vers Nice, stats cumulees (sorties, km, semaines) et les 2 echeances en lignes cliquables avec chevron",
    "Deux redondances supprimees : la banniere canicule (35 px) repetait l alerte du widget meteo, et le bloc bilan (184 px) dupliquait les stats du widget prepa",
    "Il reste 2 puces compactes pour ce qui n a pas besoin d un widget : conseil du coach et acces au plan",
    "Resultat : 906 px, aucun debordement ni troncature sur iPhone SE, 14 et Pro Max"
  ]},
  {"build":156,"date":"6 aout 2026","sha":"","tag":"Correctifs de l audit severe : les 5 defauts releves","items":[
    "1. CONTRADICTION CENTRALE : le bandeau annoncait Aujourd hui juste au-dessus d une carte disant Prochaine seance - Demain. Premiere chose vue par l utilisateur. Le mot est supprime, la date factuelle reste",
    "2. AFFORDANCE : zero chevron, zero fleche sur les 5 puces. J avais construit une logique tap-pour-le-detail sans jamais indiquer qu on pouvait taper -- les chevrons de l ancien design avaient saute au compactage. Chevron discret retabli en coin de puce",
    "3. LE BILAN HORS SYSTEME : 18 px de rayon, aucune bordure, ombre differente des puces. Un systeme auquel un element sur deux echappe n en est pas un. Aligne sur 14 px, bordure et ombre communes",
    "4. ETAT VIDE METEO : la puce affichait des points de suspension qui ne se resolvent jamais si l API echoue -- exactement le defaut du rond vert muet, corrige a un endroit et laisse a l autre. Elle affiche desormais n/d explicitement",
    "5. HIERARCHIE : les 5 puces avaient exactement la meme taille, police et fond. L echeance la plus proche se distingue maintenant par un fond degrade et un chiffre plus grand, sans changer sa largeur",
    "BONUS trouve au test : les libelles etaient TRONQUES sur les 3 formats (Marathon..., SaintExp...). Mesure faite, le mot entier tenait en 49 px sur 52 disponibles -- c est l ellipse que j avais ajoutee en JS qui debordait. Remplacee par des noms courts explicites (Nice, SaintEx)",
    "Echelle typo : suppression du 11,5 px introduit la veille pour la puce coach, qui cassait l echelle definie le jour meme",
    "Resultat : 573 -> 538 px, aucune troncature, aucun debordement sur iPhone SE, 14 et Pro Max"
  ]},
  {"build":155,"date":"6 aout 2026","sha":"","tag":"Puce coach : un mot d etat au lieu d un rond vert muet","items":[
    "Signale par Loic : un rond vert a droite de l accueil, sans aucune information. Cause : au compactage du build 153, j avais garde l icone du conseil coach et JETE le message",
    "Le conseil perdu disait pourtant quelque chose d utile : Forme a 88/100, excellent moment pour une seance qualite si le plan s y prete",
    "La puce porte desormais un MOT D ETAT (qualite OK, recup, aff\u00fbtage, relance, marge, maintien, jour J, qualite ?) plutot que le score, pour ne pas dupliquer l anneau de forme du hero",
    "Le tap ouvre une feuille avec le conseil complet et un acces direct au coach. Meme logique que la puce meteo : l essentiel visible, le detail au tap",
    "Les 8 messages de _coachNudge enrichis d un mot-cle. Verifie que chacun tient dans la largeur de puce sur iPhone SE, 14 et Pro Max",
    "aria-label ajoute sur la puce avec le message complet, pour les lecteurs d ecran"
  ]},
  {"build":154,"date":"6 aout 2026","sha":"","tag":"Accueil : suppression des residus, objectif 18/20","items":[
    "BILAN AFFICHE EN DOUBLE : le bloc historique et celui ajoute au build 153 coexistaient, avec des chiffres CONTRADICTOIRES (31 sorties contre 30). Cause : l ancien comptait les seances de PPG et mobilite, le nouveau non",
    "Resolu en gardant le bloc historique (plus riche : il porte aussi le pourcentage de prepa et la serie de semaines) et en alignant son comptage sur les seances AVEC kilometrage. Un seul bilan, un seul chiffre",
    "ALERTE FANTOME : Seance hier non loggee s affichait alors que le fractionne du 04/08 etait bien enregistre -- en PARTIEL. Le controle testait statut !== fait et ignorait le statut partiel. Une alerte qui contredit la realite est ce qui casse le plus la confiance dans un outil",
    "CONTRASTE : les valeurs des puces sortaient a 3,74:1 sur fond blanc, sous la norme WCAG AA de 4,5:1. Teintes assombries a 5,07:1 sans changer l identite visuelle",
    "Resultat : 716 -> 571 px (0,7 ecran sur iPhone 14), 37 -> 27 unites visibles. Cibles tactiles toutes au-dessus de 44 px, aucun bouton sans libelle accessible"
  ]},
  {"build":153,"date":"6 aout 2026","sha":"","tag":"Accueil epure : puces compactes au lieu de conteneurs pleine largeur","items":[
    "Retour de Loic : l ecran renvoyait une impression de desordre, comme si sa prepa etait fouillis. Mesure : 50 unites d information, 130 mots, 7 blocs pleine largeur sur 1,4 ecran",
    "Diagnostic : le probleme n etait pas la quantite d information mais le fait que CHAQUE information reclamait un conteneur entier -- une banniere pleine largeur pour dire qu il fait chaud, une autre pour un simple lien vers le plan",
    "Reference explicite donnee par Loic : l accueil Strava, qui empile 3 stats dans une ligne compacte plutot que 3 cartes",
    "REFONTE : une rangee de 5 puces compactes (2 courses, progression du plan, meteo, coach). Chaque puce porte l essentiel (une icone, un chiffre) et ouvre le detail complet au tap",
    "La meteo passe d une banniere permanente a une puce coloree selon la temperature (rouge au-dessus de 30 degres). Le tap ouvre la meteo complete AVEC les creneaux d entrainement recommandes",
    "Nouvelle puce de progression : S32, 38% du plan -- l information de parcours qui manquait totalement",
    "Bilan cumule condense en une ligne de 3 chiffres (30 sorties, 386 km, 8 semaines) au lieu de 8 fragments minuscules en bas d ecran",
    "BUGS CORRIGES au passage : les sections du build 149 mentaient sur leur contenu (Mes echeances contenait un lien vers le plan, Bilan contenait une course). Variables mal identifiees a l epoque",
    "Resultat : 1147 -> 716 px, tout tient desormais en UN ecran. 50 -> 46 unites, 130 -> 87 mots"
  ]},
  {"build":152,"date":"6 aout 2026","sha":"","tag":"Radar : Constance et Endurance faussees par la semaine en cours","items":[
    "Signale par Loic : Constance affichait 21/99, tres bas par rapport aux 68 vus deux jours plus tot",
    "Meme classe de bug que le -57% des tendances KPI corrige au build 148, appliquee a un endroit different : Constance et Endurance calculaient leurs moyennes sur les 4 dernieres semaines EN COMPTANT la semaine en cours, forcement incomplete",
    "Jeudi, S32 n avait que 2 seances sur 6 prevues (20 km) : compare a S29-S31 completes, cela faisait chuter la moyenne de seances/semaine et surtout faisait exploser le coefficient de variation du volume a 40% (le pire cas possible), effondrant le sous-score correspondant a 1/99",
    "Corrige a la racine : les deux composantes utilisent desormais les 4 dernieres semaines COMPLETES (S28-S31), jamais la semaine en cours. Constance revient a 68, Endurance de 76 a 86",
    "Ironie assumee : le correctif du build 148 n avait ete applique qu aux tendances des KPI, pas a cet indicateur pourtant construit dans la meme session"
  ]},
  {"build":151,"date":"5 aout 2026","sha":"","tag":"EF du 05/08 loggee + Clifton 10 retiree a la racine de la rotation","items":[
    "EF facile : 10,04 km a 6:01/km, FC moy 134. Corps de sortie tres stable (9,67 km a 5:59/km) puis SPRINT FINAL de 336 m confirme au metre pres (4:42/km moy, pointe 3:36/km, FC jusqu a 166) -- aucune gene, test du pied concluant",
    "Decouplage 4,29% marque incertain par le test de robustesse : une sortie aussi plate et maitrisee noie la derive reelle dans le bruit de mesure. Pas alarmant, non compte dans la tendance par prudence",
    "Fatigue musculaire ressentie malgre l allure facile, attribuee au fractionne interrompu de la veille en canicule -- signal coherent, pas une anomalie",
    "BUG STRUCTUREL TROUVE ET CORRIGE : assign_shoes() proposait encore les Clifton 10 dans sa rotation EASY, alors qu elles ont ete retirees le 27/07 pour delamination. La decision n avait jamais ete codee a la racine, seulement patchee seance par seance -- elle venait de ressortir sur la fiche du 06/08",
    "Corrige dans le generateur lui-meme : plus aucune seance a venir ne propose les Clifton. Les 3 occurrences futures restantes dans les donnees sont des seances DEJA REALISEES avant le 27/07, donc legitimes",
    "Novablast 5 J -> 661 km"
  ]},
  {"build":150,"date":"4 aout 2026","sha":"","tag":"Accueil : carte hero + echelle typographique","items":[
    "CARTE HERO : la seance du jour et la forme fusionnees en un bloc unique et dominant. Avant, elles vivaient dans deux conteneurs separes de 157 et 107 px -- rien ne designait de point focal",
    "La forme devient un anneau de progression a droite du titre, lisible d un coup d oeil. Il reste cliquable pour ouvrir le detail, sans declencher l ouverture de la seance (propagation stoppee, verifie)",
    "ECHELLE TYPOGRAPHIQUE : 16 tailles distinctes coexistaient sur un seul ecran, dont des quasi-doublons visuellement indistincts (11 et 11,52 px, 20 et 20,8 px, 10 et 10,5 px) heritees de valeurs en rem",
    "Ramene a 9 tailles sur 6 tokens (--t-micro a --t-chiffre). Les valeurs batardes sont normalisees sur l echelle",
    "Ces deux points completent la refonte du build 149 : je les avais annonces puis pas livres, ce qui expliquait la note dans le bas de ma fourchette",
    "Verifie sur iPhone SE, 14 et Pro Max : hero 145 px, aucun debordement, les deux interactions cohabitent"
  ]},
  {"build":149,"date":"4 aout 2026","sha":"","tag":"Accueil : grammaire visuelle unifiee + 4 sections","items":[
    "Constat mesure : 7 conteneurs visuellement differents empiles dans l ordre de construction des fonctionnalites. 3 systemes de rayon (18/12/14 px), 3 systemes de marge, une seule ombre sur 7 blocs",
    "L ecran ne fait pourtant qu 1,2 ecran : le probleme n etait pas la longueur mais l absence de grammaire visuelle commune -- l interface paraissait chargee sans l etre",
    "Regroupement en 4 sections par echelle de temps (Aujourd hui / Ma preparation / Mes echeances / Bilan), meme principe que la refonte du Cockpit",
    "Intertitres discrets avec filet degrade, un seul systeme de rayon (14 px), une seule echelle d ombre. La carte du jour garde une ombre plus marquee pour rester le point focal",
    "METEO : l etat d erreur brut (Meteo indisponible - reessayer) n est plus expose. Le bloc disparait silencieusement et retente une minute plus tard. La meteo est un confort, pas une information critique",
    "Precision d honnetete : l echec meteo observe venait peut-etre uniquement de l environnement de test (domaine bloque). L appel API et le service worker sont corrects -- c est la degradation qui est corrigee, pas necessairement un bug de production",
    "Verifie sans debordement sur iPhone SE, 14 et Pro Max"
  ]},
  {"build":148,"date":"4 aout 2026","sha":"","tag":"Cockpit : correction des 3 defauts releves a la notation","items":[
    "DEFAUT 1 (le plus grave) : le selecteur de fenetre 2/4/8/12 n etait visible qu en zone Analyse mais pilotait AUSSI le contenu de la zone Progression -- effet a distance, un chiffre changeait sans controle visible pour l expliquer. Le selecteur est desormais present dans les 3 zones et les 3 exemplaires sont synchronises",
    "DEFAUT 2 : les KPI affichaient un etat sans direction. Ajout d une tendance en pourcentage avec fleche, calculee contre la periode precedente de meme longueur",
    "Piege evite au test : la premiere version comparait la semaine EN COURS (incomplete) et affichait -57 % de volume un mardi matin. La semaine courante est desormais exclue du calcul, et l app affiche un tiret plutot qu un chiffre douteux quand l historique est trop court",
    "DEFAUT 3 : la carte Decouplage en zone Aujourd hui montrait la sortie du 2 aout. Requalifiee en Derniere sortie analysee -- le titre ne promet plus ce qu il ne tient pas",
    "Zone Aujourd hui stabilisee a 1073 px, soit 1,3 ecran sur iPhone 14"
  ]},
  {"build":147,"date":"4 aout 2026","sha":"","tag":"Refonte du Cockpit : 3 zones par frequence de decision","items":[
    "Constat mesure : le Cockpit faisait 5318 px, soit 6,3 ecrans. Tout ce qui depassait le 2e ecran n etait jamais consulte -- y compris le RESUME EXECUTIF, pourtant l information la plus actionnable, enterre a l ecran 3,4",
    "Principe retenu : organiser par FREQUENCE DE DECISION (le modele mental du coach), pas par type de donnee",
    "AUJOURD HUI (1,2 ecran) : forme du jour, resume executif remonte, KPI charge/ACWR remontes, verdict de la derniere sortie",
    "PROGRESSION (2,3 ecrans) : profil de coureur, efficience, acclimatation chaleur, progression saison, tendance de durabilite",
    "ANALYSE (1,3 ecran) : les 6 sections graphiques et le selecteur de fenetre 2/4/8/12",
    "Carte Decouplage scindee : le verdict du jour reste en zone 1 (913 -> 312 px), la liste de tendance des 7 sorties part en zone Progression. Gain de 491 px sur le premier ecran",
    "Un scroll ne montre pas ce qu il cache : le selecteur de zones ANNONCE ce qui existe. On passe d un acces par endurance a un acces par intention",
    "Les 17 bulles d aide sont integralement preservees -- c est la signature pedagogique de l app",
    "audit_cockpit adapte : il bascule en zone 3 avant de tester les graphes, sinon ils sont masques"
  ]},
  {"build":146,"date":"4 aout 2026","sha":"","tag":"Fractionne du 04/08 : la canicule a decide, pas le manque de forme","items":[
    "Seance marquee PARTIELLE (6 repetitions sur 8, 4 pauses non prevues de 2-3 min). Lyon confirme en vigilance orange canicule par Meteo-France au moment de la seance",
    "Reconstruction depuis les streams bruts : echauffement deja a FC 165 en fin, allures de repetition reellement produites entre 3:30 et 3:57/km (dans la cible voire plus rapide que prescrit)",
    "Le facteur limitant n etait PAS la vitesse mais la recuperation : FC restee collee a 175-180 meme en phase de recup censee etre facile -- signature physiologique de la chaleur, pas d un manque de forme",
    "Phase finale a allure tempo (5:03/km) a coute une FC moyenne de 166, soit le tarif normal d un seuil : la chaleur a change toute l equation du jour",
    "Comparaison chiffree avec dimanche 02/08 : FC 150-154 pour effort modere alors, FC 166-180 aujourd hui pour effort comparable -- seule la temperature a bouge",
    "Bonne nouvelle : ZERO douleur au pied, y compris en fin de seance et en recuperation, apres une sortie exigeante",
    "Vigilance canicule renforcee sur les seances restantes de la semaine (EF mercredi, sortie longue samedi) : depart 6h30 max, pilotage FC exclusif"
  ]},
  {"build":145,"date":"3 aout 2026","sha":"","tag":"S32 reorganisee : fractionne remplace allure marathon (choix de Loic)","items":[
    "Fractionne 8x400m ajoute mardi 04/08 en remplacement de l allure marathon initialement prevue -- construit avec segments des le depart (17 blocs, barre de deroule fonctionnelle)",
    "Lundi 03/08 saute (Loic ne court pas ce jour). Semaine recompactee sur 4 jours de course : fractionne / EF / EF+lignes droites / sortie longue",
    "Sortie longue avancee du dimanche au SAMEDI 08/08 a la demande de Loic. PPG et mobilite regroupees vendredi 07/08. Dimanche devient repos complet",
    "Consigne de recuperation explicite dans la fiche : trot reellement lent entre les 400m, pas 5:00/km comme le 21/07 qui avait fait deriver la seance vers du tempo",
    "Nuance de coach inscrite dans la fiche : la vitesse est deja a 92/99 sur le radar contre 42/99 pour l allure marathon -- seance jouable en isole, pas la priorite de la prepa"
  ]},
  {"build":144,"date":"3 aout 2026","sha":"","tag":"CORRECTIF DE REGRESSION : le bouton fermer etait de nouveau hors ecran en scrollant","items":[
    "Signale par Loic avec capture : sur la fiche Allure marathon, scroller jusqu a la Visualisation chronologique faisait totalement disparaitre le bouton fermer",
    "Diagnostic : ce probleme avait DEJA ete corrige aux builds 138 et 139 (le conteneur de scroll etait passe de .modale-overlay a .modale-boite). Mais le fichier src/css.txt reellement present sur GitHub contenait encore l ANCIENNE version sans le correctif -- le fix n avait jamais atteint le depot lors d une session precedente",
    "Le verrou JS du build 139 (_scrollLockY) etait lui bien present et intact : seul le CSS avait regresse",
    "Reapplique a l identique et reverifie par scroll REEL a la molette (pas de scrollTo programmatique) sur iPhone SE, 14, Pro Max et desktop : bouton fixe a 18px, cliquable, ferme la fiche",
    "Verifie egalement que ce depot-ci est bien pousse sur GitHub avant de considerer la livraison terminee",
    "CAUSE RACINE TROUVEE APRES COUP : release.py ne poussait jamais css.txt (ni body.html, assemble.py, preflight.py). Le fix restait local a chaque fois, invisible car gen.py/tests tournent sur les memes fichiers locaux",
    "CORRIGE DANS L OUTIL LUI-MEME : le manifeste de push inclut desormais ces fichiers, et un garde-fou bloque toute livraison future si une source du pipeline manque au manifeste"
  ]},
  {"build":143,"date":"3 aout 2026","sha":"","tag":"S32 : barre de deroule retablie + seances 1 et 2 inversees","items":[
    "Signale par Loic : la seance Allure marathon n affichait AUCUNE barre de deroule, impossible de voir la structure de la seance",
    "Cause : la seance avait ete construite a la main dans l override S32, sans le champ segments -- c est lui qui dessine la barre. Les champs struct et legende ne suffisent pas",
    "Corrige : la seance vient desormais du generateur mp() du plan, qui produit les segments. 7 segments rendus (echauffement, 3 blocs, 2 recups, retour au calme)",
    "INVERSION demandee : la seance de qualite passe au MARDI 04/08 et l EF de reprise au LUNDI 03/08",
    "Note : les EF simples n ont volontairement pas de barre dans tout le plan (rien a decomposer) -- seules les seances structurees en ont"
  ]},
  {"build":142,"date":"3 aout 2026","sha":"","tag":"Ouverture facon pack pour la carte Profil de coureur","items":[
    "La carte Profil arrive scellee dans une enveloppe qui se dechire LE LONG D UN TRACE CARDIAQUE : le trait bat en boucle, flashe au tap, et la dechirure suit exactement sa forme",
    "Le radar s ecrit ensuite comme une trace GPS qui s enregistre, puis les noeuds et les barres se posent en cascade et le score compte jusqu a sa valeur",
    "Parti pris : deux gestes issus du monde de la course (trace cardiaque, trace GPS) plutot qu une ouverture de pack generique de jeu video",
    "Rangs nommes en culture course : Coureur, Regulier, Affute (Loic a 70), Competiteur, Elite",
    "Ne se declenche qu a la PREMIERE decouverte (memorise en localStorage), sinon l animation deviendrait une friction a chaque ouverture du Cockpit. Rejouable via un bouton en pied de carte",
    "BUG ATTRAPE AU TEST : apres un rejeu le pack redevenait scelle mais sans ecouteur de clic -- il etait impossible de le rouvrir. Ecouteurs desormais poses systematiquement, cycle verifie sur 3 rejeux",
    "CORRECTIF AUDIT : audit_cockpit se calait sur la semaine CALENDAIRE alors que l app construit ses fenetres sur les semaines LOGGEES. Chaque lundi matin, avant la premiere seance, cela produisait de faux ecarts sur les zones FC. L audit suit desormais la derniere semaine loggee",
    "Accessible au clavier, reduced-motion respecte, vibration legere au tap, verifie sans debordement sur iPhone SE, 14 et Pro Max"
  ]},
  {"build":141,"date":"2 aout 2026","sha":"","tag":"Nouvelle carte : Profil de coureur (radar 7 axes)","items":[
    "Radar facon carte de jeu : 7 qualites notees sur 99, toutes calculees sur les seances reellement loggees",
    "Axes : Vitesse 92 (pointe 2:57/km), Endurance 86 (43 km max, 59 km/sem), Montagne 81, Seuil 79 (4:24/km), Durabilite 76 (decouplage median 5,1 %), Constance 68, ALLURE MARATHON 42",
    "L axe Allure marathon est le plus important pour Nice : il mesure l allure produite a FC 148-162 hors seances de qualite. A 5:40/km contre 5:20 cible, il revele le vrai point faible -- invisible dans une premiere version du radar",
    "DEUX LECTURES : profil general 75 (moyenne simple) et INDICE NICE 70 (pondere marathon : allure marathon 25 %, endurance 25 %, durabilite 20 %, seuil 15 %, constance 10 %, vitesse 5 %, montagne 0 %)",
    "Deux axes de la premiere version corriges : la Montagne ne pese plus sur la note marathon, et la Regularite basee sur l ecart-type de cadence (fausse, la cadence varie legitimement selon le type de seance) devient une vraie Constance d entrainement",
    "Bug attrape au test : l extraction de la pointe de vitesse prenait la premiere allure du commentaire (echauffement 5:02) au lieu de la plus rapide. Vitesse passait de 1 a 92 apres correction",
    "Echelle amateur assumee (1 debutant, 99 tres bon amateur) pour que la note bouge visiblement avec la progression"
  ]},
  {"build":140,"date":"2 aout 2026","sha":"","tag":"S31 bouclee + S32 reconstruite sur la derive d allure","items":[
    "EF du 02/08 loggee : 11,31 km a 5:10/km, FC 154 (max 166), decouplage 3,53 % pour 6 % attendu. Reprise apres 2 jours de repos, pied indolore au depart",
    "DECOUVERTE MAJEURE : derive d allure non intentionnelle. km 0-2 a 5:35/km FC 136, puis acceleration continue jusqu a 4:55/km FC 161 sur les km 10-12. Loic ne l a pas decide -- c est le mecanisme exact qui fait exploser un marathon",
    "Le doute de Loic sur 5:20 est contredit par ses propres donnees : 5:12/km a FC 150 et 5:09/km a FC 153, soit plus rapide que la cible a une FC INFERIEURE a la zone visee. 5:20 n est pas ambitieux, il est confortable",
    "Revue S31 : 4 seances, 45,5 km, charge 404 (contre 621 en S30, -39 %). Semaine d absorption reussie sous canicule avec deux bons arbitrages d arret",
    "S32 RECONSTRUITE : 78 -> 52 km. Le seuil 2x15 min devient 3x2 km de RETENUE a 5:20 (ne jamais descendre sous 5:15, alerte Garmin), et la longue passe de 26 km avec 8 km AM a 16 km EF pure",
    "Justification : le pied tolere environ 1h et se reveille sur l allure soutenue prolongee, pas sur l EF facile. On teste donc la duree seule avant de recombiner duree et intensite en S33",
    "Novablast 5 V -> 45 km"
  ]},
  {"build":139,"date":"30 juillet 2026","sha":"","tag":"Fix (2e passe) : bouton fermer toujours absent en scrollant","items":[
    "Loic a signale que le build 138 n avait pas regle le probleme, capture a l appui. Il avait raison",
    "Erreur de methode de ma part : mon test utilisait un scroll programmatique (scrollTo) au lieu d un vrai scroll molette/doigt. Le premier ne reproduisait pas le bug, le second si",
    "Vraie cause racine : a l ouverture d une fiche, seul body.style.overflow=hidden etait pose. Or c est l element <html> qui gere le defilement -> la PAGE ENTIERE continuait de scroller sous la modale et emportait le bouton hors de l ecran, malgre le sticky corrige au build 138",
    "Corrige : verrou complet du scroll de page (html + body en position fixed) a l ouverture, avec memorisation et restitution exacte de la position de lecture a la fermeture",
    "Verifie par scroll REEL a la molette sur 4 tailles d ecran (iPhone SE, 14, Pro Max, desktop) : page immobile, bouton a 18px, cliquable, position restituee apres fermeture",
    "Le correctif CSS du build 138 reste necessaire : les deux problemes etaient reels et se cumulaient"
  ]},
  {"build":138,"date":"30 juillet 2026","sha":"","tag":"Fix : le bouton fermer disparaissait en scrollant dans une fiche","items":[
    "Signale par Loic : fallait remonter tout en haut de la fiche pour la fermer. Diagnostic confirme par mesure : le bouton passait de 18px a -582px des le premier scroll",
    "Cause racine identifiee : le bouton etait bien en position sticky, mais se calait par rapport a .modale-boite (overflow:hidden), pas par rapport au conteneur qui defile reellement a l ecran (.modale-overlay)",
    "Corrige a la racine : c est desormais .modale-boite elle-meme qui defile (overflow-y:auto, hauteur bornee a la fenetre). Le sticky se calcule alors sur le bon conteneur, celui que l oeil voit defiler",
    "Verifie sur toutes les fiches (seance, semaine), en scroll partiel et total, avec clic reel sur le bouton, en mobile et desktop -- le bouton fermer reste visible et fonctionnel a tout moment",
    "Aucun ajout de bouton supplementaire : celui qui existait deja fonctionne enfin comme prevu"
  ]},
  {"build":137,"date":"30 juillet 2026","sha":"","tag":"Premier test allure marathon chiffre (tunnel Croix-Rousse)","items":[
    "14,09 km (echauffement + 4x2 km a allure marathon, recup 2 min), GPS perdu sous tunnel : lecture basee sur FC (fiable) et les intervalles manuels Garmin",
    "Bloc le plus instructif : bloc 2 a FC 152,3 (pile la cible 155-158) produit 5:29/km. C est la donnee la plus fiable pour situer le niveau actuel a FC cible",
    "Bloc 4 (le mieux execute, 5:07 et 5:06/km tres regulier) a FC 165,5 -- plus rapide qu au marathon a FC comparable (5:15/km a 163-167 le 23/07) : tendance encourageante",
    "Blocs 1 et 3 irreguliers (sur-correction apres perte de repere GPS), coherent avec le ressenti de Loic -- pas un signal de forme",
    "ALERTE : douleur au pied reapparue apres 10-12 km, specifiquement sur cette seance a allure soutenue (les EF faciles ne la declenchent pas). Boucle de retour ecourtee par precaution -- bonne decision",
    "Repos du 29/07 marque fait (oubli). Novablast 5 V 20 -> 34 km",
    "Decouplage non calculable sur cette seance (blocs a intensites deliberement variees) : comportement attendu, le garde-fou fonctionne"
  ]},
  {"build":136,"date":"28 juillet 2026","sha":"","tag":"EF pilotee au cardio loggee + fix composante Efficience","items":[
    "EF du 28/07 : 10,03 km a 6:06/km, FC moyenne 138 (max 149) par 28 degres et air tres sec. ZERO seconde au-dessus de 150 bpm sur une heure",
    "Decouplage 2,98 % pour 8 % attendu : allure identique entre les deux moities (5:59/km) avec seulement +1 bpm. Meilleur resultat de toutes les sorties mesurees",
    "Comparaison parlante : dimanche 26/07 meme distance, FC 146 et decouplage 11,6 %. Aujourd hui FC 138 et decouplage 3 % -- l absorption du marathon progresse",
    "Mercredi 29/07 passe en repos complet (pic de canicule + gene au pied au 6e jour). Clifton 10 -> 1158 km",
    "ALERTE MATERIEL : la sortie a ete faite en Clifton 10, paire a 1148 km avec delamination de semelle, trou dans le mesh et mousse tassee. Avec une gene plantaire, c est la combinaison a eviter -- rappel explicite dans la fiche et le conseil coach",
    "FIX composante Efficience de la Forme du jour : elle comparait des ALLURES BRUTES sans regarder la FC. Une EF deliberement ralentie a 6:06 pour tenir 138 bpm faisait chuter le score a 32/100 alors que le decouplage sortait a 3 %. Elle mesure desormais le rapport allure/FC : 88/100 (+3,2 %)"
  ]},
  {"build":135,"date":"27 juillet 2026","sha":"","tag":"Seance de vitesse du lundi loggee, mardi devient repos","items":[
    "Qualite avancee du mardi au lundi (canicule des mercredi) : 10,02 km, EF 6,12 km a 5:48/km FC 140,8 puis 6x30 sec, FC max 188, 5 records",
    "NEGATIVE SPLIT PARFAIT 6/6 : 4:22, 3:59, 3:52, 3:29, 3:20, 2:57/km. Pointe finale 19 s/km plus rapide que le meilleur intervalle du 21/07 (3:16), et ce a J+4 d un marathon",
    "Redescente cardiaque analysee (ressenti confirme) : sous 155 en 1 min mais pres de 8 min pour passer sous 150, FC entre 145 et 167 sur les 15 min de retour au calme. Trois causes cumulees : 188 bpm atteints (plafond 192), fatigue residuelle du marathon, 29 degres a 11h",
    "MARDI TRANSFORME EN REPOS : la qualite de la semaine est faite, et la gene au pied gauche en est a son cinquieme jour consecutif. Une seconde seance intense serait la decision qui transforme une gene en blessure",
    "Novablast 5 V 10 -> 20 km (rodage en vue de Nice). Volume S31 ajuste a 40 km",
    "CORRECTIF OUTILLAGE : audit_cockpit.py avait la semaine courante EN DUR (30). Il a donc bloque la livraison en comparant la mauvaise fenetre alors que l app affichait correctement S31. La semaine est desormais calculee automatiquement -- l outil de controle ne doit pas reproduire le defaut de valeur figee qu il est cense detecter"
  ]},
  {"build":134,"date":"26 juillet 2026","sha":"","tag":"Sorties longues recalees sur les enseignements du marathon","items":[
    "ALLURE MARATHON corrigee de 5:15 a 5:20/km partout : 3h45 sur 42,195 km fait 5:19/km. Le 5:15 correspondait a ce que Loic a tenu 2 km au finish du ViaRhona, mais a FC 163-167 -- insoutenable sur 3h45",
    "Repere de validation ajoute sur chaque bloc AM : viser 155-158 bpm a 5:20/km d ici octobre. Au-dela de 165, ralentir a 5:25. C est la FC, pas le chrono, qui dira si 3h45 est acquis",
    "CONTINUITE imposee sur toutes les sorties longues : pas d arret prolonge, ravitaillement en marchant. Le marathon du 23/07 comptait 56 min d arrets -- c est precisement ce qu il n a pas entraine",
    "Ambiguite levee : les fiches disaient 26 km en EF puis 8 km AM, ce qui se lisait comme 34 km. Desormais 26 km AU TOTAL dont les 8 DERNIERS a allure marathon",
    "Metrique FC des longues avec bloc AM : affiche desormais les deux zones (135-150 puis 152-163) au lieu de la seule zone EF",
    "Progression AM inchangee et validee : 8 km (S32) puis 12 (S34, gate) puis 6 (S40, post-USA) puis 12 (S41) puis 14 (S42, seance reine) puis 12 (S43) puis 4 (S44). 76 km cumules a allure marathon avant Nice"
  ]},
  {"build":133,"date":"26 juillet 2026","sha":"","tag":"S31 restructuree : absorption marathon sous canicule","items":[
    "Meteo France annonce 36-38 C a Lyon mercredi 29 et jeudi 30 (dome de chaleur saharien) : la semaine est reconstruite autour de cette contrainte",
    "Test 10 km REPORTE : un contre-la-montre maximal a J+5 d un marathon mesurerait la fatigue et pas la forme, et recalerait donc les allures sur une mauvaise mesure. A replacer une fois la canicule passee",
    "Volume 70 -> 42 km. Lundi EF 8 km, mardi VMA 6x30 (seule qualite, placee au dernier jour frais), mercredi et jeudi footings courts a 6h30, vendredi repos obligatoire, samedi sortie longue raccourcie a 12-14 km",
    "VMA reduite de 8 a 6 repetitions vs le 21/07 : meme stimulus, dose adaptee a J+5 d un marathon. Consigne explicite sur la vraie recuperation entre les reps (le 21/07 les recups a 5:00/km avaient fait glisser la seance vers du tempo)",
    "Fiches canicule : depart 6h30 imperatif, pilotage au cardio uniquement, signaux d arret d un coup de chaleur listes, rappel de la derive d environ 1 bpm par degre au-dessus de 15 C",
    "Champ RPE des 5 seances realigne sur les metriques annoncees : la fiche VMA affichait encore 9/10, valeur residuelle de l ancien test 10 km"
  ]},
  {"build":132,"date":"26 juillet 2026","sha":"","tag":"S30 bouclee : recup dimanche loggee + revue de la plus grosse semaine","items":[
    "Recup post-marathon J+3 loggee : 10,13 km a 5:56/km, FC 146/161, 27 degres en fin de journee, Novablast 5 V etrennee (0 -> 10 km)",
    "Derive cardiaque 11,6 % (attendu 8) : km 0-2 a 5:41/km FC 137 puis km 8-10 a 6:00/km FC 148. Loic a RALENTI de 19 s/km pendant que sa FC montait de 11 bpm -- son ressenti est confirme par les donnees",
    "Objectif <140 bpm non tenu (15,6 % du temps) mais objectif reel atteint : zone grise Z3 limitee a 3,6 % du temps, 85 % sous 150",
    "Revue S30 : 4 seances, 74,2 km, charge 621 -- la plus grosse semaine de la preparation, avec un marathon complet dedans",
    "CORRECTIF procedure decouplage : le test de robustesse testait un point de coupe a 2 min, encore dans la montee cardiaque sur une seance demarree a 91 bpm. Il ne teste plus que vers le haut (couper plus tot reintroduit la montee, ce que la fenetre cherche a exclure)",
    "Verifie par non-regression : les 4 seances de reference gardent des valeurs identiques, seule la seance du jour bascule d incertain a fiable",
    "BUG ATTRAPE PAR LA PORTE DE LIVRAISON : la mediane JS renvoyait la valeur HAUTE sur un effectif pair au lieu de la moyenne des deux centraux. La derive hebdo S30 affichait 11,56 au lieu de 6,00. Corrige et re-audite avant tout push"
  ]},
  {"build":131,"date":"24 juillet 2026","sha":"","tag":"Process de livraison en 4 phases + registre anti-oubli","items":[
    "Loic a raison : Z2, DC et FCZ avaient DEJA ete identifiees comme figees au build 118. Sept series sur dix avaient ete corrigees, ces trois-la non, et le compte rendu presentait le travail comme termine",
    "Cause racine : rien ne verifiait la COMPLETUDE d une correction. Un humain decidait de ce qui etait fini",
    "NOUVEAU src/kpi_registry.py : toute serie du Cockpit doit etre declaree LIVE, STATIC ou DERIVED. Une serie LIVE non recalculee par _ckRebuild fait echouer la livraison. Une serie presente dans le code mais absente du registre aussi",
    "NOUVEAU src/release.py : porte de livraison en 4 phases (recherche, experimentation, test, livraison). Le push est impossible tant que les 3 premieres ne sont pas vertes. Verifie aussi le deploiement Pages apres push",
    "Les deux controles sont complementaires et ont ete valides par injection de regression : le registre attrape une serie jamais recalculee, l audit attrape une serie recalculee avec de mauvaises valeurs",
    "Aucune exception possible : un seul echec bloque la livraison"
  ]},
  {"build":130,"date":"24 juillet 2026","sha":"","tag":"AUDIT COMPLET DU COCKPIT : 3 series figees corrigees + controle permanent","items":[
    "Audit exhaustif demande par Loic apres la Forme du jour non implementee. 159 controles automatises sur les 4 fenetres (2/4/8/12 semaines)",
    "TROUVE : Allure Z2, Derive cardiaque et Zones FC n etaient JAMAIS recalculees - figees au build depuis S26, avec des valeurs devenues incoherentes",
    "TROUVE : les zones FC du graphe utilisaient des bornes (Z2 130-144) contredisant la table officielle de l app (Z2 134-154)",
    "TROUVE : les fenetres 8 et 12 semaines ne montraient que les semaines loggees - tout l historique pre-plan avait disparu des graphes",
    "TROUVE : le delta de l allure Z2 se cassait des qu une semaine sans seance facile laissait un trou (NaN silencieux)",
    "TROUVE : une seance S27 partielle sans champs structures (re, cadence, D+) - backfillee",
    "CORRIGE : les 3 series sont recalculees en direct ; la derive cardiaque hebdo reprend desormais le KPI decouplage valide, source unique de verite",
    "CORRIGE : fusion historique + semaines loggees, les 12 semaines sont a nouveau completes (S19 a S30)",
    "CORRIGE : bornes de zones alignees sur la table officielle, aide reecrite avec la limite de methode assumee (classement par FC moyenne, pas temps-en-zone)",
    "NOUVEAU : src/audit_cockpit.py - controle automatise a lancer avant chaque push. Il recalcule independamment chaque valeur depuis les donnees brutes et echoue au moindre ecart"
  ]},
  {"build":129,"date":"24 juillet 2026","sha":"","tag":"Forme du jour : refonte du modele (fatigue reelle, pas jours de repos)","items":[
    "Signale par Loic : au lendemain du marathon de 42,5 km, le score affichait 87 avec Fraicheur 85 \u2014 exactement le meme score qu au lendemain d un footing de recuperation",
    "Cause : la composante Fraicheur ne comptait que les JOURS depuis la derniere seance, sans jamais regarder ce qui avait ete fait",
    "Corrige : la Fraicheur mesure desormais la FATIGUE RESIDUELLE via la charge sRPE de Foster (ton RPE x la duree), avec decroissance exponentielle sur 3,5 jours",
    "Echelle auto-calibree sur ta propre mediane, comme le decouplage : 100% = ta fatigue habituelle. Aujourd hui 198%, soit le 98e percentile de ta saison",
    "ACWR bascule sur une fenetre GLISSANTE 7/28 jours : avant, une semaine a peine commencee etait comparee a des semaines completes, d ou une chute artificielle chaque lundi",
    "Adherence calculee au prorata : les seances a venir dans la semaine en cours ne penalisent plus",
    "Nouvelles ponderations : Fraicheur 35% (avant 20), ACWR 25%, Adherence 20%, Efficience 20%",
    "Resultat du jour : 67 au lieu de 87, avec le message Recuperation en cours - pas de qualite aujourd hui",
    "Bulle d aide entierement reecrite : methode sRPE, sens de la mediane, fenetre glissante, et rappel que le score est un composite"
  ]},
  {"build":128,"date":"23 juillet 2026","sha":"","tag":"MARATHON ViaRhona logge + garde-fou decouplage","items":[
    "42,52 km Vienne > Saint-Rambert-d Albon en 4h18 de mouvement : la plus grosse sortie de la saison (charge 367, pres du double de la precedente SL)",
    "15 km seul a 5:36/km FC 142, puis 23 km avec Yannis a 6:21/km, puis finish a 5:16 et 5:15/km sur les km 41-42 apres 40 km dans les jambes",
    "Nutrition validee : 3 gels + 3 pastilles + Clif Bar, aucune perte d energie sur 4h18 (contre les vertiges de la SL du 16/7)",
    "Novablast 5 J -> 651 km. Vigilance : douleur sous le pied gauche apparue au dernier kilometre",
    "GARDE-FOU AJOUTE a la procedure decouplage : detection de changement d allure delibere par point de rupture",
    "Sur ce marathon le decouplage sortait a 16% (seance subie) alors que le ressenti etait excellent : artefact du ralentissement social pour rester avec Yannis. Phases isolees : +1,5% seul et +8,4% avec Yannis",
    "La seance est desormais marquee non_representatif et aucun chiffre n est stocke, pour ne pas polluer la tendance"
  ]},
  {"build":127,"date":"22 juillet 2026","sha":"","tag":"Correctif : emoji echappe en dur (preflight L04)","items":[
    "Le bloc decouplage de la fiche contenait un emoji ecrit en paire de substitution echappee au lieu du caractere litteral",
    "Regle du preflight L04 respectee : emoji litteral uniquement",
    "Note de rigueur : le build 126 a ete pousse alors que le preflight signalait cet echec - corrige immediatement"
  ]},
  {"build":126,"date":"22 juillet 2026","sha":"","tag":"Decouplage : ajout du bloc dans la fiche de seance","items":[
    "L indicateur etait uniquement dans le Cockpit (oubli signale par Loic) : il apparait desormais aussi dans la fiche de chaque seance eligible",
    "Bloc complet dans la fiche : valeur, verdict, jauge avec repere attendu, les deux moities de sortie et la derive brute",
    "Le point d aide ? est accessible directement depuis la fiche",
    "Le bloc ne s affiche que sur les seances eligibles avec un KPI valide - invisible ailleurs (verifie sur la seance VMA du 21/7)"
  ]},
  {"build":125,"date":"22 juillet 2026","sha":"","tag":"Nouvel indicateur : decouplage cardiaque","items":[
    "Nouvelle carte Cockpit : mesure si ta sortie t a coute plus cher a la fin qu au debut (rapport allure/FC degrade entre le debut et la fin)",
    "Jauge avec ton curseur ET le repere attendu, contextualise par la duree et la temperature : c est ta position par rapport a l attendu qui fait le verdict, pas la valeur brute",
    "Echelle calibree sur tes propres sorties : <3% maitrise, 3-6% conforme, 6-9% sous tension, >9% subie",
    "4 sorties backfillees (recup 20/7 +0,43%, EF 15/7 +5,12%, EF 17/7 +8,33%, SL 16/7 +9,35%) - amplitude 8,9 pts, l indicateur discrimine reellement",
    "Procedure complete versionnee dans src/decouplage.py : recuperation streams fins, nettoyage, fenetre adaptative, 4 tests de validation. Si un test echoue, aucun chiffre n est affiche",
    "Point d aide ? pedagogique : analogie, exemple chiffre, echelle, sens du repere gris, methode de calcul et limites"
  ]},
  {"build":124,"date":"21 juillet 2026","sha":"","tag":"Audit complet des indicateurs + fix efficience aerobie polluee","items":[
    "Audit automatise des 14 indicateurs du Cockpit : tous alimentes par les vraies seances loggees, aucune erreur JS",
    "BUG TROUVE ET CORRIGE : la carte Moteur aerobie integrait les seances de QUALITE (seuil dimanche a 4:31/km, VMA du jour a 3:16/km) dans le calcul de l allure a 145 bpm",
    "Consequence : l efficience affichait 4:21/km, une valeur irrealiste qui n a rien a voir avec l aisance aerobie -- corrigee a 5:17/km",
    "Double garde-fou ajoute : exclusion par type de seance (seuil/VMA/tempo/cotes/specifique) ET par allure trop rapide pour de l EF (<4:45/km)"
  ]},
  {"build":123,"date":"21 juillet 2026","sha":"","tag":"S30 : seance 2 transformee en qualite VMA (choix de Loic)","items":[
    "La seance 2 (initialement EF + lignes droites) devient une vraie seance de qualite : 8x30 sec VMA choisie par envie malgre la semaine ViaRhona",
    "Loggee : 7,5 km, FC 159/182, 8 records, negative split spontane des intervalles (4:10 -> pointe finale a 3:16/km, la plus rapide de la saison), Magic Speed 4 (-> 66 km)",
    "Revue coach : belle seance et beau potentiel vitesse, mais recups trop actives (FC jamais sous 160, vire VMA+tempo) et surtout 2e qualite de la semaine",
    "Rappel : mercredi repos ABSOLU, et jeudi 40 km a l ecoute de la fraicheur au reveil"
  ]},
  {"build":122,"date":"20 juillet 2026","sha":"","tag":"S30 : sortie de recup lundi loggee (pilotee cardio)","items":[
    "Recup lundi loggee : 14,03 km a 5:48/km, FC 139/154 (objectif <140 bpm atteint), rallongee car passage chez sa copine (Clifton 10 -> 1148 km)",
    "Cas d ecole de pilotage au cardio : par temps plus frais, la meme FC produit une allure plus rapide -- l allure n est que la consequence du cardio maitrise",
    "Derive cardiaque quasi nulle sur 1h20 : bonne fraicheur le lendemain du seuil",
    "Rappel coach : jeudi = 40 km ViaRhona, priorite absolue a la fraicheur d ici la (mardi court et facile, mercredi repos)"
  ]},
  {"build":121,"date":"19 juillet 2026","sha":"","tag":"Fix cache : le Service Worker gardait une ancienne version en memoire","items":[
    "Meme apres suppression + reinstallation de l'app, iOS Safari conserve le Service Worker et son cache tant que les donnees du site ne sont pas videes manuellement -- ce qui bloquait la mise a jour",
    "Cache du Service Worker invalide de force (nouvelle version) : purge complete de l'ancien cache a la prochaine ouverture",
    "Le fetch reseau ignore desormais aussi le cache HTTP du navigateur (no-store), pas seulement le cache du Service Worker",
    "Si le probleme persiste : ouvrir le site dans Safari normal (pas l'icone), recharger, puis rouvrir l'app installee"
  ]},
  {"build":120,"date":"19 juillet 2026","sha":"","tag":"Fix : cadre trompeur dans le detail de sortie (repere par Loic)","items":[
    "Ouvrir une seance sans streams (la plupart des seances recentes) affichait un texte de dev ambigu (\"Streams disponibles en prod via Strava\") qui ressemblait a un CTA casse",
    "Corrige : message honnete (\"Graphique detaille non disponible\") ; la legende FC/Allure/Altitude et le texte \"glisse sur le graphe\" sont desormais masques quand il n'y a pas de graphe",
    "Bonus repere en verifiant : le champ Calories affichait le mot null quand la donnee etait absente -- remplace par un tiret sur toutes les metriques manquantes"
  ]},
  {"build":119,"date":"19 juillet 2026","sha":"","tag":"Fix : le mot Canicule etait trompeur (repere par Loic)","items":[
    "La banniere disait Canicule des 3 jours prevus a plus de 28\u00b0C, alors que le badge Demain de la meme fonction utilise deja 33\u00b0C comme seuil canicule -- incoherence interne",
    "Corrige : Canicule reserve aux vrais jours a plus de 33\u00b0C ; un nouveau palier honnete Chaleur (25-33\u00b0C) couvre les jours simplement chauds",
    "Le mot Canicule ne s'affiche plus que quand c'en est vraiment une"
  ]},
  {"build":118,"date":"19 juillet 2026","sha":"","tag":"Fix majeur : 3 vues du Cockpit desormais TOUJOURS a jour","items":[
    "Diagnostic : Annee&trophees (heatmap), Analyse du coach (historique) et Analyse par sortie affichaient des donnees figees depuis mi-juin, deconnectees des seances loggees",
    "19 seances retroactivement enrichies avec champs structures (re, cadence, D+) - fondation fiable pour tous les calculs futurs",
    "Heatmap desormais calculee = historique pre-plan fusionne avec les vraies dates loggees (plus jamais figee)",
    "Journal du coach genere automatiquement depuis les revues de semaine (S26+) - plus besoin d'entree manuelle separee",
    "Analyse par sortie reconstruite en direct depuis les seances reelles a chaque ouverture (avant : jamais recalculee)",
    "Resume executif du Cockpit ne depend plus d'une tendance Z2 figee - utilise desormais l'efficience aerobie live",
    "Limite assumee : le graphe seconde-par-seconde du detail de sortie ne s'affiche que pour les runs avec streams en cache (anciens uniquement)"
  ]},
  {"build":117,"date":"19 juillet 2026","sha":"","tag":"S30 restructuree autour du 40 km (approche coach)","items":[
    "Semaine reorganisee autour du projet ViaRhona 40 km (jeudi) comme evenement central : une seule touche de rythme, fraicheur protegee",
    "Seuil et cotes RETIRES (le seuil de dimanche a deja rempli le quota qualite) : lundi recup, mardi EF + lignes droites, mercredi repos complet",
    "Volume ajuste de 88 a 72 km : c'est la densite d'intensite qu'on reduit, pas le volume (le 40 km s'en charge)",
    "Chaque fiche detaille le pourquoi coach : proteger la fraicheur avant l'ultra et la recuperation apres"
  ]},
  {"build":116,"date":"19 juillet 2026","sha":"","tag":"S29 : seuil 30 exceptionnel + revue de semaine","items":[
    "Seance seuil loggee (dimanche, en derniere seance de la semaine) : 2x8 min a 4:24 et 4:31/km, FC ~175, 10 records de segments, Novablast 5 J (-> 609 km)",
    "Blocs courus 10-15 s/km PLUS RAPIDE que la cible de 4:40, ressenti excellent — confirme la progression de la carte saisonniere",
    "PPG du dimanche marquee sautee (remplacee par le seuil) ; arret volontaire a 10 km avant le projet ViaRhona",
    "Revue de semaine S29 ajoutee : 4/5 seances, 54 km, ACWR 1,00, forme 87 — pret pour le ViaRhona"
  ]},
  {"build":115,"date":"18 juillet 2026","sha":"","tag":"Nouvelle carte : Progression par saison (efficience a FC egale)","items":[
    "Nouvelle carte Cockpit : ton allure a 145 bpm par saison (hiver -> printemps -> ete), calculee sur du vrai cardio Strava",
    "Points d ancrage reels : 3 EF route par saison (hiver/printemps figes, ete enrichi par les seances loggees)",
    "Correction thermique appliquee a l ete : +7,6 % d efficience depuis l hiver (~25 s/km plus rapide a effort egal) - la chaleur masquait cette progression",
    "Point d aide ? pedagogique expliquant la methode et pourquoi la correction chaleur est indispensable"
  ]},
  {"build":114,"date":"18 juillet 2026","sha":"","tag":"Forme du jour : preuve de fraicheur ajoutee","items":[
    "Nouvel horodatage discret sous le score : Recalcule aujourd'hui a HH:MM, avec un petit point vert qui pulse",
    "Le score etait deja recalcule en temps reel a chaque ouverture (aucune donnee figee) mais rien ne le prouvait a l'ecran",
    "Le chiffre rejoue une petite animation d'apparition a chaque fois que tu ouvres le Cockpit, pour renforcer visuellement que c'est frais",
    "Respecte reduced-motion (animations desactivees, point fixe)"
  ]},
  {"build":113,"date":"18 juillet 2026","sha":"","tag":"Fix : clic sur une seance en retard ouvrait le mauvais ecran","items":[
    "Bug repere par Loic : pour une seance en retard non loggee, taper n'importe ou sur la carte ouvrait directement l'enregistrement rapide au lieu de la fiche",
    "Cause : le clic de toute la carte etait mal aiguille vers ouvrirQuickLog ; le petit rond vert n'avait meme pas son propre gestionnaire",
    "Corrige : taper la carte ouvre toujours la fiche (ouvrirSeance) ; taper le petit rond ouvre l'enregistrement rapide, sans propager le clic a la carte",
    "Rond rendu accessible au clavier (focus + Entree/Espace)"
  ]},
  {"build":112,"date":"18 juillet 2026","sha":"","tag":"Fix : duree des seances Seuil recalculee (bug repere par Loic)","items":[
    "La Duree affichee sur les 9 seances Seuil de la saison (S29 a S51) etait fausse : saisie a la main, jamais recalculee depuis la vraie structure (echauffement + blocs + recup + retour)",
    "Ecart de +6 a +19 min selon les seances (ex: S29 affichait 68 min pour une structure reelle de 49 min)",
    "Corrige a la source : la duree est desormais calculee automatiquement depuis les segments reels, comme pour les cotes pyramidales",
    "Merci Loic d'avoir repere l'incoherence sur la fiche Seuil 30 du 18/7"
  ]},
  {"build":111,"date":"17 juillet 2026","sha":"","tag":"S30 restructuree pour le projet ViaRhona","items":[
    "Jeudi 23/7 devient la seance longue de la semaine : ViaRhona Vienne -> Saint-Rambert-d Albon, 40 km en EF entre amis (Yannis, Edwige)",
    "La sortie longue prevue dimanche (24 km dont 6 AM) est remplacee par un footing de recuperation tres facile (~8 km)",
    "Fiche ViaRhona complete : nutrition (5-6 gels sur 4h+), hydratation (villages ViaRhona en ravito), consigne de depart lent",
    "Meta semaine mise a jour : 72 -> 88 km, objectif reformule autour du projet plaisir"
  ]},
  {"build":110,"date":"17 juillet 2026","sha":"","tag":"S29 : EF+technique loggee, cardio haut explique","items":[
    "Seance loggee : 10,30 km, FC 147/172, 2 derniers km acceleres (5:15 puis 5:11/km) au lieu des lignes droites prevues",
    "Revue coach sur le ressenti cardio haut : explique par la fatigue residuelle de la sortie longue de la veille (RE 222, plus grosse charge de la saison), pas principalement par la chaleur",
    "Point chaussures : Clifton 10 a 1134 km, bien au-dela de la zone de remplacement (700-900 km) - a sortir de la rotation qualite",
    "Conseil pour le seuil de demain : decaler a dimanche si le cardio/les jambes sont encore lourds au reveil"
  ]},
  {"build":109,"date":"16 juillet 2026","sha":"","tag":"S29 : sortie longue de reference (23 km sous canicule)","items":[
    "SL loggee : 23,04 km en 2h10 avec Edwige, FC 150/179, 31 records de segments, RE 222 (Novablast 5 J -> 599 km)",
    "Bloc seuil improvise au tunnel (km 14-15) : GPS lisse mais FC 162-179 confirme, km 15 en 5:08",
    "Nutrition analysee : 2,5 L echelonnes adaptes ; vertiges avant le 2e gel (1h40) -> regle coach : gel toutes les 40-45 min sur les sorties >2h",
    "Semaine reorganisee : vendredi EF+technique, samedi seuil (jambes fraiches), dimanche PPG"
  ]},
  {"build":108,"date":"15 juillet 2026","sha":"","tag":"Chasse a la dette — 5 bugs des nouveautes corriges","items":[
    "Wrapped : le diaporama continuait de tourner en arriere-plan apres fermeture (timer fantome) ; reouverture rapide pouvait creer un double overlay — corriges",
    "Echap ferme desormais aussi le Wrapped et le replay (en priorite au-dessus de la fiche et des aides)",
    "Meteo historique : les deux cartes (efficience + acclimatation) declenchaient chacune leur appel — desormais un seul fetch partage",
    "Cache meteo : une course d'ecriture entre les deux cartes ecrasait des donnees et provoquait un re-appel a chaque ouverture du Cockpit — fusion a l'ecriture + marquage des dates introuvables (1 appel puis 0)"
  ]},
  {"build":107,"date":"15 juillet 2026","sha":"","tag":"Score d'acclimatation chaleur","items":[
    "Nouvelle carte Cockpit : ton niveau d'acclimatation a la chaleur (expositions >25\u00b0C sur 21 jours, meteo reelle de Lyon, 8 expositions = 100%)",
    "Benefice chiffre : bien acclimate, ta derive cardiaque a 30\u00b0C tombe d'environ un tiers (~10 bpm au lieu de ~15)",
    "Chaque sortie sous la canicule devient un investissement visible au lieu d'une punition",
    "Point d'aide ? pedagogique (adaptations physiologiques, persistance des gains pour novembre) ; reutilise le cache meteo de l'efficience"
  ]},
  {"build":106,"date":"15 juillet 2026","sha":"","tag":"Efficience aerobie — ta progression revelee malgre la chaleur","items":[
    "Nouvelle carte Cockpit : ton allure equivalente a 145 bpm, moyennee par semaine sur tes footings route (trails et seuil exclus)",
    "Correction temperature automatique : la FC de CHAQUE seance historique est corrigee via la meteo reelle de Lyon (archives Open-Meteo, 18h), sinon la canicule ferait croire a une regression",
    "Sparkline S25 -> S29, delta en s/km gagnees a effort egal, point d'aide ? pedagogique",
    "Premiere lecture : ~5 s/km gagnees a effort egal depuis S26 — le moteur grossit meme sous la canicule"
  ]},
  {"build":105,"date":"15 juillet 2026","sha":"","tag":"FC ajustee temperature — ta vraie forme sous la chaleur","items":[
    "Nouvel indicateur dans les fiches de seances chaudes : ta FC equivalente a 15\u00b0C (derive thermique ~1 bpm par \u00b0C au-dessus de 15, plafonnee a 15)",
    "Affiche FC brute -> FC ajustee + le %FCmax reel de l'effort, avec explication pedagogique",
    "Applique aux 2 seances chaudes documentees : EF du 15/7 (147 -> ~132 bpm, 69% au lieu de 77%) et Croisse Baulet",
    "Les prochaines seances loggees par temps chaud incluront la temperature automatiquement"
  ]},
  {"build":104,"date":"15 juillet 2026","sha":"","tag":"S29 : 1re seance loggee (EF sous chaleur) + semaine redatee","items":[
    "EF aerobie loggee : 10,35 km a 5:48/km d'une regularite remarquable, FC 147/161, cadence 175, depart 19h44 sous forte chaleur (Novablast 5 J, 566 -> 576 km)",
    "Lundi-mardi en repos assume (fatigue ecoutee apres le double trail) - demarrage de semaine mercredi, conforme a la vigilance de la revue S28",
    "Semaine redatee suivant le conseil coach : jeudi EF+technique, vendredi seuil 2x8 (jambes fraiches), samedi PPG, dimanche sortie longue",
    "Tout recalcule : ACWR, forme, Wrapped (17 sorties / 203 km)"
  ]},
  {"build":103,"date":"14 juillet 2026","sha":"","tag":"Design epure — strate 3 (fiches seance/semaine)","items":[
    "Callouts (objectif/benefices/vigilance) : fond neutre + liseré semantique fin (teal/vert/ambre), fini les aplats colores",
    "Chips chaussure degraissees (sans emoji), fond gris neutre ; hero de fiche aere sans bordure",
    "Modal a rayon genereux (22px) ; blocs internes (deroule, coach, nutrition) adoucis en gris clair",
    "Contrastes verifies WCAG AA sur tous les nouveaux fonds — la refonte epuree couvre desormais toute l'app"
  ]},
  {"build":102,"date":"14 juillet 2026","sha":"","tag":"Design epure — strate 2 (Seances, Cockpit, Courses)","items":[
    "La grammaire epuree du POC generalisee : cartes sans bordure a ombre douce sur les 3 autres onglets",
    "Hero Cockpit eclairci (fini le degrade sombre) : grand chiffre de forme sur blanc, couleur dynamique preservee (vert/ambre/rouge selon score)",
    "Selecteur de fenetres (2/4/8/12 sem.) transforme en segmented control style iOS",
    "Large Titles sur Cockpit et Courses ; boutons Wrapped et Replay degraisses (blancs, sobres, fini le scintillement)"
  ]},
  {"build":101,"date":"14 juillet 2026","sha":"","tag":"Revue de semaine S28","items":[
    "Ajout de la revue coach de la S28 (Recuperation post-Deraille) dans la fiche semaine",
    "Bilan : 5/6 seances - 60,96 km, une semaine de recup a 61 km au lieu de 36, mais intelligemment construite (intensite basse, doublé trail plaisir en montagne)",
    "Vigilance formulee pour S29 : demarrage doux apres deux grosses descentes consecutives"
  ]},
  {"build":100,"date":"12 juillet 2026","sha":"","tag":"POC design epure (direction Apple) sur l'Accueil","items":[
    "Fond global gris perle iOS (#F4F4F6), cartes blanches SANS bordure avec ombre a peine perceptible, rayons genereux",
    "Nouveau Large Title : Aujourd'hui + date du jour en tete de l'Accueil",
    "Carte Prochaine seance : fini le degrade sombre, blanc epure avec titre typographique fort (sans-serif systeme)",
    "Quoi de neuf : accent ambre discret au lieu du degrade jaune ; contrastes verifies WCAG AA",
    "POC a valider sur telephone avant de generaliser la direction aux autres onglets"
  ]},
  {"build":99,"date":"12 juillet 2026","sha":"","tag":"Retrait du hero vivant","items":[
    "Suppression de la banniere animee (coureur au coucher de soleil) sur l'Accueil, selon preference",
    "L'Accueil recommence directement par la carte Prochaine seance, comme avant",
    "Aucun impact sur le reste : Wrapped, replay et VO2max restent en place"
  ]},
  {"build":98,"date":"12 juillet 2026","sha":"","tag":"Wahoo : Hero vivant sur l'accueil","items":[
    "Nouvelle banniere animee en tete de l'Accueil : un coureur court le long d'un chemin au coucher de soleil, avec collines en parallaxe et soleil qui pulse",
    "Message d'accueil contextuel selon l'heure (footing matinal / journee / sortie du soir) + J-x avant la prochaine course",
    "Anime en douceur, respecte reduced-motion (coureur fige si l'utilisateur le demande)",
    "Termine la serie des effets wahoo : Wrapped, replay de sortie, VO2max, hero vivant"
  ]},
  {"build":97,"date":"12 juillet 2026","sha":"","tag":"VO2max enrichi : multi-records + aide explicative","items":[
    "Estimation VO2max desormais basee sur tes 3 records (5/10/semi) ponderes, plus juste qu'un seul chrono (42 central, fourchette 39-44)",
    "Affiche aussi ton profil (plutot vitesse/endurance selon l'ecart entre distances) et le detail par distance",
    "Nouveau point d'interrogation (?) : explique ce qu'est le VO2max et situe ton niveau sur une echelle (loisir -> elite), avec un +tu es ici+",
    "Transparent sur la methode (VDOT Jack Daniels) ; l'aide s'ouvre sans relancer l'animation"
  ]},
  {"build":96,"date":"12 juillet 2026","sha":"","tag":"Wahoo : VO2max revele (jauge animee)","items":[
    "Nouvelle carte VO\u2082max dans le Cockpit : une jauge demi-cercle s'anime de 0 jusqu'a ton estimation",
    "Calcul VDOT (methode Jack Daniels) a partir de tes VRAIS records (retient le meilleur effort : 10 km)",
    "Affiche l'estimation (~44), une interpretation qualitative et un marathon theorique (~3h35-3h50, coherent avec ta cible)",
    "Transparent sur la source (d'apres ton 10 km en 46:14) ; respecte reduced-motion"
  ]},
  {"build":95,"date":"12 juillet 2026","sha":"","tag":"Wahoo : Replay de sortie anime","items":[
    "Nouveau : revivre une sortie trail en animation. Un point suit ton profil d'altitude reel pendant que l'altitude, la FC et la distance defilent en direct",
    "Phases narratives (mont\u00e9e, sommet du Croisse Baulet a 2000 m, descente engagee) et couleur du point selon la pente",
    "Donnees seconde par seconde importees de Strava (Petit Croisse Baulet du 12/7)",
    "Bouton 🎬 Revoir cette sortie dans la fiche des seances qui ont un replay ; respecte reduced-motion"
  ]},
  {"build":94,"date":"12 juillet 2026","sha":"","tag":"S28 : 2e sortie trail du week-end (Petit Croisse Baulet)","items":[
    "Nouvelle seance loggee : Petit Croisse Baulet avec les copains (11 km, D+ 530 m, 2h35, sous forte chaleur, Cascadia 19)",
    "Temps fort : montee du Croisse Baulet (257 m D+ sur ~1 km, pente ~24%) puis longue descente engagee",
    "Cascadia 19 : 230 -> 241 km ; S28 passe a 5/6 seances - 60,96 km",
    "Tout recalcule : ACWR (1.01 -> 1.10), graphe denivele, Wrapped (16 sorties / 193 km / 2432 m D+)"
  ]},
  {"build":93,"date":"11 juillet 2026","sha":"","tag":"Wahoo : Ta saison en chiffres (Wrapped)","items":[
    "Nouvelle experience plein ecran facon stories : 7 cartes animees qui defilent avec tes chiffres de saison",
    "Sorties, km (equiv. marathons), D+ (equiv. Tour Eiffel), heures d'effort, records, streak, puis cap sur Nice",
    "100% calcule depuis tes vraies seances loggees ; barres de progression, grands chiffres animes, tap pour avancer",
    "Accessible depuis l'onglet Courses (bouton scintillant en tete) ; respecte reduced-motion"
  ]},
  {"build":92,"date":"11 juillet 2026","sha":"","tag":"Polish : finitions UX/accessibilite","items":[
    "Texte de la semaine en cours n'est plus tronque (passe sur 2 lignes si besoin)",
    "Etat meteo indisponible : desormais cliquable pour reessayer",
    "Hero du Cockpit accessible au clavier (role bouton + focus + Entree/Espace)",
    "Zones tactiles des boutons d'aide (?) etendues a ~44px (recommandation mobile), sans changer leur taille visuelle",
    "Nudge adapte a la phase road trip USA (randos/temps de pied) au lieu d'un rappel d'inactivite"
  ]},
  {"build":91,"date":"11 juillet 2026","sha":"","tag":"Fix 2 : comportements temporels (course, timeline, bouton)","items":[
    "Le nudge du coach connait desormais les courses : message de fraicheur en semaine de course, message special le jour J (fini le rappel d'inactivite le matin du marathon)",
    "La timeline suit la prochaine course a venir (bascule sur SainteExpress apres Nice) et disparait quand la saison est terminee",
    "Le bouton En cours se masque si la semaine courante n'existe pas dans le plan (il ne menait nulle part)",
    "Comportement du jour inchange, valide par simulation de dates (J-3, jour J, entre-courses, apres-saison, 2027)"
  ]},
  {"build":90,"date":"11 juillet 2026","sha":"","tag":"Fix 1 : cadence coherente + Quoi de neuf fiable + typo Coach","items":[
    "BUG corrige : deux elements partageaient l'id ck-cad-val, affichant deux cadences contradictoires (81 vs 172 spm) sur le meme ecran",
    "Cadence normalisee a la source : les valeurs un pied (<120) sont converties en spm standard deux pieds ; KPI en mediane (robuste au trail)",
    "BUG corrige : la carte Quoi de neuf pouvait etre consommee par un rendu en arriere-plan sans jamais s'afficher ; le diff n'est desormais consomme que si l'Accueil est visible",
    "Typo corrigee dans une reponse du Coach (log gees -> loggees)"
  ]},
  {"build":89,"date":"11 juillet 2026","sha":"","tag":"Fix : bouton En cours disponible et plus visible","items":[
    "Le bouton flottant En cours est desormais present a tout niveau de scroll sur l'onglet Seances (avant : seulement apres avoir scrolle sous la semaine en cours)",
    "Rendu plus visible : plus grand, texte plus gras, ombre renforcee avec anneau",
    "Reste masque sur les autres onglets ; le clic ramene toujours a la semaine en cours"
  ]},
  {"build":88,"date":"11 juillet 2026","sha":"","tag":"S28 : ajout sortie trail montagne","items":[
    "4e seance de S28 loggee : Trail montagne avec les copains (10,7 km, D+ 646 m, 2h07, Cascadia 19)",
    "Caracterisee comme sortie trail plaisir : montee marchee + descente active, fiche complete (structure, benefices, conseils)",
    "Cascadia 19 : 219 -> 230 km",
    "S28 passe a 4/5 seances - 49,92 km ; ACWR reajuste (0.90 -> 1.01) integrant le denivele"
  ]},
  {"build":87,"date":"11 juillet 2026","sha":"","tag":"UX : Cockpit resume executif + sections repliables","items":[
    "Resume executif en tete du Cockpit : 2-3 constats cles generes depuis les donnees (charge, forme, tendance Z2)",
    "Sections repliables : Volume & charge ouverte par defaut, les 4 autres fermees (progressive disclosure)",
    "Cockpit passe de 4,8 a 3,5 ecrans a l'ouverture (-27%) ; on deplie ce qu'on veut creuser",
    "Les graphes se rendent correctement a l'ouverture d'une section (rebuild au toggle), zero graphique vide"
  ]},
  {"build":86,"date":"11 juillet 2026","sha":"","tag":"UX : Timeline trajectoire vers Nice","items":[
    "Nouvelle frise horizontale sur l'Accueil montrant la progression jusqu'au Marathon de Nice",
    "6 segments = les 6 phases jusqu'a la semaine du marathon (S24 a S45), phase actuelle mise en valeur",
    "Marqueur de position + remplissage progressif, calcules dynamiquement depuis la semaine ISO courante",
    "Objectif affiche : J-jours et cible temps (3h45), tap ouvre l'onglet Seances",
    "Distinct du Prepa plan (%) existant : la timeline montre la position calendaire, pas le taux de completion"
  ]},
  {"build":85,"date":"11 juillet 2026","sha":"","tag":"UX : Quoi de neuf (carte de retour)","items":[
    "Nouvelle carte ephemere sur l'Accueil qui signale ce qui a change depuis la derniere visite",
    "Detecte : nouvelle seance loggee (avec mention speciale si records battus), progression significative de la forme, streak qui augmente",
    "S'affiche une seule fois par changement (signature sauvegardee immediatement), jamais de repetition",
    "Premiere visite apres deploiement : rien ne s'affiche (pas de base de comparaison), comportement normal"
  ]},
  {"build":84,"date":"11 juillet 2026","sha":"","tag":"UX : Brief du matin consolide","items":[
    "La carte Prochaine seance affiche desormais la chaussure conseillee directement, sans tap",
    "Le creneau de depart (canicule) s'affiche dans la carte principale plutot que dans une banniere separee, des que la meteo est chargee",
    "Objectif : en 5 secondes le matin, tout est visible (quoi, combien, quelle chaussure, quand partir)",
    "Zero tap supplementaire, moteur de donnees inchange"
  ]},
  {"build":83,"date":"11 juillet 2026","sha":"","tag":"Fix : Coach IA repondait \"Connexion impossible\"","items":[
    "BUG corrige : le Coach affichait une erreur de connexion au lieu de repondre — l'appel API IA ne peut pas fonctionner depuis GitHub Pages (reserve a l'environnement Claude.ai)",
    "Ajout du fallback local _cReply (absent de cette app, il n'existait que dans RunY) : le Coach repond desormais depuis les donnees embarquees",
    "Couvre : prochaine seance, forme detaillee, fatigue, courses (Nice, SainteExpress), nutrition/protocole canicule, meteo, chaussures, allures, recuperation",
    "Les reponses API en erreur basculent aussi sur le fallback (pas seulement les echecs reseau)"
  ]},
  {"build":82,"date":"10 juillet 2026","sha":"","tag":"Finition espacement complete (grille 4px)","items":[
    "Harmonisation terminee : 0 valeur d'espacement hors grille 4px dans css.txt ET css_extra.txt",
    "Correction du pattern qui ratait les declarations en fin de bloc (sans point-virgule final)",
    "Verification renforcee : dimensions de tous les composants preservees, aucun debordement, 10 graphiques intacts",
    "Cloture du chantier design system : espacement 100% tokenisable sur la grille"
  ]},
  {"build":81,"date":"10 juillet 2026","sha":"","tag":"Finition espacement + accessibilite clavier","items":[
    "Sprint A : ~98 declarations d'espacement harmonisees sur la grille 4px (valeurs impaires 3/5/7/9/11/13px arrondies), sans toucher au rythme visuel principal",
    "Sprint B : la touche Echap ferme desormais n'importe quel overlay ouvert (Coach, aide cockpit, panneau version, fiche seance)",
    "Focus clavier visible confirme sur les elements interactifs",
    "Zero regression : 10 graphiques cockpit intacts, dimensions composants preservees"
  ]},
  {"build":80,"date":"10 juillet 2026","sha":"","tag":"Fix : graphique Progression allure par type (vide)","items":[
    "BUG corrige : le graphique Progression allure par type restait vide",
    "Cause : le moteur dynamique ecrasait les 3 series d'allure par type (EF/AM/Seuil) par une seule serie moyenne",
    "Correction : snapshot des series originales + reinjection alignee sur la fenetre reconstruite",
    "Robuste aux rebuilds multiples (logs repetes) ; les 10 graphiques du cockpit affichent desormais leurs donnees"
  ]},
  {"build":79,"date":"10 juillet 2026","sha":"","tag":"Design Sprint 5 : la signature","items":[
    "Celebration speciale doree quand une seance loggee contient des records (medaille, \"X records battus\", vibration renforcee)",
    "Nouvelle signature streak : nombre de semaines consecutives avec activite (icone flamme), affichee dans le bilan des 2 semaines",
    "Bilan reequilibre en 2x2 quand le streak est present",
    "Cloture de la roadmap UX/UI 2026 (5 sprints : tokens, cockpit hero, mouvement, coach copilote, signature)"
  ]},
  {"build":78,"date":"10 juillet 2026","sha":"","tag":"Design Sprint 4 : Coach copilote proactif","items":[
    "Nouvelle carte de suggestion proactive sur l'Accueil : le Coach commente ta situation reelle (ACWR, inactivite, forme, manque de qualite)",
    "Logique de priorite : alerte surcharge > relance apres inactivite > marge de volume > manque de qualite > forme au top",
    "S'affiche seulement si pertinent (jamais intrusif), ton visuel adapte (rouge/info/vert), clic ouvre le Coach",
    "100% base sur les vraies donnees loggees, aucune modification du moteur"
  ]},
  {"build":77,"date":"10 juillet 2026","sha":"","tag":"Design Sprint 3 : le mouvement qui a du sens","items":[
    "Moment de celebration gratifiant quand une seance est loggee comme faite (check anime + kilometrage + vibration legere)",
    "La celebration ne se declenche que pour le statut faite, pas pour saute/partiel/manque",
    "Garde-fou global prefers-reduced-motion : neutralise toute animation residuelle pour qui le demande (accessibilite)",
    "Reutilise les tokens espacement Sprint 1 et le systeme existant, aucune regression sur les animations en place"
  ]},
  {"build":76,"date":"10 juillet 2026","sha":"","tag":"Design Sprint 2 : Cockpit tableau de bord vivant","items":[
    "Ajout d'un hero metric en tete du Cockpit : la Forme du jour en grand (typo numerique 64px), cliquable pour l'explication",
    "Nouvelle entree d'aide detaillee pour la Forme du jour (ACWR, adherence, allure Z2, fraicheur)",
    "KPI VO2max fige (51.6, code en dur) remplace par la Cadence, reellement dynamique depuis les seances loggees",
    "Espacements du Cockpit alignes sur les tokens du Sprint 1",
    "Aucune modification du moteur de donnees : logique KPI intacte, seule la presentation evolue"
  ]},
  {"build":75,"date":"10 juillet 2026","sha":"","tag":"Design system Sprint 1 : tokens d'espacement","items":[
    "Ajout d'une echelle d'espacement en tokens CSS (base 4px : --sp-1 a --sp-12)",
    "Ajout de rayons complementaires (--rayon-sm, --rayon-pill)",
    "Conteneurs structurants alignes sur la grille 4px (accueil, cartes semaine, KPI, cockpit, hero rows)",
    "Fondation pour les prochains sprints UX ; aucun changement fonctionnel, espacements harmonises"
  ]},
  {"build":74,"date":"10 juillet 2026","sha":"","tag":"UX : navigation vers la semaine en cours","items":[
    "Auto-scroll vers la semaine en cours a la premiere ouverture de l'onglet Seances (par session)",
    "Nouveau bouton flottant qui apparait uniquement quand la carte de la semaine en cours n'est plus visible a l'ecran",
    "Badge Courante renomme en En cours",
    "Reutilise le mecanisme jumpToWeek() deja existant (aucune nouvelle logique de scroll a risque)"
  ]},
  {"build":73,"date":"10 juillet 2026","sha":"","tag":"UX : bouton Fermer icone-seule (rattrapage changelog)","items":[
    "Le bouton Fermer de la fiche semaine devient un bouton rond icone-seule au lieu d'une pilule texte+icone",
    "Corrige la sensation de bouton flottant au-dessus du titre de la semaine",
    "Rattrapage : cette entree avait ete omise du changelog lors du push precedent (le code etait deja en ligne)"
  ]},
  {"build":72,"date":"10 juillet 2026","sha":"","tag":"Fix date « à jour » désynchronisée","items":[
    "BUG corrigé : la date « Données à jour au » restait figée au 20 juin (champ MAJ en dur, jamais mis à jour depuis le build 39)",
    "La date est désormais dérivée automatiquement du dernier build du changelog — toujours synchrone avec le numéro de build"
  ]},
  {"build":71,"date":"9 juillet 2026","sha":"","tag":"Protocole hydratation canicule validé","items":[
    "S28 séance sortie longue enrichie : détail hydratation (1,5L ~850ml/h, électrolytes zéro cal. + 1 gel)",
    "Revue coach : stratégie validée, à reconduire tant que la canicule dure",
    "VIGILANCE mise à jour : protocole carburant/électrolytes canicule documenté comme référence"
  ]},
  {"build":70,"date":"9 juillet 2026","sha":"","tag":"S28 réorganisée — sortie longue avancée","items":[
    "Sortie longue loggée au jeudi (18,16 km avec Edwige) — avancée depuis vendredi pour libérer 4 jours de montagne",
    "EF aérobie marquée sautée (raison documentée) plutôt que restée à faire indéfiniment",
    "Ajout du libellé \"Sautee\" pour le statut skipped (gap UI pré-existant corrigé)",
    "Novablast 5 J : 548 → 566 km",
    "Conseil coach avant le départ : vigilance dos/lombaires sur les descentes chargées"
  ]},
  {"build":69,"date":"9 juillet 2026","sha":"","tag":"S28 s2 — footing avec Yannis","items":[
    "S28 séance 2 loggée : 10 km avec Yannis · FC 140/163 · forte chaleur · pause 18min",
    "Dérive FC en fin de sortie identifiée comme thermique, pas physiologique",
    "Clifton 10 : 1114 → 1124 km"
  ]},
  {"build":68,"date":"7 juillet 2026","sha":"","tag":"Tests de régression + bugs corrigés","items":[
    "scripts/test_regression.py : 16 tests runtime (vues, KPI, Coach, fiches) avant chaque push",
    "BUG corrigé : _ckLine plantait sur une série sans .v (régression du rebuild KPI)",
    "BUG corrigé : _curWeek() n'existait pas — le Coach croyait être en S26 (fallback)",
    "Discipline : preflight (statique) + test_regression (runtime) verts avant toute prod"
  ]},
  {"build":67,"date":"7 juillet 2026","sha":"","tag":"Learning — garde-fous anti-erreurs","items":[
    "scripts/preflight.py : 8 checks automatiques avant chaque push (pipeline, build, JS, emoji, semaine ISO, data, token, HTML)",
    "docs/LESSONS.md : journal des erreurs passées avec cause racine + garde-fou",
    "Le preflight a déjà attrapé 7 surrogate-pairs d'emoji — converties en codepoints",
    "CLAUDE.md : section Learning en tête, lue au démarrage de chaque session"
  ]},
  {"build":66,"date":"7 juillet 2026","sha":"","tag":"KPI 100% dynamiques","items":[
    "_ckRebuild() : les KPI se recalculent depuis les séances réelles à chaque chargement",
    "Plus besoin de figer _CK au build — VOL/RE/ACWR/D+/cadence/allure recalculés en live",
    "ACWR EMA (CTL 42j / ATL 7j) calculé dynamiquement depuis le RE réel de chaque séance",
    "Recalcul aussi après chaque nouveau log — les KPI bougent en temps réel"
  ]},
  {"build":65,"date":"7 juillet 2026","sha":"","tag":"Audit KPI — ACWR & forme corrigés","items":[
    "_CK régénéré avec S27 (course) et S28 (récup) — les séries s'arrêtaient à S26",
    "ACWR_DATA à jour : 0.69 (récup) au lieu de 1.57 (obsolète, parlait encore de la Circaète)",
    "BUG corrigé : KPI ACWR était codé en dur à 1.42 — label + valeur maintenant dynamiques",
    "ACWR reflète enfin le réel : pic 1.25 en S27 (course) → 0.67 en S28 (récup)"
  ]},
  {"build":64,"date":"7 juillet 2026","sha":"","tag":"S28 s1 — récup + finish FCmax","items":[
    "S28 séance 1 loggée : 11 km avec Anis · récup pure + dernier km à 4:14/km FC192",
    "Revue coach : système neuromusculaire complètement récupéré du trail (J+2)",
    "Novablast 5 J : 537 → 548 km"
  ]},
  {"build":63,"date":"6 juillet 2026","sha":"","tag":"S28 → récup post-Déraille","items":[
    "S28 transformée en récupération active (36 km, zéro intensité) après le trail",
    "Bloc seuil décalé : S29 devient Seuil découverte (reprise progressive)",
    "Décision coach : le D+ 957m + chaleur demandent 4-5j de vraie récup avant l'intensité",
    "Suite du plan inchangée — marge suffisante jusqu'à Nice (8 nov)"
  ]},
  {"build":62,"date":"6 juillet 2026","sha":"","tag":"Revue S27 — semaine course","items":[
    "Revue coach S27 : semaine course, 53 km, Déraille 2:52:48 (66e/180)",
    "REWIND S27 — 9 slides (Edwige, tempo stoppé, affûtage, course, descente, verdict A)",
    "JOURNAL S27 ajouté · cap sur Nice pour la suite"
  ]},
  {"build":61,"date":"5 juillet 2026","sha":"","tag":"Déraille — 66e/180 (top 37%)","items":[
    "Trail Déraille : 180 engagés confirmés — 66e = top 37%",
    "Palmarès et bilan mis à jour avec le total finishers"
  ]},
  {"build":60,"date":"5 juillet 2026","sha":"","tag":"🏁 Trail Déraille terminé !","items":[
    "Trail Déraille ajouté au Palmarès : 23,3km 2:52:48 · 66e/gen · 11e/18 M0 · D+957m",
    "S27 séance 4 (course) loggée · FC 168/181 · Cascadia 19",
    "Analyse coach terrain : gestion réussie, mur final thermique (pas nutritionnel)",
    "Cascadia 19 : 196 → 219 km · Déraille retirée des courses à venir"
  ]},
  {"build":59,"date":"3 juillet 2026","sha":"","tag":"Calendrier S26/S27 corrigé","items":[
    "Correction majeure : 29 juin = LUNDI S27 (pas dimanche S26)",
    "S27 s1 = 13km avec Edwige (lun) · s2 = tempo 2×15 interrompu gastrique (mar) · s3 = 10,5km EF (jeu)",
    "S26 finalisée à 21,9km / 2 séances — spéc trail annulée canicule · verdict B+",
    "Revue S26, REWIND, JOURNAL et HIST recalculés (S25-S27 ajoutés à l'historique)"
  ]},
  {"build":58,"date":"3 juillet 2026","sha":"","tag":"S27 sorties loggées + J-2 Déraille","items":[
    "S27 séance 1 (lun 30 juin) : 6,55km EF+tempo Magic Speed 4 FC149/172",
    "S27 séance 3 (jeu 2 juil) : 10,55km EF berges FC148/170 Clifton 10 — parfait J-3",
    "Clifton 10 : 1103 → 1114 km (⚠️ fin de vie — pas pour la Déraille)",
    "S26 revue coach + JOURNAL + REWIND 8 slides inclus"
  ]},
  {"build":57,"date":"1 juillet 2026","sha":"","tag":"S26 s3 + S27 s1 loggées","items":[
    "S26 séance 3 : 13,02 km dimanche soir (remplacement spéc trail) · FC 155/178 · 20 PRs",
    "S27 séance 1 : 6,55 km lundi matin · EF+tempo naturel · Magic Speed 4 · FC 149/172",
    "Novablast 5 J : 524 → 537 km · Magic Speed 4 : 51 → 58 km",
    "Revues coach : dérive cardiaque S26s2, gestion canicule S26s3, jambes qui répondent S27s1"
  ]},
  {"build":56,"date":"25 juin 2026","sha":"","tag":"S26 séance 2 loggée — canicule","items":[
    "S26 · séance 2 (EF aérobie jeudi) loggée depuis Strava — 10,66 km 5:47/km FC148/161",
    "Revue coach : dérive cardiaque confirmée (km 5:17 à FC153, pas de gain réel)",
    "Novablast 5 J : 513 → 524 km",
    "Mardi-mercredi sautés (canicule ~40 °C) — contexte intégré"
  ]},
  {"build":55,"date":"23 juin 2026","sha":"","tag":"Coach IA — vrai LLM","items":[
    "Coach remplacé par Claude Sonnet 4.6 via API — plus de regex, vraie compréhension",
    "Contexte dynamique injecté : forme, TSB, ACWR, séances loggées, J-X course, canicule",
    "Mémoire de conversation (12 derniers échanges) — le coach garde le fil",
    "8 chips repensées : Allure AM, SaintExpress, Dos, Nutrition Déraille..."
  ]},
  {"build":53,"date":"22 juin 2026","sha":"","tag":"Fix Cockpit — zones ACWR","items":[
    "Zones ACWR (vert/orange/rouge) clipées dans le SVG — plus de voile sur les graphes voisins",
    "Gradient fill supprimé sous la courbe ACWR (lisibilité)"
  ]},
  {"build":52,"date":"22 juin 2026","sha":"","tag":"Cockpit Strava + revue séance","items":[
    "Cockpit : graphes régénérés depuis Strava réel (S12→S26, 53 sorties)",
    "VOL / RE / ACWR / D+ / Z2 / DC / PACE / FCZ / CAD — fenEtres 2/4/8/12 semaines",
    "5 sorties récentes + streams FC (Gypaètes, AM marathon, EF, S26s1, SL Saone)",
    "Prénom Coach dynamique (PROFIL.prenom — fin du Bonjour Loïc en dur)"  
  ]},
  {"build":51,"date":"22 juin 2026","sha":"","tag":"S26 séance 1 loggée","items":[
    "S26 · séance 1 (footing facile + 6 lignes droites) marquée faite — données Strava",
    "11,26 km · 1h06 · 5:53/km · FC 148/169 · cadence 172 · Novablast 5 J",
    "Revue du coach ajoutée (chaleur, cœur un peu haut, fraîcheur post-repos)",
    "Kilométrage Novablast 5 J : 502 → 513 km"
  ]},
  {"build":50,"date":"22 juin 2026","sha":"","tag":"Sprint B · Onglet Courses","items":[
    "Palmarès devient Courses — à venir + passées au même endroit",
    "Section « À venir » : J-X + accès direct au dossier de course",
    "Section « Passées » : résultats et bilans (inchangés)",
    "Cohérence IA : toutes les courses regroupées dans un seul onglet"
  ]},
  {"build":49,"date":"22 juin 2026","sha":"","tag":"Sprint A · Page d'accueil","items":[
    "Vraie page Accueil — dashboard séparé du plan (coup d'œil sans scroller)",
    "2 raccourcis : héros = prochaine séance · carte = semaine en cours",
    "Bandeau canicule conservé sur l'Accueil",
    "Onglet Suivi dissous — bilan/charge basculés dans le Cockpit",
    "Nouvelle barre : Accueil · Séances · Coach · Cockpit · Palmarès"
  ]},
  {"build":48,"date":"22 juin 2026","sha":"","tag":"Sprint 5 · Enforcement","items":[
    "CSS mort purgé — anciennes règles .tabbar/.tab supprimées (markup retiré au Sprint 2.5)",
    "Tailles de police petit-texte consolidées sur l'échelle (bande .75–1.1rem, décalage <1px)",
    "Graisses et tailles de graphes laissées intactes — layout-critiques, pas de régression",
    "Dette CSS réduite, cohérence typographique resserrée"
  ]},
  {"build":47,"date":"22 juin 2026","sha":"","tag":"Sprint 4 · Profondeur & polish","items":[
    "Transition fondu-montant au changement d'onglet",
    "Retour au tap (press-scale) cohérent sur cartes, tuiles et barre",
    "Pop de l'icône active dans la bottom bar",
    "Apparition des cartes au scroll (reveal, avec filet de sécurité)",
    "Haptique sur navigation et Coach · respect de prefers-reduced-motion",
    "Refonte UX/UI close — Sprints 0 à 4 terminés"
  ]},
  {"build":46,"date":"22 juin 2026","sha":"","tag":"Sprint 3 · Le mot du coach","items":[
    "Message d'accueil du Coach enrichi — ligne contextuelle priorisée à l'ouverture",
    "Priorité : canicule > charge élevée (ACWR) > affûtage course > marge de volume",
    "Le Coach « parle » dès le bouton central — pas d'étiquette redondante sur la Home",
    "Sprint 3 bouclé (place du Coach via la bottom bar + mot contextuel)"
  ]},
  {"build":45,"date":"21 juin 2026","sha":"","tag":"Sprint 2.5 · Bottom tab bar","items":[
    "Navigation principale déplacée en barre fixe en bas (standard mobile, accessible au pouce)",
    "Coach promu au centre de la barre, surélevé — fini le FAB perdu",
    "Barre frostée translucide + icônes line, safe-area gérée",
    "Haut de la Home libéré : le héros respire encore plus",
    "Ancien FAB Coach retiré"
  ]},
  {"build":44,"date":"21 juin 2026","sha":"","tag":"Sprint 2 · Langage d'overlay unifié","items":[
    "Backdrop unique pour les 9 overlays — même opacité + même flou (avant : .55/.6/.92, sans flou)",
    "Poignée (grab handle) harmonisée sur toutes les sheets",
    "Sheet de théorie dotée d'une poignée",
    "Règle posée : sheet = action rapide (monte du bas) · plein écran = immersion",
    "Tokens d'overlay (--ov-backdrop, --ov-blur) centralisés"
  ]},
  {"build":43,"date":"21 juin 2026","sha":"","tag":"Sprint 1 · Home qui respire","items":[
    "Home refondue — un seul point focal : la prochaine séance en héros agrandi",
    "Forme + prochaine course en tuiles compactes côte à côte (avant : blocs pleine largeur empilés)",
    "Position & météo en lignes fines ; courses lointaines repliées en pastilles",
    "Nudge auto-sync allégé en bandeau fin",
    "Bande de comptes à rebours retirée du haut — le héros prend la tête"
  ]},
  {"build":42,"date":"21 juin 2026","sha":"","tag":"Sprint 0 · Design System","items":[
    "Design system sémantique — :root refondu (primaire teal unique + états ok/warn/danger + échelle typo 7 niveaux)",
    "Couleurs rationalisées — bleu fusionné au teal, 4 verts → 1, orange+jaune → ambre, violet retiré",
    "Migration chrome + graphes (css + app.js) vers les tokens sémantiques",
    "Palette catégorielle des segments refaite, distincte et sans violet (teal/vert/slate/ambre/rouge)",
    "Profondeur iOS 27 — deux niveaux d'ombre + échelle typo exposée en variables"
  ]},
  {"build":41,"date":"21 juin 2026","sha":"","tag":"Audit final + doc","items":[
    "Fix: GEAR — Novablast 5 J et V désormais distinctes (6 paires, V verte neuve à 0km)",
    "Documentation technique v2.0 — 1657 lignes, 21 sections, guide de réplication complet",
    "CLAUDE.md enrichi — contexte complet pour reprise/réplication",
    "Audit cohérence — 9 vérifications calculs dynamiques validées"
  ]},
  {"build":40,"date":"21 juin 2026","sha":"6f3dc9a5","tag":"Sprint B+C Roadmap","items":[
    "Claude Coach in-app sans API — 10 scénarios (forme/fatigue/demain/météo/courses/nutrition/chaussures/allures/récup)",
    "Auto-sync nudge — détection séances non loggées au démarrage",
    "PMC Performance Management Chart — CTL/ATL/TSB (fitness/fatigue/forme) dans Cockpit",
    "ACWR 100% dynamique via EMA (CTL 42j / ATL 7j) — plus de valeur statique",
    "Icônes aide ? Cockpit — couleur corrigée (visible sur fond clair)"
  ]},
  {"build":39,"date":"20 juin 2026","sha":"f2794553","tag":"Sprint A Roadmap · IA & UX","items":[
    "Score de forme composite 0–100 (ACWR 30% + adhérence 25% + Z2 pace 25% + fraîcheur 20%)",
    "Barre cliquable hero → détail 4 composantes avec barres de progression",
    "Icône aide ? sur score de forme → overlay plein écran (scrollTop=0 à l'ouverture)",
    "Icônes aide ? sur 9 graphes Cockpit (volume · RE · ACWR · D+ · Z2 · découplage · allures · FC · cadence)",
    "Badge Build XX toujours visible — intégré dans renderHeader"
  ]},
  {"build":38,"date":"19 juin 2026","sha":"65668b30","tag":"Session J1 · Roadmap complète","items":[
    "Rewind S25 (10 slides · verdict A) + revue coach dans fiche semaine",
    "Checklist J-7 Nice (21 items) + SaintExpress (22 items) dans dossiers",
    "Journal nutrition dans log rapide — chips TA/Gel/Cherry/Amarena",
    "iOS Install flow · Adaptation allure T° · Mode canicule auto 10j"
  ]},
  {"build":37,"date":"19 juin 2026","sha":"ac1520eb","tag":"Session J1 · Produit & Data","items":[
    "Palmarès 4ème onglet — 5 courses officielles avec bilans coach",
    "Déplacer / Skipper séance · Checklist J-7 Déraille · Cockpit 9 graphes + 4 streams",
    "Log self-service · Palmarès MyDataRun · Historique versions"
  ]},
  {"build":36,"date":"19 juin 2026","sha":"18dabd58","tag":"Session J1 · Séances","items":[
    "S25 bouclée 5/5 · 56.6 km · Clifton 10 → 1103 km",
    "Banner météo créneaux · Accents séances corrigés"
  ]},
]

PALMARES=[
  {"nom":"Run In Lyon — Semi-Marathon","alias":"Run In Lyon semi","date":"2026-10-04","lieu":"Lyon · France","type":"semi","distance":21.1,"dplus":71,"dminus":None,"temps":"1:52:30","allure":"5:20","classement_gen":None,"classement_cat":None,"total_finishers":None,"cat":None,"fc_moy":177,"fc_max":189,"cal":1767,"chaussures":"Novablast 5 V","meteo":None,"statut":"termine","strava_id":"20443383374","accent":"#F4561D","bilan":"<strong>Semi couru malade, après cinq nuits à 3-4h de sommeil.</strong> 1:52:30 (chrono identique au meilleur effort semi Strava, ramené à 21,1 km : 1:53:29 pour 21,30 km GPS ; non confirmé par la page résultats de l'organisateur) · 5:20/km. Parti seul quand son partenaire s'est arrêté refaire ses lacets : km 1-10 à 5:06/km, km 11-20 à 5:33/km, split positif de 27 s/km. FC 177 en moyenne, 189 au maximum, environ 15 battements au-dessus de la même allure en bonne santé (22/08). <strong>Enseignement :</strong> l'ancrage humain tient la discipline d'allure, son absence se paie en moins de 3 km — le meneur d'allure s'impose pour Nice."},
  {"nom":"Trail Déraille — Lac des Sapins","alias":"Déraille","date":"2026-07-05","lieu":"Lac des Sapins · France","type":"trail","distance":23.3,"dplus":957,"dminus":957,"temps":"2:52:48","allure":"7:12","classement_gen":66,"classement_cat":11,"total_finishers":180,"cat":"M0","fc_moy":168,"fc_max":181,"cal":2388,"chaussures":"Cascadia 19","meteo":"Chaleur intense · exposition forte","statut":"termine","strava_id":"19186067917","accent":"#F4561D","bilan":"<strong>Course de gestion réussie dans des conditions extrêmes.</strong> Réalisée sur ~4h de sommeil (nuit blanche jusqu'à 2h après le match de l'équipe de France), sans aucune préparation trail depuis la Circaète (zéro côte, zéro dénivelé), par forte chaleur. 66e au général sur 180 engagés (top 37%), 11e/18 en catégorie M0.<br><br><strong>La stratégie était la bonne — les données le prouvent :</strong> FC moyenne 168 (88% FCmax) tenue sur 2h52 sans jamais d'explosion. Contrairement à la Circaète, aucun effondrement. Gestion parfaite en montée (marche active sur la Montée des Stèles : +158m à 15,7% de pente au km 13). <strong>Descente exceptionnelle</strong> — km 18 à 4:46/km, vraie signature de force.<br><br><strong>Le mur des 2 derniers km était thermique, pas nutritionnel :</strong> la FC reste haute (170-171) alors que l'allure s'effondre — signature déshydratation + surchauffe, pas de panne de sucre. Nutrition correcte (3 gels + 3L dont 1L électrolytes) mais insuffisante face à la chaleur. Alternance marche/course sur la fin, perte de ~2 min sur le partenaire.<br><br><strong>Objectifs atteints :</strong> relancer la machine, tester la nutrition, courir intelligemment. Zéro séquelle physique ou mentale. <strong>Enseignements pour Nice :</strong> la tête est le meilleur atout, la descente est une arme, la gestion thermique et l'endurance spécifique trail restent à travailler."},
  {"nom":"Trail - Circaète (Gypaète)","alias":"Circaète","date":"2026-06-06","lieu":"Ardèche · France","type":"trail","distance":29.8,"dplus":1661,"dminus":1661,"temps":"4:57:38","allure":"9:36","classement_gen":182,"classement_cat":None,"total_finishers":None,"cat":"M0","fc_moy":152,"fc_max":178,"cal":3191,"chaussures":"Cascadia 19","meteo":"26-31°C · canicule sèche","statut":"termine","strava_id":"18810734775","accent":"#F4561D","bilan":"Première grande épreuve trail de la saison. Crise électrolytique progressive à partir du km 20 — déshydratation sévère en chaleur extrême. Course terminée en 4:57:38 malgré l'effondrement. <strong>Leçon fondatrice :</strong> intégration systématique de TA Electrolytes dans toutes les sorties et courses depuis. #182 au général."},
  {"nom":"Run In Lyon 10km","alias":"Run In Lyon 10k","date":"2022-10-02","lieu":"Lyon · France","type":"route","distance":10,"dplus":None,"dminus":None,"temps":"53:58","allure":"5:24","classement_gen":4900,"classement_cat":None,"total_finishers":None,"cat":None,"fc_moy":None,"fc_max":None,"cal":None,"chaussures":None,"meteo":None,"statut":"termine","strava_id":None,"accent":"#CA8A04","bilan":"10km sur les berges de Lyon en 53:58 · allure 5:24/km. #4900 au général sur une très grande course de masse. <strong>Référence pour calibrer la progression :</strong> objectif sub-50 min en 2026-2027."},
  {"nom":"SaintéLyon — Relais Équipe","alias":"SaintéLyon relay","date":"2022-12-03","lieu":"Yssingeaux → Lyon","type":"trail_nuit","distance":22.77,"dplus":459,"dminus":900,"temps":"2:27:00","allure":"6:28","classement_gen":None,"classement_cat":None,"total_finishers":None,"cat":None,"fc_moy":None,"fc_max":None,"cal":None,"chaussures":None,"meteo":"Nuit · ~4°C · hiver","statut":"termine","strava_id":None,"accent":"#F4561D","bilan":"Relais #4 de l'équipe SaintéLyon. <strong>Référence directe pour la préparation SaintExpress 2026 :</strong> segment km 27-45 du parcours. Allure 6:28/km de nuit avec 459m D+. Validation que le segment final est gérable après km 27 parcourus."},
  {"nom":"Trail des Hautes Chaumes","alias":"Hautes Chaumes","date":"2022-05-08","lieu":"Roche · France","type":"trail","distance":6,"dplus":None,"dminus":None,"temps":"46:29","allure":"7:45","classement_gen":44,"classement_cat":None,"total_finishers":None,"cat":"SE","fc_moy":None,"fc_max":None,"cal":None,"chaussures":None,"meteo":None,"statut":"termine","strava_id":None,"accent":"#F4561D","bilan":"Court trail local ~6km · allure 7:45/km. <strong>#44 au général</strong> — excellent classement sur une épreuve technique. Catégorie SE à l'époque."},
  {"nom":"Harmonie Mutuelle Semi de Paris","alias":"Semi de Paris","date":"2022-03-06","lieu":"Paris · France","type":"semi","distance":21.1,"dplus":None,"dminus":None,"temps":"1:53:21","allure":"5:22","classement_gen":27259,"classement_cat":None,"total_finishers":None,"cat":None,"fc_moy":None,"fc_max":None,"cal":None,"chaussures":None,"meteo":None,"statut":"termine","strava_id":None,"accent":"#F4561D","bilan":"Premier grand semi-marathon officiel. 1:53:21 chrono réel · 5:22/km. #27259 au général dans l'une des plus grandes courses de France. <strong>Référence de départ :</strong> objectif 1:44 au Semi de Lyon du 4 oct. 2026 — réalisé en 1:52:30, couru malade (voir la fiche de la course)."}
]
_charge_revues_seances(SEANCES_BY_WEEK)
# Rewind de seance (P4) : index des seances qui ont un Rewind (src/rewind/<sem>-<n>.json, scripts/rewind_seance.py)
# et cible appliquee quand la seance a ete remplacee (realise.cible). assemble.py publie les fichiers.
import glob as _glob, os as _os
REWIND_SEANCE=[]
for _p in sorted(_glob.glob(_os.path.join('rewind','*.json'))):
  _k=_os.path.basename(_p)[:-5];_w,_n=_k.split('-')
  _s=next((x for x in SEANCES_BY_WEEK.get(_w,SEANCES_BY_WEEK.get(int(_w),[])) if str(x.get('id'))==_n),None)
  if not _s or (_s.get('realise') or {}).get('statut') not in ('fait','partiel'):
    raise SystemExit(f"Rewind {_k} : seance absente ou non realisee")
  _c=_j.load(open(_p,encoding='utf-8')).get('cible')
  if _c:_s['realise']['cible']=_c
  REWIND_SEANCE.append(_k)
_j.dump({"PHASES":PHASES,"COUL":COUL,"SEMAINES":SEMAINES,"SBW":SEANCES_BY_WEEK,"REWIND_SEANCE":REWIND_SEANCE,"GEAR":GEAR,"RACES":RACES,
  "PROFIL":PROFIL,"PROJ":PROJ,"RECORDS":RECORDS,"VIGILANCE":VIGILANCE,"S24R":S24_REALISE,
  "HIST":_hist["HIST"],"POLAR":_hist["POLAR"],"ALLURES":ALLURES,"ALLURES_COURSE":ALLURES_COURSE,"ZONES_FC":ZONES_FC,"MONTHLY":MONTHLY,"SAISON2026":SAISON2026,"SAISON_EFF":SAISON_EFF,"COCKPIT_SOURCES":COCKPIT_SOURCES,"ACWR_DATA":ACWR_DATA,"RECORDS_PERF":RECORDS_PERF,"JOURNAL":JOURNAL,"REWINDS":REWINDS,"MAJ":CHANGELOG[0]["date"],"HEATMAP":HEATMAP,"DOSSIERS":DOSSIERS,"PALMARES":PALMARES,"CHANGELOG":CHANGELOG},open('data.json','w',encoding='utf-8'),ensure_ascii=False)
print("OK")
