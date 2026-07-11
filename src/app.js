/* ===== helpers ===== */
function rpeColor(r){return r<=3?'#16a34a':r<=5?'#0d9488':r<=6.9?'#f59e0b':r<=8?'#f59e0b':'#ef4444';}
function rpeScale(r){let h='';for(let i=1;i<=10;i++){const on=i<=Math.round(r);h+=`<div class="rpe-seg" style="background:${on?rpeColor(r):''}"></div>`;}return h;}
function catBadge(c){return c==='specifique'?'<span class="cat-badge cat-specifique">Spécifique</span>':'<span class="cat-badge cat-classique">Classique</span>';}
function stChip(st){const m={a_faire:['st-afaire','À faire'],fait:['st-fait','Fait ✓'],partiel:['st-partiel','Partiel'],manque:['st-manque','Manqué'],skipped:['st-manque','Sautée']};const x=m[st]||m.a_faire;return `<span class="st-chip ${x[0]}">${x[1]}</span>`;}
function prCelebration(o){if(!o)return'';const pr=o.pr||0,ach=o.ach||0;if(pr+ach<=0)return'';
  const parts=[];if(pr>0)parts.push(`<span class="prc-stat"><span class="prc-n">${pr}</span> record${pr>1?'s':''} perso</span>`);
  if(ach>0)parts.push(`<span class="prc-stat"><span class="prc-n">${ach}</span> trophée${ach>1?'s':''} de segment</span>`);
  const detail=(o.pr_detail&&o.pr_detail.length)?`<div class="prc-detail">${o.pr_detail.map(d=>`<span class="prc-chip">🥇 ${d}</span>`).join('')}</div>`:'';
  return `<div class="prc"><div class="prc-burst">🎉</div><div class="prc-body"><div class="prc-titre">Records tombés !</div><div class="prc-row">${parts.join('<span class="prc-sep">·</span>')}</div>${detail}</div></div>`;}
function fmt(s){const m=Math.floor(s/60),x=s%60;return x?`${m} min ${String(x).padStart(2,'0')}`:`${m} min`;}
function paceFmt(s){const m=Math.floor(s/60),x=Math.round(s%60);return `${m}:${String(x).padStart(2,'0')}`;}
function isoWeek(d){d=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()));const day=d.getUTCDay()||7;d.setUTCDate(d.getUTCDate()+4-day);const ys=new Date(Date.UTC(d.getUTCFullYear(),0,1));return Math.ceil((((d-ys)/86400000)+1)/7);}

/* ===== graphes SVG ===== */
function chartLine(vals,o){o=o||{};const color=o.color||'#0d9488',h=o.h||150,fmtY=o.fmtY||(v=>v),baseline=o.baseline,todayIdx=o.todayIdx,labels=o.labels;
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
  const cur=`<circle cx="${X(0).toFixed(1)}" cy="${Y(wks[0].km).toFixed(1)}" r="7" fill="#16a34a" opacity=".25"/><circle cx="${X(0).toFixed(1)}" cy="${Y(wks[0].km).toFixed(1)}" r="3.5" fill="#16a34a"/>`;
  const cols=wks.map((w,i)=>`<rect x="${(X(i)-(W-2*padX)/n/2).toFixed(1)}" y="0" width="${((W-2*padX)/n).toFixed(1)}" height="${h}" fill="transparent" style="cursor:pointer" onclick="ouvrirSemaine(${w.num})"><title>S${w.num} · ${w.theme} · ${w.km} km</title></rect>`).join('');
  return `<svg viewBox="0 0 ${W} ${h}" class="chart-svg"><defs><linearGradient id="mtn" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#f59e0b" stop-opacity=".45"/><stop offset=".55" stop-color="#0d9488" stop-opacity=".2"/><stop offset="1" stop-color="#16a34a" stop-opacity="0"/></linearGradient></defs><path d="${area}" fill="url(#mtn)"/><path d="${line}" fill="none" stroke="#475569" stroke-width="2"/>${mk(42,'⛰️','Pic 88',true)}${mk(37,'🏕️','USA',false)}${mk(45,'🏁','Nice',true)}${mk(48,'🌙','SaintExpress',false)}${cur}${kmlab}${cols}</svg>`;
}
function svgDonut(segs){const tot=segs.reduce((a,s)=>a+s.val,0)||1;let a=-90,paths='';const R=54,r=31,cx=64,cy=64;
  segs.forEach(s=>{const ang=s.val/tot*360,a2=a+ang;const P=(deg,rad)=>[cx+rad*Math.cos(Math.PI*deg/180),cy+rad*Math.sin(Math.PI*deg/180)];const large=ang>180?1:0;const[x1,y1]=P(a,R),[x2,y2]=P(a2,R),[x3,y3]=P(a2,r),[x4,y4]=P(a,r);paths+=`<path d="M ${x1.toFixed(1)} ${y1.toFixed(1)} A ${R} ${R} 0 ${large} 1 ${x2.toFixed(1)} ${y2.toFixed(1)} L ${x3.toFixed(1)} ${y3.toFixed(1)} A ${r} ${r} 0 ${large} 0 ${x4.toFixed(1)} ${y4.toFixed(1)} Z" fill="${s.color}"/>`;a=a2;});
  return `<svg viewBox="0 0 128 128" width="120" height="120">${paths}</svg>`;
}

function delta(series,good){const v=series.filter(x=>x!=null);if(v.length<2)return'';const d=v[v.length-1]-v[v.length-2];if(Math.abs(d)<0.5&&good!=='down')return '<span class="delta" style="color:#94a3b8">\u25aa stable</span>';const up=d>0;const isGood=good?((good==='up'&&up)||(good==='down'&&!up)):null;const col=isGood===null?'#64748b':(isGood?'#16a34a':'#ef4444');const a=up?'\u25b2':'\u25bc';const val=Math.abs(d)>=1?Math.round(Math.abs(d)):Math.abs(d).toFixed(1);return `<span class="delta" style="color:${col}">${a} ${val} vs S-1</span>`;}

/* ===== thème ===== */
function toggleTheme(){const n=document.body.classList.toggle('nuit');document.getElementById('themebtn').textContent=n?'☀️':'🌙';}

/* ===== onglets ===== */
let _planAutoJumped=false;
function showTab(t){
  if(navigator.vibrate)try{navigator.vibrate(8)}catch(e){}
  ['accueil','plan','cockpit','palmares'].forEach(id=>{
    document.getElementById('vue-'+id).style.display=t===id?'block':'none';
    document.getElementById('tab-'+id).classList.toggle('actif',t===id);
  });
  if(t==='cockpit'){renderCockpit();renderDash();}
  if(t==='palmares')renderPalmares();
  if(t==='plan'&&!_planAutoJumped){
    _planAutoJumped=true;
    window.scrollTo(0,0);
    setTimeout(()=>jumpToWeek(isoWeek(new Date())),60);
  }else{
    window.scrollTo(0,0);
  }
  const _vw=document.getElementById('vue-'+t);
  if(_vw){_vw.classList.remove('vue-in');void _vw.offsetWidth;_vw.classList.add('vue-in');}
  if(typeof _revealScan==='function')_revealScan();
  const _fab=document.getElementById('fab-jump-week');
  if(_fab)_fab.classList.toggle('tab-plan-active',t==='plan');
  if(t==='plan'&&typeof _initJumpFabWatch==='function')_initJumpFabWatch();
}
let _revealIO=null;
function _revealScan(){
  if(!('IntersectionObserver' in window))return;
  if(!_revealIO)_revealIO=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.remove('rv-init');e.target.classList.add('rv-show');_revealIO.unobserve(e.target);}});},{threshold:.08,rootMargin:'0px 0px -6% 0px'});
  let scope=document;
  ['accueil','plan','cockpit','palmares'].forEach(function(id){var v=document.getElementById('vue-'+id);if(v&&v.style.display!=='none')scope=v;});
  scope.querySelectorAll('.sem-carte,.ck-card,.statut-carte,.pal-carte,.dash-card').forEach(function(el){
    if(el.classList.contains('rv-show'))return;
    var r=el.getBoundingClientRect();
    if(r.top<window.innerHeight*0.95){el.classList.remove('rv-init');el.classList.add('rv-show');return;}
    if(!el.classList.contains('rv-init'))el.classList.add('rv-init');
    _revealIO.observe(el);
  });
  setTimeout(function(){document.querySelectorAll('.rv-init').forEach(function(el){el.classList.remove('rv-init');el.classList.add('rv-show');});},4000);
}

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

/* ACWR dynamique — méthode EMA (même que PMC) recalculé à chaque ouverture */

/* ===== Recalcul dynamique des KPI depuis les séances réelles (à chaque chargement) ===== */
function _weekNumFromKey(k){var m=String(k).match(/(\d+)/);return m?+m[1]:0;}
function _reFromSeance(s){
  // 1) RE réel parsé du commentaire ("RE 106")
  if(s.realise&&s.realise.commentaire){var m=s.realise.commentaire.match(/RE\s+(\d+)/);if(m)return +m[1];}
  // 2) sinon estimation depuis km + type
  if(!s.realise||!s.realise.km)return 0;
  var km=s.realise.km,t=(s.type||'').toLowerCase();
  var coef=8;
  if(/trail/.test(t))coef=25;
  else if(/seuil|tempo|specifique|spécifique|marathon/.test(t))coef=13;
  else if(/longue|long/.test(t))coef=10;
  else if(/récup|recup|recovery/.test(t))coef=6;
  else if(/ef|footing|aérobie|aerobie|technique/.test(t))coef=8;
  return Math.round(km*coef);
}
function _curWeek(){
  // Semaine du plan basée sur la date réelle. Ancre : 9 mars 2026 = lundi = S11.
  var now=new Date();
  var monday=new Date(now);var day=now.getDay()||7;monday.setDate(now.getDate()-(day-1));
  monday.setHours(0,0,0,0);
  var anchor=new Date(2026,2,9);anchor.setHours(0,0,0,0); // 9 mars 2026
  var weeks=Math.round((monday-anchor)/(7*86400000));
  var wk=11+weeks;
  return (wk>=1&&wk<=53)?wk:26; // garde-fou : plage plausible sinon fallback
}

function _ckRebuild(){
  if(typeof SEANCES_BY_WEEK==='undefined'||typeof _CK==='undefined')return;
  // Snapshot one-shot des séries d'allure par type (ef/am/se) issues des données statiques,
  // pour ne pas les perdre quand le moteur reconstruit _CK.PACE (le moteur ne les recalcule pas).
  if(_CK.PACE&&!_CK._PACE_ORIG){try{_CK._PACE_ORIG=JSON.parse(JSON.stringify(_CK.PACE));}catch(e){_CK._PACE_ORIG=null;}}
  // Collecter les semaines avec des séances réalisées
  var weeks=Object.keys(SEANCES_BY_WEEK).map(_weekNumFromKey).filter(function(n){return n>0;}).sort(function(a,b){return a-b;});
  // Agréger km / RE / D+ / allure / FC / cadence réels par semaine
  var agg={};
  weeks.forEach(function(wn){
    var arr=SEANCES_BY_WEEK[String(wn)]||SEANCES_BY_WEEK[wn]||[];
    var km=0,re=0,dplus=0,fcSum=0,fcN=0,cadSum=0,cadN=0,paceSum=0,paceN=0,hasReal=false;
    arr.forEach(function(s){
      var r=s.realise;
      if(r&&(r.statut==='fait'||r.statut==='partiel')&&r.km){
        hasReal=true;km+=r.km;re+=_reFromSeance(s);
        var dm=r.commentaire&&r.commentaire.match(/D\+\s*(\d+)/);if(dm)dplus+=+dm[1];
        if(r.fc_moy){fcSum+=r.fc_moy;fcN++;}
        var cm=r.commentaire&&r.commentaire.match(/cadence\s+(\d+)/);if(cm){cadSum+=+cm[1];cadN++;}
        if(r.allure){var pm=r.allure.match(/(\d+):(\d+)/);if(pm){paceSum+=(+pm[1])*60+(+pm[2]);paceN++;}}
      }
    });
    if(hasReal)agg[wn]={km:+km.toFixed(1),re:re,dplus:dplus,fc:fcN?Math.round(fcSum/fcN):null,cad:cadN?Math.round(cadSum/cadN):null,pace:paceN?Math.round(paceSum/paceN):null};
  });
  var realWeeks=Object.keys(agg).map(Number).sort(function(a,b){return a-b;});
  if(realWeeks.length<2)return; // pas assez de données, on garde _CK figé
  // ACWR EMA (CTL 42j / ATL 7j) sur la série RE complète
  var reSeries=realWeeks.map(function(w){return agg[w].re;});
  var aC=1-Math.exp(-7/42),aA=1-Math.exp(-7/7);
  var acwrByWeek={},ctl=reSeries[0],atl=reSeries[0];
  realWeeks.forEach(function(w,i){
    var v=agg[w].re;
    if(i>0){ctl=(1-aC)*ctl+aC*v;atl=(1-aA)*atl+aA*v;}
    acwrByWeek[w]=ctl>0?+((atl/ctl).toFixed(2)):1.0;
  });
  // Reconstruire les fenêtres 2/4/8/12 de _CK
  function lastN(n){return realWeeks.slice(-n);}
  function wlabels(ws){return ws.map(function(w){return 'S'+w;});}
  [2,4,8,12].forEach(function(N){
    var ws=lastN(N);var lbl=wlabels(ws);
    if(_CK.VOL)_CK.VOL[N]={w:lbl,p:ws.map(function(){return null;}),a:ws.map(function(w){return agg[w].km;})};
    if(_CK.RE)_CK.RE[N]={w:lbl,v:ws.map(function(w){return agg[w].re;})};
    if(_CK.ACWR)_CK.ACWR[N]={w:lbl,v:ws.map(function(w){return acwrByWeek[w];})};
    if(_CK.DPLUS)_CK.DPLUS[N]={w:lbl,v:ws.map(function(w){return agg[w].dplus;})};
    if(_CK.FCZ&&agg[ws[ws.length-1]].fc){/* FCZ gardé tel quel, structure complexe */}
    if(_CK.CAD)_CK.CAD[N]={w:lbl,v:ws.map(function(w){return agg[w].cad;})};
    if(_CK.PACE){var _pp=(_CK._PACE_ORIG&&_CK._PACE_ORIG[N])||{};var _L=lbl.length;var _tail=function(a){return Array.isArray(a)?a.slice(-_L):a;};_CK.PACE[N]={w:lbl,v:ws.map(function(w){return agg[w].pace;}),ef:_tail(_pp.ef),am:_tail(_pp.am),se:_tail(_pp.se)};}
  });
  // Mettre à jour ACWR_DATA (valeur de secours) avec la dernière valeur réelle
  if(typeof ACWR_DATA!=='undefined'){
    var lastW=realWeeks[realWeeks.length-1];
    ACWR_DATA.acwr=acwrByWeek[lastW];
    ACWR_DATA.charge7j=agg[lastW].re;
    var s28=realWeeks.slice(-4);ACWR_DATA.charge28j=s28.reduce(function(a,w){return a+agg[w].re;},0);
  }
}

function _dynamicACWR(){
  const today=new Date();today.setHours(0,0,0,0);
  const curWk=isoWeek(today);
  const ckRe=typeof _CK!=='undefined'&&_CK.RE?_CK.RE[12]:null;
  if(!ckRe||!ckRe.v||ckRe.v.length<2){
    return typeof ACWR_DATA!=='undefined'?ACWR_DATA.acwr||1.0:1.0;
  }
  // RE estimé depuis séances loggées semaine courante
  const RC={EF:7,AM:16,LONG:10,SEUIL:13,TRAIL:22,RENFO:4,default:8};
  let curRE=0;
  (SEANCES_BY_WEEK[curWk]||[]).forEach(s=>{
    if(s.realise&&s.realise.statut==='fait'&&s.realise.km)curRE+=s.realise.km*(RC[s.cat]||RC.default);
  });
  const series=[...ckRe.v];
  const lastW=ckRe.w[ckRe.w.length-1];
  if(curWk>lastW&&curRE>0)series.push(curRE);
  else if(curWk===lastW&&curRE>series[series.length-1])series[series.length-1]=curRE;
  // EMA CTL (42j) + ATL (7j) → ACWR = ATL/CTL
  const aC=1-Math.exp(-7/42),aA=1-Math.exp(-7/7);
  let ctl=series[0],atl=series[0];
  series.forEach((v,i)=>{if(i>0){ctl=(1-aC)*ctl+aC*v;atl=(1-aA)*atl+aA*v;}});
  return ctl>0?+((atl/ctl).toFixed(2)):1.0;
}

/* ===== Score de forme composite (Sprint A Roadmap) ===== */
function computeFormeScore(){
  const today=new Date();today.setHours(0,0,0,0);
  const curWk=isoWeek(today);
  // 1. ACWR (30%) — dynamique depuis _CK.RE + logs
  let acwrScore=70,acwrVal=1.0,acwrLabel='—';
  acwrVal=_dynamicACWR();
  if(acwrVal>=0.8&&acwrVal<=1.3){acwrScore=100;acwrLabel='Zone optimale ('+acwrVal+')';}
  else if(acwrVal>1.3&&acwrVal<=1.5){acwrScore=58;acwrLabel='⚠ Charge élevée ('+acwrVal+')';}
  else if(acwrVal>1.5){acwrScore=22;acwrLabel='🔴 Surcharge ('+acwrVal+')';}
  else if(acwrVal>=0.7){acwrScore=72;acwrLabel='Légère sous-charge ('+acwrVal+')';}
  else{acwrScore=44;acwrLabel='Sous-charge ('+acwrVal+')';}
  // 2. Adhérence 2 sem (25%)
  let totalP=0,totalF=0;
  for(let w=curWk-1;w<=curWk;w++){const ss=SEANCES_BY_WEEK[w]||[];totalP+=ss.filter(s=>!s.opt).length;totalF+=ss.filter(s=>s.realise&&s.realise.statut==='fait').length;}
  const adherScore=totalP>0?Math.min(100,Math.round(totalF/totalP*108)):75;
  // 3. Z2 pace trend (25%)
  const efSess=[];
  Object.entries(SEANCES_BY_WEEK).forEach(([wk,ss])=>ss.forEach(s=>{
    if(s.realise&&s.realise.allure&&(s.cat==='EF'||(s.type||'').includes('EF'))){
      const p=s.realise.allure.replace('/km','').split(':');
      if(p.length===2)efSess.push({wk:+wk,pace:+p[0]*60+(+p[1]||0)});
    }
  }));
  let z2Score=72,z2Label='—';
  const rEf=efSess.filter(x=>x.wk>=curWk-1).map(x=>x.pace);
  const oEf=efSess.filter(x=>x.wk<curWk-1&&x.wk>=curWk-5).map(x=>x.pace);
  if(rEf.length&&oEf.length){
    const d=(oEf.reduce((a,b)=>a+b)/oEf.length)-(rEf.reduce((a,b)=>a+b)/rEf.length);
    if(d>15){z2Score=100;z2Label='+'+Math.round(d)+'s/km ↑↑';}
    else if(d>5){z2Score=88;z2Label='+'+Math.round(d)+'s/km ↑';}
    else if(d>-5){z2Score=75;z2Label='Stable';}
    else if(d>-15){z2Score=52;z2Label=Math.round(d)+'s/km ↓';}
    else{z2Score=32;z2Label=Math.round(d)+'s/km ↓↓';}
  }
  // 4. Fraîcheur (20%)
  let freshScore=75,freshLabel='—';
  const doneSess=Object.values(SEANCES_BY_WEEK).flat().filter(s=>s.realise&&s.realise.statut==='fait'&&s.date).sort((a,b)=>b.date.localeCompare(a.date));
  if(doneSess.length){
    const days=Math.round((today-new Date(doneSess[0].date+'T00:00:00'))/86400000);
    if(days===0){freshScore=68;freshLabel='Couru aujourd\'hui';}
    else if(days===1){freshScore=85;freshLabel='1 jour de repos';}
    else if(days===2){freshScore=95;freshLabel='2 jours · frais';}
    else if(days===3){freshScore=85;freshLabel='3 jours · prêt';}
    else{freshScore=58;freshLabel=days+' jours sans courir';}
  }
  const score=Math.round(acwrScore*.30+adherScore*.25+z2Score*.25+freshScore*.20);
  const color=score>=82?'#0d9488':score>=68?'#16a34a':score>=52?'#f59e0b':'#ef4444';
  const trend=acwrVal<=1.3&&adherScore>=90?'↑':acwrVal>1.4?'↓':'→';
  let signal='';
  if(acwrVal>1.4)signal='⚠️ Charge élevée · éviter les intensités';
  else if(adherScore>=98)signal='Adhérence parfaite · plan bien tenu';
  else if(z2Score>=88)signal='Z2 en progression · forme aérobie solide';
  else if(freshScore>=90)signal='Bien reposé · prêt pour une qualité';
  else if(score>=82)signal='Forme au top · continue sur cette lancée';
  else signal='Paramètres équilibrés · maintenir le rythme';
  return{score,trend,color,signal,components:[
    {label:'ACWR',score:acwrScore,detail:acwrLabel},
    {label:'Adhérence',score:adherScore,detail:totalF+'/'+totalP+' séances (2 sem.)'},
    {label:'Z2 pace',score:z2Score,detail:z2Label},
    {label:'Fraîcheur',score:freshScore,detail:freshLabel}
  ]};
}

