const CACHE='plan-v34';
const SHELL=['./','./index.html','./manifest.json','./icon-192.png','./icon-512.png'];

self.addEventListener('install',e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()));
});

self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys()
    .then(ks=>Promise.all(ks.map(k=>caches.delete(k))))
    .then(()=>self.clients.claim()));
});

self.addEventListener('fetch',e=>{
  const url=new URL(e.request.url);
  // Ne pas intercepter : requêtes non-GET et cross-origin (ex. API météo Open-Meteo)
  if(e.request.method!=='GET'||url.origin!==location.origin)return;
  // RÉSEAU D'ABORD, sans cache HTTP navigateur : toujours la dernière version en ligne, cache en secours hors-ligne
  e.respondWith(
    fetch(e.request,{cache:'no-store'}).then(r=>{
      // on garde le shell en cache pour le mode hors-ligne
      if(url.pathname.endsWith('/')||SHELL.some(s=>url.pathname.endsWith(s.replace('./','')))){
        const cp=r.clone();caches.open(CACHE).then(c=>c.put(e.request,cp));
      }
      return r;
    }).catch(()=>caches.match(e.request).then(m=>m||caches.match('./index.html')))
  );
});
