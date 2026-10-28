#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
log_seance.py — transforme une sortie Strava en log de seance (chantier P2).

Le shell n'atteint pas Strava : Claude lit Strava par MCP et recopie l'essentiel dans un petit
fichier d'entree (format ci-dessous), puis lance ce script. Il produit tout le reste :

  - src/logs/S44-2.json : le bloc « realise » (splits, temperature, terrain, decouplage...) et les
    champs de la seance a mettre a jour (chaussure, date, titre, segments) ; gen.py le charge ;
  - src/strava_reference.json : activite du jour et kilometrage de la chaussure ;
  - GEAR dans src/gen.py : kilometrage de la chaussure ;
  - une entree de CHANGELOG (build + 1).

Il reste a ecrire la revue du coach dans src/textes/seances/S44-2.html.

    python scripts/log_seance.py S44-2 strava/20753555995.json [options]

Options :
  --streams FICHIER   flux Strava (time, heart_rate, velocity_smooth, resolution 1000) pour le
                      decouplage : seulement pour un footing, une sortie longue ou une recuperation
  --blocs SPEC        segments de la seance, par tours : "1-8:Footing facile:vert,9-10:Fin:orange"
                      (couleurs : vert, bleu, orange, rouge)
  --statut S          fait (defaut), partiel
  --titre T --sous S  si la seance differe du plan
  --rpe N             RPE ressenti (0-10)
  --commentaire C     remplace le commentaire factuel produit automatiquement
  --sans-changelog    ne pas ajouter d'entree de CHANGELOG (plusieurs seances dans un meme build)
  --force             reecrire un log existant (la reference Strava n'est alors pas modifiee)
  --sec               affiche ce qui serait ecrit, sans rien ecrire
  --rewind FICHIER    donnees du Rewind de seance (format : scripts/rewind_seance.py) -> src/rewind/44-2.json
  --cible-allure A --cible-fc F --cible-source S
                      cible appliquee si la seance a ete remplacee (ex. 6:10- et 145), gardee dans le Rewind

Fichier d'entree (champs Strava recopies tels quels ; laps = un tableau par tour de get_activity_performance) :
{"id":"20753555995","start_local":"2026-10-27T17:04:11","sport_type":"Run","gear_id":"28498174",
 "distance":10035.6,"moving_time":3510,"elapsed_time":3525,"elevation_gain":31,"relative_effort":86,
 "total_calories":754,"avg_cadence":85.9994,"pr_count":0,"achievement_count":0,"temperature":18.4,
 "average_heartrate":145.58,"max_heartrate":165,"gear_total_distance":1284244,
 "laps":[[moving_time, distance, avg_hr, max_hr, elevation_gain], ...]}
"""
import argparse
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

GEN = os.path.join(SRC, "gen.py")
REF = os.path.join(SRC, "strava_reference.json")
LOGS = os.path.join(SRC, "logs")
SEANCES = os.path.join(ROOT, "data", "seances.json")

# gear_id Strava -> modele (cle de GEAR dans gen.py et de strava_reference.json)
GEAR_IDS = {"28498174": "Clifton 10", "28498182": "Gel Pulse 16", "28498287": "Cascadia 19",
            "28722452": "Novablast 5 J", "29204843": "Magic Speed 4", "31859870": "Novablast 5 V"}
HAUTEUR = {"vert": 40, "bleu": 60, "orange": 72, "rouge": 80}
CHAMPS_ENTREE = ("id", "start_local", "distance", "moving_time", "elapsed_time", "elevation_gain",
                 "relative_effort", "average_heartrate", "max_heartrate", "laps")
TRAIL_DPLUS_KM = 15  # m de D+ par km : au-dela, sortie classee trail (meme seuil que le decouplage)


def duree(sec):
    sec = int(round(sec))
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def allure(sec, metres):
    s = int(round(sec / (metres / 1000)))
    return f"{s // 60}:{s % 60:02d}"


def virgule(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def terrain(e):
    if e.get("sport_type") == "TrailRun":
        return "trail"
    return "trail" if e["elevation_gain"] / (e["distance"] / 1000) >= TRAIL_DPLUS_KM else "route"


def splits(laps):
    """Un split par tour d'au moins 900 m (le reliquat de fin est ignore)."""
    out = []
    for lap in laps:
        mt, dist, fc = lap[0], lap[1], lap[2]
        if dist >= 900:
            out.append({"km": len(out) + 1, "allure": allure(mt, dist), "fc": int(round(fc))})
    return out


def blocs(spec, laps):
    """'1-8:Footing facile:vert,9-10:Fin:orange' -> segments (duree, allure et FC calculees sur les tours)."""
    segs = []
    for part in spec.split(","):
        rng, nom, coul = part.split(":")
        a, _, z = rng.partition("-")
        a, z = int(a), int(z or a)
        tours = laps[a - 1:z]
        if not tours or len(tours) != z - a + 1:
            raise SystemExit(f"--blocs : tours {rng} hors limites ({len(laps)} tours)")
        t = sum(x[0] for x in tours)
        d = sum(x[1] for x in tours)
        fc = sum(x[2] * x[0] for x in tours) / t
        n = z - a + 1
        role = f"{n} km a {allure(t, d)}/km, FC {int(round(fc))}." if n > 1 else f"Km {a} a {allure(t, d)}/km, FC {int(round(fc))}."
        segs.append({"nom": nom, "role": role, "duree": int(round(t)), "couleur": coul,
                     "bloc": "—", "hauteur": HAUTEUR.get(coul, 50)})
    return segs


def decouplage(streams_path, temp, e):
    from decouplage import analyse
    if terrain(e) != "route":
        return {"qualite": "non_calculable", "raison": "trail ou denivele > 15 m/km", "algo": "decoup-v1"}
    with open(streams_path, encoding="utf-8") as f:
        r = analyse(json.load(f), temp)
    if r.get("qualite") in ("fiable", "incertain"):
        return {k: r[k] for k in ("pct", "bpm", "fen_min", "temp", "attendu", "p1", "fc1", "p2", "fc2", "qualite", "algo")}
    garde = ("qualite", "temp", "algo") if r.get("qualite") == "non_representatif" else ("qualite", "raison", "algo")
    return {k: r[k] for k in garde if k in r}


def gear_gen():
    """GEAR de gen.py : modele -> (marque, km)."""
    src = open(GEN, encoding="utf-8").read()
    bloc = src[src.index("\nGEAR=[") + 1:]
    bloc = bloc[:bloc.index("\n]") + 2]
    return {m: (marque, int(km)) for marque, m, km in
            re.findall(r'\{"marque":"([^"]+)","modele":"([^"]+)","km":(\d+)\}', bloc)}


def seance_prevue(w, i):
    with open(SEANCES, encoding="utf-8") as f:
        sbw = json.load(f)["SEANCES_BY_WEEK"]
    for s in sbw.get(str(w), []):
        if str(s["id"]) == str(i):
            return s
    raise SystemExit(f"S{w}-{i} : seance absente du plan (data/seances.json)")


def construire(cle, e, a):
    w, i = cle[1:].split("-", 1)
    prevue = seance_prevue(w, i)
    temp = int(round(e["temperature"])) if e.get("temperature") is not None else None
    date = e["start_local"][:10]
    modele = GEAR_IDS.get(str(e.get("gear_id")))
    gears = gear_gen()

    r = {"statut": a.statut}
    if a.streams:
        r["decouplage"] = decouplage(a.streams, temp, e)
    if temp is not None:
        r["temp"] = temp
    r.update({"km": round(e["distance"] / 1000, 2), "temps": duree(e["moving_time"]),
              "allure": allure(e["moving_time"], e["distance"]) + "/km",
              "fc_moy": int(round(e["average_heartrate"])), "fc_max": int(round(e["max_heartrate"])),
              "re": e["relative_effort"]})
    if e.get("avg_cadence"):
        r["cadence"] = int(round(e["avg_cadence"]))
    r["elevation_gain"] = int(round(e["elevation_gain"]))
    if e.get("total_calories"):
        r["kcal"] = int(round(e["total_calories"]))
    if a.rpe is not None:
        r["rpe_ressenti"] = a.rpe
    r["terrain"] = terrain(e)
    if a.commentaire:
        r["commentaire"] = a.commentaire
    else:
        arret = e["elapsed_time"] - e["moving_time"]
        c = (f"Realise : {virgule(r['km'])} km en {r['temps']} de deplacement"
             + (f" ({duree(e['elapsed_time'])} ecoulees)" if arret >= 60 else "")
             + f", {r['allure']}, FC {r['fc_moy']} moy / {r['fc_max']} max, D+ {r['elevation_gain']} m"
             + (f", {temp} °C" if temp is not None else "")
             + (f", {gears[modele][0]} {modele}" if modele in gears else "") + ".")
        r["commentaire"] = c
    r.update({"pr": e.get("pr_count", 0), "ach": e.get("achievement_count", 0), "pr_detail": []})
    r["splits"] = splits(e["laps"])
    r["strava_id"] = str(e["id"])

    s = {}
    if modele in gears:
        s["chaussure_realise"] = f"{gears[modele][0]} {modele}"
    if date != prevue.get("date"):
        s["date"] = date
    if a.titre:
        s["titre"] = a.titre
    if a.sous:
        s["sous"] = a.sous
    if a.blocs:
        s["segments"] = blocs(a.blocs, e["laps"])
    return {"seance": s, "realise": r}, prevue, modele, date


def maj_reference(e, modele, date, ajouter_activite):
    with open(REF, encoding="utf-8") as f:
        ref = json.load(f)
    km = round(e["distance"] / 1000, 4)
    if ajouter_activite:
        act = ref["activites"]
        nouv = [km, e["relative_effort"], int(round(e["elevation_gain"]))]
        if date in act and [round(act[date][0], 2), act[date][1], act[date][2]] == [round(km, 2)] + nouv[1:]:
            print(f"Reference : {date} contient deja cette sortie, inchangee")
        elif date in act:  # plusieurs sorties le meme jour : totaux additionnes
            old = act[date]
            act[date] = [round(old[0] + km, 4), old[1] + e["relative_effort"], old[2] + int(round(e["elevation_gain"]))]
        else:
            ref["activites"] = {date: [km, e["relative_effort"], int(round(e["elevation_gain"]))], **act}
    if modele and e.get("gear_total_distance"):
        ref["chaussures"][modele] = int(round(e["gear_total_distance"] / 1000))
    return json.dumps(ref, indent=1) + "\n"


def maj_gen(src, modele, km_gear, entree_changelog):
    if modele and km_gear is not None:
        motif = re.compile(r'(\{"marque":"[^"]+","modele":"' + re.escape(modele) + r'","km":)\d+(\})')
        src, n = motif.subn(lambda m: f"{m.group(1)}{km_gear}{m.group(2)}", src, count=1)
        if n != 1:
            raise SystemExit(f"GEAR : chaussure {modele} introuvable dans gen.py")
    if entree_changelog:
        src = src.replace("CHANGELOG=[\n", "CHANGELOG=[\n" + entree_changelog, 1)
    return src


def changelog(src, cle, log, prevue, modele, km_gear, date):
    build = int(re.search(r'CHANGELOG=\[\n  \{"build":(\d+)', src).group(1)) + 1
    w, i = cle[1:].split("-", 1)
    r = log["realise"]
    titre = log["seance"].get("titre") or prevue["titre"]
    jj = datetime.date.fromisoformat(date)
    mois = ["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre",
            "octobre", "novembre", "decembre"][jj.month - 1]
    items = [f"SEANCE : S{w} seance {i} loggee depuis Strava : {titre}, {virgule(r['km'])} km en {r['temps']} "
             f"({r['allure']}), FC {r['fc_moy']}/{r['fc_max']}, D+ {r['elevation_gain']} m"
             + (f", {r['temp']} °C" if "temp" in r else "") + (f", {modele}" if modele else "") + "."]
    if modele and km_gear is not None:
        items.append(f"CHAUSSURES : {modele} a {km_gear} km.")
    entree = {"build": build, "date": f"{jj.day} {mois} {jj.year}", "sha": "",
              "tag": f"Log S{w} seance {i} : {titre} du {jj.strftime('%d/%m')}"}
    txt = ("  " + json.dumps(entree, ensure_ascii=False, separators=(",", ":"))[:-1] + ',"items":[\n'
           + ",\n".join("    " + json.dumps(x, ensure_ascii=False) for x in items) + "]},\n")
    return txt, build


def main(argv=None):
    p = argparse.ArgumentParser(description="Strava -> log de seance (voir l'en-tete du fichier)")
    p.add_argument("seance", help="S44-2 (semaine-id)")
    p.add_argument("entree", help="fichier d'entree Strava (JSON)")
    p.add_argument("--streams")
    p.add_argument("--blocs")
    p.add_argument("--statut", default="fait", choices=["fait", "partiel"])
    p.add_argument("--titre")
    p.add_argument("--sous")
    p.add_argument("--rpe", type=int)
    p.add_argument("--commentaire")
    p.add_argument("--sans-changelog", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--sec", action="store_true")
    p.add_argument("--rewind")
    p.add_argument("--cible-allure")
    p.add_argument("--cible-fc")
    p.add_argument("--cible-source")
    a = p.parse_args(argv)
    if not re.fullmatch(r"S\d+-\w+", a.seance):
        raise SystemExit("Seance attendue au format S44-2")
    with open(a.entree, encoding="utf-8") as f:
        e = json.load(f)
    manque = [c for c in CHAMPS_ENTREE if c not in e]
    if manque:
        raise SystemExit(f"Champs manquants dans {a.entree} : {', '.join(manque)}")

    cible = os.path.join(LOGS, f"{a.seance}.json")
    existe = os.path.exists(cible)
    if existe and not a.force:
        raise SystemExit(f"{cible} existe deja (--force pour le reecrire)")

    if os.path.isdir(LOGS):  # meme sortie Strava deja loggee sous une autre seance ?
        for nom in os.listdir(LOGS):
            if nom.endswith(".json") and nom != f"{a.seance}.json":
                with open(os.path.join(LOGS, nom), encoding="utf-8") as f:
                    if json.load(f)["realise"].get("strava_id") == str(e["id"]):
                        raise SystemExit(f"Activite Strava {e['id']} deja loggee dans {nom}")

    log, prevue, modele, date = construire(a.seance, e, a)
    km_gear = int(round(e["gear_total_distance"] / 1000)) if e.get("gear_total_distance") else None
    src = open(GEN, encoding="utf-8").read()
    entree_cl, build = (None, None) if a.sans_changelog else changelog(src, a.seance, log, prevue, modele, km_gear, date)
    ref_txt = maj_reference(e, modele, date, ajouter_activite=not existe)
    gen_txt = maj_gen(src, modele, km_gear, entree_cl)
    log_txt = json.dumps(log, ensure_ascii=False, indent=1) + "\n"

    if a.sec:
        print(log_txt)
        print(entree_cl or "")
        return 0
    os.makedirs(LOGS, exist_ok=True)
    for chemin, txt in ((cible, log_txt), (REF, ref_txt), (GEN, gen_txt)):
        with open(chemin, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)
    r = log["realise"]
    print(f"{a.seance} : {virgule(r['km'])} km, {r['temps']}, {r['allure']}, FC {r['fc_moy']}/{r['fc_max']}, "
          f"terrain {r['terrain']}" + (f", decouplage {r['decouplage'].get('qualite')}" if "decouplage" in r else "")
          + (f" | {modele} {km_gear} km" if modele else " | chaussure inconnue")
          + (f" | build {build}" if build else ""))
    if "date" in log["seance"]:
        print(f"Date differente du plan : {prevue.get('date')} -> {date}")
    if a.rewind:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import rewind_seance
        rewind_seance.ecrire(a.seance, a.rewind, rewind_seance.cible(a.cible_allure, a.cible_fc, a.cible_source))
    if not os.path.exists(os.path.join(SRC, "textes", "seances", f"{a.seance}.html")):
        print(f"A FAIRE : ecrire la revue dans src/textes/seances/{a.seance}.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
