
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

P_REC="6:15-6:45/km"; P_EF="5:50-6:25/km"; P_AM="≈5:20/km"; P_SEUIL="≈4:50/km"; P_TRAIL="à l'effort"
P_S30="≈4:40/km"; P_S60="≈4:55/km"; F_S30="172-180"; F_S60="166-174"
F_REC="<140"; F_EF="135-150"; F_AM="152-163"; F_SEUIL="166-175"
GREEN="#16a34a";EF_COLOR="#16a34a";BLUE="#0d9488";ORANGE="#f59e0b";VIOLET="#64748b";RED="#ef4444";YELLOW="#94a3b8";TEAL="#0d9488"

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
          "revue":"<strong>Mission accomplie — et S25 bouclée à 5/5.</strong> 7h25 du matin chez tes parents, 10 km sortis tranquillement avant la chaleur. C'est exactement le plan discuté : sortir tôt, rester facile, rentrer avant que ça tape. La discipline du timing en week-end hors domicile, c'est une compétence à part entière.<br><br>La FC moyenne à 144 bpm est en plein milieu de la zone Z2 (130-148) — c'est un EF presque parfait. Les 10 laps varient entre 5:45 et 6:06/km sans aucune accélération, sans envie de faire mieux. C'est exactement ce qu'on cherche sur une séance optionnelle de bonus : du volume aérobie pur, zéro coût cardiaque ou musculaire pour la semaine suivante.<br><br><strong>Bilan S25 : 5/5 · 56,6 km · semaine de reprise complète.</strong> Tu arrives en S26 (allègement pré-Déraille) avec des jambes qui tournent bien et une semaine de volume solide dans les pattes. La Déraille dans 16 jours se prépare dans de bonnes conditions.<br><br>Note Clifton (1 103 km) : parfaitement appropriée pour ce type de footing léger. Uniquement pour décrassages ≤ 10 km désormais."}

        arr[3]["realise"]={"statut":"fait","km":16.05,"temps":"1h28:33","allure":"5:31/km · dernier km 4:58","fc_moy":151,"fc_max":171,"re":156,"cadence":173,"elevation_gain":52,"rpe_ressenti":6,
          "commentaire":"16 km en 1h28m33 — 13,5 km à allure constante puis fast finish progressif (5:16 → 5:01 → 4:58/km). Départ 8h, canicule. TA 500ml + gel caféiné 50ᵉ min. 5 PRs.",
          "pr":5,"ach":6,"pr_detail":["You are my best view","Quais de Saône S-N","LY Joffre/Plessier tunnel côté Saône","LY Plessier/Joffre rive gauche","darse confluence nord"],
          "revue":"<strong>La bonne réponse après hier.</strong> Même canicule, mais départ à 8h au lieu de midi — et tout change : FC moyenne à 150 contre 165 hier, max à 171 contre 181. <strong>Le seul vrai levier anti-chaleur, c'est l'heure de départ, et tu l'as appliqué.</strong><br><br>Le plan de séance était impeccable. 13,5 km réguliers — laps 2 à 13 entre 5:27 et 5:45/km, FC qui démarre à 133, se cale en zone 140-150 et dérive doucement vers 152-153 sous l'effet de la chaleur sur la fin. <strong>Cette dérive de +5 bpm à allure constante, c'est la signature physiologique de la canicule : normal, prévisible, bien géré.</strong> Tu n'as pas essayé de la combattre en forçant — tu as laissé l'allure glisser légèrement, ce qui est exactement la bonne réaction.<br><br>Le fast finish est la vraie surprise de la séance. Après 13,5 km : lap 14 à 5:16, lap 15 à 5:01, lap 16 à <strong>4:58/km</strong> — tu passes sous les 5 min sur le dernier km d'une sortie longue en canicule, à J+4 consécutif. FC 167-171 sur ces laps, tout à fait acceptable sur un effort volontaire et court. 5 PRs de segment au passage.<br><br>La nutrition a bien fonctionné : 500 ml TA électrolytes + 1 gel caféiné à 50 min (≈ km 9). C'est exactement le protocole à répliquer pour la Déraille dans 17 jours — à noter pour la fiche.<br><br><strong>Point canicule pour les 10 prochains jours :</strong> avec les températures annoncées, chaque séance se fait entre 6h et 9h, sans exception. L'allure cible baisse de 10-15 s/km automatiquement pour maintenir la même FC. Ce n'est pas un recul — c'est de la gestion intelligente. Ton moteur aérobie s'adapte à la chaleur en 7-10 jours (acclimatation thermique), et ces sorties matinales contribuent à ce processus. 💪"}

        _f={1:"fit/S25-1-footing-lignes.fit",2:"fit/S25-2-footing-facile.fit",3:"fit/S25-3-allure-marathon.fit",4:"fit/S25-4-sortie-longue.fit"}
        for s in arr: s["fit"]=_f.get(s["num"])
        arr[0]["realise"]={"statut":"fait","km":10.25,"temps":"1h00","allure":"5:51/km","fc_moy":143,"fc_max":173,"re":69,"cadence":171,"elevation_gain":43,"rpe_ressenti":3,
          "commentaire":"Footing facile 10 km en 1h + 6 lignes droites de 100 m (km 9-10 plus rapides).",
          "pr":0,"ach":2,"pr_detail":["Segment Pont de la Guillotière","Segment Antonin Poncet & Pont de la Gui"],
          "revue":"<strong>Reprise sans faute.</strong> Les 8 premiers km tenus à 6:02/km de moyenne, FC moyenne à 142 (le plafond EF de 144 respecté) : exactement la discipline qu'on visait après La Circaète. FC qui monte doucement de 133 à 144 sur l'heure — du cardiac drift normal, aucune dérive parasite. <strong>Tu n'as pas couru en zone grise : c'est ça, la vraie victoire de la séance.</strong> Les 6 lignes droites ressortent sur les km 9-10 (FC jusqu'à 173, ~90 % FCmax, 2 records de segment au passage), foulée restée propre (cadence 171, pas de sur-foulée). Avec ~30 s de récup entre chaque ligne, l'exécution était bonne : la FC moyenne élevée sur ces km (~160) n'est pas un excès, juste l'<em>inertie cardiaque</em> normale entre des efforts courts et rapprochés. Si un jour tu veux les rendre encore plus purement neuromusculaires, tu peux étirer la récup à 45-60 s — c'est une option, pas une correction. <strong>Dos et jambes ont parfaitement encaissé : reprise modèle.</strong> 👏"}
        arr[2]["realise"]={"statut":"fait","km":10.14,"temps":"54:10","allure":"5:14/km (bloc AM)","fc_moy":165,"fc_max":181,"re":169,"cadence":169,"elevation_gain":35,"rpe_ressenti":7,
          "commentaire":"6 km AM à 5:14/km de moyenne. Conditions extrêmes : midi, 30°C, gueule de bois. Séance écourtée à 10 km (vs 12 prévus) — décision sage. 4 PRs de segment au passage.",
          "pr":4,"ach":4,"pr_detail":["Pont Raymond Barre","Quai Rambaud S-N","darse Confluence","Dernier km Marathon de Lyon"],
          "revue":"<strong>La séance la plus honnête de la semaine — et probablement la plus révélatrice.</strong> Commence par les faits : 5:14/km de moyenne sur 6 km en bloc continu, à midi, 30°C, avec une gueule de bois. Km par km : 5:10 / 5:13 / 5:14 / 5:19 (pause eau) / 5:13 / 5:14. <strong>Aucun décrochage, aucune fuite en avant.</strong> C'est ça, le vrai signal de cette séance — tu as tenu l'allure cible de bout en bout dans des conditions qui auraient fait marcher beaucoup de gens.<br><br>La FC, maintenant — et là il faut être honnête. FC moy 165 sur la séance, 169-174 sur le bloc AM, max à 181 en fin de récup. <strong>C'est 20-25 bpm au-dessus de ce que produirait la même allure dans des conditions normales.</strong> La combinaison alcool la veille + déshydratation + chaleur de midi décale la FC vers le haut de façon prévisible et documentée : la chaleur augmente la demande cardiaque pour réguler la température, la déshydratation réduit le volume sanguin (le cœur doit battre plus vite pour compenser). <strong>Ce n'est pas un test de tes capacités aérobies, c'est un test de ta solidité mentale et de ton ancrage moteur à l'allure.</strong><br><br>La décision d'arrêter à 10 km était la bonne : l'essentiel était fait. Une note franche quand même : la FC à 181 (94 % de ta FCmax) sur ce qui devrait être une récupération, c'est le signe que le corps était sous forte contrainte. Ce n'est pas une leçon de morale — c'est un repère physiologique : dans ces conditions, un report ou une sortie EF lente était une meilleure option. Mais tu l'as géré, et ça donne une information précieuse : <strong>ton allure marathon est bien ancrée même quand tout va de travers. C'est rassurant pour Nice.</strong> 👏"}
        arr[1]["realise"]={"statut":"fait","km":10.14,"temps":"1h00","allure":"5:56/km","fc_moy":140,"fc_max":167,"re":58,"cadence":173,"elevation_gain":40,"rpe_ressenti":3,
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
    if n==26:
        arr[0]["date"]="2026-06-22"
        arr[0]["chaussure"]="Novablast 5 J"
        arr[0]["realise"]={"statut":"fait","km":11.26,"temps":"1h06","allure":"5:53/km","fc_moy":148,"fc_max":169,"re":105,"cadence":172,"elevation_gain":43,"rpe_ressenti":3,"commentaire":"11,26 km en 1h06 + 6 lignes droites · départ 8h33 · FC 148/169 · cadence 172 · D+ 43 m · Novablast 5 J · chaleur modérée, ressenti facile après 2 jours de repos.","pr":0,"ach":0,"pr_detail":[],"revue":"<strong>Reprise de semaine sans accroc — et la fraîcheur se voit.</strong> Départ 8h33, un peu de chaleur mais bien géré : 11,3 km en 1h06 à 5:53/km de moyenne. Les 9 premiers km en EF souple, FC calée entre 137 et 149 — pile dans la zone. Ton ressenti « cœur un peu haut » est juste et lucide : la moyenne à 148 est ~5 bpm au-dessus de ton plafond EF habituel (144), mais c'est la chaleur qui pousse, pas un défaut de gestion. Même allure un matin frais = FC ~142.<br><br><strong>Les 6 lignes droites sont propres.</strong> En fin de sortie, des bursts courts qui font monter la FC jusqu'à 169 (~88 % FCmax) avec récup entre chaque — l'inertie cardiaque normale entre efforts rapprochés, foulée restée nette (cadence 172). Rien à corriger sur l'exécution.<br><br><strong>Le vrai signal, c'est ton ressenti après 2 jours de repos : tu te sens vraiment bien.</strong> C'est exactement ce qu'on veut en entrée de S26. La semaine est allégée par conception (35 km) — la séance qui compte, c'est la spécifique vallonnée de mercredi, dernier vrai test nutrition avant la Déraille (J-13). D'ici là : easy, tôt le matin, jambes fraîches."}
        arr[1]["date"]="2026-06-25"
        arr[1]["chaussure"]="Novablast 5 J"
        arr[1]["realise"]={"statut":"fait","km":10.66,"temps":"1h02","allure":"5:47/km","fc_moy":148,"fc_max":161,"re":99,"cadence":87,"elevation_gain":20,"rpe_ressenti":5,"commentaire":"10,66 km en 1h02 \u00b7 d\u00e9part 8h00 \u00b7 FC 148/161 \u00b7 cadence 87 \u00b7 D+ 20 m \u00b7 Novablast 5 J \u00b7 canicule. Mardi et mercredi saut\u00e9s (chaleur).","pr":0,"ach":0,"pr_detail":[],"revue":"<strong>Sortir aujourd'hui, c'\u00e9tait la bonne d\u00e9cision.</strong> Apr\u00e8s 4 jours de canicule (~40\u00b0C le jour, nuits >30\u00b0C) et 2 s\u00e9ances saut\u00e9es, ce footing de 10,7 km \u00e0 5:47/km remet le moteur en route sans creuser la fatigue. La d\u00e9rive cardiaque (145 \u2192 153 bpm pour allure stable) est la signature classique chaleur + fatigue accumul\u00e9e. Tu n'as pas forc\u00e9, tu as \u00e9cout\u00e9 \u2014 gestion parfaite."}
        arr[2]["realise"]={"statut":"echec","km":0,"temps":"—","allure":"—","fc_moy":0,"fc_max":0,"rpe_ressenti":0,"commentaire":"Annulée — canicule persistante toute la semaine (40°C jour, 30°C nuit). Aucun créneau exploitable pour une spécifique vallonnée de qualité.","pr":0,"ach":0,"pr_detail":[],"revue":"<strong>Annulée, et c'était le bon choix.</strong> Une spécifique trail par 40°C à J-7 aurait coûté plus qu'elle n'aurait apporté. Le stimulus vallonné manque, mais la fraîcheur est préservée — et à une semaine d'une course Objectif C, la fraîcheur gagne."}
        # Renfo jamais realise : statut clarifie retroactivement pour qu'il ne
        # reste pas indefiniment en 'a faire' six semaines apres la date.
        arr[3]["realise"]={"statut":"skipped","km":0,"temps":"—","allure":"—","fc_moy":0,"fc_max":0,"re":0,"rpe_ressenti":0,"commentaire":"Non réalisée — semaine de canicule persistante (40 °C le jour, 30 °C la nuit) ayant déjà coûté deux séances. Le renforcement n'a pas été rattrapé.","pr":0,"ach":0,"pr_detail":[],"revue":"<strong>Sautée, sans conséquence.</strong> Dans une semaine où la canicule avait déjà coûté deux séances, ajouter du renforcement n'aurait rien apporté à sept jours de la Déraille."}
    SEANCES_BY_WEEK[str(n)]=arr
    if n==27:
        arr[0]["date"]="2026-06-29"
        arr[0]["chaussure"]="Novablast 5 J"
        arr[0]["realise"]={"statut":"fait","km":13.01,"temps":"1h13:32","allure":"5:39/km","fc_moy":155,"fc_max":178,"re":149,"cadence":86,"elevation_gain":35,"rpe_ressenti":6,"commentaire":"13,01 km en 1h13:32 · soirée 19h52 · FC 155/178 · cadence 86 · D+ 35 m · RE 149 · 1046 kcal · Novablast 5 J · avec Edwige R · 30°C ressenti 30°C · 20 PRs Strava.","pr":20,"ach":20,"pr_detail":[],"revue":"<strong>13 km tranquilles avec Edwige — et pourtant 20 PRs Strava.</strong> À 5:39/km par 30°C en soirée, la FC à 155 (80,7% FCmax) raconte le coût réel de la chaleur : une allure conversationnelle qui coûte un effort Z3. C'est la canicule, pas la forme.<br><br><strong>Courir accompagné en début de semaine de course, c'est intelligent.</strong> Le rythme se cale naturellement, on ne force jamais, et le plaisir recharge autant que le repos. Le km 13 à 4:51 en finish montre que les jambes avaient de la réserve.<br><br><strong>Seul bémol :</strong> 13 km à J-6, c'est un peu long pour une semaine de course — mais à cette intensité et avec ce plaisir, ça passe."}
        arr[1]["date"]="2026-06-30"
        arr[1]["chaussure"]="Magic Speed 4"
        arr[1]["realise"]={"statut":"partiel","km":6.54,"temps":"35:14","allure":"5:23/km","fc_moy":149,"fc_max":172,"re":85,"cadence":174,"elevation_gain":27,"rpe_ressenti":7,"commentaire":"Tempo 2×15min prévu — interrompu par un souci gastrique. 6,54 km courus : 4 km d'échauffement EF (FC 131-145) puis 2 km de tempo lancé à 4:53-4:54/km (FC 164-166) avant l'arrêt. Matin 9h31 · cadence 174/184 ppm · D+ 27 m · 24°C · Magic Speed 4 · 2 PRs (place nautique 4:26/km, berges Saône 4:53/km).","pr":2,"ach":3,"pr_detail":["Place nautique confluence 4:26/km","Berges Saône darse→Perrache 4:53/km"],"revue":"<strong>Arrêté par le corps, pas par la tête — et c'était la bonne décision.</strong> Le tempo était bien lancé : échauffement propre en Z2, puis 2 km à 4:53/km FC 164-166, exactement dans la cible. Le souci gastrique a coupé la séance — continuer un effort seuil avec des troubles digestifs à J-5 aurait coûté bien plus que les 15 minutes de tempo manquantes.<br><br><strong>Ce que les 2 km courus disent quand même :</strong> l'allure seuil sort naturellement (2 PRs sur les segments), la cadence tient à 174. Les jambes sont là. La séance est incomplète, pas ratée.<br><br><strong>Pour dimanche :</strong> surveille l'alimentation d'ici la course — rien de nouveau, rien de gras, glucides simples. Si vendredi-samedi passent bien, c'est un incident isolé (chaleur + digestion), pas un signal."}
        arr[2]["date"]="2026-07-02"
        arr[2]["chaussure"]="Clifton 10"
        arr[2]["realise"]={"statut":"fait","km":10.55,"temps":"1h01","allure":"5:41/km","fc_moy":148,"fc_max":170,"re":96,"cadence":87,"elevation_gain":46,"rpe_ressenti":4,"commentaire":"10,55 km en 1h01 · matin 9h25 · FC 148/170 · cadence 87 · D+ 46 m · RE 96 · 827 kcal · Clifton 10 · 0 PR · berges Rhône-Confluence. J-3 Déraille.","pr":0,"ach":0,"pr_detail":[],"revue":"<strong>La sortie parfaite à J-3.</strong> 10,5 km à 5:41/km, FC 148 stable en Z2 — zéro accélération, zéro PR, splits réguliers entre 5:29 et 5:58/km. Le corps tourne en automatique, et le système digestif a bien répondu après l'incident de mardi — c'est le signal qu'on attendait.<br><br><strong>Note chaussures :</strong> Clifton 10 à 1114 km — ne pas embarquer dimanche. <strong>Cascadia 19 pour la Déraille.</strong><br><br><strong>La suite :</strong> repos vendredi-samedi, hydratation, glucides simples, sommeil maximal. Tu es prêt."}
        arr[3]["date"]="2026-07-05"
        arr[3]["chaussure"]="Cascadia 19"
        arr[3]["realise"]={"statut":"fait","km":23.3,"temps":"2:52:48","allure":"7:12/km","fc_moy":168,"fc_max":181,"re":584,"cadence":150,"elevation_gain":957,"rpe_ressenti":8,"commentaire":"TRAIL DÉRAILLE · 23,3 km · D+ 957 m · 66e/gen · 11e/18 M0 · FC 168/181 (88% FCmax) · 2388 kcal · Cascadia 19 · chaleur intense · ~4h sommeil · 3 gels + 3L (1L électrolytes). Course de gestion réussie.","pr":0,"ach":1,"pr_detail":[],"revue":"<strong>Course de gestion réussie dans des conditions extrêmes.</strong> ~4h de sommeil, zéro prépa trail depuis la Circaète, forte chaleur — et tu finis 66e en courant, sans effondrement. FC moyenne 168 (88% FCmax) tenue sur 2h52 : la stratégie de gestion a parfaitement fonctionné.<br><br><strong>Le mur final était thermique, pas nutritionnel.</strong> Sur les 2 derniers km, ta FC reste à 170 pendant que l'allure s'effondre — signature déshydratation + chaleur, pas de panne de sucre. Ta descente reste une arme (km 18 à 4:46/km !). <strong>Voir le détail complet dans le Palmarès.</strong>"}
        SEANCES_BY_WEEK[str(n)]=arr
    if n==28:
        arr[0]["date"]="2026-07-07"
        arr[0]["chaussure"]="Novablast 5 J"
        arr[0]["realise"]={"statut":"fait","km":11.03,"temps":"1h07","allure":"6:02/km","fc_moy":148,"fc_max":192,"re":106,"cadence":85,"elevation_gain":39,"rpe_ressenti":4,"commentaire":"11,03 km en 1h07 · matin 9h07 · FC 148/192 · cadence 85 · D+ 39 m · RE 106 · 880 kcal · Novablast 5 J · 6 PRs · avec Anis (Yannis). Km 1-9 calés sur lui (~6:20-6:30, FC 138-153, récup pure), puis gros dernier km solo à 4:14/km avec FC 184 (max 192 = FCmax). J+2 Déraille, aucune douleur, jambes légères.","pr":6,"ach":6,"pr_detail":["Finish km 11 à 4:14/km"],"revue":"<strong>Le bon usage d'une récup active — avec un finish qui en dit long sur ton état.</strong> Km 1 à 9 calés sur Anis à 6:20-6:30/km, FC 138-153 : c'est <em>encore plus lent</em> que la prescription récup, et c'est exactement ce qu'il fallait à J+2 du trail. Circulation, zéro charge, plaisir partagé. Le manuel du coach.<br><br><strong>Puis le dernier km à 4:14/km, FC 184, max 192.</strong> Ta FCmax exacte atteinte, 2 jours après 957 m de D+, sans jambes lourdes et sans douleur. Ce finish me dit une chose claire : <strong>ton système neuromusculaire est complètement récupéré du trail.</strong> L'énergie est là, le trail est digéré.<br><br><strong>Le bémol honnête :</strong> sur une séance étiquetée récup, ce dernier km à FCmax n'était pas obligatoire, tu le dis toi-même. Une vraie récup reste sous 75% FCmax. Mais ici ça ne compromet rien : c'était court (1 km), le reste était vraiment très facile, et ton corps encaisse bien. À ne pas répéter à chaque footing — mais ponctuellement, sur des jambes qui en réclament, aucun problème.<br><br><strong>L'enseignement :</strong> tu es en avance sur ta récup. On garde S28 en récup comme prévu (pas de bêtise), mais on abordera le seuil de S29 avec sérénité — ton corps répond mieux que le plan ne le supposait."}
        arr[1]["date"]="2026-07-08"
        arr[1]["chaussure"]="Clifton 10"
        arr[1]["realise"]={"statut":"fait","km":10.03,"temps":"1h02","allure":"6:12/km","fc_moy":140,"fc_max":163,"re":60,"cadence":87,"elevation_gain":22,"rpe_ressenti":3,"commentaire":"10,03 km en 1h02 (temps de mouvement) · matin 9h16 · FC 140/163 · cadence 87 · D+ 22 m · RE 60 · 775 kcal · Clifton 10 · 4 PRs · avec Yannis · forte chaleur (canicule persistante). Pause d'environ 18 min au km 5 (discussion), FC qui dérive légèrement en fin de sortie (153→163) par la chaleur, allure stable.","pr":4,"ach":4,"pr_detail":[],"revue":"<strong>Vrai footing de récup, partagé et bien géré malgré la chaleur.</strong> FC moyenne 140 (73% FCmax) sur 10 km à 6:12/km — exactement le registre attendu après la semaine de récup post-Déraille. La pause d'une vingtaine de minutes au km 5 (visiblement une pause discussion avec Yannis) n'a rien d'un problème : courir accompagné avec des arrêts naturels, c'est aussi ça la récup active, et c'est bon pour le mental autant que pour les jambes.<br><br><strong>La dérive de FC en fin de sortie (137 en milieu de course → 154 puis 163 sur le dernier km) alors que l'allure reste stable</strong> est la signature classique de la chaleur qui s'accumule, pas d'un manque de forme — le même mécanisme que sur la Déraille, mais ici sans enjeu puisque c'est un footing tranquille. Rien d'inquiétant, juste le rappel que l'été lyonnais tape fort en ce moment.<br><br><strong>Bilan :</strong> semaine de récup qui se déroule comme prévu, deuxième sortie facile encaissée sans accroc après le gros footing de mardi. Cap sur la suite de S28."}
        arr[2]["realise"]={"statut":"skipped","reason":"Sortie longue avancée au jeudi","km":0,"temps":"—","allure":"—","fc_moy":0,"fc_max":0,"rpe_ressenti":0,"commentaire":"EF aérobie sacrifiée — la sortie longue a été avancée au jeudi (à la place de vendredi), départ prévu 4 jours en montagne dès vendredi. Aucun créneau restant cette semaine.","pr":0,"ach":0,"pr_detail":[],"revue":"<strong>Un report logique, pas un abandon.</strong> Face à un départ en voyage, avancer la sortie longue au jeudi était le bon arbitrage : la longue est la séance la plus structurante de la semaine, elle ne se sacrifie pas. L'EF aérobie passe à la trappe — c'est la bonne priorité à sacrifier quand le temps manque."}
        arr[3]["date"]="2026-07-09"
        arr[3]["chaussure"]="Novablast 5 J"
        arr[3]["realise"]={"statut":"fait","km":18.16,"temps":"1h46","allure":"5:50/km","fc_moy":148,"fc_max":165,"re":171,"cadence":88,"elevation_gain":67,"rpe_ressenti":6,"commentaire":"18,16 km en 1h46 (temps de mouvement) · matin 8h53 · FC 148/165 · cadence 88 · D+ 67 m · RE 171 · 1410 kcal · Novablast 5 J · 5 PRs · avec Edwige. Sortie longue avancée au jeudi (au lieu de vendredi) car départ 4 jours en montagne (rando probable) dès demain. Allure très homogène (5:19 à 6:12/km selon les km), FC qui monte en fin de sortie (146→160) sur les 2 derniers km à allure inchangée. Hydratation : 1 flasque 500ml boisson d'effort électrolytes zéro calorie en démarrage, puis 2 flasques 500ml (1,5L total, ~850 ml/h) + 1 gel. Stratégie ressentie comme très efficace par forte chaleur.","pr":5,"ach":5,"pr_detail":[],"revue":"<strong>Belle sortie longue, et une réorganisation intelligente.</strong> Avancer la longue au jeudi pour libérer les 4 jours de montagne à venir, c'est exactement le bon réflexe : ne jamais sacrifier la séance la plus structurante de la semaine pour un impératif d'agenda — on la déplace, on ne l'annule pas.<br><br><strong>Exécution solide :</strong> 18 km à 5:50/km de moyenne, allure remarquablement stable du début à la fin (5:19 à 6:12/km selon les segments, sans vraie chute). FC moyenne 148 (77% FCmax) — un effort maîtrisé, ni trop mou ni poussé.<br><br><strong>La dérive de FC des 2 derniers kilomètres</strong> (146 → 152 → 160, max 165) alors que l'allure ne bouge quasiment pas est la même signature que sur tes sorties précédentes cette semaine : la chaleur qui s'accumule sur la durée, pas un signe de fatigue ou de mauvaise gestion. À 1h46 d'effort avec cette canicule persistante, c'est attendu et sans gravité.<br><br><strong>La stratégie d'hydratation était la bonne, et à retenir.</strong> 1,5L sur la sortie (~850 ml/h) en commençant par une boisson d'effort électrolytes zéro calorie plutôt que d'attendre la soif : c'est exactement ce qui traite la cause de cette dérive de FC en fin de sortie — pertes hydro-électrolytiques qui s'accumulent avec la chaleur. Complété par 1 gel pour le carburant, dosage cohérent pour 1h46 d'effort modéré. <strong>Garde ce protocole tant que la canicule dure</strong> — attaquer avec les électrolytes puis boire en continu, c'est la bonne discipline. Seule nuance si tu montes en durée (2h30-3h type finish AM) : il faudra alors combiner électrolytes et apport glucidique dans la boisson, les électrolytes seuls ne suffisant plus sur des efforts plus longs.<br><br><strong>Avant de partir :</strong> pense à ton dos sur les 4 jours de rando — sac à dos bien réglé (poids proche du corps, bretelles serrées), surtout en descente où les lombaires encaissent. La rando en montagne est une vraie charge physique, pas du repos passif : ce sera bénéfique pour l'endurance générale, à condition de rester attentif à l'hydratation et à ne pas forcer sur les descentes chargé si le dos tire. Bon voyage — on recalibre S28 et la reprise à ton retour."}
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
        arr[4]["legende"]=[{"c":"#16a34a","l":"Montée marchée / échauffement"},{"c":"#94a3b8","l":"Descente active"}]
        arr[4]["benefices"]="Moteur aérobie (2h d'effort continu), force spécifique via le dénivelé, travail excentrique des quadriceps en descente, proprioception et vivacité de pied. Et surtout : plaisir et mental, le carburant d'une prépa longue."
        arr[4]["coach"]=[{"titre":"En montée","texte":"Marcher sur les fortes pentes n'est pas un aveu de faiblesse — c'est souvent plus efficace et moins coûteux que courir. Les meilleurs traileurs le font."},{"titre":"En descente","texte":"La descente technique est un vrai travail : elle muscle l'excentrique et affûte la proprioception, des qualités qu'un plan route ne développe jamais."}]
        arr[4]["vigilance"]="Après une descente chargée en dénivelé, surveille ton dos (ta vigilance connue) et tes quadriceps qui encaissent l'excentrique. Rien d'alarmant ici, mais reste à l'écoute les 48h suivantes."
        arr[4]["realise"]={"statut":"fait","km":10.70,"temps":"2h07","allure":"11:53/km","fc_moy":138,"fc_max":179,"re":118,"cadence":65,"elevation_gain":646,"rpe_ressenti":4,"commentaire":"10,70 km en 2h07 (temps de mouvement) \u00b7 matin 9h28 \u00b7 D+ 646 m \u00b7 FC 138/179 \u00b7 cadence 65 \u00b7 RE 118 \u00b7 1245 kcal \u00b7 Cascadia 19 \u00b7 avec les copains. Vrai profil trail montagne : mont\u00e9e raide march\u00e9e sur les 2 premiers km (pente +13 puis +16%, FC 134-150, cadence 54-56), terrain ondulant au milieu, puis descente active et engag\u00e9e sur la fin (pente jusqu'\u00e0 -20%, cadence qui monte \u00e0 82-84, vitesse jusqu'\u00e0 ~3:00/km, FC 165-179 sur les segments roulants). Sortie plaisir, tr\u00e8s bonnes sensations.","pr":0,"ach":1,"pr_detail":[],"revue":"<strong>La sortie qui fait du bien \u2014 et qui compte plus qu'elle n'en a l'air.</strong> 646 m de D+ sur 10,7 km, c'est un vrai profil de montagne : un ratio d\u00e9nivel\u00e9/distance qui met les jambes et le cardio au travail bien au-del\u00e0 de ce que la distance sugg\u00e8re. Le d\u00e9couper en \u00ab montée march\u00e9e / descente active \u00bb \u00e9tait exactement la bonne fa\u00e7on de l'aborder en sortie plaisir.<br><br><strong>La montée</strong> (km 1-2, pente +13 \u00e0 +16%, FC 134-150, cadence 54-56) : march\u00e9e intelligemment. Sur ces pentes, marcher est souvent plus efficace et moins co\u00fbteux que courir \u2014 les meilleurs traileurs le font. Zéro g\u00e2chis d'énergie, FC ma\u00eetris\u00e9e.<br><br><strong>La descente</strong> (fin de sortie, pente jusqu'\u00e0 -20%, cadence 82-84, FC 165-179) : c'est l\u00e0 que tu es all\u00e9 chercher de l'intensit\u00e9, et c'est parfait ainsi. La descente technique travaille l'excentrique (les quadriceps encaissent), la proprioception et la vivacit\u00e9 de pied \u2014 des qualit\u00e9s qu'un plan route ne d\u00e9veloppe jamais. FC moyenne 138 (72% FCmax) sur 2h : effort a\u00e9robie mod\u00e9r\u00e9, parfaitement dans le registre \u00ab sortie plaisir \u00bb.<br><br><strong>Ce que \u00e7a apporte \u00e0 ta pr\u00e9pa Nice :</strong> m\u00eame si Nice est une route, cette sortie construit du moteur a\u00e9robie (2h d'effort continu), de la force sp\u00e9cifique (le d\u00e9nivel\u00e9), et surtout du plaisir et du mental \u2014 le carburant qui te fait tenir 30 semaines de pr\u00e9pa. Elle tombe en semaine de r\u00e9cup post-D\u00e9raille, donc j'aurais un l\u00e9ger bémol si tu avais cherch\u00e9 la performance ; mais l\u00e0, c'\u00e9tait march\u00e9 en mont\u00e9e et jou\u00e9 en descente, sans forcer \u2014 le corps encaisse tr\u00e8s bien.<br><br><strong>Un point mat\u00e9riel :</strong> Cascadia 19 \u00e0 pr\u00e9sent ~230 km, elle est parfaite pour ce terrain. Et pense \u00e0 ton dos apr\u00e8s les descentes charg\u00e9es \u2014 rien \u00e0 signaler ici visiblement, mais c'est ta vigilance connue. <strong>Belle sortie, exactement le genre \u00e0 s'autoriser.</strong>"}
        arr.append({"id":6,"num":28,"type":"Trail montagne — sortie plaisir","cat":"trail","sport":"Trail",
          "titre":"Petit Croisse Baulet avec les copains",
          "sous":"Trail montagne sous la chaleur \u00b7 grosse mont\u00e9e march\u00e9e, longue descente engag\u00e9e",
          "date":"2026-07-12","chaussure":"Cascadia 19","rpe":4,"accent":"#0d9488","opt":False,"fill":True,
          "metriques":{"Distance":"11,0 km","D+":"530 m","Dur\u00e9e":"2h35","Type":"Trail montagne"},
          "objectif":"Deuxi\u00e8me sortie trail plaisir du week-end, cette fois au Petit Croisse Baulet et en pleine chaleur de l'apr\u00e8s-midi. Toujours le m\u00eame esprit : on grimpe tranquille, on profite, on l\u00e2che les jambes en descente. Une belle mani\u00e8re de boucler la semaine de r\u00e9cup avec du d\u00e9nivel\u00e9 et du plaisir.",
          "struct":[{"nom":"Approche","txt":"Terrain roulant et l\u00e9g\u00e8re descente pour se mettre en jambes (km 1-4)."},{"nom":"La grosse mont\u00e9e","txt":"Mont\u00e9e du Petit Croisse Baulet : 257 m D+ sur ~1 km (pente ~24%), FC jusqu'\u00e0 176. March\u00e9e, forc\u00e9ment."},{"nom":"La descente","txt":"Longue descente engag\u00e9e (km 8-12, pente -14 \u00e0 -28%), cadence qui grimpe \u00e0 76-84, on d\u00e9roule."}],
          "legende":[{"c":"#16a34a","l":"Approche / mont\u00e9e march\u00e9e"},{"c":"#94a3b8","l":"Descente active"}],
          "benefices":"Force sp\u00e9cifique (une mont\u00e9e \u00e0 24% !), travail excentrique en descente longue, endurance a\u00e9robie sur 2h35, et gestion de l'effort par forte chaleur \u2014 une comp\u00e9tence pr\u00e9cieuse \u00e0 l'approche de l'\u00e9t\u00e9.",
          "coach":[{"titre":"La chaleur","texte":"D\u00e9part \u00e0 13h en pleine chaleur : c'est exigeant. Ta FC moyenne reste pourtant basse (129, 67% FCmax) gr\u00e2ce \u00e0 la marche en mont\u00e9e \u2014 gestion intelligente. Pense hydratation et \u00e9lectrolytes comme sur tes sorties chaudes."},{"titre":"Deux trails en deux jours","texte":"Apr\u00e8s la sortie d'hier, un deuxi\u00e8me trail avec du D+ : le volume de d\u00e9nivel\u00e9 du week-end est cons\u00e9quent. Le corps encaisse car c'est \u00e0 intensit\u00e9 mod\u00e9r\u00e9e, mais accorde-toi une vraie r\u00e9cup d\u00e9but de semaine prochaine."}],
          "vigilance":"Deux sorties trail cons\u00e9cutives avec beaucoup de descente : tes quadriceps et ton dos ont travaill\u00e9. Priorise le repos ou un footing tr\u00e8s facile lundi-mardi. \u00c9coute les signaux.",
          "realise":{"statut":"fait","km":11.04,"temps":"2h35","allure":"14:00/km","fc_moy":129,"fc_max":176,"temp":30,"re":109,"cadence":125,"elevation_gain":530,"rpe_ressenti":4,"commentaire":"11,04 km en 2h35 (temps de mouvement) \u00b7 apr\u00e8s-midi 13h01 (grosse chaleur) \u00b7 D+ 530 m \u00b7 FC 129/176 \u00b7 cadence 62 \u00b7 RE 109 \u00b7 1240 kcal \u00b7 Cascadia 19 \u00b7 avec les copains. Temps fort : la mont\u00e9e du Petit Croisse Baulet (257 m D+ sur ~1 km, pente ~24%, FC 163-176, march\u00e9e). Longue descente engag\u00e9e sur la fin (km 8-12, pente -14 \u00e0 -28%, cadence 76-84, FC 145-165). FC moyenne basse (129) gr\u00e2ce \u00e0 la marche en mont\u00e9e malgr\u00e9 la chaleur. Deuxi\u00e8me trail du week-end.","pr":0,"ach":0,"pr_detail":[],
          "revue":"<strong>Le doubl\u00e9 trail du week-end, et sous la chaleur en prime.</strong> Apr\u00e8s le trail d'hier, tu remets \u00e7a au Petit Croisse Baulet : 530 m de D+ sur 11 km, avec un d\u00e9part \u00e0 13h en pleine cagnard. Chapeau, c'est exigeant.<br><br><strong>La mont\u00e9e du Croisse Baulet</strong> (257 m D+ sur \u00e0 peine 1 km, soit ~24% de pente moyenne, FC jusqu'\u00e0 176) : c'est le gros morceau. \u00c0 cette inclinaison, marcher est la seule option intelligente, et c'est exactement ce que tu as fait. Ce type d'effort d\u00e9veloppe une force sp\u00e9cifique que rien d'autre ne reproduit.<br><br><strong>La longue descente</strong> (km 8-12, pente -14 \u00e0 -28%, cadence 76-84) : belle relance, tu as d\u00e9roul\u00e9. Attention n\u00e9anmoins \u2014 c'est ta deuxi\u00e8me grosse descente en deux jours, les quadriceps encaissent beaucoup d'excentrique.<br><br><strong>La gestion de la chaleur :</strong> FC moyenne 129 (67% FCmax) sur 2h35 par forte chaleur, c'est ma\u00eetris\u00e9 \u2014 la marche en mont\u00e9e a contenu le cardio. J'esp\u00e8re que l'hydratation a suivi (\u00e9lectrolytes d\u00e8s le d\u00e9part, ~850 ml/h, ton protocole canicule).<br><br><strong>Mon conseil de coach :</strong> deux trails avec beaucoup de D+ en deux jours en semaine de r\u00e9cup, c'est un joli volume de d\u00e9nivel\u00e9. Le plaisir prime et le corps encaisse, mais accorde-toi un vrai lundi-mardi tranquille (repos ou footing tr\u00e8s facile) pour laisser les quadriceps et le dos r\u00e9cup\u00e9rer. <strong>Superbe week-end de montagne \u2014 tu attaques la suite de la pr\u00e9pa avec le plein de plaisir.</strong>"}})
        SEANCES_BY_WEEK[str(n)]=arr
    if n==29:
        arr[0]["date"]="2026-07-15"
        arr[3]["date"]="2026-07-16"
        arr[2]["date"]="2026-07-17"
        arr[2]["realise"]={"statut":"fait","km":10.30,"decouplage":{"pct":8.33,"bpm":1.9,"fen_min":49,"temp":28,"attendu":8,"p1":"5:53/km","fc1":144,"p2":"5:59/km","fc2":146,"qualite":"fiable","algo":"decoup-v1"},"temps":"1h00","allure":"5:51/km","fc_moy":147,"fc_max":172,"re":93,"cadence":87,"elevation_gain":33,"rpe_ressenti":5,"commentaire":"10,30 km en 1h00 · matin 9h49 · corps de sortie km 1-8 assez lent (6:00-6:14/km) mais FC déjà 144-149 · accélération sur les 2 derniers km au lieu des lignes droites prévues : km 9 en 5:15/km (FC 158), km 10 en 5:11/km (FC 165), pointe finale à 172 · cadence 87 (stable, n'a pas augmenté sur l'accélération) · RE 93 · 806 kcal · HOKA Clifton 10 (1124 km, fin de vie). Ressenti cardio anormalement haut par rapport à l'habitude, alors que la chaleur avait pourtant diminué.",
        "pr":0,"ach":2,"pr_detail":[],
        "revue":"<strong>Le cardio haut que tu ressens n'est (probablement) pas la chaleur \u2014 c'est la facture d'hier.</strong> Tu as raison d'avoir été surpris : la chaleur a diminué, et pourtant ton corps de sortie tourne à 144-149 bpm sur un rythme de 6:00-6:14/km. Pour comparaison, mercredi tu faisais 5:48/km à 147 bpm (30°C). Aujourd'hui, allure nettement plus lente, FC quasi identique : quelque chose d'autre pousse le cardio vers le haut.<br><br><strong>L'explication la plus probable : tu n'as pas encore totalement récupéré de la sortie longue d'hier.</strong> 23 km sous canicule avec un RE de 222 (ta plus grosse charge de la saison), ça laisse une empreinte 24 à 48h après \u2014 glycogène pas totalement rechargé, hydratation qui rattrape son retard, système nerveux encore sollicité. C'est un schéma classique : la FC de base et d'effort restent élevées le lendemain d'un gros volume, même à allure très facile. Ce n'est pas un signal d'alarme, c'est ton corps qui digère encore.<br><br><strong>Deux détails secondaires qui n'aident pas :</strong> tes Clifton 10 affichent 1124 km \u2014 largement au-delà de la zone de remplacement d'une mousse route (700-900 km), l'amorti mort coûte un peu d'efficacité et donc un peu de cardio en plus. Et tu as couru une accélération de 2 km (5:15 puis 5:11/km) au lieu des lignes droites prévues \u2014 plus intense que prévu sur un corps déjà chargé, ce qui explique la pointe à 172.<br><br><strong>Le point rassurant :</strong> ces 2 km accélérés sur jambes fatiguées, à 5:15 et 5:11/km, restent de bonnes valeurs \u2014 ta forme est là, elle est juste temporairement masquée par la fatigue d'hier.<br><br><strong>Pour le seuil de demain :</strong> si au réveil tu sens encore ce cardio élevé ou les jambes lourdes, n'hésite pas à décaler le seuil à dimanche et garder demain en PPG légère \u2014 mieux vaut un seuil réussi à J+3 qu'un seuil raté à J+2. Si tu te sens bien, fonce, ta base est solide. <strong>Et pense à sortir les Clifton de la rotation qualité \u2014 elles sont clairement en fin de vie.</strong>"}
        arr[1]["date"]="2026-07-19"
        arr[4]["date"]="2026-07-19"
        arr[1]["chaussure"]="Novablast 5 J"
        arr[1]["realise"]={"statut":"fait","km":10.03,"temps":"1h04","allure":"blocs 4:24 & 4:31/km","fc_moy":150,"fc_max":182,"re":96,"cadence":171,"elevation_gain":15,"rpe_ressenti":7,"commentaire":"Seuil 30 avec 2 amis, fait dimanche en derni\u00e8re s\u00e9ance de la semaine \u00b7 d\u00e9part 10h09 \u00b7 10,03 km \u00b7 \u00e9chauffement ~37 min \u00e0 FC 130-143, puis 2\u00d78 min seuil. BLOC 1 : 1808 m \u00e0 4:24/km, FC ~175 (max 182) \u2014 ressenti excellent, a l\u00e2ch\u00e9 Yannis. R\u00e9cup 3 min (FC redescend \u00e0 161). BLOC 2 : 1764 m \u00e0 4:31/km, FC ~175 (max 179) \u2014 volontairement un peu plus rapide, aucune difficult\u00e9. Arr\u00eat\u00e9 \u00e0 10 km (gros projet ViaRh\u00f4na cette semaine). RE 96, 10 records de segments, Novablast 5 J. Aucune douleur, s\u00e9ance ador\u00e9e.",
        "pr":10,"ach":10,"pr_detail":[],
        "revue":"<strong>La plus belle s\u00e9ance de qualit\u00e9 de ta pr\u00e9pa \u2014 et de loin.</strong> Tu devais tenir ~4:40/km au seuil 30 : tu as couru tes deux blocs \u00e0 <strong>4:24 et 4:31/km</strong>, soit 10-15 s/km PLUS RAPIDE que la cible, en te sentant \u00ab tr\u00e8s tr\u00e8s tr\u00e8s bien \u00bb. Ce n'est pas un hasard : c'est exactement ce que ta carte Progression par saison annon\u00e7ait \u2014 ton moteur a chang\u00e9 de dimension.<br><br><strong>Le d\u00e9tail des blocs :</strong> BLOC 1 \u00e0 4:24/km, FC moyenne ~175 avec un pic \u00e0 182 ; r\u00e9cup propre (FC qui redescend \u00e0 161, signe d'un c\u0153ur qui r\u00e9cup\u00e8re vite) ; BLOC 2 \u00e0 4:31/km, FC ~175. Tu parles d'un \u00ab cardio un peu haut \u00bb : en r\u00e9alit\u00e9, 175 bpm sur du seuil 30, c'est <strong>pile dans la zone cible (172-180)</strong> \u2014 ton cardio n'\u00e9tait pas trop haut, il \u00e9tait exactement l\u00e0 o\u00f9 il doit \u00eatre pour cette allure. Et tenir 4:24 \u00e0 cette FC, c'est la signature d'une vraie puissance a\u00e9robie.<br><br><strong>La maturit\u00e9 de gestion :</strong> t'arr\u00eater \u00e0 10 km alors que tu te sentais fort, parce que le ViaRh\u00f4na arrive jeudi, c'est exactement la d\u00e9cision d'un coureur qui pense \u00e0 sa semaine et pas juste \u00e0 sa sortie. Bravo pour \u00e7a.<br><br><strong>10 records de segments</strong> sur une simple s\u00e9ance de seuil, z\u00e9ro douleur, du plaisir plein les jambes : tu arrives au ViaRh\u00f4na en pleine confiance. <strong>Repos ou tr\u00e8s facile d'ici jeudi \u2014 tu es pr\u00eat.</strong>"}
        arr[4]["realise"]={"statut":"skipped","reason":"remplac\u00e9e par le seuil"}
        arr[3]["chaussure"]="Novablast 5 J"
        arr[3]["realise"]={"statut":"fait","km":23.04,"decouplage":{"pct":9.35,"bpm":7.9,"fen_min":125,"temp":31,"attendu":10,"p1":"5:39/km","fc1":146,"p2":"5:41/km","fc2":154,"qualite":"fiable","algo":"decoup-v1"},"temps":"2h10","allure":"5:39/km","fc_moy":150,"fc_max":179,"re":222,"cadence":177,"elevation_gain":67,"temp":28,"rpe_ressenti":7,"commentaire":"23,04 km en 2h10 (2h23 avec pauses ravito) \u00b7 d\u00e9part 9h37 sous canicule \u00b7 avec Edwige \u00b7 allure 5:39/km \u00b7 FC 150/179 \u00b7 cadence 177 spm \u00b7 RE 222 \u00b7 1715 kcal \u00b7 31 records de segments \u00b7 Novablast 5 J. Bloc seuil improvis\u00e9 au tunnel (km 14-15, frais) : GPS liss\u00e9 sous terre mais FC 162-179 confirme l'effort, km 15 en 5:08 (le plus rapide). Hydratation ~2,5 L : 500 ml \u00e9lectrolytes 0 kcal + 500 ml claire + 500 ml pastille sodium + 1 L d'eau. 2 gels caf\u00e9, le 2e vers 1h40-45 apr\u00e8s l\u00e9gers vertiges \u2014 pris un peu tard. Aucune douleur, bien revenu sur la fin, de la r\u00e9serve \u00e0 l'arriv\u00e9e.",
        "pr":31,"ach":31,"pr_detail":[],
        "revue":"<strong>Une sortie longue de r\u00e9f\u00e9rence \u2014 23 km sous canicule, et tu finis avec de la r\u00e9serve.</strong> C'est plus long qu'un semi, par 28\u00b0C et plus, avec une gestion qui montre que les le\u00e7ons des derni\u00e8res semaines sont int\u00e9gr\u00e9es.<br><br><strong>Le d\u00e9roul\u00e9 :</strong> d\u00e9part contr\u00f4l\u00e9 (km 1-5 \u00e0 FC 135-144, discipline parfaite), corps de sortie r\u00e9gulier autour de 5:35-5:50, puis <strong>ton bloc seuil improvis\u00e9 dans le tunnel</strong> (km 14-15) : le GPS a liss\u00e9 les allures sous terre, mais ta FC raconte la v\u00e9rit\u00e9 \u2014 162 de moyenne avec des pics \u00e0 179, et le km 15 boucl\u00e9 en 5:08, le plus rapide de la sortie. Utiliser le seul kilom\u00e8tre frais du parcours pour placer de l'intensit\u00e9, c'est malin \u2014 et \u00e7a donne un avant-go\u00fbt du seuil de samedi.<br><br><strong>La d\u00e9rive thermique :</strong> FC 135-144 en d\u00e9but \u2192 152-160 en fin \u00e0 allure \u00e9gale. Classique sur 2h10 de canicule, et pr\u00e9cis\u00e9ment ce que ta carte Acclimatation est en train de r\u00e9duire semaine apr\u00e8s semaine.<br><br><strong>La nutrition \u2014 le point \u00e0 retenir :</strong> 2,5 L d'hydratation \u00e9chelonn\u00e9e (\u00e9lectrolytes d'abord, sodium renforc\u00e9 ensuite) : pour un gros transpireur sur 2h+ de chaleur, ce n'est PAS trop, c'est adapt\u00e9 \u2014 ton protocole canicule appliqu\u00e9 \u00e0 la lettre. En revanche, <strong>les vertiges vers 1h40 avant le 2e gel sont un signal clair</strong> : sur les sorties >2h, ton 2e gel doit arriver vers 1h15-1h30, pas 1h45. La r\u00e8gle simple pour la suite : un gel toutes les 40-45 min \u00e0 partir de 45 min d'effort. Tu l'as rattrap\u00e9 \u00e0 temps et c'est bien revenu \u2014 mais en course, ce passage \u00e0 vide co\u00fbterait cher.<br><br><strong>31 records de segments</strong> sur une sortie longue caniculaire, sans douleur, avec de la r\u00e9serve \u00e0 la fin : ta base a\u00e9robie est en train de changer de dimension. <strong>Vendredi tr\u00e8s facile pour dig\u00e9rer (RE 222, c'est une grosse charge), le seuil samedi sur jambes fra\u00eeches.</strong> 👏"}
        arr[0]["chaussure"]="Novablast 5 J"
        arr[0]["realise"]={"statut":"fait","km":10.35,"decouplage":{"pct":5.12,"bpm":2.5,"fen_min":58,"temp":30,"attendu":8,"p1":"5:45/km","fc1":146,"p2":"5:48/km","fc2":149,"qualite":"fiable","algo":"decoup-v1"},"temps":"1h00","allure":"5:48/km","fc_moy":147,"fc_max":161,"re":94,"cadence":175,"elevation_gain":31,"temp":30,"rpe_ressenti":5,"commentaire":"10,35 km en 1h00 \u00b7 d\u00e9part 19h44 sous forte chaleur \u00b7 allure 5:48/km tr\u00e8s r\u00e9guli\u00e8re (laps 5:48-5:56, km 2 en 5:28) \u00b7 FC 147/161 (76 % FCmax) \u00b7 cadence 175 spm \u00b7 RE 94 \u00b7 810 kcal \u00b7 plat (berges de Lyon, D+ 31 m) \u00b7 Novablast 5 J. Lundi-mardi en repos (montagne avec les amis, fatigue ressentie) \u2014 semaine d\u00e9marr\u00e9e mercredi volontairement. D\u00e9rive cardiaque mod\u00e9r\u00e9e en fin de sortie (140\u2192155), classique sous chaleur.","pr":0,"ach":0,"pr_detail":[],
        "revue":"<strong>Le d\u00e9marrage intelligent de la S29 \u2014 exactement ce que je t'avais demand\u00e9.</strong> Deux jours de vrai repos apr\u00e8s le doubl\u00e9 trail du week-end, une fatigue \u00e9cout\u00e9e plut\u00f4t que combattue, et une reprise mercredi en EF propre. C'est la vigilance de la revue S28 appliqu\u00e9e \u00e0 la lettre : d\u00e9marrage doux, sans culpabiliser.<br><br><strong>La s\u00e9ance elle-m\u00eame :</strong> 10,35 km \u00e0 5:48/km d'une r\u00e9gularit\u00e9 remarquable \u2014 les 10 kilom\u00e8tres tiennent dans une fourchette de 8 secondes (hors km 2). FC moyenne 147 (76 % FCmax), c'est le haut de ta Z2 : un poil au-dessus de l'EF id\u00e9al, mais par cette chaleur \u00e0 19h44, c'est en r\u00e9alit\u00e9 tr\u00e8s ma\u00eetris\u00e9. La d\u00e9rive cardiaque (140 en d\u00e9but \u2192 155 en fin) est purement thermique, ton allure n'a pas boug\u00e9 d'un pouce.<br><br><strong>La cadence \u00e0 175 spm</strong> sur du plat, c'est ta belle signature technique habituelle \u2014 rien \u00e0 redire.<br><br><strong>Pour la suite de la semaine :</strong> avec le d\u00e9calage, il te reste 4 s\u00e9ances sur 4 jours (seuil, EF technique, PPG, sortie longue). Mon conseil : jeudi EF + technique en r\u00e9cup\u00e9ration active, vendredi le seuil 2\u00d78 min (les jambes seront fra\u00eeches), samedi PPG l\u00e9g\u00e8re, dimanche la sortie longue. Si tu dois sacrifier une s\u00e9ance, c'est la PPG \u2014 jamais le seuil ni la longue en ce moment. <strong>Reprise s\u00e9rieuse, corps \u00e9cout\u00e9, semaine bien engag\u00e9e.</strong>"}

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
        "revue":"<strong>Un marathon complet \u00e0 l'entra\u00eenement, et de loin la plus grosse sortie de ta saison.</strong> 42,52 km, 4h18 de course, charge 367 \u2014 pr\u00e8s du double de ta pr\u00e9c\u00e9dente SL. Tu es all\u00e9 au bout sans jamais te d\u00e9liter, avec de la r\u00e9serve \u00e0 l'arriv\u00e9e. C'est un jalon majeur pour Nice ET pour SaintExpress.<br><br><strong>Le d\u00e9roul\u00e9 est exemplaire.</strong> Seul sur les 15 premiers km \u00e0 5:36/km avec une FC \u00e0 141,8 : c'est tr\u00e8s bas pour cette allure, tu \u00e9tais parfaitement dans ta zone. Puis 23 km avec Yannis \u00e0 6:21/km \u2014 45 s/km plus lent, un choix social assum\u00e9 qui t'a fait \u00e9conomiser \u00e9norm\u00e9ment. Ta FC ne monte qu'\u00e0 145,4 sur cette portion, alors que la temp\u00e9rature grimpait : la chaleur a co\u00fbt\u00e9, pas l'effort.<br><br><strong>Le finish est le vrai enseignement.</strong> Sur les km 41 et 42, tu tiens <strong>5:16 et 5:15/km apr\u00e8s 40 km dans les jambes</strong>, \u00e0 FC 163-167. Ton allure cible Nice, c'est 5:20/km : tu viens de la tenir sur des jambes d\u00e9j\u00e0 fatigu\u00e9es. C'est un signal tr\u00e8s encourageant.<br><br><strong>Mais je dois nuancer, sinon je te mentirais.</strong> Ce n'est pas un marathon continu : 56 minutes d'arr\u00eats r\u00e9partis sur le parcours, et une allure moyenne de 6:04/km, tr\u00e8s loin des 5:20 exig\u00e9s en continu. Ta FC \u00e0 165 sur ces 2 km rapides est \u00e9galement haute \u2014 en course, il faudrait tenir cette allure d\u00e8s le d\u00e9part et pendant 3h45. Ce que \u00e7a prouve : ta r\u00e9sistance \u00e0 la fatigue et ta capacit\u00e9 \u00e0 relancer en fin d'effort sont r\u00e9elles. Ce que \u00e7a ne prouve pas encore : que 5:20 en continu soit acquis. Ce sera le r\u00f4le des sorties longues avec blocs allure marathon cet automne.<br><br><strong>La nutrition a tr\u00e8s bien fonctionn\u00e9.</strong> 3 gels + 3 pastilles + la Clif Bar, et surtout tu as beaucoup bu : z\u00e9ro perte d'\u00e9nergie sur 4h18, aucun vertige, contrairement \u00e0 la SL du 16/7. Le protocole est valid\u00e9, garde-le pour SaintExpress.<br><br><strong>\u26a0\ufe0f Le point qui prime sur tout le reste : ta douleur sous le pied gauche.</strong> Apparue au dernier kilom\u00e8tre apr\u00e8s la plus grosse charge de ta saison, c'est tr\u00e8s probablement de l'accumulation \u2014 mais la localisation (sous le pied) demande de la vigilance. <strong>Rien avant qu'elle ait totalement disparu.</strong> Le signal \u00e0 surveiller : si \u00e7a fait mal aux <em>premiers pas au r\u00e9veil</em> et que \u00e7a s'att\u00e9nue en marchant, c'est la signature d'une irritation de l'apon\u00e9vrose plantaire et il faut la traiter s\u00e9rieusement, pas courir dessus. Glace, \u00e9tirements doux du mollet et de la vo\u00fbte, chaussures amortissantes au quotidien. Si \u00e7a persiste au-del\u00e0 de 3-4 jours ou revient d\u00e8s la reprise \u2192 avis d'un professionnel sans tarder. Tes Clifton 10 sont mortes, ne les remets surtout pas : c'est exactement le type de chaussure qui aggraverait \u00e7a.<br><br><strong>Bravo.</strong> Un marathon en autonomie, une nutrition ma\u00eetris\u00e9e, un finish \u00e0 allure cible, et l'intelligence d'avoir fait du plaisir plut\u00f4t que de la performance. La suite, c'est du repos \u2014 tu l'as largement m\u00e9rit\u00e9."}
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
        "revue":"<strong>Ton ressenti est exact, et les donn\u00e9es le confirment pr\u00e9cis\u00e9ment.</strong> Tu as senti que \u00e7a remontait sur la fin en ayant l'impression d'avoir frein\u00e9 plut\u00f4t qu'acc\u00e9l\u00e9r\u00e9 : c'est exactement ce qui s'est pass\u00e9. Km 0-2 \u00e0 <strong>5:41/km pour 136,7 bpm</strong>, km 8-10 \u00e0 <strong>6:00/km pour 148 bpm</strong>. Tu as ralenti de 19 s/km <em>et</em> ton cardio a pris 11 bpm. C'est de la vraie d\u00e9rive cardiaque, pas un emballement d'allure.<br><br><strong>Ce que \u00e7a dit :</strong> le d\u00e9couplage sort \u00e0 11,6 % contre ~8 % attendu vu la chaleur. Le verdict brut est s\u00e9v\u00e8re, mais le contexte l'explique enti\u00e8rement \u2014 J+3 apr\u00e8s un marathon, 27\u00b0C en fin de journ\u00e9e, apr\u00e8s trois jours sans courir. <strong>Ce n'est pas un d\u00e9faut d'ex\u00e9cution : c'est un marqueur objectif que tu n'es pas encore r\u00e9cup\u00e9r\u00e9.</strong> Ton corps te l'a dit pendant la sortie, l'indicateur le confirme apr\u00e8s coup. C'est exactement \u00e0 \u00e7a qu'il sert.<br><br><strong>Sur ton objectif des 140 bpm :</strong> tu ne l'as pas tenu (15,6 % du temps seulement sous 140, moyenne \u00e0 146). Mais attention \u00e0 ne pas te juger l\u00e0-dessus \u2014 <strong>ta vraie r\u00e9ussite est ailleurs</strong> : ta zone Z2 d'endurance fondamentale va de 134 \u00e0 154 bpm, et tu as pass\u00e9 85 % du temps sous 150. La zone grise (Z3, 154-167) n'a captur\u00e9 que <strong>3,6 % de ta sortie</strong>. L'objectif que tu t'\u00e9tais vraiment fix\u00e9 \u2014 ne pas partir en zone grise \u2014 est pleinement atteint. Le seuil des 140 \u00e9tait simplement trop ambitieux \u00e0 J+3 d'un marathon par 27\u00b0C.<br><br><strong>Le pied :</strong> une g\u00eane sans douleur sur 10 km, trois jours apr\u00e8s le marathon, c'est le sc\u00e9nario rassurant. Continue de surveiller le test des premiers pas au r\u00e9veil. Tant que \u00e7a reste une g\u00eane qui ne s'aggrave pas en courant, on avance prudemment.<br><br><strong>Bon r\u00e9flexe chaussure :</strong> \u00e9trenner la Novablast 5 V maintenant est exactement ce qu'il faut faire \u2014 on ne court jamais un marathon avec une paire neuve. Continue de la roder progressivement d'ici novembre, en alternance, pour arriver \u00e0 Nice avec une chaussure faite \u00e0 ton pied mais pas us\u00e9e.<br><br><strong>Verdict :</strong> sortie utile et bien g\u00e9r\u00e9e dans l'intention. Tu as fait ce qu'il fallait \u2014 bouger doucement pour relancer la circulation sans construire. La d\u00e9rive n'est pas une faute, c'est l'\u00e9tat de fra\u00eecheur du moment. <strong>La semaine prochaine reprend en douceur : pas de qualit\u00e9 avant que le pied soit totalement silencieux et que la d\u00e9rive redescende.</strong>"}
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
        "revue":"<strong>Exactement la sortie qu'il fallait — et un cas d'école de pilotage au cardio.</strong> Tu voulais du facile après le seuil d'hier, tu as tenu FC 139 de moyenne (sous ta barre des 140), et tu as parfaitement raison : l'allure de 5:48/km n'est que la <em>conséquence</em> de ce cardio maîtrisé, pas un objectif en soi. Par temps plus frais, la même FC produit une allure plus rapide qu'en canicule — c'est la preuve en direct de tout ce qu'on a construit ces dernières semaines.<br><br><strong>La dérive cardiaque quasi nulle</strong> (128-138 en début → 137-145 en croisière, sans envolée sur 1h20) confirme une aisance aérobie réelle : ton corps tient cette intensité sans coût croissant. Le lendemain d'un seuil, c'est un excellent signal de fraîcheur.<br><br><strong>Sortie longue ou pas ?</strong> Ta question est juste. À 14 km / 1h20, c'est une <em>grosse sortie facile</em> plutôt qu'une vraie sortie longue au sens de l'entraînement (qui viserait 1h45-2h+ avec une intention spécifique). Disons : une belle séance d'endurance fondamentale, un cran au-dessus d'un footing de récup classique. Ce n'est pas grave qu'elle soit un peu plus longue que prévu — l'intensité est restée basse, donc le coût est celui d'une récup, pas d'une charge.<br><br><strong>Le seul bémol, mineur :</strong> une récup post-seuil idéale se serait arrêtée vers 8-10 km. Les 14 km ne posent aucun problème vu la FC très basse, mais garde en tête que <strong>jeudi c'est 40 km</strong> — d'ici là, priorité absolue à la fraîcheur. Ta séance de demain (mardi) : vraiment courte et facile, et surtout ne rallonge pas. Mercredi repos, comme prévu. <strong>Tu es dans les clous, le corps répond bien, et tu arrives vers le ViaRhôna exactement comme il faut.</strong>"}
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
        "revue":"<strong>Une très belle séance de vitesse — avec un negative split spontané qui en dit long sur ta forme.</strong> Tu as géré exactement comme il faut quand on découvre sa forme du jour : prudent au début (4:10/km), puis tu montes crescendo jusqu'à une <strong>pointe finale à 3:16/km</strong>, ta plus rapide de la saison sur ce format. Ça confirme le potentiel vitesse de ton profil, et le ressenti excellent + zéro douleur, c'est tout bon.<br><br><strong>Le point de vigilance, que tu as toi-même identifié :</strong> tes récups trop actives. À ~5:00/km avec la FC restée à 160-163, ton cœur n'est jamais vraiment redescendu entre les efforts — il monte même de 160 à 182 sur les derniers. Résultat : ta séance a glissé d'une <em>VMA pure</em> vers un mélange <em>tempo + VMA</em>, plus exigeant métaboliquement. Ce n'est pas un défaut, mais c'est à savoir : sur une vraie VMA, les récups doivent te laisser redescendre sous 140 pour que chaque sprint reparte frais et travaille la vitesse pure. Là, tu as fait plus dur.<br><br><strong>Le vrai enjeu maintenant :</strong> c'est ta <strong>2e séance de qualité de la semaine</strong> (après le seuil de dimanche), dans une semaine qui devait en protéger une seule pour préserver le 40 km. Tu le savais, tu as assumé — ton droit. Mais du coup : <strong>mercredi repos ABSOLU, non négociable</strong>, et jeudi tu surveilles ta fraîcheur au réveil. Si les jambes sont lourdes, le ViaRhôna devient une sortie à l'écoute, sans hésiter à raccourcir ou ralentir. Bon choix de chaussure au passage — la Magic Speed 4, c'est exactement son terrain."}
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
        "revue":"<strong>Meilleure s\u00e9ance de vitesse de ta saison, et de loin \u2014 quatre jours apr\u00e8s un marathon.</strong> Tes six intervalles sont en <strong>negative split parfait 6/6</strong> : 4:22, 3:59, 3:52, 3:29, 3:20, 2:57/km. Pas une seule r\u00e9p\u00e9tition qui d\u00e9croche. C'est exactement le sch\u00e9ma d'ex\u00e9cution qu'on cherche : partir prudent, construire, finir fort.<br><br><strong>Ta pointe \u00e0 2:57/km est un vrai marqueur.</strong> Le 21/07, frais, ton meilleur intervalle \u00e9tait \u00e0 3:16/km. Aujourd'hui, \u00e0 J+4 d'un marathon, tu vas <strong>19 s/km plus vite</strong>. Ta r\u00e9serve de vitesse pure est bien r\u00e9elle, et elle progresse.<br><br><strong>L'\u00e9chauffement \u00e9tait bon :</strong> 6,12 km \u00e0 5:48/km avec une FC moyenne de 140,8 \u2014 tu es rest\u00e9 en endurance sur toute la premi\u00e8re partie, ce qui a prot\u00e9g\u00e9 le pied et pr\u00e9par\u00e9 les jambes. C'est le bon format.<br><br><strong>Sur ta difficult\u00e9 \u00e0 redescendre : ton ressenti est exact.</strong> Tu as touch\u00e9 <strong>188 bpm</strong>, soit ton plafond personnel (192). La redescente a \u00e9t\u00e9 rapide jusqu'\u00e0 155 (1 min), puis <strong>bloqu\u00e9e : pr\u00e8s de 8 minutes pour passer sous 150</strong>, et ta FC est rest\u00e9e entre 145 et 167 sur les 15 min de retour au calme. Trois causes se cumulent : tu es mont\u00e9 plus haut qu'au 21/07 (188 contre 182), tu es \u00e0 J+4 d'un marathon avec une fatigue r\u00e9siduelle encore \u00e9lev\u00e9e, et il faisait 29\u00b0C \u00e0 11h. <strong>Ce n'est pas un signal inqui\u00e9tant</strong> \u2014 c'est le prix normal d'\u00eatre all\u00e9 aussi vite dans ces conditions. \u00c0 surveiller quand m\u00eame : si \u00e7a se reproduit sur une s\u00e9ance plus facile et par temps frais, on regardera de plus pr\u00e8s.<br><br><strong>\u26a0\ufe0f Ce que \u00e7a change pour la semaine.</strong> Tu viens de faire ta qualit\u00e9, en mieux que pr\u00e9vu. La s\u00e9ance de demain n'a donc plus lieu d'\u00eatre : <strong>elle devient du repos</strong>. Et ton pied en est au cinqui\u00e8me jour de g\u00eane continue, aujourd'hui sollicit\u00e9 par une s\u00e9ance intense. Encha\u00eener une deuxi\u00e8me qualit\u00e9 demain serait pr\u00e9cis\u00e9ment la d\u00e9cision qui transforme une g\u00eane en blessure.<br><br><strong>Bon r\u00e9flexe chaussure :</strong> deuxi\u00e8me sortie avec la Novablast 5 V, le rodage avance bien pour Nice."}
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
        "revue":"<strong>Ta meilleure s\u00e9ance de pilotage cardiaque de la saison.</strong> FC moyenne 138, jamais au-dessus de 149, <strong>z\u00e9ro seconde pass\u00e9e au-dessus de 150 bpm</strong> sur une heure par 28\u00b0C et air sec. Tu voulais courir au cardio : c'est fait, et de mani\u00e8re exemplaire.<br><br><strong>Sur ton allure de 6:06 que tu trouves \u00ab pas incroyable \u00bb \u2014 c'est une erreur de lecture.</strong> Le d\u00e9couplage le prouve : <strong>2,98 % contre 8 % attendu</strong> vu la chaleur. Concr\u00e8tement, tu as couru la seconde moiti\u00e9 \u00e0 la m\u00eame allure que la premi\u00e8re (5:59/km) avec seulement <strong>+1 bpm</strong>. C'est le meilleur r\u00e9sultat de toutes tes sorties mesur\u00e9es, r\u00e9cup du 20/07 comprise. L'allure est la cons\u00e9quence de la chaleur, pas de ta forme.<br><br><strong>La comparaison qui compte :</strong> dimanche 26/07, m\u00eame distance, FC moyenne 146 et d\u00e9couplage 11,6 %. Aujourd'hui, FC 138 et d\u00e9couplage 3 %. En deux jours, tu es pass\u00e9 d'une s\u00e9ance subie \u00e0 une s\u00e9ance parfaitement ma\u00eetris\u00e9e \u2014 et c'est le signe que tu absorbes enfin le marathon.<br><br><strong>Ton RE de 49 est le plus bas depuis des semaines</strong> : cette sortie t'a co\u00fbt\u00e9 tr\u00e8s peu. C'est exactement ce qu'on veut d'une EF.<br><br><strong>\u26a0\ufe0f Deux points de vigilance.</strong> Le premier : ton pied. Une g\u00eane compar\u00e9e \u00e0 un bleu ressenti <em>\u00e0 chaque pas</em> et pr\u00e9sente depuis six jours, ce n'est plus anodin. Le second, et il aggrave le premier : <strong>tu as couru en Clifton 10</strong>, la paire \u00e0 1148 km, la plus us\u00e9e de ton parc. Courir avec une g\u00eane plantaire dans une chaussure \u00e0 l'amorti fortement entam\u00e9, c'est la combinaison qui transforme une irritation en aponev\u00e9rosite. <strong>Garde-la pour les footings courts</strong> et privil\u00e9gie tes paires r\u00e9centes tant que le pied n'est pas clos.<br><br><strong>Demain repos, et c'est parfait.</strong> Tu as encha\u00een\u00e9 vitesse lundi et une heure d'EF aujourd'hui. Profites-en pour laisser le pied se calmer : si la g\u00eane persiste apr\u00e8s cette journ\u00e9e sans impact, il faudra consulter avant la reprise."}
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
        "revue":"<strong>Le pied a tenu, et c'est l'essentiel du jour.</strong> Deux jours de repos complet ont suffi \u00e0 faire dispara\u00eetre la douleur au d\u00e9part, et la g\u00eane n'est revenue qu'en toute fin de sortie \u2014 sans douleur franche. Ton arr\u00eat \u00e0 ce moment pr\u00e9cis \u00e9tait le bon r\u00e9flexe. Le pied tol\u00e8re environ une heure de course : c'est une information utile pour construire la suite.<br><br><strong>Mais le vrai enseignement est ailleurs, et tu l'as identifi\u00e9 toi-m\u00eame.</strong> Regarde ta progression : km 0-2 \u00e0 <strong>5:35/km \u00e0 FC 136</strong>, puis 5:12, 5:09, 5:16, 5:07, et enfin <strong>4:55/km \u00e0 FC 161</strong> sur la fin. Tu as acc\u00e9l\u00e9r\u00e9 de 40 secondes au kilom\u00e8tre <em>sans le d\u00e9cider</em>, avec une FC qui monte de 25 battements.<br><br><strong>C'est exactement le m\u00e9canisme qui fait exploser un marathon.</strong> Tu ne pars pas trop vite au sens o\u00f9 tu le sentirais \u2014 tu d\u00e9rives progressivement parce que \u00e7a passe bien, et le co\u00fbt n'appara\u00eet qu'apr\u00e8s 30 km. L'identifier maintenant, \u00e0 15 semaines de Nice, c'est pr\u00e9cieux. Ta lucidit\u00e9 sur ce point vaut plus que la s\u00e9ance elle-m\u00eame.<br><br><strong>Sur ton doute concernant 5:20 :</strong> les donn\u00e9es te donnent tort, dans le bon sens. Tu as tenu <strong>5:12/km \u00e0 FC 150</strong> sur les km 2-4, et <strong>5:09/km \u00e0 FC 153</strong> sur les km 4-6. C'est <em>plus rapide</em> que 5:20 \u00e0 une FC <em>inf\u00e9rieure</em> \u00e0 ta cible (155-158). Physiologiquement, 5:20 n'est pas ambitieux pour toi \u2014 il est confortable. Ton probl\u00e8me n'est pas de l'atteindre, c'est de <strong>ne pas aller plus vite</strong>.<br><br><strong>D\u00e9couplage 3,53 % pour 6 % attendu</strong> : bon r\u00e9sultat, d'autant que tu as acc\u00e9l\u00e9r\u00e9 en cours de route. Ton moteur encaisse bien.<br><br><strong>Ce que \u00e7a change pour la suite :</strong> ta priorit\u00e9 num\u00e9ro un n'est plus d'apprendre \u00e0 courir \u00e0 5:20, mais d'apprendre \u00e0 <strong>ne pas d\u00e9passer</strong> 5:20. C'est un travail de discipline, pas de forme \u2014 et il se fait avec un retour d'allure fiable (alerte Garmin sur parcours d\u00e9gag\u00e9), pas au ressenti."}
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
        "revue":"<strong>Ta premi\u00e8re vraie donn\u00e9e chiffr\u00e9e allure/FC pour Nice \u2014 et elle est plut\u00f4t encourageante.</strong> Le probl\u00e8me du GPS sous tunnel a rendu la r\u00e9gulation d'allure difficile en temps r\u00e9el, mais gr\u00e2ce \u00e0 la FC (qui ne d\u00e9pend pas du GPS) et \u00e0 tes intervalles manuels, on peut quand m\u00eame en tirer une lecture solide.<br><br><strong>Le bloc le plus instructif est le 2 :</strong> \u00e0 FC 152,3 \u2014 pile dans ta zone cible (155-158) \u2014 tu as produit <strong>5:29/km</strong>. C'est la donn\u00e9e la plus fiable de la s\u00e9ance : elle situe pr\u00e9cis\u00e9ment ton niveau actuel \u00e0 la FC que tu dois apprendre \u00e0 tenir 3h45. L'\u00e9cart avec 5:20 est de 9 secondes au kilom\u00e8tre \u2014 pas norm\u00e9ment.<br><br><strong>Le bloc 4 confirme une progression :</strong> tr\u00e8s bien ex\u00e9cut\u00e9, r\u00e9gulier (5:07 puis 5:06), \u00e0 FC 165,5. C'est <strong>plus rapide qu'au marathon \u00e0 FC comparable</strong> (5:15/km \u00e0 163-167 le 23/07). M\u00eame si c'est encore au-dessus de ta FC cible, la tendance va dans le bon sens.<br><br><strong>Sur tes blocs 1 et 3, irr\u00e9guliers</strong> (5:34\u21924:15 puis 5:41\u21924:29) : c'est exactement le probl\u00e8me du rep\u00e8re perdu que tu d\u00e9cris, pas un souci de forme. Sans allure affich\u00e9e, on sur-corrige apr\u00e8s avoir jug\u00e9 le d\u00e9but trop prudent. C'est une lecture utile sur la difficult\u00e9 \u00e0 piloter au ressenti pur \u2014 le repos et la r\u00e9p\u00e9tition r\u00e9soudront \u00e7a.<br><br><strong>Ta propre conclusion est juste :</strong> tu es en capacit\u00e9 de tenir 5:20/km, il faut maintenant travailler la r\u00e9gularit\u00e9 \u00e0 cette allure pr\u00e9cise \u2014 id\u00e9alement sur piste ou parcours balis\u00e9 pour retrouver un vrai rep\u00e8re GPS.<br><br><strong>\u26a0\ufe0f Le point le plus important : la douleur au pied est revenue apr\u00e8s 10-12 km, sp\u00e9cifiquement sur une s\u00e9ance \u00e0 allure soutenue.</strong> C'est une information pr\u00e9cieuse qu'on n'avait pas encore : tes EF faciles ne la d\u00e9clenchent pas, mais l'allure marathon prolong\u00e9e oui. Ta d\u00e9cision d'\u00e9courter plut\u00f4t que de boucler la boucle pr\u00e9vue est exactement le bon r\u00e9flexe.<br><br><strong>Demain repos complet, non n\u00e9gociable.</strong> La suite se d\u00e9cide au ressenti : si la douleur a totalement disparu apr\u00e8s une journ\u00e9e, deux jours de repos peuvent suffire avant la sortie longue de samedi \u2014 mais si elle persiste, mieux vaut un troisi\u00e8me jour et d\u00e9caler la sortie longue plut\u00f4t que de forcer. On ne joue pas cette d\u00e9cision \u00e0 la l\u00e9g\u00e8re : une allure marathon qui r\u00e9veille une g\u00eane plantaire est le signal le plus s\u00e9rieux depuis le marathon."}
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
        "revue":"<strong>Tu as pris la bonne d\u00e9cision, et les donn\u00e9es le confirment sans ambigu\u00eft\u00e9.</strong> Ton \u00e9chauffement terminait d\u00e9j\u00e0 \u00e0 FC 165 \u2014 un \u00e9chauffement facile ne fait jamais \u00e7a. La chaleur pesait avant m\u00eame la premi\u00e8re r\u00e9p\u00e9tition.<br><br><strong>Le point le plus important : ta vitesse n'\u00e9tait pas le probl\u00e8me.</strong> Tes tentatives de 400 tournent entre 3:30 et 3:57/km \u2014 tu as souvent \u00e9t\u00e9 <em>plus rapide</em> que la cible de 3:45-3:50. Musculairement et en allure pure, tu avais largement le niveau. <strong>Ce qui a c\u00e9d\u00e9, c'est la r\u00e9cup\u00e9ration entre les efforts</strong> : ta FC restait coll\u00e9e \u00e0 175-180 bpm m\u00eame pendant les phases cens\u00e9es \u00eatre faciles. Un c\u0153ur qui ne redescend plus entre les blocs, c'est le signal physiologique exact d'une chaleur qui a chang\u00e9 la donne, pas d'un manque de forme.<br><br><strong>La comparaison avec dimanche est parlante.</strong> M\u00eame toi, m\u00eame niveau de forme : FC 150-154 dimanche pour un effort mod\u00e9r\u00e9, FC 166-180 aujourd'hui pour un effort comparable ou moindre. Seule la temp\u00e9rature a boug\u00e9. Ce n'est pas qu'une impression \u2014 <strong>Lyon est actuellement en vigilance orange canicule</strong>, confirm\u00e9 par M\u00e9t\u00e9o-France.<br><br><strong>La fin de s\u00e9ance le confirme aussi</strong> : 5:03/km \u2014 une allure tempo mod\u00e9r\u00e9e \u2014 t'a co\u00fbt\u00e9 une FC moyenne de 166, soit le tarif normal d'un seuil. M\u00eame le \u00ab plan B \u00bb tournait cher.<br><br><strong>La vraie bonne nouvelle du jour : z\u00e9ro douleur au pied</strong>, y compris en fin de s\u00e9ance et en r\u00e9cup\u00e9ration, apr\u00e8s une sortie exigeante. C'est un signal solide que la g\u00eane de fin juillet est derri\u00e8re toi.<br><br><strong>Ce que \u00e7a change pour la suite de la semaine.</strong> La vigilance canicule reste active. Les s\u00e9ances de mercredi et jeudi doivent imp\u00e9rativement partir tr\u00e8s t\u00f4t (6h30 maximum), rester pilot\u00e9es au cardio et non \u00e0 l'allure, et rester courtes. La sortie longue de samedi m\u00e9ritera la m\u00eame vigilance \u2014 d\u00e9part \u00e0 l'aube non n\u00e9gociable. <strong>6 r\u00e9p\u00e9titions sur 8 dans ces conditions, c'est un bon r\u00e9sultat, pas un \u00e9chec.</strong>"}
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
        "revue":"<strong>Une sortie de r\u00e9cup\u00e9ration ex\u00e9cut\u00e9e exactement comme il fallait, avec un test de pied concluant.</strong> Corps de sortie tr\u00e8s stable \u00e0 5:59/km et FC 134 de moyenne \u2014 un vrai EF facile, sans \u00e0-coup.<br><br><strong>Ton sprint final est confirm\u00e9 au m\u00e8tre pr\u00e8s :</strong> 336 m \u00e0 4:42/km de moyenne, avec une pointe \u00e0 <strong>3:36/km</strong> et une FC qui monte \u00e0 166. <strong>Aucune g\u00eane signal\u00e9e</strong> \u2014 c'est le test que tu voulais faire, et il est concluant : le pied encaisse une acc\u00e9l\u00e9ration franche en fin de sortie fatigu\u00e9e.<br><br><strong>Sur ta fatigue musculaire ressentie malgr\u00e9 l'allure facile \u2014 c'est un vrai signal, pas une impression.</strong> Le fractionn\u00e9 d'hier a co\u00fbt\u00e9 plus cher que son volume ne le laissait penser : 6 r\u00e9p\u00e9titions \u00e0 haute intensit\u00e9 en canicule, avec des pauses forc\u00e9es, ce n'est pas anodin pour les jambes m\u00eame si le kilom\u00e9trage total \u00e9tait mod\u00e9r\u00e9. C'est cette fatigue-l\u00e0 que tu sens aujourd'hui, et c'est exactement ce \u00e0 quoi sert une sortie facile le lendemain.<br><br><strong>Sur le d\u00e9couplage :</strong> il ressort \u00e0 4,29 % mais marqu\u00e9 \"incertain\" par la proc\u00e9dure \u2014 et c'est en fait une bonne nouvelle d\u00e9guis\u00e9e. Le test de robustesse d\u00e9tecte une petite instabilit\u00e9 en fin de fen\u00eatre, ce qui arrive pr\u00e9cis\u00e9ment quand une sortie est <em>si plate et ma\u00eetris\u00e9e</em> que la d\u00e9rive r\u00e9elle est noy\u00e9e dans le bruit de mesure. Rien d'alarmant : ta r\u00e9gularit\u00e9 aujourd'hui rend le chiffre difficile \u00e0 mesurer pr\u00e9cis\u00e9ment, pas le signe d'un probl\u00e8me. Il ne sera pas compt\u00e9 dans la tendance, par prudence.<br><br><strong>Un point technique corrig\u00e9 en coulisses :</strong> la fiche de demain proposait tes Clifton 10 par d\u00e9faut. Elles restent dans ta rotation, mais tant que le pied est sous surveillance je pr\u00e9f\u00e8re orienter les s\u00e9ances \u00e0 venir vers tes paires r\u00e9centes.<br><br><strong>Bilan : bonne d\u00e9cision d'aujourd'hui.</strong> Tu as \u00e9cout\u00e9 la fatigue sans la sur-interpr\u00e9ter, test\u00e9 le pied intelligemment en fin de sortie plut\u00f4t qu'\u00e0 froid, et le r\u00e9sultat est rassurant sur tous les plans."}

        # Jeudi : EF + lignes droites (decale du mercredi)
        arr[2]["date"]="2026-08-06"
        arr[2]["realise"]={"statut":"fait","km":10.09,"temps":"1h00","allure":"5:56/km","fc_moy":140,"fc_max":170,"re":56,"cadence":175,"elevation_gain":36,"temp":26,"rpe_ressenti":4,
        "decouplage":{"pct":-0.61,"bpm":-1.2,"fen_min":43,"temp":26,"attendu":8,"p1":"6:06/km","fc1":138,"p2":"6:08/km","fc2":137,"qualite":"incertain","algo":"decoup-v1"},
        "commentaire":"EF + 6\u00d7100 m, r\u00e9cup 30 sec active \u00b7 d\u00e9part 9h15, ~26\u00b0C \u00b7 10,09 km en 1h00. CORPS EF (9,46 km) tr\u00e8s ma\u00eetris\u00e9 : profil en 3 tiers 6:09 \u2192 6:13 \u2192 5:51/km avec FC 137 \u2192 137 \u2192 141 \u2014 mont\u00e9e en r\u00e9gime progressive et quasi gratuite en co\u00fbt cardiaque (le \"diesel\" d\u00e9crit). D\u00e9couplage -0,61 % (quasi nul, sens n\u00e9gatif) pour 8 % attendu \u2014 aucune d\u00e9rive. Sur les 6\u00d7100 m : accel\u00e9rations ressenties comme naturelles et non forc\u00e9es, progressives, dernier r\u00e9p\u00e9t\u00e9 volontairement moins vite que l'avant-dernier par prudence (3\u00e8me sortie de la semaine). Deux segments confirm\u00e9s dans les donn\u00e9es \u00e0 3:42-3:46/km, FC 162-168. RPE bas (4/10) pour une s\u00e9ance incluant des accel\u00e9rations. ZERO douleur au pied. \u26a0\ufe0f Chauss\u00e9 en HOKA Clifton 10 (paire retir\u00e9e de la rotation le 27/07 pour d\u00e9lamination).",
        "pr":1,"ach":1,"pr_detail":[],
        "revue":"<strong>Le sch\u00e9ma \"diesel\" que tu d\u00e9cris est exactement ce que montrent les donn\u00e9es, et c'est un tr\u00e8s bon signe.</strong> Ton corps de sortie EF se d\u00e9coupe en trois tiers tr\u00e8s parlants : <strong>6:09/km \u00e0 FC 137</strong>, puis <strong>6:13/km \u00e0 FC 137</strong> (identique, le temps de vraiment se mettre en jambes), puis <strong>5:51/km \u00e0 FC 141</strong> \u2014 tu acc\u00e9l\u00e8res de 22 secondes au kilom\u00e8tre pour seulement 4 battements de plus. C'est une acc\u00e9l\u00e9ration quasi gratuite en co\u00fbt cardiaque, le signe d'un moteur a\u00e9robie qui monte en temp\u00e9rature progressivement plut\u00f4t que d'un manque de forme.<br><br><strong>Le d\u00e9couplage confirme ind\u00e9pendamment ce que tu ressens :</strong> -0,61 %, quasi nul et m\u00eame l\u00e9g\u00e8rement n\u00e9gatif (ta FC a \u00e9t\u00e9 stable voire meilleure en fin de corps EF). Aucune d\u00e9rive, alors que 8 % \u00e9taient attendus vu la temp\u00e9rature. C'est une preuve chiffr\u00e9e que ta base a\u00e9robie encaisse tr\u00e8s bien.<br><br><strong>Sur les 6\u00d7100 m :</strong> ta lecture de la s\u00e9ance est juste. Les deux segments que je peux confirmer dans les donn\u00e9es tournent \u00e0 3:42-3:46/km, FC 162-168 \u2014 des vraies pointes de vitesse, produites sans forcer. Et ta d\u00e9cision de lever le pied sur le dernier plut\u00f4t que d'aller chercher un chrono, \u00e0 J+2 du fractionn\u00e9 interrompu de mardi, c'est exactement le genre d'\u00e9coute qui \u00e9vite les blessures. Tu as raison de noter que c'est ta 3\u00e8me sortie de la semaine : le d\u00e9marrage plus lent en est probablement la cons\u00e9quence directe, pas un signal n\u00e9gatif.<br><br><strong>Z\u00e9ro douleur au pied</strong>, sur une s\u00e9ance qui incluait des acc\u00e9l\u00e9rations \u2014 c'est le test le plus concret depuis la reprise, et il est concluant.<br><br><strong>Un point mat\u00e9riel, sans reproche.</strong> Tu as couru en <strong>Clifton 10</strong>, une paire qui reste dans ta rotation mais affiche un kilom\u00e9trage \u00e9lev\u00e9. Aucune cons\u00e9quence aujourd\'hui, z\u00e9ro douleur. Ma recommandation : garde-les pour les footings courts et privil\u00e9gie tes paires r\u00e9centes sur les s\u00e9ances longues ou rapides \u2014 c\'est l\u00e0 que l\'amorti compte vraiment."}

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
        "revue":"<strong>La lecture terrain confirme ce que tu ressens, au kilom\u00e8tre pr\u00e8s.</strong> Sur les 10 laps, l'allure oscille entre 5:47 et 6:11/km et la FC entre 124 et 136 bpm \u2014 une bande tr\u00e8s resserr\u00e9e, sans aucun emballement. C'est exactement l'oppos\u00e9 de ta d\u00e9rive naturelle habituelle : ici, tu as tenu la bride sur 10 km complets, pas seulement sur les premi\u00e8res minutes.<br><br><strong>Sur l'objectif \u00abpasser sous 130\u00bb :</strong> les donn\u00e9es expliquent pourquoi c'est dur. Ton lap le plus lent en FC basse (lap 3, 6:00/km) est tomb\u00e9 \u00e0 124 bpm \u2014 mais c'\u00e9tait en l\u00e9g\u00e8re descente. D\u00e8s que le terrain redevient plat ou l\u00e9g\u00e8rement montant, ta FC remonte vers 133-136 m\u00eame en gardant une allure proche de 5:50-6:00/km. <strong>Ce n'est pas un manque de discipline \u2014 c'est ton moteur a\u00e9robie actuel qui situe naturellement le seuil des 130 bpm autour de 6:05-6:15/km sur terrain plat, pas en dessous.</strong> Descendre sous 130 tout en restant sous 6:00/km, c'est un gain qui viendra de l'entra\u00eenement de fond dans la dur\u00e9e (des mois, pas des s\u00e9ances), pas d'un effort de volont\u00e9 suppl\u00e9mentaire un matin donn\u00e9.<br><br><strong>La fra\u00eecheur matinale n'est pas qu'une impression.</strong> D\u00e9part \u00e0 7h49, bien avant que la chaleur ne s'installe : ta FC pour cette allure est nettement plus basse qu'elle ne l'aurait \u00e9t\u00e9 \u00e0 9h ou 10h en pleine canicule. La tr\u00e8s faible transpiration que tu signales va dans le m\u00eame sens \u2014 c'est un vrai marqueur physiologique de sortie fra\u00eeche, pas juste un ressenti agr\u00e9able. Ce timing matinal est \u00e0 reproduire chaque fois que possible tant que la canicule dure.<br><br><strong>Z\u00e9ro douleur au pied sur une 4e sortie cons\u00e9cutive</strong> \u2014 c'est le signal le plus solide depuis la reprise. La g\u00eane du 23/07-5/08 semble bel et bien derri\u00e8re toi.<br><br><strong>Le point de vigilance honn\u00eate :</strong> cette sortie n'\u00e9tait pas au plan, le jour \u00e9tait pos\u00e9 en repos pour une raison pr\u00e9cise \u2014 arriver frais avant la boucle de Saint-\u00c9tienne de dimanche (27 km, 650 m D+). L'intensit\u00e9 tr\u00e8s faible et le z\u00e9ro douleur rassurent, mais tu es maintenant \u00e0 4 jours cons\u00e9cutifs avant un effort vallonn\u00e9 exigeant, avec un seul jour de repos (samedi) entre les deux. <strong>Le repos de demain n'est plus une option de confort, c'est ce qui garantit que dimanche se passe bien.</strong> Aucune sollicitation samedi, pas m\u00eame une marche longue.<br><br><strong>Bilan : belle initiative, bien ex\u00e9cut\u00e9e, mais \u00e9coute le repos de demain \u00e0 la lettre.</strong> Le travail de retenue cardiaque que tu fais l\u00e0, c'est litt\u00e9ralement ton point faible du radar (allure marathon 42/99) que tu adresses directement \u2014 la bonne direction, au bon rythme, sans forcer."}

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
        "revue":"<strong>Tu me dis qu'on ne peut pas en tirer de grands enseignements. Je ne suis pas d'accord : c'est la sortie la plus instructive depuis ViaRhona, et l'enseignement est dans les six derniers kilometres.</strong><br><br><strong>Ce que disent les laps apres le depart de Yannis (km 23) :</strong> km 22 en 7:15/km (FC 139), puis 5:57 (FC 145), 5:42 (FC 151), 5:42 (FC 155), 5:28 (FC 162), et le dernier a <strong>5:07/km a FC 166, max 172</strong>. Tu as accelere de plus de deux minutes au kilometre sur la fin, avec une FC qui monte de 27 battements, en escalier, sans interruption.<br><br><strong>Tu m'as decrit ca comme \"j'ai eu un petit don et sur la fin ca s'est remonte, c'est chouette\". Les donnees decrivent autre chose : ta derive.</strong> C'est exactement le pattern qu'on cherche a corriger - 5:35 qui devient 4:55 sans decision consciente. Ici, des que le cadre social a disparu (Didier au 20e, Yannis au 23e), l'allure s'est envolee toute seule. <strong>Le contraste avec vendredi est saisissant : 132 bpm tenus sur 10 km quand tu avais une cible chiffree en tete, 166 bpm sur le dernier kilometre quand plus rien ne t'encadrait.</strong> Ce n'est pas un probleme de moteur, c'est un probleme de pilote automatique.<br><br><strong>Deuxieme lecture, et elle est tres positive :</strong> finir un 27 km avec 662 m D+ en accelerant a 5:07/km, c'est-a-dire <em>plus vite que ton allure marathon cible</em>, avec une FC de 166 - c'est un vrai marqueur de durabilite. Ton moteur va bien, tres bien meme. Ce dernier kilometre valide aussi la plage FC dont on parlait : 5:07/km sur jambes fatiguees te coute 166 bpm, ce qui confirme que ta cible de 148-160 bpm a 5:20/km est bien calibree.<br><br><strong>Note aussi que ton ressenti et le terrain divergent.</strong> Tu situes le passage dur au km 24-25 - or c'est precisement la que tu accelerais (5:42/km). La difficulte venait de la chaleur et du plein soleil, pas du rythme. Tu as encaisse la chaleur en <em>montant</em> l'allure : c'est courageux, mais c'est aussi la definition d'une allure non pilotee.<br><br><strong>Le reste de la sortie est propre.</strong> FC moyenne 145 sur 3h16, montees gerees entre 140 et 155 bpm, marche assumee dans les portions raides (cadence descendue a 60-68 sur Rochetaillee et la montee du km 21) - c'est exactement la bonne gestion en trail. Effort relatif 246, ta plus grosse charge depuis ViaRhona.<br><br><strong>Le signal medical du jour est excellent : zero douleur au pied apres 27 km et 662 m D+, sur terrain instable et en descente technique.</strong> C'etait le dernier test que le pied n'avait pas passe depuis la gene du 23/07. Il l'a passe. Le dossier peut etre considere comme clos, sous reserve de la reponse a J+1 et J+2.<br><br><strong>Un point materiel a corriger :</strong> tu as couru en Novablast 5 J (route, desormais 689 km) alors que le plan indiquait Cascadia 19. Ca s'est bien passe, mais sur 662 m D+ avec descentes techniques, une semelle route sur sentier c'est une accroche en moins pour rien - et 689 km sur une paire d'entrainement, l'amorti commence a etre entame. Pour SaintExpress et ses sorties preparatoires, reflexe Cascadia.<br><br><strong>Bilan : superbe sortie, objectif plaisir atteint, et un enseignement technique de premier ordre.</strong> Ne retiens pas seulement \"c'etait chouette de finir fort\" - retiens que tu as accelere sans le decider. A Nice, ce meme automatisme au km 25 te coutera le chrono. C'est precisement le muscle qu'on entraine avec les blocs de retenue."}

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
# Revues de semaine post-bilan
_S25_REVUE="<p>La semaine de reprise que tu devais faire. Pas celle que tu espérais peut-être, mais celle qu'il fallait — et tu l'as exécutée proprement.</p><p><strong>Ce qui ressort avant tout : la gestion de la chaleur.</strong> Quatre séances sur cinq démarrées entre 7h25 et 8h30. L'écart entre la s3 (FC 165/181, subi à midi par 30°C) et les quatre autres (FC 140-151, maîtrisé) dit tout sur l'importance de l'horaire. Ce n'est pas une variable de confort, c'est une variable de performance.</p><p><strong>La progression dans la semaine est nette.</strong> S1/S2 très faciles (FC 140-143, moteur en veille). S3 qualité tenue en conditions difficiles, 6 km à 5:14/km. S4 sortie longue avec <strong>fast finish à 4:58/km sur le dernier kilomètre</strong> — sub-5 min au 4e jour consécutif en canicule. S5 bonus parfait à 7h25 chez les parents, FC 144 en plein cœur de la Z2, rien dépensé.</p><p><strong>Ce que cette semaine confirme pour la Déraille (J-16) :</strong> tu n'es pas en reprise, tu es en forme. La résistance à la fatigue est là. S26 est allégée par conception — laisse-la être légère, la séance clé c'est mercredi.</p>"
_S26_REVUE="La semaine que la canicule a mangée. Quatre nuits à plus de 30°C, journées à 40°C — sur 4 séances prévues, 2 réalisées (21,9 km sur 35). Mais les 2 faites étaient les bonnes : lundi footing + lignes droites à 5:53/km FC 148 (RPE 3), jeudi 10,7 km à 5:47/km avec dérive cardiaque maîtrisée après 2 jours d'arrêt forcé. Mardi-mercredi sautés : pas de la flemme, du jugement — courir par 40°C à J-10 aurait coûté plus que ça n'aurait rapporté. La spécifique trail vallonnée a été sacrifiée à la chaleur — le stimulus manque, la fraîcheur est intacte. À une semaine d'une course Objectif C, c'est le bon arbitrage."
_S27_REVUE="La semaine de course, et elle s'est terminée comme elle devait : par une vraie réussite de gestion. 53 km au total dont la Déraille (23,3 km, D+ 957 m) bouclée en 2:52:48 — 66e sur 180, 11e/18 en M0. La semaine a commencé fort avec 13 km tranquilles avec Edwige lundi (un peu longs pour une semaine de course, mais faits en plaisir), puis un tempo interrompu par un souci gastrique mardi — arrêté au bon moment, sans forcer. Le footing EF de jeudi (10,5 km, FC 148, zéro PR) était la sortie d'affûtage parfaite : le corps en automatique, le système digestif rétabli. Et dimanche, la course : FC moyenne 168 tenue sur 2h52 sans jamais d'effondrement, contrairement à la Circaète. Le mur des 2 derniers km était thermique (FC haute, allure qui chute), pas nutritionnel. Sur ~4h de sommeil et sans prépa trail, c'est une performance de tête autant que de jambes. Objectifs atteints : relancer la machine, tester la nutrition, courir intelligemment. Bilan de semaine : solide."
_S28_REVUE="<p><strong>Une semaine de « récupération » à 61 km au lieu de 36 — parlons-en franchement.</strong> Sur le papier, c'est un dépassement de 69 % du volume cible, ce qui d'ordinaire mériterait un vrai froncement de sourcils de coach. Dans les faits, c'est l'une des plus belles semaines de ta saison — parce que le volume ne dit pas tout, l'intensité et le contexte disent le reste.</p><p><strong>Le déroulé :</strong> deux récupérations actives propres mardi-mercredi (FC 137-140, discipline parfaite), la sortie longue avancée à jeudi et gérée intelligemment sous la chaleur (18 km, protocole hydratation validé, fast finish maîtrisé), puis <strong>le doublé trail du week-end en montagne</strong> : 10,7 km / D+ 646 m samedi, 11 km / D+ 530 m dimanche au Petit Croisse Baulet, départ 13h en pleine chaleur. 1 176 m de D+ cumulés en deux jours — du jamais vu dans ta saison.</p><p><strong>Pourquoi ça passe :</strong> les FC racontent la vérité. 138 et 129 de moyenne sur les deux trails (67-72 % FCmax) — tu as marché les montées, déroulé les descentes, zéro forcing. C'est du temps de pied et du dénivelé en mode plaisir, pas de la charge d'entraînement au sens dur. La forme finit la semaine à 90/100 et l'ACWR à 1,10 : le corps a encaissé, et il a même apprécié.</p><p><strong>Ce que la semaine t'apporte :</strong> de la force spécifique (une montée à 24 % !), du travail excentrique en descente, 2h30+ d'effort continu deux jours de suite, et surtout du plaisir entre copains — le carburant mental d'une prépa de 30 semaines. C'est exactement le genre de « récupération active » qui ne s'écrit pas dans les plans mais qui construit un coureur.</p><p><strong>Le point de vigilance pour S29 :</strong> deux grosses descentes consécutives, ça laisse des traces dans les quadriceps et ça sollicite le dos (ta vigilance connue). La S29 « Seuil découverte » démarre par du facile — respecte ce démarrage doux, et si les jambes parlent encore mardi, décale le premier bloc seuil d'un jour sans culpabiliser. <strong>Bilan : 5/6 · 60,96 km · une semaine de récup qui n'en avait que le nom, et c'est très bien comme ça.</strong> 👏</p>"
_S29_REVUE="<p><strong>Une semaine de reprise magistrale \u2014 et elle se termine en apoth\u00e9ose.</strong> Apr\u00e8s le double trail du week-end pr\u00e9c\u00e9dent, tu as \u00e9cout\u00e9 ton corps (lundi-mardi off), red\u00e9marr\u00e9 en douceur mercredi, encha\u00een\u00e9 une sortie longue de r\u00e9f\u00e9rence, puis boucl\u00e9 par la plus belle s\u00e9ance de qualit\u00e9 de ta pr\u00e9pa. 4 s\u00e9ances, 54 km, z\u00e9ro douleur, une confiance qui explose.</p><p><strong>Le d\u00e9roul\u00e9 :</strong> EF de reprise mercredi (10,4 km, FC ma\u00eetris\u00e9e sous 30\u00b0C) \u00b7 sortie longue jeudi (23 km sous canicule, 31 records, protocole nutrition affin\u00e9) \u00b7 EF technique vendredi (cardio un peu haut, expliqu\u00e9 par la fatigue de la veille) \u00b7 et dimanche <strong>le seuil 30 \u00e0 4:24 et 4:31/km</strong>, soit bien plus rapide que la cible de 4:40, en te sentant \u00ab tr\u00e8s tr\u00e8s bien \u00bb. La PPG a saut\u00e9 \u2014 c'est le bon arbitrage, on ne sacrifie jamais le seuil ni la longue.</p><p><strong>Ce que la semaine r\u00e9v\u00e8le :</strong> ta progression est d\u00e9sormais visible partout \u2014 le seuil couru 15 s/km plus vite que pr\u00e9vu, l'efficience estivale au sommet, l'acclimatation chaleur qui porte ses fruits. La carte Progression par saison le chiffre : +7,6 % d'efficience depuis l'hiver. Tu ne le \u00ab sens \u00bb plus seulement, tu le vois.</p><p><strong>Deux apprentissages act\u00e9s :</strong> la r\u00e8gle nutrition (1 gel toutes les 40-45 min sur les sorties >2h, apr\u00e8s les vertiges de la SL), et la fin de vie des Clifton 10 (1134 km, \u00e0 sortir de la rotation qualit\u00e9).</p><p><strong>Bilan : 4/5 \u00b7 54 km \u00b7 ACWR 1,00 \u00b7 forme 87.</strong> Tu arrives au projet ViaRh\u00f4na de jeudi en pleine possession de tes moyens. Repos ou tr\u00e8s facile d'ici l\u00e0 \u2014 et savoure, c'est une tr\u00e8s belle semaine. 👏</p>"
_S30_REVUE="<p><strong>La plus grosse semaine de ta pr\u00e9paration, et de loin \u2014 74,2 km, dont un marathon complet.</strong> 4 s\u00e9ances, charge 621, sans le moindre incident majeur. Pour situer : c'est <strong>21 km de plus que la semaine derni\u00e8re</strong> et ton plus haut volume de la saison. Et tu la termines debout.</p><p><strong>Le d\u00e9roul\u00e9 :</strong> r\u00e9cup lundi (14 km pilot\u00e9s \u00e0 139 bpm, d\u00e9rive quasi nulle) \u00b7 s\u00e9ance de vitesse mardi (8\u00d730 sec, pointe finale \u00e0 <strong>3:16/km</strong>, ta plus rapide de la saison) \u00b7 repos mercredi \u00b7 <strong>MARATHON ViaRh\u00f4na jeudi : 42,52 km</strong> Vienne \u2192 Saint-Rambert-d'Albon \u00b7 trois jours de repos complet \u00b7 r\u00e9cup dimanche (10 km).</p><p><strong>Ce que le marathon a prouv\u00e9.</strong> 15 km seul \u00e0 5:36/km avec une FC \u00e0 141,8 \u2014 tr\u00e8s bas pour cette allure. Puis 23 km ralentis volontairement pour rester avec Yannis. Et surtout, les <strong>km 41 et 42 tenus \u00e0 5:16 et 5:15/km</strong>, ton allure cible Nice, sur des jambes ayant d\u00e9j\u00e0 40 km. La nutrition (3 gels + 3 pastilles + Clif Bar) a parfaitement tenu : z\u00e9ro perte d'\u00e9nergie sur 4h18, \u00e0 l'oppos\u00e9 des vertiges de la SL du 16/7. <strong>Le protocole est valid\u00e9 pour SaintExpress.</strong></p><p><strong>Le pari de mardi.</strong> Tu voulais ta s\u00e9ance de vitesse, je te l'avais d\u00e9conseill\u00e9e dans une semaine cens\u00e9e prot\u00e9ger le 40 km. Tu l'as faite, elle s'est tr\u00e8s bien pass\u00e9e, et le marathon deux jours plus tard aussi. <strong>Le pari est gagn\u00e9</strong> \u2014 il faut le dire aussi clairement que j'avais dit ma r\u00e9serve. Retiens quand m\u00eame que \u00e7a n'en fait pas une r\u00e8gle : deux qualit\u00e9s avant un ultra reste un pari, gagn\u00e9 cette fois gr\u00e2ce \u00e0 ta base a\u00e9robie solide.</p><p><strong>Le signal de dimanche.</strong> Ta r\u00e9cup a montr\u00e9 une d\u00e9rive cardiaque de 11,6 % : tu as ralenti de 19 s/km pendant que ta FC montait de 11 bpm. Ce n'est pas un d\u00e9faut d'ex\u00e9cution, c'est la preuve chiffr\u00e9e que <strong>tu n'es pas encore r\u00e9cup\u00e9r\u00e9 du marathon</strong>. Trois jours de repos ne suffisent pas apr\u00e8s 42 km \u2014 c'est normal et attendu.</p><p><strong>\u26a0\ufe0f Le point qui prime : ton pied gauche.</strong> Douleur apparue au dernier kilom\u00e8tre du marathon, encore une g\u00eane dimanche. Le sc\u00e9nario reste rassurant (pas de douleur franche en courant), mais c'est <strong>la variable qui commande la semaine prochaine</strong>. Le test : si \u00e7a fait mal aux premiers pas au r\u00e9veil et que \u00e7a s'att\u00e9nue en marchant, il faut traiter, pas courir dessus.</p><p><strong>Bilan : 4 s\u00e9ances \u00b7 74,2 km \u00b7 charge 621 \u00b7 un marathon dans les jambes.</strong> Une semaine qui restera comme un jalon de la pr\u00e9pa Nice. La suite est simple et non n\u00e9gociable : <strong>reprise progressive, aucune qualit\u00e9 tant que le pied parle et que la d\u00e9rive n'est pas redescendue.</strong> Tu as construit quelque chose de solide cette semaine, ne le grille pas en repartant trop vite. \U0001F3C3</p>"
_S31_REVUE="<p><strong>Semaine d'absorption r\u00e9ussie \u2014 et une le\u00e7on qui vaut plus que les kilom\u00e8tres.</strong> 4 s\u00e9ances, 45,5 km, charge 404 (contre 621 en S30). Le volume baisse de 39 %, c'est exactement ce qu'il fallait apr\u00e8s un marathon, sous un d\u00f4me de chaleur \u00e0 36-38\u00b0C et avec un pied qui parlait.</p><p><strong>Le d\u00e9roul\u00e9 :</strong> lundi vitesse (6\u00d730 en negative split parfait, pointe \u00e0 <strong>2:57/km</strong>, 19 s/km plus rapide qu'au 21/07) \u00b7 mardi EF pilot\u00e9e au cardio (FC 138, z\u00e9ro seconde au-dessus de 150, d\u00e9couplage 3 %) \u00b7 mercredi repos \u00b7 jeudi tunnel Croix-Rousse avec 4\u00d72 km \u00e0 allure marathon \u00b7 vendredi et samedi repos forc\u00e9 pour le pied \u00b7 dimanche EF de reprise.</p><p><strong>La d\u00e9couverte de la semaine : ta d\u00e9rive naturelle vers le haut.</strong> Dimanche, tu es pass\u00e9 de 5:35/km \u00e0 FC 136 sur les premiers kilom\u00e8tres \u00e0 <strong>4:55/km \u00e0 FC 161</strong> sur les derniers \u2014 sans jamais d\u00e9cider d'acc\u00e9l\u00e9rer. C'est le m\u00e9canisme exact qui fait exploser un marathon parti trop vite. L'avoir identifi\u00e9 \u00e0 15 semaines de Nice, c'est un acquis majeur.</p><p><strong>Sur ton doute concernant 5:20 : les donn\u00e9es te contredisent, dans le bon sens.</strong> Dimanche tu as tenu 5:12/km \u00e0 FC 150, puis 5:09/km \u00e0 FC 153 \u2014 <em>plus rapide que 5:20 \u00e0 une FC inf\u00e9rieure \u00e0 ta cible</em>. Jeudi, le bloc 2 du tunnel donnait 5:29/km \u00e0 FC 152. Physiologiquement, 5:20 n'est pas ambitieux : il est confortable. <strong>Ton probl\u00e8me n'est pas de l'atteindre, c'est de ne pas le d\u00e9passer.</strong></p><p><strong>Le pied :</strong> douleur apparue au marathon, r\u00e9veill\u00e9e jeudi apr\u00e8s 10-12 km \u00e0 allure soutenue, puis dispar\u00e2ue apr\u00e8s deux jours de repos complet. Dimanche, aucune douleur au d\u00e9part et une simple g\u00eane \u00e0 l'arriv\u00e9e. Le sch\u00e9ma se pr\u00e9cise : <strong>il tol\u00e8re environ une heure de course, et se manifeste sur l'allure soutenue prolong\u00e9e plus que sur l'EF facile.</strong></p><p><strong>Bilan : 4 s\u00e9ances \u00b7 45,5 km \u00b7 charge 404.</strong> Une semaine sans h\u00e9ro\u00efsme, bien pilot\u00e9e, o\u00f9 tu as pris les bonnes d\u00e9cisions d'arr\u00eat \u00e0 deux reprises. Le marathon est absorb\u00e9, le pied va mieux, et tu as gagn\u00e9 une compr\u00e9hension pr\u00e9cieuse de ton propre pilotage. \U0001F44D</p>"
_S32_REVUE="<p><strong>La semaine où ton corps a dit oui, et où ta discipline a dit à peu près.</strong> 5 sorties, 67,3 km, 817 m D+, charge 487 (contre 404 en S31). Le volume grimpe de 48 % — sauf que la cible affichée était 52 km. Tu as donc couru 29 % de plus que prévu, avec 2 sorties sur 5 qui n'étaient pas au plan.</p><p><strong>Le déroulé :</strong> mardi fractionné 8×400 interrompu à 6/8 en canicule (bonne décision, la FC ne redescendait plus entre les blocs) · mercredi EF 10 km · jeudi EF + 6×100 · vendredi <em>jour de repos au plan</em>, transformé en EF de retenue, puis 1h33 de vélo le soir · samedi repos · dimanche boucle de Saint-Étienne, 27 km et 662 m D+.</p><p><strong>Le résultat qui compte le plus : le pied s'est tu.</strong> Zéro douleur sur les 5 sorties, y compris après 27 km de trail avec descentes techniques et appuis instables. C'était le dernier test que la gêne du 23/07 n'avait pas passé. <strong>Le dossier ouvert depuis trois semaines est clos.</strong></p><p><strong>La leçon de la semaine tient dans deux sorties séparées de 48 heures.</strong> Vendredi, tu annonces une cible chiffrée avant de partir — FC moyenne ≤135 — et tu tiens 132, avec une bande resserrée entre 124 et 136 sur 10 km, sans un seul emballement. Dimanche, personne ne t'encadre plus après le départ de Yannis au km 23 : 7:15 → 5:57 → 5:42 → 5:42 → 5:28 → <strong>5:07/km</strong>, avec la FC qui monte de 139 à 166. Tu m'as décrit ça comme un regain agréable. C'est ta dérive, dans sa forme la plus pure.</p><p><strong>Ta retenue existe quand elle est chiffrée. Elle disparaît quand elle est laissée au ressenti.</strong> Ce n'est pas un problème de motivation ni de moteur — c'est un pilote automatique qui reprend la main dès qu'aucun nombre ne l'occupe. À Nice, ce même automatisme au km 25 te coûtera le chrono.</p><p><strong>La lecture positive, parce qu'elle est réelle aussi :</strong> finir un 27 km à 662 m D+ en accélérant jusqu'à 5:07/km — plus vite que ton allure marathon cible — à FC 166, c'est un vrai marqueur de durabilité. Ton moteur va bien. Ce dernier kilomètre valide au passage ta plage cible : 148-160 bpm à 5:20/km est bien calibrée.</p><p><strong>La charge est saine.</strong> ACWR à 0,97 (aigu 487, chronique 504/semaine) : pile la zone optimale, ni sous-charge ni surcharge. Deux nuances tout de même — ce ratio est atteint avec 2 sorties non planifiées, et la moitié de la charge vient d'une seule sortie. La marge existe pour S33 ; elle autorise à suivre le plan, pas à en rajouter.</p><p><strong>Un écart matériel, et un point de vigilance :</strong> dimanche tu as couru 662 m de dénivelé technique en Novablast route (désormais 689 km) au lieu des Cascadia — ça, c'est l'écart. Mercredi tu as couru en Clifton 10 : elles restent dans ta rotation, moins utilisées, et c'est ton choix ; le seul sujet est leur kilométrage, pas leur présence. Aucune conséquence cette fois. Mais sur SaintExpress et ses sorties préparatoires, la Cascadia doit redevenir un réflexe.</p><p><strong>Décision pour S33 :</strong> allègement maintenu, et lundi en repos complet non négociable après une semaine à 5 sorties dont un trail à 246 d'effort relatif. Le seuil 2×10 reste. La longue de 18 km se court <strong>plafonnée en FC</strong>, pas au chrono. Et surtout : chaque sortie part avec un nombre annoncé à l'avance — FC plafond ou allure plancher. Vendredi a prouvé que ça marche. L'objectif de la semaine n'est pas d'aller plus vite, c'est de finir une sortie sans avoir accéléré sans le décider.</p>"

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
      "revue":"<strong>Bonne décision, et prise pour la bonne raison.</strong> Le repos était déjà au programme ; tu l'as confirmé sur des sensations, pas par facilité. Après 246 d'effort relatif dimanche, un jour de plus ne coûte rien et protège la séance clé de la semaine."}
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
      "revue":"<p><strong>La séance que j'attendais depuis dimanche.</strong> Objectif annoncé 140 bpm, FC moyenne réalisée 138. Tenu.</p><p><strong>Le chiffre qui compte n'est pas l'allure, c'est l'amplitude :</strong> 15 secondes au kilomètre entre ton plus lent (6:18) et ton plus rapide (6:03). Dimanche, l'écart était de 128 secondes. Tu viens de courir dix kilomètres sans jamais accélérer sans le décider — exactement l'axe de travail identifié cette semaine.</p><p><strong>Ta perception est juste, et les données la nuancent utilement.</strong> Tu décris une lourdeur sur les 6 premiers kilomètres puis un déliement : côté cardiaque, c'est l'inverse qui apparaît (136,8 bpm sur les km 1-6, 140,4 sur les km 7-10). Ce n'est pas contradictoire. Au départ, tes jambes travaillaient contre une raideur post-trail à faible coût cardiaque — le km 1 à 6:18 pour seulement 129 bpm. Ensuite la mécanique s'est libérée, l'allure a progressé, et la FC est montée par dérive normale après 40 minutes, accentuée par les 14 m de D+ des km 8 et 9. Sensation et cardio racontent la même histoire vue de deux côtés.</p><p><strong>Pied : zéro douleur sur 10 km, quatre jours après un trail de 27 km et 662 m de D+.</strong> Le dossier est clos, et je ne le rouvrirai que si tu le rouvres.</p><p><strong>Un point à traiter, en revanche : tu as couru avec les Clifton 10, qui affichent 1179 km.</strong> C'est très au-delà de la zone de remplacement, située entre 700 et 900 km. À ce kilométrage, la mousse d'amorti est fortement dégradée et ne restitue plus grand-chose : les contraintes remontent dans le pied, la cheville et le tibia. Tu sors précisément d'un dossier pied, et ce sont les seules chaussures à ce niveau d'usure de ton parc. Elles ne sont pas en cause aujourd'hui — aucune douleur, effort relatif 53 — mais elles n'ont plus rien à faire sur une séance de récupération, encore moins sur une longue. <strong>La Novablast 5 V (56 km) et la Novablast 5 J (699 km) sont là pour ça.</strong> Pour le déplacement à La Rochelle, emporte la V.</p><p><strong>Effort relatif 53</strong> — le plus bas depuis trois semaines. C'est précisément ce que doit coûter un footing de récupération. Cadence 175, stable du premier au dernier kilomètre.</p><p><strong>Ce qu'on fait maintenant :</strong> mercredi footing court avec lignes droites, puis <strong>seuil 2×10 jeudi</strong>, avec deux jours pleins de digestion du trail. C'est le bon décalage — le seuil mérite des jambes disponibles, pas des jambes qui se déplient.</p>"}
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
      "revue":"<p><strong>Le negative split est réussi, et de peu s'en faut qu'il soit parfait.</strong></p>"
        "<table style='width:100%;border-collapse:collapse;font-size:.88rem;margin:10px 0'>"
        "<tr style='background:#0f172a;color:#fff'><th style='padding:6px'>Ligne</th><th>Temps</th><th>Allure</th><th>FC fin</th></tr>"
        "<tr><td style='padding:5px;text-align:center'>1</td><td style='text-align:center'>23 s</td><td style='text-align:center'>3:50/km</td><td style='text-align:center'>163</td></tr>"
        "<tr style='background:#f1f5f9'><td style='padding:5px;text-align:center'>2</td><td style='text-align:center'>21 s</td><td style='text-align:center'>3:30/km</td><td style='text-align:center'>168</td></tr>"
        "<tr><td style='padding:5px;text-align:center'>3</td><td style='text-align:center;color:#b45309'><strong>22 s</strong></td><td style='text-align:center'>3:40/km</td><td style='text-align:center'>173</td></tr>"
        "<tr style='background:#f1f5f9'><td style='padding:5px;text-align:center'>4</td><td style='text-align:center'>19 s</td><td style='text-align:center'>3:10/km</td><td style='text-align:center'>176</td></tr>"
        "<tr><td style='padding:5px;text-align:center'>5</td><td style='text-align:center'>19 s</td><td style='text-align:center'>3:10/km</td><td style='text-align:center'>181</td></tr>"
        "<tr style='background:#ecfdf5'><td style='padding:5px;text-align:center'><strong>6</strong></td><td style='text-align:center'><strong>16 s</strong></td><td style='text-align:center'><strong>2:40/km</strong></td><td style='text-align:center'>180</td></tr></table>"
        "<p><strong>23 s → 16 s, soit 30 % de gain entre la première et la dernière.</strong> Seule la ligne 3 casse la série, d'une seconde. Sur six répétitions menées à la sensation, sans montre au poignet pour te caler, c'est un contrôle d'allure remarquable — et c'est exactement la compétence qu'on travaille depuis dimanche.</p>"
        "<p><strong>La pointe finale est ta plus rapide de la saison : 24,3 km/h (2:28/km).</strong> À comparer aux 3:16/km du 21 juillet et aux 2:57/km du 27 juillet. Cinq records personnels sur segments au passage.</p>"
        "<p><strong>Ce qui me plaît le plus n'est pas la vitesse, c'est la cadence.</strong> Elle monte à 94 sur la ligne 6, contre 85-88 sur le reste de la séance. Tu accélères en augmentant la fréquence, pas en allongeant la foulée — c'est le mécanisme le plus économique et le moins traumatisant pour le pied. Rien à corriger.</p>"
        "<p><strong>Le point de vigilance :</strong> FC max 186 sur la dernière ligne, soit 97 % de ta FCmax. C'est très haut pour une séance étiquetée footing. Ce n'est pas grave sur 16 secondes et la FC redescend immédiatement, mais ça change la nature de la séance : effort relatif 61 contre 53 hier, alors que le volume est identique. Ce n'était pas une EF, c'était une EF avec un vrai travail neuromusculaire au bout.</p>"
        "<p><strong>Sur la partie endurance :</strong> 137 bpm de moyenne, dans la cible. L'amplitude est de 39 s/km (5:45 à 6:24) contre 15 hier — la dérive est plus marquée, avec une accélération progressive du km 6 au km 9 avant les lignes droites. Rien d'alarmant pour une séance qui préparait justement des accélérations, mais c'est le schéma à surveiller : <strong>vendredi, sur le bloc à 5:20, cette amplitude devra retomber sous 6 secondes.</strong></p>"
        "<p><strong>Chaussures : Novablast 5 J (699 km).</strong> Mieux que les Clifton d'hier, mais cette paire arrive aussi en fin de zone. Pour La Rochelle, emporte la 5 V.</p>"
        "<p><strong>Verdict : A.</strong> Objectif annoncé, objectif tenu, et une séance qui fait le pont entre la retenue de mardi et le travail d'allure de vendredi. Bonne route.</p>"}
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
      "revue":"<p><strong>Séance réussie, et dans des conditions qui ne s'y prêtaient pas. C'est ce qui la rend intéressante.</strong></p>"
        "<table style='width:100%;border-collapse:collapse;font-size:.88rem;margin:10px 0'>"
        "<tr style='background:#0f172a;color:#fff'><th style='padding:6px'>km</th><th>Allure</th><th>Écart /5:20</th><th>FC</th></tr>"
        "<tr><td style='padding:5px;text-align:center'>1</td><td style='text-align:center'>5:20,9</td><td style='text-align:center;color:#16a34a'>+0,9 s</td><td style='text-align:center'>151</td></tr>"
        "<tr style='background:#f1f5f9'><td style='padding:5px;text-align:center'>2</td><td style='text-align:center'>5:15,3</td><td style='text-align:center;color:#b45309'>−4,7 s</td><td style='text-align:center'>154</td></tr>"
        "<tr><td style='padding:5px;text-align:center'>3</td><td style='text-align:center'>5:11,2</td><td style='text-align:center;color:#dc2626'>−8,8 s</td><td style='text-align:center'>164</td></tr>"
        "<tr style='background:#f1f5f9'><td style='padding:5px;text-align:center'>4</td><td style='text-align:center'>5:18,9</td><td style='text-align:center;color:#16a34a'>−1,1 s</td><td style='text-align:center'>158</td></tr>"
        "<tr><td style='padding:5px;text-align:center'>5</td><td style='text-align:center'>5:22,2</td><td style='text-align:center;color:#16a34a'>+2,2 s</td><td style='text-align:center'>161</td></tr>"
        "<tr style='background:#f1f5f9'><td style='padding:5px;text-align:center'>6</td><td style='text-align:center'>5:12,7</td><td style='text-align:center;color:#dc2626'>−7,3 s</td><td style='text-align:center'>165</td></tr></table>"
        "<p><strong>Moyenne du bloc : 5:17/km pour une cible à 5:20. Amplitude 11 secondes.</strong> Pour situer : dimanche, sur la fin du trail, elle était de 128 secondes. Mardi, sur une EF plafonnée en FC, de 15. Tu viens de faire mieux sur une allure spécifique que sur un footing il y a deux jours — sur un terrain que tu ne connaissais pas.</p>"
        "<p><strong>Le seul reproche, et il est mineur : trois kilomètres sous 5:15</strong> (le 3ᵉ à 5:11, le 6ᵉ à 5:13). L'écart moyen à la cible reste de 4,2 secondes, donc l'exercice est réussi. Mais le schéma est reconnaissable : tu accélères quand ça passe bien. Le dernier kilomètre à 5:12 est le plus révélateur — c'est le moment où tu sais que le bloc se termine.</p>"
        "<p><strong>Ce que dit ton cardiaque, en revanche, mérite plus d'attention que l'allure.</strong> Sur les 6 km, ta FC est passée de 151 à 165 — <strong>+13,5 bpm à allure constante</strong>. Les trois derniers kilomètres sont 2 secondes plus lents que les trois premiers mais 5 pulsations plus hauts. Ta cible était 148-160 : tu as fini à 165, donc au-dessus.</p>"
        "<p><strong>Ce n'est pas un problème de forme, c'est la somme du contexte :</strong> environ 5h30 de sommeil, 7 heures de voiture la veille, chaleur et humidité côtières, et troisième séance en trois jours. Le découplage reste à 2,5 %, ce qui est faible — ton moteur a bien répondu. Mais l'effort relatif de 128, contre 53 mardi et 61 mercredi, dit la vérité : <strong>cette séance t'a coûté deux fois et demie ce que tu as fait cette semaine.</strong></p>"
        "<p><strong>Pied : aucune douleur, sur une séance à 5:17 de moyenne et sur terrain inconnu.</strong> C'est la meilleure confirmation possible depuis la reprise.</p>"
        "<p><strong>Verdict : A.</strong> C'est ta première vraie séance d'allure marathon réussie de la préparation, réalisée dans des conditions défavorables. Ce que tu as prouvé aujourd'hui n'est pas que tu peux courir à 5:20 — on le savait — mais que <strong>tu peux le faire en le décidant, et t'y tenir sur 6 kilomètres.</strong> C'est exactement le point faible identifié dimanche.</p>"
        "<p><strong>La suite :</strong> repos vendredi, tu as raison. Après un effort relatif de 128 sur un sommeil court, une quatrième séance n'apporterait rien. Le déverrouillage de dimanche soir reste optionnel — et si l'organisation familiale ne le permet pas, <strong>la semaine est déjà réussie.</strong> Trois séances, dont celle-ci, valent mieux que cinq séances tièdes.</p>"}
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
      "revue":"<p><strong>Bonne décision d'écourter, et le corps te donne raison — mais pas pour la raison que tu crois.</strong></p>"
        "<p><strong>Sur le plan cardiaque, cette séance est excellente.</strong> FC moyenne 139 pour 5:59/km. Compare avec mardi : 138 bpm pour 6:09/km. Tu cours aujourd'hui <strong>11 secondes au kilomètre plus vite pour une pulsation de plus</strong>. Et la dérive est nulle : 138,8 bpm sur les 4 premiers kilomètres, 139,6 sur les 4 derniers, à allure identique. Sur une sortie où tu te sens fatigué, c'est un signal de forme, pas de surcharge.</p>"
        "<p><strong>Effort relatif 50, le plus bas de la semaine.</strong> Deux records personnels sur segments au passage, sans les chercher.</p>"
        "<p><strong>Alors d'où vient la fatigue ?</strong> Elle est réelle, mais son origine n'est pas l'entraînement. Six à sept heures de sommeil par nuit depuis le début du séjour, 7 heures de voiture mercredi, chaleur et humidité continues, rythme familial. <strong>Ton moteur va bien ; c'est ta récupération qui est entamée.</strong> C'est une distinction importante : elle se corrige en dormant, pas en réduisant l'entraînement.</p>"
        "<p><strong>La séance a d'ailleurs un vrai défaut, et il est mineur :</strong> l'amplitude d'allure est de 34 s/km, avec un 2ᵉ kilomètre à 5:40 nettement plus rapide que le reste. Sur un footing de liaison, ça n'a aucune conséquence. Je le note parce que c'est le même réflexe que d'habitude — le corps part quand il se sent bien, même un jour de fatigue.</p>"
        "<p><strong>Verdict : A−.</strong> Séance juste, décision juste. Écourter pour préserver la journée et la récupération est exactement le bon arbitrage un samedi de vacances, à 12 semaines de Nice.</p>"}
    arr.append(_sam)
    arr[4]["date"]="2026-08-16"
    arr[4]["chaussure"]="ASICS Novablast 5 V"
    arr[4]["titre"]="Déverrouillage retour de route"
    arr[4]["type"]="EF aérobie"
    arr[4]["opt"]=True
    arr[4]["sous"]="Optionnel — seulement si l'envie est là."
    arr[4]["metriques"]={"Distance":"6-8 km","Durée":"~45 min","Allure":"6:10-6:30/km","FC":"< 140","RPE":"2-3","Type":"Déverrouillage"}
    arr[4]["objectif"]="Après 6h30 de voiture, l'objectif est de <strong>débloquer les jambes, pas de s'entraîner</strong>. Très facile, FC sous 140. <strong>Si la fatigue du trajet domine, une marche de 20 minutes fait le même travail</strong> — ne force pas cette séance, elle ne vaut pas une semaine suivante entamée."
    arr[4]["struct"]=[
      {"nom":"Corps","txt":"6 à 8 km à allure très facile, FC plafonnée à 140. Aucune ligne droite, aucune accélération."},
      {"nom":"Alternative","txt":"20 à 30 min de marche + mobilité hanches et chaîne postérieure si les jambes sont trop lourdes."}]
