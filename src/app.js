/* ===== helpers ===== */
function rpeColor(r){return r<=3?'#22c55e':r<=5?'#3b82f6':r<=6.9?'#eab308':r<=8?'#f97316':'#ef4444';}
function rpeScale(r){let h='';for(let i=1;i<=10;i++){const on=i<=Math.round(r);h+=`<div class="rpe-seg" style="background:${on?rpeColor(r):''}"></div>`;}return h;}
function catBadge(c){return c==='specifique'?'<span class="cat-badge cat-specifique">Spécifique</span>':'<span class="cat-badge cat-classique">Classique</span>';}
function stChip(st){const m={a_faire:['st-afaire','À faire'],fait:['st-fait','Fait ✓'],partiel:['st-partiel','Partiel'],manque:['st-manque','Manqué']};const x=m[st]||m.a_faire;return `<span class="st-chip ${x[0]}">${x[1]}</span>`;}
function prCelebration(o){if(!o)return'';const pr=o.pr||0,ach=o.ach||0;if(pr+ach<=0)return'';
  const parts=[];if(pr>0)parts.push(`<span class="prc-stat"><span class="prc-n">${pr}</span> record${pr>1?'s':''} perso</span>`);
  if(ach>0)parts.push(`<span class="prc-stat"><span class="prc-n">${ach}</span> trophée${ach>1?'s':''} de segment</span>`);
  const detail=(o.pr_detail&&o.pr_detail.length)?`<div class="prc-detail">${o.pr_detail.map(d=>`<span class="prc-chip">🥇 ${d}</span>`).join('')}</div>`:'';
  return `<div class="prc"><div class="prc-burst">🎉</div><div class="prc-body"><div class="prc-titre">Records tombés !</div><div class="prc-row">${parts.join('<span class="prc-sep">·</span>')}</div>${detail}</div></div>`;}
function fmt(s){const m=Math.floor(s/60),x=s%60;return x?`${m} min ${String(x).padStart(2,'0')}`:`${m} min`;}
function paceFmt(s){const m=Math.floor(s/60),x=Math.round(s%60);return `${m}:${String(x).padStart(2,'0')}`;}
function isoWeek(d){d=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()));const day=d.getUTCDay()||7;d.setUTCDate(d.getUTCDate()+4-day);const ys=new Date(Date.UTC(d.getUTCFullYear(),0,1));return Math.ceil((((d-ys)/86400000)+1)/7);}

/* ===== graphes SVG ===== */
function chartLine(vals,o){o=o||{};const color=o.color||'#3b82f6',h=o.h||150,fmtY=o.fmtY||(v=>v),baseline=o.baseline,todayIdx=o.todayIdx,labels=o.labels;
  const W=720,pad=30,padB=22,padT=12;const idx=vals.map((v,i)=>[i,v]).filter(p=>p[1]!=null);if(!idx.length)return'';
  const ys=idx.map(p=>p[1]);let max=Math.max(...ys),min=Math.min(...ys);if(baseline!=null){max=Math.max(max,baseline);min=Math.min(min,baseline);}
  const rng=(max-min)||1;max+=rng*0.12;min-=rng*0.12;if(min<0&&Math.min(...ys)>=0)min=0;max=Math.ceil(max);min=Math.floor(min);const n=vals.length;
  const X=i=>pad+(W-pad-12)*i/(n-1);const Y=v=>padT+(h-padT-padB)*(1-(v-min)/(max-min));
  let line='',area='',lastX=0;idx.forEach((p,k)=>{const cx=X(p[0]),cy=Y(p[1]);if(k===0){line=`M ${cx.toFixed(1)} ${cy.toFixed(1)}`;area=`M ${cx.toFixed(1)} ${(h-padB).toFixed(1)} L ${cx.toFixed(1)} ${cy.toFixed(1)}`;}else{line+=` L ${cx.toFixed(1)} ${cy.toFixed(1)}`;area+=` L ${cx.toFixed(1)} ${cy.toFixed(1)}`;}lastX=cx;});
  area+=` L ${lastX.toFixed(1)} ${(h-padB).toFixed(1)} Z`;
  let bl='';if(baseline!=null){const by=Y(baseline);bl=`<line x1="${pad}" y1="${by.toFixed(1)}" x2="${W-12}" y2="${by.toFixed(1)}" stroke="#ef4444" stroke-dasharray="4 4" stroke-width="1.2"/><text x="${W-14}" y="${(by-4).toFixed(1)}" font-size="9" fill="#ef4444" text-anchor="end">seuil 1.5</text>`;}
  let td='';if(todayIdx!=null){const tx=X(todayIdx);td=`<line x1="${tx.toFixed(1)}" y1="${padT}" x2="${tx.toFixed(1)}" y2="${h-padB}" stroke="#94a3b8" stroke-dasharray="3 3"/><text x="${tx.toFixed(1)}" y="9" font-size="8.5" fill="#94a3b8" text-anchor="middle">aujourd'hui</text>`;}
  const gid='g'+color.replace('#','');
  const yl=`<text x="2" y="${(Y(max)+8).toFixed(1)}" font-size="9" fill="#94a3b8">${fmtY(max)}</text><text x="2" y="${(Y(min)+2).toFixed(1)}" font-size="9" fill="#94a3b8">${fmtY(min)}</text>`;
  let xl='';if(labels){xl=idx.filter((_,k)=>k%Math.ceil(idx.length/6)===0).map(p=>`<text x="${X(p[0]).toFixed(1)}" y="${h-6}" font-size="8" fill="#94a3b8" text-anchor="middle">${labels[p[0]]||''}</text>`).join('');}
  let ann='';if(o.annotate){const pp=[];for(let i=0;i<vals.length;i++){if(vals[i]==null)continue;const a=(i>0?vals[i-1]:null),b=(i<vals.length-1?vals[i+1]:null);let lab=false,up=true;if(a==null||b==null){lab=true;up=(b!=null?vals[i]>=b:(a!=null?vals[i]>=a:true));}else if(vals[i]>a&&vals[i]>=b){lab=true;up=true;}else if(vals[i]<a&&vals[i]<=b){lab=true;up=false;}if(lab)pp.push({i,up});}ann=pp.map(p=>`<text x="${X(p.i).toFixed(1)}" y="${(p.up?Y(vals[p.i])-6:Y(vals[p.i])+13).toFixed(1)}" font-size="9" font-weight="700" fill="#94a3b8" text-anchor="middle">${fmtY(vals[p.i])}</text>`).join('');}
  return `<svg viewBox="0 0 ${W} ${h}" class="chart-svg"><defs><linearGradient id="${gid}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${color}" stop-opacity=".32"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></linearGradient></defs>${bl}<path d="${area}" fill="url(#${gid})"/><path d="${line}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linejoin="round"/>${td}${ann}${yl}${xl}</svg>`;
}
function svgMountain(){const wks=SEMAINES.filter(s=>s.num>=25);const W=760,h=195,padT=24,padB=26,padX=10,n=wks.length,maxKm=92;
  const X=i=>padX+(W-2*padX)*i/(n-1);const Y=km=>padT+(h-padT-padB)*(1-km/maxKm);
  const line='M '+wks.map((w,i)=>`${X(i).toFixed(1)} ${Y(w.km).toFixed(1)}`).join(' L ');
  const area=`M ${X(0).toFixed(1)} ${h-padB} `+wks.map((w,i)=>`L ${X(i).toFixed(1)} ${Y(w.km).toFixed(1)} `).join('')+`L ${X(n-1).toFixed(1)} ${h-padB} Z`;
  const mk=(num,emoji,lab,up)=>{const i=wks.findIndex(w=>w.num===num);if(i<0)return'';const cx=X(i),cy=Y(wks[i].km);return `<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="3.5" fill="#fff" stroke="#475569" stroke-width="2"/><text x="${cx.toFixed(1)}" y="${(up?cy-8:cy+15).toFixed(1)}" font-size="12" text-anchor="middle">${emoji}</text><text x="${cx.toFixed(1)}" y="${up?(cy-21).toFixed(1):(h-7)}" font-size="8.5" fill="#64748b" text-anchor="middle" font-weight="700">${lab}</text>`;};
  const tpidx=[];wks.forEach((w,i)=>{const a=i>0?wks[i-1].km:null,b=i<n-1?wks[i+1].km:null;let lab=false;if(a==null||b==null)lab=true;else if((w.km>a&&w.km>=b)||(w.km<a&&w.km<=b))lab=true;if(lab&&![42,37,45,48].includes(w.num))tpidx.push(i);});
  const kmlab=tpidx.map(i=>{const w=wks[i];const up=(i>0)?(w.km>=wks[i-1].km):true;return `<text x="${X(i).toFixed(1)}" y="${(up?Y(w.km)-6:Y(w.km)+13).toFixed(1)}" font-size="8.5" font-weight="700" fill="#94a3b8" text-anchor="middle">${w.km}</text>`;}).join('');
  const cur=`<circle cx="${X(0).toFixed(1)}" cy="${Y(wks[0].km).toFixed(1)}" r="7" fill="#22c55e" opacity=".25"/><circle cx="${X(0).toFixed(1)}" cy="${Y(wks[0].km).toFixed(1)}" r="3.5" fill="#22c55e"/>`;
  const cols=wks.map((w,i)=>`<rect x="${(X(i)-(W-2*padX)/n/2).toFixed(1)}" y="0" width="${((W-2*padX)/n).toFixed(1)}" height="${h}" fill="transparent" style="cursor:pointer" onclick="ouvrirSemaine(${w.num})"><title>S${w.num} · ${w.theme} · ${w.km} km</title></rect>`).join('');
  return `<svg viewBox="0 0 ${W} ${h}" class="chart-svg"><defs><linearGradient id="mtn" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#f97316" stop-opacity=".45"/><stop offset=".55" stop-color="#3b82f6" stop-opacity=".2"/><stop offset="1" stop-color="#22c55e" stop-opacity="0"/></linearGradient></defs><path d="${area}" fill="url(#mtn)"/><path d="${line}" fill="none" stroke="#475569" stroke-width="2"/>${mk(42,'⛰️','Pic 88',true)}${mk(37,'🏕️','USA',false)}${mk(45,'🏁','Nice',true)}${mk(48,'🌙','SaintExpress',false)}${cur}${kmlab}${cols}</svg>`;
}
function svgDonut(segs){const tot=segs.reduce((a,s)=>a+s.val,0)||1;let a=-90,paths='';const R=54,r=31,cx=64,cy=64;
  segs.forEach(s=>{const ang=s.val/tot*360,a2=a+ang;const P=(deg,rad)=>[cx+rad*Math.cos(Math.PI*deg/180),cy+rad*Math.sin(Math.PI*deg/180)];const large=ang>180?1:0;const[x1,y1]=P(a,R),[x2,y2]=P(a2,R),[x3,y3]=P(a2,r),[x4,y4]=P(a,r);paths+=`<path d="M ${x1.toFixed(1)} ${y1.toFixed(1)} A ${R} ${R} 0 ${large} 1 ${x2.toFixed(1)} ${y2.toFixed(1)} L ${x3.toFixed(1)} ${y3.toFixed(1)} A ${r} ${r} 0 ${large} 0 ${x4.toFixed(1)} ${y4.toFixed(1)} Z" fill="${s.color}"/>`;a=a2;});
  return `<svg viewBox="0 0 128 128" width="120" height="120">${paths}</svg>`;
}

