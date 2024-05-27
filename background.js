let timerInterval;
let startTime;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "startTimer") {
        startTime = new Date().getTime();
        timerInterval = setInterval(() => {
            const currentTime = new Date().getTime();
            const elapsedTime = currentTime - startTime;
            const hours = Math.floor(elapsedTime / (1000 * 60 * 60));
            const minutes = Math.floor((elapsedTime % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((elapsedTime % (1000 * 60)) / 1000);
            
            const timeString = `Session: ${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
            chrome.storage.local.set({ timer: timeString });
            chrome.runtime.sendMessage({ action: "updateTimer", timeString: timeString });
        }, 1000);

        fetch("http://localhost:5000/start_process", {
            method: "GET"
        })
        .then(response => {
            if (response.ok) {
                console.log("Process started successfully");
            } else {
                console.error("Error starting process:", response.statusText);
            }
        })
        .catch(error => console.error("Error starting process:", error));

        sendResponse({ status: "started" });
    } else if (request.action === "stopTimer") {
        clearInterval(timerInterval);
        chrome.storage.local.remove("timer");
        sendResponse({ status: "stopped" });
    }
    return true;
});

function pad(num) {
    return num < 10 ? '0' + num : num;
}
