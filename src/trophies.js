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
