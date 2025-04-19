import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging.js";

const firebaseConfig = {
    apiKey: "AIzaSyC83xNvqQqAb5NlGkMAHg0-myQw0Wx9o1Y",
    authDomain: "quickserve-bea56.firebaseapp.com",
    projectId: "quickserve-bea56",
    storageBucket: "quickserve-bea56.appspot.com",
    messagingSenderId: "408249548434",
    appId: "1:408249548434:web:8ab995fb5b4df7364bb04b",
    measurementId: "G-HFR9FQ4N0H"
};

const firebaseApp = initializeApp(firebaseConfig);
const messaging = getMessaging(firebaseApp);

async function requestNotificationPermission() {
    try {
        const permission = await Notification.requestPermission();
        if (permission === "granted") {
            console.log("Notification permission granted.");
            getFCMToken();
        } else {
            console.warn("Please give notification permission.");
        }
    } catch (error) {
        console.error("Error while requesting notification permission");
    }
}

async function getFCMToken() {
    try {
        const currentToken = await getToken(messaging, { vapidKey: "BHWRPMYFEEQ7qnfU7tfXHH4QPk9_2rSSyv0-XvdgayxKhTPY_5gk01H9K1MGELgkCbRgzGI8DqD2H_QUhkbs67k" });

        if (currentToken) {
            console.log("FCM Token generated:", currentToken);
            const isEmployee = await checkUserRole();
            if (isEmployee) {
                sendTokenToBackend(currentToken);
            } else {
                console.warn("User does not have the required role.");
            }
        } else {
            console.warn("No registration token available.");
        }
    } catch (error) {
        console.error(" Error getting FCM token:", error);
    }
}

function getCSRFToken() {
    const cookieValue = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];

    return cookieValue || "";
}

async function checkUserRole() {
    try {
        const csrfToken = getCSRFToken();

        const response = await fetch("/check-user-role/", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            }
        });

        const data = await response.json();
        return data.is_employee;
    } catch (error) {
        console.error("Error checking user role:", error);
        return false;
    }
}

async function sendTokenToBackend(token) {
    try {
        const csrfToken = getCSRFToken();

        const response = await fetch("/update-fcm-token/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ fcm_token: token })
        });

        const data = await response.json();
        console.log("Token sent successfully:", data);
    } catch (error) {
        console.error("Error sending token to backend:", error);
    }
}

if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/firebase-messaging-sw.js')
        .then(function (registration) {
            console.log("Service Worker registered with scope:", registration.scope);
        }).catch(function (error) {
            console.log("Service Worker registration failed:", error);
        });
}

onMessage(messaging, (payload) => {
    console.log("Foreground message received:", payload);
    console.log("Click Action URL:", payload.data.click_action);
    const notificationTitle = payload.notification?.title || "New Notification";
    const notificationOptions = {
        body: payload.notification?.body || "You have a new update.",
        icon: payload.notification?.icon || "/default-icon.png",
        data: payload.data,
    };

    if (Notification.permission === "granted") {
        const notification = new Notification(notificationTitle, notificationOptions);

        notification.onclick = (event) => {
            event.preventDefault();
            const url = payload.data?.click_action;
            console.log("Redirecting to:", url)
            if(url) {
                window.location.href = url;
            } else {
                console.warn("No valid click_action found, redirecting to dashboard.")
                window.location.href = "/employee/employee_dashboard/";
            }
        };
    } else {
        console.warn("Notification permission not granted.");
    }
});

document.addEventListener("DOMContentLoaded", requestNotificationPermission);