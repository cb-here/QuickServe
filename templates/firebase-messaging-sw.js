importScripts("https://www.gstatic.com/firebasejs/9.6.1/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging-compat.js");

const firebaseConfig = {
    apiKey: "AIzaSyC83xNvqQqAb5NlGkMAHg0-myQw0Wx9o1Y",
    authDomain: "quickserve-bea56.firebaseapp.com",
    projectId: "quickserve-bea56",
    storageBucket: "quickserve-bea56.appspot.com",
    messagingSenderId: "408249548434",
    appId: "1:408249548434:web:8ab995fb5b4df7364bb04b",
    measurementId: "G-HFR9FQ4N0H"
};

firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
    console.log("📩 Background message received:", payload);

    const notificationTitle = payload.notification?.title || "New Booking";
    const notificationOptions = {
        body: payload.notification?.body || "Tap to view details",
        icon: payload.notification?.icon || "/default-icon.png",
        data: payload.data  // Store data for handling clicks
    };

    return self.registration.showNotification(notificationTitle, notificationOptions);
});

self.addEventListener("notificationclick", function (event) {
    event.notification.close();

    // Get the `click_action` from notification data
    const url = event.notification.data?.click_action || "/employee/employee_dashboard/";

    event.waitUntil(
        clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
            for (let client of clientList) {
                if (client.url.includes(url) && "focus" in client) {
                    return client.focus();
                }
            }
            return clients.openWindow(url);
        })
    );
});
