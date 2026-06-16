#!/usr/bin/env python3
import json, os, hashlib, unicodedata, struct
from fit_encode import fit_file, step, fit_crc

def deburr(s):
    s=s.replace("’","'").replace("×","x").replace("…","...")
    return ''.join(c for c in unicodedata.normalize('NFKD',s) if not unicodedata.combining(c))

# Cibles d'allure ('speed', low_slower, high_faster) — convention identique à S25-3
SP_AM=('speed','5:20','5:10')      # allure marathon ~5:15/km
SP_S30=('speed','4:45','4:35')     # seuil 30 ~4:40/km
SP_S60=('speed','5:00','4:50')     # seuil 60 ~4:55/km
SP_EF=('speed','6:25','5:50')      # endurance facile

NAME={"seuil":None,"allure-marathon":"Allure marathon","sortie-longue":"Sortie longue",
      "cotes":"Cotes pyramide","test-10km":"Test 10km","deraille":"Prepa Deraille",
      "footing-lignes":"EF + lignes droites","footing-facile":"Footing facile"}

def seg_to_step(seg, idx, last_idx, stype, sub):
    name=deburr(seg['nom'])[:30]
    coul=seg['couleur']
    dur=('time', int(seg['duree']))
    # intensité de base
    if idx==0:        kind='warmup'
    elif idx==last_idx: kind='cooldown'
    elif coul=='orange': kind='rest'
    else: kind='active'
    target=None
    if kind=='active':
        if coul=='bleu':
            if stype.startswith('Côtes'):
                target=None  # côte : effort/relief, pas de cible d'allure
            elif stype=='Spécifique marathon' or stype.startswith('Sortie longue'):
                target=SP_AM
                # fiche exprime le bloc en km → encoder en distance pour cohérence montre/app
                # durée bâtie depuis km_each*5.25*60 → conversion inverse exacte
                dist_m = round(int(seg['duree']) / (5.25 * 60) * 1000)
                dur = ('distance', dist_m)
            elif stype.startswith('Seuil'):
                target=SP_S60 if sub=='Seuil 60' else SP_S30
                # fiche exprime le bloc en minutes → garder en temps
        elif coul=='rouge':
            target=None  # test 10 km : effort libre
        elif coul=='violet':
            target=None  # marqueur gel/ravito
        elif coul=='vert':
            target=SP_EF  # corps EF / transition à allure facile
    return step(name, kind, dur, target)

def wkt_name(wk, slug, sub):
    base = sub if slug=='seuil' else NAME.get(slug) or slug
    return deburr(f"S{wk} {base}")[:23]

def build_all(data_path, out_dir):
    d=json.load(open(data_path))
    sbw=d['SBW']
    os.makedirs(out_dir, exist_ok=True)
    made=[]
    for wk,arr in sbw.items():
        if not (25<=int(wk)<=53): continue
        for s in arr:
            fit=s.get('fit')
            if not fit: continue
            base=fit.split('/')[-1]
            slug=base.rsplit('-',1)[0].split('-',2)[-1] if base.count('-')>=2 else 'sortie-longue'
            # slug fiable : dérive du nom de fichier "S{wk}-{num}-{slug}.fit"
            slug=base[:-4].split('-',2)[2]
            stype=s['type']; sub=(s.get('metriques') or {}).get('Type','')
            segs=s.get('segments')
            if not segs:
                import re as _re
                mins=55; dm=_re.search(r'(\d+)\s*min',(s.get('metriques') or {}).get('Durée',''))
                if dm: mins=int(dm.group(1))
                body=max(600,(mins-15)*60)
                steps=[step('Echauffement','warmup',('time',600),None),
                       step('Endurance facile','active',('time',body),SP_EF),
                       step('Retour au calme','cooldown',('time',300),None)]
            else:
                last=len(segs)-1
                steps=[seg_to_step(seg,i,last,stype,sub) for i,seg in enumerate(segs)]
            serial=int(hashlib.md5(base.encode()).hexdigest(),16)%90000+1000
            blob=fit_file(wkt_name(wk,slug,sub), steps, serial)
            open(os.path.join(out_dir,base),'wb').write(blob)
            made.append((base,len(blob),len(steps)))
    return made

if __name__=='__main__':
    made=build_all('/tmp/data.json','/tmp/fit_out')
    print(f"{len(made)} fichiers .fit générés")
    # auto-validation CRC + parsabilité
    bad=0
    for base,ln,nst in made:
        b=open(f'/tmp/fit_out/{base}','rb').read()
        if fit_crc(b[:-2])!=struct.unpack('<H',b[-2:])[0]:
            print("  CRC FAIL", base); bad+=1
    print("Tous CRC OK" if bad==0 else f"{bad} CRC en échec")
    # échantillon
    for base,ln,nst in made[:6]:
        print(f"  {base:32s} {ln:4d} o  {nst} steps")
