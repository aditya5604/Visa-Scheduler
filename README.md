# Setting Up Visa-Scheduler Chrome Extension:



https://github.com/AashishKumar-3002/Visa-Scheduler/assets/110625812/7d886754-f190-4330-a4e8-1a3b325cfe70


To watch the video demo, navigate to the `statics` folder of your local copy of the repository and open the file named `demo_extension.mp4`.

To set up Visa-Scheduler, follow these steps:

1. **Download Repository as ZIP**:
   - Download the repository as a ZIP file from [Visa-Scheduler GitHub Repository]([https://github.com/AashishKumar-3002/WebTalk-Fusion](https://github.com/AashishKumar-3002/Visa-Scheduler)).

2. **Unzip the Repository**:
   - Unzip the downloaded repository.

3. **Open Browser and Enable Developer Settings**:
   - Open Chrome or any preferred browser.
   - Turn on developer settings.

4. **Load Unpacked Extension**:
   - In the browser, select "Load Unpacked" option in the developer settings.
   - Navigate to the unzipped repository folder and select it.

5. **Install Visual Studio Code (VS Code)**:
   - Download and install [Visual Studio Code](https://code.visualstudio.com/) if you don't have it installed already.

6. **Download Python and pip**:
   - Download and install [Python](https://www.python.org/downloads/) and ensure that pip is installed.

7. **Navigate to the Backend Folder**:
   - Open the repository folder in VS Code.
   - Navigate to the `backend` folder.

8. **Install Python Dependencies**:
   - Run the following command in the terminal to install the required Python dependencies:
     ```bash
     pip install -r requirements.txt
     ```

9. **Run Python Server**:
   - Start the Python server by running the following command:
     ```bash
     python app.py
     ```

10. **Deployment (Optional)**:
    - For deployment, install Gunicorn by running:
      ```bash
      pip install gunicorn
      ```
    - Run Gunicorn command with 2 workers:
      ```bash
      gunicorn -w 2 -b 0.0.0.0:8000 server:app
      ```

11. **Access the Application**:
    - Access the application in your browser.

Note: 
1. For Mac please turn off the airplay receiver for local testing.
2. For win , Add exclusion in the windows firewall
3. For linux , no worries

You have now successfully set up WebTalk-Fusion and can start using it for engaging conversations with websites.

