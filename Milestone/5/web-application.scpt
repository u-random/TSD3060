
function constructLoginXML(formData) {
    let email = formData.get('email');
    let password = formData.get('password');
    return `<login><email>${email}</email><password>${password}</password></login>`;
}

function constructLoginXML(formData) {
    let email = formData.get('email');
    let password = formData.get('password');
    return `<login><email>${email}</email><password>${password}</password></login>`;
}

function constructLoginXML(formData) {
    let email = formData.get('email');
    let password = formData.get('password');
    return `<login><email>${email}</email><password>${password}</password></login>`;
}
















function addDikt(title) {
    // XML format for the request
    var xmlData = '<dikt><title>' + title + '</title></dikt>';

    // API endpoint
    var apiUrl = 'http://192.168.10.200:8180/dikt/add';

    // Using Fetch API to send the request
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/xml', // Assuming the API expects XML data
        },
        body: xmlData
    })
    .then(response => response.text())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}



function getDikt() {
    // TODO: Make an XMLHttpRequest or fetch request here to communicate with the REST API
    // TODO: Handle the response from the server and update the UI accordingly
	fetch('your_REST_API_endpoint_here')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Process the data received from the server
            // Update the UI with the retrieved poems
            console.log('Poems data:', data);
        })
        .catch(error => {
            // Handle any errors that occur during the fetch request
            console.error('Error fetching poems:', error);
        });
}

// Define a function to handle the service worker functionality
function setupServiceWorker() {
    // Implement the service worker logic here
    // Cache all the necessary files and poems from the database
}

// Call the functions to start the required processes
fetchPoems(); // Call this function when the application loads to fetch the poems from the database


// Check if the browser supports service workers and then set up the service worker accordingly
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
                setupServiceWorker();
            })
            .catch(err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}                               jscr  
��ޭ
