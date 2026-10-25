// Road to 3 Plates, offline support. Change VERSION whenever index.html changes.
const VERSION = 'r3p-v23';
const OWN = 'r3p-'; // only ever clean up this app's own caches: the other builds share this origin
const HOME = new URL('./', self.location).pathname; // this app's own folder
const SHELL = ['./', './index.html', './manifest.webmanifest', './icon-180.png', './icon-192.png', './icon-512.png'];
const CACHE_HOSTS = ['raw.githubusercontent.com'];
self.addEventListener('install', (e) => { e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', (e) => { e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== VERSION && k.indexOf(OWN) === 0).map((k) => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', (e) => {
  const req = e.request; if (req.method !== 'GET') return; const url = new URL(req.url);
  if (CACHE_HOSTS.includes(url.hostname)) {
    // Exercise photos: cache first, so they still show offline at the gym.
    e.respondWith(caches.match(req).then((hit) => hit || fetch(req).then((res) => { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); return res; }).catch(() => hit)));
    return;
  }
  if (url.origin !== self.location.origin) return;
  // Files in a sub-folder (like shayan/) belong to another copy of the app. Leave them to that copy's own worker.
  if (!url.pathname.startsWith(HOME) || url.pathname.slice(HOME.length).includes('/')) return;
  if (url.pathname.endsWith('/logs.json')) { e.respondWith(fetch(req).catch(() => caches.match(req))); return; }
  if (req.mode === 'navigate') { e.respondWith(fetch(req).then((res) => { const copy = res.clone(); caches.open(VERSION).then((c) => c.put('./index.html', copy)); return res; }).catch(() => caches.match('./index.html'))); return; }
  e.respondWith(caches.match(req).then((hit) => hit || fetch(req).then((res) => { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); return res; })));
});
