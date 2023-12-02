const CACHE_NAME = 'dikt-cache-v1';
const urlsToCache = [
    '/',
    '/style.css',
    '/dikt_dashboard_local.html',
    // add other URLs to cache
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', function(event) {
    const url = new URL(event.request.url);

    // Check if the request is for the RestAPI
    if (url.pathname.startsWith('/dikt')) {
        event.respondWith(
            caches.open(CACHE_NAME).then(function(cache) {
                // Fetch the dikts from the network
                return fetch(event.request).then(function(networkResponse) {
                    // Clone the response
                    let responseToCache = networkResponse.clone();

                    // Put the cloned response in the cache
                    cache.put(event.request, responseToCache);

                    // Serve the original response to the browser
                    return networkResponse;
                });
            })
        );
    } else {
        // For other requests, try to serve from the cache, and if not in the cache, fetch from the network
        event.respondWith(
            caches.match(event.request)
                .then(function(response) {
                    if (response) {
                        return response;
                    }
                    return fetch(event.request);
                })
        );
    }
});

// Delete one of these:
self.addEventListener('fetch', function(event) {
    const url = new URL(event.request.url);

    // Check if the request is for the RestAPI
    if (url.pathname.startsWith('/dikt')) {
        event.respondWith(
            caches.open(CACHE_NAME).then(function(cache) {
                return cache.match(event.request).then(function(response) {
                    if (response) {
                        // If the response is in the cache, serve it
                        return response;
                    } else {
                        // If the response is not in the cache, fetch it from the network
                        return fetch(event.request).then(function(networkResponse) {
                            // Clone the response
                            let responseToCache = networkResponse.clone();

                            // Put the cloned response in the cache
                            cache.put(event.request, responseToCache);

                            // Serve the original response to the browser
                            return networkResponse;
                        });
                    }
                });
            })
        );
    } else {
        // For other requests, try to serve from the cache, and if not in the cache, fetch from the network
        event.respondWith(
            caches.match(event.request)
                .then(function(response) {
                    if (response) {
                        return response;
                    }
                    return fetch(event.request);
                })
        );
    }
});

self.addEventListener('activate', function(event) {
    var cacheWhitelist = ['dikt-cache-v1'];
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheWhitelist.indexOf(cacheName) === -1) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});