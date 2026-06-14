const CACHE='plan-v16';
const SHELL=['./','./index.html','./manifest.json','./icon-192.png','./icon-512.png'];

self.addEventListener('install',e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()));
});

self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});

self.addEventListener('fetch',e=>{
  const url=new URL(e.request.url);
  // .fit : réseau en priorité (téléchargement direct), cache en fallback
  if(url.pathname.endsWith('.fit')){
    e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)));
    return;
  }
  // shell (index.html, icons, manifest) : cache en priorité, màj en arrière-plan (stale-while-revalidate)
  if(SHELL.some(s=>url.pathname.endsWith(s.replace('./','')))||url.pathname==='/'){
    e.respondWith(caches.open(CACHE).then(c=>c.match(e.request).then(cached=>{
      const fresh=fetch(e.request).then(r=>{c.put(e.request,r.clone());return r;});
      return cached||fresh;
    })));
    return;
  }
  // reste : réseau
  e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)));
});
