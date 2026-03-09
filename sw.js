const CACHE_NAME = 'ascun-v1';
const ASSETS = [
    './index.html',
    './data.json'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(ASSETS))
    );
});

self.addEventListener('fetch', (event) => {
    // Para data.json, intentamos red primero para tener siempre los datos más frescos
    if (event.request.url.includes('data.json')) {
        event.respondWith(
            fetch(event.request)
                .then(networkResponse => {
                    // Actualizar cache con la data fresca
                    const responseClone = networkResponse.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseClone));
                    return networkResponse;
                })
                .catch(() => caches.match(event.request))
        );
    } else {
        event.respondWith(
            caches.match(event.request)
                .then(response => response || fetch(event.request))
        );
    }
});

let shownMatchTitles = new Set();

async function checkMatchesAndNotify() {
    try {
        const response = await fetch('./data.json');
        const matches = await response.json();

        const now = new Date();
        const todayStr = now.toISOString().split('T')[0]; // YYYY-MM-DD

        matches.forEach(match => {
            if (match.start) {
                const matchDateStr = match.start.split('T')[0];

                // Si el partido es HOY y no hemos notificado sobre él
                if (matchDateStr === todayStr && !shownMatchTitles.has(match.title)) {
                    shownMatchTitles.add(match.title);

                    self.registration.showNotification(`⚽ PARTIDO HOY: ${match.title}`, {
                        body: `No te lo pierdas a las ${match.start.split('T')[1].substring(0, 5)} en ${match.location}`,
                        icon: 'https://bogotaclausura2610.ascundeportes.org/uploads/c8ddd89739431c7edb933831ce2c89bd23f1e0f7.jpg',
                        vibrate: [300, 100, 300, 100, 300],
                        tag: match.title, // Evita notificaciones duplicadas del mismo partido en el sistema
                        requireInteraction: true
                    });
                }
            }
        });
    } catch (e) {
        console.error("Error comprobando partidos para notificar", e);
    }
}

// Check every time the SW wakes up or is activated
self.addEventListener('activate', (event) => {
    event.waitUntil(checkMatchesAndNotify());
});

// Since rigorous background sync requires special permissions, 
// we also piggyback on fetch events (when user browses) to do a check.
self.addEventListener('fetch', (event) => {
    if (event.request.mode === 'navigate') {
        checkMatchesAndNotify();
    }
});
