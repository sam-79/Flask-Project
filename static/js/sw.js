// simple pwa config

var cacheVersion = new Date().getTime();
var staticCacheName = "onlinetools-v" + cacheVersion

var filesToCache = [
    '/offline',
    '/favicon.ico',
    '/static/images/icons/icon-72x72.png',
    '/static/images/icons/icon-96x96.png',
    '/static/images/icons/icon-128x128.png',
    '/static/images/icons/icon-144x144.png',
    '/static/images/icons/icon-152x152.png',
    '/static/images/icons/icon-192x192.png',
    '/static/images/icons/icon-384x384.png',
    '/static/images/icons/icon-512x512.png',
    'https://fonts.googleapis.com/css2?family=El+Messiri:wght@600&display=swap'
];

// Cache on install
self.addEventListener("install", event => {
  this.skipWaiting();
  event.waitUntil(
    caches.open(staticCacheName)
      .then(cache => {
        return cache.addAll(filesToCache);
      })
  )
});

// Clear cache on activate
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(cacheName => (cacheName.startsWith("onlinetools-")))
          .filter(cacheName => (cacheName !== staticCacheName))
          .map(cacheName => caches.delete(cacheName))
      );
    })
  );
});

// Serve from cache, and return offline page if client is offline 
this.addEventListener('fetch', event => {
  if (event.request.mode === 'navigate' || (event.request.method === 'GET' && event.request.headers.get('accept').includes('text/html'))) {
    event.respondWith(
      fetch(event.request.url).catch(error => {
        return caches.match('/offline');
      })
    );
  } else{
    event.respondWith(caches.match(event.request)
        .then(function (response) {
        return response || fetch(event.request);
      })
    );
  }
});

// Register Service Worker
if('serviceWorker' in navigator){
  window.addEventListener('load',() => {
    navigator.serviceWorker.register("/service-worker.js")
    .then(reg=>{console.log('registered '+reg.scope);})
    .catch(regErr => {console.log('error'+regErr);});
  });  
}