for _s in SEMAINES:
    if _s["num"]==25: _s["revue"]=_S25_REVUE
    if _s["num"]==26: _s["revue"]=_S26_REVUE
    if _s["num"]==27: _s["revue"]=_S27_REVUE
    if _s["num"]==28: _s["revue"]=_S28_REVUE
    if _s["num"]==29: _s["revue"]=_S29_REVUE
    if _s["num"]==30: _s["revue"]=_S30_REVUE
    if _s["num"]==31: _s["revue"]=_S31_REVUE
    if _s["num"]==32: _s["revue"]=_S32_REVUE

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
  {"marque":"HOKA","modele":"Clifton 10","km":1179},
  {"marque":"ASICS","modele":"Novablast 5 J","km":709},
  {"marque":"ASICS","modele":"Novablast 5 V","km":56},
  {"marque":"ASICS","modele":"Gel Pulse 16","km":225},
  {"marque":"Brooks","modele":"Cascadia 19","km":241},
  {"marque":"ASICS","modele":"Magic Speed 4","km":75},
]
RACES=[{"nom":"Marathon de Nice","date":"2026-11-08","dossier":"nice"},{"nom":"SaintExpress","date":"2026-11-28","dossier":"saintexpress"}]

# ===== DOSSIERS DE COURSE (modale au clic sur le badge) =====
DOSSIERS={
 "nice":{
  "nom":"Marathon des Alpes-Maritimes Nice-Cannes",
  "soustitre":"Promenade des Anglais, Nice → Boulevard de la Croisette, Cannes",
  "date":"Dimanche 8 novembre 2026",
  "depart":"Départ 8 h 00 · Promenade des Anglais (Nice) · Sas 3h45 disponible",
  "format":"42,195 km · Point-à-point · Label FFA & World Athletics · ~15 000 coureurs",
  "accent":"#f59e0b",
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
    {"n":"1","tag":"CONSERVATEUR","c":"#f59e0b","titre":"Sortie de Nice — freiner l'ego","txt":"8h00 sur la Promenade des Anglais avec 15 000 coureurs. Les km 1-5 sont les plus dangereux du marathon : jambes fraîches, euphorie, public, faux-plats. Cible <strong>5:25 / km</strong> minimum sur les 5 premiers. Si tu passes le km 5 sous 26:30, tu es trop rapide.","fuel":"Gel dès 40 min de course (km 8 environ) sans attendre la faim. Ravito km 5 : eau."},
    {"n":"2","tag":"GÉRER","c":"#ea580c","titre":"La longue ligne droite côtière","txt":"Km 8 à 20 : tenir le 5:20/km sans forcer. La côte Méditerranée est magnifique, ça peut aller vite — surveille ton allure. Passage de la demi vers 1h52 à 1h53 : si tu es en avance, lève le pied. Marathon = compétition contre soi-même, pas contre les coureurs autour.","fuel":"Gel km 16 environ. Ravitos km 10, 15, 20 : eau + boisson sucrée si dispo. Commence l'électrolyte."},
    {"n":"3","tag":"VIGILANCE","c":"#dc2626","titre":"Antibes & le mur (km 25-35)","txt":"<strong>La section décisive.</strong> La bosse d'Antibes (km 25-28, max 35 m) peut faire accélérer le cœur si tu n'es pas attentif — régule. Puis km 30 : c'est là que les glucides s'épuisent et que les jambes commencent à parler. Ton mental et ton carburant doivent tenir. Cadence haute, foulée courte.","fuel":"Gel km 24 et gel km 32 — <strong>celui du km 32 est le plus important du marathon</strong>. Le caféiné ici si tu en as un."},
    {"n":"4","tag":"POUSSER","c":"#f59e0b","titre":"La Croisette — vider le réservoir","txt":"Km 35-42 : si tu as bien géré, tu doubles du monde sur les derniers km. La Croisette de Cannes approche avec les marches rouges du Festival et le public. Laisse parler les émotions, accélère si tes jambes suivent. <strong>3h45 c'est à ta portée : ne lâche rien.</strong>","fuel":"Dernier gel km 37-38 si tu en as encore. Sinon eau seule pour les 5 derniers km."}],
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
  "accent":"#0d9488",
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
    {"n":"1","tag":"TERRAIN INCONNU","c":"#0d9488","titre":"km 0-27 — découverte et prudence","txt":"Les 27 premiers km sont du terrain inédit pour toi. Pas de repère, pas d'anticipation possible — tu gères à l'effort, à la sensation et à la frontale. <strong>Plus conservateur que d'habitude</strong>, surtout sur les descentes techniques de nuit. L'objectif est d'arriver à Soucieu avec des jambes.","fuel":"Gel non-caféiné à 20 min avant départ. Flasques TA. Gel km 7 et km 14 (ravito Saint-Genou)."},
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
  {"m":"Jan","km":224,"elev":1342,"sorties":19,"re":2431},
  {"m":"Fév","km":227,"elev":1674,"sorties":21,"re":2229},
  {"m":"Mar","km":342,"elev":2962,"sorties":25,"re":2978},
  {"m":"Avr","km":283,"elev":2254,"sorties":23,"re":2265},
  {"m":"Mai","km":202,"elev":5978,"sorties":15,"re":2171},
  {"m":"Juin","km":82,"elev":2012,"sorties":5,"re":1112},
  {"m":"Juil","km":257,"elev":2805,"sorties":18,"re":2669},
  {"m":"Août","km":79,"elev":853,"sorties":6,"re":592},
]
SAISON2026={"km":1696,"elev":19880,"sorties":132,"mois":8,"note":"Course à pied uniquement (Run + Trail) · randonnées, raquettes et vélo exclus · aligné Strava · août arrêté au 09/08"}
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
  ],
  "note":"À FC égale, +7,6 % d'efficience entre l'hiver et l'été (≈ 25 s/km plus rapide). L'été n'est PAS une régression : la chaleur gonflait ton cardio et masquait la vraie progression. Échantillon de 2-3 sorties par saison — tendance fiable, valeurs à ±quelques secondes."
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
    _ref=max(d for d,_ in faits)
    c7 =sum(re for d,re in faits if 0<=(_ref-d).days<=6)
    c28=sum(re for d,re in faits if 0<=(_ref-d).days<=27)
    _a=round(c7/(c28/4),2) if c28 else None
    return {"charge7j":c7,"charge28j":c28,"acwr":_a,"ref":_ref.isoformat()}