function delta(series,good){const v=series.filter(x=>x!=null);if(v.length<2)return'';const d=v[v.length-1]-v[v.length-2];if(Math.abs(d)<0.5&&good!=='down')return '<span class="delta" style="color:#94a3b8">\u25aa stable</span>';const up=d>0;const isGood=good?((good==='up'&&up)||(good==='down'&&!up)):null;const col=isGood===null?'#64748b':(isGood?'#22c55e':'#ef4444');const a=up?'\u25b2':'\u25bc';const val=Math.abs(d)>=1?Math.round(Math.abs(d)):Math.abs(d).toFixed(1);return `<span class="delta" style="color:${col}">${a} ${val} vs S-1</span>`;}

/* ===== thème ===== */
function toggleTheme(){const n=document.body.classList.toggle('nuit');document.getElementById('themebtn').textContent=n?'☀️':'🌙';}

/* ===== onglets ===== */
function showTab(t){document.getElementById('vue-plan').style.display=t==='plan'?'block':'none';document.getElementById('vue-dash').style.display=t==='dash'?'block':'none';document.getElementById('tab-plan').classList.toggle('actif',t==='plan');document.getElementById('tab-dash').classList.toggle('actif',t==='dash');if(t==='dash')renderDash();window.scrollTo(0,0);}

/* ===== header + hero ===== */
function prochaineSeance(){
  const t=new Date();t.setHours(0,0,0,0);let best=null;
  Object.entries(SEANCES_BY_WEEK).forEach(([wk,arr])=>arr.forEach(se=>{
    if(!se.date)return;
    const done=se.realise&&(se.realise.statut==='fait'||se.realise.statut==='partiel');
    if(done)return;
    const d=new Date(se.date+'T00:00:00');
    if(d>=t&&(!best||d<best.d))best={d:d,wk:+wk,se:se};
  }));
  return best;
}

function renderHeader(){
  const cur=isoWeek(new Date());const sc=SEMAINES.find(s=>s.num===cur)||SEMAINES[0];
  const nx=SEMAINES.find(s=>s.num===cur+1)||SEMAINES.find(s=>s.num===25);
  let heroNow;
  if(sc.statut==='courante'){const r=S24R.runs.length;heroNow=`<div class="hero-card hero-now" onclick="ouvrirSemaine(${sc.num})"><div class="hero-l">Cette semaine \u00b7 S${sc.num}</div><div class="hero-t">${sc.theme}</div><div class="hero-s">${r} sorties réalisées \u00b7 récupération post-Circaète \u2192</div></div>`;}
  else{const ses=SEANCES_BY_WEEK[sc.num]||[];const f=ses.filter(x=>x.realise&&x.realise.statut!=='a_faire').length;heroNow=`<div class="hero-card hero-now" onclick="ouvrirSemaine(${sc.num})"><div class="hero-l">Cette semaine \u00b7 S${sc.num}</div><div class="hero-t">${sc.theme}</div><div class="hero-s">${f}/${ses.length} séances \u00b7 ${sc.km} km \u2192</div></div>`;}
  const heroNext=nx?`<div class="hero-card hero-next" onclick="ouvrirSemaine(${nx.num})"><div class="hero-l">À suivre \u00b7 S${nx.num}</div><div class="hero-t" style="font-size:1.05rem">${nx.theme}</div><div class="hero-s">${nx.km} km \u00b7 ${nx.charge} \u2192</div></div>`:'';
  const _t=new Date();_t.setHours(0,0,0,0);
  const _ps=prochaineSeance();let _psCard='';
  if(_ps){
    const _diff=Math.round((_ps.d-_t)/86400000);
    const _J=['dimanche','lundi','mardi','mercredi','jeudi','vendredi','samedi'];
    const _M=['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.'];
    const _jn=_J[_ps.d.getDay()];
    const _lbl=_diff===0?"Aujourd'hui":_diff===1?'Demain':_jn.charAt(0).toUpperCase()+_jn.slice(1)+' '+_ps.d.getDate()+' '+_M[_ps.d.getMonth()];
    const _se=_ps.se;
    const _fit=_se.fit?`<a class="vdj-fit" href="${_se.fit}" download onclick="event.stopPropagation()">⌚ Télécharger la séance</a>`:'';
    const _dist=(_se.metriques&&_se.metriques.Distance)?' · '+_se.metriques.Distance:'';
    _psCard=`<div class="vdj" onclick="ouvrirSeance(${_ps.wk},${_se.id})"><div class="vdj-lbl">Prochaine séance · ${_lbl}</div><div class="vdj-t">${_se.titre}</div><div class="vdj-s">${_se.type}${_dist} · S${_ps.wk}</div>${_fit}</div>`;
  }
  let _cd='';
  if(RACES&&RACES.length){
    const _it=RACES.map(r=>{const _dn=Math.max(0,Math.ceil((new Date(r.date)-_t)/86400000));return `<div class="vdj-cd-item"><span class="vdj-cd-n">J-${_dn}</span><span class="vdj-cd-l">${r.nom}</span></div>`;}).join('<div class="vdj-cd-sep"></div>');
    _cd=`<div class="vdj-cd">${_it}</div>`;
  }
  const _maj=`<div class="vdj-maj">Données à jour au ${MAJ}</div>`;
  const _h=document.getElementById('hero');_h.style.display='flex';
  _h.innerHTML=`${_psCard}${_cd}<div class="hero-sem">${heroNow}${heroNext}</div>${_maj}`;
}

