document.getElementById('startSchedulerButton').addEventListener('click', function() {
  chrome.runtime.sendMessage({ action: "startTimer" }, (response) => {
      console.log(response.status);
  });
});

document.getElementById('stopSchedulerButton').addEventListener('click', function() {
  chrome.runtime.sendMessage({ action: "stopTimer" }, (response) => {
      console.log(response.status);
      var timerDisplay = document.getElementById('timer');
      timerDisplay.textContent = ''; // Clear the timer display
  });
});

// Update the timer display when receiving messages from the background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "updateTimer") {
      var timerDisplay = document.getElementById('timer');
      timerDisplay.textContent = request.timeString;
  }
});

let captchaInterval;

// Function to fetch CAPTCHA image from the server and display it
function fetchAndDisplayCaptchaImage() {
  fetch("http://localhost:5000/captcha_image")
      .then(response => response.blob())
      .then(blob => {
          const captchaImage = document.getElementById("captchaImage");
          captchaImage.src = URL.createObjectURL(blob);
          captchaImage.style.display = "block";
      })
      .catch(error => console.error("Error fetching CAPTCHA image:", error));
}

// Function to start the CAPTCHA refresh interval
function startCaptchaRefresh() {
  fetchAndDisplayCaptchaImage(); // Immediately fetch a new CAPTCHA when starting
  captchaInterval = setInterval(fetchAndDisplayCaptchaImage, 5000);
}

// Function to stop the CAPTCHA refresh interval
function stopCaptchaRefresh() {
  if (captchaInterval) {
    clearInterval(captchaInterval);
  }
}


// Event listener for visibility change
document.addEventListener('visibilitychange', function() {
  if (document.visibilityState === 'visible') {
      startCaptchaRefresh();
  } else {
      stopCaptchaRefresh();
  }
});

// Fetch and display CAPTCHA image and start refresh when the page loads
window.addEventListener("load", () => {
  startCaptchaRefresh();
});

// Submit CAPTCHA text to server
function submitCaptchaText() {
  const captchaInput = document.getElementById("captchaInput").value;
  if (!captchaInput) {
    console.error("Captcha input is empty");
    return;
  }
  fetch("http://localhost:5000/captcha_input", {
      method: "POST",
      headers: {
          "Content-Type": "application/json"
      },
      body: JSON.stringify({
          captcha_input: captchaInput
      })
  })
  .then(response => {
      if (response.ok) {
          console.log("CAPTCHA input submitted successfully");
      } else {
          console.error("Error submitting CAPTCHA input:", response.statusText);
      }
  })
  .catch(error => console.error("Error submitting CAPTCHA input:", error));
}

// Event listener for submitting CAPTCHA text
document.getElementById("submitCaptchaButton").addEventListener("click", () => {
  submitCaptchaText();
});
