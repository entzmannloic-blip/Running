/* Service worker — genere par src/build.py (ne pas copier a la main : 236 et [
 "./",
 "./index.html",
 "./manifest.json",
 "./icon-180.png",
 "./icon-192.png",
 "./icon-512.png",
 "./src/app.js",
 "./data/changelog.json",
 "./data/historique.json",
 "./data/meta.json",
 "./data/plan.json",
 "./data/seances.json"
]
   sont remplaces). Le nom du cache suit le numero de build : un nouveau build = nouveau cache,
   les anciens (dont plan-v34) sont supprimes a l'activation. */
const BUILD='236';
const CACHE='plan-'+BUILD;
const SHELL=[
 "./",
 "./index.html",
 "./manifest.json",
 "./icon-180.png",
 "./icon-192.png",
 "./icon-512.png",
 "./src/app.js",
 "./data/changelog.json",
 "./data/historique.json",
 "./data/meta.json",
 "./data/plan.json",
 "./data/seances.json"
];
const TIMEOUT_MS=3000;

self.addEventListener('install',e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()));
});

self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys()
    .then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k))))
    .then(()=>self.clients.claim()));
});

/* RESEAU D'ABORD (toujours la derniere version en ligne), avec repli sur le cache si le reseau
   echoue ou met plus de 3 s a repondre (4G degradee). La reponse reseau met le cache a jour
   meme quand le cache a deja repondu. */
function fromCache(req){
  return caches.match(req,{ignoreSearch:true}).then(m=>m||(req.mode==='navigate'?caches.match('./index.html'):undefined));
}
function networkFirst(req){
  return new Promise(resolve=>{
    let done=false;
    const timer=setTimeout(()=>{
      fromCache(req).then(m=>{if(m&&!done){done=true;resolve(m);}});
    },TIMEOUT_MS);
    fetch(req,{cache:'no-store'}).then(r=>{
      clearTimeout(timer);
      if(r&&r.status===200){const cp=r.clone();caches.open(CACHE).then(c=>c.put(req,cp));}
      if(!done){done=true;resolve(r);}
    }).catch(()=>{
      clearTimeout(timer);
      if(!done){done=true;fromCache(req).then(m=>resolve(m||Response.error()));}
    });
  });
}

self.addEventListener('fetch',e=>{
  const url=new URL(e.request.url);
  // Ne pas intercepter : requetes non-GET et cross-origin (ex. API meteo Open-Meteo)
  if(e.request.method!=='GET'||url.origin!==location.origin)return;
  e.respondWith(networkFirst(e.request));
});