/* ===== PLAN ===== */
function renderPlan(){const phasesEl=document.getElementById('phases');phasesEl.innerHTML='';
  PHASES.forEach(ph=>{const bloc=document.createElement('div');bloc.className='phase-bloc';const sems=SEMAINES.filter(s=>s.phase===ph.id);
    const cartes=sems.map(s=>{const ses=SEANCES_BY_WEEK[s.num]||[];const fait=ses.filter(x=>x.realise&&(x.realise.statut==='fait'||x.realise.statut==='partiel')).length;
      const cnt=s.num===24?`<div class="sem-km" style="margin-top:4px"><span>${S24R.runs.length} sorties · ${S24R.km} km réalisés</span></div>`:(ses.length?`<div class="sem-km" style="margin-top:4px"><span>${fait}/${ses.length} séances</span></div>`:'');
      const badge=s.statut==='courante'?`<div class="sem-statut st-courante">Courante</div>`:'';
      return `<div class="sem-carte cliquable" onclick="ouvrirSemaine(${s.num})">${badge}<div class="sem-num">Semaine ${s.num}</div><div class="sem-theme">${s.theme}</div><div class="sem-km">${s.km} <span>km · ${s.charge}</span></div>${cnt}<div class="sem-barre"><div class="sem-barre-fill" style="width:${Math.min(100,s.km/88*100)}%;background:${ph.c}"></div></div></div>`;}).join('');
    bloc.innerHTML=`<div class="phase-entete"><div class="phase-puce" style="background:${ph.c}"></div><div class="phase-nom">${ph.nom}</div><div class="phase-sem">${ph.sem}</div></div><p class="phase-role">${ph.role}</p><div class="sem-grille">${cartes}</div>`;
    phasesEl.appendChild(bloc);});
}

/* ===== TABLEAU DE BORD ===== */
/* ===== Calendrier d'entraînement ===== */
let calMonth=null;
function calEvents(){
  const evs=[];const today=new Date();today.setHours(0,0,0,0);
  Object.entries(SEANCES_BY_WEEK).forEach(([wk,arr])=>arr.forEach(se=>{
    if(!se.date)return;
    const done=se.realise&&(se.realise.statut==='fait'||se.realise.statut==='partiel');
    const d=new Date(se.date+'T00:00:00');
    const color=done?'g':(d<today?'o':'x');
    evs.push({iso:se.date,color,titre:se.titre,open:'ouvrirSeance('+wk+','+se.id+')'});
  }));
  (typeof S24R!=='undefined'&&S24R.runs?S24R.runs:[]).forEach((r,i)=>{
    if(r.iso)evs.push({iso:r.iso,color:'g',titre:r.titre,open:'ouvrirSeanceS24('+i+')'});
  });
  return evs;
}
function calHTML(){
  if(!calMonth){calMonth=new Date();calMonth.setDate(1);calMonth.setHours(0,0,0,0);}
  const y=calMonth.getFullYear(),m=calMonth.getMonth();
  const MN=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];
  const evs=calEvents();
  const start=(new Date(y,m,1).getDay()+6)%7;
  const ndays=new Date(y,m+1,0).getDate();
  const todayISO=new Date().toISOString().slice(0,10);
  const dow=['L','M','M','J','V','S','D'];
  let cells=dow.map(d=>'<div class="cal-dow">'+d+'</div>').join('');
  for(let i=0;i<start;i++)cells+='<div class="cal-cell cal-empty"></div>';
  for(let day=1;day<=ndays;day++){
    const iso=y+'-'+String(m+1).padStart(2,'0')+'-'+String(day).padStart(2,'0');
    const de=evs.filter(e=>e.iso===iso);
    const tdy=iso===todayISO?' cal-today':'';
    if(de.length){
      const e=de[0];
      cells+='<button type="button" class="cal-cell cal-'+e.color+tdy+'" onclick="'+e.open+'" title="'+e.titre.replace(/"/g,'')+'"><span class="cal-num">'+day+'</span><span class="cal-dot"></span></button>';
    }else{
      cells+='<div class="cal-cell'+tdy+'"><span class="cal-num cal-muted">'+day+'</span></div>';
    }
  }
  return '<div class="cal-head"><button class="cal-nav" onclick="calNav(-1)">‹</button><div class="cal-title">'+MN[m]+' '+y+'</div><button class="cal-nav" onclick="calNav(1)">›</button></div>'+
    '<div class="cal-grid">'+cells+'</div>'+
    '<div class="cal-legend"><span><i class="cal-lg cal-g"></i>Réalisé</span><span><i class="cal-lg cal-o"></i>Non réalisé</span><span><i class="cal-lg cal-x"></i>À venir</span><span style="opacity:.45;margin-left:auto">build 10</span></div>';
}
function calNav(d){calMonth.setMonth(calMonth.getMonth()+d);const w=document.getElementById('cal-inner');if(w)w.innerHTML=calHTML();}

