var timerInterval;

    document.getElementById('startSchedulerButton').addEventListener('click', function() {
      // var captchaInput = document.getElementById('captchaInput').value;
      // if (captchaInput.trim() === "") {
      //   // If CAPTCHA field is empty, show error message and vibrate
      //   var timerDisplay = document.getElementById('timer');
      //   timerDisplay.textContent = 'Captcha not entered!';
      //   navigator.vibrate(200); // Vibrate for 200 milliseconds
      //   setTimeout(function() {
      //     timerDisplay.textContent = ''; // Clear the error message after 2 seconds
      //   }, 2000);
      // } else {
        // If CAPTCHA field is not empty, start the timer
        var startTime = new Date().getTime();
        var timerDisplay = document.getElementById('timer');
        timerInterval = setInterval(function() {
          var currentTime = new Date().getTime();
          var elapsedTime = currentTime - startTime;
          var hours = Math.floor(elapsedTime / (1000 * 60 * 60));
          var minutes = Math.floor((elapsedTime % (1000 * 60 * 60)) / (1000 * 60));
          var seconds = Math.floor((elapsedTime % (1000 * 60)) / 1000);
          timerDisplay.textContent = 'Session: ' + pad(hours) + ':' + pad(minutes) + ':' + pad(seconds);
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
    });

    document.getElementById('stopSchedulerButton').addEventListener('click', function() {
      clearInterval(timerInterval); // Stop the timer
      var timerDisplay = document.getElementById('timer');
      timerDisplay.textContent = ''; // Clear the timer display
    });

    function pad(num) {
      return num < 10 ? '0' + num : num;
    }

// Fetch CAPTCHA image from server and display it
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

// Submit CAPTCHA text to server
function submitCaptchaText() {
  const captchaInput = document.getElementById("captchaInput").value;
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

// Fetch and display CAPTCHA image when the page loads
window.addEventListener("load", () => {
  fetchAndDisplayCaptchaImage();
});

// Event listener for submitting CAPTCHA text
document.getElementById("submitCaptchaButton").addEventListener("click", () => {
  submitCaptchaText();
});
