/* Service worker — Fundación Reserva para la Infancia
   -------------------------------------------------------------------------
   Estrategia deliberadamente conservadora, pensada para que el equipo del
   colegio pueda actualizar el sitio sin pelear con la caché del navegador:

   · HTML, CSS y JS  → red primero, caché solo como respaldo sin conexión.
     (Si publicas un cambio, se ve de inmediato.)
   · Imágenes        → caché primero, con actualización en segundo plano.
     (Son las que más pesan y las que menos cambian.)

   Sube el número de VERSION cada vez que hagas un despliegue grande. */
const VERSION = 'fri-v2';

const OFFLINE_PAGES = [
  './',
  'index.html',
  'nosotros.html',
  'proyecto-educativo.html',
  'niveles.html',
  'vida-escolar.html',
  'admisiones.html',
  'noticias.html',
  'contacto.html',
  '404.html',
  'assets/css/style.css',
  'assets/js/main.js',
  'assets/img/logo.svg'
];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(VERSION)
      .then(function (c) { return c.addAll(OFFLINE_PAGES); })
      .then(function () { return self.skipWaiting(); })
      .catch(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys()
      .then(function (keys) {
        return Promise.all(keys.map(function (k) {
          return k === VERSION ? null : caches.delete(k);
        }));
      })
      .then(function () { return self.clients.claim(); })
  );
});

function putInCache(req, res) {
  var copy = res.clone();
  caches.open(VERSION).then(function (c) { c.put(req, copy); });
  return res;
}

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;

  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // fuentes y mapas: sin interceptar

  var isImage = req.destination === 'image' || /\.(svg|png|jpe?g|webp|avif|gif|ico)$/i.test(url.pathname);

  // Imágenes: caché primero, refresco en segundo plano.
  if (isImage) {
    e.respondWith(
      caches.match(req).then(function (hit) {
        var network = fetch(req).then(function (res) { return putInCache(req, res); }).catch(function () { return hit; });
        return hit || network;
      })
    );
    return;
  }

  // Documentos, hojas de estilo y scripts: red primero.
  e.respondWith(
    fetch(req)
      .then(function (res) { return putInCache(req, res); })
      .catch(function () {
        return caches.match(req).then(function (hit) {
          if (hit) return hit;
          if (req.mode === 'navigate') return caches.match('404.html');
          return Response.error();
        });
      })
  );
});