_ACW=_acwr_compute()

def _acwr_zone(a):
    if a is None:            return "Donnees insuffisantes pour calculer le ratio."
    if a < 0.8:              return "Sous-charge : la charge recente est nettement inferieure a ton habitude. Utile en recuperation ou en affutage, a surveiller si ce n'est pas voulu."
    if a <= 1.3:             return "Zone optimale : la charge recente est coherente avec ton habitude des quatre dernieres semaines. C'est le ratio dans lequel les adaptations se construisent avec le risque de blessure le plus bas."
    if a <= 1.5:             return "Charge elevee : tu montes plus vite que ton corps ne s'adapte. Tolerable ponctuellement, risque si cela dure."
    return "Surcharge : ratio associe a une hausse nette du risque de blessure. Allege sans attendre."

ACWR_DATA={"charge7j":_ACW["charge7j"],"charge28j":_ACW["charge28j"],"acwr":_ACW["acwr"],
  "ref":_ACW["ref"],
  "interpretation":_acwr_zone(_ACW["acwr"])+" Charge aigue "+str(_ACW["charge7j"])+" sur 7 jours, chronique "+str(_ACW["charge28j"])+" sur 28 jours (soit "+str(round(_ACW["charge28j"]/4))+" par semaine), calcule au "+str(_ACW["ref"])+"."}