function _coachNudge(){
  // Copilote : suggestion proactive contextuelle. Retourne null si rien de pertinent (jamais intrusif).
  try{
    const cur=isoWeek(new Date());
    const acwr=(typeof _dynamicACWR==='function')?_dynamicACWR():1.0;
    const forme=(typeof computeFormeScore==='function')?computeFormeScore():{score:75};
    // Toutes les séances réellement loggées, triées par date
    const done=[];
    Object.entries(SEANCES_BY_WEEK).forEach(([wk,ss])=>ss.forEach(s=>{
      if(s.realise&&s.realise.statut==='fait'&&s.date)done.push({date:s.date,type:(s.type||'')});
    }));
    done.sort((a,b)=>b.date.localeCompare(a.date));
    const today=new Date();today.setHours(0,0,0,0);
    // Jours depuis la dernière séance qualité (seuil / tempo / VMA / fractionné / côtes)
    const isQuality=t=>/seuil|tempo|vma|fraction|c[ôo]tes?|intervalle|allure/i.test(t);
    let lastQ=null;
    for(const d of done){if(isQuality(d.type)){lastQ=d.date;break;}}
    const daysSinceQ=lastQ?Math.floor((today-new Date(lastQ+'T12:00:00'))/86400000):999;
    const daysSinceAny=done.length?Math.floor((today-new Date(done[0].date+'T12:00:00'))/86400000):999;
    // Priorité aux signaux de risque, puis de relance
    if(acwr>1.5)
      return {tone:'warn',icon:'\u{1F534}',txt:'Ton ACWR est \u00e0 '+acwr.toFixed(2)+' \u2014 charge aigu\u00eb \u00e9lev\u00e9e. Priorise la r\u00e9cup ces prochains jours.'};
    if(daysSinceAny>=5&&daysSinceAny<900)
      return {tone:'info',icon:'\u{1F440}',txt:daysSinceAny+' jours sans sortie logg\u00e9e. Tout va bien ? Une sortie facile relancerait la machine.'};
    if(acwr<0.7&&daysSinceAny<5)
      return {tone:'info',icon:'\u{1F4C8}',txt:'Charge basse (ACWR '+acwr.toFixed(2)+') \u2014 de la marge pour ajouter du volume si la forme suit.'};
    if(daysSinceQ>=10&&daysSinceQ<900)
      return {tone:'info',icon:'\u26a1',txt:daysSinceQ+' jours sans s\u00e9ance qualit\u00e9. Un seuil ou un tempo ferait progresser ton chrono.'};
    if(forme.score>=85)
      return {tone:'ok',icon:'\u{1F7E2}',txt:'Forme \u00e0 '+forme.score+'/100 \u2014 excellent moment pour une s\u00e9ance qualit\u00e9 si le plan s\u2019y pr\u00eate.'};
    return null;
  }catch(e){return null;}
}
function _computeStreak(){
  // Signature : nombre de semaines consécutives (jusqu'à la semaine en cours) avec au moins une séance faite.
  try{
    const cur=isoWeek(new Date());
    let streak=0;
    for(let w=cur;w>0;w--){
      const ss=SEANCES_BY_WEEK[w];
      if(!ss)break;
      const done=ss.some(s=>s.realise&&(s.realise.statut==='fait'||s.realise.statut==='partiel'));
      if(done)streak++;
      else if(w<cur)break; // la semaine en cours peut être encore vide sans casser la série
    }
    return streak;
  }catch(e){return 0;}
}
function _whatsNew(){
  // Détecte ce qui a changé depuis la dernière visite (nouvelle séance, PR, forme, streak).
  // Ephémère : ne se montre qu'une fois par changement (signature sauvegardée immédiatement).
  try{
    const done=[];
    Object.entries(SEANCES_BY_WEEK).forEach(([wk,ss])=>ss.forEach(s=>{
      if(s.realise&&s.realise.statut==='fait'&&s.date)done.push({date:s.date,km:s.realise.km||0,pr:(parseInt(s.realise.pr,10)||0)+(parseInt(s.realise.ach,10)||0)});
    }));
    done.sort((a,b)=>b.date.localeCompare(a.date));
    const lastDate=done.length?done[0].date:'';
    const lastPr=done.length?done[0].pr:0;
    const lastKm=done.length?done[0].km:0;
    const forme=(typeof computeFormeScore==='function')?computeFormeScore().score:null;
    const streak=(typeof _computeStreak==='function')?_computeStreak():0;
    const cur={lastDate,forme,streak};
    let prev=null;try{prev=JSON.parse(localStorage.getItem('wn_seen')||'null');}catch(e){}
    localStorage.setItem('wn_seen',JSON.stringify(cur));
    if(!prev)return null; // première visite : rien à comparer
    let msg=null;
    if(lastDate&&lastDate>prev.lastDate){
      if(lastPr>0)msg={icon:'\u{1F3C5}',txt:lastPr+' record'+(lastPr>1?'s':'')+' battu'+(lastPr>1?'s':'')+' depuis ta derni\u00e8re visite !'};
      else msg={icon:'\u2705',txt:'Nouvelle s\u00e9ance logg\u00e9e : '+String(lastKm).replace('.',',')+' km'};
    }else if(streak>(prev.streak||0)&&streak>=2){
      msg={icon:'\u{1F525}',txt:streak+' semaines d\u2019affil\u00e9e maintenant !'};
    }else if(forme!==null&&prev.forme!==null&&Math.abs(forme-prev.forme)>=8){
      msg=forme>prev.forme?{icon:'\u{1F4C8}',txt:'Ta forme a progress\u00e9 : '+prev.forme+' \u2192 '+forme}:null;
    }
    return msg;
  }catch(e){return null;}
}
function _timelineHTML(){
  // Frise "trajectoire vers Nice" : phases de la saison jusqu'à la semaine du marathon.
  try{
    if(typeof PHASES==='undefined'||!PHASES.length||typeof RACES==='undefined')return '';
    const nice=RACES.find(r=>/nice/i.test(r.nom));
    if(!nice)return '';
    const niceWeek=(new Date(nice.date)).toLocaleDateString?(function(){const d=new Date(nice.date);const dd=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()));const day=dd.getUTCDay()||7;dd.setUTCDate(dd.getUTCDate()+4-day);const ys=new Date(Date.UTC(dd.getUTCFullYear(),0,1));return Math.ceil((((dd-ys)/86400000)+1)/7);})():45;
    // Parser les phases, ne garder que celles jusqu'à (et incluant) la semaine du marathon
    const parsed=PHASES.map(p=>{const m=(p.sem||'').match(/S(\d+)\s*[–-]\s*S?(\d+)?/);return {nom:p.nom,start:m?+m[1]:0,end:m?(+m[2]||+m[1]):0};}).filter(p=>p.start>0);
    const relevant=parsed.filter(p=>p.start<=niceWeek);
    if(!relevant.length)return '';
    const startWk=relevant[0].start;
    const curWk=isoWeek(new Date());
    const totalSpan=Math.max(1,niceWeek-startWk);
    const prog=Math.max(0,Math.min(100,Math.round((curWk-startWk)/totalSpan*100)));
    const curPhase=relevant.find(p=>curWk>=p.start&&curWk<=p.end)||relevant[relevant.length-1];
    const jRace=Math.max(0,Math.ceil((new Date(nice.date)-new Date())/86400000));
    const cible=(typeof PROFIL!=='undefined'&&PROFIL.cible_marathon)?PROFIL.cible_marathon:'3h45';
    const segs=relevant.map(p=>{
      const w=((p.end-p.start+1)/totalSpan*100).toFixed(2);
      const isCur=p===curPhase;
      return `<div class="tl-seg${isCur?' tl-cur':''}" style="width:${w}%" title="${p.nom}"></div>`;
    }).join('');
    return `<div class="timeline-wrap" onclick="showTab('plan')">
      <div class="tl-head"><span class="tl-phase">${curPhase.nom}</span><span class="tl-week">S${curWk}</span></div>
      <div class="tl-track">${segs}<div class="tl-fill" style="width:${prog}%"></div><div class="tl-you" style="left:${prog}%"></div></div>
      <div class="tl-foot"><span>Début S${startWk}</span><span class="tl-goal">🏁 Nice · J-${jRace} · ${cible}</span></div>
    </div>`;
  }catch(e){return '';}
}
function renderHeader(){
  const cur=isoWeek(new Date());const sc=SEMAINES.find(s=>s.num===cur)||SEMAINES[0];
  const _t=new Date();_t.setHours(0,0,0,0);
  const _ps=prochaineSeance();let _psCard='';
  // Feature 2 — ajustement allure selon température
  let _tempAdj='';
  try{const mc=JSON.parse(localStorage.getItem('meteo_cache')||'null');
    if(mc&&mc.temp!==undefined){
      const _diff0=_ps?Math.round((_ps.d-_t)/86400000):0;
      const refT=Math.round(_diff0<=1&&mc.tomorrow_max?mc.tomorrow_max:mc.temp);
      if(refT>22){const adj=refT<26?10:refT<30?20:refT<34?30:40;
        _tempAdj=`<div class="vdj-adj">🌡️ ${refT}° · allure cible <strong>+${adj}s/km</strong></div>`;}
    }}catch(e){}
  if(_ps){
    const _diff=Math.round((_ps.d-_t)/86400000);
    const _J=['dimanche','lundi','mardi','mercredi','jeudi','vendredi','samedi'];
    const _M=['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.'];
    const _jn=_J[_ps.d.getDay()];
    const _lbl=_diff===0?"Aujourd'hui":_diff===1?'Demain':_jn.charAt(0).toUpperCase()+_jn.slice(1)+' '+_ps.d.getDate()+' '+_M[_ps.d.getMonth()];
    const _se=_ps.se;
    const _fit=_se.fit?`<a class="vdj-fit" href="${_se.fit}" download onclick="event.stopPropagation()">⌚ Télécharger la séance</a>`:'';
    const _dist=(_se.metriques&&_se.metriques.Distance)?' · '+_se.metriques.Distance:'';
    const _shoe=_se.chaussure?`<div class="vdj-shoe">👟 ${_se.chaussure}</div>`:'';
    _psCard=`<div class="vdj" onclick="ouvrirSeance(${_ps.wk},${_se.id})"><div class="vdj-lbl">Prochaine séance · ${_lbl}</div><div class="vdj-t">${_se.titre}</div><div class="vdj-s">${_se.type}${_dist} · S${_ps.wk}</div>${_shoe}<div class="vdj-depart" id="vdj-depart" style="display:none"></div>${_fit}${_tempAdj}</div>`;
  }
  // Sprint 1 — Score de forme en tuile compacte
  const _forme=computeFormeScore();
  const _formeTile=`<button class="htile htile-forme" onclick="document.getElementById('forme-detail').classList.toggle('fd-open')"><span class="ht-k">Forme du jour <span class="ht-help" role="button" tabindex="0" onclick="event.stopPropagation();openFormeHelp()">\u24d8</span></span><span class="ht-v" style="color:${_forme.color}">${_forme.score}<span class="ht-trend">${_forme.trend}</span></span><span class="ht-s">${_forme.signal}</span></button>`;
  const _formeDetail=`<div class="forme-detail" id="forme-detail">${_forme.components.map(c=>`<div class="fd-row"><div class="fd-lbl">${c.label}</div><div class="fd-track"><div class="fd-fill" style="width:${c.score}%;background:${c.score>=80?'#0d9488':c.score>=65?'#16a34a':c.score>=50?'#f59e0b':'#ef4444'}"></div></div><div class="fd-val">${c.detail}</div></div>`).join('')}</div>`;
  // Sprint 1 — courses : la plus proche en tuile, les autres repliees
  let _nearTile='',_mini='';
  if(RACES&&RACES.length){
    const _rc=RACES.map(r=>Object.assign({},r,{dn:Math.max(0,Math.ceil((new Date(r.date)-_t)/86400000))})).sort((a,b)=>a.dn-b.dn);
    const _n=_rc[0];
    _nearTile=`<button class="htile htile-race" ${_n.dossier?`onclick="ouvrirDossier('${_n.dossier}')"`:''}><span class="ht-k">Prochaine course</span><span class="ht-v">J-${_n.dn}</span><span class="ht-s">${_n.nom}</span>${_n.dossier?'<span class="ht-arr">\u203a</span>':''}</button>`;
    _mini=_rc.slice(1).map(r=>`<button class="hmini" ${r.dossier?`onclick="ouvrirDossier('${r.dossier}')"`:''}><span class="hmini-n">J-${r.dn}</span>${r.nom}${r.dossier?'<span class="hmini-go">\u203a</span>':''}</button>`).join('');
  }
  const _latestBuild=(typeof CHANGELOG!=='undefined'&&CHANGELOG.length)?CHANGELOG[0].build:'—';
  const _latestDate=(typeof CHANGELOG!=='undefined'&&CHANGELOG.length&&CHANGELOG[0].date)?CHANGELOG[0].date:MAJ;
  const _maj=`<div class="vdj-maj">Données à jour au ${_latestDate}<button id="build-badge" onclick="openVersionPanel()">Build ${_latestBuild}</button></div>`;
  document.getElementById('cd-strip').innerHTML='';
  const _cw=`<button class="cw-link" onclick="jumpToWeek(${sc.num})"><span class="cw-pin">📍</span><span class="cw-txt">Tu es en <strong>S${sc.num} · ${sc.theme}</strong></span><span class="cw-arr">voir dans le plan →</span></button>`;
  const _nudge=_coachNudge();
  const _nudgeCard=_nudge?`<button class="coach-nudge cn-${_nudge.tone}" onclick="openCoach()"><span class="cn-ico">${_nudge.icon}</span><span class="cn-txt">${_nudge.txt}</span><span class="cn-go">Coach ›</span></button>`:'';
  const _wn=_whatsNew();
  const _wnCard=_wn?`<div class="whats-new"><span class="wn-ico">${_wn.icon}</span><span class="wn-txt">${_wn.txt}</span></div>`:'';
  const _tl=_timelineHTML();
  document.getElementById('hero-plan').innerHTML=`${_psCard}${_wnCard}<div class="hx-row">${_formeTile}${_nearTile}</div>${_tl}${_formeDetail}<div id="canicule-banner" style="display:none"></div>${_cw}${_nudgeCard}<div id="meteo-widget" class="meteo"><div class="meteo-loc">⏳ Météo…</div></div>${_mini?`<div class="hmini-row">${_mini}</div>`:''}`;
  renderMeteo();
  document.getElementById('maj-foot').innerHTML=_maj;
   try{const _aSe=Object.values(SEANCES_BY_WEEK).flat();const _aF=_aSe.filter(s=>s.realise&&(s.realise.statut==='fait'||s.realise.statut==='partiel')).length;const _aKm=Math.round(_aSe.reduce((a,s)=>a+((s.realise&&s.realise.km)||0),0));const _aP=_aSe.length?Math.round(_aF/_aSe.length*100):0;const _ae=document.getElementById('accueil-annee');const _aStreak=_computeStreak();const _streakTile=_aStreak>=2?`<div class="acc-stat acc-streak"><div class="av">${_aStreak}<span>\u{1F525}</span></div><div class="ak">Sem. d\u2019affil\u00e9e</div></div>`:'';if(_ae)_ae.innerHTML=`<div class="acc-lab">Bilan du plan</div><div class="acc-annee ${_streakTile?'has-streak':''}"><div class="acc-stat"><div class="av">${_aF}</div><div class="ak">Sorties</div></div><div class="acc-stat"><div class="av">${_aKm}<span>km</span></div><div class="ak">R\u00e9alis\u00e9</div></div><div class="acc-stat"><div class="av">${_aP}<span>%</span></div><div class="ak">Pr\u00e9pa plan</div></div>${_streakTile}</div>`;}catch(e){}
  const _ab=document.getElementById('appbar');if(_ab&&document.documentElement)document.documentElement.style.setProperty('--appbar-h',_ab.offsetHeight+'px');
}

/* ===== Widget météo (accueil) — Open-Meteo, lieu fixé Lyon quai des Bons Enfants ===== */
const METEO_LAT=45.76,METEO_LON=4.83,METEO_TTL=30*60*1000;
function _meteoEmoji(c){
  if(c===0)return'☀️';
  if(c===1||c===2)return'⛅';
  if(c===3)return'☁️';
  if(c===45||c===48)return'🌫️';
  if(c>=51&&c<=57)return'🌦️';
  if((c>=61&&c<=67)||(c>=80&&c<=82))return'🌧️';
  if((c>=71&&c<=77)||c===85||c===86)return'🌨️';
  if(c>=95)return'⛈️';
  return'🌡️';
}
function _meteoPaint(d){
  const el=document.getElementById('meteo-widget');if(!el)return;
  const t=(d.temp!==undefined&&!isNaN(+d.temp))?d.temp:d.app;
  const tempStr=Math.round(t)+'°'+(d.app!==undefined&&Math.round(d.app)!==Math.round(t)?' <small>ressenti '+Math.round(d.app)+'°</small>':'');
  const precipStr=(d.precip!==undefined?d.precip.toFixed(1)+' mm · ':'')+Math.round(d.rain)+'%';
  const tmaxOk=d.tomorrow_max!==undefined&&!isNaN(d.tomorrow_max);
  const demainHtml=tmaxOk?
    '<div class="meteo-demain">Demain&nbsp;&nbsp;<span class="meteo-demain-t">'+d.tomorrow_max+'°</span>'+
    (d.tomorrow_max>33?'&nbsp;<span class="meteo-badge canicule">⚠️ Canicule</span>':d.tomorrow_max>28?'&nbsp;<span class="meteo-badge chaud">🌡️ Chaud</span>':'')+'</div>':'';
  const showChip=Math.round(t)>28||(tmaxOk&&d.tomorrow_max>28);
  const chipHtml=showChip?
    '<div class="wx-chip" onclick="openCreneaux()">'+
      '<span class="wx-chip-ico">🌡️</span>'+
      '<div class="wx-chip-body"><div class="wx-chip-title">Créneaux d\'entraînement</div><div class="wx-chip-sub">Meilleures heures aujourd\'hui et demain</div></div>'+
      '<span class="wx-chip-arr">›</span></div>':'';
  el.innerHTML=
    '<div class="meteo-row">'+
      '<span class="meteo-ico">'+_meteoEmoji(d.code)+'</span>'+
      '<span class="meteo-temp">'+tempStr+'</span>'+
      '<span class="meteo-metrics">'+
        '<span class="meteo-m">💨 '+Math.round(d.wind)+' km/h</span>'+
        '<span class="meteo-m">🌧️ '+precipStr+'</span>'+
      '</span>'+
    '</div>'+demainHtml+chipHtml;
  if(d.hourly_today||d.hourly_tomorrow)window._wxHourly={today:d.hourly_today||[],tomorrow:d.hourly_tomorrow||[]};
  // Feature 3 — bannière canicule auto
  const canDays=d.canicule_days||0;
  const canEl=document.getElementById('canicule-banner');
  if(canEl){if(canDays>=3){canEl.innerHTML=`<span>☀️ <strong>Canicule</strong> · ${canDays}j chauds prévus</span>`;canEl.style.display='flex';}else{canEl.style.display='none';}}
  const depEl=document.getElementById('vdj-depart');
  if(depEl){
    const T=Math.round(d.tomorrow_max!==undefined?d.tomorrow_max:d.temp);
    if(T>=26){depEl.innerHTML=`🌡️ ${T}° demain — <strong>pars avant 8h30</strong>`;depEl.style.display='block';}
    else{depEl.style.display='none';}
  }
}
async function renderMeteo(){
  let cached=null;
  try{cached=JSON.parse(localStorage.getItem('meteo_cache')||'null');}catch(e){}
  /* cache valide seulement si la structure inclut temp (sinon re-fetch immédiat) */
  const cacheOk=cached&&cached.temp!==undefined&&Date.now()-cached.ts<METEO_TTL;
  if(cached)_meteoPaint(cached);
  if(cacheOk)return;
  try{
    const u='https://api.open-meteo.com/v1/forecast?latitude='+METEO_LAT+'&longitude='+METEO_LON+
      '&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,precipitation'+
      '&hourly=temperature_2m,precipitation_probability&daily=temperature_2m_max&forecast_days=10&timezone=Europe%2FParis';
    const r=await fetch(u);if(!r.ok)throw 0;
    const j=await r.json();
    const todayStr=new Date().toISOString().slice(0,10);
    const tomorrowStr=new Date(Date.now()+86400000).toISOString().slice(0,10);
    let rain=0;const hToday=[],hTomorrow=[];
    if(j.hourly&&j.hourly.time){
      const curH=j.current.time?j.current.time.slice(0,13):'';
      j.hourly.time.forEach((tt,i)=>{
        if(tt.slice(0,13)===curH)rain=j.hourly.precipitation_probability[i]||0;
        const h=parseInt(tt.slice(11,13)),ds=tt.slice(0,10);
        if(h>=5&&h<=22){const tp=Math.round(j.hourly.temperature_2m[i]);
          if(ds===todayStr)hToday.push([h,tp]);
          if(ds===tomorrowStr)hTomorrow.push([h,tp]);}
      });
    }
    const tMax=hTomorrow.length?Math.max(...hTomorrow.map(x=>x[1])):undefined;
    let caniculeDays=0;
    if(j.daily&&j.daily.temperature_2m_max){j.daily.temperature_2m_max.forEach(t=>{if(t>28)caniculeDays++;});}
    const d={ts:Date.now(),temp:j.current.temperature_2m,app:j.current.apparent_temperature,wind:j.current.wind_speed_10m,code:j.current.weather_code,precip:j.current.precipitation||0,rain,tomorrow_max:tMax,hourly_today:hToday,hourly_tomorrow:hTomorrow,canicule_days:caniculeDays};
    localStorage.setItem('meteo_cache',JSON.stringify(d));
    _meteoPaint(d);
  }catch(e){
    if(!cached){const el=document.getElementById('meteo-widget');if(el)el.innerHTML='<div style="font-size:.75rem;color:var(--texte-trois)">🌡️ Météo indisponible</div>';}
  }
}

