from flask import Flask, request, jsonify , send_file
from flask_cors import CORS
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import time
import os.path
from PIL import Image
import io
from get_slots import SlotFinder , receive_captcha_input

app = Flask(__name__)
CORS(app)

# Global variables to store login details temporarily
login_details = {}
security_questions = {}

@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        login_details["username"] = username
        login_details["password"] = password
    return jsonify({"password": password , "username": username})


@app.route("/security_question", methods=["POST"])
def security_question_route():
    if request.method == "POST":
        # Retrieve the data from the form
        question_1 = request.form.get("question_1")
        answer_1 = request.form.get("answer_1")
        question_2 = request.form.get("question_2")
        answer_2 = request.form.get("answer_2")
        question_3 = request.form.get("question_3")
        answer_3 = request.form.get("answer_3")
        
        # Store the data in the security_questions dictionary
        security_questions["question_1"] = question_1
        security_questions["answer_1"] = answer_1
        security_questions["question_2"] = question_2
        security_questions["answer_2"] = answer_2
        security_questions["question_3"] = question_3
        security_questions["answer_3"] = answer_3
        
        # You can process the security questions and answers here
        
    return jsonify(security_questions)

@app.route("/captcha_input", methods=["POST"])
def receive_captcha_from_frontend():
    captcha_data = request.json.get("captcha_input")
    receive_captcha_input(captcha_data)
    return "CAPTCHA input received successfully"

@app.route("/start_process", methods=["GET"])
def start_process():
    global login_details, security_questions
    print(login_details)
    print(security_questions)
    # Check if login details and security questions are available
    if "username" in login_details and "password" in login_details and security_questions:
        # Start the process with Selenium
        slot_finder = SlotFinder()
        slot_finder.find_my_slots(login_details["username"], login_details["password"] , security_questions)
        return jsonify({"status": "success"})
    else:
        return jsonify({"error": "Login details or security questions not provided"})


@app.route("/captcha_image", methods=["GET"])
def get_captcha_image():
    # Return the CAPTCHA image file
    return send_file("../Image/captcha_image.png", mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