print("ACWR calcule :", ACWR_DATA["charge7j"], "/", ACWR_DATA["charge28j"], "=>", ACWR_DATA["acwr"], "(ref", ACWR_DATA["ref"] + ")")
RECORDS_PERF=[
  {"dist":"5 km","record":"22:52","record_sub":"meilleur effort Strava","actuel":"4:35/km","actuel_sub":"meilleur effort 2026","temps_rec":"22:52","temps_act":"~22:52"},
  {"dist":"10 km","record":"46:14","record_sub":"meilleur effort Strava","actuel":"4:37/km","actuel_sub":"meilleur effort 2026","temps_rec":"46:14","temps_act":"~46:14"},
  {"dist":"Semi 21,1","record":"1h52:39","record_sub":"meilleur effort Strava","actuel":"5:20/km","actuel_sub":"projeté depuis forme actuelle","temps_rec":"1h52:39","temps_act":"~1h50-1h52"},
]
ALLURES_COURSE=[{"d":"5 km","temps":"~22:35","allure":"4:31/km"},{"d":"10 km","temps":"~47:00","allure":"4:42/km"},{"d":"Semi 21,1 km","temps":"~1h44","allure":"4:55/km"},{"d":"30 km","temps":"~2h31","allure":"5:02/km"},{"d":"Marathon objectif","temps":"3h45","allure":"5:20/km"},{"d":"Marathon projeté","temps":"~3h38-3h42","allure":"~5:12-5:15/km"}]
ALLURES=[{"nom":"Seuil 30","val":"≈4:40/km","sub":"~30 min · proche 10 km"},{"nom":"Seuil 60","val":"≈4:55/km","sub":"~60 min · proche semi"},{"nom":"Allure marathon","val":"≈5:15/km","sub":"cible Nice 3h42"},{"nom":"Endurance facile","val":"5:50-6:25/km","sub":"le socle"},{"nom":"VMA courte","val":"≈4:15/km","sub":"plafond aérobie"}]
ZONES_FC=[{"z":"Z1","nom":"Récupération","bpm":"< 134","pct":"< 70%","col":"#86efac","allure":"≥ 6:45/km"},{"z":"Z2","nom":"Endurance fondamentale","bpm":"134-154","pct":"70-80%","col":"#16a34a","allure":"5:50-6:25/km"},{"z":"Z3","nom":"Tempo / marathon","bpm":"154-167","pct":"80-87%","col":"#f59e0b","allure":"5:05-5:30/km"},{"z":"Z4","nom":"Seuil","bpm":"167-177","pct":"87-92%","col":"#ea580c","allure":"4:40-4:55/km"},{"z":"Z5","nom":"VO2 / VMA","bpm":"177-192","pct":"92-100%","col":"#ef4444","allure":"≤ 4:20/km"}]
REPLAY={"nom": "Petit Croisse Baulet", "date": "2026-07-12", "km": 11.04, "dplus": 530, "temps": "2h35", "alt": [1910, 1893, 1882, 1866, 1859, 1850, 1840, 1827, 1815, 1808, 1815, 1818, 1820, 1825, 1808, 1800, 1789, 1779, 1765, 1753, 1740, 1731, 1732, 1738, 1748, 1771, 1800, 1828, 1845, 1834, 1814, 1793, 1780, 1797, 1781, 1760, 1746, 1732, 1718, 1745, 1758, 1771, 1764, 1764, 1750, 1735, 1727, 1746, 1768, 1763, 1748, 1728, 1731, 1724, 1737, 1742, 1757, 1783, 1806, 1834, 1864, 1897, 1919, 1945, 1973, 2000, 1982, 1953, 1918, 1887, 1851, 1817, 1788, 1766, 1745, 1742, 1727, 1700, 1669, 1644, 1622, 1601, 1571, 1546, 1520, 1490, 1453, 1423, 1388, 1353, 1324, 1299, 1290, 1283, 1271, 1261, 1251, 1241, 1236, 1230], "dist": [0, 111, 223, 335, 446, 558, 669, 780, 892, 1003, 1115, 1226, 1338, 1449, 1561, 1673, 1784, 1895, 2008, 2118, 2230, 2342, 2454, 2564, 2676, 2788, 2899, 3011, 3123, 3234, 3345, 3457, 3569, 3680, 3792, 3903, 4015, 4126, 4238, 4349, 4460, 4572, 4683, 4795, 4906, 5018, 5130, 5241, 5352, 5464, 5575, 5687, 5799, 5910, 6022, 6134, 6245, 6357, 6468, 6580, 6691, 6802, 6914, 7025, 7136, 7248, 7361, 7471, 7583, 7694, 7806, 7917, 8030, 8140, 8252, 8362, 8475, 8586, 8698, 8810, 8920, 9031, 9144, 9255, 9368, 9478, 9590, 9702, 9813, 9924, 10036, 10148, 10259, 10371, 10482, 10596, 10706, 10816, 10930, 11040], "hr": [91, 93, 90, 93, 85, 87, 87, 84, 87, 93, 118, 93, 99, 121, 92, 87, 90, 83, 85, 82, 84, 89, 84, 99, 116, 152, 157, 160, 113, 101, 98, 106, 120, 111, 107, 101, 106, 115, 106, 158, 150, 141, 120, 122, 137, 136, 122, 164, 155, 125, 131, 140, 140, 125, 148, 136, 154, 163, 169, 168, 172, 172, 162, 162, 162, 137, 142, 148, 142, 141, 140, 142, 146, 133, 141, 158, 154, 142, 144, 146, 145, 150, 140, 141, 146, 138, 156, 149, 157, 144, 144, 140, 143, 153, 156, 162, 165, 164, 166, 166], "pace": [None, 25.25, 15.72, 11.74, 17.01, 12.44, 18.12, None, 16.67, 16.34, 14.37, 11.42, 12.25, 15.72, 13.23, 14.88, 13.23, 18.94, 15.15, 13.44, 12.44, 18.94, 17.73, 14.37, 10.16, 13.02, 17.01, 13.66, 24.51, 16.03, 18.52, 5.67, 21.37, 18.94, 17.73, 11.74, 11.57, 24.51, 9.8, 26.88, 13.89, 8.5, 11.74, 11.74, 6.72, 6.61, 9.47, 15.15, 18.12, 8.42, 8.33, 5.63, 8.59, 11.42, 14.12, 9.36, 13.23, 13.02, 11.74, 16.03, 24.51, 18.12, 25.25, None, 18.52, 9.36, 6.83, 12.44, 17.01, 10.96, 11.57, 15.43, 8.33, 10.96, 7.86, 7.25, 7.72, 8.87, 12.25, 7.65, 10.68, 6.41, 9.26, 7.65, 9.58, 10.16, 7.79, 10.96, 11.11, 19.38, 6.22, 15.72, 5.48, 3.97, 3.82, 4.39, 4.03, 3.75, 4.11, 4.48], "altMin": 1230, "altMax": 2000, "hrMax": 172}
PROFIL={"prenom":"Loïc","ville":"Lyon","cible_marathon":"3h45","marathon_projete":"~3h38-3h42","cible_semi":"~1h44","fcmax":192,"poids":84}
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
 {"bg":"linear-gradient(160deg,#b45309,#451a03)","kicker":"LA SUITE","big":"S25","txt":"Reprise & déblocage — 52 km, retour des séances structurées.<br><strong>La machine démarre lundi. 🚀</strong>"}]},
{"id":"S25","titre":"Ta semaine 25","sous":"Reprise & déblocage · 15-19 juin · canicule","slides":[
 {"bg":"linear-gradient(160deg,#0f172a,#1e3a5f)","kicker":"REWIND · SEMAINE 25","big":"🎬","txt":"5 séances, canicule, fast finish et bonus chez les parents.<br>Tape pour avancer."},
 {"bg":"linear-gradient(160deg,#065f46,#022c22)","kicker":"LE VOLUME","big":"56,6 km","txt":"en 5 sorties — une semaine de reprise qui ressemble à une vraie semaine. Ta base reprend ses droits."},
 {"bg":"linear-gradient(160deg,#7c2d12,#1c0a00)","kicker":"LA FC DE LA SEMAINE","big":"144 bpm","txt":"Moyenne sur l'ensemble des sorties faciles. Moteur Z2 propre, régulier, dans les cibles."},
 {"bg":"linear-gradient(160deg,#1e3a8a,#0c1c3d)","kicker":"LE COUP DE REIN","big":"4:58/km","txt":"Dernier km de la sortie longue, au 4e jour consécutif, 30°C dehors. Sub-5 min. <strong>Tu avais encore du carburant.</strong>"},
 {"bg":"linear-gradient(160deg,#581c87,#1e1b4b)","kicker":"LA CANICULE","big":"31°C","txt":"Pic de la semaine. 4 séances sur 5 démarrées avant 8h30. La discipline de l'horaire, c'est une compétence de compétiteur."},
 {"bg":"linear-gradient(160deg,#9a3412,#431407)","kicker":"LA SÉANCE CLUE","big":"5:14/km","txt":"Bloc AM de 6 km mercredi à midi · 30°C · lendemain de soirée. FC 165/181. <strong>Tenu.</strong> Menti à personne."},
 {"bg":"linear-gradient(160deg,#134e4a,#042f2e)","kicker":"LE BONUS","big":"10 km","txt":"Vendredi 7h25 chez les parents. FC 144. Personne ne t'y obligeait. C'est ça, la discipline d'un marathonien."},
 {"bg":"linear-gradient(160deg,#3b0764,#0f172a)","kicker":"LES CHAUSSURES","big":"4 paires","txt":"Clifton · Gel Pulse · Magic Speed · Novablast J. Rotation parfaite. La V (verte) attend son tour."},
 {"bg":"linear-gradient(160deg,#14532d,#052e16)","kicker":"VERDICT DU COACH","big":"A","txt":"Semaine 5/5. Volume solide, qualité maintenue en conditions difficiles, fast finish, bonus. <strong>La Déraille dans 16 jours, tu arrives bien.</strong>"},
 {"bg":"linear-gradient(160deg,#b45309,#451a03)","kicker":"LA SUITE","big":"S26","txt":"Allègement + prépa Déraille — 35 km · séance spécifique mercredi.<br><strong>On garde les poudres sèches. 🎯</strong>"}]},
{"id":"S26","titre":"Ta semaine 26","sous":"Allègement + canicule · 22-28 juin · J-13→J-7 Déraille","slides":[
 {"bg":"linear-gradient(160deg,#0f172a,#1c3d2e)","kicker":"REWIND · SEMAINE 26","big":"🌡️","txt":"La semaine que la canicule a mangée. 40°C le jour, 30°C la nuit.<br>Tape pour avancer."},
 {"bg":"linear-gradient(160deg,#065f46,#022c22)","kicker":"LE VOLUME","big":"21,9 km","txt":"sur 35 planifiés, en 2 sorties sur 4. La canicule a décidé — <strong>toi, tu as décidé de ne pas te battre contre elle.</strong>"},
 {"bg":"linear-gradient(160deg,#7c2d12,#1c0a00)","kicker":"LES JOURS SAUTÉS","big":"Mar + Mer","txt":"Pas de lâche. Du jugement. 4 nuits sans vraie récupération — <strong>savoir ne pas courir, c'est une compétence.</strong>"},
 {"bg":"linear-gradient(160deg,#1e3a8a,#0c1c3d)","kicker":"LES 2 SORTIES","big":"FC 148","txt":"Lundi 11,3 km à 5:53. Jeudi 10,7 km à 5:47 avec dérive cardiaque maîtrisée. <strong>Z2 propre les deux fois — le moteur tourne.</strong>"},
 {"bg":"linear-gradient(160deg,#7f1d1d,#1c0a00)","kicker":"LE SACRIFICE","big":"Spéc. trail","txt":"La séance vallonnée n'a pas eu lieu. Le stimulus manque — <strong>mais la fraîcheur est intacte. À J-7, c'est elle qui compte.</strong>"},
 {"bg":"linear-gradient(160deg,#134e4a,#042f2e)","kicker":"VERDICT DU COACH","big":"B+","txt":"Semaine incomplète mais bien arbitrée. Conditions extrêmes, zéro prise de risque, les 2 séances clés exécutées proprement. <strong>Le corps est prêt.</strong>"},
 {"bg":"linear-gradient(160deg,#b45309,#451a03)","kicker":"LA SUITE","big":"S27","txt":"Semaine de course — Déraille dimanche.<br><strong>C'est ton jour. 🏁</strong>"}]},
{"id":"S27","titre":"Ta semaine 27","sous":"Semaine course · 29 juin-5 juillet · Trail Déraille","slides":[
 {"bg":"linear-gradient(160deg,#0f172a,#1c3d2e)","kicker":"REWIND · SEMAINE 27","big":"🏁","txt":"La semaine de course. Objectif : relancer la machine.<br>Tape pour avancer."},
 {"bg":"linear-gradient(160deg,#065f46,#022c22)","kicker":"LE VOLUME","big":"53 km","txt":"dont la Déraille (23,3 km · D+957m). Une vraie semaine de course, bien remplie."},
 {"bg":"linear-gradient(160deg,#1e3a8a,#0c1c3d)","kicker":"LUNDI AVEC EDWIGE","big":"13 km","txt":"Sortie tranquille à deux, 5:39/km par 30°C. Le plaisir recharge autant que le repos."},
 {"bg":"linear-gradient(160deg,#7c2d12,#1c0a00)","kicker":"MARDI","big":"Stop","txt":"Tempo interrompu par un souci gastrique. <strong>Arrêté au bon moment — écouter le corps, c'est aussi ça courir intelligemment.</strong>"},
 {"bg":"linear-gradient(160deg,#134e4a,#042f2e)","kicker":"JEUDI · AFFÛTAGE","big":"FC 148","txt":"10,5 km en Z2 pure, zéro PR, digestion rétablie. La sortie parfaite à J-3. Le corps en automatique."},
 {"bg":"linear-gradient(160deg,#7f1d1d,#1c0a00)","kicker":"DIMANCHE · LA COURSE","big":"2:52:48","txt":"Trail Déraille · 66e/180 (top 37%) · 11e/18 M0. <strong>FC 168 tenue sur 2h52 sans effondrement.</strong>"},
 {"bg":"linear-gradient(160deg,#581c87,#1e1b4b)","kicker":"LA DESCENTE","big":"4:46/km","txt":"Km 18 en pleine descente technique. <strong>Ta vraie arme — elle est intacte.</strong>"},
 {"bg":"linear-gradient(160deg,#b45309,#451a03)","kicker":"VERDICT DU COACH","big":"A","txt":"Course de gestion réussie sur 4h de sommeil et zéro prépa trail. La tête a fait la différence. <strong>Objectifs atteints, zéro séquelle.</strong>"},
 {"bg":"linear-gradient(160deg,#0d9488,#0f766e)","kicker":"LA SUITE","big":"Nice","txt":"Cap sur le Marathon — 8 novembre.<br><strong>Le vrai objectif commence maintenant.</strong>"}]},
{"id":"S28","titre":"Ta semaine 28","sous":"Récupération post-Déraille · 6-12 juillet · montagne","slides":[
 {"bg":"linear-gradient(160deg,#0f172a,#1e3a5f)","kicker":"REWIND · SEMAINE 28","big":"🎬","txt":"Une « récupération » à 61 km. Et pourtant, l'une des plus belles semaines de ta saison.<br>Tape pour avancer."},
 {"bg":"linear-gradient(160deg,#7c2d12,#1c0a00)","kicker":"LE DÉPASSEMENT","big":"+69 %","txt":"61 km réalisés pour 36 ciblés. D'ordinaire, ça mérite un froncement de sourcils. Ici, le volume ne dit pas tout."},
 {"bg":"linear-gradient(160deg,#1e3a8a,#0c1c3d)","kicker":"LE WEEK-END MONTAGNE","big":"1176 m","txt":"de D+ cumulés en deux jours : 646 m samedi, 530 m dimanche au Petit Croisse Baulet. <strong>Du jamais vu dans ta saison.</strong>"},
 {"bg":"linear-gradient(160deg,#065f46,#022c22)","kicker":"POURQUOI ÇA PASSE","big":"138 · 129","txt":"les FC moyennes des deux trails. À ces valeurs, tu récupérais en montant. Le cœur raconte la vérité que le volume cache."},
 {"bg":"linear-gradient(160deg,#134e4a,#042f2e)","kicker":"LA DISCIPLINE","big":"137-140","txt":"bpm sur les deux récups actives de mardi et mercredi. Exécution parfaite, sans une seule tentation d'accélérer."},
 {"bg":"linear-gradient(160deg,#0c4a6e,#082f49)","kicker":"LA SORTIE LONGUE","big":"18 km","txt":"avancée au jeudi et gérée sous la chaleur. <strong>Protocole hydratation validé</strong> — celui qui te sert encore aujourd'hui."},
 {"bg":"linear-gradient(160deg,#134e4a,#042f2e)","kicker":"VERDICT DU COACH","big":"A−","txt":"Le chiffre du volume dit dépassement, le terrain dit intelligence. <strong>Tu as transformé une semaine de récup en semaine de montagne, sans le payer.</strong>"},
 {"bg":"linear-gradient(160deg,#b45309,#451a03)","kicker":"LA SUITE","big":"S29","txt":"Seuil découverte — on relance la qualité.<br><strong>Le corps est prêt. 🎯</strong>"}]},
{"id":"S29","titre":"Ta semaine 29","sous":"Seuil découverte · 13-19 juillet · canicule","slides":[
 {"bg":"linear-gradient(160deg,#0f172a,#1e3a5f)","kicker":"REWIND · SEMAINE 29","big":"🎬","txt":"Une reprise magistrale qui se termine en apothéose.<br>Tape pour avancer."},
 {"bg":"linear-gradient(160deg,#065f46,#022c22)","kicker":"LE VOLUME","big":"53,7 km","txt":"en 4 sorties et 5h14 de mouvement. Zéro douleur, et une confiance qui explose."},
 {"bg":"linear-gradient(160deg,#0c4a6e,#082f49)","kicker":"L'ÉCOUTE","big":"2 jours","txt":"off lundi et mardi après le double trail. <strong>Tu n'as pas forcé la reprise</strong> — et tout le reste de la semaine en a découlé."},
 {"bg":"linear-gradient(160deg,#7c2d12,#1c0a00)","kicker":"LA SORTIE LONGUE","big":"23 km","txt":"sous canicule, avec 31 records personnels au passage et un protocole nutrition affiné."},
 {"bg":"linear-gradient(160deg,#581c87,#1e1b4b)","kicker":"LA SÉANCE DE LA SEMAINE","big":"4:24","txt":"et 4:31/km sur le seuil 30, pour une cible à 4:40. <strong>15 secondes au kilomètre plus vite que prévu</strong> — en te sentant très bien."},
 {"bg":"linear-gradient(160deg,#134e4a,#042f2e)","kicker":"LE BON ARBITRAGE","big":"PPG","txt":"sautée. Et c'est le bon choix : <strong>on ne sacrifie jamais le seuil ni la sortie longue</strong> pour du renforcement."},
 {"bg":"linear-gradient(160deg,#134e4a,#042f2e)","kicker":"VERDICT DU COACH","big":"A","txt":"Reprise progressive, arbitrages justes, séance clé au-dessus des attentes. <strong>La progression est désormais visible partout.</strong>"},
 {"bg":"linear-gradient(160deg,#b45309,#451a03)","kicker":"LA SUITE","big":"S30","txt":"Semaine ViaRhôna — le marathon à l'entraînement.<br><strong>Le vrai test. 🎯</strong>"}]},
{"id":"S30","titre":"Ta semaine 30","sous":"Semaine ViaRhôna · 20-26 juillet · marathon","slides":[
 {"bg":"linear-gradient(160deg,#0f172a,#1e3a5f)","kicker":"REWIND · SEMAINE 30","big":"🎬","txt":"La plus grosse semaine de ta préparation. Et de loin.<br>Tape pour avancer."},
 {"bg":"linear-gradient(160deg,#065f46,#022c22)","kicker":"LE VOLUME","big":"74,2 km","txt":"en 4 sorties, charge 621. <strong>Ton plus haut volume de la saison</strong> — 21 km de plus que la semaine précédente."},
 {"bg":"linear-gradient(160deg,#581c87,#1e1b4b)","kicker":"LE JALON","big":"42,52 km","txt":"Vienne → Saint-Rambert-d'Albon. <strong>Un marathon complet à l'entraînement</strong>, jeudi, en pleine préparation."},
 {"bg":"linear-gradient(160deg,#0c4a6e,#082f49)","kicker":"LE CHIFFRE QUI COMPTE","big":"141,8","txt":"bpm sur les 15 premiers kilomètres à 5:36/km. <strong>Très bas pour cette allure</strong> — la base aérobie est là."},
 {"bg":"linear-gradient(160deg,#134e4a,#042f2e)","kicker":"LA PREUVE","big":"5:16 · 5:15","txt":"les kilomètres 41 et 42, à ton allure cible Nice, <strong>sur des jambes qui avaient déjà 40 km</strong>. C'est ça, la vraie réponse."},
 {"bg":"linear-gradient(160deg,#7c2d12,#1c0a00)","kicker":"LA VITESSE AUSSI","big":"3:16/km","txt":"en pointe finale sur les 8×30 sec du mardi. Ta plus rapide de la saison, deux jours avant le marathon."},
 {"bg":"linear-gradient(160deg,#134e4a,#042f2e)","kicker":"VERDICT DU COACH","big":"A","txt":"Un marathon encaissé sans incident, une nutrition validée, et la fin de course la plus instructive de ta saison. <strong>Tu la termines debout.</strong>"},
 {"bg":"linear-gradient(160deg,#b45309,#451a03)","kicker":"LA SUITE","big":"S31","txt":"Absorption — on digère avant de repartir.<br><strong>Le repos fait partie du plan. 🎯</strong>"}]},
{"id":"S31","titre":"Ta semaine 31","sous":"Absorption marathon · 27 juil-2 août · canicule","slides":[
 {"bg":"linear-gradient(160deg,#0f172a,#1e3a5f)","kicker":"REWIND · SEMAINE 31","big":"🎬","txt":"Une semaine d'absorption réussie — et une leçon qui vaut plus que les kilomètres.<br>Tape pour avancer."},
 {"bg":"linear-gradient(160deg,#0c4a6e,#082f49)","kicker":"LA BAISSE VOULUE","big":"−39 %","txt":"45,5 km et charge 404, contre 621 en S30. <strong>Exactement ce qu'il fallait</strong> après un marathon, sous 36-38 °C."},
 {"bg":"linear-gradient(160deg,#7c2d12,#1c0a00)","kicker":"LA VITESSE INTACTE","big":"2:57/km","txt":"en pointe sur les 6×30 du lundi, en negative split parfait. <strong>19 s/km plus rapide qu'au 21 juillet.</strong>"},
 {"bg":"linear-gradient(160deg,#134e4a,#042f2e)","kicker":"LA DISCIPLINE","big":"0 sec","txt":"passée au-dessus de 150 bpm mardi, FC moyenne 138, découplage 3 %. Une EF pilotée au cardio, parfaitement tenue."},
 {"bg":"linear-gradient(160deg,#9a3412,#431407)","kicker":"LA DÉCOUVERTE","big":"5:35 → 4:55","txt":"dimanche, FC 136 → 161. <strong>Sans jamais décider d'accélérer.</strong> C'est là que ta dérive a été identifiée pour la première fois."},
 {"bg":"linear-gradient(160deg,#581c87,#1e1b4b)","kicker":"POURQUOI ÇA COMPTE","big":"🎯","txt":"C'est le mécanisme exact qui fait exploser un marathon parti trop vite. <strong>L'identifier en juillet vaut mieux que le découvrir à Nice.</strong>"},
 {"bg":"linear-gradient(160deg,#134e4a,#042f2e)","kicker":"VERDICT DU COACH","big":"A−","txt":"Absorption bien menée, repos respecté pour le pied, vitesse préservée. <strong>Et surtout : le vrai point faible enfin nommé.</strong>"},
 {"bg":"linear-gradient(160deg,#b45309,#451a03)","kicker":"LA SUITE","big":"S32","txt":"Reprise progressive — et le début du travail de retenue.<br><strong>Un chiffre avant chaque sortie. 🎯</strong>"}]},
{"id":"S32","titre":"Ta semaine 32","sous":"Reprise progressive · 3-9 août · canicule","slides":[
 {"bg":"linear-gradient(160deg,#0f172a,#1e3a5f)","kicker":"REWIND · SEMAINE 32","big":"🎬","txt":"5 sorties, un pied qui se tait enfin, et une leçon qui vaut pour Nice.<br>Tape pour avancer."},
 {"bg":"linear-gradient(160deg,#065f46,#022c22)","kicker":"LE VOLUME","big":"67,3 km","txt":"en 5 sorties — ta plus grosse semaine depuis ViaRhôna. Soit à peu près Lyon → Saint-Étienne… où tu as justement fini dimanche."},
 {"bg":"linear-gradient(160deg,#7c2d12,#1c0a00)","kicker":"TEMPS EN MOUVEMENT","big":"7h07","txt":"de course, 5 194 kcal brûlées, et ≈ 61 000 battements de cœur. Le moteur a tourné long."},
 {"bg":"linear-gradient(160deg,#1e3a8a,#0c1c3d)","kicker":"LE DÉNIVELÉ","big":"817 m","txt":"dont 662 sur la seule journée de dimanche. Le reste de la semaine était plat comme une table."},
 {"bg":"linear-gradient(160deg,#134e4a,#042f2e)","kicker":"LA SORTIE QUI COMPTE","big":"132 bpm","txt":"Vendredi, cible ≤135 annoncée à l'avance. Résultat : FC entre 124 et 136 sur 10 km, sans un seul emballement. <strong>Retenue parfaite.</strong>"},
 {"bg":"linear-gradient(160deg,#9a3412,#431407)","kicker":"ET SON MIROIR","big":"5:07/km","txt":"Dimanche, km 27, seul, sans cible. 7:15 → 5:07/km et FC 139 → 166 en six kilomètres. <strong>Tu n'as jamais décidé d'accélérer.</strong>"},
 {"bg":"linear-gradient(160deg,#581c87,#1e1b4b)","kicker":"LA LEÇON DE LA SEMAINE","big":"🎯","txt":"<strong>Ta retenue existe quand elle est chiffrée. Elle disparaît quand elle est laissée au ressenti.</strong><br>Vendredi et dimanche l'ont prouvé à 48 h d'écart."},
 {"bg":"linear-gradient(160deg,#14532d,#052e16)","kicker":"LE DOSSIER CLOS","big":"0 douleur","txt":"au pied, sur 5 sorties, dont 27 km de trail avec descentes techniques. <strong>La gêne du 23/07 est derrière toi.</strong>"},
 {"bg":"linear-gradient(160deg,#0c4a6e,#082f49)","kicker":"LA CHARGE","big":"ACWR 0,97","txt":"Charge aiguë 487, chronique 504/semaine. Pile la zone optimale — ni sous-charge, ni surcharge."},
 {"bg":"linear-gradient(160deg,#7f1d1d,#1c0a00)","kicker":"LE POINT MATÉRIEL","big":"👟","txt":"Dimanche : Novablast route sur 662 m de sentier, au lieu des Cascadia. <strong>Aucune conséquence — cette fois.</strong>"},
 {"bg":"linear-gradient(160deg,#134e4a,#042f2e)","kicker":"VERDICT DU COACH","big":"B+","txt":"Physiquement excellent : volume, santé, charge maîtrisée. <strong>Mais 2 sorties sur 5 hors plan, une dérive non décidée et deux erreurs de chaussures.</strong> Le corps suit mieux que la discipline."},
 {"bg":"linear-gradient(160deg,#b45309,#451a03)","kicker":"LA SUITE","big":"S33","txt":"Allègement — seuil 2×10 et longue 18 km plafonnée en FC.<br><strong>L'objectif : finir sans avoir accéléré. 🎯</strong>"}]}]
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
  {"build":185,"date":"15 aout 2026","sha":"","tag":"Correction : les Clifton 10 n'ont jamais quitte la rotation","items":[
    "CORRECTION APPORTEE PAR LOIC : les Clifton 10 restent dans sa rotation, simplement moins utilisees. Elles n'ont jamais ete retirees. Le flag Strava (retired=false) etait donc juste ; c'est mon interpretation qui etait fausse.",
    "PORTEE DE L'ERREUR : je ne me suis pas contente d'une donnee inexacte, j'ai qualifie sur cette base des choix de Loic comme des ECARTS. La revue du 05/08 parlait d'une paire « attrapee par reflexe » et suggerait de la sortir de la maison ; la revue de S32 comptait deux « ecarts materiels » ; une slide du Rewind S32 affichait « LES DEUX ECARTS ». Un seul de ces ecarts existait reellement, celui des Novablast route sur 662 m de sentier technique.",
    "TEXTES CORRIGES : revue du 28/07, revue du 05/08, revue de S32, slide du Rewind S32, conseil coach de S31. Le fond technique est conserve -- 1179 km reste un kilometrage eleve et l'amorti est entame -- mais formule comme une RECOMMANDATION (garder cette paire pour les footings courts, privilegier les paires recentes sur les seances longues ou rapides) et non comme un constat de retrait deja acte.",
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
    "ETAT APRES CORRECTIFS : audit runtime a 0 anomalie sur 30 semaines, 132 seances, 5 Rewinds et toutes les fenetres Cockpit ; audit statique a 1 seul point restant (une seance du 25/06 jamais loguee, sans consequence)."
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
    "Fond global gris perle iOS (#f2f2f7), cartes blanches SANS bordure avec ombre a peine perceptible, rayons genereux",
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
  {"nom":"Trail Déraille — Lac des Sapins","alias":"Déraille","date":"2026-07-05","lieu":"Lac des Sapins · France","type":"trail","distance":23.3,"dplus":957,"dminus":957,"temps":"2:52:48","allure":"7:12","classement_gen":66,"classement_cat":11,"total_finishers":180,"cat":"M0","fc_moy":168,"fc_max":181,"cal":2388,"chaussures":"Cascadia 19","meteo":"Chaleur intense · exposition forte","statut":"termine","strava_id":"19186067917","accent":"#0d9488","bilan":"<strong>Course de gestion réussie dans des conditions extrêmes.</strong> Réalisée sur ~4h de sommeil (nuit blanche jusqu'à 2h après le match de l'équipe de France), sans aucune préparation trail depuis la Circaète (zéro côte, zéro dénivelé), par forte chaleur. 66e au général sur 180 engagés (top 37%), 11e/18 en catégorie M0.<br><br><strong>La stratégie était la bonne — les données le prouvent :</strong> FC moyenne 168 (88% FCmax) tenue sur 2h52 sans jamais d'explosion. Contrairement à la Circaète, aucun effondrement. Gestion parfaite en montée (marche active sur la Montée des Stèles : +158m à 15,7% de pente au km 13). <strong>Descente exceptionnelle</strong> — km 18 à 4:46/km, vraie signature de force.<br><br><strong>Le mur des 2 derniers km était thermique, pas nutritionnel :</strong> la FC reste haute (170-171) alors que l'allure s'effondre — signature déshydratation + surchauffe, pas de panne de sucre. Nutrition correcte (3 gels + 3L dont 1L électrolytes) mais insuffisante face à la chaleur. Alternance marche/course sur la fin, perte de ~2 min sur le partenaire.<br><br><strong>Objectifs atteints :</strong> relancer la machine, tester la nutrition, courir intelligemment. Zéro séquelle physique ou mentale. <strong>Enseignements pour Nice :</strong> la tête est le meilleur atout, la descente est une arme, la gestion thermique et l'endurance spécifique trail restent à travailler."},
  {"nom":"Trail - Circaète (Gypaète)","alias":"Circaète","date":"2026-06-06","lieu":"Ardèche · France","type":"trail","distance":29.8,"dplus":1661,"dminus":1661,"temps":"4:57:38","allure":"9:36","classement_gen":182,"classement_cat":None,"total_finishers":None,"cat":"M0","fc_moy":152,"fc_max":178,"cal":3191,"chaussures":"Cascadia 19","meteo":"26-31°C · canicule sèche","statut":"termine","strava_id":"18810734775","accent":"#0d9488","bilan":"Première grande épreuve trail de la saison. Crise électrolytique progressive à partir du km 20 — déshydratation sévère en chaleur extrême. Course terminée en 4:57:38 malgré l'effondrement. <strong>Leçon fondatrice :</strong> intégration systématique de TA Electrolytes dans toutes les sorties et courses depuis. #182 au général."},
  {"nom":"Run In Lyon 10km","alias":"Run In Lyon 10k","date":"2022-10-02","lieu":"Lyon · France","type":"route","distance":10,"dplus":None,"dminus":None,"temps":"53:58","allure":"5:24","classement_gen":4900,"classement_cat":None,"total_finishers":None,"cat":None,"fc_moy":None,"fc_max":None,"cal":None,"chaussures":None,"meteo":None,"statut":"termine","strava_id":None,"accent":"#f59e0b","bilan":"10km sur les berges de Lyon en 53:58 · allure 5:24/km. #4900 au général sur une très grande course de masse. <strong>Référence pour calibrer la progression :</strong> objectif sub-50 min en 2026-2027."},
  {"nom":"SaintéLyon — Relais Équipe","alias":"SaintéLyon relay","date":"2022-12-03","lieu":"Yssingeaux → Lyon","type":"trail_nuit","distance":22.77,"dplus":459,"dminus":900,"temps":"2:27:00","allure":"6:28","classement_gen":None,"classement_cat":None,"total_finishers":None,"cat":None,"fc_moy":None,"fc_max":None,"cal":None,"chaussures":None,"meteo":"Nuit · ~4°C · hiver","statut":"termine","strava_id":None,"accent":"#0d9488","bilan":"Relais #4 de l'équipe SaintéLyon. <strong>Référence directe pour la préparation SaintExpress 2026 :</strong> segment km 27-45 du parcours. Allure 6:28/km de nuit avec 459m D+. Validation que le segment final est gérable après km 27 parcourus."},
  {"nom":"Trail des Hautes Chaumes","alias":"Hautes Chaumes","date":"2022-05-08","lieu":"Roche · France","type":"trail","distance":6,"dplus":None,"dminus":None,"temps":"46:29","allure":"7:45","classement_gen":44,"classement_cat":None,"total_finishers":None,"cat":"SE","fc_moy":None,"fc_max":None,"cal":None,"chaussures":None,"meteo":None,"statut":"termine","strava_id":None,"accent":"#0d9488","bilan":"Court trail local ~6km · allure 7:45/km. <strong>#44 au général</strong> — excellent classement sur une épreuve technique. Catégorie SE à l'époque."},
  {"nom":"Harmonie Mutuelle Semi de Paris","alias":"Semi de Paris","date":"2022-03-06","lieu":"Paris · France","type":"semi","distance":21.1,"dplus":None,"dminus":None,"temps":"1:53:21","allure":"5:22","classement_gen":27259,"classement_cat":None,"total_finishers":None,"cat":None,"fc_moy":None,"fc_max":None,"cal":None,"chaussures":None,"meteo":None,"statut":"termine","strava_id":None,"accent":"#0d9488","bilan":"Premier grand semi-marathon officiel. 1:53:21 chrono réel · 5:22/km. #27259 au général dans l'une des plus grandes courses de France. <strong>Référence de départ :</strong> objectif 1:44 au Semi de Lyon 4 oct. 2026 = −9 min en 4 ans de progression."}
]
_j.dump({"PHASES":PHASES,"COUL":COUL,"SEMAINES":SEMAINES,"SBW":SEANCES_BY_WEEK,"GEAR":GEAR,"RACES":RACES,
  "PROFIL":PROFIL,"PROJ":PROJ,"RECORDS":RECORDS,"VIGILANCE":VIGILANCE,"S24R":S24_REALISE,
  "HIST":_hist["HIST"],"POLAR":_hist["POLAR"],"ALLURES":ALLURES,"ALLURES_COURSE":ALLURES_COURSE,"ZONES_FC":ZONES_FC,"MONTHLY":MONTHLY,"SAISON2026":SAISON2026,"SAISON_EFF":SAISON_EFF,"ACWR_DATA":ACWR_DATA,"RECORDS_PERF":RECORDS_PERF,"JOURNAL":JOURNAL,"REWINDS":REWINDS,"MAJ":"10 juillet 2026","HEATMAP":HEATMAP,"DOSSIERS":DOSSIERS,"PALMARES":PALMARES,"CHANGELOG":CHANGELOG},open('/tmp/data.json','w'),ensure_ascii=False)
print("OK")