/* ===== PLAN ===== */
function renderPlan(){const phasesEl=document.getElementById('phases');phasesEl.innerHTML='';const _cur=isoWeek(new Date());
  PHASES.forEach(ph=>{const bloc=document.createElement('div');bloc.className='phase-bloc';const sems=SEMAINES.filter(s=>s.phase===ph.id);
    const cartes=sems.map(s=>{const ses=SEANCES_BY_WEEK[s.num]||[];const fait=ses.filter(x=>x.realise&&(x.realise.statut==='fait'||x.realise.statut==='partiel')).length;
      const cnt=s.num===24?`<div class="sem-km" style="margin-top:4px"><span>${S24R.runs.length} sorties · ${S24R.km} km réalisés</span></div>`:(ses.length?`<div class="sem-km" style="margin-top:4px"><span>${fait}/${ses.length} séances</span></div>`:'');
      const badge=s.num===_cur?`<div class="sem-statut st-courante">En cours</div>`:'';
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
    '<div class="cal-legend"><span><i class="cal-lg cal-g"></i>Réalisé</span><span><i class="cal-lg cal-o"></i>Non réalisé</span><span><i class="cal-lg cal-x"></i>À venir</span><span style="opacity:.45;margin-left:auto">build 37</span></div>'+_emptyCal;
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
let _jumpFabIO=null;
function _initJumpFabWatch(){
  const cur=isoWeek(new Date());const el=document.getElementById('wk-'+cur);const fab=document.getElementById('fab-jump-week');
  if(!el||!fab)return;
  if(!('IntersectionObserver' in window)){fab.classList.add('visible');return;}
  if(_jumpFabIO)_jumpFabIO.disconnect();
  _jumpFabIO=new IntersectionObserver(entries=>{
    entries.forEach(e=>fab.classList.toggle('visible',!e.isIntersecting));
  },{threshold:0,rootMargin:'-'+((document.getElementById('appbar')?.offsetHeight||60)+10)+'px 0px 0px 0px'});
  _jumpFabIO.observe(el);
}
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
  const deltaTxt=ahead>=0?`<strong style="color:#16a34a">${ahMin} min d\u2019avance</strong> sur l\u2019objectif 3h45`
    :`<strong style="color:#f59e0b">+${ahMin} min</strong> au-dessus de 3h45`;
  const deltaShort=ahead>=0?`${ahMin} min d'avance sur l'objectif 3h45`:`${ahMin} min au-dessus de 3h45 — le bloc va combler l'écart`;
  let clarte;
  if(P.n===0)clarte=`<div class="cb-clarte">🌫️ <strong>Boule encore voilée.</strong> La projection part de ta forme actuelle (${PROJ.base_label}). Elle s'affinera à chaque séance qualité loguée — le <strong>test 10 km de la S31</strong> sera le premier gros recalibrage, puis chaque seuil et chaque séance d'allure marathon.</div>`;
  else clarte=`<div class="cb-clarte">🔮 <strong>${P.n} séance${P.n>1?'s':''} qualité intégrée${P.n>1?'s':''}.</strong> Plus tu logues de qualité, plus la projection se précise.</div>`;
  const sources=P.n?`<div class="cb-src"><div class="cb-src-t">Ce qui nourrit la projection</div>${P.sources.map(s=>`<div class="cb-src-l"><span>${s.label}${s.sub?` · ${s.sub}`:''}</span><span class="cb-src-v">${_s2hm(s.sec)}</span></div>`).join('')}<div class="cb-src-l cb-src-base"><span>Forme de départ (référence)</span><span class="cb-src-v">${_s2hm(PROJ.base)}</span></div></div>`:'';
  const trend=P.trend.length>=2?`<div class="cb-trend"><div class="cb-src-t">Affinage de la projection séance après séance</div>${chartLine(P.trend.map(v=>v/60),{color:'#0d9488',h:120,fmtY:v=>_s2hm(v*60),baseline:goal/60,annotate:true})}</div>`:'';
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
  const pol=[{label:'Très facile',val:POLAR.tres_facile,color:'#bbf7d0'},{label:'EF facile',val:POLAR.ef,color:'#16a34a'},{label:'Zone grise',val:POLAR.gris,color:'#f59e0b'},{label:'Qualité',val:POLAR.qualite,color:'#ef4444'}];
  const histKm=HIST.map(h=>h.km);const histRe=HIST.map(h=>h.re);const histLab=HIST.map(h=>h.sem);

  // Couleur ACWR
  const acwr=ACWR_DATA.acwr;const acwrCol=acwr>1.5?'#ef4444':acwr<0.8?'#0d9488':'#16a34a';
  const acwrLabel=acwr>1.5?'Attention — charge élevée':acwr<0.8?'Frais / allègement':'Charge maîtrisée';

  // Chaussures
  const maxShKm=Math.max(...GEAR.map(g=>g.km));
  const shoes=GEAR.slice().sort((a,b)=>b.km-a.km).map(g=>{
    const col=g.km>900?'#ef4444':g.km>700?'#f59e0b':'#16a34a';
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
      <div class="dstat" style="--accent:#0d9488"><div class="dstat-l">Sorties</div><div class="dstat-v">${SAISON2026.sorties}</div><div class="dstat-s">en ${SAISON2026.mois} mois</div></div>
      <div class="dstat" style="--accent:#16a34a"><div class="dstat-l">Kilométrage</div><div class="dstat-v">${SAISON2026.km}</div><div class="dstat-s">km parcourus</div></div>
      <div class="dstat" style="--accent:#f59e0b"><div class="dstat-l">Dénivelé +</div><div class="dstat-v">${SAISON2026.elev.toLocaleString()}</div><div class="dstat-s">mètres</div></div>
      <div class="dstat" style="--accent:#0d9488"><div class="dstat-l">Prépa plan</div><div class="dstat-v">${faites}/${total}</div><div class="dstat-s">séances réalisées</div></div>
    </div>
    <div class="kpi-t" style="font-size:.88rem;margin-bottom:8px">Volume mensuel (km)</div>
    ${svgMonthly('km','#0d9488',v=>Math.round(v))}
    <div style="margin-top:14px">
    <div class="kpi-t" style="font-size:.88rem;margin-bottom:8px">Dénivelé mensuel (m)</div>
    ${svgMonthly('elev','#f59e0b',v=>v>=1000?(v/1000).toFixed(1)+'k':v)}</div>
    <div style="margin-top:14px">
    <div class="kpi-t" style="font-size:.88rem;margin-bottom:8px">Sorties par mois</div>
    ${svgMonthly('sorties','#0d9488',v=>v)}</div>
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
    <div style="margin-top:14px">${delta(histRe)} ${chartLine(histRe,{color:'#0d9488',labels:histLab,annotate:true,h:140})}</div>
  </div>

  <!-- 5. Volume hebdo -->
  <div class="kpi"><div class="kpi-t">📈 Ton volume — historique 28 semaines</div><div class="kpi-r">Tes vraies semaines Strava. Le plan prend le relais à la S25.</div>${delta(histKm)} ${chartLine(histKm,{color:'#0d9488',labels:histLab,fmtY:v=>Math.round(v)+'km',annotate:true,h:150})}</div>

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
        <td style="padding:9px 6px;text-align:center"><div style="font-weight:700;color:#0d9488">${r.temps_act}</div><div style="font-size:.7rem;color:var(--texte-trois)">${r.actuel_sub}</div></td>
        <td style="padding:9px 6px;text-align:right"><div style="font-weight:700">${r.actuel}</div></td>
      </tr>`).join('')}</tbody>
    </table>
    <div style="margin-top:14px"><div class="kpi-t" style="font-size:.88rem;margin-bottom:8px">Allures de course estimées (Riegel)</div>
    <div class="course-grid">${ALLURES_COURSE.map(a=>`<div class="course-row"><span class="course-d">${a.d}</span><span class="course-t">${a.temps}</span><span class="course-a">${a.allure}</span></div>`).join('')}</div></div>
  </div>

  <!-- 9. Objectifs course -->
  <div class="kpi">
    <div class="kpi-t">🎯 Objectifs course</div>
    <div class="kpi-r">Trois objectifs, trois logiques différentes.</div>
    <div class="dash-stats">
      <div class="dstat" style="--accent:#0d9488"><div class="dstat-l">J avant Déraille</div><div class="dstat-v">J-${cd[0]}</div><div class="dstat-s">Trail 24 km · 5 juil. · plaisir & test nutrition</div></div>
      <div class="dstat" style="--accent:#f59e0b"><div class="dstat-l">J avant Nice</div><div class="dstat-v">J-${cd[1]}</div><div class="dstat-s">Marathon 8 nov. · objectif 3h45</div></div>
      <div class="dstat" style="--accent:#0d9488"><div class="dstat-l">J avant SaintExpress</div><div class="dstat-v">J-${cd[2]}</div><div class="dstat-s">45 km night trail 28 nov.</div></div>
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
document.addEventListener('keydown',e=>{if(e.key!=='Escape')return;
  // Ferme l'overlay actuellement ouvert (priorité au plus au-dessus)
  var coach=document.getElementById('coach-ov');
  if(coach&&coach.classList.contains('open')){if(typeof closeCoach==='function')closeCoach();return;}
  var help=document.getElementById('ck-help-ov');
  if(help&&help.classList.contains('open')){if(typeof closeCkHelp==='function')closeCkHelp();return;}
  var ver=document.getElementById('version-ov');
  if(ver&&ver.classList.contains('open')){if(typeof closeVersionPanel==='function')closeVersionPanel();return;}
  if(typeof fermer==='function')fermer();
});
const btnFermer='<button class="btn-close-round" onclick="fermer()" aria-label="Fermer la fiche">✕</button>';


function s24Chart(splits){const n=splits.length,W=720,h=190,padL=8,padR=8,padT=26,padB=30;
  const paces=splits.map(s=>s[0]),hrs=splits.map(s=>s[1]);
  const spd=paces.map(p=>1000/p);const sMin=Math.min(...spd)*0.94,sMax=Math.max(...spd)*1.03;
  const hMin=Math.min(...hrs)-6,hMax=Math.max(...hrs)+8;
  const bw=(W-padL-padR)/n;
  const bars=splits.map((s,i)=>{const sp=1000/s[0];const bh=(sp-sMin)/(sMax-sMin)*(h-padT-padB);const x=padL+i*bw,y=h-padB-bh;
    const pm=Math.floor(s[0]/60),ps=Math.round(s[0]%60);
    return `<rect x="${(x+2).toFixed(1)}" y="${y.toFixed(1)}" width="${(bw-4).toFixed(1)}" height="${bh.toFixed(1)}" rx="3" fill="#0d9488" opacity=".55"/>
      <text x="${(x+bw/2).toFixed(1)}" y="${(h-padB+11).toFixed(1)}" font-size="7.6" fill="#94a3b8" text-anchor="middle">${pm}:${String(ps).padStart(2,'0')}</text>
      <text x="${(x+bw/2).toFixed(1)}" y="${(h-padB+21).toFixed(1)}" font-size="6.8" fill="#cbd5e1" text-anchor="middle">km${i+1}</text>`;}).join('');
  const HY=v=>padT+(h-padT-padB)*(1-(v-hMin)/(hMax-hMin));
  const line='M '+hrs.map((v,i)=>`${(padL+i*bw+bw/2).toFixed(1)} ${HY(v).toFixed(1)}`).join(' L ');
  const hrlab=hrs.map((v,i)=>{if(i===0||i===n-1||v===Math.max(...hrs))return `<text x="${(padL+i*bw+bw/2).toFixed(1)}" y="${(HY(v)-6).toFixed(1)}" font-size="8" font-weight="700" fill="#ef4444" text-anchor="middle">${v}</text>`;return '';}).join('');
  return `<svg viewBox="0 0 ${W} ${h}" class="chart-svg">${bars}<path d="${line}" fill="none" stroke="#ef4444" stroke-width="2" stroke-linejoin="round"/>${hrlab}
    <text x="${padL}" y="11" font-size="8.5" fill="#0d9488" font-weight="700">▮ Allure /km</text><text x="${padL+74}" y="11" font-size="8.5" fill="#ef4444" font-weight="700">— FC moyenne /km</text></svg>`;
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

function dosProfilSVG(D,ac){
  const pts=D.profil_pts; if(!pts||!pts.length)return '';
  const n=pts.length,dist=D.profil_dist||24.06;
  const W=620,H=172,padL=32,padR=10,padT=18,padB=20;
  const plotW=W-padL-padR,plotH=H-padT-padB;
  const mn=Math.min(...pts),mx=Math.max(...pts);
  const lo=Math.floor((mn-15)/100)*100,hi=Math.ceil((mx+15)/100)*100;
  const X=i=>padL+i/(n-1)*plotW, Y=v=>padT+plotH-(v-lo)/(hi-lo)*plotH;
  let d=`M ${X(0).toFixed(1)} ${Y(pts[0]).toFixed(1)}`;
  for(let i=1;i<n;i++)d+=` L ${X(i).toFixed(1)} ${Y(pts[i]).toFixed(1)}`;
  const area=d+` L ${X(n-1).toFixed(1)} ${(padT+plotH).toFixed(1)} L ${X(0).toFixed(1)} ${(padT+plotH).toFixed(1)} Z`;
  const yl=[lo,hi].map(v=>`<line x1="${padL}" y1="${Y(v).toFixed(1)}" x2="${W-padR}" y2="${Y(v).toFixed(1)}" class="dp-grid"/><text x="${padL-5}" y="${(Y(v)+3).toFixed(1)}" class="dp-ax" text-anchor="end">${v}</text>`).join('');
  const xl=[0,8,16,24].map(km=>{const xx=padL+Math.min(km,dist)/dist*plotW;return `<text x="${xx.toFixed(1)}" y="${H-5}" class="dp-ax" text-anchor="middle">${km}</text>`;}).join('');
  let mi=0;for(let i=0;i<n;i++)if(pts[i]>pts[mi])mi=i;
  const sx=X(mi),sy=Y(pts[mi]);
  const sum=`<circle cx="${sx.toFixed(1)}" cy="${sy.toFixed(1)}" r="3.4" fill="${ac}"/><text x="${sx.toFixed(1)}" y="${(sy-7).toFixed(1)}" class="dp-mk" text-anchor="middle">${pts[mi]} m</text>`;
  return `<svg class="dos-prof" viewBox="0 0 ${W} ${H}" role="img" aria-label="Profil réel du parcours"><style>.dp-ax{font:600 9px system-ui;fill:#94a3b8}.dp-grid{stroke:#e2e8f0;stroke-width:1}.dp-mk{font:700 9.5px system-ui;fill:${ac}}</style>${yl}<path d="${area}" fill="${ac}" opacity="0.13"/><path d="${d}" fill="none" stroke="${ac}" stroke-width="2.4" stroke-linejoin="round"/>${sum}${xl}</svg><div class="dos-prof-cap">Profil réel (trace GPX officielle) · altitude (m) en ordonnée, distance (km) en abscisse · sommet 897 m vers le km 15</div>`;
}
/* ===== Checklist J-7 par course ===== */
const CK_SECS={deraille:[
  {id:'equip',ico:'🎒',title:'Équipement',items:[
    {id:'dossard',label:'Dossard récupéré',note:'À retirer sur place le matin dès 7h30'},
    {id:'gilet',label:'Gilet HDV5 préparé',note:'Flasques 2×500ml · sifflet · couverture de survie obligatoire'},
    {id:'cascadia',label:'Cascadia 19 vérifiées',note:'Lacets · semelles · pas de nouveauté le jour J'},
    {id:'tenue',label:'Tenue de course posée',note:'Short · t-shirt technique · casquette · crème solaire'},
    {id:'garmin',label:'Garmin chargé + contact urgence',note:'Fenix 6 Pro · ceinture cardiaque Decathlon chargée'}
  ]},
  {id:'nutrition',ico:'⚡',title:'Nutrition & hydratation',items:[
    {id:'ta_tube',label:'TA Electrolytes — tube complet',note:'Min. 6 cpr · 2 départ + 1 ravito km 8 + 1 après'},
    {id:'gels_apto',label:'2 gels non-caféinés Aptonia',note:'Km 0 dans gilet + km 8 ravito ou gilet'},
    {id:'cherry',label:'1 Nduranz Cherry 65mg',note:'Km 13-14 — pic d\'effort montée finale'},
    {id:'amarena',label:'1 Nduranz Coffee Amarena 130mg',note:'Km 20-21 — relance pour la descente finale'},
    {id:'ptidej',label:'Petit-déjeuner J-0 planifié',note:'Pâtes la veille · toast + œuf le matin · 1 cpr TA 1h avant'}
  ]},
  {id:'logistique',ico:'🗺️',title:'Logistique',items:[
    {id:'transport',label:'Transport organisé',note:'Lac des Sapins — Valsonne 69170 · ~1h de Lyon'},
    {id:'horaire',label:'Heure de départ vague connue',note:'Consulter site officiel · départ prévu ~9h'},
    {id:'ravitos',label:'Ravitos repérés',note:'2 ravitos sur le parcours · km ~8 et ~15'},
    {id:'dropbag',label:'Sac de récupération préparé',note:'Vêtements chauds · chaussures · snack post-course'}
  ]},
  {id:'technique',ico:'🧠',title:'Stratégie de course',items:[
    {id:'plan_relu',label:'Plan d\'exécution relu',note:'4 étapes · montée progressive · pas de départ trop vite'},
    {id:'allures',label:'Allures cibles mémorisées',note:'~9:30/km montée · flotter en descente · FC max 165'},
    {id:'electro',label:'Protocole électrolytes mémorisé',note:'2 cpr départ + 1 cpr ravito km 8 · toujours avec eau'},
    {id:'cafeine',label:'Protocole caféine mémorisé',note:'Cherry km 13 · Amarena km 20 · pas avant'}
  ]},
  {id:'recup',ico:'🛌',title:'Récupération J+0',items:[
    {id:'ta_apres',label:'1 cpr TA immédiatement à l\'arrivée',note:'Dans la poche short · ne pas oublier même euphorique'},
    {id:'vetements',label:'Vêtements chauds accessibles',note:'Le corps refroidit vite après l\'arrivée en altitude'}
  ]}
],nice:[
  {id:'equip',ico:'🎽',title:'Équipement',items:[
    {id:'dossard',label:'Dossard / billet TER récupéré',note:'Le dossard vaut billet de train Nice · vérifier horaire'},
    {id:'novablast',label:'Novablast 5 V (vertes) prêtes',note:'Chaussures de course fraîches · vérifier lacets et semelles'},
    {id:'tenue',label:'Tenue marathon posée',note:'Short · t-shirt · manchons si froid matinal · casquette'},
    {id:'garmin',label:'Garmin + ceinture chargés',note:'Profil marathon configuré · contact urgence · playlist'},
    {id:'gels_kit',label:'Kit nutrition du matin préparé',note:'TA + gels dans poche accessible dès le départ'}
  ]},
  {id:'nutrition',ico:'⚡',title:'Nutrition J-0',items:[
    {id:'ta_réveil',label:'2 cpr TA au réveil (5h)',note:'Avec grand verre d\'eau · avant le petit-déjeuner'},
    {id:'ptidej',label:'Petit-déjeuner 3h avant départ',note:'Toast + banane + café · rien de nouveau · connu et testé'},
    {id:'gel0',label:'1 gel Aptonia 15min avant le départ',note:'Dans les starting blocks · déclenche les réserves'},
    {id:'gels',label:'Gels Aptonia km 8 · 16 · 24 prêts',note:'Poche droite accessible · 1 gel toutes les 8 bornes'},
    {id:'cherry',label:'Nduranz Cherry km 32',note:'Anti-mur · NE PAS OUBLIER · 65mg caféine'},
    {id:'amarena',label:'Nduranz Coffee Amarena km 38',note:'Relance finale · 130mg caféine · tout lâcher ensuite'}
  ]},
  {id:'logistique',ico:'🚂',title:'Logistique',items:[
    {id:'ter',label:'Billet TER Nice confirmé',note:'Dossard = billet · horaire aller + retour validé'},
    {id:'hébergement',label:'Hébergement J-1 confirmé',note:'Arriver la veille · pâtes le soir · calme garanti'},
    {id:'expo',label:'Retrait dossard planifié',note:'Horaires expo à vérifier · dossard physique si nécessaire'},
    {id:'vague',label:'Numéro de vague connu',note:'Vague 3h30-3h59 · arriver 45min avant le départ'}
  ]},
  {id:'stratégie',ico:'🧠',title:'Stratégie de course',items:[
    {id:'allure',label:'5:20/km mémorisé = objectif 3h45',note:'Ne pas partir à 5:10 · les 5 premiers km sont toujours trop rapides'},
    {id:'antibes',label:'Segment Antibes km 25-28 anticipé',note:'+35m D+ · ralentir à 5:30 · FC < 162 · ne pas paniquer'},
    {id:'mur',label:'Plan anti-mur km 30-35 validé',note:'Cherry km 32 · penser technique · rester régulier'},
    {id:'finish',label:'Relance km 38-42 mentalisée',note:'Amarena km 38 · si bien géré → donner le reste'}
  ]},
  {id:'recup',ico:'🛌',title:'Récupération',items:[
    {id:'ta_arrivée',label:'1 cpr TA à l\'arrivée',note:'Dans la poche · avant même la médaille'},
    {id:'vêtements',label:'Vêtements chauds dans sac remis',note:'Le corps chute vite après l\'effort · couche chaude immédiate'}
  ]}
],saintexpress:[
  {id:'equip',ico:'🌙',title:'Équipement nuit',items:[
    {id:'dossard',label:'Dossard récupéré',note:'Retrait sur site Sainte-Catherine · vérifier horaire'},
    {id:'frontale1',label:'Frontale principale chargée',note:'Obligatoire · ≥ 200 lumens · batterie 100%'},
    {id:'frontale2',label:'Frontale de secours',note:'Obligatoire · vérification batterie indépendante'},
    {id:'gilet',label:'Gilet trail nuit complet',note:'Flasques · sifflet · couverture survie · trousse secours'},
    {id:'cascadia',label:'Cascadia 19 (trail technique)',note:'Km 0-27 inconnu · trail technique nocturne'},
    {id:'tenue_nuit',label:'Tenue nuit (0-5°C au départ)',note:'Départ 23h à 757m · manches longues + coupe-vent + gants'}
  ]},
  {id:'nutrition',ico:'⚡',title:'Nutrition (5h30–7h)',items:[
    {id:'ta_gilet',label:'TA Electrolytes dans le gilet',note:'6+ cpr · TA partenaire officiel → aussi aux ravitos'},
    {id:'gels_nuit',label:'2-3 gels Aptonia',note:'Non-caféinés · km ~5 et km ~15'},
    {id:'cherry',label:'Nduranz Cherry km ~27 (Soucieu)',note:'~1h30 du matin · début terrain connu · 65mg caféine'},
    {id:'amarena',label:'Nduranz Coffee Amarena km ~38',note:'Avant les aqueducs · dernier effort technique · 130mg'}
  ]},
  {id:'logistique',ico:'🗺️',title:'Logistique nuit',items:[
    {id:'transport',label:'Transport Sainte-Catherine organisé',note:'757m · ~1h de Lyon · partir à 22h max'},
    {id:'retour',label:'Retour Lyon planifié',note:'Arrivée ~5h-6h matin · transport ou attente organisée'},
    {id:'contact',label:'Contact urgence informé',note:'Sainte-Catherine → Lyon · heure estimée d\'arrivée communiquée'}
  ]},
  {id:'stratégie',ico:'🧠',title:'Stratégie de course',items:[
    {id:'terrain_inconnu',label:'Km 0-27 : terrain INCONNU · très prudent',note:'FC < 160 · marcher les montées dures · ne pas s\'emballer'},
    {id:'terrain_connu',label:'Km 27-45 : terrain CONNU (relay 2022)',note:'Référence : 6:28/km · tu connais ce segment de nuit'},
    {id:'lumière',label:'Gestion lumière planifiée',note:'Frontale sur la tête 100% du parcours · vérifier à mi-course'},
    {id:'ravitos_ta',label:'Ravitos TA repérés',note:'TA partenaire officiel → électrolytes disponibles sur tout le parcours'}
  ]},
  {id:'recup',ico:'🌅',title:'Récupération J+0',items:[
    {id:'ta_arrivée',label:'1 cpr TA immédiatement à l\'arrivée',note:'Arrivée ~5h-6h · corps épuisé · électrolytes en priorité'},
    {id:'vêtements_chauds',label:'Vêtements très chauds à l\'arrivée',note:'Nuit froide · le corps refroidit instantanément à l\'arrêt'},
    {id:'récup_j1',label:'J+1 : journée de repos complet',note:'Aucune reprise avant J+3 · protéines + sommeil'}
  ]}
]};
function _ckLoad(r){try{return JSON.parse(localStorage.getItem('ck_'+r)||'{}')}catch(e){return{};}}
function _ckSave(r,s){localStorage.setItem('ck_'+r,JSON.stringify(s));}
function ckToggle(race,id){const s=_ckLoad(race);s[id]=!s[id];_ckSave(race,s);_ckRender(race);}
function ckToggleSec(race,id){const s=_ckLoad(race);s['_o_'+id]=s['_o_'+id]===false?true:false;_ckSave(race,s);_ckRender(race);}
function ckReset(race){if(confirm('Réinitialiser la checklist ?')){_ckSave(race,{});_ckRender(race);}}
function _ckRender(race){
  const secs=CK_SECS[race];if(!secs)return;
  const st=_ckLoad(race);
  const total=secs.reduce((a,s)=>a+s.items.length,0);
  const done=secs.reduce((a,s)=>a+s.items.filter(it=>st[it.id]).length,0);
  const pb=document.getElementById('ck-pb');if(pb)pb.style.width=(done/total*100)+'%';
  const pc=document.getElementById('ck-pc');if(pc)pc.textContent=done+'/'+total;
  const ps=document.getElementById('ck-ps');if(ps)ps.textContent=done===total?'Tout est prêt ✓':(total-done)+' item'+(total-done>1?'s':'')+' restant'+(total-done>1?'s':'');
  const ad=document.getElementById('ck-ad');if(ad)ad.style.display=done===total?'block':'none';
  const el=document.getElementById('ck-secs');if(!el)return;
  el.innerHTML=secs.map(sec=>{
    const sd=sec.items.filter(it=>st[it.id]).length,all=sd===sec.items.length,open=st['_o_'+sec.id]!==false;
    return`<div class="ck-sc"><div class="ck-sh" onclick="ckToggleSec('${race}','${sec.id}')">
      <span class="ck-si">${sec.ico}</span><span class="ck-st">${sec.title}</span>
      <span class="ck-sb ${all?'ck-sbd':''}">${sd}/${sec.items.length}</span>
      <span class="ck-sa ${open?'ck-sao':''}">›</span></div>
    ${open?`<div class="ck-is">${sec.items.map(it=>`<div class="ck-item" onclick="ckToggle('${race}','${it.id}')">
      <div class="ck-chk ${st[it.id]?'ck-on':''}">${st[it.id]?'✓':''}</div>
      <div class="ck-itx"><div class="ck-il ${st[it.id]?'ck-ild':''}">${it.label}</div>
      ${it.note?`<div class="ck-in">${it.note}</div>`:''}</div></div>`).join('')}</div>`:''}
    </div>`;
  }).join('');
}
function renderChecklistHTML(race){
  if(!CK_SECS[race])return'';
  const total=CK_SECS[race].reduce((a,s)=>a+s.items.length,0);
  return`<h3 class="dos-h3">✅ Checklist J-7</h3>
    <div class="ck-prog"><div class="ck-ph"><span class="ck-ptit">Préparation course</span><span class="ck-pc" id="ck-pc">0/${total}</span></div>
      <div class="ck-pbw"><div class="ck-pb" id="ck-pb" style="width:0%"></div></div>
      <div class="ck-ps" id="ck-ps">${total} items à valider</div></div>
    <div class="ck-done" id="ck-ad" style="display:none">✅&nbsp;&nbsp;<strong>Tout est prêt !</strong> Bonne course 💪</div>
    <div id="ck-secs"></div>
    <button class="ck-rst" onclick="ckReset('${race}')">↺ Réinitialiser</button>`;
}

function ouvrirDossier(id){
  const D=(typeof DOSSIERS!=='undefined')?DOSSIERS[id]:null; if(!D)return;
  const ac=D.accent||'#0d9488';
  const stats=D.stats.map(s=>`<div class="dos-stat"><div class="dos-stat-v">${s[0]}</div><div class="dos-stat-l">${s[1]}</div></div>`).join('');
  const segs=D.segments.map(s=>`<div class="dos-seg"><div class="dos-seg-h"><span class="dos-seg-t">${s.t}</span><span class="dos-seg-km">${s.km}</span></div><div class="dos-seg-f">${s.faire}</div></div>`).join('');
  const plan=D.plan.map(p=>`<div class="dos-plan" style="--pc:${p.c}"><div class="dos-plan-h"><span class="dos-plan-n">${p.n}</span><span class="dos-plan-titre">${p.titre}</span><span class="dos-plan-tag">${p.tag}</span></div><div class="dos-plan-txt">${p.txt}</div><div class="dos-plan-fuel">⛽ ${p.fuel}</div></div>`).join('');
  const nut=D.nutrition.items.map(i=>`<div class="dos-nut"><div class="dos-nut-n">${i[0]}</div><div class="dos-nut-d">${i[1]}</div><div class="dos-nut-r">${i[2]}</div></div>`).join('');
  const zones=D.zones.map(z=>`<div class="dos-zone"><span class="dos-zone-n">${z[0]}</span><span class="dos-zone-fc">${z[1]}</span><span class="dos-zone-o">${z[2]}</span></div>`).join('');
  const prat=D.pratique.map(p=>`<div class="dos-prat"><div class="dos-prat-l">${p[0]}</div><div class="dos-prat-v">${p[1]}</div></div>`).join('');
  const err=D.erreurs.map(e=>`<li>${e}</li>`).join('');
  contenu.innerHTML=`
   <div class="dos" style="--ac:${ac}">
     <div class="dos-head">
       <div class="dos-eyebrow">Dossier de course</div>
       <h2 class="dos-nom">${D.nom}</h2>
       <div class="dos-sous">${D.soustitre}</div>
       <div class="dos-meta">${D.date} · ${D.format}<br>${D.depart}</div>
     </div>
     <div class="dos-stats">${stats}</div>
     <div class="dos-intro">${D.intro}</div>
     <div class="dos-phrase">${D.phrase}</div>
     <h3 class="dos-h3">Le profil</h3>
     ${dosProfilSVG(D,ac)}
     <p class="dos-p">${D.profil}</p>
     <h3 class="dos-h3">Le déroulé</h3>
     ${segs}
     <h3 class="dos-h3">Plan d'exécution</h3>
     ${plan}
     <h3 class="dos-h3">Nutrition — le cœur de cette course</h3>
     ${D.nutrition.avant?`<div class="dos-bloc dos-av"><div class="dos-bloc-ico">🌅</div><div><strong>Avant la course</strong><br>${D.nutrition.avant}</div></div>`:''}
     <p class="dos-p">${D.nutrition.intro}</p>
     ${nut}
     <p class="dos-note">${D.nutrition.note}</p>
     <div class="dos-hydra">💧 ${D.hydra}</div>
     ${D.nutrition.apres?`<div class="dos-bloc dos-ap"><div class="dos-bloc-ico">🔄</div><div><strong>Après la course</strong><br>${D.nutrition.apres}</div></div>`:''}
     <h3 class="dos-h3">Zones d'effort (FC)</h3>
     ${zones}
     <h3 class="dos-h3">Terrain &amp; infos pratiques</h3>
     <p class="dos-p">${D.terrain}</p>
     ${prat}
     <h3 class="dos-h3">Les erreurs à ne pas faire</h3>
     <ul class="dos-err">${err}</ul>
     <p class="dos-sources">${D.sources}</p>
     ${renderChecklistHTML(id)}
   </div>`;
  topbar.innerHTML=`<span></span>${btnFermer}`;
  ouvrir();
  if(CK_SECS[id])_ckRender(id);
}
function ouvrirSeanceS24(idx){const r=S24R.runs[idx];if(!r)return;segActif=null;
  topbar.innerHTML=`<button class="btn-nav" onclick="ouvrirSemaine(24)">‹ Retour semaine 24</button>${btnFermer}`;
  const metr=Object.entries(r.metriques).map(([k,v])=>`<div class="metrique"><div class="metrique-l">${k}</div><div class="metrique-v">${v}</div></div>`).join('');
  contenu.innerHTML=`<div class="sd-hero"><div class="hero-badges"><span class="sd-badge" style="background:#16a34a22;color:#15803d">Course à pied</span><span class="st-chip st-fait">Fait ✓</span><span class="seance-tag">${r.tag}</span></div>
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
    const runs=S24R.runs.map((r,i)=>`<div class="seance-carte" onclick="ouvrirSeanceS24(${i})"><div class="seance-bande" style="background:#16a34a"></div><div class="seance-idx">${r.date}</div><div class="seance-info"><div class="seance-nom">${r.titre}</div><div class="seance-desc">${r.desc}</div><div class="seance-tags"><span class="st-chip st-fait">Fait ✓</span><span class="seance-tag">${r.tag}</span><span class="cat-badge cat-classique">Classique</span></div></div><div class="seance-fleche">›</div></div>`).join('');
    contenu.innerHTML=`<div class="sw-hero"><span class="sw-tag" style="background:${COUL[s.phase]}22;color:${COUL[s.phase]}">${ph.nom}</span><h2 class="sw-titre">Semaine ${s.num} — ${s.theme}</h2><p class="sw-sous">Semaine terminée · récupération post-Circaète</p></div>
      <div class="sw-corps"><div class="callout callout-obj">${s.objectif}</div>
      <div class="sw-section">Réalisé sur la semaine — ${S24R.runs.length} sorties · ${S24R.km} km</div><div class="seance-liste">${runs}</div>
      <div style="text-align:center"><button class="rw-btn" onclick="rwOpen('S24')">🎬 Lance le Rewind de ta semaine</button></div><div class="sw-section">Bilan du coach</div><div class="rev-coach">${S24R.revue}</div>
      <div class="sw-section">🎯 Cap sur la S25</div><div class="callout callout-cap">${S25_CAP}</div>
      <p class="note-foot" style="margin-top:24px">La reprise structurée démarre maintenant, en S25.</p></div>`;ouvrir();return;}
  const seances=SEANCES_BY_WEEK[num]||[];const fait=seances.filter(x=>x.realise&&(x.realise.statut==='fait'||x.realise.statut==='partiel')).length;const realKm=seances.reduce((a,x)=>a+((x.realise&&x.realise.km)||0),0);
  topbar.innerHTML=`<span></span>${btnFermer}`;
  const liste=seances.map(se=>{
    const r=se.realise||{statut:'a_faire'};
    const isSkipped=r.statut==='skipped';
    const isDone=r.statut==='fait'||r.statut==='partiel';
    const _today=new Date();_today.setHours(0,0,0,0);
    const loggable=!isDone&&!isSkipped&&se.date&&new Date(se.date+'T00:00:00')<=_today;
    const tags=[stChip(isSkipped?'skipped':r.statut),`<span class="seance-tag">${se.type}</span>`,catBadge(se.cat),`<span class="rpe-pill"><span class="rpe-dot" style="background:${rpeColor(se.rpe)}"></span>RPE ${se.rpe}</span>`];
    if(se.chaussure)tags.push(`<span class="seance-shoe">👟 ${se.chaussure.replace("ASICS ","").replace("HOKA ","").replace("Brooks ","")}</span>`);
    if(se.fit)tags.push('<span class="seance-fit">⌚ .fit</span>');
    if(se.opt)tags.push('<span class="seance-tag tag-opt">Optionnelle</span>');
    if(isSkipped&&r.reason)tags.push(`<span class="seance-tag" style="color:#92400e;background:#fef9c3">⏭ ${r.reason}</span>`);
    const rs=r.km?`<div class="seance-desc" style="color:#15803d;font-weight:700;margin-top:3px">✓ ${r.km} km${r.allure?' · '+r.allure:''}</div>`:'';
    const menuBtn=(!isDone&&!isSkipped)?`<button class="sm-btn" onclick="event.stopPropagation();openSM(${num},'${se.id}')">···</button>`:'';
    const rightEl=isDone
      ?`<div class="seance-fleche sc-check">✓</div>`
      :isSkipped
        ?`<div class="seance-fleche" style="color:#f59e0b;font-size:20px">—</div>`
        :loggable
          ?`<div class="ql-btn"><i class="ti ti-check"></i></div>${menuBtn}`
          :menuBtn;
    const cardClass=isDone?' sc-fait':isSkipped?' sc-skipped':'';
    return `<div class="seance-carte${cardClass}" id="sc-${num}-${se.id}" onclick="${loggable?'ouvrirQuickLog('+num+','+se.id+')':'ouvrirSeance('+num+','+se.id+')'}"  ><div class="seance-bande" style="background:${se.accent}"></div><div class="seance-idx">Séance ${se.num}</div><div class="seance-info"><div class="seance-nom">${se.titre}</div><div class="seance-desc">${se.sous}</div>${rs}<div class="seance-tags">${tags.join('')}</div></div><div class="seance-fleche-wrap">${rightEl}</div></div>`;
  }).join('');
  const repPill=s.repartition&&s.repartition!=='—'?`<div class="sw-pill"><div class="sw-pill-l">Répartition</div><div class="sw-pill-v" style="font-size:.74rem">${s.repartition}</div></div>`:'';
  contenu.innerHTML=`<div class="sw-hero"><span class="sw-tag" style="background:${COUL[s.phase]}22;color:${COUL[s.phase]}">${ph.nom}</span><h2 class="sw-titre">Semaine ${s.num} — ${s.theme}</h2><p class="sw-sous">Semaine type · clique une séance</p><div class="sw-meta"><div class="sw-pill"><div class="sw-pill-l">Volume cible</div><div class="sw-pill-v">${s.km} km</div></div><div class="sw-pill"><div class="sw-pill-l">Réalisé</div><div class="sw-pill-v">${fait}/${seances.length} · ${realKm} km</div></div><div class="sw-pill"><div class="sw-pill-l">Charge</div><div class="sw-pill-v" style="font-size:.84rem">${s.charge}</div></div>${repPill}</div></div><div class="sw-corps"><div class="callout callout-obj">${s.objectif}</div><div class="sw-section">Séances de la semaine</div><div class="seance-liste">${liste}</div>${s.revue?`<div class="sw-section">Revue du coach — bilan de la semaine</div><div class="rev-coach">${s.revue}</div>`:`<div class="realise-empty" style="margin-top:18px"><strong>Revue de la semaine à venir.</strong> Quand la semaine sera bouclée, tu trouveras ici mon bilan complet : volume et charge vs prévu, adhérence, signaux à surveiller, et la décision pour la semaine suivante. Elle alimentera aussi le Journal du coach.</div>`}</div>`;ouvrir();
}
/* ===== Créneaux météo — popup horaire ===== */
function _wxStatus(t){
  if(t<22)return{cls:'wx-ideal',lbl:'🟢 Idéal',c:'#16a34a'};
  if(t<27)return{cls:'wx-ok',lbl:'🟡 OK',c:'#f59e0b'};
  if(t<32)return{cls:'wx-dur',lbl:'🟠 Difficile',c:'#f59e0b'};
  return{cls:'wx-evit',lbl:'🔴 Éviter',c:'#ef4444'};
}
function _wxReco(hrs){
  const ideal=hrs.filter(([h,t])=>t<22);
  const ok=hrs.filter(([h,t])=>t>=22&&t<27);
  const mx=Math.max(...hrs.map(x=>x[1]));
  const peak=(hrs.find(([h,t])=>t===mx)||[null])[0];
  if(ideal.length)return`<strong>Fenêtre idéale :</strong> ${ideal[0][0]}h–${ideal[ideal.length-1][0]+1}h (< 22°C). Pic à ${mx}° vers ${peak}h — éviter impérativement.`;
  if(ok.length)return`<strong>Acceptable :</strong> ${ok[0][0]}h–${ok[ok.length-1][0]+1}h avec hydratation renforcée. Pic à ${mx}° vers ${peak}h.`;
  return`<strong>Journée très difficile.</strong> Pic à ${mx}°. Réduire ou reporter la séance au lendemain matin.`;
}
function _wxRenderTab(k){
  const hrs=k==='today'?(window._wxHourly&&window._wxHourly.today):( window._wxHourly&&window._wxHourly.tomorrow);
  if(!hrs||!hrs.length)return;
  const mx=Math.max(...hrs.map(x=>x[1])),mn=Math.min(...hrs.map(x=>x[1]));
  document.getElementById('wx-reco').innerHTML=_wxReco(hrs);
  document.getElementById('wx-strip').innerHTML=hrs.map(([h,t])=>`<div class="wx-strip-seg" style="background:${_wxStatus(t).c}"></div>`).join('');
  document.getElementById('wx-hours').innerHTML=hrs.map(([h,t])=>{
    const s=_wxStatus(t);const p=mx===mn?50:((t-mn)/(mx-mn)*100).toFixed(0);const hi=s.cls==='wx-ideal'?' wx-hr-hi':'';
    return`<div class="wx-hr${hi}"><span class="wx-hr-t">${h}h</span><div class="wx-hr-bw"><div class="wx-hr-b" style="width:${p}%;background:${s.c}"></div></div><span class="wx-hr-temp">${t}°</span><span class="wx-hr-tag ${s.cls}">${s.lbl}</span></div>`;
  }).join('');
}
function openCreneaux(){
  const data=window._wxHourly;if(!data)return;
  const t0max=data.today.length?Math.max(...data.today.map(x=>x[1])):null;
  const t1max=data.tomorrow.length?Math.max(...data.tomorrow.map(x=>x[1])):null;
  const el0=document.getElementById('wx-t0'),el1=document.getElementById('wx-t1');
  if(el0&&t0max)el0.textContent='Aujourd\'hui · '+t0max+'°';
  if(el1&&t1max)el1.textContent='Demain · '+t1max+'°';
  el0&&el0.classList.add('active');el1&&el1.classList.remove('active');
  document.getElementById('wx-ov').classList.add('open');
  _wxRenderTab('today');
}
function closeCreneaux(){document.getElementById('wx-ov').classList.remove('open');}
function wxTab(k){
  document.getElementById('wx-t0').classList.toggle('active',k==='today');
  document.getElementById('wx-t1').classList.toggle('active',k==='tomorrow');
  _wxRenderTab(k);
}
function initCreneaux(){
  if(!document.body||typeof document.body.insertAdjacentHTML!=='function')return;
  document.body.insertAdjacentHTML('beforeend',`
<div id="wx-ov" onclick="if(event.target===this)closeCreneaux()">
  <div id="wx-sheet">
    <div class="wx-head">
      <div class="wx-handle"></div>
      <div class="wx-sheet-title">🌡️ Créneaux d'entraînement</div>
      <div class="wx-tabs"><div class="wx-tab active" id="wx-t0" onclick="wxTab('today')">Aujourd'hui</div><div class="wx-tab" id="wx-t1" onclick="wxTab('tomorrow')">Demain</div></div>
      <div class="wx-reco" id="wx-reco"></div>
      <div class="wx-strip" id="wx-strip"></div>
    </div>
    <div class="wx-hours" id="wx-hours"></div>
    <button class="wx-close" onclick="closeCreneaux()">Fermer</button>
  </div>
</div>`);}

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
function _celebrateLog(realise){
  // Moment gratifiant quand une séance est loggée "faite". Respecte reduced-motion.
  if(!realise||realise.statut!=='fait')return;
  const nbPr=(parseInt(realise.pr,10)||0)+(parseInt(realise.ach,10)||0);
  const isPr=nbPr>0;
  if(navigator.vibrate)try{navigator.vibrate(isPr?[15,50,15,50,25]:[12,40,12])}catch(e){}
  const prev=document.getElementById('log-celeb');if(prev)prev.remove();
  const km=realise.km?(String(realise.km).replace('.',',')+' km'):'';
  const ov=document.createElement('div');ov.id='log-celeb';ov.className='log-celeb'+(isPr?' lc-pr':'');
  if(isPr){
    const label=(parseInt(realise.pr,10)||0)>0?((parseInt(realise.pr,10))+' record'+((parseInt(realise.pr,10))>1?'s':'')+' battu'+((parseInt(realise.pr,10))>1?'s':'')+' !'):(nbPr+' troph\u00e9e'+(nbPr>1?'s':'')+' !');
    ov.innerHTML='<div class="lc-card"><div class="lc-medal">\u{1F3C5}</div><div class="lc-txt">'+label+'</div>'+(km?'<div class="lc-sub">'+km+'</div>':'')+'</div>';
  }else{
    ov.innerHTML='<div class="lc-card"><div class="lc-check">\u2713</div><div class="lc-txt">S\u00e9ance enregistr\u00e9e</div>'+(km?'<div class="lc-sub">'+km+'</div>':'')+'</div>';
  }
  document.body.appendChild(ov);
  const dur=_reduceMotion()?400:(isPr?1900:1300);
  requestAnimationFrame(()=>ov.classList.add('show'));
  setTimeout(()=>{ov.classList.remove('show');setTimeout(()=>ov.remove(),260);},dur);
}
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
  _celebrateLog(realise);
  _afterLog(wk,id);
}
function unlogSeance(wk,id){const se=findSeance(wk,id);if(!se)return;const logs=loadLogs();delete logs[logId(wk,id)];saveLogs(logs);se.realise={statut:'a_faire'};_afterLog(wk,id);}
/* ===== Cockpit — aides contextuelles ===== */
const _CK_HELP={
  forme:{t:'Forme du jour',c:'#0d9488',body:`<p>La <strong>Forme du jour</strong> est un score de synthèse sur 100 qui résume ton état de préparation actuel, recalculé à chaque ouverture à partir de tes vraies séances loggées.</p>
    <div class="ch-rule"><div class="ch-dot" style="background:#0d9488"></div><div><strong>ACWR (30%)</strong> : équilibre entre ta charge récente et ta charge de fond. Le cœur du score.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#16a34a"></div><div><strong>Adhérence (25%)</strong> : régularité sur les 2 dernières semaines — as-tu fait ce qui était prévu ?</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#0891b2"></div><div><strong>Allure Z2 (25%)</strong> : progression de ton allure en endurance fondamentale, l'indicateur n°1 du moteur aérobie.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#f59e0b"></div><div><strong>Fraîcheur (20%)</strong> : ta charge du moment, pour capter la fatigue accumulée.</div></div>
    <div class="ch-tip">💡 Un score élevé = bon moment pour une séance qualité. Un score bas = privilégie la récup ou l'endurance facile.</div>`},
  pmc:{t:'PMC — Fitness · Fatigue · Forme',c:'#0d9488',body:`<p>Le <strong>Performance Management Chart</strong> (PMC) est le graphe fondamental du coaching de haut niveau — c'est ce qu'utilisent les entraîneurs TrainingPeaks. Il montre l'équilibre entre ta construction de forme et ta fatigue.</p>
    <div class="ch-rule"><div class="ch-dot" style="background:#0d9488"></div><div><strong>CTL — Fitness (teal)</strong> : Charge chronique sur 42 jours. Représente ta forme physique accumulée. Monte lentement avec l'entraînement, descend lentement avec le repos.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#f59e0b"></div><div><strong>ATL — Fatigue (orange tirets)</strong> : Charge aiguë sur 7 jours. Réagit vite aux variations de charge. Monte rapidement après une grosse semaine, descend vite avec le repos.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#16a34a"></div><div><strong>TSB — Forme (barres)</strong> : CTL − ATL. Positif (vert) = tu es frais, reposé. Négatif (rouge) = tu accumules de la fatigue.</div></div>
    <div class="ch-tip">💡 <strong>Comment lire ce graphe pour Nice :</strong> La CTL doit monter progressivement jusqu'à octobre (pic prévu ~65-70), puis la TSB doit remonter en positif grâce au tapering J-21/J-14/J-7. Le jour de Nice, visée : CTL élevée + TSB entre +5 et +20 = pic de forme.</div>`},
  vol:{t:'Volume hebdomadaire',c:'#f59e0b',body:`<p>Kilomètres courus chaque semaine (barres colorées) comparés au volume planifié (barres grises en arrière-plan).</p>
    <div class="ch-rule"><div class="ch-dot" style="background:#f59e0b"></div><div><strong>Barre au-dessus du gris</strong> → tu as sur-performé. Vérifie que ce n'était pas au détriment de la qualité des séances.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#94a3b8"></div><div><strong>Barre en dessous du gris</strong> → semaine incomplète. Normal pendant les allègements ou après une course.</div></div>
    <div class="ch-tip">💡 Tendance à surveiller : une progression de +5–10% max par semaine. Au-delà, tu accumules une dette de récupération même sans le ressentir.</div>`},
  re:{t:'Relative Effort (RE)',c:'#f59e0b',body:`<p>Score de charge calculé par Strava à partir de la fréquence cardiaque. Il intègre à la fois la durée et l'intensité de chaque sortie.</p>
    <div class="ch-rule"><div class="ch-dot" style="background:#16a34a"></div><div><strong>EF 10 km facile</strong> ≈ 40–70 RE</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#f59e0b"></div><div><strong>Sortie longue 16 km</strong> ≈ 150–180 RE</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#ef4444"></div><div><strong>Circaète 30 km trail</strong> ≈ 696 RE</div></div>
    <div class="ch-tip">💡 Glisse le doigt sur le graphe pour voir la valeur semaine par semaine. La tendance sur 8 semaines est plus parlante que la valeur isolée.</div>`},
  acwr:{t:'ACWR — Risque de blessure',c:'#f59e0b',body:`<p>Ratio Charge Aiguë / Charge Chronique (Acute:Chronic Workload Ratio). Compare la charge des 7 derniers jours à la moyenne des 28 derniers jours.</p>
    <div class="ch-rule"><div class="ch-dot" style="background:#0d9488"></div><div><strong>ACWR &lt; 0.8 (bleu)</strong> → Sous-entraîné. Semaine légère ou récup prolongée. Faible risque mais perte de forme.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#16a34a"></div><div><strong>ACWR 0.8–1.3 (vert)</strong> → Zone optimale. Continue sur cette lancée.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#f59e0b"></div><div><strong>ACWR 1.3–1.5 (orange)</strong> → Charge élevée. Pas dangereux si ponctuel, mais surveille.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#ef4444"></div><div><strong>ACWR &gt; 1.5 (rouge)</strong> → Surcharge. Risque de blessure ×5. Réduire l'intensité immédiatement.</div></div>
    <div class="ch-tip">💡 Objectif : rester dans la zone verte 80% du temps. Dépasser 1.3 ponctuellement (semaine de pic avant compétition) est acceptable si les semaines suivantes permettent de récupérer.</div>`},
  dp:{t:'Dénivelé positif (D+)',c:'#0d9488',body:`<p>Mètres de dénivelé positif cumulés par semaine. Indicateur clé pour la préparation aux courses de trail.</p>
    <div class="ch-rule"><div class="ch-dot" style="background:#0d9488"></div><div><strong>Semaine route pure</strong> → D+ ≈ 30–80 m (variation naturelle du terrain)</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#0d9488"></div><div><strong>Semaine trail légère</strong> → D+ 200–500 m</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#f59e0b"></div><div><strong>Semaine spécifique trail</strong> → D+ 600–1000 m</div></div>
    <div class="ch-tip">💡 Pour la Déraille (+901m) et SaintExpress, le D+ hebdo doit idéalement atteindre 500–800m dans les 4 semaines précédentes. Ce graphe permet de vérifier que la spécificité trail est bien intégrée.</div>`},
  z2:{t:'Z2 pace — Allure EF',c:'#0d9488',body:`<p>Allure moyenne de tes footings faciles semaine par semaine. C'est <strong>l'indicateur fondamental</strong> du développement aérobie.</p>
    <p>La Zone 2 = effort où tu peux tenir une conversation. FC < 144 bpm pour toi.</p>
    <div class="ch-rule"><div class="ch-dot" style="background:#0d9488"></div><div><strong>Courbe descendante</strong> (allure plus rapide) = ta forme aérobie progresse. Tu vas plus vite sans travailler plus fort.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#f59e0b"></div><div><strong>Courbe plate</strong> = stagnation. Normal en période de maintien ou de volume élevé.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#ef4444"></div><div><strong>Courbe montante</strong> = régression. Souvent liée à la fatigue, la chaleur, ou un ACWR > 1.3.</div></div>
    <div class="ch-tip">💡 Ton objectif saison : passer de 5:56/km à ~5:40/km en Z2 d’ici octobre. Chaque dixième de seconde gagné reflète une adaptation mitochondriale réelle.</div>`},
  dc:{t:'Découplage cardiaque',c:'#0d9488',body:`<p>Mesure l'écart entre ton allure et ta FC sur une sortie longue. Un faible découplage = ton cœur reste stable alors que tu te fatigues.</p>
    <div class="ch-rule"><div class="ch-dot" style="background:#16a34a"></div><div><strong>&lt; 5% (vert)</strong> → Excellent. Ton système aérobie est solide et stable sur la durée.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#f59e0b"></div><div><strong>5–8% (orange)</strong> → Acceptable. Léger décrochage en fin de sortie, souvent dû à la chaleur ou à la fatigue.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#ef4444"></div><div><strong>&gt; 8% (rouge)</strong> → Problème. Sortie trop longue, trop chaude, ou nutrition insuffisante.</div></div>
    <div class="ch-tip">💡 Ce graphe te dit si tes sorties longues sont vraiment "faciles" ou si ton cœur souffre en fin de sortie sans que tu le ressentes. Un découplage élevé en canicule est normal — c'est pour ça qu'on court avant 8h30.</div>`},
  pace:{t:'Progression allure par type',c:'#16a34a',body:`<p>3 courbes d'allure sur la fenêtre sélectionnée — footings faciles (EF), allure marathon (AM) et seuil. Permet de voir si tu progresses sur tous les registres.</p>
    <div class="ch-rule"><div class="ch-dot" style="background:#16a34a"></div><div><strong>EF (vert)</strong> → Allure Z2, footing facile. Doit descendre progressivement toute la saison.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#0d9488"></div><div><strong>AM (bleu)</strong> → Allure marathon cible. Doit converger vers 5:20/km pour Nice (objectif 3h45).</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#f59e0b"></div><div><strong>Seuil (orange)</strong> → Allure séance AM ou tempo. Reflète ta capacité lactique.</div></div>
    <div class="ch-tip">💡 Glisse le doigt sur le graphe pour voir les 3 valeurs simultanément. L'écart entre EF et seuil = ton amplitude de vitesse. Plus il est grand, meilleur est ton profil de coureur.</div>`},
  fc:{t:'Zones FC — Distribution',c:'#ef4444',body:`<p>Répartition du temps passé dans chaque zone de fréquence cardiaque sur la semaine sélectionnée. Reflète la structure de ton entraînement.</p>
    <div class="ch-rule"><div class="ch-dot" style="background:#0d9488"></div><div><strong>Z1 Récup (&lt;130 bpm)</strong> → Échauffement, récupération active. Peut être augmenté.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#16a34a"></div><div><strong>Z2 Endurance (130–148)</strong> → Moteur aérobie. Doit représenter 70–80% du volume total.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#f59e0b"></div><div><strong>Z3 Seuil (148–163)</strong> → Zone "grise" : trop dur pour récupérer vite, trop facile pour progresser fort. À limiter.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#f59e0b"></div><div><strong>Z4 Lactique (163–178)</strong> → Séances AM, tempo. 15–20% du volume = optimal.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#ef4444"></div><div><strong>Z5 Max (&gt;178)</strong> → Fractionné intense. Réservé aux séances très ciblées.</div></div>
    <div class="ch-tip">💡 Distribution idéale (entraînement polarisé) : 75–80% Z1-Z2 + 5% Z3 + 15–20% Z4-Z5. Trop de Z3 = entraînement "moyen partout" = progression lente.</div>`},
  cad:{t:'Cadence (pas/min)',c:'#6366f1',body:`<p>Nombre de pas par minute. La valeur affichée est en SPM (steps per minute = total des deux pieds). Ta cadence naturelle est d'environ 172–174 spm en route.</p>
    <div class="ch-rule"><div class="ch-dot" style="background:#16a34a"></div><div><strong>170–180 spm</strong> → Zone optimale. Limite l'impact au sol et réduit le risque de blessures aux genoux et hanches.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#f59e0b"></div><div><strong>&lt;170 spm</strong> → Foulée trop longue. Augmente les forces d'impact. Surtout visible en fatigue ou en descente trail.</div></div>
    <div class="ch-rule"><div class="ch-dot" style="background:#6366f1"></div><div><strong>Trail &lt;155 spm</strong> → Normal en montée raide (marche) ou sur terrain très technique.</div></div>
    <div class="ch-tip">💡 Ta cadence trail (146 spm au Circaète) inclut les passages de marche en montée — c'est tout à fait normal. L'écart route/trail que tu vois dans ce graphe est attendu et sain.</div>`}
};
function _ckCtxBlock(key){
  try{
    var D=_CK,W=8;
    var now=new Date();
    var _rd=(typeof RACES!=='undefined'&&RACES.length)?RACES.map(function(r){return Math.ceil((new Date(r.date+'T12:00:00')-now)/86400000);}).filter(function(n){return n>=0;}).sort(function(a,b){return a-b;}):[],jrace=_rd.length?_rd[0]:999;
    var race0=(typeof RACES!=='undefined'&&RACES.length)?RACES.find(function(r){return Math.ceil((new Date(r.date+'T12:00:00')-now)/86400000)>=0;}):null;
    var rname=race0?race0.nom:'la prochaine course';
    var acwr=D.ACWR&&D.ACWR[2]?D.ACWR[2].v[D.ACWR[2].v.length-1]:null;
    var canEl=document.getElementById('canicule-banner');
    var isHot=canEl&&canEl.style.display!=='none'&&canEl.textContent.trim();
    var h='<div class="ck-ctx"><div class="ck-ctx-h">\u{1F4CD} Ta lecture en ce moment</div><p>';
    if(key==='pmc'){
      var pmc=typeof _pmcCompute==='function'?_pmcCompute(W):null;
      if(!pmc||!pmc.length)return '';
      var last=pmc[pmc.length-1];
      var ctl=last.ctl.toFixed(0),atl=last.atl.toFixed(0),tsb=(last.tsb>=0?'+':'')+last.tsb.toFixed(0);
      var tsbCol=last.tsb>5?'#16a34a':last.tsb>-10?'#f59e0b':'#ef4444';
      var lec='';
      if(jrace<=14){
        lec='J-'+jrace+' avant '+rname+' \u2014 ton TSB \u00e0 <strong>'+tsb+'</strong> est '+(last.tsb>5?'positif\u00a0: tu arrives frais, exactement comme voulu.':'encore l\u00e9g\u00e8rement n\u00e9gatif. Normal en aff\u00fbtage \u2014 il remontera d\u2019ici le d\u00e9part si tu restes easy.');
      }else if(jrace<=30){
        lec='\u00c0 J-'+jrace+', l\u2019aff\u00fbtage commence. Ta CTL \u00e0 <strong>'+ctl+'</strong> repr\u00e9sente la forme accumul\u00e9e \u2014 elle va descendre un peu avec la r\u00e9duction du volume, c\u2019est voulu. Objectif\u00a0: TSB \u00e0 +5/+20 le jour J.';
      }else{
        var trend=pmc.length>=4?Math.round(pmc[pmc.length-1].ctl-pmc[pmc.length-4].ctl):null;
        var trendStr=trend!==null?(trend>0?' (+'+trend+' sur 4\u00a0sem. \u2014 bonne progression)':(trend<-2?' ('+trend+' sur 4\u00a0sem. \u2014 surveille la stagnation)':' (stable)')):'';
        var tsbState=last.tsb>5?'tu es frais':last.tsb>-5?'tu es en \u00e9quilibre':'tu accumules de la fatigue\u00a0: soigne le sommeil et garde les footings vraiment faciles';
        lec='Ta CTL est \u00e0 <strong>'+ctl+'</strong>'+trendStr+'. Fatigue ATL <strong>'+atl+'</strong> \u2192 forme TSB <strong style="color:'+tsbCol+'">'+tsb+'</strong> \u2014 '+tsbState+'. Pour '+rname+', vise CTL 65\u201370 + TSB entre +5 et +20 le jour J.';
      }
      if(isHot)lec+=' En canicule\u00a0: l\u2019ATL grimpe plus vite pour la m\u00eame allure \u2014 ton TSB peut para\u00eetre plus bas qu\u2019il n\u2019est. Cours t\u00f4t, r\u00e9duis l\u2019intensit\u00e9 de 10\u201315\u00a0%, \u00e7a ne change pas ta CTL.';
      return h+lec+'</p></div>';
    }
    if(key==='acwr'){
      if(acwr===null)return '';
      var col=acwr>1.3?'#ef4444':acwr<0.8?'#0d9488':'#16a34a';
      var label=acwr>1.5?'en surcharge':acwr>1.3?'charge \u00e9lev\u00e9e':acwr<0.8?'sous-entra\u00een\u00e9':'dans la zone optimale';
      var txt='Ton ACWR est \u00e0 <strong style="color:'+col+'">'+acwr.toFixed(2)+'</strong> \u2014 tu es <strong>'+label+'</strong>.';
      if(acwr>1.3&&jrace<=21)txt+=' J-'+jrace+' avant '+rname+'\u00a0: c\u2019est le moment de lever le pied. R\u00e9duis le volume de 20\u201330\u00a0% cette semaine, garde 2\u20133 acc\u00e9l\u00e9rations courtes, dors bien. Tu arriveras plus frais que si tu pushs.';
      else if(acwr>1.3)txt+=' Surveille les signaux de fatigue (jambes lourdes, sommeil perturb\u00e9, FC matin \u00e9lev\u00e9e). Si un 2\u1d49\u1d49 indicateur clignote, all\u00e8ge la semaine.';
      else if(acwr<0.8)txt+=' Tu peux relancer le volume progressivement. Pas de rattrapage brutal \u2014 +10\u00a0% max par semaine.';
      else txt+=' Continue sur cette lanc\u00e9e.'+(jrace<=60?' Avec J-'+jrace+' avant '+rname+', c\u2019est exactement le bon rythme.':'');
      if(isHot)txt+=' Avec la canicule, l\u2019ACWR sous-estime la fatigue r\u00e9elle \u2014 ajoute un cr\u00e9dit de +0,1 \u00e0 ta lecture.';
      return h+txt+'</p></div>';
    }
    if(key==='z2'){
      var z2d=D.Z2&&D.Z2[4]?D.Z2[4].v.filter(function(x){return x;}):[];
      if(!z2d.length)return '';
      var zlast=z2d[z2d.length-1],zfirst=z2d[0],zdiff=zfirst-zlast;
      var zStr=typeof _ckSmin==='function'?_ckSmin(zlast):Math.floor(zlast/60)+':'+String(Math.round(zlast%60)).padStart(2,'0');
      var ztxt='Ton allure EF actuelle est <strong>'+zStr+'/km</strong>.';
      if(zdiff>5)ztxt+=' Tu as gagn\u00e9 '+Math.round(zdiff)+'\u00a0sec/km en Z2 sur la p\u00e9riode \u2014 vraie progression a\u00e9robie.';
      else if(zdiff<-5)ztxt+=' Allure EF l\u00e9g\u00e8rement moins bonne. Souvent li\u00e9 \u00e0 la chaleur (d\u00e9rive cardiaque) ou \u00e0 la fatigue accumul\u00e9e \u2014 pas forc\u00e9ment une r\u00e9gression r\u00e9elle.';
      else ztxt+=' Allure stable \u2014 coh\u00e9rent en phase de volume \u00e9lev\u00e9.';
      ztxt+=' Objectif saison\u00a0: ~5:40/km en Z2 d\u2019ici octobre.';
      if(isHot)ztxt+=' Par temps chaud, cours \u00e0 allure \u00ab\u00a0confort\u00a0\u00bb plut\u00f4t qu\u2019\u00e0 une allure cible.';
      return h+ztxt+'</p></div>';
    }
    if(key==='vol'){
      var vol=D.VOL&&D.VOL[4]?D.VOL[4]:null;if(!vol)return '';
      var vr=vol.a[vol.a.length-1],vp=vol.p?vol.p[vol.p.length-1]:null;
      var vtxt='Cette semaine\u00a0: <strong>'+vr+'\u00a0km</strong>'+(vp?' sur <strong>'+vp+'\u00a0km</strong> planifi\u00e9s':'')+'. ';
      if(jrace<=14)vtxt+='Normal d\u2019\u00eatre en dessous \u2014 c\u2019est l\u2019aff\u00fbtage, le volume r\u00e9duit sert \u00e0 arriver frais.';
      else if(vp&&vr<vp*0.7)vtxt+='Semaine incompl\u00e8te. Si c\u2019est voulu, pas de probl\u00e8me. Sinon, essaie de caler la s\u00e9ance manqu\u00e9e en d\u00e9but de semaine prochaine.';
      else if(vp&&vr>=vp)vtxt+='Volume dans les clous \u2014 belle semaine.';
      else vtxt+='En cours de semaine, continue comme pr\u00e9vu.';
      return h+vtxt+'</p></div>';
    }
  }catch(e){return '';}
  return '';
}
function openCkHelp(key){
  const d=_CK_HELP[key];if(!d)return;
  const o=document.getElementById('ck-help-ov');if(!o)return;
  document.getElementById('ck-help-title').textContent=d.t;
  document.getElementById('ck-help-body').innerHTML=d.body+_ckCtxBlock(key);
  o.classList.add('open');o.scrollTop=0;
}
function closeCkHelp(){const o=document.getElementById('ck-help-ov');if(o)o.classList.remove('open');}
function initCkHelp(){
  if(!document.body||typeof document.body.insertAdjacentHTML!=='function')return;
  document.body.insertAdjacentHTML('beforeend',`
<div id="ck-help-ov">
  <div class="ckh-topbar">
    <div class="ckh-title" id="ck-help-title"></div>
    <button class="ckh-close" onclick="closeCkHelp()">✕</button>
  </div>
  <div class="ckh-body" id="ck-help-body"></div>
</div>`);}

function _isPwa(){return(window.matchMedia&&window.matchMedia('(display-mode:standalone)').matches)||window.navigator.standalone===true;}
function _isIos(){return/iPhone|iPod|iPad/i.test(navigator.userAgent)&&!window.MSStream;}
function initInstall(){
  if(!document.body||typeof document.body.insertAdjacentHTML!=='function')return;
  if(_isPwa())return;
  if(localStorage.getItem('install_dismissed')==='1')return;
  if(!_isIos())return;
  document.body.insertAdjacentHTML('beforeend',`
<div id="install-banner"><span class="inst-ico">📲</span><span class="inst-txt">Installe l'app sur l'écran d'accueil</span><button class="inst-cta" onclick="openInstall()">Voir</button><button class="inst-x" onclick="dismissInstall()">✕</button></div>
<div id="install-ov" onclick="if(event.target===this)closeInstall()">
  <div class="inst-sheet">
    <div class="inst-handle"></div>
    <div class="inst-title">📲 Installer l'app</div>
    <div class="inst-sub">3 étapes · 10 secondes</div>
    <div class="inst-steps">
      <div class="inst-step"><span class="inst-n">1</span><div><div class="inst-sl">Tape l'icône <strong>Partage</strong></div><div class="inst-ss">Le carré avec la flèche ↑ en bas de Safari</div></div></div>
      <div class="inst-step"><span class="inst-n">2</span><div><div class="inst-sl">Sélectionne <strong>Ajouter à l'écran d'accueil</strong></div><div class="inst-ss">Fais défiler le menu si nécessaire</div></div></div>
      <div class="inst-step"><span class="inst-n">3</span><div><div class="inst-sl">Tape <strong>Ajouter</strong> en haut à droite</div><div class="inst-ss">L'app apparaît directement sur l'écran</div></div></div>
    </div>
    <button class="inst-done" onclick="closeInstall();dismissInstall()">✓ C'est fait</button>
    <button class="inst-later" onclick="closeInstall()">Plus tard</button>
  </div>
</div>`);
}
function openInstall(){const o=document.getElementById('install-ov');if(o)o.classList.add('open');}
function closeInstall(){const o=document.getElementById('install-ov');if(o)o.classList.remove('open');}
function dismissInstall(){localStorage.setItem('install_dismissed','1');const b=document.getElementById('install-banner');if(b)b.remove();}

/* ===== Historique des versions ===== */
function initVersionPanel(){
  if(!document.body||typeof document.body.insertAdjacentHTML!=='function')return;
  const cl=(typeof CHANGELOG!=='undefined'?CHANGELOG:[])||[];
  const latest=cl[0]||{build:'—',date:'—'};
  document.body.insertAdjacentHTML('beforeend',`
<div id="ver-ov" onclick="if(event.target===this)closeVersionPanel()">
  <div class="ver-sheet">
    <div class="ver-handle"></div>
    <div class="ver-title">🕐 Historique des versions</div>
    <div class="ver-sub">Tap un build pour le détail · Rollback → me demander le SHA</div>
    <div class="ver-list">
    ${cl.map((b,i)=>`<div class="ver-item ${i===0?'ver-latest':''}">
      <div class="ver-hd" onclick="this.nextElementSibling.classList.toggle('ver-open')">
        <div><div class="ver-build">Build ${b.build} <span class="ver-tag">${b.tag}</span></div>
        <div class="ver-date">${b.date} · SHA ${b.sha}</div></div>
        <span class="ver-arr">›</span>
      </div>
      <div class="ver-feats">
        ${b.items.map(f=>`<div class="ver-feat">· ${f}</div>`).join('')}
        <div class="ver-sha-row">SHA : <code>${b.sha}</code></div>
      </div>
    </div>`).join('')}
    </div>
    <button class="ver-close" onclick="closeVersionPanel()">Fermer</button>
  </div>
</div>`);
}
function openFormeHelp(){
  const o=document.getElementById('forme-help-ov');
  if(o){o.classList.add('open');o.scrollTop=0;}
}
function closeFormeHelp(){const o=document.getElementById('forme-help-ov');if(o)o.classList.remove('open');}
function initFormeHelp(){
  if(!document.body||typeof document.body.insertAdjacentHTML!=='function')return;
  document.body.insertAdjacentHTML('beforeend',`
<div id="forme-help-ov">
  <div class="fh-topbar">
    <div class="fh-topbar-title">Score de forme · Comment ça marche ?</div>
    <button class="fh-close-top" onclick="closeFormeHelp()">✕</button>
  </div>
  <div class="fh-body">
    <div class="fh-intro">Un seul chiffre chaque matin pour savoir où tu en es. Il synthétise automatiquement 4 indicateurs de ton entraînement récent.</div>
    <div class="fh-sec">L'échelle de 0 à 100</div>
    <div class="fh-scale">
      <div class="fh-s-item"><div class="fh-dot" style="background:#0d9488"></div><div><strong>82–100 · Excellent</strong> — Tu es en forme, tu peux attaquer une séance qualité sans hésiter.</div></div>
      <div class="fh-s-item"><div class="fh-dot" style="background:#16a34a"></div><div><strong>68–81 · Bon</strong> — Paramètres dans la norme. Suis le plan tel quel.</div></div>
      <div class="fh-s-item"><div class="fh-dot" style="background:#f59e0b"></div><div><strong>52–67 · Vigilance</strong> — Quelque chose mérite attention. Tape sur la barre pour identifier le point faible.</div></div>
      <div class="fh-s-item"><div class="fh-dot" style="background:#ef4444"></div><div><strong>0–51 · Alerte</strong> — Privilégie le repos ou un EF très léger. Ne force pas une qualité.</div></div>
    </div>
    <div class="fh-sec">Les 4 composantes</div>
    <div class="fh-comps">
      <div class="fh-comp"><div class="fh-c-head">ACWR <span>30 %</span></div><div class="fh-c-txt">Ratio charge aiguë / charge chronique sur 4 semaines glissantes. Zone idéale : 0,8–1,3. En dessous = sous-entraîné. Au-dessus = surcharge, risque blessure.</div></div>
      <div class="fh-comp"><div class="fh-c-head">Adhérence <span>25 %</span></div><div class="fh-c-txt">Pourcentage de séances réalisées vs planifiées sur les 2 dernières semaines, hors optionnelles. Reflète ta régularité.</div></div>
      <div class="fh-comp"><div class="fh-c-head">Z2 pace <span>25 %</span></div><div class="fh-c-txt">Tendance de ton allure sur les footings faciles (EF). Si tu cours de plus en plus vite à même FC, ta forme aérobie progresse — et le score monte.</div></div>
      <div class="fh-comp"><div class="fh-c-head">Fraîcheur <span>20 %</span></div><div class="fh-c-txt">Jours de repos depuis ta dernière séance. Optimal : 1–2 jours. 0 = couru aujourd'hui (neutre). 4+ jours sans courir = tu perds du fil.</div></div>
    </div>
    <div class="fh-note">💡 Tape directement sur la barre "Forme du jour" pour voir le détail de chaque composante avec tes valeurs du jour en temps réel.</div>
    <div class="fh-note" style="background:#f0fdf4;color:#15803d">🎯 L'objectif à long terme : maintenir le score au-dessus de 75 sur les semaines de charge, et au-dessus de 80 pendant les allègements. Le trend (↑ ↓ →) te dit si tu vas dans le bon sens.</div>
  </div>
</div>`);}

function openVersionPanel(){const o=document.getElementById('ver-ov');if(o)o.classList.add('open');}
function closeVersionPanel(){const o=document.getElementById('ver-ov');if(o)o.classList.remove('open');}

/* ===================================================================
   COACH — Sprint B Option B (sans clé API, données app)
   =================================================================== */
function _cFmt(t){
  return t
    .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>')
    .replace(/`(.+?)`/g,'<code style="background:#0f172a;padding:1px 4px;border-radius:3px;font-size:.85em;color:#0d9488">$1</code>')
    .replace(/^[-\u2022] (.+)$/gm,'<li>$1</li>')
    .replace(/(<li>[\s\S]+?<\/li>\n?)+/g,function(m){return '<ul style="margin:6px 0 6px 14px">'+m+'</ul>';})
    .replace(/\n\n/g,'<br><br>').replace(/\n/g,'<br>');
}
function _cReply(txt){
  const t=txt.toLowerCase();
  const forme=computeFormeScore();
  const today=new Date();today.setHours(0,0,0,0);
  const curWk=isoWeek(today);
  const sc=SEMAINES.find(s=>s.num===curWk)||{theme:'',km:0};
  const ps=(typeof prochaineSeance==='function')?prochaineSeance():null;
  if(/fatigu|crev[e\u00e9]|mal aux|douleur|bless/.test(t)){
    const warn=forme.score<65?`Ton score de forme est bas (${forme.score}/100) \u2014 le repos est justifi\u00e9.`:`Ton score de forme est \u00e0 ${forme.score}/100, les donn\u00e9es sont bonnes. La fatigue ressentie est probablement normale apr\u00e8s ${sc.theme||'cette p\u00e9riode'}.`;
    return `${warn}\n\nEn cas de doute : un EF l\u00e9ger 30min FC<144 vaut mieux qu'un repos complet ou une s\u00e9ance forc\u00e9e. Et garde un \u0153il sur ton dos \u2014 ta vigilance connue.`;
  }
  if(/demain|prochain|suivant|apr\u00e8s-demain/.test(t)){
    if(!ps)return 'Toutes les s\u00e9ances de la semaine sont log g\u00e9es ou pass\u00e9es \u{1F389} La suite se cale lundi.';
    const diff=Math.round((ps.d-today)/86400000);
    const quand=diff<=0?"aujourd'hui":diff===1?'demain':`dans ${diff} jours`;
    let msg=`**${ps.se.titre||ps.se.type}** \u2014 ${quand}\n\n${ps.se.sous||ps.se.objectif||''}`;
    return msg;
  }
  if(/forme|score|comment (je|tu|\u00e7a va)|bilan/.test(t)){
    const c=forme.components||[];
    let det='';c.forEach(x=>{det+=`\n\u2022 ${x.label} : ${Math.round(x.score)}/100 \u2014 ${x.detail}`;});
    return `**Forme du jour : ${forme.score}/100 ${forme.trend||''}**\n${det}\n\n\u2192 ${forme.signal||''}`;
  }
  if(/nice|saintex|sainte|course|objectif|marathon|j-\d/.test(t)){
    const R=[{n:'Marathon de Nice',d:'2026-11-08',i:'42,195 km \u00b7 Objectif A \u00b7 3h45 (5:20/km)'},
             {n:'Saint\u00e9Express',d:'2026-11-28',i:'45 km nuit \u00b7 Objectif B \u00b7 finisher'}];
    return R.map(x=>{const j=Math.ceil((new Date(x.d)-today)/86400000);return `**${x.n}** \u2014 J-${j}\n${x.i}`;}).join('\n\n');
  }
  if(/nutri|gel|[e\u00e9]lectro|hydrat|boire|manger|caf[e\u00e9]/.test(t))
    return `**Protocole carburant & \u00e9lectrolytes (r\u00e9f\u00e9rence canicule valid\u00e9e)**\n\n\u2022 Boisson d'effort \u00e9lectrolytes z\u00e9ro calorie d\u00e8s le d\u00e9part\n\u2022 ~850 ml/h en continu par forte chaleur (1,5L sur ~1h45)\n\u2022 +1 gel par heure d'effort\n\u2022 Sortie > 2h : ajouter des glucides dans la boisson (les \u00e9lectrolytes seuls ne suffisent plus)\n\n\u26a0\ufe0f La d\u00e9rive de FC en fin de sortie par chaleur = signal hydro-\u00e9lectrolytique, pas une baisse de forme.`;
  if(/m[e\u00e9]t[e\u00e9]o|chaud|canicule|chaleur/.test(t)){
    try{const mc=JSON.parse(localStorage.getItem('meteo_cache')||'null');
      if(mc&&mc.temp){const T=Math.round(mc.temp);
        if(T>28)return `\u{1F534} **Canicule : ${T}\u00b0C**\n\n\u2022 D\u00e9part avant 8h30\n\u2022 Allure : +20-30s/km\n\u2022 \u00c9lectrolytes d\u00e8s le d\u00e9part, ~850ml/h\n\u2022 FC d\u00e9rive attendue en fin de sortie \u2014 normal`;
        if(T>22)return `\u{1F7E1} **${T}\u00b0C** \u2014 pars t\u00f4t, allure +10-20s/km, hydratation continue.`;
        return `\u{1F7E2} **${T}\u00b0C** \u2014 conditions favorables, plan nominal.`;
      }}catch(e){}
    return `Par d\u00e9faut en ce moment : canicule persistante \u2014 d\u00e9part avant 8h30, \u00e9lectrolytes d\u00e8s le d\u00e9part, ~850ml/h.`;
  }
  if(/chaussure|shoe|clifton|novablast|cascadia|magic|pulse/.test(t)){
    const g=(typeof GEAR!=='undefined')?GEAR:[];
    if(!g.length)return 'Donn\u00e9es chaussures non disponibles.';
    return `**Parc chaussures** \u{1F45F}\n\n`+g.map(x=>`${x.km>1000?'\u26a0\ufe0f':x.km>700?'\u{1F7E1}':'\u{1F7E2}'} **${x.marque} ${x.modele}** \u2014 ${x.km} km`).join('\n')+`\n\n\u2022 Clifton 10 : fin de vie, d\u00e9crassages courts seulement\n\u2022 Magic Speed : qualit\u00e9/AM uniquement\n\u2022 Cascadia : trail\n\u2022 Novablast V : r\u00e9serv\u00e9e Nice`;
  }
  if(/allure|vitesse|pace/.test(t))
    return `**Allures cibles 2026**\n\n\u2022 EF Z2 : 5:50\u20136:05/km (FC<144)\n\u2022 AM marathon : **5:20/km** \u2192 3h45 Nice\n\u2022 Seuil : 4:50\u20135:00/km\n\nZ2 en progression \u2014 objectif automne : gagner 10-15s/km \u00e0 m\u00eame FC.`;
  if(/repos|r[e\u00e9]cup|day off/.test(t))
    return `**R\u00e9cup\u00e9ration**\n\n\u2022 48h apr\u00e8s effort intense : EF l\u00e9ger FC<135 OK\n\u2022 72h : retour entra\u00eenement normal\n\u2022 Douleur (dos notamment) : repos complet jusqu'\u00e0 disparition\n\nLa r\u00e9cup\u00e9ration est de l'entra\u00eenement. Tu te construis au repos, pas \u00e0 l'effort.`;
  const tip=forme.score>=82?'en pleine forme':forme.score>=68?'en bonne forme':'\u00e0 surveiller';
  return `Tu es ${tip} (${forme.score}/100). Je peux t'aider sur : **ma forme** \u00b7 **demain** \u00b7 **fatigue** \u00b7 **m\u00e9t\u00e9o** \u00b7 **courses** \u00b7 **nutrition** \u00b7 **chaussures** \u00b7 **allures** \u00b7 **r\u00e9cup\u00e9ration**.`;
}
function _cAddMsg(role,html){
  const el=document.getElementById('coach-msgs');if(!el)return;
  const t=new Date().toLocaleTimeString('fr',{hour:'2-digit',minute:'2-digit'});
  const d=document.createElement('div');
  d.className='coach-msg '+role;
  d.innerHTML='<div class="cmsg-bbl">'+html+'</div><div class="cmsg-t">'+t+'</div>';
  el.appendChild(d);el.scrollTop=9999;
}
function _cTypingShow(){
  const el=document.getElementById('coach-msgs');if(!el)return;
  const d=document.createElement('div');d.className='coach-msg coach';d.id='c-dots-msg';
  d.innerHTML='<div class="cmsg-bbl"><div class="c-dots"><span></span><span></span><span></span></div></div>';
  el.appendChild(d);el.scrollTop=9999;
}
function _cTypingHide(){const x=document.getElementById('c-dots-msg');if(x)x.remove();}
function _cBuildSystemPrompt(){
  var now=new Date();now.setHours(0,0,0,0);
  var rdays=(typeof RACES!=='undefined'&&RACES.length)?RACES.map(function(r){return{nom:r.nom,j:Math.ceil((new Date(r.date+'T12:00:00')-now)/86400000)};}).filter(function(x){return x.j>=0;}).sort(function(a,b){return a.j-b.j;}):[],raceLine=rdays.map(function(r){return r.nom+' J-'+r.j;}).join(' \u00b7 ');
  var acwr=(typeof _dynamicACWR==='function')?_dynamicACWR().toFixed(2):'?';
  var forme=(typeof computeFormeScore==='function')?computeFormeScore():{score:0,signal:'',trend:''};
  var pmc=(typeof _pmcCompute==='function')?_pmcCompute(8):null;
  var ctl=pmc&&pmc.length?pmc[pmc.length-1].ctl.toFixed(0):'?';
  var atl=pmc&&pmc.length?pmc[pmc.length-1].atl.toFixed(0):'?';
  var tsb=pmc&&pmc.length?((pmc[pmc.length-1].tsb>=0?'+':'')+pmc[pmc.length-1].tsb.toFixed(0)):'?';
  var sbw=typeof SEANCES_BY_WEEK!=='undefined'?SEANCES_BY_WEEK:{};
  var curW=(typeof _curWeek==='function'?_curWeek():null)||26;
  var seancesSem=sbw[curW]||[];
  var loggedSem=seancesSem.filter(function(s){return s.realise&&(s.realise.statut==='fait'||s.realise.statut==='partiel');});
  var loggedAll=Object.values(sbw).flat().filter(function(s){return s.realise&&s.realise.km;}).slice(-8).map(function(s){return s.type.substring(0,20)+' '+s.realise.km+'km '+s.realise.allure+' FC'+s.realise.fc_moy+'/'+s.realise.fc_max+' RPE'+s.realise.rpe_ressenti;});
  var gearLines=(typeof GEAR!=='undefined'?GEAR:[]).map(function(g){return (g.km>900?'\u26a0\ufe0f':g.km>600?'\u{1F7E1}':'\u{1F7E2}')+' '+g.marque+' '+g.modele+' \u2014 '+g.km+'km';}).join('\n');
  var vigLines=(typeof VIGILANCE!=='undefined'?VIGILANCE:[]).map(function(v){return '- '+v.t+(v.d?': '+v.d:'');}).join('\n');
  var canEl=document.getElementById('canicule-banner');
  var isHot=canEl&&canEl.style.display!=='none'&&canEl.textContent.trim()?'OUI \u2014 '+(canEl.textContent.trim()):'non';
  var pr=typeof PROFIL!=='undefined'?PROFIL:{};
  return 'Tu es le coach running personnel de '+pr.prenom+' (Lyon, '+(pr.poids||84)+'kg, FCmax '+(pr.fcmax||192)+').\nTu connais toutes ses donn\u00e9es en temps r\u00e9el. R\u00e9ponds en coach direct et pr\u00e9cis \u2014 pas de g\u00e9n\u00e9ralit\u00e9s, cite toujours ses vrais chiffres. Fran\u00e7ais uniquement. R\u00e9ponses courtes sauf si question complexe. Markdown simple : **gras** et tirets pour les listes.\n\n## \u00c9tat actuel\n- Date : '+now.toLocaleDateString('fr')+' \u00b7 S'+curW+'\n- Forme : '+forme.score+'/100 ('+forme.signal+')\n- CTL fitness : '+ctl+' \u00b7 ATL fatigue : '+atl+' \u00b7 TSB forme : '+tsb+'\n- ACWR : '+acwr+'\n- Canicule : '+isHot+'\n- Courses : '+raceLine+'\n\n## S\u00e9ances semaine courante (S'+curW+')\n- Faites : '+loggedSem.length+'/'+seancesSem.length+'\n'+seancesSem.map(function(s){var r=s.realise||{};return '- '+(r.statut==='fait'?'[FAIT]':r.statut==='partiel'?'[PARTIEL]':'[A FAIRE]')+' '+s.type.substring(0,30)+(r.km?' | '+r.km+'km '+r.allure+' FC'+r.fc_moy+'/'+r.fc_max+' RPE'+r.rpe_ressenti:'');}).join('\n')+'\n\n## Derni\u00e8res s\u00e9ances logg\u00e9es\n'+loggedAll.join('\n')+'\n\n## Objectifs\n- Marathon Nice 8 nov 2026 : cible '+(pr.cible_marathon||'3h45')+' (allure 5:20/km) \u00b7 projet\u00e9 '+(pr.marathon_projete||'~3h38-42')+'\n- Trail D\u00e9raille 5 juil · Semi cible '+(pr.cible_semi||'~1h44')+'\n\n## Parc chaussures\n'+gearLines+'\n\n## Zones FC\n- Z2 EF : 134-154 bpm \u00b7 5:50-6:25/km\n- Z3 marathon : 154-167 bpm \u00b7 5:05-5:30/km\n- Z4 seuil : 167-177 bpm\n\n## Vigilances\n'+vigLines+'\n\n## Plan synth\u00e8se\n- S24-27 reprise/g\u00e9n\u00e9ral (28\u219252km)\n- S28-35 bloc seuil (70\u219282km) + sorties longues AM progressives\n- S36-38 USA maintien (~40km)\n- S39-43 pic marathon (64\u219288km)\n- S44-45 aff\u00fbatage Nice \u00b7 S46-48 transition+SaintExpress\n\nPoints forts : base a\u00e9robie solide, structure ondulante correcte, progression AM exemplaire.\nPoints faibles : 0 s\u00e9ance c\u00f4tes sur 30sem, mobilit\u00e9 insuffisante (3/30sem), FC AM un peu haute (165 vs cible 154-163), 6/131 s\u00e9ances logg\u00e9es seulement.';
}
var _coachHistory=[];
function openCoach(){
  if(navigator.vibrate)try{navigator.vibrate(8)}catch(e){}
  const ov=document.getElementById('coach-ov');if(!ov)return;
  ov.classList.add('open');
  if(!document.getElementById('coach-msgs').children.length){
    _coachHistory=[];
    setTimeout(function(){
      var forme=(typeof computeFormeScore==='function')?computeFormeScore():{score:0,signal:'',trend:''};
      var now=new Date();now.setHours(0,0,0,0);
      var rdays=(typeof RACES!=='undefined'&&RACES.length)?RACES.map(function(r){return{nom:r.nom,j:Math.ceil((new Date(r.date+'T12:00:00')-now)/86400000)};}).filter(function(x){return x.j>=0;}).sort(function(a,b){return a.j-b.j;}):[];
      var acwr=(typeof _dynamicACWR==='function')?_dynamicACWR().toFixed(2):'—';
      var pmc=(typeof _pmcCompute==='function')?_pmcCompute(8):null;
      var tsb=pmc&&pmc.length?((pmc[pmc.length-1].tsb>=0?'+':'')+pmc[pmc.length-1].tsb.toFixed(0)):'—';
      var emoji=forme.score>=82?'\u{1F7E2}':forme.score>=68?'\u{1F7E1}':'\u{1F534}';
      var pr=typeof PROFIL!=='undefined'?PROFIL:{prenom:'toi'};
      var next=rdays.length?rdays[0]:null;
      var intro='Bonjour '+pr.prenom+' \u{1F44B}<br><br>'+emoji+' <strong>Forme '+forme.score+'/100</strong> \u00b7 TSB '+tsb+' \u00b7 ACWR '+acwr+(next?'<br><br>\u{1F3C1} <strong>J-'+next.j+' avant '+next.nom+'.</strong>':'')+'<br><br>Je connais ton plan, tes s\u00e9ances logg\u00e9es, tes chaussures et tes courses. Pose-moi n\u2019importe quelle question.';
      _cAddMsg('coach',intro);
      _coachHistory.push({role:'assistant',content:intro.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim()});
    },300);
  }
}
function closeCoach(){document.getElementById('coach-ov')?.classList.remove('open');}
async function coachSend(){
  const inp=document.getElementById('coach-inp');if(!inp)return;
  const txt=inp.value.trim();if(!txt)return;
  inp.value='';inp.disabled=true;
  const btn=document.querySelector('.c-send');if(btn)btn.disabled=true;
  _cAddMsg('user',txt);
  _coachHistory.push({role:'user',content:txt});
  _cTypingShow();
  try{
    const res=await fetch('https://api.anthropic.com/v1/messages',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        model:'claude-sonnet-4-6',
        max_tokens:600,
        system:_cBuildSystemPrompt(),
        messages:_coachHistory.slice(-12)
      })
    });
    const d=await res.json();
    if(!res.ok||!d.content||!d.content[0]||!d.content[0].text)throw new Error('api');
    _cTypingHide();
    const reply=d.content[0].text;
    _cAddMsg('coach',_cFmt(reply));
    _coachHistory.push({role:'assistant',content:reply});
  }catch(e){
    _cTypingHide();
    const local=_cReply(txt);
    _cAddMsg('coach',_cFmt(local));
    _coachHistory.push({role:'assistant',content:local});
  }
  inp.disabled=false;if(btn)btn.disabled=false;inp.focus();
}
function coachChip(txt){const inp=document.getElementById('coach-inp');if(inp){inp.value=txt;coachSend();}}
function initCoach(){
  if(!document.body||typeof document.body.insertAdjacentHTML!=='function')return;
  document.body.insertAdjacentHTML('beforeend',`<div id="coach-ov">
  <div class="coach-topbar">
    <div class="c-avatar">🏃</div>
    <div class="c-head"><div class="c-title">Coach IA</div><div class="c-sub"><div class="c-live"></div>Analyse depuis tes donn\u00e9es</div></div>
    <button class="c-close" onclick="closeCoach()">\u2715</button>
  </div>
  <div id="coach-msgs" class="coach-msgs"></div>
  <div class="coach-chips">
    <div class="c-chip" onclick="coachChip('Ma forme aujourd\'hui')">Ma forme</div>
    <div class="c-chip" onclick="coachChip('Que faire demain ?')">Demain</div>
    <div class="c-chip" onclick="coachChip('Je me sens fatigué')">Fatigue ?</div>
    <div class="c-chip" onclick="coachChip('Mon allure marathon est-elle bonne ?')">Allure AM</div>
    <div class="c-chip" onclick="coachChip('Mes chaussures')">Chaussures</div>
    <div class="c-chip" onclick="coachChip('Nutrition et fueling pour la Déraille')">Nutrition</div>
    <div class="c-chip" onclick="coachChip('SaintExpress après Nice, c\'est réaliste ?')">SaintExpress</div>
    <div class="c-chip" onclick="coachChip('Risque blessure dos cette semaine ?')">Dos</div>
  </div>
  <div class="coach-inp-row">
    <input id="coach-inp" type="text" placeholder="Pose ta question\u2026" onkeydown="if(event.key===\'Enter\'&&!this.disabled)coachSend()">
    <button class="c-send" onclick="coachSend()">\u2191</button>
  </div>
</div>`);
}

function checkAutoSync(){
  const today=new Date();today.setHours(0,0,0,0);
  const yest=new Date(today);yest.setDate(today.getDate()-1);
  const curWk=isoWeek(today);
  for(const wk of[curWk,curWk-1]){
    for(const s of(SEANCES_BY_WEEK[wk]||[])){
      if(!s.date||s.opt)continue;
      const d=new Date(s.date+'T00:00:00');
      if((+d===+today||+d===+yest)&&(!s.realise||s.realise.statut!=='fait')){
        const k='as_'+s.id;if(localStorage.getItem(k))continue;
        const hero=document.getElementById('hero-plan');if(!hero)return;
        const bar=document.createElement('div');bar.className='as-bar';
        const when=+d===+today?"aujourd'hui":'hier';
        bar.innerHTML=`<div class="as-ico">📍</div><div class="as-txt"><strong>Séance ${when} non loggée</strong> — S${wk} ${s.titre}</div><button class="as-btn" onclick="ouvrirQuickLog(${wk},${s.id})">Logger</button><button class="as-x" onclick="localStorage.setItem('${k}','1');this.parentElement.remove()">✕</button>`;
        hero.insertAdjacentElement('afterend',bar);return;
      }
    }
  }
}

/* ===================================================================
   PALMARÈS — Historique des courses officielles
   =================================================================== */
function renderPalmares(){
  const el=document.getElementById('palmares-contenu');if(!el)return;
  const P=(typeof PALMARES!=='undefined'?PALMARES:DATA.PALMARES)||[];
  const types={'trail':'🏔️ Trail','trail_nuit':'🌙 Trail nuit','route':'🛣️ Route','semi':'🏃 Semi-marathon','marathon':'🏅 Marathon'};
  const totalKm=P.reduce((a,p)=>a+p.distance,0);
  const totalDplus=P.reduce((a,p)=>a+(p.dplus||0),0);
  const _tdy=new Date();_tdy.setHours(0,0,0,0);
  const _moisC=['janv.','f\u00e9vr.','mars','avr.','mai','juin','juil.','ao\u00fbt','sept.','oct.','nov.','d\u00e9c.'];
  const _up=((typeof RACES!=='undefined'?RACES:(typeof DATA!=='undefined'&&DATA.RACES))||[]).map(r=>{const d=new Date(r.date+'T12:00:00');return{nom:r.nom,dossier:r.dossier,d:d,dn:Math.ceil((d-_tdy)/86400000)};}).filter(r=>r.dn>=0).sort((a,b)=>a.dn-b.dn);
  const _aVenir=_up.length?'<div class="crs-lab">\u00c0 venir</div>'+_up.map(r=>{const ds=r.d.getDate()+' '+_moisC[r.d.getMonth()]+' '+r.d.getFullYear();return `<button class="crs-up"${r.dossier?` onclick="ouvrirDossier('${r.dossier}')"`:''}><span class="crs-jx">J-${r.dn}</span><span class="crs-mid"><span class="crs-nom">${r.nom}</span><span class="crs-date">${ds}</span></span>${r.dossier?'<span class="crs-go">Dossier \u203a</span>':''}</button>`;}).join(''):''; 
  el.innerHTML=`<div style="padding:12px 12px 40px">
<div style="font-size:22px;font-weight:700;color:var(--texte);letter-spacing:-.02em;margin-bottom:2px">Courses</div>
<div style="font-size:11px;color:var(--texte-deux);margin-bottom:14px">À venir &amp; passées · objectifs et résultats</div>${_aVenir}<div class="crs-lab">Passées</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:16px">
  <div style="background:var(--bg-card,#fff);border:.5px solid var(--bord-card,#e2e8f0);border-radius:12px;padding:10px;text-align:center"><div style="font-size:20px;font-weight:700;color:var(--texte)">${P.length}</div><div style="font-size:9px;text-transform:uppercase;letter-spacing:.05em;color:var(--texte-deux);margin-top:3px">Courses</div></div>
  <div style="background:var(--bg-card,#fff);border:.5px solid var(--bord-card,#e2e8f0);border-radius:12px;padding:10px;text-align:center"><div style="font-size:20px;font-weight:700;color:var(--texte)">${totalKm.toFixed(0)}</div><div style="font-size:9px;text-transform:uppercase;letter-spacing:.05em;color:var(--texte-deux);margin-top:3px">km courus</div></div>
  <div style="background:var(--bg-card,#fff);border:.5px solid var(--bord-card,#e2e8f0);border-radius:12px;padding:10px;text-align:center"><div style="font-size:20px;font-weight:700;color:var(--texte)">${(totalDplus/1000).toFixed(1)}k</div><div style="font-size:9px;text-transform:uppercase;letter-spacing:.05em;color:var(--texte-deux);margin-top:3px">D+ cumulé</div></div>
</div>
${P.slice().sort((a,b)=>b.date.localeCompare(a.date)).map((p,i)=>{
  const typeLabel=types[p.type]||p.type;
  const d=new Date(p.date+'T12:00:00');
  const mois=['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.'];
  const dateStr=d.getDate()+' '+mois[d.getMonth()]+' '+d.getFullYear();
  const classGen=p.classement_gen?`<span style="font-size:11px;font-weight:600;padding:2px 7px;border-radius:99px;background:#f0fdfa;color:#0f766e">#${p.classement_gen}${p.total_finishers?' / '+p.total_finishers:''} général</span>`:'';
  const classCat=p.classement_cat?`<span style="font-size:11px;font-weight:600;padding:2px 7px;border-radius:99px;background:#f0fdf4;color:#15803d">#${p.classement_cat} cat.</span>`:'';
  return`<div style="background:var(--bg-card,#fff);border:.5px solid var(--bord-card,#e2e8f0);border-radius:14px;margin-bottom:10px;overflow:hidden">
    <div style="display:flex;align-items:stretch">
      <div style="width:5px;background:${p.accent};flex:0 0 5px"></div>
      <div style="padding:12px 13px;flex:1;min-width:0">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
          <div>
            <div style="font-size:11px;color:var(--texte-deux);margin-bottom:2px">${typeLabel} · ${dateStr}</div>
            <div style="font-size:15px;font-weight:700;color:var(--texte);line-height:1.2">${p.nom}</div>
            <div style="font-size:11px;color:var(--texte-deux);margin-top:1px">${p.lieu}</div>
          </div>
          <div style="text-align:right;flex:0 0 auto;margin-left:8px">
            <div style="font-size:20px;font-weight:700;color:var(--texte)">${p.temps||'—'}</div>
            <div style="font-size:10px;color:var(--texte-deux)">${p.allure?p.allure+'/km':''}</div>
          </div>
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:8px">
          <span style="font-size:11px;font-weight:600;padding:2px 7px;border-radius:99px;background:var(--gris-fond,#f1f5f9);color:var(--texte-deux)">${p.distance} km</span>
          <span style="font-size:11px;font-weight:600;padding:2px 7px;border-radius:99px;background:var(--gris-fond,#f1f5f9);color:var(--texte-deux)">D+ ${p.dplus} m</span>
          ${p.fc_moy?`<span style="font-size:11px;font-weight:600;padding:2px 7px;border-radius:99px;background:#fee2e2;color:#b91c1c">❤️ ${p.fc_moy}/${p.fc_max}</span>`:''}
          ${p.meteo?`<span style="font-size:11px;padding:2px 7px;border-radius:99px;background:var(--gris-fond,#f1f5f9);color:var(--texte-deux)">🌡️ ${p.meteo}</span>`:''}
          ${classGen}${classCat}
        </div>
        ${p.chaussures?`<div style="font-size:11px;color:var(--texte-deux);margin-bottom:6px">👟 ${p.chaussures}</div>`:''}
        <div style="font-size:12px;color:var(--texte-deux);line-height:1.55;background:var(--gris-fond,#f8fafc);border-radius:8px;padding:9px 10px">${p.bilan}</div>
      </div>
    </div>
  </div>`;
}).join('')}
<div style="font-size:11px;color:var(--texte-deux);text-align:center;margin-top:8px;font-style:italic">Classements à compléter après chaque course · partage les résultats officiels</div>
</div>`;
}

/* ===================================================================
   COCKPIT — Dashboard analytique complet
   =================================================================== */
const _CK={
  VOL:{
  2:{w:["S27","S28"],p:[null,null],a:[53.4,11.0]},
  4:{w:["S25","S26","S27","S28"],p:[null,null,null,null],a:[56.6,21.9,53.4,11.0]},
  8:{w:["S21","S22","S23","S24","S25","S26","S27","S28"],p:[null,null,null,null,null,null,null,null],a:[70.4,35.2,55.9,36.4,56.6,21.9,53.4,11.0]},
  12:{w:["S17","S18","S19","S20","S21","S22","S23","S24","S25","S26","S27","S28"],p:[null,null,null,null,null,null,null,null,null,null,null,null],a:[56.4,53.1,38.7,8.4,70.4,35.2,55.9,36.4,56.6,21.9,53.4,11.0]}
},
  RE:{
  2:{w:["S27","S28"],v:[889,106]},
  4:{w:["S25","S26","S27","S28"],v:[531,116,889,106]},
  8:{w:["S21","S22","S23","S24","S25","S26","S27","S28"],v:[818,365,901,255,531,116,889,106]},
  12:{w:["S17","S18","S19","S20","S21","S22","S23","S24","S25","S26","S27","S28"],v:[410,542,418,85,818,365,901,255,531,116,889,106]}
},
  ACWR:{
  2:{w:["S27","S28"],v:[1.25,0.67]},
  4:{w:["S25","S26","S27","S28"],v:[0.95,0.56,1.25,0.67]},
  8:{w:["S21","S22","S23","S24","S25","S26","S27","S28"],v:[1.13,0.9,1.3,0.84,0.95,0.56,1.25,0.67]},
  12:{w:["S17","S18","S19","S20","S21","S22","S23","S24","S25","S26","S27","S28"],v:[0.91,0.94,0.84,0.47,1.13,0.9,1.3,0.84,0.95,0.56,1.25,0.67]}
},
  DPLUS:{
  2:{w:["S25","S26"],v:[208,43]},
  4:{w:["S23","S24","S25","S26"],v:[1913,136,208,43]},
  8:{w:["S19","S20","S21","S22","S23","S24","S25","S26"],v:[1429,198,2165,799,1913,136,208,43]},
  12:{w:["S15","S16","S17","S18","S19","S20","S21","S22","S23","S24","S25","S26"],v:[600,740,366,836,1429,198,2165,799,1913,136,208,43]}
},
  Z2:{
  2:{w:["S25","S26"],v:[268,66]},
  4:{w:["S23","S24","S25","S26"],v:[71,122,268,66]},
  8:{w:["S19","S20","S21","S22","S23","S24","S25","S26"],v:[128,0,206,151,71,122,268,66]},
  12:{w:["S15","S16","S17","S18","S19","S20","S21","S22","S23","S24","S25","S26"],v:[248,344,318,61,128,0,206,151,71,122,268,66]}
},
  DC:{
  2:{w:["S25","S26"],v:[30.4,11.3]},
  4:{w:["S23","S24","S25","S26"],v:[0,20.4,30.4,11.3]},
  8:{w:["S19","S20","S21","S22","S23","S24","S25","S26"],v:[10.5,0,0,4.0,0,20.4,30.4,11.3]},
  12:{w:["S15","S16","S17","S18","S19","S20","S21","S22","S23","S24","S25","S26"],v:[12.0,0,10.3,10.7,10.5,0,0,4.0,0,20.4,30.4,11.3]}
},
  PACE:{
  2:{w:["S25","S26"],ef:[346,353],am:[321,null],se:[null,null]},
  4:{w:["S23","S24","S25","S26"],ef:[352,359,346,353],am:[343,322,321,null],se:[590,null,null,null]},
  8:{w:["S19","S20","S21","S22","S23","S24","S25","S26"],ef:[326,null,583,441,352,359,346,353],am:[811,359,409,326,343,322,321,null],se:[null,null,283,null,590,null,null,null]},
  12:{w:["S15","S16","S17","S18","S19","S20","S21","S22","S23","S24","S25","S26"],ef:[381,346,339,340,326,null,583,441,352,359,346,353],am:[331,318,null,364,811,359,409,326,343,322,321,null],se:[null,null,null,null,null,null,283,null,590,null,null,null]}
},
  FCZ:{
  2:[["Z1","#16a34a",10],["Z2","#16a34a",58],["Z3","#f59e0b",22],["Z4+","#ef4444",10]],
  4:[["Z1","#16a34a",10],["Z2","#16a34a",58],["Z3","#f59e0b",22],["Z4+","#ef4444",10]],
  8:[["Z1","#16a34a",10],["Z2","#16a34a",58],["Z3","#f59e0b",22],["Z4+","#ef4444",10]],
  12:[["Z1","#16a34a",10],["Z2","#16a34a",58],["Z3","#f59e0b",22],["Z4+","#ef4444",10]]
},
  CAD:{
  2:{w:["S25","S26"],v:[172,172]},
  4:{w:["S23","S24","S25","S26"],v:[162,172,172,172]},
  8:{w:["S19","S20","S21","S22","S23","S24","S25","S26"],v:[152,168,156,166,162,172,172,172]},
  12:{w:["S15","S16","S17","S18","S19","S20","S21","S22","S23","S24","S25","S26"],v:[167,171,172,171,152,168,156,166,162,172,172,172]}
},
  RUNS:[
    {id:"18967988695",title:"Sortie longue Saône-Rhône",date:"Jeu 18 juin",type:"#f59e0b",km:16.0,al:"5:32",re:156,fcm:151,fcx:171,cad:173,dp:52,cal:1249,hasStreams:true},
    {id:"18955432704",title:"AM marathon 10km",date:"Mar 17 juin",type:"#0d9488",km:10.1,al:"5:21",re:169,fcm:165,fcx:181,cad:169,dp:35,cal:816,hasStreams:true},
    {id:"18939731283",title:"Footing facile",date:"Lun 16 juin",type:"#16a34a",km:10.1,al:"5:56",re:58,fcm:140,fcx:167,cad:173,dp:40,cal:788,hasStreams:false},
    {id:"19018847549",title:"Footing facile + lignes droites",date:"Lun 22 juin",type:"#16a34a",km:11.3,al:"5:53",re:105,fcm:148,fcx:169,cad:172,dp:43,cal:885,hasStreams:true},
    {id:"18810734775",title:"Trail des Gypaètes (Circaète 29km)",date:"Sam 6 juin",type:"#0d9488",km:29.8,al:"9:50",re:696,fcm:152,fcx:178,cad:146,dp:1662,cal:3191,hasStreams:true}
  ],
  STREAMS:{
  "18967988695":{hr:[109,133,139,138,127,153,157,152,145,157,158,143,146,144,148,149,145,146,150,147,144,142,143,139,142,144,147,141,151,153,150,151,146,149,154,155,150,153,152,149,160,153,154,148,150,153,150,153,154,148,152,166,166,162,166,164,162,169,170,169]},
  "18955432704":{hr:[95,140,150,143,147,145,150,156,155,154,158,150,154,153,162,157,163,163,171,168,171,166,166,167,169,169,167,167,168,169,172,167,172,167,166,172,171,169,170,168,174,173,170,171,176,169,171,171,179,176,174,174,170,170,172,172,174,175,178,174]},
  "18810734775":{hr:[111,172,178,177,164,168,173,172,162,172,159,159,159,167,157,160,167,154,167,163,174,175,169,166,165,166,170,154,168,175,163,171,166,172,132,164,160,157,153,108,160,160,148,152,155,127,149,155,150,161,154,154,146,149,141,148,136,151,151,168]},
  "19018847549":{hr:[93,134,140,137,139,137,133,147,146,152,143,151,148,158,155,148,142,148,148,148,149,155,146,146,144,146,148,148,146,150,142,145,146,143,145,142,148,146,147,139,155,147,143,141,156,152,142,158,161,157,162,158,156,160,167,152,145,146,149,155]}
}
};;
let _ckWin=8;
/* PMC — Performance Management Chart (Sprint C) */
function _pmcCompute(win){
  const re=_CK.RE[win];if(!re)return[];
  const aC=1-Math.exp(-7/42),aA=1-Math.exp(-7/7);
  let ctl=re.v[0]/7,atl=re.v[0]/7;
  return re.v.map((v,i)=>{
    const d=v/7;if(i>0){ctl=(1-aC)*ctl+aC*d;atl=(1-aA)*atl+aA*d;}
    return{wk:re.w[i],ctl:+ctl.toFixed(1),atl:+atl.toFixed(1),tsb:+(ctl-atl).toFixed(1)};
  });
}
function _pmcRender(win){
  const data=_pmcCompute(win);if(!data.length)return;
  const svg=document.getElementById('ckPMC');if(!svg)return;
  const W=svg.parentElement?.offsetWidth||320,H=90;
  const pl=6,pr=28,pt=8,pb=18,cw=W-pl-pr,ch=H-pt-pb;
  const allV=[...data.map(d=>d.ctl),...data.map(d=>d.atl)];
  const yMax=Math.max(...allV)*1.15,yMin=0;
  const tMax=Math.max(10,...data.map(d=>Math.abs(d.tsb)))*1.5;
  const n=data.length;
  const xS=i=>pl+i/(n-1)*cw,yS=v=>pt+ch-(v-yMin)/(yMax-yMin)*ch,tS=v=>pt+ch/2-v/tMax*(ch/2);
  const bars=data.map((d,i)=>{const x=xS(i)-cw/(n*2.2),w=Math.max(1,cw/n*0.75);const h=Math.abs(d.tsb)/tMax*(ch/2);const y=d.tsb>=0?tS(d.tsb):pt+ch/2;return`<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" fill="${d.tsb>=0?'rgba(34,197,94,.3)':'rgba(239,68,68,.2)'}" rx="1"/>`;}).join('');
  const zy=(pt+ch/2).toFixed(1);
  const cP='M'+data.map((d,i)=>`${xS(i).toFixed(1)},${yS(d.ctl).toFixed(1)}`).join('L');
  const aP='M'+data.map((d,i)=>`${xS(i).toFixed(1)},${yS(d.atl).toFixed(1)}`).join('L');
  const lbls=data.map((d,i)=>(i===0||i===n-1||i===Math.floor(n/2))?`<text x="${xS(i).toFixed(1)}" y="${H-2}" text-anchor="middle" font-size="9" fill="#64748b">${d.wk}</text>`:'').join('');
  const last=data[n-1];
  const endLbls=`<text x="${(pl+cw+3).toFixed(1)}" y="${yS(last.ctl).toFixed(1)}" font-size="9" fill="#0d9488">${last.ctl.toFixed(0)}</text><text x="${(pl+cw+3).toFixed(1)}" y="${yS(last.atl).toFixed(1)}" font-size="9" fill="#f59e0b">${last.atl.toFixed(0)}</text><text x="${(pl+cw+3).toFixed(1)}" y="${tS(last.tsb).toFixed(1)}" font-size="9" fill="${last.tsb>=0?'#16a34a':'#ef4444'}">${last.tsb>=0?'+':''}${last.tsb.toFixed(0)}</text>`;
  svg.innerHTML=`${bars}<line x1="${pl}" y1="${zy}" x2="${pl+cw}" y2="${zy}" stroke="rgba(100,116,139,.3)" stroke-dasharray="3,3" stroke-width="1"/><path d="${cP}" stroke="#0d9488" stroke-width="2" fill="none" stroke-linejoin="round"/><path d="${aP}" stroke="#f59e0b" stroke-width="1.5" fill="none" stroke-linejoin="round" stroke-dasharray="4,2"/>${lbls}${endLbls}`;
  const wrap=document.getElementById('ckPMCW');if(!wrap)return;
  wrap.onpointermove=ev=>{const r=wrap.getBoundingClientRect(),idx=Math.max(0,Math.min(n-1,Math.round((ev.clientX-r.left-pl)/cw*(n-1))));const d=data[idx];const tt=document.getElementById('ckPMCT');if(tt)tt.textContent=`${d.wk} · Fitness ${d.ctl.toFixed(0)} · Fatigue ${d.atl.toFixed(0)} · Forme ${d.tsb>=0?'+':''}${d.tsb.toFixed(0)}`;};
  wrap.onpointerleave=()=>{const tt=document.getElementById('ckPMCT');if(tt)tt.textContent='glisse pour voir les valeurs';};
  const s=document.getElementById('ckPMC-sub');if(s)s.textContent=`Fitness ${last.ctl.toFixed(0)} · Fatigue ${last.atl.toFixed(0)} · Forme ${last.tsb>=0?'+':''}${last.tsb.toFixed(0)}`;
}
function _ckSmin(s){if(s==null)return'—';const m=Math.floor(s/60),x=Math.round(s%60);return m+':'+(x<10?'0':'')+x;}
function _ckXL(id,weeks){const el=document.getElementById(id);if(!el)return;el.innerHTML='';const n=weeks.length;const show=n<=4?weeks.map((_,i)=>i):[0,Math.floor(n/3),Math.floor(2*n/3),n-1];weeks.forEach((wk,i)=>{const sp=document.createElement('span');sp.textContent=show.includes(i)?wk:'';el.appendChild(sp);});}
function _ckBar(svgId,wrapId,ttId,xlId,data,opt){
  opt=opt||{};const H=opt.h||90,n=data.w.length,gap=300/n,bw=gap*0.6;
  const vals=data.v||data.a;const mx=Math.max(...vals.filter(x=>x!=null),(data.p?Math.max(...data.p):0));
  let s='';data.w.forEach((wk,i)=>{const x=i*gap+gap*0.2;
    if(opt.ref&&data.p){const ph=data.p[i]/mx*(H-12);s+=`<rect x="${x}" y="${H-ph}" width="${bw}" height="${ph}" rx="2" fill="${opt.col||'#0d9488'}" opacity="0.2"/>`;}
    const v=vals[i];if(v==null)return;const h=v/mx*(H-12);
    let c=opt.col||'#0d9488';
    if(opt.thr)c=v>opt.thr[1]?'#ef4444':v>opt.thr[0]?'#f59e0b':'#16a34a';
    if(opt.ref&&data.p)c=v>=data.p[i]?'#0d9488':'#ef4444';
    s+=`<rect class="ck-bar-${svgId}" data-i="${i}" x="${x}" y="${H-h}" width="${bw}" height="${h}" rx="2" fill="${c}"/>`;});
  const svg=document.getElementById(svgId);if(!svg)return;svg.setAttribute('viewBox',`0 0 300 ${H}`);svg.innerHTML=s;
  _ckXL(xlId,data.w);
  const tt=document.getElementById(ttId),wrap=document.getElementById(wrapId);if(!tt||!wrap)return;
  svg.querySelectorAll('.ck-bar-'+svgId).forEach(b=>{b.addEventListener('click',()=>{
    const i=+b.dataset.i;const v=vals[i];
    tt.innerHTML=`<div style="font-size:9px;color:#64748b">${data.w[i]}</div><div style="font-size:13px;font-weight:700">${v==null?'—':v}${opt.unit||''}</div>`+(opt.ref&&data.p?`<div style="font-size:9px;color:#64748b">prévu ${data.p[i]}</div>`:'');
    const r=b.getBoundingClientRect(),wr=wrap.getBoundingClientRect();
    tt.style.left=Math.min(Math.max(r.left-wr.left,0),wr.width-80)+'px';tt.style.top='-4px';tt.classList.add('show');
    clearTimeout(tt._t);tt._t=setTimeout(()=>tt.classList.remove('show'),2200);
  });});
}
function _ckLine(svgId,wrapId,ttId,xlId,weeks,series,fmt,opt){
  opt=opt||{};const H=opt.h||90,n=weeks.length;
  if(!n)return;
  // garde-fou : ne garder que les series ayant un tableau .v exploitable
  series=(series||[]).filter(s=>s&&Array.isArray(s.v));
  if(!series.length)return;
  const allV=series.flatMap(s=>s.v.filter(x=>x!=null));if(!allV.length)return;
  let mn=Math.min(...allV),mx=Math.max(...allV);const pad=(mx-mn)*0.15||5;mn-=pad;mx+=pad;
  const xs=weeks.map((_,i)=>10+i*((300-20)/Math.max(1,n-1)));
  const ym=v=>H-10-((v-mn)/(mx-mn)*(H-20));
  let defs='',paths='',zones='';
  const clipId=`ck-clip-${svgId}`;defs+=`<clipPath id="${clipId}"><rect x="0" y="0" width="300" height="${H}"/></clipPath>`;
  if(opt.zones)opt.zones.forEach(z=>{const y1=ym(Math.min(z[1],mx+pad)),y2=ym(Math.max(z[0],mn-pad));zones+=`<rect x="0" y="${Math.max(0,y1).toFixed(1)}" width="300" height="${Math.max(0,y2-y1).toFixed(1)}" fill="${z[2]}" opacity="0.06" clip-path="url(#${clipId})"/>`;});
  series.forEach((s,si)=>{
    const c=s.v.map((v,i)=>v==null?null:[xs[i],ym(v)]).filter(Boolean);if(!c.length)return;
    const line=c.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' ');
    if(opt.fill!==false){defs+=`<linearGradient id="ckG${svgId}${si}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${s.color}" stop-opacity="0.2"/><stop offset="100%" stop-color="${s.color}" stop-opacity="0"/></linearGradient>`;paths+=`<path d="${line} L${c[c.length-1][0]} ${H} L${c[0][0]} ${H} Z" fill="url(#ckG${svgId}${si})"/>`;}
    paths+=`<path d="${line}" fill="none" stroke="${s.color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`;
  });
  let dots='';series.forEach((s,si)=>{dots+=`<circle id="${svgId}dt${si}" r="4" fill="${s.color}" opacity="0" stroke="#fff" stroke-width="1.5"/>`;});
  const scrub=`<line id="${svgId}sc" x1="0" y1="0" x2="0" y2="${H}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3" opacity="0"/>`;
  const svg=document.getElementById(svgId);if(!svg)return;svg.setAttribute('viewBox',`0 0 300 ${H}`);svg.innerHTML=`<defs>${defs}</defs><g clip-path="url(#${clipId})">${zones}${paths}</g>${scrub}${dots}`;
  _ckXL(xlId,weeks);
  const wrap=document.getElementById(wrapId),tt=document.getElementById(ttId);if(!wrap||!tt)return;
  function doScrub(cx){try{
    const rect=svg.getBoundingClientRect();const rel=(cx-rect.left)/rect.width*300;
    let idx=Math.round((rel-10)/((300-20)/Math.max(1,n-1)));idx=Math.max(0,Math.min(n-1,idx));
    const sx=xs[idx];document.getElementById(svgId+'sc').setAttribute('x1',sx);document.getElementById(svgId+'sc').setAttribute('x2',sx);document.getElementById(svgId+'sc').setAttribute('opacity','1');
    let html=`<div style="font-size:9px;color:#64748b">${weeks[idx]}</div>`;
    series.forEach((s,si)=>{const v=s.v[idx];const dot=document.getElementById(svgId+'dt'+si);
      if(v==null){dot.setAttribute('opacity','0');return;}
      dot.setAttribute('cx',sx);dot.setAttribute('cy',ym(v));dot.setAttribute('opacity','1');
      html+=`<div style="font-size:13px;font-weight:700;color:${s.color}">${fmt(v)}${s.lbl?' <span style="font-size:9px;color:#64748b">'+s.lbl+'</span>':''}</div>`;});
    tt.innerHTML=html;const wr=wrap.getBoundingClientRect();let tx=(sx/300*wr.width)-42;tx=Math.max(0,Math.min(tx,wr.width-84));tt.style.left=tx+'px';tt.style.top='-6px';tt.classList.add('show');
  }catch(e){}}
  function end(){try{document.getElementById(svgId+'sc').setAttribute('opacity','0');series.forEach((s,si)=>{const d=document.getElementById(svgId+'dt'+si);if(d)d.setAttribute('opacity','0');});tt.classList.remove('show');}catch(e){}}
  wrap.ontouchstart=e=>{e.preventDefault();doScrub(e.touches[0].clientX);};
  wrap.ontouchmove=e=>{e.preventDefault();doScrub(e.touches[0].clientX);};
  wrap.ontouchend=end;
  wrap.onmousedown=e=>{doScrub(e.clientX);wrap.onmousemove=ev=>doScrub(ev.clientX);};
  wrap.onmouseup=()=>{wrap.onmousemove=null;end();};
  wrap.onmouseleave=()=>{wrap.onmousemove=null;end();};
}
function _ckOpenRun(i){
  const r=_CK.RUNS[i],st=r.hasStreams?_CK.STREAMS[r.id]:null;
  const el=document.getElementById('ck-modal');if(!el)return;
  el.querySelector('#ck-m-title').textContent=r.title;
  el.querySelector('#ck-m-sub').textContent=r.date+' · '+r.km+' km · '+r.al+'/km';
  el.querySelector('#ck-m-metrics').innerHTML=[['Distance',r.km+' km'],['Allure',r.al+'/km'],['Effort',r.re],['FC moy',r.fcm+' bpm'],['FC max',r.fcx+' bpm'],['Cadence',r.cad+' spm'],['D+',r.dp+' m'],['Calories',r.cal]].map(m=>`<div style="background:var(--gris-fond);border-radius:9px;padding:8px;text-align:center"><div style="font-size:14px;font-weight:700;color:var(--texte)">${m[1]}</div><div style="font-size:8.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--texte-deux);margin-top:3px">${m[0]}</div></div>`).join('');
  el.style.display='flex';
  if(r.hasStreams){
    const H=140,n=st.km.length,xs=st.km.map(d=>10+d/st.km[n-1]*(280));
    const hrMn=Math.min(...st.hr)-5,hrMx=Math.max(...st.hr)+5;
    const altMn=Math.min(...st.alt)-2,altMx=Math.max(...st.alt)+8;
    const pace=st.v.map(v=>v>0.3?1000/v:600);const pMn=Math.min(...pace),pMx=Math.min(Math.max(...pace),600);
    const yHR=v=>H-12-((v-hrMn)/(hrMx-hrMn)*(H-24));
    const yAlt=v=>H-12-((v-altMn)/(altMx-altMn)*(H-24));
    const yP=v=>H-12-((Math.min(v,pMx)-pMn)/(pMx-pMn)*(H-24));
    const path=(arr,ym)=>arr.map((v,i)=>(i?'L':'M')+xs[i].toFixed(1)+' '+ym(v).toFixed(1)).join(' ');
    const altL=path(st.alt,yAlt),hrL=path(st.hr,yHR),pL=path(pace,yP);
    const svg=el.querySelector('#ck-m-svg');svg.setAttribute('viewBox',`0 0 300 ${H}`);
    svg.innerHTML=`<defs><linearGradient id="ckAltG" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#94a3b8" stop-opacity="0.2"/><stop offset="100%" stop-color="#94a3b8" stop-opacity="0"/></linearGradient></defs>
      <path d="${altL} L${xs[n-1]} ${H-12} L${xs[0]} ${H-12} Z" fill="url(#ckAltG)"/>
      <path d="${altL}" fill="none" stroke="#94a3b8" stroke-width="1" opacity="0.5"/>
      <path d="${pL}" fill="none" stroke="#0d9488" stroke-width="1.5"/>
      <path d="${hrL}" fill="none" stroke="#ef4444" stroke-width="2"/>
      <line id="ck-msc" x1="-10" y1="0" x2="-10" y2="${H}" stroke="#475569" stroke-width="1" stroke-dasharray="3 3"/>
      <circle id="ck-mdHR" r="4" fill="#ef4444" opacity="0" stroke="#fff" stroke-width="1.5"/>
      <circle id="ck-mdP" r="4" fill="#0d9488" opacity="0" stroke="#fff" stroke-width="1.5"/>`;
    const wrap=el.querySelector('#ck-m-wrap'),tt=el.querySelector('#ck-m-tt');
    function scrubM(cx){try{
      const rect=svg.getBoundingClientRect();const rel=(cx-rect.left)/rect.width*300;
      let idx=0,best=1e9;xs.forEach((x,j)=>{const d=Math.abs(x-rel);if(d<best){best=d;idx=j;}});
      document.getElementById('ck-msc').setAttribute('x1',xs[idx]);document.getElementById('ck-msc').setAttribute('x2',xs[idx]);
      const dHR=document.getElementById('ck-mdHR');dHR.setAttribute('cx',xs[idx]);dHR.setAttribute('cy',yHR(st.hr[idx]));dHR.setAttribute('opacity','1');
      const dP=document.getElementById('ck-mdP');dP.setAttribute('cx',xs[idx]);dP.setAttribute('cy',yP(pace[idx]));dP.setAttribute('opacity','1');
      tt.innerHTML=`<div style="font-size:9px;color:#64748b">km ${st.km[idx].toFixed(1)}</div><div style="font-size:12px;font-weight:700;color:#ef4444">${st.hr[idx]} bpm</div><div style="font-size:12px;font-weight:700;color:#0d9488">${_ckSmin(pace[idx])}/km</div><div style="font-size:9px;color:#64748b">alt ${st.alt[idx].toFixed(0)} m</div>`;
      const wr=wrap.getBoundingClientRect();let tx=(xs[idx]/300*wr.width)-44;tx=Math.max(0,Math.min(tx,wr.width-90));tt.style.left=tx+'px';tt.style.top='-6px';tt.classList.add('show');
    }catch(e){}}
    function endM(){try{document.getElementById('ck-msc').setAttribute('x1','-10');document.getElementById('ck-mdHR').setAttribute('opacity','0');document.getElementById('ck-mdP').setAttribute('opacity','0');tt.classList.remove('show');}catch(e){}}
    wrap.ontouchstart=e=>{e.preventDefault();scrubM(e.touches[0].clientX);};
    wrap.ontouchmove=e=>{e.preventDefault();scrubM(e.touches[0].clientX);};
    wrap.ontouchend=endM;
    wrap.onmousedown=e=>{scrubM(e.clientX);wrap.onmousemove=ev=>scrubM(ev.clientX);};
    wrap.onmouseup=()=>{wrap.onmousemove=null;endM();};
    wrap.onmouseleave=()=>{wrap.onmousemove=null;endM();};
  } else {
    const svg=el.querySelector('#ck-m-svg');svg.setAttribute('viewBox','0 0 300 140');
    svg.innerHTML='<text x="150" y="70" text-anchor="middle" fill="#94a3b8" font-size="12">Streams disponibles en prod via Strava</text>';
  }
}
function _ckRenderAll(win){
  const D=_CK;const W=win;
  // KPIs dynamiques
  const totalKm=D.VOL[W].a.reduce((a,b)=>a+b,0);
  const totalRE=D.RE[W].v.reduce((a,b)=>a+b,0);
  const kmEl=document.getElementById('ck-km-val');if(kmEl){kmEl.textContent=totalKm.toFixed(0);}
  const kmLbl=document.getElementById('ck-km-lbl');if(kmLbl){kmLbl.textContent=W+' semaines';}
  const reLbl=document.getElementById('ck-re-lbl');if(reLbl){reLbl.textContent='Effort · '+W+' sem.';}
  document.getElementById('ck-re-val').textContent=totalRE;
  (function(){var cv=document.getElementById('ck-cad-val');if(!cv)return;try{var cs=(_CK&&_CK.CAD&&_CK.CAD[W]&&Array.isArray(_CK.CAD[W].v))?_CK.CAD[W].v.filter(x=>x!=null):[];if(cs.length){var avg=Math.round(cs.reduce((a,b)=>a+b,0)/cs.length);cv.innerHTML=avg+'<span class="ck-ku">spm</span>';}else{cv.innerHTML='—<span class="ck-ku">spm</span>';}}catch(e){}})();
  _pmcRender(W);
  _ckBar('ckVol','ckVolW','ckVolT','ckVolX',D.VOL[W],{ref:true,col:'#0d9488',unit:' km',h:90});
  document.getElementById('ck-vol-sub').textContent=totalKm.toFixed(0)+' km · '+W+' sem.';
  _ckBar('ckRE','ckREW','ckRET','ckREX',D.RE[W],{col:'#0d9488',h:80});
  _ckLine('ckACWR','ckACWRW','ckACWRT','ckACWRX',D.ACWR[W].w,[{v:D.ACWR[W].v,color:'#f59e0b',lbl:''}],v=>v.toFixed(2),{h:65,fill:false,zones:[[0,0.8,'#0d9488'],[0.8,1.3,'#16a34a'],[1.3,2,'#ef4444']]});
  const al=D.ACWR[W].v[D.ACWR[W].v.length-1];
  var _av=document.getElementById('ck-acwr-val');_av.textContent=al.toFixed(2);
  var _acol=al>1.5?'#ef4444':al>1.3?'#f59e0b':al<0.8?'#0d9488':'#16a34a';
  _av.style.color=_acol;_av.classList.remove('warn');
  var _alab=al>1.5?'\u{1F534} surcharge':al>1.3?'\u26a0 \u00e9lev\u00e9':al<0.8?'frais / all\u00e8gement':'ma\u00eetris\u00e9';
  var _akd=_av.parentElement.querySelector('.ck-kd');if(_akd){_akd.textContent=_alab;_akd.style.color=_acol;_akd.classList.remove('warn');}
  var _av2=document.getElementById('ck-acwr-val2');if(_av2){_av2.textContent=al.toFixed(2);_av2.style.color=_acol;}
  _ckBar('ckDP','ckDPW','ckDPT','ckDPX',D.DPLUS[W],{col:'#94a3b8',unit:' m',h:75});
  _ckLine('ckZ2','ckZ2W','ckZ2T','ckZ2X',D.Z2[W].w,[{v:D.Z2[W].v,color:'#0d9488',lbl:'/km'}],_ckSmin,{h:85});
  document.getElementById('ck-z2-val').textContent=_ckSmin(D.Z2[W].v[D.Z2[W].v.length-1]);
  const z2d=D.Z2[W].v[0]-D.Z2[W].v[D.Z2[W].v.length-1];document.getElementById('ck-z2-delta').textContent=(z2d>0?'↓ −'+_ckSmin(z2d)+'/km · le moteur grossit 💪':'↑ à surveiller');document.getElementById('ck-z2-delta').style.color=z2d>0?'#16a34a':'#ef4444';
  const dcLast=D.DC[W].v.filter(x=>x!=null).pop();_ckLine('ckDC','ckDCW','ckDCT','ckDCX',D.DC[W].w,[{v:D.DC[W].v,color:'#16a34a',lbl:'%'}],v=>v.toFixed(1)+'%',{h:75,zones:[[0,5,'#16a34a'],[5,8,'#f59e0b'],[8,15,'#ef4444']]});
  document.getElementById('ck-dc-val').textContent=dcLast?dcLast.toFixed(1)+'%':'—';document.getElementById('ck-dc-val').style.color=dcLast<5?'#16a34a':dcLast<8?'#f59e0b':'#ef4444';
  _ckLine('ckPACE','ckPACEW','ckPACET','ckPACEX',D.PACE[W].w,[{v:D.PACE[W].ef,color:'#16a34a',lbl:'EF'},{v:D.PACE[W].am,color:'#0d9488',lbl:'AM'},{v:D.PACE[W].se,color:'#f59e0b',lbl:'Seuil'}],_ckSmin,{h:95,fill:false});
  // Zones FC
  const z=D.FCZ[W],H=100,n=z.length,gap=300/n,bw=gap*0.5,mxz=Math.max(...z.map(x=>x[2]));
  let fcs='';z.forEach((zone,i)=>{const x=i*gap+gap*0.25,h=zone[2]/mxz*(H-22);fcs+=`<rect class="ck-fcb" data-i="${i}" x="${x}" y="${H-h-10}" width="${bw}" height="${h}" rx="3" fill="${zone[1]}"/><text x="${x+bw/2}" y="${H-h-14}" text-anchor="middle" font-size="11" font-weight="700" fill="${zone[1]}">${zone[2]}%</text><text x="${x+bw/2}" y="${H-1}" text-anchor="middle" font-size="9" fill="#94a3b8">${zone[0]}</text>`;});
  const fcSvg=document.getElementById('ckFC');fcSvg.setAttribute('viewBox',`0 0 300 ${H}`);fcSvg.innerHTML=fcs;
  document.getElementById('ck-fc-sub').textContent=z[1][2]+'% en Z2 · '+W+' sem.';
  fcSvg.querySelectorAll('.ck-fcb').forEach(b=>b.addEventListener('click',()=>{const zone=z[+b.dataset.i];const ranges={'Z1':'<130 bpm','Z2':'130-144','Z3':'145-165','Z4+':'>165 bpm'};document.getElementById('ck-fc-info').innerHTML=`<strong style="color:${zone[1]}">${zone[0]}</strong> · ${ranges[zone[0]]} · ${zone[2]}%`;}));
  _ckLine('ckCAD','ckCADW','ckCADT','ckCADX',D.CAD[W].w,[{v:D.CAD[W].v,color:'#06b6d4',lbl:'spm'}],v=>v.toFixed(0)+' spm',{h:70});
  const cadLast=D.CAD[W].v.filter(x=>x!=null).pop();document.getElementById('ck-cad-val').textContent=cadLast?cadLast.toFixed(0):'—';
  // Run list
  document.getElementById('ck-runs').innerHTML=D.RUNS.map((r,i)=>`<div onclick="_ckOpenRun(${i})" style="background:var(--gris-fond);border-radius:10px;padding:10px 12px;display:flex;align-items:center;gap:10px;cursor:pointer;margin-bottom:6px"><div style="width:7px;height:7px;border-radius:50%;background:${r.type};flex:0 0 7px"></div><div style="flex:1;min-width:0"><div style="font-size:13px;font-weight:600;color:var(--texte)">${r.title}${r.hasStreams?' <span style="font-size:9px;color:#0d9488">⊙ live</span>':''}</div><div style="font-size:10px;color:var(--texte-deux);margin-top:1px">${r.date} · RE ${r.re} · FC ${r.fcm}/${r.fcx}</div></div><div style="text-align:right"><div style="font-size:14px;font-weight:700;color:var(--texte)">${r.km}</div><div style="font-size:9px;color:var(--texte-deux)">${r.al}/km</div></div></div>`).join('');
}
function renderCockpit(){
  const el=document.getElementById('cockpit-contenu');
  if(el.innerHTML.trim()){_ckRenderAll(_ckWin);return;}
  const FC_RANGE={'Z1':'<130 bpm','Z2':'130-144','Z3':'145-165','Z4+':'>165 bpm'};
  function card(id,title,sub,valId,valSuffix,chartH,extra,helpKey){
    const hb=helpKey?`<button class="ck-help" onclick="event.stopPropagation();openCkHelp('${helpKey}')">?</button>`:'';
    return`<div class="ck-card"><div class="ck-ch"><div><div class="ck-ct">${title}${hb}</div><div class="ck-cs" id="${id}-sub">${sub}</div></div>${valId?`<div style="text-align:right"><div class="ck-big" id="${valId}">—</div>${valSuffix?'<div class="ck-cs">'+valSuffix+'</div>':''}</div>`:''}</div><div class="ck-cw" id="${id}W"><svg id="${id}" height="${chartH}" style="display:block;width:100%"></svg><div class="ck-tt" id="${id}T"></div></div><div class="ck-xl" id="${id}X"></div>${extra||''}</div>`;
  }
  const _f=computeFormeScore();
  const _fcol=_f.color||'#0d9488';
  const _ftrend=_f.trend||'→';
  el.innerHTML=`
<div style="padding:var(--sp-3) var(--sp-3) var(--sp-10)">
<div style="font-size:22px;font-weight:700;color:var(--texte);letter-spacing:-.02em;margin-bottom:2px">Cockpit</div>
<div style="font-size:11px;color:var(--texte-deux);margin-bottom:var(--sp-4)">Glisse sur les courbes · touche une barre · tap une sortie</div>
<div class="ck-hero" onclick="openCkHelp('forme')">
  <div class="ck-hero-l">
    <div class="ck-hero-lbl">Forme du jour</div>
    <div class="ck-hero-val" style="color:${_fcol}">${_f.score}<span class="ck-hero-tr">${_ftrend}</span></div>
    <div class="ck-hero-sig">${_f.signal||''}</div>
  </div>
</div>
<div class="ck-toggle" id="ck-tgl">
  <button class="ck-tg" onclick="ckWin(2,this)">2 sem.</button>
  <button class="ck-tg" onclick="ckWin(4,this)">4 sem.</button>
  <button class="ck-tg ck-on" onclick="ckWin(8,this)">8 sem.</button>
  <button class="ck-tg" onclick="ckWin(12,this)">12 sem.</button>
</div>
<div class="ck-kpis">
  <div class="ck-kpi"><div class="ck-kv" id="ck-km-val">—<span class="ck-ku">km</span></div><div class="ck-kl" id="ck-km-lbl">fenêtre</div><div class="ck-kd up">cumulé</div></div>
  <div class="ck-kpi"><div class="ck-kv" id="ck-re-val">—</div><div class="ck-kl" id="ck-re-lbl">Effort</div><div class="ck-kd up">cumulé</div></div>
  <div class="ck-kpi"><div class="ck-kv" id="ck-acwr-val">0.69</div><div class="ck-kl">ACWR</div><div class="ck-kd">frais</div></div>
  <div class="ck-kpi"><div class="ck-kv" id="ck-cad-val">—<span class="ck-ku">spm</span></div><div class="ck-kl">Cadence</div><div class="ck-kd" id="ck-cad-d">moy.</div></div>
</div>
<div class="ck-sec">📊 Volume &amp; charge</div>
<div class="ck-sec">📈 Performance Management Chart</div>
<div class="ck-card"><div class="ck-ch"><div><div class="ck-ct">CTL · ATL · TSB<button class="ck-help" onclick="event.stopPropagation();openCkHelp('pmc')">?</button></div><div class="ck-cs" id="ckPMC-sub">Fitness · Fatigue · Forme</div></div></div><div class="ck-cw" id="ckPMCW"><svg id="ckPMC" height="90" style="display:block;width:100%"></svg><div class="ck-tt" id="ckPMCT">glisse pour voir les valeurs</div></div><div style="display:flex;gap:14px;font-size:10px;color:var(--texte-deux);margin-top:6px;padding:0 2px"><span><span style="color:#0d9488">●</span> CTL fitness</span><span><span style="color:#f59e0b">●</span> ATL fatigue</span><span><span style="color:#16a34a">▌</span> TSB forme</span></div></div>
${card('ckVol','Volume hebdomadaire','',null,null,90,'<div style="font-size:9px;color:#94a3b8;text-align:center;margin-top:4px">touche une barre · ■ prévu</div>','vol')}
<div class="ck-cs" id="ck-vol-sub" style="margin:-4px 0 8px;padding:0 2px"></div>
${card('ckRE','⚡ Relative Effort / sem.','charge Strava réelle',null,null,80,'<div style="font-size:9px;color:#94a3b8;text-align:center;margin-top:4px">glisse →</div>','re')}
<div class="ck-card"><div class="ck-ch"><div><div class="ck-ct">🩹 ACWR — risque blessure<button class="ck-help" onclick="event.stopPropagation();openCkHelp('acwr')">?</button></div><div class="ck-cs">ratio charge aiguë / chronique</div></div><div style="font-size:26px;font-weight:700;line-height:1" id="ck-acwr-val2">0.69</div></div><div class="ck-cw" id="ckACWRW"><svg id="ckACWR" height="65" style="display:block;width:100%"></svg><div class="ck-tt" id="ckACWRT"></div></div><div class="ck-xl" id="ckACWRX"></div></div>
${card('ckDP','⛰ Dénivelé D+','',null,'m',75,'','dp')}
<div class="ck-sec">🔋 Moteur aérobie</div>
<div class="ck-card"><div class="ck-ch"><div><div class="ck-ct">Z2 pace — allure EF à FC&lt;144<button class="ck-help" onclick="event.stopPropagation();openCkHelp('z2')">?</button></div><div class="ck-cs">indicateur n°1 du développement</div></div><div style="text-align:right"><div style="font-size:22px;font-weight:700;color:#0d9488" id="ck-z2-val">5:54</div><div class="ck-cs">/km</div></div></div><div style="font-size:10px;font-weight:600;margin:3px 0 6px" id="ck-z2-delta"></div><div class="ck-cw" id="ckZ2W"><svg id="ckZ2" height="85" style="display:block;width:100%"></svg><div class="ck-tt" id="ckZ2T"></div></div><div class="ck-xl" id="ckZ2X"></div></div>
<div class="ck-card"><div class="ck-ch"><div><div class="ck-ct">💓 Découplage cardiaque<button class="ck-help" onclick="event.stopPropagation();openCkHelp('dc')">?</button></div><div class="ck-cs">dérive FC sortie longue · &lt;5% idéal</div></div><div style="font-size:22px;font-weight:700" id="ck-dc-val">—</div></div><div class="ck-cw" id="ckDCW"><svg id="ckDC" height="75" style="display:block;width:100%"></svg><div class="ck-tt" id="ckDCT"></div></div><div class="ck-xl" id="ckDCX"></div></div>
<div class="ck-sec">📈 Allure &amp; vitesse</div>
<div class="ck-card"><div class="ck-ch"><div><div class="ck-ct">Progression allure par type<button class="ck-help" onclick="event.stopPropagation();openCkHelp('pace')">?</button></div><div class="ck-cs">EF · marathon · seuil</div></div></div><div class="ck-cw" id="ckPACEW"><svg id="ckPACE" height="95" style="display:block;width:100%"></svg><div class="ck-tt" id="ckPACET"></div></div><div class="ck-xl" id="ckPACEX"></div><div style="display:flex;gap:12px;font-size:10px;color:var(--texte-deux);margin-top:7px"><span><span style="color:#16a34a">●</span> EF</span><span><span style="color:#0d9488">●</span> AM</span><span><span style="color:#f59e0b">●</span> Seuil</span></div></div>
<div class="ck-sec">❤️ Cardiaque &amp; cadence</div>
<div class="ck-card"><div class="ck-ch"><div><div class="ck-ct">Zones FC<button class="ck-help" onclick="event.stopPropagation();openCkHelp('fc')">?</button></div><div class="ck-cs" id="ck-fc-sub"></div></div></div><div class="ck-cw" id="ckFCW"><svg id="ckFC" height="100" style="display:block;width:100%"></svg><div class="ck-tt" id="ckFCT"></div></div><div style="font-size:10px;color:var(--texte-deux);text-align:center;margin-top:6px;min-height:14px" id="ck-fc-info">touche une zone</div></div>
<div class="ck-card"><div class="ck-ch"><div><div class="ck-ct">🦶 Cadence<button class="ck-help" onclick="event.stopPropagation();openCkHelp('cad')">?</button></div><div class="ck-cs">route ~172 spm · trail ~146 spm</div></div><div><div style="font-size:22px;font-weight:700;color:var(--texte)" id="ck-cad-val">172</div><div class="ck-cs">spm</div></div></div><div class="ck-cw" id="ckCADW"><svg id="ckCAD" height="70" style="display:block;width:100%"></svg><div class="ck-tt" id="ckCADT"></div></div><div class="ck-xl" id="ckCADX"></div></div>
<div class="ck-sec">🔍 Analyse par sortie</div>
<div id="ck-runs"></div>
</div>
<div id="ck-modal" style="display:none;position:fixed;inset:0;background:rgba(15,23,42,.6);z-index:200;align-items:flex-end">
  <div style="background:var(--bg-card,#fff);border-radius:18px 18px 0 0;width:100%;max-height:90vh;overflow-y:auto">
    <div style="position:sticky;top:0;background:var(--bg-card,#fff);padding:14px 14px 10px;border-bottom:.5px solid var(--bord-card,#e2e8f0)">
      <div style="width:36px;height:4px;background:#cbd5e1;border-radius:99px;margin:0 auto 12px"></div>
      <button onclick="document.getElementById('ck-modal').style.display='none'" style="position:absolute;top:14px;right:14px;width:28px;height:28px;border-radius:50%;background:var(--gris-fond);border:none;color:var(--texte-deux);font-size:15px;cursor:pointer">✕</button>
      <div style="font-size:16px;font-weight:700;color:var(--texte)" id="ck-m-title"></div>
      <div style="font-size:11px;color:var(--texte-deux);margin-top:2px" id="ck-m-sub"></div>
    </div>
    <div style="padding:12px 14px">
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-bottom:12px" id="ck-m-metrics"></div>
      <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--texte-deux);margin-bottom:6px">FC · Allure · Altitude</div>
      <div style="position:relative;touch-action:none" id="ck-m-wrap"><svg id="ck-m-svg" height="140" style="display:block;width:100%"></svg><div class="ck-tt" id="ck-m-tt"></div></div>
      <div style="display:flex;gap:12px;font-size:10px;color:var(--texte-deux);margin-top:6px"><span><span style="color:#ef4444">●</span> FC</span><span><span style="color:#0d9488">●</span> Allure</span><span><span style="color:#94a3b8">●</span> Altitude</span></div>
      <div style="font-size:9px;color:#94a3b8;text-align:center;margin-top:4px;font-style:italic">glisse sur le graphe seconde par seconde</div>
    </div>
  </div>
</div>`;
  _ckRenderAll(_ckWin);
}
function ckWin(w,el){_ckWin=w;document.querySelectorAll('.ck-tg').forEach(b=>b.classList.remove('ck-on'));el.classList.add('ck-on');_ckRenderAll(w);}
/* ===== Déplacer / Skipper séance ===== */
const SM_REASONS=['Fatigue / récupération','Contrainte agenda','Météo défavorable','Repos actif choisi'];
let _smWk=null,_smId=null,_smReason=null;
function _smOvKey(wk,id){return wk+'-'+id;}
function _smLoad(){try{return JSON.parse(localStorage.getItem('session_overrides')||'{}')}catch(e){return{};}}
function _smSave(o){localStorage.setItem('session_overrides',JSON.stringify(o));}
function hydrateOverrides(){
  const ovs=_smLoad();
  Object.entries(ovs).forEach(([k,ov])=>{
    const i=k.indexOf('-');const wk=k.slice(0,i),id=k.slice(i+1);
    const se=findSeance(wk,id);if(!se)return;
    if(ov.action==='move'&&ov.newDate)se.date=ov.newDate;
    if(ov.action==='skip')se.realise={statut:'skipped',reason:ov.reason};
  });
}
function _smFmtDate(d){
  const dt=new Date(d+'T12:00:00');
  const j=['dim','lun','mar','mer','jeu','ven','sam'];
  const m=['jan','fév','mar','avr','mai','juin','juil','août','sep','oct','nov','déc'];
  return j[dt.getDay()]+' '+dt.getDate()+' '+m[dt.getMonth()];
}
function openSM(wk,id){
  _smWk=wk;_smId=id;
  const se=findSeance(wk,id);if(!se)return;
  const ov=_smLoad();
  document.getElementById('sm-title').textContent=se.titre;
  document.getElementById('sm-sub').textContent='S'+wk+' · Séance '+se.num+(se.date?' · '+_smFmtDate(se.date):'');
  document.getElementById('sm-overlay').classList.add('open');
}
function closeSM(){document.getElementById('sm-overlay').classList.remove('open');}
function openSMMove(){
  closeSM();
  const se=findSeance(_smWk,_smId);if(!se)return;
  document.getElementById('sm-dp-sub').textContent=se.titre;
  const inp=document.getElementById('sm-dp-input');
  inp.value=se.date||'';
  if(se.date){
    const d=new Date(se.date+'T12:00:00');const dow=d.getDay()||7;
    const mon=new Date(d);mon.setDate(d.getDate()-(dow-1));
    const sun=new Date(mon);sun.setDate(mon.getDate()+6);
    inp.min=mon.toISOString().slice(0,10);inp.max=sun.toISOString().slice(0,10);
  }
  document.getElementById('sm-dp-ov').classList.add('open');
}
function closeSMDate(){document.getElementById('sm-dp-ov').classList.remove('open');}
function openSMSkip(){
  closeSM();_smReason=null;
  const se=findSeance(_smWk,_smId);if(!se)return;
  document.getElementById('sm-sk-sub').textContent=se.titre+' · S'+_smWk;
  document.getElementById('sm-sk-reasons').innerHTML=SM_REASONS.map((r,i)=>`<div class="sm-reason" id="smr${i}" onclick="selSMReason(${i},'${r}')"><div class="sm-rdot"></div><span class="sm-rlbl">${r}</span></div>`).join('');
  document.getElementById('sm-sk-ov').classList.add('open');
}
function closeSMSkip(){document.getElementById('sm-sk-ov').classList.remove('open');}
function selSMReason(i,r){_smReason=r;document.querySelectorAll('.sm-reason').forEach((el,j)=>el.classList.toggle('sm-rsel',i===j));}
function confirmSMMove(){
  const d=document.getElementById('sm-dp-input').value;if(!d)return;
  const ovs=_smLoad();const k=_smOvKey(_smWk,_smId);
  ovs[k]=Object.assign(ovs[k]||{},{action:'move',newDate:d});
  _smSave(ovs);closeSMDate();
  hydrateOverrides();renderHeader();renderPlan();
  _smToast('Séance déplacée au '+_smFmtDate(d));
}
function confirmSMSkip(){
  if(!_smReason)return;
  const ovs=_smLoad();ovs[_smOvKey(_smWk,_smId)]={action:'skip',reason:_smReason};
  _smSave(ovs);closeSMSkip();
  hydrateOverrides();renderHeader();renderPlan();
  _smToast('Séance passée — '+_smReason.toLowerCase());
}
function _smToast(msg){const t=document.getElementById('sm-toast');if(!t)return;t.textContent=msg;t.classList.remove('sm-show');void t.offsetWidth;t.classList.add('sm-show');}
function initSessionMenu(){
  if(!document.body||typeof document.body.insertAdjacentHTML!=='function')return;
  document.body.insertAdjacentHTML('beforeend',`
<div id="sm-overlay" onclick="if(event.target===this)closeSM()">
  <div class="sm-sheet">
    <div class="sm-handle"></div>
    <div class="sm-stitle" id="sm-title"></div>
    <div class="sm-ssub" id="sm-sub"></div>
    <button class="sm-action" onclick="openSMMove()"><span class="sm-aico">📅</span><div><div class="sm-al">Déplacer cette séance</div><div class="sm-as">Choisir une autre date</div></div><span class="sm-aarr">›</span></button>
    <button class="sm-action" onclick="openSMSkip()"><span class="sm-aico">⏭</span><div><div class="sm-al">Passer cette séance</div><div class="sm-as">Fatigue, agenda, météo…</div></div><span class="sm-aarr">›</span></button>
    <button class="sm-cancel" onclick="closeSM()">Annuler</button>
  </div>
</div>
<div id="sm-dp-ov" onclick="if(event.target===this)closeSMDate()">
  <div class="sm-sheet">
    <div class="sm-handle"></div>
    <div class="sm-stitle">Déplacer la séance</div>
    <div class="sm-ssub" id="sm-dp-sub"></div>
    <label class="sm-label">Nouvelle date<input type="date" id="sm-dp-input"></label>
    <button class="sm-confirm" onclick="confirmSMMove()">Déplacer</button>
    <button class="sm-cancel" onclick="closeSMDate()">Annuler</button>
  </div>
</div>
<div id="sm-sk-ov" onclick="if(event.target===this)closeSMSkip()">
  <div class="sm-sheet">
    <div class="sm-handle"></div>
    <div class="sm-stitle">Passer cette séance</div>
    <div class="sm-ssub" id="sm-sk-sub"></div>
    <div id="sm-sk-reasons"></div>
    <button class="sm-confirm sm-danger" onclick="confirmSMSkip()">Confirmer — passer la séance</button>
    <button class="sm-cancel" onclick="closeSMSkip()">Annuler</button>
  </div>
</div>
<div id="sm-toast" class="sm-toast"></div>`);
}
function _afterLog(wk,id){try{_ckRebuild();}catch(e){}renderHeader();renderPlan();if(document.getElementById('vue-cockpit').style.display!=='none'){renderCockpit();renderDash();}ouvrirSeance(wk,id);setTimeout(()=>{const b=document.querySelector&&document.querySelector('.lf-save');if(b){b.textContent='Enregistré ✓';b.classList.add('lf-saved');setTimeout(()=>{if(b)b.textContent='Enregistrer';},1800);}},80);}
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
/* ===== Quick Log — bottom sheet depuis la liste semaine ===== */
let _qlWk=null,_qlId=null;
function ouvrirQuickLog(wk,id){
  _qlWk=wk;_qlId=id;
  const se=findSeance(wk,id);if(!se)return;
  const r=se.realise||{};
  document.getElementById('ql-titre').textContent=se.titre;
  document.getElementById('ql-sous').textContent='S'+wk+' · Séance '+se.num;
  const distNum=se.metriques&&se.metriques.Distance?parseFloat(se.metriques.Distance.replace(/[^0-9.,]/g,'').replace(',','.'))||'':'';
  document.getElementById('ql-km').value=r.km||distNum||'';
  document.getElementById('ql-temps').value=r.temps||'';
  document.getElementById('ql-rpe').value=r.rpe_ressenti||'';
  _qlCalc();
  document.getElementById('ql-overlay').classList.add('open');
  setTimeout(()=>document.getElementById('ql-km').focus(),220);
}
function fermerQuickLog(){document.getElementById('ql-overlay').classList.remove('open');}
function _qlCalc(){
  const km=parseFloat((document.getElementById('ql-km').value||'').replace(',','.'));
  const t=document.getElementById('ql-temps').value;
  const el=document.getElementById('ql-allure');
  el.textContent=(km&&t)?computeAllure(km,t):'—';
}
function qlNutr(el){el.classList.toggle('ql-nc-on');}
function soumettreQuickLog(){
  const km=parseFloat((document.getElementById('ql-km').value||'').replace(',','.'))||0;
  if(!km)return;
  const temps=document.getElementById('ql-temps').value||'';
  const rpe=document.getElementById('ql-rpe').value||'';
  const nutr=Array.from(document.querySelectorAll('.ql-nc.ql-nc-on')).map(e=>e.dataset.n).join(', ');
  const se=findSeance(_qlWk,_qlId);if(!se)return;
  const allure=computeAllure(km,temps);
  const ex=se.realise||{};
  const realise={statut:'fait',km,temps,allure,
    fc_moy:ex.fc_moy||'',fc_max:ex.fc_max||'',rpe_ressenti:rpe,
    nutrition:nutr||ex.nutrition||'',
    commentaire:ex.commentaire||'',pr:ex.pr||0,ach:ex.ach||0,revue:ex.revue||''};
  const logs=loadLogs();logs[logId(_qlWk,_qlId)]=realise;saveLogs(logs);se.realise=realise;
  fermerQuickLog();
  // Mise à jour DOM immédiate de la carte
  const card=document.getElementById('sc-'+_qlWk+'-'+_qlId);
  if(card){
    card.classList.add('sc-fait');
    const b=card.querySelector('.ql-btn');
    if(b)b.outerHTML='<div class="seance-fleche sc-check">✓</div>';
    const nom=card.querySelector('.seance-nom');if(nom)nom.style.color='#15803d';
    const info=card.querySelector('.seance-info');
    if(info&&!info.querySelector('.ql-real'))
      info.querySelector('.seance-desc').insertAdjacentHTML('afterend',
        `<div class="seance-desc ql-real" style="color:#15803d;font-weight:700;margin-top:3px">✓ ${km} km${allure?' · '+allure:''}</div>`);
  }
  renderHeader();
  const toast=document.getElementById('ql-toast');
  if(toast){toast.classList.remove('ql-show');void toast.offsetWidth;toast.classList.add('ql-show');}
}
function initQuickLog(){
  if(!document.body||typeof document.body.insertAdjacentHTML!=='function')return;
  document.body.insertAdjacentHTML('beforeend',`
<div id="ql-overlay" onclick="if(event.target===this)fermerQuickLog()">
  <div id="ql-sheet">
    <div class="ql-handle"></div>
    <div id="ql-titre" class="ql-titre"></div>
    <div id="ql-sous" class="ql-sous"></div>
    <div class="ql-fields">
      <label class="ql-label">Distance (km)<input id="ql-km" type="number" step="0.1" inputmode="decimal" oninput="_qlCalc()"></label>
      <div class="ql-row2">
        <label class="ql-label">Temps<input id="ql-temps" type="text" inputmode="numeric" placeholder="0:54:10" oninput="_qlCalc()"></label>
        <label class="ql-label">Allure<div id="ql-allure" class="ql-allure-val">—</div></label>
      </div>
      <label class="ql-label">RPE (1-10)<input id="ql-rpe" type="number" min="1" max="10" inputmode="numeric"></label>
      <div class="ql-label">Nutrition (optionnel)
        <div class="ql-nutr" id="ql-nutr">
          <div class="ql-nc" data-n="TA Electrolytes" onclick="qlNutr(this)">⚡ TA</div>
          <div class="ql-nc" data-n="Gel Aptonia" onclick="qlNutr(this)">🟡 Gel</div>
          <div class="ql-nc" data-n="Nduranz Cherry" onclick="qlNutr(this)">🍒 Cherry</div>
          <div class="ql-nc" data-n="Nduranz Amarena" onclick="qlNutr(this)">☕ Amarena</div>
        </div>
      </div>
    </div>
    <button class="ql-submit" onclick="soumettreQuickLog()"><i class="ti ti-check"></i> Enregistrer</button>
    <button class="ql-cancel" onclick="fermerQuickLog()">Annuler</button>
  </div>
</div>
<div id="ql-toast" class="ql-toast">Séance enregistrée ✓</div>`);
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
   theorie:"<p><strong>Pourquoi c'est la séance reine.</strong> Le marathon se gagne sur l'endurance, et l'endurance se construit sur la durée. La sortie longue étend tes réserves de glycogène, multiplie les capillaires, et surtout muscle ta tête : apprendre à rester efficace quand c'est long et inconfortable.</p><p><strong>Le fueling, ta priorité n°1.</strong> C'est ton limiteur identifié — l'effondrement de La Circaète (km 21) venait d'un déficit d'eau et d'électrolytes par forte chaleur. La sortie longue est <em>l'</em>occasion de répéter ton plan : électrolytes réguliers, gels testés (4Endurance, Nduranz), boire avant la soif. Ne jamais découvrir son fueling le jour de la course.</p><p><strong>Le finish allure marathon.</strong> Courir les derniers km à 5:20 sur des jambes déjà fatiguées, c'est répéter <em>exactement</em> le 35e km de Nice. C'est dur, c’est volontaire, et c'est ce qui fait la différence entre finir fort et marcher.</p>",
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
  const Z=[['Z1','Récup / EF','<134','#16a34a'],['Z2','Endurance','134-154','#84cc16'],['Z3','Tempo / AM','154-167','#f59e0b'],['Z4','Seuil','167-177','#f59e0b'],['Z5','VO2max','>177','#ef4444']];
  const w=300,bh=34,gap=4,x0=8;let bars='',labs='';const bw=(w-x0*2-gap*4)/5;
  Z.forEach((z,i)=>{const x=x0+i*(bw+gap);const on=hi===i;bars+=`<rect x="${x}" y="14" width="${bw}" height="${bh}" rx="5" fill="${z[3]}" opacity="${on?1:.3}"/>${on?`<rect x="${x}" y="14" width="${bw}" height="${bh}" rx="5" fill="none" stroke="${z[3]}" stroke-width="2.5"/>`:''}`;labs+=`<text x="${x+bw/2}" y="62" text-anchor="middle" font-size="9" font-weight="700" fill="${on?z[3]:'#94a3b8'}">${z[0]}</text><text x="${x+bw/2}" y="73" text-anchor="middle" font-size="7.5" fill="#94a3b8">${z[2]}</text>`;});
  return `<svg viewBox="0 0 ${w} 82" class="theo-svg" role="img" aria-label="Zones de fréquence cardiaque">${bars}${labs}</svg>`;
}
function svg8020(){
  return `<svg viewBox="0 0 300 96" class="theo-svg" role="img" aria-label="Répartition polarisée 80/20">
    <rect x="8" y="14" width="200" height="30" rx="5" fill="#16a34a"/><text x="108" y="33" text-anchor="middle" font-size="11" font-weight="800" fill="#fff">80 % FACILE</text>
    <rect x="212" y="14" width="34" height="30" rx="5" fill="#f59e0b" opacity=".35"/>
    <rect x="250" y="14" width="42" height="30" rx="5" fill="#ef4444"/><text x="271" y="33" text-anchor="middle" font-size="10" font-weight="800" fill="#fff">20 %</text>
    <text x="229" y="58" text-anchor="middle" font-size="8" font-weight="700" fill="#f59e0b">zone grise</text>
    <text x="229" y="68" text-anchor="middle" font-size="7.5" fill="#94a3b8">le piège</text>
    <path d="M229 44 L229 50" stroke="#f59e0b" stroke-width="1.5"/>
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
    <path d="M34 14 C140 28, 240 52, 292 64" fill="none" stroke="#16a34a" stroke-width="2.5"/>
    <text x="200" y="44" font-size="8" font-weight="700" fill="#16a34a">avec fueling</text>
    <text x="206" y="113" font-size="7.5" fill="#94a3b8">~30-32 km</text>
  </svg>`;
}
function svgDerive(){
  return `<svg viewBox="0 0 300 120" class="theo-svg" role="img" aria-label="Dérive cardiaque">
    <line x1="30" y1="10" x2="30" y2="92" stroke="#cbd5e1" stroke-width="1"/><line x1="30" y1="92" x2="292" y2="92" stroke="#cbd5e1" stroke-width="1"/>
    <text x="150" y="112" text-anchor="middle" font-size="8.5" fill="#94a3b8">temps →</text>
    <line x1="30" y1="60" x2="292" y2="60" stroke="#0d9488" stroke-width="2.5" stroke-dasharray="0"/>
    <text x="200" y="54" font-size="8" font-weight="700" fill="#0d9488">allure (constante)</text>
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
    <path d="M30 86 C120 84, 170 78, 200 64 C225 52, 250 26, 285 14" fill="none" stroke="#0d9488" stroke-width="2.5"/>
    <line x1="200" y1="14" x2="200" y2="92" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4 3"/>
    <text x="200" y="106" text-anchor="middle" font-size="8" font-weight="700" fill="#f59e0b">SEUIL</text>
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
   {h:'Le finish allure marathon',html:`<p>Quand la sortie longue se termine par quelques km à 5:20/km sur des jambes déjà entamées, tu répètes <strong>exactement le 35e km de Nice</strong>. C'est dur, c’est volontaire, et c'est ce qui fait la différence entre finir solide et marcher. Garde toujours du jus pour ce finish : tu dois le terminer en contrôle, pas cramé.</p>`}],
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
    <path d="M40 100 L210 30 L210 100 Z" fill="#16a34a" opacity=".12"/>
    <path d="M40 100 L210 30" stroke="#16a34a" stroke-width="2.5"/>
    <circle cx="120" cy="62" r="6" fill="#1e293b"/>
    <path d="M120 62 L132 56" stroke="#1e293b" stroke-width="3" stroke-linecap="round"/>
    <path d="M120 62 L112 72" stroke="#1e293b" stroke-width="3" stroke-linecap="round"/>
    <path d="M126 50 L140 40" stroke="#f59e0b" stroke-width="2.5" marker-end="url(#ar)"/>
    <defs><marker id="ar" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto"><path d="M0 0 L6 3.5 L0 7 Z" fill="#f59e0b"/></marker></defs>
    <text x="158" y="44" font-size="8" font-weight="700" fill="#f59e0b">pousse contre</text>
    <text x="158" y="54" font-size="8" font-weight="700" fill="#f59e0b">la gravité</text>
    <text x="60" y="115" font-size="8" fill="#94a3b8">+ de fibres recrutées · tendons = ressort · 0 stress vitesse</text>
  </svg>`;
}
function svgRiegel(){
  return `<svg viewBox="0 0 300 124" class="theo-svg" role="img" aria-label="Prédiction de performance">
    <line x1="34" y1="12" x2="34" y2="96" stroke="#cbd5e1" stroke-width="1"/><line x1="34" y1="96" x2="288" y2="96" stroke="#cbd5e1" stroke-width="1"/>
    <text x="14" y="26" font-size="8" fill="#94a3b8">temps</text>
    <path d="M50 84 C120 78, 200 60, 278 22" fill="none" stroke="#0d9488" stroke-width="2.5"/>
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
  const struct=se.struct.map((b,i)=>{const c=(i===0||i===se.struct.length-1)?'#16a34a':se.accent;return `<div class="struct-ligne"><div class="struct-puce" style="background:${c}"></div><div class="struct-nom">${b.nom}</div><div class="struct-txt">${b.txt}</div></div>`;}).join('');
  const LEGMAP={vert:['#16a34a','Endurance / échauffement / retour au calme'],bleu:['#0d9488','Travail qualitatif / spécifique'],orange:['#f59e0b','Récupération'],violet:['#64748b','Nutrition / rappel'],jaune:['#94a3b8','Descente active'],rouge:['#ef4444','Effort chrono']};
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
hydrateLogs();hydrateOverrides();try{_ckRebuild();}catch(e){console.warn('_ckRebuild',e);}initQuickLog();initCreneaux();initSessionMenu();initInstall();initVersionPanel();initFormeHelp();initCkHelp();initCoach();renderHeader();renderPlan();rwAuto();setTimeout(checkAutoSync,800);
if('serviceWorker'in navigator)navigator.serviceWorker.register('./sw.js').catch(()=>{});

if(typeof window!=='undefined'){window.addEventListener('load',function(){setTimeout(function(){try{_revealScan()}catch(e){}},350)});}
