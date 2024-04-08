var timerInterval;

    document.getElementById('startSchedulerButton').addEventListener('click', function() {
      var captchaInput = document.getElementById('captchaInput').value;
      if (captchaInput.trim() === "") {
        // If CAPTCHA field is empty, show error message and vibrate
        var timerDisplay = document.getElementById('timer');
        timerDisplay.textContent = 'Captcha not entered!';
        navigator.vibrate(200); // Vibrate for 200 milliseconds
        setTimeout(function() {
          timerDisplay.textContent = ''; // Clear the error message after 2 seconds
        }, 2000);
      } else {
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
      }
    });

    document.getElementById('stopSchedulerButton').addEventListener('click', function() {
      clearInterval(timerInterval); // Stop the timer
      var timerDisplay = document.getElementById('timer');
      timerDisplay.textContent = ''; // Clear the timer display
    });

    function pad(num) {
      return num < 10 ? '0' + num : num;
    }