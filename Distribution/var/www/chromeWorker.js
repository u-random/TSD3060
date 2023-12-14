/*
 Copyright 2016 Google Inc. All Rights Reserved.
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 */

// Modified by me to allow for cross-origin requests and to do network first caching

// Names of the two caches used in this version of the service worker.
// Change to v2, etc. when you update any of the local resources, which will
// in turn trigger the installation event again.
const PRECACHE = 'precache-v1';
const RUNTIME = 'runtime';

// Milestone 5.3: Service worker skal cache alle filene den trenger
// A list of local resources we always want to be cached.
const PRECACHE_URLS = [
    'index.html',
    './', // Alias for index.html
    'style.css',
    'dikt_dashboard_local.html',
    'http://localhost:8280/dikt'
];


// The installation handler takes care of precaching the resources we always need.
self.addEventListener('install', event => {
    // Browser should wait until the promise is resolved
    event.waitUntil(
        // Open the cache
        caches.open(PRECACHE)
            // Add all the files to the cache
            .then(cache => cache.addAll(PRECACHE_URLS))
            // Forces the waiting service worker to become the active service worker
            // Bypass waiting state and immediately activate the new service worker
            .then(self.skipWaiting())
    );
});


// The activate handler takes care of cleaning up old caches.
self.addEventListener('activate', event => {
    // Create a list of caches that should not be deleted
    const currentCaches = [PRECACHE, RUNTIME];
    // Browser should wait until the promise is resolved
    event.waitUntil(
        // Get all the cache keys (names)
        caches.keys().then(cacheNames => {
            // Filter the list of cache keys (names) and return the ones that should be deleted
            return cacheNames.filter(cacheName => !currentCaches.includes(cacheName));
            // Delete all the caches that should be deleted
        }).then(cachesToDelete => {
            // Promise.all() takes an array of promises and waits on them all to settle (either resolve or reject)
            // before returning a promise that resolves to an array of the results of the input promises.
            // If any of the input promises reject, the returned promise will reject with the same reason.
            return Promise.all(cachesToDelete.map(cacheToDelete => {
                // Delete the cache
                return caches.delete(cacheToDelete);
            }));
            // Wait for all the caches to be deleted
            // Updates take effect immediately,
            // but the old service worker won't be gone until all tabs that use it are closed.
        }).then(() => self.clients.claim())
    );
});


// The fetch handler serves responses for same-origin AND cross-origin resources from a cache.
// If no response is found, it populates the runtime cache with the response
// from the network before returning it to the page.
self.addEventListener('fetch', event => {

    // Parse the URL of the request
    const url = new URL(event.request.url);

    // Only cache GET requests and exclude /isloggedin path
    if (event.request.method !== 'GET' || url.pathname === '/isloggedin') {
        return;
    }
    // Determine if the request is for a same-origin or cross-origin resource
    const isSameOrigin = url.origin === self.location.origin;

    // If the request is for a same-origin resource, do standard strategy
    if (isSameOrigin) {
        console.log('Same origin requested: ', url.pathname );
        // Handle same-origin requests as before
        event.respondWith(
            // Open the runtime cache and look for a cached response
            caches.open(RUNTIME).then(cache => {
                // First, try to fetch the request from the network
                return fetch(event.request).then(networkResponse => {
                    // Cloning the response before caching it, as the response is a stream
                    // and its body can only be consumed once.
                    // Milestone 5.4: Cache alle dikt i Databasen
                    cache.put(event.request, networkResponse.clone()).catch(err => {
                        // Handle error during cache storage
                        console.error('Cache put failed: ', err);
                    });
                    console.log('Serving from network');
                    // Return the network response
                    return networkResponse;
                }).catch(() => {
                    // If network request fails, try to serve from cache
                    return cache.match(event.request).then(cachedResponse => {
                        // If no cached response is found, return a default response
                        if (cachedResponse) {
                            console.log('Serving from cache');
                            return cachedResponse;
                        }
                        
                    });
                });
            })
        );
    } else { // If the request is for a cross-origin resource, do CORS strategy
        console.log('Cross origin requested:', url.pathname );
        // Handle cross-origin requests
        event.respondWith(
            // Open the runtime cache and look for a cached response
            caches.open(RUNTIME).then(cache => {
                // First, try to fetch the request from the network
                return fetch(event.request, { mode: 'cors' }).then(networkResponse => {
                    // Clone the response before caching it, as the response is a stream
                    // and its body can only be consumed once.
                    cache.put(event.request, networkResponse.clone()).catch(err => {
                        // Handle error during cache storage
                        console.error('Cache put failed: ', err);
                    });
                    console.log('Serving CORS from network');
                    // Return the network response
                    return networkResponse;
                }).catch(() => {
                    // If network request fails, try to serve from cache
                    return cache.match(event.request).then(cachedResponse => {
                        // If no cached response is found, return a default response
                        if (cachedResponse) {
                            console.log('Serving CORS from cache');
                            return cachedResponse;
                        }
                        
                    });
                });
            })
        );
    }
});

