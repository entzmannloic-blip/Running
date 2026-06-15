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
    const _it=RACES.map(r=>{const _dn=Math.max(0,Math.ceil((new Date(r.date)-_t)/86400000));return `<span class="cds-item"><span class="cds-n">J-${_dn}</span><span class="cds-l">${r.nom}</span></span>`;}).join('');
    _cd=`${_it}`;
  }
  const _maj=`<div class="vdj-maj">Données à jour au ${MAJ}</div>`;
  document.getElementById('cd-strip').innerHTML=_cd;
  const _cw=`<button class="cw-link" onclick="jumpToWeek(${sc.num})"><span class="cw-pin">📍</span><span class="cw-txt">Tu es en <strong>S${sc.num} · ${sc.theme}</strong></span><span class="cw-arr">voir dans le plan →</span></button>`;
  document.getElementById('hero-plan').innerHTML=`${_psCard}${_cw}`;
  document.getElementById('maj-foot').innerHTML=_maj;
  const _ab=document.getElementById('appbar');if(_ab&&document.documentElement)document.documentElement.style.setProperty('--appbar-h',_ab.offsetHeight+'px');
}

/* ===== PLAN ===== */
function renderPlan(){const phasesEl=document.getElementById('phases');phasesEl.innerHTML='';const _cur=isoWeek(new Date());
  PHASES.forEach(ph=>{const bloc=document.createElement('div');bloc.className='phase-bloc';const sems=SEMAINES.filter(s=>s.phase===ph.id);
    const cartes=sems.map(s=>{const ses=SEANCES_BY_WEEK[s.num]||[];const fait=ses.filter(x=>x.realise&&(x.realise.statut==='fait'||x.realise.statut==='partiel')).length;
      const cnt=s.num===24?`<div class="sem-km" style="margin-top:4px"><span>${S24R.runs.length} sorties · ${S24R.km} km réalisés</span></div>`:(ses.length?`<div class="sem-km" style="margin-top:4px"><span>${fait}/${ses.length} séances</span></div>`:'');
      const badge=s.num===_cur?`<div class="sem-statut st-courante">Courante</div>`:'';
      return `<div class="sem-carte cliquable" id="wk-${s.num}" onclick="ouvrirSemaine(${s.num})">${badge}<div class="sem-num">Semaine ${s.num}</div><div class="sem-theme">${s.theme}</div><div class="sem-km">${s.km} <span>km · ${s.charge}</span></div>${cnt}<div class="sem-barre"><div class="sem-barre-fill" style="width:${Math.min(100,s.km/88*100)}%;background:${ph.c}"></div></div></div>`;}).join('');
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
  let _mLogged=false;
  for(let day=1;day<=ndays;day++){
    const iso=y+'-'+String(m+1).padStart(2,'0')+'-'+String(day).padStart(2,'0');
    const de=evs.filter(e=>e.iso===iso);
    const tdy=iso===todayISO?' cal-today':'';
    if(de.length){
      const e=de[0];
      if(e.color==='g'||e.color==='o')_mLogged=true;
      const _stMap={g:'Réalisé',o:'Non réalisé',x:'À venir'};
      const _albl=day+' '+MN[m]+' — '+(_stMap[e.color]||'')+' : '+e.titre.replace(/"/g,'');
      cells+='<button type="button" class="cal-cell cal-'+e.color+tdy+'" onclick="'+e.open+'" aria-label="'+_albl+'" title="'+e.titre.replace(/"/g,'')+'"><span class="cal-num">'+day+'</span><span class="cal-dot"></span></button>';
    }else{
      cells+='<div class="cal-cell'+tdy+'"><span class="cal-num cal-muted">'+day+'</span></div>';
    }
  }
  const _emptyCal=_mLogged?'':'<div class="empty-note"><span class="en-ic">🗓️</span><span>Aucune séance loguée sur ce mois pour l\'instant — les jours se colorent en <strong>vert</strong> dès que tu réalises une séance. Dis-moi « j\'ai fait la séance X de la semaine Y » et le mois prend vie.</span></div>';
  return '<div class="cal-head"><button class="cal-nav" onclick="calNav(-1)" aria-label="Mois précédent">‹</button><div class="cal-title">'+MN[m]+' '+y+'</div><button class="cal-nav" onclick="calNav(1)" aria-label="Mois suivant">›</button></div>'+
    '<div class="cal-grid">'+cells+'</div>'+
    '<div class="cal-legend"><span><i class="cal-lg cal-g"></i>Réalisé</span><span><i class="cal-lg cal-o"></i>Non réalisé</span><span><i class="cal-lg cal-x"></i>À venir</span><span style="opacity:.45;margin-left:auto">build 22</span></div>'+_emptyCal;
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
  {id:'coach',ic:'🧠',t:'Analyse du coach'},
  {id:'annee',ic:'🔥',t:'Année & trophées'},
  {id:'saison',ic:'📊',t:'Saison en chiffres'},
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
  const ab=document.getElementById('appbar');const abh=ab?ab.offsetHeight:0;
  const y=s.getBoundingClientRect().top+window.scrollY-(abh+(nav?nav.offsetHeight:0)+10);window.scrollTo({top:y,behavior:_reduceMotion()?'auto':'smooth'});}
function dgrpHead(id,ic,t){return `<section class="dgrp" id="grp-${id}"><button class="dgrp-head" onclick="dashToggle('${id}')"><span class="dgrp-ic">${ic}</span><span class="dgrp-t">${t}</span><span class="dgrp-arr">▾</span></button><div class="dgrp-body">`;}
function _reduceMotion(){return window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;}
function jumpToWeek(num){if(document.getElementById('vue-plan').style.display==='none')showTab('plan');
  const el=document.getElementById('wk-'+num);if(!el)return;
  const ab=document.getElementById('appbar');const abh=ab?ab.offsetHeight:0;
  const y=el.getBoundingClientRect().top+window.scrollY-(abh+14);window.scrollTo({top:y,behavior:_reduceMotion()?'auto':'smooth'});
  el.classList.add('wk-flash');setTimeout(()=>el.classList.remove('wk-flash'),1700);}
/* ===== Item 4 — Projection marathon « boule de cristal » ===== */
function _pace2s(p){if(p==null)return null;const m=String(p).match(/(\d+):(\d+)/);return m?(+m[1]*60+ +m[2]):null;}
function _s2hm(s){s=Math.round(s);const h=Math.floor(s/3600),m=Math.floor((s%3600)/60);return h+'h'+String(m).padStart(2,'0');}
function _s2hms(s){s=Math.round(s);const h=Math.floor(s/3600),m=Math.floor((s%3600)/60),x=s%60;return h+'h'+String(m).padStart(2,'0')+':'+String(x).padStart(2,'0');}
function _riegel(km,t){return t*Math.pow(42.195/km,1.07);}
function marathonEquiv(se){
  const r=se.realise;if(!r||(r.statut!=='fait'&&r.statut!=='partiel'))return null;
  const t=se.type,sub=(se.metriques||{}).Type||'',pace=_pace2s(r.allure);
  if(t==='Test / recalibrage'){
    const km=parseFloat(String(r.km).replace(',','.'))||10;let tot=null;
    if(r.temps&&/^\d{1,3}:\d{2}$/.test(String(r.temps).trim()))tot=_pace2s(r.temps);else if(pace)tot=pace*km;
    if(!tot)return null;return{sec:_riegel(km,tot),w:3,label:`Test ${km} km`,sub:r.allure||r.temps};
  }
  if(!pace)return null;
  if(t==='Spécifique marathon')return{sec:pace*1.015*42.195,w:2,label:'Allure marathon',sub:r.allure};
  if(t==='Seuil (puissance aérobie)'){const f=sub==='Seuil 60'?1.06:1.12;return{sec:pace*f*42.195,w:1.5,label:sub||'Seuil',sub:r.allure};}
  return null;
}
function marathonProjection(){
  const q=[];Object.values(SEANCES_BY_WEEK).flat().forEach(se=>{const e=marathonEquiv(se);if(e){e.date=se.date;q.push(e);}});
  q.sort((a,b)=>String(a.date||'').localeCompare(String(b.date||'')));
  let num=PROJ.base,den=1;const trend=[PROJ.base];
  q.forEach((e,i)=>{const w=e.w*(1+i*0.4);num+=e.sec*w;den+=w;trend.push(num/den);});
  return{sec:num/den,n:q.length,sources:q,trend:trend};
}
function renderCrystalBall(){
  const P=marathonProjection();const goal=PROJ.goal,gmin=PROJ.gmin,gmax=PROJ.gmax;
  const clamp=v=>Math.max(0,Math.min(100,v));
  const pos=clamp((P.sec-gmin)/(gmax-gmin)*100);
  const goalPos=clamp((goal-gmin)/(gmax-gmin)*100);
  const ahead=goal-P.sec;
  const ahMin=Math.round(Math.abs(ahead)/60);
  const deltaTxt=ahead>=0?`<strong style="color:#22c55e">${ahMin} min d\u2019avance</strong> sur l\u2019objectif 3h45`
    :`<strong style="color:#f97316">+${ahMin} min</strong> au-dessus de 3h45`;
  const deltaShort=ahead>=0?`${ahMin} min d'avance sur l'objectif 3h45`:`${ahMin} min au-dessus de 3h45 — le bloc va combler l'écart`;
  let clarte;
  if(P.n===0)clarte=`<div class="cb-clarte">🌫️ <strong>Boule encore voilée.</strong> La projection part de ta forme actuelle (${PROJ.base_label}). Elle s'affinera à chaque séance qualité loguée — le <strong>test 10 km de la S31</strong> sera le premier gros recalibrage, puis chaque seuil et chaque séance d'allure marathon.</div>`;
  else clarte=`<div class="cb-clarte">🔮 <strong>${P.n} séance${P.n>1?'s':''} qualité intégrée${P.n>1?'s':''}.</strong> Plus tu logues de qualité, plus la projection se précise.</div>`;
  const sources=P.n?`<div class="cb-src"><div class="cb-src-t">Ce qui nourrit la projection</div>${P.sources.map(s=>`<div class="cb-src-l"><span>${s.label}${s.sub?` · ${s.sub}`:''}</span><span class="cb-src-v">${_s2hm(s.sec)}</span></div>`).join('')}<div class="cb-src-l cb-src-base"><span>Forme de départ (référence)</span><span class="cb-src-v">${_s2hm(PROJ.base)}</span></div></div>`:'';
  const trend=P.trend.length>=2?`<div class="cb-trend"><div class="cb-src-t">Affinage de la projection séance après séance</div>${chartLine(P.trend.map(v=>v/60),{color:'#8b5cf6',h:120,fmtY:v=>_s2hm(v*60),baseline:goal/60,annotate:true})}</div>`:'';
  return `<div class="kpi cb">
    <div class="cb-head"><span class="cb-orb">🔮</span><div><div class="kpi-t" style="margin:0">Projection marathon — boule de cristal</div><div class="kpi-r" style="margin:2px 0 0">Temps projeté sur Nice, recalculé à chaque séance qualité loguée.</div></div></div>
    <div class="cb-big"><div class="cb-time">${_s2hm(P.sec)}</div><div class="cb-delta">${deltaTxt}</div></div>
    <div class="cb-gauge">
      <div class="cb-bar"><div class="cb-fill" style="width:${pos}%"></div>
        <div class="cb-goal" style="left:${goalPos}%"><span>🎯 3h45</span></div>
        <div class="cb-needle" style="left:${pos}%"><span>${_s2hm(P.sec)}</span></div></div>
      <div class="cb-scale"><span>3h30</span><span>4h00</span></div>
    </div>
    ${clarte}${trend}${sources}
    <div class="cb-method">Méthode : mélange pondéré de ta forme de départ et de tes séances qualité loguées — test 10 km via Riegel (exp. 1,07), allure marathon ×1,015, seuil 30 ×1,12 / seuil 60 ×1,06, projetés sur 42,195 km. Les séances récentes pèsent davantage.</div>
  </div>`;
}
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

  </div></section>`+dgrpHead('perf','🏆','Performances & objectifs')+renderCrystalBall()+`
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
function ouvrir(){overlay.classList.add('ouverte');document.body.style.overflow='hidden';overlay.scrollTop=0;boite.scrollTop=0;}
function fermer(){if(typeof ttsStop==='function')ttsStop();overlay.classList.remove('ouverte');document.body.style.overflow='';setTimeout(()=>{contenu.innerHTML='';topbar.innerHTML='';},300);}
overlay.addEventListener('click',e=>{if(e.target===overlay)fermer()});
(function(){const to=document.getElementById('theoOverlay');if(to)to.addEventListener('click',e=>{if(e.target===to)closeTheory();});})();
document.addEventListener('keydown',e=>{if(e.key==='Escape')fermer()});
const btnFermer='<button class="btn-nav" onclick="fermer()" aria-label="Fermer la fiche">Fermer ✕</button>';


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

const S25_CAP=`<strong>Reprise &amp; déblocage.</strong> Le chantier de la semaine, c'est <strong>corriger la zone grise</strong> : footings vraiment faciles (≥ 6:00/km, FC ≤ 144), lignes droites relâchées pour réveiller la foulée, et on relance la structure tout en douceur. Tu arrives <strong>en avance sur la récupération</strong> — dos et jambes OK, aucune douleur — les conditions sont idéales pour repartir proprement. Objectif : 52 km sur 5 séances, zéro précipitation. C'est le socle du bloc de développement qui démarre juste après.`;
function ouvrirSemaine(num){const s=SEMAINES.find(x=>x.num===num);const ph=PHASES.find(p=>p.id===s.phase);segActif=null;
  if(num===24){topbar.innerHTML=`<span></span>${btnFermer}`;
    const runs=S24R.runs.map((r,i)=>`<div class="seance-carte" onclick="ouvrirSeanceS24(${i})"><div class="seance-bande" style="background:#22c55e"></div><div class="seance-idx">${r.date}</div><div class="seance-info"><div class="seance-nom">${r.titre}</div><div class="seance-desc">${r.desc}</div><div class="seance-tags"><span class="st-chip st-fait">Fait ✓</span><span class="seance-tag">${r.tag}</span><span class="cat-badge cat-classique">Classique</span></div></div><div class="seance-fleche">›</div></div>`).join('');
    contenu.innerHTML=`<div class="sw-hero"><span class="sw-tag" style="background:${COUL[s.phase]}22;color:${COUL[s.phase]}">${ph.nom}</span><h2 class="sw-titre">Semaine ${s.num} — ${s.theme}</h2><p class="sw-sous">Semaine terminée · récupération post-Circaète</p></div>
      <div class="sw-corps"><div class="callout callout-obj">${s.objectif}</div>
      <div class="sw-section">Réalisé sur la semaine — ${S24R.runs.length} sorties · ${S24R.km} km</div><div class="seance-liste">${runs}</div>
      <div style="text-align:center"><button class="rw-btn" onclick="rwOpen('S24')">🎬 Lance le Rewind de ta semaine</button></div><div class="sw-section">Bilan du coach</div><div class="rev-coach">${S24R.revue}</div>
      <div class="sw-section">🎯 Cap sur la S25</div><div class="callout callout-cap">${S25_CAP}</div>
      <p class="note-foot" style="margin-top:24px">La reprise structurée démarre maintenant, en S25.</p></div>`;ouvrir();return;}
  const seances=SEANCES_BY_WEEK[num]||[];const fait=seances.filter(x=>x.realise&&(x.realise.statut==='fait'||x.realise.statut==='partiel')).length;const realKm=seances.reduce((a,x)=>a+((x.realise&&x.realise.km)||0),0);
  topbar.innerHTML=`<span></span>${btnFermer}`;
  const liste=seances.map(se=>{const r=se.realise||{statut:'a_faire'};const tags=[stChip(r.statut),`<span class="seance-tag">${se.type}</span>`,catBadge(se.cat),`<span class="rpe-pill"><span class="rpe-dot" style="background:${rpeColor(se.rpe)}"></span>RPE ${se.rpe}</span>`];if(se.chaussure)tags.push(`<span class="seance-shoe">👟 ${se.chaussure.replace("ASICS ","").replace("HOKA ","").replace("Brooks ","")}</span>`);if(se.fit)tags.push('<span class="seance-fit">⌚ .fit</span>');if(se.opt)tags.push('<span class="seance-tag tag-opt">Optionnelle</span>');
    const rs=r.km?`<div class="seance-desc" style="color:#15803d;font-weight:700;margin-top:3px">✓ ${r.km} km${r.allure?' · '+r.allure:''}</div>`:'';
    return `<div class="seance-carte" onclick="ouvrirSeance(${num},${se.id})"><div class="seance-bande" style="background:${se.accent}"></div><div class="seance-idx">Séance ${se.num}</div><div class="seance-info"><div class="seance-nom">${se.titre}</div><div class="seance-desc">${se.sous}</div>${rs}<div class="seance-tags">${tags.join('')}</div></div><div class="seance-fleche">›</div></div>`;}).join('');
  const repPill=s.repartition&&s.repartition!=='—'?`<div class="sw-pill"><div class="sw-pill-l">Répartition</div><div class="sw-pill-v" style="font-size:.74rem">${s.repartition}</div></div>`:'';
  contenu.innerHTML=`<div class="sw-hero"><span class="sw-tag" style="background:${COUL[s.phase]}22;color:${COUL[s.phase]}">${ph.nom}</span><h2 class="sw-titre">Semaine ${s.num} — ${s.theme}</h2><p class="sw-sous">Semaine type · clique une séance</p><div class="sw-meta"><div class="sw-pill"><div class="sw-pill-l">Volume cible</div><div class="sw-pill-v">${s.km} km</div></div><div class="sw-pill"><div class="sw-pill-l">Réalisé</div><div class="sw-pill-v">${fait}/${seances.length} · ${realKm} km</div></div><div class="sw-pill"><div class="sw-pill-l">Charge</div><div class="sw-pill-v" style="font-size:.84rem">${s.charge}</div></div>${repPill}</div></div><div class="sw-corps"><div class="callout callout-obj">${s.objectif}</div><div class="sw-section">Séances de la semaine</div><div class="seance-liste">${liste}</div>${s.revue?`<div class="sw-section">Revue du coach — bilan de la semaine</div><div class="rev-coach">${s.revue}</div>`:`<div class="realise-empty" style="margin-top:18px"><strong>Revue de la semaine à venir.</strong> Quand la semaine sera bouclée, tu trouveras ici mon bilan complet : volume et charge vs prévu, adhérence, signaux à surveiller, et la décision pour la semaine suivante. Elle alimentera aussi le Journal du coach.</div>`}</div>`;ouvrir();
}
/* ===== Lot 2 — Logging réel des séances (persistance localStorage) ===== */
const LOG_KEY='runlog_v1';
function loadLogs(){try{return JSON.parse(localStorage.getItem(LOG_KEY)||'{}');}catch(e){return {};}}
function saveLogs(o){try{localStorage.setItem(LOG_KEY,JSON.stringify(o));}catch(e){}}
function logId(wk,id){return wk+'-'+id;}
function findSeance(wk,id){return (SEANCES_BY_WEEK[wk]||[]).find(x=>String(x.id)===String(id));}
function hydrateLogs(){const logs=loadLogs();Object.entries(logs).forEach(([k,r])=>{const i=k.indexOf('-');const wk=k.slice(0,i),id=k.slice(i+1);const se=findSeance(wk,id);if(se)se.realise=r;});}
function _parseTime(t){if(!t)return null;const p=String(t).trim().split(':').map(x=>parseInt(x,10));if(!p.length||p.some(isNaN))return null;if(p.length===3)return p[0]*3600+p[1]*60+p[2];if(p.length===2)return p[0]*60+p[1];if(p.length===1)return p[0]*60;return null;}
function computeAllure(km,temps){const s=_parseTime(temps);if(!s||!km)return '';const sk=s/km;const m=Math.floor(sk/60),x=Math.round(sk%60);return (x===60?(m+1)+':00':m+':'+String(x).padStart(2,'0'))+'/km';}
let _pendingStatut='fait';
function lfPickStatut(st){_pendingStatut=st;document.querySelectorAll('.lf-st').forEach(b=>b.classList.toggle('actif',b.dataset.st===st));}
function lfToggle(wk,id){const f=document.getElementById('logform');if(!f)return;const open=f.style.display==='none';f.style.display=open?'block':'none';const b=document.getElementById('lf-toggle');if(b)b.textContent=open?'Masquer le formulaire':'✎ Logger / modifier le réalisé';if(open)f.scrollIntoView({behavior:_reduceMotion()?'auto':'smooth',block:'center'});}
function _v(id){const e=document.getElementById(id);return e?e.value.trim():'';}
function logSeance(wk,id){
  const se=findSeance(wk,id);if(!se)return;
  const km=parseFloat(_v('lf-km').replace(',','.'))||'';
  const temps=_v('lf-temps');
  const allure=(km&&temps)?computeAllure(km,temps):'';
  const realise={statut:_pendingStatut,km:km,temps:temps,allure:allure,
    fc_moy:parseInt(_v('lf-fcmoy'),10)||'',fc_max:parseInt(_v('lf-fcmax'),10)||'',
    rpe_ressenti:_v('lf-rpe'),commentaire:_v('lf-comm'),
    pr:parseInt(_v('lf-pr'),10)||0,ach:parseInt(_v('lf-ach'),10)||0,
    revue:(se.realise&&se.realise.revue)||''};
  const logs=loadLogs();logs[logId(wk,id)]=realise;saveLogs(logs);
  se.realise=realise;
  _afterLog(wk,id);
}
function unlogSeance(wk,id){const se=findSeance(wk,id);if(!se)return;const logs=loadLogs();delete logs[logId(wk,id)];saveLogs(logs);se.realise={statut:'a_faire'};_afterLog(wk,id);}
function _afterLog(wk,id){renderHeader();renderPlan();if(document.getElementById('vue-dash').style.display!=='none')renderDash();ouvrirSeance(wk,id);setTimeout(()=>{const b=document.querySelector&&document.querySelector('.lf-save');if(b){b.textContent='Enregistré ✓';b.classList.add('lf-saved');setTimeout(()=>{if(b)b.textContent='Enregistrer';},1800);}},80);}
function logForm(wk,se){
  const r=se.realise||{statut:'a_faire'};const logged=r.statut!=='a_faire';
  _pendingStatut=logged?r.statut:'fait';
  const st=[['fait','Fait ✓'],['partiel','Partiel'],['manque','Manqué']].map(s=>`<button type="button" class="lf-st${_pendingStatut===s[0]?' actif':''}" data-st="${s[0]}" onclick="lfPickStatut('${s[0]}')">${s[1]}</button>`).join('');
  const f=(id,lbl,val,ph,extra='')=>`<label class="lf-f"><span>${lbl}</span><input id="${id}" value="${val!=null&&val!==''?String(val).replace(/"/g,'&quot;'):''}" placeholder="${ph}" ${extra}></label>`;
  return `<div class="lf-wrap">
    <button type="button" class="lf-toggle" id="lf-toggle" onclick="lfToggle(${wk},${se.id})">${logged?'✎ Modifier le réalisé':'✎ Logger cette séance'}</button>
    <div class="logform" id="logform" style="display:none">
      <div class="lf-statut">${st}</div>
      <div class="lf-grid">
        ${f('lf-km','Distance (km)',r.km,'10,5','type="text" inputmode="decimal"')}
        ${f('lf-temps','Temps',r.temps,'48:30 ou 1:24:30','type="text" inputmode="numeric"')}
        ${f('lf-fcmoy','FC moy',r.fc_moy,'152','type="text" inputmode="numeric"')}
        ${f('lf-fcmax','FC max',r.fc_max,'171','type="text" inputmode="numeric"')}
        ${f('lf-rpe','RPE /10',r.rpe_ressenti,'6','type="text" inputmode="numeric"')}
        ${f('lf-pr','Records perso',r.pr,'0','type="text" inputmode="numeric"')}
        ${f('lf-ach','Trophées segment',r.ach,'0','type="text" inputmode="numeric"')}
      </div>
      <label class="lf-f lf-comm"><span>Commentaire</span><textarea id="lf-comm" placeholder="Ressenti, conditions, sensations…">${r.commentaire?String(r.commentaire).replace(/</g,'&lt;'):''}</textarea></label>
      <div class="lf-hint">L'allure se calcule automatiquement depuis distance + temps. Les records/trophées déclenchent la célébration et la projection se réactualise.</div>
      <div class="lf-actions"><button type="button" class="lf-save" onclick="logSeance(${wk},${se.id})">Enregistrer</button>${logged?`<button type="button" class="lf-clear" onclick="unlogSeance(${wk},${se.id})">Réinitialiser</button>`:''}</div>
    </div></div>`;
}
function realiseBloc(num,se){const r=se.realise||{statut:'a_faire'};
  if(r.statut==='a_faire')return `<div class="sd-section">Réalisé & revue du coach</div><div class="realise-empty"><strong>Séance pas encore réalisée.</strong> Log-la ci-dessous dès que c'est fait — le calendrier, la boule de cristal et les records s'activent automatiquement.</div>${logForm(num,se)}`;
  const p=se.metriques;
  const prevu=`<div class="rvp-l"><span>Distance</span><span>${p.Distance||'—'}</span></div><div class="rvp-l"><span>Durée</span><span>${p['Durée']||p['Durée totale']||'—'}</span></div><div class="rvp-l"><span>Allure</span><span>${p.Allure||'—'}</span></div><div class="rvp-l"><span>FC</span><span>${p.FC||'—'}</span></div><div class="rvp-l"><span>RPE</span><span>${p.RPE||'—'}</span></div>`;
  const reb=`<div class="rvp-l"><span>Distance</span><span>${r.km?r.km+' km':'—'}</span></div><div class="rvp-l"><span>Temps</span><span>${r.temps||'—'}</span></div><div class="rvp-l"><span>Allure</span><span>${r.allure||'—'}</span></div><div class="rvp-l"><span>FC moy/max</span><span>${r.fc_moy?r.fc_moy+(r.fc_max?'/'+r.fc_max:''):'—'}</span></div><div class="rvp-l"><span>RPE ressenti</span><span>${r.rpe_ressenti||'—'}</span></div>`;
  return `<div class="sd-section">Réalisé vs prévu — ${stChip(r.statut)}</div><div class="rvp"><div class="rvp-col"><h5>Prévu</h5>${prevu}</div><div class="rvp-col"><h5>Réalisé</h5>${reb}</div></div>${prCelebration(r)}${coachDebrief(num,se)}${r.commentaire?`<div class="comm-user">« ${r.commentaire} »</div>`:''}<div class="sd-section">Revue du coach</div><div class="rev-coach">${r.revue||'—'}</div>${logForm(num,se)}`;
}
/* ===== Coach IA — contenu pédagogique par type de séance (pourquoi / comment / théorie / lecture) ===== */
const COACH_THEORY={
 ef:{nom:'Endurance fondamentale',
   pourquoi:"Construire le moteur aérobie qui porte tout le reste : densifier mitochondries et capillaires, et apprendre au corps à brûler les graisses. C'est 80 % de ton volume — sans cette base large, pas de seuil élevé ni de tenue sur marathon.",
   comment:"Allure conversationnelle, FC sous ~75 % FCmax (≤ 144). Si tu peux parler en phrases complètes, c'est bon. Ralentis sans ego : trop vite = zone grise, ton ennemi n°1. Foulée souple, respiration facile par le nez.",
   theorie:"<p><strong>Le principe du 80/20 (polarisation).</strong> Les coureurs qui progressent le plus courent ~80 % de leur volume très facile et ~20 % vraiment dur. Le piège, c'est la « zone grise » : ni assez lent pour récupérer et construire, ni assez rapide pour stimuler — c'est ton point faible historique (53 % de tes km y passaient).</p><p><strong>Ce qui se passe physiologiquement.</strong> À basse intensité, tu recrutes les fibres lentes (type I) et tu stimules la <em>biogenèse mitochondriale</em> : plus de « centrales énergétiques » dans tes muscles. Tu densifies aussi ton réseau capillaire (plus d'oxygène livré) et tu améliores l'<em>oxydation des lipides</em> — apprendre à brûler le gras épargne ton glycogène, la clé pour ne pas taper le mur à Nice.</p><p><strong>Pourquoi si lent ?</strong> Ces adaptations dépendent du <em>volume</em> et de la <em>durée</em>, pas de l'intensité. Courir plus vite ne les accélère pas — ça ajoute juste de la fatigue qui t'empêche de bien faire tes séances qualité. Facile vraiment facile, dur vraiment dur.</p>",
   lecture:{fcBand:[0,144],fcLabel:"≤ 144 (75 % FCmax)"}},
 seuil:{nom:'Seuil',
   pourquoi:"Repousser ton seuil lactique — le point où le lactate s'accumule plus vite que tu ne l'élimines. Plus ton seuil est haut, plus tu cours vite longtemps sans « exploser ». C'est le déterminant n°1 de ta perf du 10 km au marathon.",
   comment:"Allure « confortablement dure » : tu pourrais lâcher 3-4 mots, pas une phrase. ~4:40/km (seuil 30) ou ~4:55 (seuil 60), FC 88-92 % FCmax (169-177). Tu dois finir en te disant « j'aurais pu tenir un bloc de plus », pas vidé.",
   theorie:"<p><strong>Qu'est-ce que le seuil ?</strong> À l'effort, tes muscles produisent du lactate. Tant que tu l'élimines (le « clearance ») aussi vite que tu le produis, tu tiens. Au-delà du seuil, il s'accumule, l'acidité monte, et tu dois ralentir. Entraîner le seuil, c'est déplacer ce plafond <em>plus haut</em>.</p><p><strong>Pourquoi « confortablement dur » et pas plus ?</strong> Le seuil se travaille <em>à</em> l'intensité du seuil, pas au-dessus. Si tu pars trop vite (FC > 180), tu bascules en VO2max : plus fatigant, moins spécifique, et tu rates la cible physiologique. Le contrôle de l'allure est toute la séance.</p><p><strong>Seuil 30 vs 60.</strong> Le « seuil 30 » (allure tenable ~30 min en course) est légèrement plus rapide et plus dur ; le « seuil 60 » (~allure semi) est un poil plus lent mais en blocs plus longs. Les deux poussent le même plafond par deux angles. C'est la séance qui fait le plus progresser ton chrono marathon par heure investie.</p>",
   lecture:{fcBand:[169,177],fcLabel:"169-177 (88-92 % FCmax)"}},
 am:{nom:'Allure marathon',
   pourquoi:"Apprendre à ton corps à tenir précisément l'allure de Nice (5:20/km pour 3h45) et à brûler efficacement à cette intensité. C'est la spécificité absolue : le geste, l'allure, le fueling, répétés à l'identique du jour J.",
   comment:"5:10-5:20/km, FC ~80-85 % FCmax (154-163). Ça doit sembler « facile-modéré » au début — si c'est dur d'entrée, tu es trop rapide. Cale respiration et foulée, et profites-en pour tester ton fueling de course. Régularité absolue.",
   theorie:"<p><strong>La spécificité.</strong> Plus tu approches de la course, plus l'entraînement doit ressembler à la course. Tenir 5:20/km en séance apprend à ton système nerveux le <em>geste exact</em> et à ton métabolisme le bon <em>mix énergétique</em> à cette intensité (un mélange de glucides et de graisses propre à l'allure marathon).</p><p><strong>Le glycogène et le mur.</strong> À allure marathon, tu puises majoritairement dans le glycogène — un stock limité (~90-120 min). Le « mur » du marathon, c'est l'épuisement de ce stock. Deux parades que cette séance entraîne : mieux oxyder les graisses (épargner le glycogène) et <em>apprendre à manger en courant</em> pour recharger.</p><p><strong>Pourquoi répéter l'allure exacte ?</strong> Le jour J, partir 10 sec/km trop vite ruine la fin de course. Répéter 5:20 jusqu'à ce que ce soit gravé dans les jambes te protège de l'erreur la plus coûteuse du marathon : partir trop vite.</p>",
   lecture:{fcBand:[154,163],fcLabel:"154-163 (80-85 % FCmax)"}},
 cotes:{nom:'Côtes',
   pourquoi:"Développer la force spécifique et l'économie de course sans le stress articulaire de la vitesse à plat. La côte recrute plus de fibres et renforce tes chaînes — utile pour le marathon, indispensable pour le trail SaintExpress.",
   comment:"Effort vif et constant en montée (pas un sprint), FC qui monte haut en fin de côte. Foulée courte et active, regard 5 m devant. Descente en récup totale, jamais en force — tu protèges quadris et lombaires.",
   theorie:"<p><strong>Pourquoi la côte plutôt que la muscu ?</strong> Monter, c'est de la musculation spécifique : tu pousses contre la gravité avec exactement le geste de la course. Tu recrutes davantage de fibres rapides, tu renforces fessiers, mollets et tendons — sans charger une barre ni casser ta semaine.</p><p><strong>L'économie de course.</strong> La côte améliore la <em>raideur tendineuse</em> (stiffness) : tes tendons stockent et restituent mieux l'énergie élastique à chaque foulée, comme un ressort. Résultat : tu cours plus vite pour le même coût énergétique. C'est un gain « gratuit » de performance.</p><p><strong>Le lien trail.</strong> Pour SaintExpress (45 km de D+ nocturne), la force en côte et le geste de descente relâché sont déterminants. La descente en récup totale n'est pas une pause : c'est de la technique, et la protection de ton dos.</p>",
   lecture:{fcBand:[0,0],fcLabel:"variable (effort, pas allure)"}},
 longue:{nom:'Sortie longue',
   pourquoi:"La séance reine du marathon. Elle apprend à ton corps à <em>durer</em> : étend tes réserves de glycogène, densifie les capillaires, et entraîne la tête à tenir l'effort long. Avec finish allure marathon, elle simule la fin de course quand ça pique.",
   comment:"Corps en EF (≤ 144), finish AM si prévu. Mange et bois AVANT d'avoir faim ou soif — c'est l'entraînement du fueling autant que des jambes. Sur le finish, garde du jus : tu dois finir solide, pas cramé.",
   theorie:"<p><strong>Pourquoi c'est la séance reine.</strong> Le marathon se gagne sur l'endurance, et l'endurance se construit sur la durée. La sortie longue étend tes réserves de glycogène, multiplie les capillaires, et surtout muscle ta tête : apprendre à rester efficace quand c'est long et inconfortable.</p><p><strong>Le fueling, ta priorité n°1.</strong> C'est ton limiteur identifié — l'effondrement de La Circaète (km 21) venait d'un déficit d'eau et d'électrolytes par forte chaleur. La sortie longue est <em>l'</em>occasion de répéter ton plan : électrolytes réguliers, gels testés (4Endurance, Nduranz), boire avant la soif. Ne jamais découvrir son fueling le jour de la course.</p><p><strong>Le finish allure marathon.</strong> Courir les derniers km à 5:20 sur des jambes déjà fatiguées, c'est répéter <em>exactement</em> le 35e km de Nice. C'est dur, c'est volontaire, et c'est ce qui fait la différence entre finir fort et marcher.</p>",
   lecture:{fcBand:[0,150],fcLabel:"corps ≤ 144, finish ~155-163"}},
 test:{nom:'Test / recalibrage',
   pourquoi:"Recalibrer objectivement. Un test mesure ta forme réelle et permet d'ajuster tes zones, tes allures cibles et la projection marathon. C'est ton juge de paix périodique — la vérité du terrain.",
   comment:"Échauffement complet (à froid, le test est faussé). Pars légèrement sous ce que tu penses tenir, finis en accélérant : un négatif split révèle ton vrai potentiel. Donne tout sur les 2 derniers km.",
   theorie:"<p><strong>Pourquoi tester ?</strong> Les allures cibles dérivent quand la forme évolue. Un test recale tout : tes zones FC, tes allures de seuil et de marathon, et la boule de cristal. Sans recalibrage, tu t'entraînes sur des chiffres périmés.</p><p><strong>La prédiction de performance.</strong> Un 10 km bien couru prédit assez bien le marathon via des modèles comme Riegel (le temps grandit avec la distance selon un exposant ~1,07). C'est ce qui nourrit ta projection : un 10 km plus rapide tire la projection marathon vers le bas.</p><p><strong>Le pacing fausse tout.</strong> Parti trop vite, tu finis en marchant et le chrono <em>sous-estime</em> ta forme. En négatif split, le chrono reflète ton vrai niveau. Le test mesure autant ta forme que ta gestion d'allure — deux choses qui comptent le jour J.</p>",
   lecture:{fcBand:[0,0],fcLabel:"proche max sur la fin"}},
 trail:{nom:'Spécifique trail',
   pourquoi:"Le trail ne se court pas à l'allure mais à l'effort. Ces séances préparent SaintExpress (45 km de nuit, ton objectif plaisir) : le relief, la technique de descente, et la gestion d'effort sur la longue durée.",
   comment:"Montée en effort constant (marche rapide si ça pique, souvent plus économique), descente <strong>relâchée</strong> et cadence rapide pour protéger ton dos. Fueling et hydratation à intervalles réguliers à la montre, pas à la sensation. L'allure n'est pas un repère.",
   theorie:"<p>Le trail ajoute le relief, la technique et une gestion mentale plus longue. La montée se gère en effort (power hiking assumé), la descente est une compétence à part entière. Le fueling longue durée — ton limiteur — devient critique, surtout de nuit au froid où la soif est masquée.</p>",
   lecture:{fcBand:[0,0],fcLabel:"variable (effort / relief)"}}
};
function seanceTag(se){const t=se.type||'';
  if(t.indexOf('Seuil')>=0)return 'seuil';
  if(t.indexOf('Spécifique marathon')>=0)return 'am';
  if(t.indexOf('Côtes')>=0)return 'cotes';
  if(t.indexOf('Sortie longue')>=0)return 'longue';
  if(t.indexOf('Test')>=0)return 'test';
  if(t.indexOf('trail')>=0||t.indexOf('Trail')>=0)return 'trail';
  if(t.indexOf('EF')>=0||t.indexOf('Récup')>=0||t.indexOf('Endurance')>=0||t.indexOf('Footing')>=0)return 'ef';
  return null;}
function theoToggle(){const p=document.getElementById('theo-panel');if(!p)return;const open=p.style.display==='none';p.style.display=open?'block':'none';const b=document.getElementById('theo-btn');if(b)b.textContent=open?'▲ Replier la théorie':'📖 La théorie pour progresser';}
function coachAvant(num,se){const c=COACH_THEORY[seanceTag(se)];if(!c)return '';
  const tag=seanceTag(se);const rich=!!RICH_THEORY[tag];
  const theoBtn=rich
    ? `<button type="button" class="theo-btn theo-btn-rich" onclick="openTheory(${num},${se.id})">📖 Théorie & coaching approfondi <span class="theo-btn-arr">→</span></button>`
    : `<button type="button" class="theo-btn" id="theo-btn" onclick="theoToggle()">📖 La théorie pour progresser</button><div class="theo-panel" id="theo-panel" style="display:none"><div class="theo-tag">${c.nom} — la science</div>${c.theorie}</div>`;
  return `<div class="sd-section">🎓 Comprendre cette séance</div>
    <div class="cc-block">
      <div class="cc-item"><div class="cc-h">Pourquoi cette séance ?</div><div class="cc-txt">${c.pourquoi}</div></div>
      <div class="cc-item"><div class="cc-h">Comment l'exécuter ?</div><div class="cc-txt">${c.comment}</div></div>
      ${theoBtn}
    </div>`;}
/* --- Débrief après séance, calculé depuis les données loguées --- */
function _pacesIn(str){if(!str)return[];const m=String(str).match(/\d+:\d{2}/g);return m?m.map(x=>{const[a,b]=x.split(':');return +a*60+ +b;}):[];}
function coachDebrief(num,se){
  const r=se.realise;if(!r||(r.statut==='a_faire'))return '';
  const c=COACH_THEORY[seanceTag(se)];const find=[];
  // statut
  if(r.statut==='manque'){return `<div class="sd-section">📊 Débrief du coach</div><div class="cd-debrief"><div class="cd-line cd-warn"><span class="cd-ic">🟠</span><span><strong>Séance manquée.</strong> Pas de drame — une séance ratée ne casse pas un bloc. Si c'est le dos ou la fatigue, c'était la bonne décision. Si c'est l'organisation, on cale la prochaine. L'important, c'est la régularité sur la durée, pas la perfection.</span></div></div>`;}
  // Allure : cible (métriques) vs réalisé
  const tgt=_pacesIn((se.metriques||{}).Allure);const real=_pacesIn(r.allure)[0];
  if(real&&tgt.length){
    const lo=Math.min(...tgt),hi=Math.max(...tgt);
    if(real<lo-4){find.push(['⚠️','warn',`<strong>Plus rapide que la cible.</strong> Tu visais ${(se.metriques||{}).Allure}, tu as tenu ${r.allure}. ${c&&seanceTag(se)==='ef'?"Sur un footing facile, c'est le piège de la zone grise : trop rapide pour récupérer. Lâche du lest la prochaine fois.":"Attention à ne pas transformer la séance en un effort plus dur que prévu — tu perds en spécificité et tu ajoutes de la fatigue."}`]);}
    else if(real>hi+6){find.push(['🟠','warn',`<strong>Plus lent que la cible.</strong> Cible ${(se.metriques||{}).Allure}, réalisé ${r.allure}. Soit la fatigue, soit les conditions (chaleur, vent, relief), soit un objectif un peu ambitieux. À surveiller si ça se répète.`]);}
    else{find.push(['✅','good',`<strong>Allure dans la cible.</strong> ${r.allure} pour un objectif ${(se.metriques||{}).Allure} — exactement ce qu'il fallait. Le contrôle d'allure, c'est la moitié de la réussite d'une séance.`]);}
  }
  // FC vs bande attendue
  if(c&&r.fc_moy&&c.lecture.fcBand[1]>0){
    const[a,b]=c.lecture.fcBand;const fc=+r.fc_moy;
    if(a>0&&fc<a-5)find.push(['🟠','warn',`<strong>FC plus basse qu'attendu</strong> (${fc}, cible ${c.lecture.fcLabel}). Tu as peut-être sous-dosé l'intensité — la séance était plus facile que son objectif.`]);
    else if(fc>b+5)find.push(['⚠️','warn',`<strong>FC élevée</strong> (${fc} pour ${c.lecture.fcLabel}). Si l'allure était bonne mais la FC haute, pense dérive cardiaque : chaleur ou hydratation — ton point de vigilance depuis La Circaète. ${r.fc_max?'Pic à '+r.fc_max+'.':''}`]);
    else find.push(['✅','good',`<strong>FC dans la zone</strong> (${fc}, cible ${c.lecture.fcLabel}). Intensité bien dosée, tu as travaillé la bonne filière.`]);
  }
  // RPE ressenti vs attendu
  if(r.rpe_ressenti&&se.rpe){const rr=parseInt(r.rpe_ressenti,10);if(!isNaN(rr)){
    if(rr>=se.rpe+2)find.push(['⚠️','warn',`<strong>Ressenti plus dur que prévu</strong> (RPE ${rr} vs ${se.rpe} attendu). Pour une même allure, un RPE qui grimpe = fatigue accumulée, sommeil, ou conditions. Si ça persiste sur plusieurs séances, c'est un signal pour alléger.`]);
    else if(rr<=se.rpe-2)find.push(['✅','good',`<strong>Plus facile que prévu</strong> (RPE ${rr} vs ${se.rpe}). Bon signe de fraîcheur et de progression — la séance commence à rentrer dans tes cordes.`]);}}
  // PR / records
  if((r.pr||0)+(r.ach||0)>0)find.push(['🏆','good',`<strong>Des records au passage</strong> — ${r.pr?r.pr+' perso':''}${r.pr&&r.ach?', ':''}${r.ach?r.ach+' segment(s)':''}. La forme monte, c'est concret.`]);
  if(!find.length)return '';
  const lines=find.map(f=>`<div class="cd-line cd-${f[1]}"><span class="cd-ic">${f[0]}</span><span>${f[2]}</span></div>`).join('');
  return `<div class="sd-section">📊 Débrief du coach</div><div class="cd-debrief">${lines}<div class="cd-foot">Lecture automatique de tes données. Pour une analyse fine d'une séance précise, parle-m'en — j'ajoute ma revue détaillée.</div></div>`;
}
/* ===== Schémas théoriques SVG (FCmax 192) ===== */
function svgZonesFC(hi){
  const Z=[['Z1','Récup / EF','<134','#22c55e'],['Z2','Endurance','134-154','#84cc16'],['Z3','Tempo / AM','154-167','#eab308'],['Z4','Seuil','167-177','#f97316'],['Z5','VO2max','>177','#ef4444']];
  const w=300,bh=34,gap=4,x0=8;let bars='',labs='';const bw=(w-x0*2-gap*4)/5;
  Z.forEach((z,i)=>{const x=x0+i*(bw+gap);const on=hi===i;bars+=`<rect x="${x}" y="14" width="${bw}" height="${bh}" rx="5" fill="${z[3]}" opacity="${on?1:.3}"/>${on?`<rect x="${x}" y="14" width="${bw}" height="${bh}" rx="5" fill="none" stroke="${z[3]}" stroke-width="2.5"/>`:''}`;labs+=`<text x="${x+bw/2}" y="62" text-anchor="middle" font-size="9" font-weight="700" fill="${on?z[3]:'#94a3b8'}">${z[0]}</text><text x="${x+bw/2}" y="73" text-anchor="middle" font-size="7.5" fill="#94a3b8">${z[2]}</text>`;});
  return `<svg viewBox="0 0 ${w} 82" class="theo-svg" role="img" aria-label="Zones de fréquence cardiaque">${bars}${labs}</svg>`;
}
function svg8020(){
  return `<svg viewBox="0 0 300 96" class="theo-svg" role="img" aria-label="Répartition polarisée 80/20">
    <rect x="8" y="14" width="200" height="30" rx="5" fill="#22c55e"/><text x="108" y="33" text-anchor="middle" font-size="11" font-weight="800" fill="#fff">80 % FACILE</text>
    <rect x="212" y="14" width="34" height="30" rx="5" fill="#f97316" opacity=".35"/>
    <rect x="250" y="14" width="42" height="30" rx="5" fill="#ef4444"/><text x="271" y="33" text-anchor="middle" font-size="10" font-weight="800" fill="#fff">20 %</text>
    <text x="229" y="58" text-anchor="middle" font-size="8" font-weight="700" fill="#f97316">zone grise</text>
    <text x="229" y="68" text-anchor="middle" font-size="7.5" fill="#94a3b8">le piège</text>
    <path d="M229 44 L229 50" stroke="#f97316" stroke-width="1.5"/>
    <text x="108" y="86" text-anchor="middle" font-size="8" fill="#94a3b8">récupération + construction du moteur</text>
    <text x="271" y="86" text-anchor="middle" font-size="8" fill="#94a3b8">stimulus</text>
  </svg>`;
}
function svgGlycogen(){
  return `<svg viewBox="0 0 300 130" class="theo-svg" role="img" aria-label="Glycogène et le mur">
    <line x1="34" y1="10" x2="34" y2="100" stroke="#cbd5e1" stroke-width="1"/><line x1="34" y1="100" x2="292" y2="100" stroke="#cbd5e1" stroke-width="1"/>
    <text x="6" y="20" font-size="8" fill="#94a3b8">100%</text><text x="14" y="103" font-size="8" fill="#94a3b8">0</text>
    <text x="150" y="122" text-anchor="middle" font-size="8.5" fill="#94a3b8">distance (km) →</text>
    <text x="18" y="60" font-size="8" fill="#94a3b8" transform="rotate(-90 18 60)">glycogène</text>
    <rect x="210" y="10" width="82" height="90" fill="#ef4444" opacity=".08"/>
    <text x="251" y="48" text-anchor="middle" font-size="9" font-weight="800" fill="#ef4444">LE MUR</text>
    <path d="M34 14 C120 30, 180 78, 215 100" fill="none" stroke="#ef4444" stroke-width="2.5"/>
    <text x="120" y="78" font-size="8" font-weight="700" fill="#ef4444">sans fueling</text>
    <path d="M34 14 C140 28, 240 52, 292 64" fill="none" stroke="#22c55e" stroke-width="2.5"/>
    <text x="200" y="44" font-size="8" font-weight="700" fill="#16a34a">avec fueling</text>
    <text x="206" y="113" font-size="7.5" fill="#94a3b8">~30-32 km</text>
  </svg>`;
}
function svgDerive(){
  return `<svg viewBox="0 0 300 120" class="theo-svg" role="img" aria-label="Dérive cardiaque">
    <line x1="30" y1="10" x2="30" y2="92" stroke="#cbd5e1" stroke-width="1"/><line x1="30" y1="92" x2="292" y2="92" stroke="#cbd5e1" stroke-width="1"/>
    <text x="150" y="112" text-anchor="middle" font-size="8.5" fill="#94a3b8">temps →</text>
    <line x1="30" y1="60" x2="292" y2="60" stroke="#3b82f6" stroke-width="2.5" stroke-dasharray="0"/>
    <text x="200" y="54" font-size="8" font-weight="700" fill="#3b82f6">allure (constante)</text>
    <path d="M30 50 C120 48, 200 38, 292 22" fill="none" stroke="#ef4444" stroke-width="2.5"/>
    <text x="120" y="36" font-size="8" font-weight="700" fill="#ef4444">FC (qui monte)</text>
    <text x="60" y="84" font-size="7.5" fill="#94a3b8">→ découplage = fatigue / chaleur / déshydratation</text>
  </svg>`;
}
function svgLactate(){
  return `<svg viewBox="0 0 300 120" class="theo-svg" role="img" aria-label="Courbe du lactate">
    <line x1="30" y1="10" x2="30" y2="92" stroke="#cbd5e1" stroke-width="1"/><line x1="30" y1="92" x2="292" y2="92" stroke="#cbd5e1" stroke-width="1"/>
    <text x="150" y="112" text-anchor="middle" font-size="8.5" fill="#94a3b8">intensité / allure →</text>
    <text x="12" y="50" font-size="8" fill="#94a3b8" transform="rotate(-90 12 50)">lactate</text>
    <path d="M30 86 C120 84, 170 78, 200 64 C225 52, 250 26, 285 14" fill="none" stroke="#8b5cf6" stroke-width="2.5"/>
    <line x1="200" y1="14" x2="200" y2="92" stroke="#f97316" stroke-width="1.5" stroke-dasharray="4 3"/>
    <text x="200" y="106" text-anchor="middle" font-size="8" font-weight="700" fill="#f97316">SEUIL</text>
    <text x="95" y="78" font-size="7.5" fill="#16a34a">éliminé = tu tiens</text>
    <text x="232" y="34" font-size="7.5" fill="#ef4444">s'accumule</text>
  </svg>`;
}
/* ===== Panneau théorie & coaching approfondi (pilote S25) ===== */
const RICH_THEORY={
 ef:{titre:'Endurance fondamentale',icone:'🌱',sections:[
   {h:'Le moteur aérobie, ta fondation',html:`<p>L'endurance fondamentale, c'est 80 % de ton volume et la base de <strong>toute</strong> ta performance. À cette intensité, tu construis le moteur : tu multiplies les <em>mitochondries</em> (les centrales énergétiques de tes muscles), tu densifies ton réseau de <em>capillaires</em> (plus d'oxygène livré à chaque foulée), et tu renforces ton cœur. Rien de spectaculaire séance par séance — mais c'est la somme de ces footings qui fait qu'en novembre tu tiendras 42 km.</p>`+svgZonesFC(0)+`<p>Sur un EF, tu vis dans la <strong>Z1-Z2</strong> : FC sous ~144 (75 % de tes 192 de FCmax). Pas plus.</p>`},
   {h:'La polarisation 80/20',html:`<p>Les coureurs qui progressent le plus courent <strong>très facile la plupart du temps</strong>, et <strong>vraiment dur le reste</strong>. Le danger, c'est le milieu — la fameuse « zone grise » : ni assez lent pour récupérer et construire, ni assez rapide pour créer un vrai stimulus. Tu paies la fatigue d'un effort dur sans en récolter les bénéfices.</p>`+svg8020()+`<p class="theo-perso">📌 <strong>Pour toi, Loïc :</strong> ton analyse historique montrait <strong>53 % de tes km en zone grise</strong>. C'est ton chantier n°1. Sur tes footings, vise <strong>≥ 6:00/km</strong> et ne négocie pas, même si tu te sens bien — surtout si tu te sens bien.</p>`},
   {h:'Apprendre à brûler les graisses',html:`<p>À basse intensité, ton corps puise majoritairement dans les <em>lipides</em> — un stock quasi illimité. Plus tu cours lentement et souvent, plus tu deviens efficace pour brûler du gras. L'enjeu : <strong>épargner ton glycogène</strong> (le carburant rapide mais limité). Un coureur qui oxyde bien les graisses tape le mur du marathon beaucoup plus tard. L'EF, c'est littéralement l'entraînement de cette filière.</p>`},
   {h:'Le test de la parole',html:`<p>La meilleure jauge ne coûte rien : <strong>si tu peux tenir une conversation en phrases complètes, l'allure est bonne</strong>. Dès que tu haches tes phrases, tu es trop vite. Respire facilement par le nez, foulée souple et relâchée. Sur un EF tu dois finir <strong>frais</strong>, capable d'en refaire autant.</p>`},
   {h:'Les 3 erreurs classiques',html:`<p><strong>1. L'ego du chrono.</strong> Courir « pas trop lent pour ne pas avoir honte » = zone grise garantie.<br><strong>2. Accélérer sur la fin.</strong> Finir vite un footing flatte, mais ajoute de la fatigue parasite.<br><strong>3. Sauter l'EF parce que « c'est juste un footing ».</strong> C'est la séance qui construit le plus, justement parce qu'elle est facile.</p>`}],
   coach:`<p>Loïc, sur tes footings, l'objectif n'est jamais la distance ni l'allure : c'est de <strong>tenir le réflexe « facile = vraiment facile »</strong>. FC plafonnée à 144, allure ≥ 6:00/km, sans négocier — c'est ton antidote à la zone grise qui te plombait. Quand un footing inclut des lignes droites, ce sont 6 accélérations courtes et <strong>relâchées</strong>, juste pour réveiller la foulée : jamais un travail de vitesse, jamais en force, pour préserver ton dos.</p>`},
 am:{titre:'Allure marathon',icone:'🎯',sections:[
   {h:'La spécificité : t\'entraîner comme tu courses',html:`<p>Plus tu approches de Nice, plus l'entraînement doit <strong>ressembler à la course</strong>. Tenir précisément 5:20/km en séance apprend deux choses à ton corps : à ton <em>système nerveux</em>, le geste exact à cette allure ; à ton <em>métabolisme</em>, le bon mélange de carburants. C'est la définition de la spécificité — et c'est pour ça que ces séances montent en volume à mesure que la course approche.</p>`},
   {h:'Le métabolisme à allure marathon',html:`<p>À 5:20/km, tu brûles un <strong>mélange de glucides et de graisses</strong>. Le glycogène (sucre stocké dans les muscles et le foie) est ton carburant rapide, mais limité : ~90 à 120 minutes de stock. Au-delà, si tu n'as pas rechargé, c'est la panne.</p>`+svgGlycogen()+`<p>D'où les deux parades que cette séance entraîne : mieux <strong>oxyder les graisses</strong> (pour épargner le glycogène) et <strong>apprendre à manger en courant</strong>.</p>`},
   {h:'Le mur, expliqué',html:`<p>« Le mur » du marathon (souvent vers 30-35 km) n'est pas une faiblesse mentale : c'est <strong>l'épuisement du glycogène</strong>. Ton cerveau et tes muscles manquent brutalement de carburant rapide, l'allure s'effondre. La séance d'allure marathon, en répétant l'intensité exacte de la course, repousse ce seuil — et te force à roder ton plan nutrition.</p>`},
   {h:'Pourquoi 5:20/km, à la seconde près',html:`<p>Pour viser <strong>3h45</strong>, il faut tenir <strong>5:20/km</strong>. L'erreur la plus coûteuse du marathon, c'est de partir 10 sec/km trop vite : tu « gagnes » 2 minutes au début que tu rends au prix de 5-6 minutes à la fin. Répéter 5:20 jusqu'à ce que ce soit gravé dans tes jambes, c'est ta meilleure assurance.</p><table class="theo-tab"><tr><th>Point</th><th>Temps cible</th></tr><tr><td>5 km</td><td>26:40</td></tr><tr><td>10 km</td><td>53:20</td></tr><tr><td>Semi (21,1)</td><td>1:52:30</td></tr><tr><td>30 km</td><td>2:40:00</td></tr><tr><td>Arrivée</td><td>3:45:00</td></tr></table>`},
   {h:'La dérive cardiaque',html:`<p>Sur un effort prolongé, ta FC peut <strong>monter alors que ton allure reste constante</strong> : c'est le découplage. Plus il survient tôt, plus c'est un signal de fatigue, de chaleur ou de déshydratation.</p>`+svgDerive()+`<p class="theo-perso">📌 <strong>Pour toi :</strong> surveille ce découplage sur tes séances AM. S'il apparaît vite, c'est ton signal hydratation/électrolytes — exactement le mécanisme de La Circaète.</p>`}],
   coach:`<p>Loïc, chaque séance d'allure marathon est un <strong>test de calibrage</strong> : est-ce que 5:20/km « coule » ou est-ce que ça force déjà ? Plus tu avances dans le bloc, plus ces séances s'allongent (1×4 km en reprise, puis 3×4, puis 2×6 km au cœur du spécifique) — c'est là que se joue 3h45. Profites-en <strong>systématiquement pour roder ton fueling de course</strong> : un gel testé (4Endurance ou Nduranz) même sur les formats courts, pour habituer l'estomac. Rien de nouveau le jour J.</p>`},
 longue:{titre:'Sortie longue',icone:'⛰️',sections:[
   {h:'La séance reine',html:`<p>Si tu ne devais garder qu'une séance par semaine, ce serait celle-ci. Le marathon se gagne sur l'endurance, et l'endurance se construit sur la <strong>durée</strong>. La sortie longue étend tes réserves de glycogène, multiplie tes capillaires, renforce tendons et articulations dans la durée, et surtout muscle ta tête : rester efficace quand c'est long et que ça devient inconfortable.</p>`},
   {h:'Glycogène, capillaires, durée',html:`<p>Passé ~90 minutes, ton corps s'adapte : il apprend à stocker plus de glycogène et à mieux brûler les graisses pour l'épargner. C'est l'adaptation clé du marathonien.</p>`+svgGlycogen()+`<p>C'est aussi pour ça que la durée compte plus que l'allure : courir lentement <strong>longtemps</strong> bat courir vite <strong>court</strong>.</p>`},
   {h:'Le fueling, ton limiteur n°1',html:`<p class="theo-perso">📌 C'est <strong>ton</strong> point faible identifié. À La Circaète, tu t'es effondré au km 20-21 : pas par manque de jambes, mais par <strong>déficit d'eau et d'électrolytes</strong> par 26-31°C. Yannis t'a relancé avec une pastille de sodium.</p><p>La sortie longue est <em>l'</em>occasion de répéter ton plan, jamais de l'improviser le jour J :</p><p><strong>• Électrolytes :</strong> 1 pastille toutes les 45 min sur effort long ou par chaleur, sans attendre.<br><strong>• Hydratation :</strong> boire <strong>avant</strong> d'avoir soif (~500-600 ml/h).<br><strong>• Glucides :</strong> 1 gel testé toutes les 40-45 min (4Endurance Pro, Nduranz NRGY — déjà validés en training).<br><strong>• Règle d'or :</strong> rien de nouveau le jour de la course.</p>`},
   {h:'L\'endurance mentale (la durabilité)',html:`<p>Au-delà du physique, la sortie longue entraîne ta <strong>durabilité</strong> : ta capacité à garder une foulée efficace quand la fatigue s'installe. Deux coureurs avec le même VO2max ne finissent pas pareil un marathon — c'est la durabilité qui les sépare. Et ça, ça ne se travaille qu'en accumulant des kilomètres fatigués.</p>`},
   {h:'Le finish allure marathon',html:`<p>Quand la sortie longue se termine par quelques km à 5:20/km sur des jambes déjà entamées, tu répètes <strong>exactement le 35e km de Nice</strong>. C'est dur, c'est volontaire, et c'est ce qui fait la différence entre finir solide et marcher. Garde toujours du jus pour ce finish : tu dois le terminer en contrôle, pas cramé.</p>`}],
   coach:`<p>Loïc, sur tes sorties longues, deux non-négociables. <strong>Un : le fueling, dès le départ et même sans « besoin »</strong> — c'est l'automatisme à graver après ta défaillance de juin (pastilles d'électrolytes + gels testés, boire avant la soif). <strong>Deux : la régularité de l'allure</strong>, en EF (≤ 144) sur le corps. Quand un finish allure marathon est prévu, garde du jus pour le tenir en contrôle : c'est la répétition exacte du 35e km de Nice. Plus tard, ces longues iront jusqu'à 30 km avec 14 km de finish AM — la vraie séance reine de ta prépa.</p>`},
 seuil:{titre:'Seuil',icone:'🔥',sections:[
   {h:'Qu\'est-ce que le seuil ?',html:`<p>À l'effort, tes muscles produisent du <em>lactate</em>. Tant que ton corps l'élimine (la « clairance ») aussi vite qu'il le produit, tu tiens. Au-delà d'une certaine intensité — ton <strong>seuil lactique</strong> — le lactate s'accumule, l'acidité monte, et tu dois ralentir.</p>`+svgLactate()+`<p>Entraîner le seuil, c'est déplacer ce point de bascule <strong>plus haut</strong> : courir plus vite, plus longtemps, avant de « cramer ».</p>`},
   {h:'Le déterminant n°1 de ton chrono',html:`<p>Plus que le VO2max (largement génétique), c'est ton seuil qui décide de ta performance du 10 km au marathon. C'est aussi la qualité qui répond le plus vite à l'entraînement : <strong>quelques semaines de seuil bien fait font gagner des minutes</strong>. C'est ton meilleur retour sur investissement par heure courue.</p>`},
   {h:'Confortablement dur (et pas plus)',html:`<p>L'allure de seuil, c'est « confortablement dur » : tu pourrais lâcher 3-4 mots, pas une phrase complète. FC <strong>88-92 % de FCmax (169-177)</strong>.</p>`+svgZonesFC(3)+`<p>Tu dois finir en te disant « j'aurais pu tenir un bloc de plus » — <strong>pas vidé</strong>. Si tu finis cuit, c'était trop rapide.</p>`},
   {h:'Seuil 30 vs Seuil 60',html:`<p><strong>Seuil 30</strong> ≈ l'allure que tu tiendrais 30 min en course (~4:40/km pour toi) : un poil plus rapide, blocs plus courts. <strong>Seuil 60</strong> ≈ ton allure semi (~4:55/km) : un peu plus lent, blocs plus longs. Les deux poussent le même plafond par deux angles complémentaires.</p>`},
   {h:'L\'erreur qui ruine la séance',html:`<p class="theo-perso">📌 Partir trop vite (FC > 180) te fait <strong>basculer au-dessus du seuil</strong>, en VO2max : plus fatigant, moins spécifique, et tu rates la cible physiologique. Le contrôle de l'allure <em>est</em> la séance. Mieux vaut 4:45 tenu proprement que 4:30 qui explose au 2e bloc.</p>`}],
   coach:`<p>Loïc, le seuil est la séance qui fera le plus bouger ta projection marathon. La règle d'or pour toi : <strong>FC 169-177, allure contrôlée, et tu surveilles la dérive</strong> sur les derniers blocs. Si ta FC grimpe de +8-10 bpm à allure constante, c'est soit la fatigue, soit l'hydratation (ton point Circaète) — note-le dans ton ressenti, ça nourrit mon analyse. Deux séances qualité par semaine maximum, jamais deux jours de suite.</p>`},
 cotes:{titre:'Côtes — force & économie',icone:'⛰️',sections:[
   {h:'La force spécifique',html:`<p>Monter, c'est de la musculation <strong>avec le geste exact de la course</strong>. Tu pousses contre la gravité, tu recrutes davantage de fibres rapides, tu renforces fessiers, mollets et tendons — sans charger une barre ni casser ta semaine.</p>`+svgCote()},
   {h:'L\'économie de course (le ressort)',html:`<p>La côte améliore la <em>raideur tendineuse</em> (stiffness) : tes tendons stockent et restituent mieux l'énergie élastique à chaque foulée, comme un ressort. Résultat concret : tu cours <strong>plus vite pour le même coût énergétique</strong>. C'est un gain « gratuit » de performance qui se transfère au plat.</p>`},
   {h:'Pourquoi la côte plutôt que la muscu',html:`<p>La salle développe la force, mais la côte développe la force <em>utilisable en courant</em> — le bon angle, la bonne chaîne, le bon timing. Et sans le stress articulaire de la vitesse à plat : tu montes vite mais tu n'encaisses pas d'impacts violents. Idéal quand on a un dos à ménager.</p>`},
   {h:'La descente : récup ET technique',html:`<p class="theo-perso">📌 La descente n'est <strong>jamais</strong> en force. Tu redescends en récupération totale, foulée souple, pour deux raisons : laisser le cœur redescendre avant la côte suivante, et <strong>protéger tes quadriceps et tes lombaires</strong> des impacts excentriques. C'est une consigne clé pour toi.</p>`},
   {h:'Le lien avec SaintExpress',html:`<p>Pour ton trail de nuit de 45 km, la force en côte et un geste de descente relâché sont déterminants. Ces séances construisent les jambes qui encaisseront le D+ — et la technique de descente que tu rejoueras dans le Pilat.</p>`}],
   coach:`<p>Loïc, en côte : <strong>effort vif et constant en montée</strong> (pas un sprint de départ qui meurt à mi-pente), foulée courte et active, regard 5 m devant. L'idéal, c'est que ta dernière côte ressemble à la première — si elles s'effondrent, tu es parti trop fort. Et je le répète parce que c'est ton point : <strong>descente totalement relâchée</strong>, pour le cœur et pour le dos. Si tu sens une raideur lombaire après, c'est que tu as freiné en force en descente : allège.</p>`},
 test:{titre:'Test / recalibrage',icone:'⏱️',sections:[
   {h:'Pourquoi tester ?',html:`<p>Tes allures cibles dérivent quand ta forme évolue. Un test <strong>recale tout</strong> : tes zones FC, tes allures de seuil et de marathon, et ta projection. Sans recalibrage régulier, tu t'entraînes sur des chiffres périmés — trop faciles ou trop durs.</p>`},
   {h:'La prédiction de performance',html:`<p>Un 10 km bien couru prédit assez fidèlement ton marathon, via des modèles comme <strong>Riegel</strong> (le temps grandit avec la distance selon un exposant ~1,07).</p>`+svgRiegel()+`<p>C'est exactement ce qui nourrit ta <strong>boule de cristal</strong> : un 10 km plus rapide tire ta projection marathon vers le bas, automatiquement.</p>`},
   {h:'Le pacing change tout',html:`<p class="theo-perso">📌 Parti trop vite, tu finis en marchant et le chrono <strong>sous-estime</strong> ta vraie forme. En <strong>négatif split</strong> (2e moitié plus rapide), le chrono reflète ton potentiel réel. Le test mesure autant ta forme que ta gestion d'allure — deux choses qui comptent le jour J.</p>`},
   {h:'Comment courir ton test',html:`<p>Échauffement <strong>complet</strong> (15-20 min + quelques accélérations) : un test à froid est faussé et sous-évalue tout. Pars légèrement <em>sous</em> ce que tu penses tenir, installe-toi, puis accélère progressivement. Donne tout sur les 2 derniers km.</p>`},
   {h:'Ce que le test recalibre',html:`<p>Après un test : on remonte (ou ajuste) tes zones FC, tes allures de seuil et marathon, et la projection se met à jour. C'est ton <strong>juge de paix périodique</strong> — la vérité du terrain, sans ego ni sensation trompeuse.</p>`}],
   coach:`<p>Loïc, un test, ça se respecte : échauffement sérieux, pacing maîtrisé, et tu logues bien le résultat (distance + temps) — la boule de cristal se réactualise toute seule et tes allures cibles suivent. Pars sur un négatif split : c'est le meilleur moyen d'obtenir ton <strong>vrai</strong> niveau, pas un chrono gâché par un départ trop ambitieux. Et compare au test précédent : une allure qui progresse = des zones à remonter.</p>`},
 trail:{titre:'Spécifique trail',icone:'🏔️',sections:[
   {h:'Le trail, une autre discipline',html:`<p>Le trail ne se court pas comme la route. L'allure ne veut plus rien dire (le relief commande), c'est l'<strong>effort</strong> qui se gère. On ajoute la technique (pieds, équilibre, lecture du terrain), le dénivelé, et une gestion mentale plus longue. Tes séances spécifiques trail préparent <strong>SaintExpress</strong> : 45 km de nuit, ton objectif plaisir.</p>`},
   {h:'Économie en montée et descente',html:`<p>La montée se gère en <strong>effort constant</strong>, quitte à marcher vite (power hiking) quand ça devient raide — souvent plus économique que courir. La descente, elle, est une compétence à part entière : relâchement, cadence rapide, petits pas.</p>`+svgCote()},
   {h:'La gestion d\'effort',html:`<p>Sur un long trail, partir « aux sensations » est un piège : le relief te fait surpayer le moindre excès. La règle : rester en deçà de ce que tu pourrais faire, surtout en début de course. <strong>Le trail se gagne en seconde moitié</strong>, sur ceux qui ont gardé des jambes.</p>`},
   {h:'Fueling longue durée — et de nuit',html:`<p class="theo-perso">📌 C'est <strong>ton</strong> limiteur, et SaintExpress l'amplifie : 45 km, plusieurs heures, de nuit, au froid. Le froid masque la soif → tu bois moins → risque de défaillance comme à La Circaète. Plan : <strong>boire et manger à intervalles réguliers à la montre</strong> (pas à la sensation), électrolytes même par temps frais, et des apports solides en plus des gels sur cette durée.</p>`},
   {h:'Technique de descente & ton dos',html:`<p>En descente, <strong>ne freine pas en force</strong> : tu déroules, cadence élevée, buste légèrement en avant. Freiner avec les quadris contractés, c'est l'impact excentrique qui martèle tes lombaires — ton point de vigilance. Une descente relâchée protège ton dos <em>et</em> va plus vite.</p>`}],
   coach:`<p>Loïc, SaintExpress est ton objectif <strong>plaisir</strong>, 3 semaines après Nice : aucune pression chrono, c'est l'expérience du nocturne hivernal et du relief. Ces séances trail construisent les jambes (force, descente) et rodent ta logistique de nuit (frontale, couches, fueling au froid). Reste prudent sur les descentes pour le dos, et traite chaque sortie comme une répétition de gestion d'effort longue durée. Le Pilat est ton terrain — profites-en.</p>`}
};
function theoryPanelHTML(tag){const T=RICH_THEORY[tag];if(!T)return '';
  const secs=T.sections.map((s,i)=>`<div class="theo-sec" id="tsec-${i}"><div class="theo-sec-h"><span class="theo-sec-n">${i+1}</span>${s.h}</div><div class="theo-sec-b">${s.html}</div></div>`).join('');
  const ttsBar=(typeof window!=='undefined'&&'speechSynthesis' in window)?`<div class="tts-bar" id="ttsBar"><button class="tts-btn tts-play" onclick="ttsPlay()">🔊 Écouter la leçon</button><span class="tts-hint">lecture vocale de toute la leçon</span></div>`:'';
  return `<div class="theo-sheet-head"><div><div class="theo-kicker">Théorie & coaching · ${T.icone}</div><div class="theo-sheet-titre">${T.titre}</div></div><button class="theo-close" onclick="closeTheory()" aria-label="Fermer le panneau">✕</button></div>
    ${ttsBar}
    <div class="theo-sheet-body" id="theoSheetBody">${secs}<div class="theo-coachbox" id="tsec-coach"><div class="theo-coachbox-h">🧠 Le mot du coach — personnalisé</div>${T.coach}</div><div class="theo-end">Tu sais maintenant le <em>pourquoi</em> et le <em>comment</em>. Bonne séance, Loïc.</div></div>`;
}
function openTheory(num,id){const se=findSeance(num,id);if(!se)return;const tag=seanceTag(se);if(!RICH_THEORY[tag])return;
  if(typeof ttsStop==='function')ttsStop();
  const ov=document.getElementById('theoOverlay'),sh=document.getElementById('theoSheet');
  try{window._ttsTag=tag;}catch(e){}
  sh.innerHTML=theoryPanelHTML(tag);ov.classList.add('ouverte');document.body.style.overflow='hidden';
  const b=document.getElementById('theoSheetBody');if(b)b.scrollTop=0;}
function closeTheory(){if(typeof ttsStop==='function')ttsStop();const ov=document.getElementById('theoOverlay');ov.classList.remove('ouverte');
  if(!document.getElementById('overlay').classList.contains('ouverte'))document.body.style.overflow='';}

/* ===== Lecture vocale (Web Speech API, on-device, sans serveur) ===== */
let _ttsChunks=[],_ttsI=0,_ttsOn=false,_ttsPaused=false,_ttsKeep=null,_ttsVoice=null,_ttsCtx=null,_ttsBarId='ttsBar';
function _ttsPickVoice(){try{const vs=speechSynthesis.getVoices()||[];_ttsVoice=vs.find(v=>/fr-FR/i.test(v.lang)&&/(enhanced|premium|siri|amélie|amelie|thomas|audrey|aurélie|marie)/i.test(v.name))||vs.find(v=>/fr-FR/i.test(v.lang))||vs.find(v=>/^fr/i.test(v.lang))||null;}catch(e){_ttsVoice=null;}return _ttsVoice;}
if(typeof window!=='undefined'&&'speechSynthesis' in window){try{speechSynthesis.onvoiceschanged=_ttsPickVoice;_ttsPickVoice();}catch(e){}}
function _ttsClean(html){return String(html)
  .replace(/<svg[\s\S]*?<\/svg>/gi,' ')
  .replace(/<th[^>]*>/gi,' ').replace(/<\/th>/gi,' ')
  .replace(/<td[^>]*>/gi,' ').replace(/<\/td>/gi,' : ')
  .replace(/<tr[^>]*>/gi,' ').replace(/<\/tr>/gi,'. ')
  .replace(/<br\s*\/?>/gi,'. ').replace(/<\/p>/gi,'. ').replace(/<\/div>/gi,'. ')
  .replace(/<[^>]+>/g,' ')
  .replace(/&nbsp;/gi,' ').replace(/&amp;/gi,' et ').replace(/&eacute;/gi,'é').replace(/&[a-z]+;/gi,' ')
  .replace(/(\d):(\d{2}):(\d{2})/g,'$1 heures $2 minutes $3')
  .replace(/(\d{1,2}):(\d{2})/g,'$1 minutes $2')
  .replace(/\/km/gi,' par kilomètre').replace(/FCmax/gi,'fréquence cardiaque maximale').replace(/\bFC\b/g,'fréquence cardiaque').replace(/\bD\+/g,'dénivelé positif')
  .replace(/\s+([.,:;!?])/g,'$1').replace(/\.(\s*\.)+/g,'. ').replace(/\s+/g,' ').trim();}
function _ttsSentences(t){return t.split(/(?<=[.!?…])\s+/).reduce((acc,s)=>{s=s.trim();if(!s)return acc;if(s.length<=200){acc.push(s);return acc;}let cur='';s.split(/,\s*/).forEach(p=>{if((cur+p).length>180){if(cur)acc.push(cur.trim());cur=p;}else cur+=(cur?', ':'')+p;});if(cur)acc.push(cur.trim());return acc;},[]);}
function _ttsBuildLesson(tag){const T=RICH_THEORY[tag],C=COACH_THEORY[tag],ch=[];const add=(txt,sec)=>{_ttsSentences(txt).forEach(s=>{if(s)ch.push({txt:s,sec});});};
  add('Leçon du jour. '+T.titre+'.',-1);
  if(C){add('Pourquoi cette séance. '+_ttsClean(C.pourquoi),-1);add('Comment l\u2019exécuter. '+_ttsClean(C.comment),-1);}
  T.sections.forEach((s,i)=>{add(s.h+'.',i);add(_ttsClean(s.html),i);});
  add('Le mot du coach. '+_ttsClean(T.coach),'coach');return ch;}
function _ttsBar(state){const el=document.getElementById(_ttsBarId);if(!el)return;
  if(state==='playing')el.innerHTML=`<button class="tts-btn" onclick="ttsPause()">⏸ Pause</button><button class="tts-btn tts-stop" onclick="ttsStop()">⏹ Stop</button><span class="tts-state"><span class="tts-eq"><i></i><i></i><i></i></span> Lecture en cours…</span>`;
  else if(state==='paused')el.innerHTML=`<button class="tts-btn tts-play" onclick="ttsResume()">▶︎ Reprendre</button><button class="tts-btn tts-stop" onclick="ttsStop()">⏹ Stop</button>`;
  else{const sc=_ttsCtx&&_ttsCtx.t==='seance';el.innerHTML=sc?`<button class="tts-btn tts-play" onclick="ttsPlaySeance(${_ttsCtx.num},${_ttsCtx.id})">🔊 Lecture de la séance</button><span class="tts-hint">lecture vocale de la fiche, de haut en bas</span>`:`<button class="tts-btn tts-play" onclick="ttsPlay()">🔊 Écouter la leçon</button><span class="tts-hint">lecture vocale de toute la leçon</span>`;}}
function _ttsHi(sec){try{document.querySelectorAll('.theo-sec,.theo-coachbox').forEach(e=>e.classList.remove('tts-reading'));}catch(e){}
  let el=null;if(sec==='coach')el=document.getElementById('tsec-coach');else if(typeof sec==='number'&&sec>=0)el=document.getElementById('tsec-'+sec);
  if(el){el.classList.add('tts-reading');try{el.scrollIntoView({behavior:'smooth',block:'center'});}catch(e){}}}
function _ttsNext(){if(!_ttsOn)return;if(_ttsI>=_ttsChunks.length){ttsStop();return;}
  const ch=_ttsChunks[_ttsI];const u=new SpeechSynthesisUtterance(ch.txt);if(_ttsVoice)u.voice=_ttsVoice;u.lang='fr-FR';u.rate=0.97;u.pitch=1;
  u.onstart=()=>_ttsHi(ch.sec);u.onend=()=>{_ttsI++;if(_ttsOn&&!_ttsPaused)_ttsNext();};u.onerror=()=>{_ttsI++;if(_ttsOn&&!_ttsPaused)_ttsNext();};
  try{speechSynthesis.speak(u);}catch(e){}}
function _ttsStart(chunks){if(typeof window==='undefined'||!('speechSynthesis' in window))return;
  try{speechSynthesis.cancel();}catch(e){}
  _ttsChunks=chunks||[];_ttsI=0;_ttsOn=true;_ttsPaused=false;if(!_ttsVoice)_ttsPickVoice();_ttsBar('playing');
  if(_ttsKeep)clearInterval(_ttsKeep);_ttsKeep=setInterval(()=>{if(_ttsOn&&!_ttsPaused){try{speechSynthesis.resume();}catch(e){}}},9000);
  _ttsNext();}
function ttsPlay(){const tag=(typeof window!=='undefined')&&window._ttsTag;if(!tag||!RICH_THEORY[tag])return;_ttsCtx={t:'lesson'};_ttsBarId='ttsBar';_ttsStart(_ttsBuildLesson(tag));}
function ttsPlaySeance(num,id){const se=findSeance(num,id);if(!se)return;_ttsCtx={t:'seance',num:num,id:id};_ttsBarId='ttsBarSeance';_ttsStart(_ttsBuildSeance(num,id));}
function _ttsBuildSeance(num,id){const se=findSeance(num,id);if(!se)return [];const ch=[];
  const add=(txt)=>{_ttsSentences(_ttsClean(txt)).forEach(s=>{if(s)ch.push({txt:s,sec:null});});};
  add('Séance. '+se.titre+'. '+(se.sous||''));
  if(se.metriques)add(Object.entries(se.metriques).map(([k,v])=>k+' '+v).join('. ')+'.');
  add('Intensité ressentie. R P E '+se.rpe+' sur 10.');
  add('Objectif. '+se.objectif);
  const C=COACH_THEORY[seanceTag(se)];if(C){add('Pourquoi cette séance. '+C.pourquoi);add('Comment l\u2019exécuter. '+C.comment);}
  if(se.struct&&se.struct.length){add('Déroulé.');se.struct.forEach(b=>add(b.nom+'. '+b.txt));}
  if(se.benefices)add('Bénéfices recherchés. '+se.benefices);
  if(se.coach&&se.coach.length){add('Conseil du coach.');se.coach.forEach(c=>add(c.titre+'. '+c.texte));}
  if(se.nutrition&&se.nutrition.items)add('Nutrition de séance. '+se.nutrition.titre+'. '+se.nutrition.items.map(i=>i[0]+', '+i[1]).join('. '));
  if(se.vigilance)add('Points de vigilance. '+se.vigilance);
  const r=se.realise;if(r&&r.statut&&r.statut!=='a_faire'){const deb=coachDebrief(num,se);if(deb)add(deb);if(r.revue)add('Revue du coach. '+r.revue);}
  return ch;}
function ttsPause(){_ttsPaused=true;try{speechSynthesis.pause();}catch(e){}_ttsBar('paused');}
function ttsResume(){_ttsPaused=false;_ttsBar('playing');try{speechSynthesis.resume();}catch(e){}try{if(!speechSynthesis.speaking)_ttsNext();}catch(e){}}
function ttsStop(){_ttsOn=false;_ttsPaused=false;if(_ttsKeep){clearInterval(_ttsKeep);_ttsKeep=null;}try{speechSynthesis.cancel();}catch(e){}_ttsHi(null);_ttsBar('idle');}
function svgCote(){
  return `<svg viewBox="0 0 300 120" class="theo-svg" role="img" aria-label="Course en côte : force et économie">
    <line x1="20" y1="100" x2="280" y2="100" stroke="#cbd5e1" stroke-width="1"/>
    <path d="M40 100 L210 30 L210 100 Z" fill="#22c55e" opacity=".12"/>
    <path d="M40 100 L210 30" stroke="#16a34a" stroke-width="2.5"/>
    <circle cx="120" cy="62" r="6" fill="#1e293b"/>
    <path d="M120 62 L132 56" stroke="#1e293b" stroke-width="3" stroke-linecap="round"/>
    <path d="M120 62 L112 72" stroke="#1e293b" stroke-width="3" stroke-linecap="round"/>
    <path d="M126 50 L140 40" stroke="#f97316" stroke-width="2.5" marker-end="url(#ar)"/>
    <defs><marker id="ar" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto"><path d="M0 0 L6 3.5 L0 7 Z" fill="#f97316"/></marker></defs>
    <text x="158" y="44" font-size="8" font-weight="700" fill="#f97316">pousse contre</text>
    <text x="158" y="54" font-size="8" font-weight="700" fill="#f97316">la gravité</text>
    <text x="60" y="115" font-size="8" fill="#94a3b8">+ de fibres recrutées · tendons = ressort · 0 stress vitesse</text>
  </svg>`;
}
function svgRiegel(){
  return `<svg viewBox="0 0 300 124" class="theo-svg" role="img" aria-label="Prédiction de performance">
    <line x1="34" y1="12" x2="34" y2="96" stroke="#cbd5e1" stroke-width="1"/><line x1="34" y1="96" x2="288" y2="96" stroke="#cbd5e1" stroke-width="1"/>
    <text x="14" y="26" font-size="8" fill="#94a3b8">temps</text>
    <path d="M50 84 C120 78, 200 60, 278 22" fill="none" stroke="#3b82f6" stroke-width="2.5"/>
    <circle cx="92" cy="74" r="4.5" fill="#16a34a"/><text x="78" y="66" font-size="8" font-weight="700" fill="#16a34a">10 km</text>
    <line x1="92" y1="74" x2="250" y2="34" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3"/>
    <circle cx="250" cy="34" r="4.5" fill="#ef4444"/><text x="214" y="30" font-size="8" font-weight="700" fill="#ef4444">marathon prédit</text>
    <text x="58" y="110" font-size="8" fill="#94a3b8">10 km</text><text x="135" y="110" font-size="8" fill="#94a3b8">semi</text><text x="240" y="110" font-size="8" fill="#94a3b8">marathon</text>
    <text x="150" y="122" text-anchor="middle" font-size="7.5" fill="#94a3b8">un 10 km bien couru prédit ton marathon (Riegel, exp. 1,07)</text>
  </svg>`;
}
function ouvrirSeance(num,id){const se=(SEANCES_BY_WEEK[num]||[]).find(x=>x.id===id);if(!se)return;segActif=null;if(typeof ttsStop==='function')ttsStop();
  const ttsBarSeance=(typeof window!=='undefined'&&'speechSynthesis' in window)?`<div class="tts-bar tts-bar-seance" id="ttsBarSeance"><button class="tts-btn tts-play" onclick="ttsPlaySeance(${num},${se.id})">🔊 Lecture de la séance</button><span class="tts-hint">lecture vocale de la fiche, de haut en bas</span></div>`:'';
  topbar.innerHTML=`<button class="btn-nav" onclick="ouvrirSemaine(${num})">‹ Retour semaine ${num}</button>${btnFermer}`;
  const metr=Object.entries(se.metriques).map(([k,v])=>`<div class="metrique"><div class="metrique-l">${k}</div><div class="metrique-v">${v}</div></div>`).join('');
  const struct=se.struct.map((b,i)=>{const c=(i===0||i===se.struct.length-1)?'#22c55e':se.accent;return `<div class="struct-ligne"><div class="struct-puce" style="background:${c}"></div><div class="struct-nom">${b.nom}</div><div class="struct-txt">${b.txt}</div></div>`;}).join('');
  const LEGMAP={vert:['#22c55e','Endurance / échauffement / retour au calme'],bleu:['#3b82f6','Travail qualitatif / spécifique'],orange:['#f97316','Récupération'],violet:['#8b5cf6','Nutrition / rappel'],jaune:['#eab308','Descente active'],rouge:['#ef4444','Effort chrono']};
  const leg=(se.segments?[...new Set(se.segments.map(s=>s.couleur))].map(c=>LEGMAP[c]||['#94a3b8',c]).map(x=>`<div class="legende-item"><div class="legende-puce" style="background:${x[0]}"></div>${x[1]}</div>`).join(''):se.legende.map(l=>`<div class="legende-item"><div class="legende-puce" style="background:${l.c}"></div>${l.l}</div>`).join(''));
  const coach=se.coach.map(c=>`<div class="coach-carte"><div class="coach-titre">${c.titre}</div><p class="coach-texte">${c.texte}</p></div>`).join('');
  const viz=se.segments?`<div class="sd-section">Visualisation chronologique</div><div class="viz-wrap"><div class="viz-entete"><span class="viz-label">Structure de la séance</span><span class="viz-hint">Clique un segment</span></div><div class="barre-scroll"><div class="barre-piste" id="piste"></div></div><div class="detail-panneau" id="dpan"><div class="detail-nom" id="dnom"></div><div class="detail-role" id="drole"></div><div class="detail-grille" id="dgr"></div></div></div>`:'';
  contenu.innerHTML=`<div class="sd-hero"><div class="hero-badges"><span class="sd-badge" style="background:${se.accent}22;color:${se.accent}">${se.sport}</span>${catBadge(se.cat)}${stChip((se.realise||{}).statut||'a_faire')}</div><h2 class="sd-titre">${se.titre}</h2><p class="sd-sous">${se.sous}</p><div class="sd-metriques">${metr}</div>${se.chaussure?`<div class="shoe-chip">👟 Chaussure conseillée — ${se.chaussure}</div>`:''}${se.fit?`<a class="fit-btn" href="${se.fit}" download>⌚ Télécharger la séance</a>`:''}</div><div class="sd-corps">${ttsBarSeance}<div class="sd-section">Intensité ressentie (RPE)</div><div class="rpe-wrap"><div class="rpe-info"><div class="rpe-label">RPE</div><div class="rpe-val" style="color:${rpeColor(se.rpe)}">${se.rpe}<span style="font-size:.8rem;color:var(--texte-trois);font-weight:600">/10</span></div></div><div class="rpe-scale">${rpeScale(se.rpe)}</div></div><div class="sd-section">Objectif</div><div class="callout callout-obj">${se.objectif}</div>${coachAvant(num,se)}<div class="sd-section">Légende</div><div class="legende">${leg}</div><div class="sd-section">Déroulé</div><div class="struct">${struct}</div>${viz}<div class="sd-section">Bénéfices recherchés</div><div class="callout callout-ben">${se.benefices}</div><div class="sd-section">Conseil du coach</div><div class="coach-grille">${coach}</div>${se.nutrition?`<div class="sd-section">Nutrition de séance</div><div class="nutri"><div class="nutri-t">🍌 ${se.nutrition.titre}</div>${se.nutrition.items.map(i=>`<div class="nutri-l"><b>${i[0]}</b><span>${i[1]}</span></div>`).join('')}</div>`:''}<div class="sd-section">Points de vigilance</div><div class="callout callout-vig">${se.vigilance}</div>${realiseBloc(num,se)}</div>`;
  ouvrir();if(se.segments)initBarre(se);
}
function initBarre(se){const piste=document.getElementById('piste');if(!piste)return;const pan=document.getElementById('dpan'),dnom=document.getElementById('dnom'),drole=document.getElementById('drole'),dgr=document.getElementById('dgr');const total=se.segments[se.segments.length-1].fin;
  se.segments.forEach(seg=>{const e=document.createElement('div');e.className=`seg seg-${seg.couleur}`;e.style.width=`${(seg.duree/total)*100}%`;e.style.height=`${seg.hauteur}%`;e.title=seg.nom;
    e.addEventListener('click',()=>{if(segActif)segActif.classList.remove('actif');if(segActif===e){segActif=null;pan.classList.remove('visible');return;}segActif=e;e.classList.add('actif');dnom.textContent=seg.nom;drole.textContent=seg.role;dgr.innerHTML=`<div><div class="di-label">Durée</div><div class="di-val">${fmt(seg.duree)}</div></div><div><div class="di-label">Bloc</div><div class="di-val">${seg.bloc}</div></div><div><div class="di-label">Début</div><div class="di-val">${fmt(seg.debut)}</div></div><div><div class="di-label">Fin</div><div class="di-val">${fmt(seg.fin)}</div></div>`;pan.classList.add('visible');});
    piste.appendChild(e);});
}
hydrateLogs();renderHeader();renderPlan();rwAuto();
if('serviceWorker'in navigator)navigator.serviceWorker.register('./sw.js').catch(()=>{});
