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
