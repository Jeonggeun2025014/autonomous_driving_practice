const CACHE_NAME = 'remote-controller-v1';
const ASSETS = [
  '/',
  '/src/autonomous_driving_practice/remote_controller/index.html',
  '/src/autonomous_driving_practice/remote_controller/styles.css',
  '/src/autonomous_driving_practice/remote_controller/app.js'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(ASSETS)));
});

self.addEventListener('fetch', (e) => {
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