/* ===== Heatmap annuelle ===== */
function hmIso(d){return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
function heatColor(km){if(!km)return 'h0';if(km<6)return 'h1';if(km<12)return 'h2';if(km<20)return 'h3';return 'h4';}
function hmStats(){
  const days=Object.keys(HEATMAP).sort();
  let best=0,cur=0,prev=null;
  days.forEach(iso=>{const d=new Date(iso+'T00:00:00');if(prev&&Math.round((d-prev)/86400000)===1)cur++;else cur=1;if(cur>best)best=cur;prev=d;});
  const totalKm=Object.values(HEATMAP).reduce((a,b)=>a+b,0);
  return '🔥 Plus longue série : <strong>'+best+' jours</strong> · <strong>'+days.length+'</strong> jours courus · <strong>'+Math.round(totalKm)+' km</strong> en 2026';
}
function renderHeatmap(){
  const year=2026, jan1=new Date(year,0,1);
  const start=new Date(jan1); start.setDate(start.getDate()-((start.getDay()+6)%7));
  const todayISO=hmIso(new Date());
  const M=['Jan','Fév','Mar','Avr','Mai','Juin','Juil','Août','Sep','Oct','Nov','Déc'];
  let grid='',months='',lastM=-1;
  for(let w=0;w<53;w++){
    const monday=new Date(start);monday.setDate(start.getDate()+w*7);
    let ml='';
    if(monday.getFullYear()===year && monday.getMonth()!==lastM){ml=M[monday.getMonth()];lastM=monday.getMonth();}
    months+='<div class="hm-mlabel">'+ml+'</div>';
    let col='';
    for(let d=0;d<7;d++){
      const c=new Date(start);c.setDate(start.getDate()+w*7+d);
      if(c.getFullYear()!==year){col+='<div class="hm-cell hm-out"></div>';continue;}
      const iso=hmIso(c), km=HEATMAP[iso]||0, tdy=iso===todayISO?' hm-today':'';
      col+='<button type="button" class="hm-cell '+heatColor(km)+tdy+'" onclick="hmPick(\''+iso+'\','+km+')"></button>';
    }
    grid+='<div class="hm-col">'+col+'</div>';
  }
  return '<div class="hm-months">'+months+'</div><div class="hm-grid">'+grid+'</div>';
}
function hmPick(iso,km){
  const el=document.getElementById('hm-cap');if(!el)return;
  const d=new Date(iso+'T00:00:00');
  const M=['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.'];
  const J=['dim.','lun.','mar.','mer.','jeu.','ven.','sam.'];
  el.innerHTML=J[d.getDay()]+' '+d.getDate()+' '+M[d.getMonth()]+' — <strong>'+(km?String(km).replace('.',',')+' km':'repos')+'</strong>';
}

/* ===== Trophées & métaphores ===== */
function dashTotals(){
  const S=(typeof SAISON2026!=='undefined')?SAISON2026:{km:0,elev:0};
  const vals=Object.values(HEATMAP);
  const longest=vals.length?Math.max.apply(null,vals):0;
  const active=Object.keys(HEATMAP).length;
  const days=Object.keys(HEATMAP).sort();let best=0,cur=0,prev=null;
  days.forEach(iso=>{const d=new Date(iso+'T00:00:00');if(prev&&Math.round((d-prev)/86400000)===1)cur++;else cur=1;if(cur>best)best=cur;prev=d;});
  return {km:S.km,dplus:S.elev,longest:longest,active:active,streak:best};
}
function renderTrophees(){
  const t=dashTotals();
  const fmt=n=>Math.round(n).toLocaleString('fr-FR');
  const B=[
   {i:'🏃',n:'1 000 km',d:t.km>=1000,s:fmt(t.km)+' km'},
   {i:'⛰️',n:'10 000 m D+',d:t.dplus>=10000,s:fmt(t.dplus)+' m'},
   {i:'🥾',n:'Premier 30 km',d:t.longest>=30,s:Math.round(t.longest)+' km max'},
   {i:'🔥',n:'Série 7 jours',d:t.streak>=7,s:t.streak+" jours d'affilée"},
   {i:'💯',n:'100 jours courus',d:t.active>=100,s:t.active+' jours'},
   {i:'🏁',n:'Marathon bouclé',d:t.longest>=42,s:'MaraTrail'},
   {i:'🎯',n:'Marathon < 3h45',d:false,s:'Nice · 8 nov'},
   {i:'🌙',n:'Trail de nuit',d:false,s:'SaintExpress · 28 nov'}
  ];
  const cards=B.map(b=>'<div class="tr-badge'+(b.d?' tr-on':'')+'"><div class="tr-i">'+b.i+'</div><div class="tr-n">'+b.n+'</div><div class="tr-s">'+b.s+'</div>'+(b.d?'<div class="tr-chk">✓</div>':'<div class="tr-lock">🔒</div>')+'</div>').join('');
  const maras=t.km/42.195, mb=t.dplus/4807, ev=t.dplus/8849;
  const meta='📏 <strong>'+fmt(t.km)+' km</strong> en 2026, soit <strong>'+maras.toFixed(0)+' marathons</strong> enchaînés.<br>⛰️ <strong>'+fmt(t.dplus)+' m</strong> de D+, soit <strong>'+mb.toFixed(1)+'× le Mont Blanc</strong> gravi ('+ev.toFixed(1)+"× l'Everest depuis la mer).";
  return '<div class="tr-grid">'+cards+'</div><div class="tr-meta">'+meta+'</div>';
}

/* ===== Item 2 — Navigation dashboard (sections repliables + sous-nav collante) ===== */
const DASH_GROUPS=[
  {id:'cal',ic:'📅',t:"Aujourd'hui & calendrier"},
  {id:'annee',ic:'🔥',t:'Année & trophées'},
  {id:'saison',ic:'📊',t:'Saison en chiffres'},
  {id:'coach',ic:'🧠',t:'Analyse du coach'},
  {id:'charge',ic:'❤️',t:'Charge & physiologie'},
  {id:'perf',ic:'🏆',t:'Performances & objectifs'},
  {id:'profil',ic:'⛰️',t:'Profil & matériel'},
];
function dashGrpOpen(id){try{const v=localStorage.getItem('dash_grp_'+id);if(v===null)return id==='cal';return v==='1';}catch(e){return id==='cal';}}
function dashNav(){return `<div class="dash-nav" id="dash-nav">${DASH_GROUPS.map(g=>`<button class="dnav-chip" data-g="${g.id}" onclick="dashJump('${g.id}')">${g.ic} ${g.t}</button>`).join('')}</div>`;}
function dashApplyState(){DASH_GROUPS.forEach(g=>{const s=document.getElementById('grp-'+g.id);if(s)s.classList.toggle('open',dashGrpOpen(g.id));});}
function dashToggle(id){const s=document.getElementById('grp-'+id);if(!s)return;const open=!s.classList.contains('open');s.classList.toggle('open',open);try{localStorage.setItem('dash_grp_'+id,open?'1':'0');}catch(e){}}
function dashJump(id){const s=document.getElementById('grp-'+id);if(!s)return;if(!s.classList.contains('open')){s.classList.add('open');try{localStorage.setItem('dash_grp_'+id,'1');}catch(e){}}
  const nav=document.getElementById('dash-nav');nav&&nav.querySelectorAll('.dnav-chip').forEach(c=>c.classList.toggle('actif',c.dataset.g===id));
  const y=s.getBoundingClientRect().top+window.scrollY-(nav?nav.offsetHeight+58:64);window.scrollTo({top:y,behavior:'smooth'});}
function dgrpHead(id,ic,t){return `<section class="dgrp" id="grp-${id}"><button class="dgrp-head" onclick="dashToggle('${id}')"><span class="dgrp-ic">${ic}</span><span class="dgrp-t">${t}</span><span class="dgrp-arr">▾</span></button><div class="dgrp-body">`;}
function renderDash(){const el=document.getElementById('dash-contenu');
  const today=new Date();const cd=RACES.map(r=>Math.max(0,Math.ceil((new Date(r.date)-today)/86400000)));
  const allSe=Object.values(SEANCES_BY_WEEK).flat();const total=allSe.length;
  const faites=allSe.filter(s=>s.realise&&(s.realise.statut==='fait'||s.realise.statut==='partiel')).length;
  const planKm=1947;
  const realKm=allSe.reduce((a,s)=>a+((s.realise&&s.realise.km)||0),0);
  const planPct=faites>0?Math.round(faites/total*100):0;

  // Graphe mensuel (barres SVG)
  function svgMonthly(key,col,fmtV){
    const vals=MONTHLY.map(m=>m[key]);const max=Math.max(...vals)||1;
    const W=700,h=110,padL=36,padB=28,bw=60,gap=14;
    const bars=MONTHLY.map((m,i)=>{const x=padL+i*(bw+gap);const bh=(m[key]/max)*(h-padB-10);const y=h-padB-bh;
      return `<rect x="${x}" y="${y.toFixed(1)}" width="${bw}" height="${bh.toFixed(1)}" rx="5" fill="${col}" opacity=".85"/>
        <text x="${(x+bw/2).toFixed(1)}" y="${(y-4).toFixed(1)}" font-size="9.5" font-weight="700" fill="#94a3b8" text-anchor="middle">${fmtV(m[key])}</text>
        <text x="${(x+bw/2).toFixed(1)}" y="${h-10}" font-size="9" fill="#94a3b8" text-anchor="middle">${m.m}</text>`;}).join('');
    return `<svg viewBox="0 0 ${W} ${h}" class="chart-svg">${bars}</svg>`;
  }

  // Donut polarisation
  const pol=[{label:'Très facile',val:POLAR.tres_facile,color:'#86efac'},{label:'EF facile',val:POLAR.ef,color:'#22c55e'},{label:'Zone grise',val:POLAR.gris,color:'#f59e0b'},{label:'Qualité',val:POLAR.qualite,color:'#ef4444'}];
  const histKm=HIST.map(h=>h.km);const histRe=HIST.map(h=>h.re);const histLab=HIST.map(h=>h.sem);

  // Couleur ACWR
  const acwr=ACWR_DATA.acwr;const acwrCol=acwr>1.5?'#ef4444':acwr<0.8?'#3b82f6':'#22c55e';
  const acwrLabel=acwr>1.5?'Attention — charge élevée':acwr<0.8?'Frais / allègement':'Charge maîtrisée';

  // Chaussures
  const maxShKm=Math.max(...GEAR.map(g=>g.km));
  const shoes=GEAR.slice().sort((a,b)=>b.km-a.km).map(g=>{
    const col=g.km>900?'#ef4444':g.km>700?'#f97316':'#22c55e';
    const al=g.km>900?`<div class="shoe-alert">⚠ ${g.km} km — remplacement à envisager</div>`:'';
    return `<div><div class="shoe-row"><div class="shoe-name">${g.marque} ${g.modele}</div><div class="shoe-track"><div class="shoe-fill" style="width:${g.km/maxShKm*100}%;background:${col}"></div></div><div class="shoe-km">${g.km} km</div></div>${al}</div>`;}).join('');

  el.innerHTML=dashNav()+dgrpHead('cal','📅',"Aujourd'hui & calendrier")+`
  <!-- 0. Calendrier -->
  <div class="kpi cal-block">
    <div class="kpi-t">🗓️ Calendrier d'entraînement</div>
    <div class="kpi-r">Clique un jour coloré pour ouvrir la séance. Vert : réalisé · Orange : prévu non réalisé · Gris : à venir.</div>
    <div id="cal-inner">${calHTML()}</div>
  </div>
  </div></section>`+dgrpHead('annee','🔥','Année & trophées')+`
  <!-- 0b. Heatmap annuelle -->
  <div class="kpi">
    <div class="kpi-t">🔥 Ton année en un coup d'oeil</div>
    <div class="kpi-r" style="margin-bottom:12px">${hmStats()}</div>
    <div class="hm-scroll">${renderHeatmap()}</div>
    <div id="hm-cap" class="hm-cap">Touche une case pour le détail du jour.</div>
    <div class="hm-legend">Moins<i class="hm-cell h1"></i><i class="hm-cell h2"></i><i class="hm-cell h3"></i><i class="hm-cell h4"></i>Plus</div>
  </div>
  <!-- 0c. Trophees -->
  <div class="kpi">
    <div class="kpi-t">🏆 Tes trophées 2026</div>
    ${renderTrophees()}
  </div>
  </div></section>`+dgrpHead('saison','📊','Saison en chiffres')+`
  <!-- 1. Saison en chiffres -->
  <div class="kpi">
    <div class="kpi-t">📅 Ta saison 2026 en chiffres</div>
    <div class="kpi-r">Depuis le 1er janvier 2026 · <strong>Run + Trail uniquement</strong>, aligné sur Strava (108 activités). Hikes et raquettes non inclus dans le compteur Strava running.</div>
    <div class="dash-stats" style="margin-bottom:18px">
      <div class="dstat" style="--accent:#3b82f6"><div class="dstat-l">Sorties</div><div class="dstat-v">${SAISON2026.sorties}</div><div class="dstat-s">en ${SAISON2026.mois} mois</div></div>
      <div class="dstat" style="--accent:#22c55e"><div class="dstat-l">Kilométrage</div><div class="dstat-v">${SAISON2026.km}</div><div class="dstat-s">km parcourus</div></div>
      <div class="dstat" style="--accent:#f97316"><div class="dstat-l">Dénivelé +</div><div class="dstat-v">${SAISON2026.elev.toLocaleString()}</div><div class="dstat-s">mètres</div></div>
      <div class="dstat" style="--accent:#8b5cf6"><div class="dstat-l">Prépa plan</div><div class="dstat-v">${faites}/${total}</div><div class="dstat-s">séances réalisées</div></div>
    </div>
    <div class="kpi-t" style="font-size:.88rem;margin-bottom:8px">Volume mensuel (km)</div>
    ${svgMonthly('km','#3b82f6',v=>Math.round(v))}
    <div style="margin-top:14px">
    <div class="kpi-t" style="font-size:.88rem;margin-bottom:8px">Dénivelé mensuel (m)</div>
    ${svgMonthly('elev','#f97316',v=>v>=1000?(v/1000).toFixed(1)+'k':v)}</div>
    <div style="margin-top:14px">
    <div class="kpi-t" style="font-size:.88rem;margin-bottom:8px">Sorties par mois</div>
    ${svgMonthly('sorties','#8b5cf6',v=>v)}</div>
  </div>

  </div></section>`+dgrpHead('coach','🧠','Analyse du coach')+`
  <!-- 3. Analyse du coach : zone grise + consignes + journal -->
  <div class="kpi">
    <div class="kpi-t">🧠 L'analyse du coach</div>
    <div class="kpi-r">Ta répartition d'intensité réelle sur les 6 derniers mois — le diagnostic central de ta préparation.</div>
    <div class="donut-wrap">${svgDonut(pol)}<div class="donut-leg">${pol.map(p=>`<div><i style="background:${p.color}"></i>${p.label} — <strong>${p.val}%</strong></div>`).join('')}</div></div>
    <div class="rev-coach" style="margin-top:14px">
      <strong>Le verdict :</strong> ${POLAR.gris}% de tes km en « zone grise » — ni assez lent pour récupérer, ni assez rapide pour progresser. C'est le problème n°1 à corriger.<br><br>
      <strong>Tes 3 règles pour la prépa :</strong><br>
      ① <strong>Footings faciles : ≥ 6:00/km</strong>, sans négocier. Si tu accélères sans le vouloir, c'est le réflexe zone grise.<br>
      ② <strong>Qualité = 2 séances/semaine max</strong>, distinctes et délibérées (seuil, AM, côtes).<br>
      ③ <strong>Facile vraiment facile, dur vraiment dur</strong> — la polarisation, c'est ça.
    </div>
    <div style="margin-top:14px"><div class="kpi-t" style="font-size:.88rem;margin-bottom:10px">📓 Journal du coach</div>
    ${JOURNAL.map(j=>`<div class="jour-item"><div class="jour-h">${j.sem} — ${j.theme}</div><div class="jour-x">${j.texte}</div></div>`).join('')}</div>
  </div>

  </div></section>`+dgrpHead('charge','❤️','Charge & physiologie')+`
<!-- 6. Zones FC + allures -->
  <div class="kpi">
    <div class="kpi-t">❤️ Zones FC & allures correspondantes</div>
    <div class="kpi-r">Calculées sur ta FC max réelle (192 bpm). Les allures sont indicatives <strong>à plat</strong> — la FC reste le juge en côte ou par forte chaleur. À recaler après le test 10 km (S31).</div>
    <div class="zfc">${ZONES_FC.map(z=>`<div class="zfc-row"><span class="zfc-z" style="background:${z.col}">${z.z}</span><span class="zfc-n">${z.nom}</span><span class="zfc-b">${z.bpm} bpm</span><span class="zfc-p">${z.pct}</span><span class="zfc-a">${z.allure}</span></div>`).join('')}</div>
  </div>

  
  <!-- 4. Charge & fraîcheur -->
  <div class="kpi">
    <div class="kpi-t">❤️ Charge & fraîcheur</div>
    <div class="kpi-r">Ratio aigu/chronique calculé en <strong>fenêtres glissantes réelles</strong> (charge 7 jours vs moyenne sur 28 jours). Au-dessus de 1,5 : risque de blessure. En-dessous de 0,8 : allègement.</div>
    <div class="dash-stats">
      <div class="dstat" style="--accent:${acwrCol}"><div class="dstat-l">Charge 7 jours</div><div class="dstat-v">${ACWR_DATA.charge7j}</div><div class="dstat-s">RE (Relative Effort)</div></div>
      <div class="dstat" style="--accent:#64748b"><div class="dstat-l">Charge 28 jours / sem.</div><div class="dstat-v">${Math.round(ACWR_DATA.charge28j/4)}</div><div class="dstat-s">RE moyen / semaine</div></div>
      <div class="dstat" style="--accent:${acwrCol}"><div class="dstat-l">Ratio ACWR</div><div class="dstat-v" style="color:${acwrCol}">${acwr.toFixed(2)}</div><div class="dstat-s">${acwrLabel}</div></div>
    </div>
    <div class="rev-coach">${ACWR_DATA.interpretation}</div>
    <div style="margin-top:14px">${delta(histRe)} ${chartLine(histRe,{color:'#8b5cf6',labels:histLab,annotate:true,h:140})}</div>
  </div>

  <!-- 5. Volume hebdo -->
  <div class="kpi"><div class="kpi-t">📈 Ton volume — historique 28 semaines</div><div class="kpi-r">Tes vraies semaines Strava. Le plan prend le relais à la S25.</div>${delta(histKm)} ${chartLine(histKm,{color:'#3b82f6',labels:histLab,fmtY:v=>Math.round(v)+'km',annotate:true,h:150})}</div>

  </div></section>`+dgrpHead('perf','🏆','Performances & objectifs')+`
  <!-- 7. Allures d'entraînement -->
  <div class="kpi"><div class="kpi-t">⏱️ Tes allures d'entraînement</div><div class="kpi-r">Dont le <strong>seuil 30</strong> (proche 10 km) et le <strong>seuil 60</strong> (proche semi). À recaler après le test 10 km (S31).</div><div class="allure-grid">${ALLURES.map(a=>`<div class="allure"><div class="allure-v">${a.val}</div><div class="allure-n">${a.nom}</div><div class="allure-s">${a.sub}</div></div>`).join('')}</div></div>

  <!-- 8. Allures de course + records -->
  <div class="kpi">
    <div class="kpi-t">🏆 Performances & projections</div>
    <div class="kpi-r">Meilleurs efforts réels depuis ton Strava · à comparer avec tes projections actuelles. Le semi 2022 reste ta référence officielle (course).</div>
    <table style="width:100%;border-collapse:collapse;font-size:.84rem">
      <thead><tr style="color:var(--texte-trois);font-size:.65rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em">
        <th style="text-align:left;padding:7px 6px;border-bottom:1px solid var(--gris-clair)">Distance</th>
        <th style="text-align:center;padding:7px 6px;border-bottom:1px solid var(--gris-clair)">Record / référence</th>
        <th style="text-align:center;padding:7px 6px;border-bottom:1px solid var(--gris-clair)">Meilleur effort 2026</th>
        <th style="text-align:right;padding:7px 6px;border-bottom:1px solid var(--gris-clair)">Projeté aujourd'hui</th>
      </tr></thead>
      <tbody>${RECORDS_PERF.map((r,i)=>`<tr style="border-bottom:1px solid var(--gris-clair)">
        <td style="padding:9px 6px;font-weight:800">${r.dist}</td>
        <td style="padding:9px 6px;text-align:center"><div style="font-weight:700">${r.temps_rec||'—'}</div><div style="font-size:.7rem;color:var(--texte-trois)">${r.record_sub}</div></td>
        <td style="padding:9px 6px;text-align:center"><div style="font-weight:700;color:#3b82f6">${r.temps_act}</div><div style="font-size:.7rem;color:var(--texte-trois)">${r.actuel_sub}</div></td>
        <td style="padding:9px 6px;text-align:right"><div style="font-weight:700">${r.actuel}</div></td>
      </tr>`).join('')}</tbody>
    </table>
    <div style="margin-top:14px"><div class="kpi-t" style="font-size:.88rem;margin-bottom:8px">Allures de course estimées (Riegel)</div>
    <div class="course-grid">${ALLURES_COURSE.map(a=>`<div class="course-row"><span class="course-d">${a.d}</span><span class="course-t">${a.temps}</span><span class="course-a">${a.allure}</span></div>`).join('')}</div></div>
  </div>

  <!-- 9. Objectifs course -->
  <div class="kpi">
    <div class="kpi-t">🎯 Objectifs course</div>
    <div class="kpi-r">Deux objectifs, deux logiques différentes.</div>
    <div class="dash-stats">
      <div class="dstat" style="--accent:#f97316"><div class="dstat-l">J avant Nice</div><div class="dstat-v">J-${cd[0]}</div><div class="dstat-s">Marathon 8 nov. · objectif 3h45</div></div>
      <div class="dstat" style="--accent:#8b5cf6"><div class="dstat-l">J avant SaintExpress</div><div class="dstat-v">J-${cd[1]}</div><div class="dstat-s">45 km night trail 28 nov.</div></div>
    </div>
    <div class="rec-grid" style="margin-top:12px">
      <div class="rec"><div class="rec-v">3h45</div><div class="rec-l">Marathon objectif</div><div class="rec-s">Nice · 8 nov.</div></div>
      <div class="rec"><div class="rec-v" style="font-size:1.15rem">~3h38-3h42</div><div class="rec-l">Marathon projeté</div><div class="rec-s">depuis ta forme actuelle</div></div>
      <div class="rec"><div class="rec-v">Plaisir</div><div class="rec-l">SaintExpress 45 km</div><div class="rec-s">28 nov.</div></div>
    </div>
    <div class="rev-coach" style="margin-top:14px">La stratégie : <strong>cibler 3h45 (5:20/km)</strong> et laisser le corps aller chercher 3h38-3h42 si tout va bien le jour J. L'erreur classique sur un premier marathon avec objectif ambitieux = partir sur la projection et exploser aux 35 km. Ici on part prudent et on accélère si le corps l'autorise.</div>
  </div>

  </div></section>`+dgrpHead('profil','⛰️','Profil & matériel')+`
<!-- 2. Profil de saison -->
  <div class="kpi"><div class="kpi-t">⛰️ Le profil de ta saison — plan S25→S53</div><div class="kpi-r">Ta périodisation vue comme une ascension : montée vers le pic 88 km (S42), la vallée USA, puis Nice et la SaintExpress. Touche un sommet pour ouvrir la semaine.</div>${svgMountain()}</div>

  
  <!-- 10. Chaussures -->
  <div class="kpi"><div class="kpi-t">🥁 Rotation chaussures</div><div class="kpi-r">Rotation conseillée : récup/easy → Clifton & Gel Pulse (rare), longues → Novablast, qualité → Magic Speed, trail → Cascadia. Chaque séance du plan porte sa paire conseillée.</div>${shoes}</div>

  </div></section>
  <p class="note-foot">Dashboard alimenté par ta vraie donnée Strava · Mis à jour à chaque séance logée</p>`;
  dashApplyState();
}

/* ===== MODALE ===== */
const overlay=document.getElementById('overlay'),boite=document.getElementById('boite'),topbar=document.getElementById('topbar'),contenu=document.getElementById('contenu');
let segActif=null;
function ouvrir(){overlay.classList.add('ouverte');document.body.style.overflow='hidden';boite.scrollTop=0;}
function fermer(){overlay.classList.remove('ouverte');document.body.style.overflow='';setTimeout(()=>{contenu.innerHTML='';topbar.innerHTML='';},300);}
overlay.addEventListener('click',e=>{if(e.target===overlay)fermer()});
document.addEventListener('keydown',e=>{if(e.key==='Escape')fermer()});
const btnFermer='<button class="btn-nav" onclick="fermer()">Fermer ✕</button>';


function s24Chart(splits){const n=splits.length,W=720,h=190,padL=8,padR=8,padT=26,padB=30;
  const paces=splits.map(s=>s[0]),hrs=splits.map(s=>s[1]);
  const spd=paces.map(p=>1000/p);const sMin=Math.min(...spd)*0.94,sMax=Math.max(...spd)*1.03;
  const hMin=Math.min(...hrs)-6,hMax=Math.max(...hrs)+8;
  const bw=(W-padL-padR)/n;
  const bars=splits.map((s,i)=>{const sp=1000/s[0];const bh=(sp-sMin)/(sMax-sMin)*(h-padT-padB);const x=padL+i*bw,y=h-padB-bh;
    const pm=Math.floor(s[0]/60),ps=Math.round(s[0]%60);
    return `<rect x="${(x+2).toFixed(1)}" y="${y.toFixed(1)}" width="${(bw-4).toFixed(1)}" height="${bh.toFixed(1)}" rx="3" fill="#3b82f6" opacity=".55"/>
      <text x="${(x+bw/2).toFixed(1)}" y="${(h-padB+11).toFixed(1)}" font-size="7.6" fill="#94a3b8" text-anchor="middle">${pm}:${String(ps).padStart(2,'0')}</text>
      <text x="${(x+bw/2).toFixed(1)}" y="${(h-padB+21).toFixed(1)}" font-size="6.8" fill="#cbd5e1" text-anchor="middle">km${i+1}</text>`;}).join('');
  const HY=v=>padT+(h-padT-padB)*(1-(v-hMin)/(hMax-hMin));
  const line='M '+hrs.map((v,i)=>`${(padL+i*bw+bw/2).toFixed(1)} ${HY(v).toFixed(1)}`).join(' L ');
  const hrlab=hrs.map((v,i)=>{if(i===0||i===n-1||v===Math.max(...hrs))return `<text x="${(padL+i*bw+bw/2).toFixed(1)}" y="${(HY(v)-6).toFixed(1)}" font-size="8" font-weight="700" fill="#ef4444" text-anchor="middle">${v}</text>`;return '';}).join('');
  return `<svg viewBox="0 0 ${W} ${h}" class="chart-svg">${bars}<path d="${line}" fill="none" stroke="#ef4444" stroke-width="2" stroke-linejoin="round"/>${hrlab}
    <text x="${padL}" y="11" font-size="8.5" fill="#3b82f6" font-weight="700">▮ Allure /km</text><text x="${padL+74}" y="11" font-size="8.5" fill="#ef4444" font-weight="700">— FC moyenne /km</text></svg>`;
}

/* ===== REWIND hebdo ===== */
let rwIdx=0,rwCur=null;
function rwRender(){const r=rwCur;if(!r)return;const s=r.slides[rwIdx];
  const prog=r.slides.map((_,i)=>`<div class="rw-seg ${i<=rwIdx?'done':''}"></div>`).join('');
  const card=document.getElementById('rwcard');card.style.background=s.bg;
  card.innerHTML=`<div class="rw-prog">${prog}</div><button class="rw-close" onclick="event.stopPropagation();rwClose()">\u2715</button>
    <div class="rw-kicker">${s.kicker}</div><div class="rw-big">${s.big}</div><div class="rw-txt">${s.txt}</div>
    <div class="rw-hint">tape pour continuer \u00b7 ${rwIdx+1}/${r.slides.length}</div>`;}
function rwOpen(id){rwCur=REWINDS.find(x=>x.id===id);if(!rwCur)return;rwIdx=0;document.getElementById('rwoverlay').classList.add('on');document.body.style.overflow='hidden';rwRender();
  try{localStorage.setItem('rw_seen',id);}catch(e){}}
function rwNext(){if(!rwCur)return;if(rwIdx<rwCur.slides.length-1){rwIdx++;rwRender();}else rwClose();}
function rwClose(){const o=document.getElementById('rwoverlay');if(o)o.classList.remove('on');document.body.style.overflow='';rwCur=null;}
function rwAuto(){const last=REWINDS[REWINDS.length-1];if(!last)return;const d=new Date();if(d.getDay()!==1)return;/* 1 = lundi */const wk=isoWeek(d)+'-'+d.getFullYear();try{if(localStorage.getItem('rw_mon')===wk)return;localStorage.setItem('rw_mon',wk);}catch(e){}setTimeout(()=>rwOpen(last.id),900);}

function ouvrirSeanceS24(idx){const r=S24R.runs[idx];if(!r)return;segActif=null;
  topbar.innerHTML=`<button class="btn-nav" onclick="ouvrirSemaine(24)">‹ Retour semaine 24</button>${btnFermer}`;
  const metr=Object.entries(r.metriques).map(([k,v])=>`<div class="metrique"><div class="metrique-l">${k}</div><div class="metrique-v">${v}</div></div>`).join('');
  contenu.innerHTML=`<div class="sd-hero"><div class="hero-badges"><span class="sd-badge" style="background:#22c55e22;color:#15803d">Course à pied</span><span class="st-chip st-fait">Fait ✓</span><span class="seance-tag">${r.tag}</span></div>
    <h2 class="sd-titre">${r.titre}</h2><p class="sd-sous">Semaine 24 · ${r.date} juin · récupération post-Circaète</p>
    <div class="sd-metriques">${metr}</div>${r.chaussure?`<div class="shoe-chip">👟 ${r.chaussure}</div>`:''}${prCelebration(r)}</div>
    <div class="sd-corps">
    <div class="sd-section">Kilomètre par kilomètre</div><div class="viz-wrap" style="padding:14px">${s24Chart(r.splits)}</div>
    <div class="sd-section">Lecture de la séance</div><div class="callout callout-obj">${r.lecture}</div>
    <div class="sd-section">Revue du coach</div><div class="rev-coach">${r.revue}</div></div>`;
  ouvrir();boite.scrollTop=0;
}

function ouvrirSemaine(num){const s=SEMAINES.find(x=>x.num===num);const ph=PHASES.find(p=>p.id===s.phase);segActif=null;
  if(s.statut==='courante'){topbar.innerHTML=`<span></span>${btnFermer}`;
    const runs=S24R.runs.map((r,i)=>`<div class="seance-carte" onclick="ouvrirSeanceS24(${i})"><div class="seance-bande" style="background:#22c55e"></div><div class="seance-idx">${r.date}</div><div class="seance-info"><div class="seance-nom">${r.titre}</div><div class="seance-desc">${r.desc}</div><div class="seance-tags"><span class="st-chip st-fait">Fait ✓</span><span class="seance-tag">${r.tag}</span><span class="cat-badge cat-classique">Classique</span></div></div><div class="seance-fleche">›</div></div>`).join('');
    contenu.innerHTML=`<div class="sw-hero"><span class="sw-tag" style="background:${COUL[s.phase]}22;color:${COUL[s.phase]}">${ph.nom}</span><h2 class="sw-titre">Semaine ${s.num} — ${s.theme}</h2><p class="sw-sous">Semaine en cours · récupération post-Circaète</p></div>
      <div class="sw-corps"><div class="callout callout-obj">${s.objectif}</div>
      <div class="sw-section">Réalisé cette semaine — ${S24R.runs.length} sorties · ${S24R.km} km</div><div class="seance-liste">${runs}</div>
      <div style="text-align:center"><button class="rw-btn" onclick="rwOpen('S24')">🎬 Lance le Rewind de ta semaine</button></div><div class="sw-section">Revue du coach</div><div class="rev-coach">${S24R.revue}</div>
      <p class="note-foot" style="margin-top:28px">La reprise structurée démarre en S25.</p></div>`;ouvrir();return;}
  const seances=SEANCES_BY_WEEK[num]||[];const fait=seances.filter(x=>x.realise&&(x.realise.statut==='fait'||x.realise.statut==='partiel')).length;const realKm=seances.reduce((a,x)=>a+((x.realise&&x.realise.km)||0),0);
  topbar.innerHTML=`<span></span>${btnFermer}`;
  const liste=seances.map(se=>{const r=se.realise||{statut:'a_faire'};const tags=[stChip(r.statut),`<span class="seance-tag">${se.type}</span>`,catBadge(se.cat),`<span class="rpe-pill"><span class="rpe-dot" style="background:${rpeColor(se.rpe)}"></span>RPE ${se.rpe}</span>`];if(se.chaussure)tags.push(`<span class="seance-shoe">👟 ${se.chaussure.replace("ASICS ","").replace("HOKA ","").replace("Brooks ","")}</span>`);if(se.fit)tags.push('<span class="seance-fit">⌚ .fit</span>');if(se.opt)tags.push('<span class="seance-tag tag-opt">Optionnelle</span>');
    const rs=r.km?`<div class="seance-desc" style="color:#15803d;font-weight:700;margin-top:3px">✓ ${r.km} km${r.allure?' · '+r.allure:''}</div>`:'';
    return `<div class="seance-carte" onclick="ouvrirSeance(${num},${se.id})"><div class="seance-bande" style="background:${se.accent}"></div><div class="seance-idx">Séance ${se.num}</div><div class="seance-info"><div class="seance-nom">${se.titre}</div><div class="seance-desc">${se.sous}</div>${rs}<div class="seance-tags">${tags.join('')}</div></div><div class="seance-fleche">›</div></div>`;}).join('');
  const repPill=s.repartition&&s.repartition!=='—'?`<div class="sw-pill"><div class="sw-pill-l">Répartition</div><div class="sw-pill-v" style="font-size:.74rem">${s.repartition}</div></div>`:'';
  contenu.innerHTML=`<div class="sw-hero"><span class="sw-tag" style="background:${COUL[s.phase]}22;color:${COUL[s.phase]}">${ph.nom}</span><h2 class="sw-titre">Semaine ${s.num} — ${s.theme}</h2><p class="sw-sous">Semaine type · clique une séance</p><div class="sw-meta"><div class="sw-pill"><div class="sw-pill-l">Volume cible</div><div class="sw-pill-v">${s.km} km</div></div><div class="sw-pill"><div class="sw-pill-l">Réalisé</div><div class="sw-pill-v">${fait}/${seances.length} · ${realKm} km</div></div><div class="sw-pill"><div class="sw-pill-l">Charge</div><div class="sw-pill-v" style="font-size:.84rem">${s.charge}</div></div>${repPill}</div></div><div class="sw-corps"><div class="callout callout-obj">${s.objectif}</div><div class="sw-section">Séances de la semaine</div><div class="seance-liste">${liste}</div>${s.revue?`<div class="sw-section">Revue du coach — bilan de la semaine</div><div class="rev-coach">${s.revue}</div>`:`<div class="realise-empty" style="margin-top:18px"><strong>Revue de la semaine à venir.</strong> Quand la semaine sera bouclée, tu trouveras ici mon bilan complet : volume et charge vs prévu, adhérence, signaux à surveiller, et la décision pour la semaine suivante. Elle alimentera aussi le Journal du coach.</div>`}</div>`;ouvrir();
}
function realiseBloc(num,se){const r=se.realise||{statut:'a_faire'};
  if(r.statut==='a_faire')return `<div class="sd-section">Réalisé & revue du coach</div><div class="realise-empty"><strong>Séance pas encore réalisée.</strong> Quand tu me diras « j'ai fait la séance ${se.num} de la semaine ${num} », je remplirai ici le <strong>réalisé</strong> (Strava), ton <strong>ressenti</strong>, et ma <strong>revue du coach</strong> — ce qui a été bien fait, et surtout ce qu'il faut corriger.</div>`;
  const p=se.metriques;
  const prevu=`<div class="rvp-l"><span>Distance</span><span>${p.Distance||'—'}</span></div><div class="rvp-l"><span>Durée</span><span>${p['Durée']||p['Durée totale']||'—'}</span></div><div class="rvp-l"><span>Allure</span><span>${p.Allure||'—'}</span></div><div class="rvp-l"><span>FC</span><span>${p.FC||'—'}</span></div><div class="rvp-l"><span>RPE</span><span>${p.RPE||'—'}</span></div>`;
  const reb=`<div class="rvp-l"><span>Distance</span><span>${r.km?r.km+' km':'—'}</span></div><div class="rvp-l"><span>Temps</span><span>${r.temps||'—'}</span></div><div class="rvp-l"><span>Allure</span><span>${r.allure||'—'}</span></div><div class="rvp-l"><span>FC moy/max</span><span>${r.fc_moy?r.fc_moy+(r.fc_max?'/'+r.fc_max:''):'—'}</span></div><div class="rvp-l"><span>RPE ressenti</span><span>${r.rpe_ressenti||'—'}</span></div>`;
  return `<div class="sd-section">Réalisé vs prévu — ${stChip(r.statut)}</div><div class="rvp"><div class="rvp-col"><h5>Prévu</h5>${prevu}</div><div class="rvp-col"><h5>Réalisé</h5>${reb}</div></div>${prCelebration(r)}${r.commentaire?`<div class="comm-user">« ${r.commentaire} »</div>`:''}<div class="sd-section">Revue du coach</div><div class="rev-coach">${r.revue||'—'}</div>`;
}
function ouvrirSeance(num,id){const se=(SEANCES_BY_WEEK[num]||[]).find(x=>x.id===id);if(!se)return;segActif=null;
  topbar.innerHTML=`<button class="btn-nav" onclick="ouvrirSemaine(${num})">‹ Retour semaine ${num}</button>${btnFermer}`;
  const metr=Object.entries(se.metriques).map(([k,v])=>`<div class="metrique"><div class="metrique-l">${k}</div><div class="metrique-v">${v}</div></div>`).join('');
  const struct=se.struct.map((b,i)=>{const c=(i===0||i===se.struct.length-1)?'#22c55e':se.accent;return `<div class="struct-ligne"><div class="struct-puce" style="background:${c}"></div><div class="struct-nom">${b.nom}</div><div class="struct-txt">${b.txt}</div></div>`;}).join('');
  const LEGMAP={vert:['#22c55e','Endurance / échauffement / retour au calme'],bleu:['#3b82f6','Travail qualitatif / spécifique'],orange:['#f97316','Récupération'],violet:['#8b5cf6','Nutrition / rappel'],jaune:['#eab308','Descente active'],rouge:['#ef4444','Effort chrono']};
  const leg=(se.segments?[...new Set(se.segments.map(s=>s.couleur))].map(c=>LEGMAP[c]||['#94a3b8',c]).map(x=>`<div class="legende-item"><div class="legende-puce" style="background:${x[0]}"></div>${x[1]}</div>`).join(''):se.legende.map(l=>`<div class="legende-item"><div class="legende-puce" style="background:${l.c}"></div>${l.l}</div>`).join(''));
  const coach=se.coach.map(c=>`<div class="coach-carte"><div class="coach-titre">${c.titre}</div><p class="coach-texte">${c.texte}</p></div>`).join('');
  const viz=se.segments?`<div class="sd-section">Visualisation chronologique</div><div class="viz-wrap"><div class="viz-entete"><span class="viz-label">Structure de la séance</span><span class="viz-hint">Clique un segment</span></div><div class="barre-scroll"><div class="barre-piste" id="piste"></div></div><div class="detail-panneau" id="dpan"><div class="detail-nom" id="dnom"></div><div class="detail-role" id="drole"></div><div class="detail-grille" id="dgr"></div></div></div>`:'';
  contenu.innerHTML=`<div class="sd-hero"><div class="hero-badges"><span class="sd-badge" style="background:${se.accent}22;color:${se.accent}">${se.sport}</span>${catBadge(se.cat)}${stChip((se.realise||{}).statut||'a_faire')}</div><h2 class="sd-titre">${se.titre}</h2><p class="sd-sous">${se.sous}</p><div class="sd-metriques">${metr}</div>${se.chaussure?`<div class="shoe-chip">👟 Chaussure conseillée — ${se.chaussure}</div>`:''}${se.fit?`<a class="fit-btn" href="${se.fit}" download>⌚ Télécharger la séance</a>`:''}</div><div class="sd-corps"><div class="sd-section">Intensité ressentie (RPE)</div><div class="rpe-wrap"><div class="rpe-info"><div class="rpe-label">RPE</div><div class="rpe-val" style="color:${rpeColor(se.rpe)}">${se.rpe}<span style="font-size:.8rem;color:var(--texte-trois);font-weight:600">/10</span></div></div><div class="rpe-scale">${rpeScale(se.rpe)}</div></div><div class="sd-section">Objectif</div><div class="callout callout-obj">${se.objectif}</div><div class="sd-section">Légende</div><div class="legende">${leg}</div><div class="sd-section">Déroulé</div><div class="struct">${struct}</div>${viz}<div class="sd-section">Bénéfices recherchés</div><div class="callout callout-ben">${se.benefices}</div><div class="sd-section">Conseil du coach</div><div class="coach-grille">${coach}</div>${se.nutrition?`<div class="sd-section">Nutrition de séance</div><div class="nutri"><div class="nutri-t">🍌 ${se.nutrition.titre}</div>${se.nutrition.items.map(i=>`<div class="nutri-l"><b>${i[0]}</b><span>${i[1]}</span></div>`).join('')}</div>`:''}<div class="sd-section">Points de vigilance</div><div class="callout callout-vig">${se.vigilance}</div>${realiseBloc(num,se)}</div>`;
  ouvrir();if(se.segments)initBarre(se);
}
function initBarre(se){const piste=document.getElementById('piste');if(!piste)return;const pan=document.getElementById('dpan'),dnom=document.getElementById('dnom'),drole=document.getElementById('drole'),dgr=document.getElementById('dgr');const total=se.segments[se.segments.length-1].fin;
  se.segments.forEach(seg=>{const e=document.createElement('div');e.className=`seg seg-${seg.couleur}`;e.style.width=`${(seg.duree/total)*100}%`;e.style.height=`${seg.hauteur}%`;e.title=seg.nom;
    e.addEventListener('click',()=>{if(segActif)segActif.classList.remove('actif');if(segActif===e){segActif=null;pan.classList.remove('visible');return;}segActif=e;e.classList.add('actif');dnom.textContent=seg.nom;drole.textContent=seg.role;dgr.innerHTML=`<div><div class="di-label">Durée</div><div class="di-val">${fmt(seg.duree)}</div></div><div><div class="di-label">Bloc</div><div class="di-val">${seg.bloc}</div></div><div><div class="di-label">Début</div><div class="di-val">${fmt(seg.debut)}</div></div><div><div class="di-label">Fin</div><div class="di-val">${fmt(seg.fin)}</div></div>`;pan.classList.add('visible');});
    piste.appendChild(e);});
}
renderHeader();renderPlan();rwAuto();
