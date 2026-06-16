
import datetime as _dt
RACE_DATES={"Course — Objectif A":"2026-11-08","Course — Objectif B":"2026-11-28","Trail — Objectif C":"2026-07-05"}
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
CSS=open('/tmp/css.txt').read()

P_REC="6:15-6:45/km"; P_EF="5:50-6:25/km"; P_AM="≈5:15/km"; P_SEUIL="≈4:50/km"; P_TRAIL="à l'effort"
P_S30="≈4:40/km"; P_S60="≈4:55/km"; F_S30="172-180"; F_S60="166-174"
F_REC="<140"; F_EF="135-150"; F_AM="152-163"; F_SEUIL="166-175"
GREEN="#22c55e";BLUE="#3b82f6";ORANGE="#f97316";VIOLET="#8b5cf6";RED="#ef4444";YELLOW="#eab308";TEAL="#14b8a6"

def segs(raw):
    t=0;out=[]
    for s in raw:
        s=dict(s); s['debut']=t; s['fin']=t+s['duree']; t+=s['duree']; out.append(s)
    return out
def mmss(sec): return f"{sec//60} min {sec%60:02d}" if sec%60 else f"{sec//60} min"

def ef(dist,dur,strides=False,opt=False,recovery=False,desc=None):
    if strides:
        d=dict(titre="Footing facile + lignes droites",type="EF + technique",sport="Course à pied",opt=opt,accent=GREEN,fill=34,
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
        d=dict(titre="Footing de récupération",type="Récupération active",sport="Course à pied",opt=opt,accent=GREEN,fill=22,
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
        d=dict(titre="Footing facile",type="EF aérobie",sport="Course à pied",opt=opt,accent=GREEN,fill=28,
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
    return dict(titre=f"{niv} — {reps}\u00d7{minutes} min",type="Seuil (puissance aérobie)",sport="Course à pied",opt=False,accent=VIOLET,fill=fill,
      sous=desc,metriques={"Distance":f"~{dist} km","Durée":f"~{dur} min","Allure":pace,"FC":fc,"RPE":"7-8","Type":niv},
      objectif=f"Travail au <strong>{niv}</strong> ({nd}) : tenir une allure soutenue mais contrôlée. Le seuil 30 affûte le haut, le seuil 60 construit l'endurance de seuil — les deux nourrissent ta capacité à tenir l'allure marathon longtemps.",
      struct=[{"nom":"Échauffement","txt":"20 min facile + 3 lignes droites."},
              {"nom":"Corps","txt":f"{reps} \u00d7 {minutes} min à {niv.lower()} ({pace}), récup {recup} min footing lent entre les blocs. {nd[0].upper()+nd[1:]}."},
              {"nom":"Retour","txt":"10 min souple."}],
      benefices="Élévation du seuil lactique, capacité à tenir l'allure longtemps — la base de ta résistance sur marathon.",
      vigilance="Pars contrôlé : le dernier bloc à la même allure que le premier. Allures à recaler après le test 10 km (S31).",
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
    vig="Pars volontairement lent : la longue se court sur la retenue. Fatigue marquée → réduis la distance mais ne supprime pas la séance."
    if heat: vig+=" Été : par forte chaleur, cours à la FC/sensation (pas au chrono) et renforce l'hydratation/électrolytes."
    return dict(titre=("Sortie longue + allure marathon" if mp_km else "Sortie longue endurance"),type=("Sortie longue spécifique" if mp_km else "Sortie longue"),sport="Course à pied",opt=False,accent=(BLUE if mp_km else GREEN),fill=fill,
      sous=desc or ("La séance clé — endurance + carburant."+(f" Finish {mp_km} km AM." if mp_km else "")),
      metriques={"Distance":f"~{dist} km tout compris","Durée":f"~{dur} min","Allure":(P_EF+" + AM" if mp_km else P_EF),"FC":F_EF,"RPE":("5-6" if mp_km else "4-5"),"Type":"Longue"},
      objectif=(("Endurance + spécificité : "+f"{mp_km} km à allure marathon en fin de longue" if mp_km else "Reconstruire/entretenir l'endurance fondamentale")+", et roder le carburant. <strong>Séance clé, non optionnelle.</strong>"),
      struct=[{"nom":"Échauffement","txt":"15 min très souples."},
              {"nom":"Corps","txt":(f"{dist} km en EF régulière, puis {mp_km} km à allure marathon ({P_AM}) pour finir sur fond de fatigue." if mp_km else f"{dist} km à allure facile régulière, plat à légèrement vallonné.")+" Nutrition : boire toutes les 15-20 min, électrolytes dès le départ, 1 gel/30-40 min au-delà d'1h30."},
              {"nom":"Retour","txt":"Marche 5 min + étirements, recharge hydrique/électrolytes."}],
      benefices="Endurance, oxydation des graisses, résistance à la fatigue"+(", tenue de l'allure cible sur fin de course" if mp_km else "")+" — et rodage du carburant.",
      vigilance=vig,
      legende=[{"c":GREEN,"l":"Facile / EF"}]+([{"c":BLUE,"l":"Allure marathon"}] if (mp_km or fuel) else []),
      coach=[{"titre":"Le carburant, ta priorité","texte":"La longue est ton labo nutrition. Note ce que tu absorbes et ton ressenti — on cale la stratégie marathon dessus."}],
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
W(25,[ef(10,65,strides=True), ef(9,55), mp(12,72,1,6,"Premier contact sérieux avec l'allure marathon — 6 km à tenir proprement.",cool_min=25), longrun(18,110,heat=True,desc="Reconstruire l'endurance + roder le carburant."), renfo(opt=True)])
# Allègement + prépa Déraille (course plaisir B, 5 juillet)
W(26,[ef(11,66,strides=True), ef(9,55), deraille_prep(15,90), renfo(opt=True)])
# Semaine de course — Trail Déraille au Lac des Sapins (dim. 5 juillet)
W(27,[ef(8,48,strides=True), ef(7,45,recovery=True), ef(6,38,recovery=True), race("deraille")])
W(28,[ef(12,72), thresh(12,68,2,8,"Découverte du seuil : 2 blocs courts."), ef(10,60,strides=True), longrun(22,135,mp_km=5,heat=True), renfo(opt=False)])
W(29,[ef(10,60), thresh(10,58,2,6,"Seuil allégé, semaine de récup."), ef(10,60,strides=True), longrun(16,95,heat=True,desc="Longue raccourcie, on assimile."), renfo(opt=True)])
W(30,[ef(12,72), thresh(13,75,3,8,"Seuil consolidé, 3 blocs."), pyr_hills(45), longrun(24,145,mp_km=6,heat=True), renfo(opt=False)])
W(31,[ef(11,66,strides=True), benchmark(), ef(10,60), longrun(20,120,heat=True,desc="Longue facile après le test."), renfo(opt=False)])
# Seuil & pré-USA
W(32,[ef(12,72), thresh(14,80,2,15,"Seuil long : 2×15 min, le vrai travail.",recup=4), ef(12,72,strides=True), longrun(26,155,mp_km=8,heat=True), renfo(opt=False), mobilite()])
W(33,[ef(11,66), thresh(12,70,2,10,"Seuil allégé avant le pic."), ef(10,60,strides=True), longrun(18,108,heat=True,desc="Récup avant le gros bloc."), renfo(opt=True)])
W(34,[ef(12,72), thresh(14,82,3,12,"Pic seuil pré-voyage.",recup=3), ef(12,72), longrun(28,170,mp_km=12,heat=True,desc="Longue 28 km dont 12 à allure marathon — c'est le GATE de la séance reine : si elle passe bien, on validera 14 km AM en S42."), renfo(opt=False), mobilite()])
W(35,[ef(12,72,strides=True), thresh(11,66,2,8,"Seuil court, on lève le pied."), ef(10,60), longrun(18,108,heat=True,desc="On prépare le corps au déload du voyage."), renfo(opt=True)])
# USA
W(36,[ef(10,60,recovery=True), ef(10,62), ef(10,62), trailsess(12,90,"randos & sentiers US","Temps de pied en montagne, à l'effort libre.")])
W(37,[ef(9,55,recovery=True), ef(9,55), trailsess(12,90,"randos & sentiers US","Profiter du relief des parcs, sans structure."), ef(8,50)])
W(38,[ef(9,55,recovery=True), ef(9,55), ef(10,62), trailsess(10,75,"randos & sentiers US","Entretien aérobie, zéro pression.")])
W(39,[ef(8,50,recovery=True), ef(10,62), ef(11,66,strides=True), longrun(16,100,fuel=False,desc="Retour : remise en route, on réveille la longue.")])
# Bloc marathon (re-construction + 1 grosse qualité/sem + longues plafonnées)
W(40,[ef(11,66), thresh(13,72,2,10,"Relance DOUCE du seuil après le voyage.",recup=3), ef(10,60,strides=True), longrun(20,120,mp_km=6,desc="Longue de re-construction, 20 km dont 6 AM."), renfo(opt=False)])
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
    MAGIC="ASICS Magic Speed 4";NOVA="ASICS Novablast 5";CLIF="HOKA Clifton 10";GEL="ASICS Gel Pulse 16";CASC="Brooks Cascadia 19"
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
        _f={1:"fit/S25-1-footing-lignes.fit",2:"fit/S25-2-footing-facile.fit",3:"fit/S25-3-allure-marathon.fit",4:"fit/S25-4-sortie-longue.fit"}
        for s in arr: s["fit"]=_f.get(s["num"])
        arr[0]["realise"]={"statut":"fait","km":10.25,"temps":"1h00","allure":"5:51/km","fc_moy":143,"fc_max":173,"rpe_ressenti":3,
          "commentaire":"Footing facile 10 km en 1h + 6 lignes droites de 100 m (km 9-10 plus rapides).",
          "pr":0,"ach":2,"pr_detail":["Segment Pont de la Guillotière","Segment Antonin Poncet & Pont de la Gui"],
          "revue":"<strong>Reprise sans faute.</strong> Les 8 premiers km tenus à 6:02/km de moyenne, FC moyenne à 142 (le plafond EF de 144 respecté) : exactement la discipline qu'on visait après La Circaète. FC qui monte doucement de 133 à 144 sur l'heure — du cardiac drift normal, aucune dérive parasite. <strong>Tu n'as pas couru en zone grise : c'est ça, la vraie victoire de la séance.</strong> Les 6 lignes droites ressortent sur les km 9-10 (FC jusqu'à 173, ~90 % FCmax, 2 records de segment au passage), foulée restée propre (cadence 171, pas de sur-foulée). Avec ~30 s de récup entre chaque ligne, l'exécution était bonne : la FC moyenne élevée sur ces km (~160) n'est pas un excès, juste l'<em>inertie cardiaque</em> normale entre des efforts courts et rapprochés. Si un jour tu veux les rendre encore plus purement neuromusculaires, tu peux étirer la récup à 45-60 s — c'est une option, pas une correction. <strong>Dos et jambes ont parfaitement encaissé : reprise modèle.</strong> 👏"}
        arr[1]["realise"]={"statut":"fait","km":10.14,"temps":"1h00","allure":"5:56/km","fc_moy":140,"fc_max":167,"rpe_ressenti":3,
          "commentaire":"Footing facile 10,1 km en 1h pile, allure régulière ~5:56/km le long des berges. Effort relatif 58 (plus bas que S25-1) — un vrai easy.",
          "pr":0,"ach":0,"pr_detail":[],
          "revue":"<strong>Deuxième easy, deuxième sans-faute.</strong> FC moyenne à 140 sur l'heure (plafond EF de 144 respecté, encore mieux que les 143 de mardi), allure métronomique entre 5:48 et 6:06/km : tu es exactement où tu dois être. Le détail qui me plaît, c'est la stabilité — la FC démarre à 132 sur les 2 premiers km, touche 144 au km 3, puis se cale autour de 138-142 jusqu'au bout sans jamais déraper. <strong>Aucune dérive cardiaque parasite sur 1 h : le moteur aérobie encaisse proprement.</strong> Le seul pic à 167 est sur les 142 derniers mètres (petite bosse à 3 %), c'est anecdotique et ça ne compte pas comme un excès. Cadence à 173, régulière et propre, foulée économique. L'effort relatif à 58 contre 69 mardi confirme que celui-ci était plus facile — la fraîcheur revient. <strong>Deux footings d'affilée tenus dans la zone juste : la discipline anti-zone-grise qui te plombait est en train de devenir un automatisme.</strong> C'est précisément le socle qu'il faut poser avant d'attaquer l'allure marathon en séance 3. Rien à corriger — continue comme ça. 👏"}
    elif 26<=n<=53:
        _FT={"Seuil (puissance aérobie)":"seuil","Spécifique marathon":"allure-marathon",
             "Sortie longue":"sortie-longue","Sortie longue spécifique":"sortie-longue",
             "Spécifique trail (vallonné)":"deraille",
             "Côtes — force / économie":"cotes","Test / recalibrage":"test-10km"}
        for s in arr:
            _sl=_FT.get(s["type"])
            if _sl: s["fit"]=f"fit/S{n}-{s['num']}-{_sl}.fit"
    SEANCES_BY_WEEK[str(n)]=arr

META=[
(24,'reprise','Récupération',28,'Légère','—',"Absorber La Circaète : repos actif, footings très faciles, mobilité du dos."),
(25,'reprise','Reprise & déblocage',52,'Modérée','≈ 85 % facile · 15 % qualité légère',"Relancer une structure : ré-ancrer le vrai easy, vivacité, premier contact allure marathon, longue + carburant."),
(26,'general','Allègement + prépa Déraille',35,'Allégée','≈ 78 % facile · 22 % spécifique',"Volume réduit, une séance spécifique vallonnée avec répétition nutrition : on prépare la Déraille sans entamer la reprise."),
(27,'general','Semaine course — Déraille',45,'Course','—',"Affûtage court (3 footings) + Trail Déraille au Lac des Sapins le 5 juillet. Objectif C, plaisir & test nutrition. (21 km allégés + 24 km course.)"),
(28,'general','Seuil découverte',70,'Soutenue','≈ 80 % facile · 20 % qualité',"Premier vrai seuil, longue qui s'allonge avec bloc AM."),
(29,'general','Allègement',56,'Légère','≈ 85 % facile · 15 % qualité',"Récupération : on assimile, le dos respire."),
(30,'general','Seuil + pyramide',72,'Soutenue','≈ 80 % facile · 20 % qualité',"Seuil 3 blocs, rappel pyramide, longue 24 km dont 6 AM."),
(31,'general','Test 10 km + recalibrage',70,'Soutenue','≈ 82 % facile · test',"Benchmark 10 km pour recaler les allures avant le bloc spécifique."),
(32,'seuil','Seuil long',78,'Élevée','≈ 80 % facile · 20 % qualité',"Seuil long (2×15 min) + longue 26 km dont 8 AM. 2ᵉ mobilité ajoutée."),
(33,'seuil','Allègement',64,'Légère','≈ 85 % facile · 15 % qualité',"Récupération avant le pic pré-USA."),
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
(44,'affutage','Affûtage 1',54,'Modérée','≈ 80 % facile · 20 % qualité',"Décharge nette + intensité courte maintenue (Bosquet) : on évacue la fatigue."),
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

PHASES=[
 {"id":'reprise',"nom":'Reprise',"c":GREEN,"sem":'S24 – S25',"role":"Digérer La Circaète puis relancer en douceur en corrigeant la zone grise."},
 {"id":'general',"nom":'Développement général & aérobie',"c":BLUE,"sem":'S26 – S31',"role":"Volume, polarisation, côtes en pyramide (force/économie), seuil, et benchmark 10 km pour recaler les allures."},
 {"id":'seuil',"nom":'Seuil & spécifique (pré-USA)',"c":VIOLET,"sem":'S32 – S35',"role":"Front-loader le seuil et l'allure marathon avant le voyage."},
 {"id":'usa',"nom":'Maintien — Road trip USA',"c":'#94a3b8',"sem":'S36 – S39',"role":"Deload bien placé : courir quand possible, randos = temps de pied."},
 {"id":'marathon',"nom":'Bloc spécifique marathon',"c":ORANGE,"sem":'S40 – S43',"role":"Ré-entrée progressive, une grosse séance spécifique par semaine, pic à 88 km avec la séance reine."},
 {"id":'affutage',"nom":'Affûtage marathon',"c":YELLOW,"sem":'S44 – S45',"role":"Décharge progressive (Bosquet) : volume en baisse, intensité courte maintenue, fraîcheur pour le 8 nov."},
 {"id":'transition',"nom":'Transition & bascule trail',"c":TEAL,"sem":'S46 – S47',"role":"Récup marathon progressive puis réveil des jambes de trail."},
 {"id":'saintexpress',"nom":'SaintExpress 45 km',"c":RED,"sem":'S48',"role":"Objectif B sur les acquis : nocturne, hivernal, au plaisir."},
 {"id":'regen',"nom":'Régénération fin de saison',"c":'#94a3b8',"sem":'S49 – S53',"role":"Décompression, course libre, entretien de la base, cap vers 2027."},
]
COUL={p["id"]:p["c"] for p in PHASES}
GEAR=[
  {"marque":"HOKA","modele":"Clifton 10","km":1093},
  {"marque":"ASICS","modele":"Novablast 5","km":486},
  {"marque":"ASICS","modele":"Gel Pulse 16","km":225},
  {"marque":"Brooks","modele":"Cascadia 19","km":196},
  {"marque":"ASICS","modele":"Magic Speed 4","km":40},
]
RACES=[{"nom":"Trail Déraille — Lac des Sapins","date":"2026-07-05","dossier":"deraille"},{"nom":"Marathon de Nice","date":"2026-11-08","dossier":"nice"},{"nom":"SaintExpress","date":"2026-11-28","dossier":"saintexpress"}]

# ===== DOSSIERS DE COURSE (modale au clic sur le badge) =====
DOSSIERS={
 "nice":{
  "nom":"Marathon des Alpes-Maritimes Nice-Cannes",
  "soustitre":"Promenade des Anglais, Nice → Boulevard de la Croisette, Cannes",
  "date":"Dimanche 8 novembre 2026",
  "depart":"Départ 8 h 00 · Promenade des Anglais (Nice) · Sas 3h45 disponible",
  "format":"42,195 km · Point-à-point · Label FFA & World Athletics · ~15 000 coureurs",
  "accent":"#f97316",
  "stats":[["42,195","km"],["+70","D+ (m)"],["35","alt. max (m)"],["3 h 45","objectif"],["5:20/km","allure cible"]],
  "intro":"Le 2ᵉ plus grand marathon de France après Paris. <strong>42,195 km quasi plats le long de la Méditerranée</strong>, de la Promenade des Anglais à la Croisette — vue mer permanente, palmiers, soleil de novembre. Route intégralement bitumée, D+ de seulement ~70 m : pas de dénivelé à gérer, pas de marche prévue. Tout l'enjeu est <strong>la gestion d'allure sur la durée</strong>. C'est ton Objectif A de la saison.",
  "phrase":"3 h 45, soit <strong>5 min 20 / km</strong> du départ à l'arrivée. Le lièvre 3h45 est disponible — accroche-toi à lui jusqu'au km 30, puis gère selon tes jambes. Le seul piège : partir trop vite dans l'euphorie du départ.",
  "profil":"Profil réel GPX officiel (marathon06.com). Course quasi plate au niveau de la mer. Deux légères ondulations : une petite bosse vers le km 15-18 (Cagnes / Villeneuve-Loubet, ~12 m) et <strong>la seule vraie bosse du parcours vers le km 25-28 (Antibes, ~35 m)</strong>. Cette montée est modeste mais peut surprendre à mi-course si tu n'es pas calé à l'effort. Retour au niveau de la mer à partir de Juan-les-Pins.",
  "profil_dist":42.195,
  "profil_pts":[11,8,9,10,14,8,9,9,9,5,6,11,11,9,5,4,4,6,7,7,3,2,5,5,4,5,4,6,12,12,10,7,4,10,7,10,11,6,4,5,3,4,3,3,4,6,3,5,5,4,3,8,15,13,7,12,6,6,6,7,7,9,9,16,7,10,7,28,33,28,19,11,6,5,4,4,5,5,5,12,8,8,10,5,2,3,4,5,3,13,16,15,22,17,19,15,14,6,5,5,8,7,3,7,4,10,7,6,4],
  "segments":[
    {"t":"1 · Nice — Saint-Laurent","km":"km 0 → 8","faire":"Départ Promenade des Anglais. Jambes fraîches, foule, adrénaline : <strong>le piège du marathon</strong>. Cible : 5:25/km au moins sur les 5 premiers km. Le lièvre 3h45 sera là — laisse-le légèrement partir devant si tu pars trop vite."},
    {"t":"2 · Cagnes — Villeneuve-Loubet","km":"km 8 → 18","faire":"La Marina Baie des Anges vers le km 15. Légère ondulation, rien de méchant. <strong>Mi-course approche : gère à l'effort</strong>, pas au chrono. Si tu passes la demi à moins de 1h52, tu risques de payer après le km 30."},
    {"t":"3 · Antibes — Juan-les-Pins","km":"km 20 → 30","faire":"La seule vraie bosse (km 25-28, ~35 m) — prends-la sans accélérer. Autour du km 20-21 tu franchis la demi-distance : moment de recalibrer. <strong>Le seuil critique du « mur » est entre le km 30 et 35</strong> — si tu arrives là fatigué, c'est que tu es parti trop vite."},
    {"t":"4 · Golfe-Juan → Cannes","km":"km 30 → 42","faire":"C'est ici que la course se joue. Si tu as géré avant : tiens le 5:20/km et double les gens qui ont cramé. Si tu souffres : raccourcis légèrement la foulée, cadence haute, gel, et accroche-toi. La Croisette arrive — les marches rouges du Festival, c'est l'arrivée."}],
  "plan":[
    {"n":"1","tag":"CONSERVATEUR","c":"#f97316","titre":"Sortie de Nice — freiner l'ego","txt":"8h00 sur la Promenade des Anglais avec 15 000 coureurs. Les km 1-5 sont les plus dangereux du marathon : jambes fraîches, euphorie, public, faux-plats. Cible <strong>5:25 / km</strong> minimum sur les 5 premiers. Si tu passes le km 5 sous 26:30, tu es trop rapide.","fuel":"Gel dès 40 min de course (km 8 environ) sans attendre la faim. Ravito km 5 : eau."},
    {"n":"2","tag":"GÉRER","c":"#ea580c","titre":"La longue ligne droite côtière","txt":"Km 8 à 20 : tenir le 5:20/km sans forcer. La côte Méditerranée est magnifique, ça peut aller vite — surveille ton allure. Passage de la demi vers 1h52 à 1h53 : si tu es en avance, lève le pied. Marathon = compétition contre soi-même, pas contre les coureurs autour.","fuel":"Gel km 16 environ. Ravitos km 10, 15, 20 : eau + boisson sucrée si dispo. Commence l'électrolyte."},
    {"n":"3","tag":"VIGILANCE","c":"#dc2626","titre":"Antibes & le mur (km 25-35)","txt":"<strong>La section décisive.</strong> La bosse d'Antibes (km 25-28, max 35 m) peut faire accélérer le cœur si tu n'es pas attentif — régule. Puis km 30 : c'est là que les glucides s'épuisent et que les jambes commencent à parler. Ton mental et ton carburant doivent tenir. Cadence haute, foulée courte.","fuel":"Gel km 24 et gel km 32 — <strong>celui du km 32 est le plus important du marathon</strong>. Le caféiné ici si tu en as un."},
    {"n":"4","tag":"POUSSER","c":"#f97316","titre":"La Croisette — vider le réservoir","txt":"Km 35-42 : si tu as bien géré, tu doubles du monde sur les derniers km. La Croisette de Cannes approche avec les marches rouges du Festival et le public. Laisse parler les émotions, accélère si tes jambes suivent. <strong>3h45 c'est à ta portée : ne lâche rien.</strong>","fuel":"Dernier gel km 37-38 si tu en as encore. Sinon eau seule pour les 5 derniers km."}],
  "nutrition":{
   "avant":"<strong>J-3 à J-1 :</strong> ↑ glucides légèrement (+ 20-30 %), 1 comprimé TA dans 500 ml d'eau/jour. <strong>Veille :</strong> dîner pâtes/riz, coucher tôt. <strong>Matin de course</strong> (réveil ~5h, départ 8h) : 2 comprimés TA dans 500 ml d'eau dès le lever — priorité absolue. Petit-dej 3h avant : flocons d'avoine + banane + miel + café. <strong>15-20 min avant le départ :</strong> 1 gel non-caféiné (amorce le moteur glycolytique).",
   "intro":"Marathon = moteur glycolytique sur 3h45. L'apport glucidique doit être continu et anticipé — sans gel régulier, le mur du km 30 est inévitable. Les <strong>comprimés TA</strong> (350 mg Na/cpr) couvrent les électrolytes en pré-course, des <strong>gels non-caféinés</strong> assurent le débit de base (3 à acheter, ex. Aptonia Decathlon ~1 €/pièce), les <strong>Nduranz caféinés</strong> interviennent uniquement sur les deux moments critiques. <strong>Pas de BCAA dans ce plan.</strong>",
   "items":[
     ["TA Energy Electrolytes Tropical","350 mg Na · 80 mg K · 52 mg Mg / cpr","PRÉ-COURSE — 2 cpr dans 500 ml dès le réveil. 1 cpr en poche → à dissoudre dans un gobelet ravito km 20-25."],
     ["Gel non-caféiné (Aptonia ou équiv.)","~25-45 g glucides · 0 mg caféine","BASE — km 8, km 16, km 24 : débit régulier anti-mur (+ 1 avant le départ)"],
     ["Nduranz NRGY 45 — Cherry","45 g glucides · 65 mg caféine","ARME 1 — km 32 : le gel le plus important du marathon (anti-mur, pic caféine en 35 min)"],
     ["Nduranz NRGY 45 — Coffee Amarena","45 g glucides · 130 mg caféine","ARME 2 — km 38 : finale Croisette, vide le réservoir"]],
   "note":"Cible : <strong>50-60 g glucides/h</strong>. La boisson STC Nutrition des ravitos (~30-40 g glucides/500 ml) complète les gels — bois systématiquement à chaque table. Caféine total en course : 195 mg — raisonnable sur 3h45. Ne jamais forcer un gel si l'estomac est tendu : eau seule et reprendre au prochain ravito.",
   "apres":"<strong>Dans les 15 min :</strong> 1 comprimé TA dans 500 ml d'eau (priorité). <strong>Dans l'heure :</strong> repas protéiné complet (protéines + glucides). <strong>Le soir :</strong> vigilance crampes nocturnes → 1 dernier comprimé TA dans l'eau au coucher. Le dossard TER est valable toute la journée pour rentrer à Nice depuis Cannes."},
  "hydra":"<strong>Électrolytes pré-course :</strong> 2 comprimés TA dans 500 ml dès le réveil (5h). La course est en novembre (~12-16°C) : la soif est modérée mais les ravitos tous les 5 km sont obligatoires — ne saute aucune table. Tu peux glisser 1 comprimé TA dans ta poche et le dissoudre dans un gobelet d'eau à un ravito (km 20-25). Post-course : 1 comprimé TA dans 500 ml immédiatement à l'arrivée.",
  "zones":[
   ["Zone marathon","134 – 152","L'allure 3h45 doit tenir dans cette plage. Si FC &gt; 155 dans les 15 premiers km : tu pars trop vite."],
   ["Dérive normale","152 – 162","Km 25-35 : la FC monte naturellement même à allure constante. Normal — maintiens l'effort, pas la FC."],
   ["Danger","&gt; 162","Si FC &gt; 162 avant le km 20 : freine. Au-delà du km 35 avec mur enclenché : encaisse et maintiens."]],
  "terrain":"Route bitumée 100%, large et sécurisée, traversant 7 communes. <strong>Chaussures :</strong> tes chaussures de route avec amorti — les Clifton 10 sont parfaites pour 42 km sur route. Oublie les Cascadia : route uniquement. <strong>Tenue :</strong> novembre en Côte d'Azur, départ 8h00 → 10-14°C. Bras longs au départ (ou brassière + bras jetables), tu enlèveras au km 5-10. <strong>Vent :</strong> côtier donc potentiellement présent. Si vent de face, colle à un groupe.",
  "pratique":[
   ["🚉 Logistique retour","Ton dossard = billet TER Nice-Cannes valable le jour J. Prévois où tu récupères tes affaires (service transfert de sacs disponible)."],
   ["👟 Lièvre 3h45","Cherche le groupe 3h45 dans ton sas. Reste avec eux jusqu'au km 30 au moins — c'est ton GPS vivant."],
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
  "sources":"Profil GPX officiel MAM 2026 (marathon06.com/2026/dl/MAM2026_parcours.gpx). D+ officiel ~70 m. Infos ravitaillements et lièvres : marathon06.com, finishers.com. Zones FC basées sur FCmax ~192 et objectif 3h45 (≈74 % FCmax en allure marathon). Météo : moyennes historiques Nice novembre (Météo-France)."},
 "saintexpress":{
  "nom":"SaintExpress 45 km",
  "soustitre":"Sainte-Catherine (757 m) → Lyon · Halle Tony Garnier · Monts du Lyonnais",
  "date":"Samedi 28 novembre 2026 — départ 23 h 00",
  "depart":"Départ nocturne 23 h 00 · Sainte-Catherine (757 m) · 4 000 coureurs",
  "format":"45 km · 900 m D+ · 1 400 m D− · SaintéLyon depuis 2010 · maratrail nocturne",
  "accent":"#8b5cf6",
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
    {"n":"1","tag":"TERRAIN INCONNU","c":"#8b5cf6","titre":"km 0-27 — découverte et prudence","txt":"Les 27 premiers km sont du terrain inédit pour toi. Pas de repère, pas d'anticipation possible — tu gères à l'effort, à la sensation et à la frontale. <strong>Plus conservateur que d'habitude</strong>, surtout sur les descentes techniques de nuit. L'objectif est d'arriver à Soucieu avec des jambes.","fuel":"Gel non-caféiné à 20 min avant départ. Flasques TA. Gel km 7 et km 14 (ravito Saint-Genou)."},
    {"n":"2","tag":"TERRAIN CONNU","c":"#16a34a","titre":"km 27-45 — tu rentres à la maison","txt":"À Soucieu, tu bascules sur ton terrain de relais. <strong>Tu sais ce qui t'attend</strong> : le rythme, les aqueducs, les faubourgs. C'est un avantage mental énorme à 2h du matin. Pas d'accélération brutale, mais tu peux relâcher l'hyper-vigilance et gérer à l'instinct.","fuel":"Nduranz Cherry (65 mg) au départ de Soucieu (~km 27). Coffee Amarena (130 mg) avant les aqueducs (~km 38)."},
    {"n":"3","tag":"QUADS FIRST","c":"#dc2626","titre":"Préserver les quads — 1400 m de D−","txt":"Course de descente avant tout. <strong>1400 m de descente sur terrain technique de nuit</strong> : foulée courte, appuis rapides, regard 3-4 m devant la frontale. La différence entre bien et mal gérer les descentes, c'est 1h sur le chrono final.","fuel":"Hydratation régulière. Ne jamais attendre la soif dans le froid."},
    {"n":"4","tag":"VIGILANCE NUIT","c":"#ea580c","titre":"Creux circadien 1h-3h du matin","txt":"Entre 1h et 3h du matin, même toi qui as déjà couru de nuit, la vigilance baisse. <strong>C'est là que les chutes arrivent.</strong> La caféine Cherry à Soucieu (~km 27, vers 1h30-2h du matin selon ton allure) est calculée pour couvrir exactement ce creux.","fuel":"Nduranz Cherry (65 mg) à Soucieu → pic en 30-35 min = plein creux nocturne couvert."}],
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
  "accent":"#0d9488",
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
    {"n":"2","tag":"FAIRE LE PLEIN","c":"#ea580c","titre":"Plateau — manger &amp; rouler","txt":"Replat ondulé d'altitude (km 8-12) avec un creux vers le km 11. Relâche, foulée courte cadence haute, profite de cette accalmie pour t'alimenter avant la remontée. Vitesse gratuite, pas forcée.","fuel":"1 gel ici, et recharge l'eau à fond au ravito du plateau."},
    {"n":"3","tag":"VIGILANCE","c":"#dc2626","titre":"Crux — survivre, marcher, manger","txt":"Remontée au sommet 897 m (km 12-16) sur jambes entamées. C'est ici que les gens explosent — à cause de la Montée 1 surcuite. Marche assumée, petits pas, on survit, on ne brille pas.","fuel":"Gel caféiné Nduranz juste avant : la caféine culmine en plein crux."},
    {"n":"4","tag":"POUSSER","c":"#0d9488","titre":"Descente finale — lâcher les chevaux","txt":"Longue descente roulante (km 16-22, −415 m). Contrôlé en haut le temps de te remettre en jambes, puis plein gaz sur le roulant et le retour au lac. Si tu as été discipliné avant, tu doubles du monde et tu finis en plaisir.","fuel":"Dernier gel si besoin pour la relance."}],
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
  "sources":"Données : trace GPX officielle du 24 km (tracedetrail.fr/trace/327465) — 24,06 km, sommet 897 m, départ/arrivée 447 m. D+ officiel 901 m (le GPS lit souvent ~1040 m, normal). Trail Tour Beaujolais, organisateur Y’A.C.A. Courir. Zones FC basées sur tes repères (FCmax ~192, bascule marche ~160) — ne remplacent pas un avis médical."}
}
print("Semaines:",len(SEANCES_BY_WEEK)+1,"| Séances:",sum(len(v) for v in SEANCES_BY_WEEK.values()))
import json as _j
_hist=_j.load(open('/tmp/hist.json'))
MONTHLY=[
  {"m":"Jan","km":234,"elev":1579,"sorties":21,"re":502},
  {"m":"Fév","km":227,"elev":1674,"sorties":21,"re":2229},
  {"m":"Mar","km":342,"elev":2962,"sorties":25,"re":2978},
  {"m":"Avr","km":283,"elev":2254,"sorties":23,"re":2265},
  {"m":"Mai","km":241,"elev":7856,"sorties":19,"re":2139},
  {"m":"Juin","km":82,"elev":2012,"sorties":5,"re":1112},
]
SAISON2026={"km":1361,"elev":16222,"sorties":108,"mois":6,"note":"Run + Trail uniquement, aligné Strava"}
ACWR_DATA={"charge7j":951,"charge28j":2424,"acwr":1.57,"interpretation":"Encore élevé car la Circaète (696 RE) est dans la fenêtre 7 jours — elle en sort ce week-end et le ratio va redescendre naturellement. Les 3 footings de récup (164+47+44) sont, eux, parfaitement légers. Rien d'inquiétant : c'est la digestion normale d'une course."}
RECORDS_PERF=[
  {"dist":"5 km","record":"22:52","record_sub":"meilleur effort Strava","actuel":"4:35/km","actuel_sub":"meilleur effort 2026","temps_rec":"22:52","temps_act":"~22:52"},
  {"dist":"10 km","record":"46:14","record_sub":"meilleur effort Strava","actuel":"4:37/km","actuel_sub":"meilleur effort 2026","temps_rec":"46:14","temps_act":"~46:14"},
  {"dist":"Semi 21,1","record":"1h52:39","record_sub":"meilleur effort Strava","actuel":"5:20/km","actuel_sub":"projeté depuis forme actuelle","temps_rec":"1h52:39","temps_act":"~1h50-1h52"},
]
ALLURES_COURSE=[{"d":"5 km","temps":"~22:35","allure":"4:31/km"},{"d":"10 km","temps":"~47:00","allure":"4:42/km"},{"d":"Semi 21,1 km","temps":"~1h44","allure":"4:55/km"},{"d":"30 km","temps":"~2h31","allure":"5:02/km"},{"d":"Marathon objectif","temps":"3h45","allure":"5:20/km"},{"d":"Marathon projeté","temps":"~3h38-3h42","allure":"~5:12-5:15/km"}]
ALLURES=[{"nom":"Seuil 30","val":"≈4:40/km","sub":"~30 min · proche 10 km"},{"nom":"Seuil 60","val":"≈4:55/km","sub":"~60 min · proche semi"},{"nom":"Allure marathon","val":"≈5:15/km","sub":"cible Nice 3h42"},{"nom":"Endurance facile","val":"5:50-6:25/km","sub":"le socle"},{"nom":"VMA courte","val":"≈4:15/km","sub":"plafond aérobie"}]
ZONES_FC=[{"z":"Z1","nom":"Récupération","bpm":"< 134","pct":"< 70%","col":"#86efac","allure":"≥ 6:45/km"},{"z":"Z2","nom":"Endurance fondamentale","bpm":"134-154","pct":"70-80%","col":"#22c55e","allure":"5:50-6:25/km"},{"z":"Z3","nom":"Tempo / marathon","bpm":"154-167","pct":"80-87%","col":"#eab308","allure":"5:05-5:30/km"},{"z":"Z4","nom":"Seuil","bpm":"167-177","pct":"87-92%","col":"#f97316","allure":"4:40-4:55/km"},{"z":"Z5","nom":"VO2 / VMA","bpm":"177-192","pct":"92-100%","col":"#ef4444","allure":"≤ 4:20/km"}]
PROFIL={"prenom":"Loïc","ville":"Lyon","cible_marathon":"3h45","marathon_projete":"~3h38-3h42","cible_semi":"~1h44","fcmax":192,"poids":84}
PROJ={"base":13200,"goal":13500,"gmin":12600,"gmax":14400,
      "base_label":"forme de départ (réf. semi 1h52:39 + 16 km progressif du 9 juin à 4:50/km)",
      "mp_goal":"5:20/km"}
RECORDS=[{"label":"Semi 2022","val":"1h53","sub":"référence"},{"label":"Semi projeté","val":"~1h44","sub":"forme actuelle"},{"label":"Marathon visé","val":"3h42","sub":"objectif Nice"}]
VIGILANCE=[{"t":"Dos / lombaires","d":"surveiller en montée de charge"},{"t":"Carburant & électrolytes","d":"roder sur chaque longue"}]
S24_REALISE={"km":36.4,"runs":[
 {"iso":"2026-06-09","date":"Mar. 9","titre":"Footing 16 km — finish progressif","desc":"1h26 · 5:22/km · FC 153 (max 171) · charge 164 · Novablast 5","tag":"Endurance",
  "pr":2,"ach":11,"pr_detail":["Meilleur effort 2 km","Meilleur effort 1 mile"],
  "metriques":{"Distance":"16,0 km","Temps":"1h26","Allure":"5:22/km","FC moy / max":"153 / 171","D+":"54 m","Charge":"164","Cadence":"173 ppm","Calories":"1 205"},
  "chaussure":"ASICS Novablast 5",
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
  "chaussure":"ASICS Novablast 5",
  "splits":[[362,130],[351,133],[357,139],[359,135],[362,135],[349,136],[346,138],[335,140],[350,141],[343,141]],
  "lecture":"Allure régulière entre 5:35 et 6:02/km, FC qui glisse doucement de 130 à 141 — une dérive de +11 bpm sur une heure, parfaitement normale et même basse. Cadence stable à 172 ppm du début à la fin. Le 8e km à 5:35 est le seul moment où ça frémit.",
  "revue":"La séance compte moins que la décision : parti pour 13-15 km en se sentant très bien, tu as coupé à 10. <strong>S'arrêter parce que ça va bien, c'est la compétence n°1 du coureur qui dure</strong> — et celle qui te manquait mardi. Allure au bord intérieur de la cible (5:52 pour un plancher à 5:55), mais la FC à 137 valide l'effort. Trois jours, trois enseignements : mardi le piège, mercredi le modèle, vendredi la maturité."}],
 "revue":"<strong>Semaine de récup exemplaire : 3 sorties, 36,4 km, tout à plat, zéro intensité structurée.</strong> Mardi, le 16 km a fini en progressif jusqu'à 4:50/km (FC 164) — le réflexe zone grise dans sa version la plus sournoise : la séance qui dérive. Mercredi et vendredi : deux 10 km modèles (FC plate à 137). Le signal fort de la semaine, c'est vendredi : parti pour 13-15 km en se sentant très bien, tu as coupé à 10. <strong>S'arrêter parce qu'on se sent bien, c'est la maturité d'entraînement qu'on cherche.</strong> Zéro douleur dos, zéro douleur jambes : récupération en avance. Tu abordes la S25 dans des conditions idéales."}
REWINDS=[{"id":"S24","titre":"Ta semaine 24","sous":"Récupération post-Circaète · 8-14 juin","slides":[
 {"bg":"linear-gradient(160deg,#0f172a,#1e3a5f)","kicker":"REWIND · SEMAINE 24","big":"🎬","txt":"Ta semaine de récup en 30 secondes.<br>Tape pour avancer."},
 {"bg":"linear-gradient(160deg,#065f46,#022c22)","kicker":"LE VOLUME","big":"36,4 km","txt":"en 3 sorties — l'équivalent d'un Lyon → Vienne par les berges."},
 {"bg":"linear-gradient(160deg,#7c2d12,#1c0a00)","kicker":"TEMPS EN MOUVEMENT","big":"3h28","txt":"de course. Et ton cœur a battu ≈ 29 500 fois pendant tes runs."},
 {"bg":"linear-gradient(160deg,#581c87,#1e1b4b)","kicker":"LE CARBURANT","big":"2 727 kcal","txt":"brûlées en courant — environ 13 pains au chocolat. La boulangerie te dit merci."},
 {"bg":"linear-gradient(160deg,#1e3a8a,#0c1c3d)","kicker":"LE MÉTRONOME","big":"172 ppm","txt":"Ta cadence n'a pas bougé d'un poil sur les 3 sorties. Régularité de machine."},
 {"bg":"linear-gradient(160deg,#9a3412,#431407)","kicker":"LE KM LE PLUS RAPIDE","big":"4:47","txt":"le 13e km de mardi… en pleine semaine de récup. On en a parlé. 😏"},
 {"bg":"linear-gradient(160deg,#134e4a,#042f2e)","kicker":"LA LEÇON DE LA SEMAINE","big":"📏","txt":"<strong>Un footing a une allure de début ET une allure de fin — la même.</strong><br>Mercredi et vendredi l'ont prouvé : FC plate, récup parfaite."},
 {"bg":"linear-gradient(160deg,#3b0764,#0f172a)","kicker":"LA STAR DE LA SEMAINE","big":"👟","txt":"ASICS Novablast 5 — 2 sorties, 26 km. La Clifton vous salue (1 093 km au compteur)."},
 {"bg":"linear-gradient(160deg,#14532d,#052e16)","kicker":"VERDICT DU COACH","big":"A−","txt":"Récup exemplaire, un seul écart (mardi). Zéro douleur, fraîcheur au top. <strong>Tu es prêt.</strong>"},
 {"bg":"linear-gradient(160deg,#b45309,#451a03)","kicker":"LA SUITE","big":"S25","txt":"Reprise & déblocage — 52 km, retour des séances structurées.<br><strong>La machine démarre lundi. 🚀</strong>"}]}]
JOURNAL=[{"sem":"S24","theme":"Récupération post-Circaète","texte":S24_REALISE["revue"]}]
HEATMAP={"2026-01-03": 10.1, "2026-01-05": 11.2, "2026-01-06": 13.0, "2026-01-10": 21.6, "2026-01-12": 10.0, "2026-01-13": 11.3, "2026-01-14": 11.0, "2026-01-15": 14.1, "2026-01-16": 4.0, "2026-01-17": 11.1, "2026-01-20": 11.0, "2026-01-21": 21.1, "2026-01-22": 10.0, "2026-01-23": 3.5, "2026-01-26": 10.3, "2026-01-27": 11.5, "2026-01-28": 10.0, "2026-01-29": 18.2, "2026-01-31": 11.0, "2026-02-02": 14.0, "2026-02-03": 21.2, "2026-02-05": 8.9, "2026-02-06": 11.1, "2026-02-07": 12.1, "2026-02-08": 4.2, "2026-02-09": 20.4, "2026-02-10": 10.2, "2026-02-11": 11.8, "2026-02-16": 10.2, "2026-02-17": 20.0, "2026-02-18": 10.0, "2026-02-20": 10.6, "2026-02-21": 10.0, "2026-02-22": 11.8, "2026-02-23": 10.1, "2026-02-24": 2.5, "2026-02-25": 10.0, "2026-02-26": 12.5, "2026-02-27": 5.0, "2026-03-01": 4.4, "2026-03-02": 11.3, "2026-03-03": 18.0, "2026-03-04": 20.4, "2026-03-05": 17.1, "2026-03-07": 21.2, "2026-03-09": 17.0, "2026-03-10": 16.0, "2026-03-11": 10.0, "2026-03-12": 17.2, "2026-03-15": 4.2, "2026-03-16": 18.1, "2026-03-17": 13.0, "2026-03-18": 14.2, "2026-03-19": 21.2, "2026-03-20": 10.5, "2026-03-23": 13.0, "2026-03-24": 30.1, "2026-03-26": 15.0, "2026-03-27": 10.0, "2026-03-29": 15.0, "2026-03-30": 12.0, "2026-03-31": 13.0, "2026-04-01": 10.0, "2026-04-03": 14.3, "2026-04-04": 21.2, "2026-04-06": 18.6, "2026-04-07": 15.0, "2026-04-09": 24.7, "2026-04-10": 12.0, "2026-04-13": 18.0, "2026-04-14": 14.5, "2026-04-15": 15.1, "2026-04-16": 11.0, "2026-04-18": 30.1, "2026-04-19": 3.8, "2026-04-20": 13.0, "2026-04-21": 17.0, "2026-04-22": 16.0, "2026-04-24": 10.3, "2026-04-26": 4.0, "2026-04-27": 10.7, "2026-04-30": 3.6, "2026-05-01": 42.4, "2026-05-04": 13.0, "2026-05-06": 10.5, "2026-05-08": 11.1, "2026-05-09": 11.1, "2026-05-16": 8.4, "2026-05-18": 17.0, "2026-05-20": 10.0, "2026-05-21": 21.2, "2026-05-22": 22.2, "2026-05-27": 4.6, "2026-05-28": 4.0, "2026-05-29": 16.6, "2026-05-31": 10.0, "2026-06-01": 14.0, "2026-06-02": 12.0, "2026-06-06": 29.8, "2026-06-09": 16.0, "2026-06-10": 10.3, "2026-06-12": 10.0}
_j.dump({"PHASES":PHASES,"COUL":COUL,"SEMAINES":SEMAINES,"SBW":SEANCES_BY_WEEK,"GEAR":GEAR,"RACES":RACES,
  "PROFIL":PROFIL,"PROJ":PROJ,"RECORDS":RECORDS,"VIGILANCE":VIGILANCE,"S24R":S24_REALISE,
  "HIST":_hist["HIST"],"POLAR":_hist["POLAR"],"ALLURES":ALLURES,"ALLURES_COURSE":ALLURES_COURSE,"ZONES_FC":ZONES_FC,"MONTHLY":MONTHLY,"SAISON2026":SAISON2026,"ACWR_DATA":ACWR_DATA,"RECORDS_PERF":RECORDS_PERF,"JOURNAL":JOURNAL,"REWINDS":REWINDS,"MAJ":"16 juin 2026","HEATMAP":HEATMAP,"DOSSIERS":DOSSIERS},open('/tmp/data.json','w'),ensure_ascii=False)
print("OK")
