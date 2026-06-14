const data=require("./data.json");
global.SEMAINES=data.SEMAINES;global.HIST=data.HIST;global.POLAR=data.POLAR;global.GEAR=data.GEAR;
global.PHASES=data.PHASES;global.COUL=data.COUL;global.RACES=data.RACES;global.RECORDS=data.RECORDS;
global.PROFIL=data.PROFIL;global.PROJ=data.PROJ;global.VIGILANCE=data.VIGILANCE;global.S24R=data.S24R;global.ALLURES=data.ALLURES;global.ZONES_FC=data.ZONES_FC;global.ALLURES_COURSE=data.ALLURES_COURSE;global.MONTHLY=data.MONTHLY;global.SAISON2026=data.SAISON2026;global.ACWR_DATA=data.ACWR_DATA;global.RECORDS_PERF=data.RECORDS_PERF;global.JOURNAL=data.JOURNAL;global.REWINDS=data.REWINDS;global.MAJ=data.MAJ;global.HEATMAP=data.HEATMAP;global.localStorage={setItem(){},getItem(){return null}};global.SEANCES_BY_WEEK=data.SBW;
const stub={addEventListener(){},classList:{add(){},remove(){},toggle(){return false}},style:{},scrollTop:0,set innerHTML(v){},get innerHTML(){return""},textContent:"",appendChild(){}};
global.document={getElementById:()=>stub,addEventListener(){},body:{classList:{toggle(){return false},add(){}},style:{}},createElement:()=>stub,documentElement:{style:{setProperty(){}}}};
global.window={scrollTo(){}};
let app=require("fs").readFileSync("app.js","utf8").replace(/renderHeader\(\);renderPlan\(\);\s*$/,"");
eval(app);
console.log("isoWeek 2026-06-10 :",isoWeek(new Date("2026-06-10")));
console.log("svgMountain :",svgMountain().length,"car");
console.log("svgDonut :",svgDonut([{label:"a",val:8,color:"#86efac"},{label:"b",val:43,color:"#22c55e"},{label:"c",val:43,color:"#f59e0b"},{label:"d",val:5,color:"#ef4444"}]).length,"car");
console.log("chartLine km :",chartLine(HIST.map(h=>h.km),{color:"#3b82f6",labels:HIST.map(h=>h.sem)}).length,"car");
console.log("chartLine easy(nulls):",chartLine(HIST.map(h=>h.easy_pace),{color:"#22c55e",fmtY:v=>paceFmt(v)}).length,"car");
console.log("renderHeader :",(typeof renderHeader),"| renderDash :",(typeof renderDash),"| ouvrirSemaine :",(typeof ouvrirSemaine));
renderHeader();renderDash();ouvrirSemaine(25);ouvrirSemaine(24);ouvrirSeance(42,4);
console.log("Toutes les fonctions de rendu s'exécutent sans erreur ✓");
ouvrirSeanceS24(0);ouvrirSeanceS24(1);ouvrirSeanceS24(2);
console.log("Fiches S24 OK ✓ | chart 16km:",s24Chart(S24R.runs[0].splits).length,"car");

// --- Item 4 : test du recalcul de la projection marathon ---
const baseProj=marathonProjection();
console.log("Projection (0 séance qualité) :",_s2hm(baseProj.sec),"| n =",baseProj.n,"| =base:",Math.round(baseProj.sec)===PROJ.base);
// On logue un test 10 km à 4:30/km (très bonne forme) -> la projection doit s'améliorer
const wk31=SEANCES_BY_WEEK["31"];const testSe=wk31.find(s=>s.type==="Test / recalibrage");
testSe.realise={statut:"fait",km:"10",temps:"45:00",allure:"4:30/km"};
const p2=marathonProjection();
console.log("Après test 10 km 45:00 loggué :",_s2hm(p2.sec),"| n =",p2.n,"| trend pts =",p2.trend.length);
console.log("Recalcul effectif (projection a bougé) :", Math.round(p2.sec)!==Math.round(baseProj.sec) && p2.n===1);
delete testSe.realise; testSe.realise={statut:"a_faire"};
console.log("Boule de cristal rendue :", renderCrystalBall().length>500 ? "OK ("+renderCrystalBall().length+" car)" : "FAIL");
