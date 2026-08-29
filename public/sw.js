const CACHE='ol-quiz-v2';
const ASSETS=['./','./index.html','./data/courses.json','./manifest.webmanifest','./icon-192.png','./icon-512.png','./icon-maskable-512.png','./apple-touch-icon.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting()).catch(()=>{}));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  // pagina e file delle domande: network-first, così gli aggiornamenti arrivano
  // anche senza bump di CACHE. Offline si ricade sulla copia in cache.
  const url=new URL(e.request.url);
  const isPage = e.request.mode==='navigate' || e.request.destination==='document';
  const isData = url.origin===self.location.origin && url.pathname.includes('/data/');
  if(isPage || isData){
    e.respondWith(
      fetch(e.request).then(resp=>{
        const copy=resp.clone(); caches.open(CACHE).then(c=>c.put(e.request,copy)).catch(()=>{});
        return resp;
      }).catch(()=> caches.match(e.request).then(r=> r || caches.match('./index.html')))
    );
    return;
  }
  // icone, manifest e altri asset statici: cache-first
  e.respondWith(
    caches.match(e.request).then(r=> r || fetch(e.request).then(resp=>{
      const copy=resp.clone(); caches.open(CACHE).then(c=>c.put(e.request,copy)).catch(()=>{});
      return resp;
    }).catch(()=> caches.match('./index.html')))
  );
});
