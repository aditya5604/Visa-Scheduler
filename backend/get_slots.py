import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service as ChromeService
import time
from PIL import Image
import io
import os.path

def receive_captcha_input(self, captcha_data):
    return captcha_data

class SlotFinder:
    def __init__(self):
        # set the user agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.105 Safari/537.36"
        # Set Chrome options
        chrome_options = uc.ChromeOptions()
        # chrome_options.add_argument("--headless=new")  # Set to True if you want to run in headless mode
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # Create a new Selenium Chrome Service
        service = Service('/usr/bin/google-chrome-stable')
        # service = ChromeService(ChromeDriverManager().install())

        # Start the WebDriver
        self.driver = uc.Chrome(service=service, options=chrome_options)

        # Use the stealth module to make the bot undetectable
        stealth(
            self.driver,
            user_agent=user_agent,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=False,
            run_on_insecure_origins=False,
        )



    def save_captcha_image(self):

        # Get the bounding box of the image
        img = self.driver.find_element(By.ID, "captchaImage")
        print(img.size)
        image_location = img.location
        image_size = img.size
        image_bounding_box = (
            image_location["x"],
            image_location["y"],
            image_location["x"] + image_size["width"],
            image_location["y"] + image_size["height"],
        )

        # Take a screenshot of the specific area
        screenshot = self.driver.get_screenshot_as_png()
        captcha_image = Image.open(io.BytesIO(screenshot)).crop(image_bounding_box)

        # Save the cropped captcha image
        captcha_image.save("../Image/captcha_image.png")

    def get_capcha_text(self):
        try: 
                captcha_text = None

                while not captcha_text:
                    try:
                        # Save the CAPTCHA image
                        self.save_captcha_image()

                        # Wait for the CAPTCHA input from the frontend
                        time.sleep(1)  # Adjust the sleep time as needed

                        captcha_text = receive_captcha_input()
                    except NoSuchElementException:
                        print("CAPTCHA input not received yet. Waiting...")

                if not captcha_text:
                    # Get the captcha image and extract text using pytesseract
                    captcha_text = input("Enter the captcha text: ")

                # Find the captcha input field and enter the extracted text
                captcha_field = self.driver.find_element(
                    By.ID, "extension_atlasCaptchaResponse"
                )
                captcha_field.send_keys(captcha_text)

        except Exception as e:
            print("Error:", str(e))

    def find_my_slots(self, username, password , security_questionsanswers):
        try:
            # Find the username and password fields and enter the user-provided values
            username_field = self.driver.find_element(By.ID, "signInName")
            username_field.send_keys(username)

            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)

            self.get_capcha_text()

            # Find the sign-in button and click it
            sign_in_button = self.driver.find_element(By.ID, "continue")
            sign_in_button.click()

            try:
                # Check if the captcha verification was successful
                captcha_reverification_required = not self.driver.find_elements(
                    By.ID, "claimVerificationServerError"
                )

                # If the captcha verification was not successful, refresh the captcha
                if not captcha_reverification_required:
                    # Use JavaScript to click the captcha refresh button
                    captcha_refresh_button = self.driver.find_element(
                        By.ID, "captchaRefreshImage"
                    )
                    self.driver.execute_script(
                        "arguments[0].click();", captcha_refresh_button
                    )

                    # Wait for the new captcha image to load
                    # You may need to adjust the sleep time based on the website's behavior
                    time.sleep(3)

                    captcha_field = self.driver.find_element(
                        By.ID, "extension_atlasCaptchaResponse"
                    )
                    captcha_field.clear()

                    self.save_captcha_image(self.driver)

                    self.get_capcha_text()

                    # Find the sign-in button and click it
                    sign_in_button = self.driver.find_element(By.ID, "continue")
                    sign_in_button.click()
            except NoSuchElementException:
                print("Captcha verification successful")

            # Wait for the security questions to appear
            wait = WebDriverWait(self.driver, 30)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[id^='kbq']")))

            # Find the security question labels and answer fields
            security_question_labels = self.driver.find_elements(
                By.CSS_SELECTOR, "label[id^='kbq']"
            )
            security_answer_fields = self.driver.find_elements(
                By.CSS_SELECTOR, "input[id^='kba']"
            )

            # Iterate through the security questions and answer fields
            for i in range(len(security_question_labels)):
                security_question_label = security_question_labels[i]
                security_answer_field = security_answer_fields[i]

                security_answer_field.clear()

                # Get the security question text
                security_question_text = security_question_label.find_element(
                    By.XPATH, "./following-sibling::p"
                ).text
                print(f"Security Question: {security_question_text}")

                corresponding_answer = None
                # Find the corresponding answer based on the security question text
                for i in range(1, 4):
                    if security_question_text == security_questionsanswers[f"question_{i}"]:
                        corresponding_answer = security_questionsanswers[f"answer_{i}"]
                        print(f"Corresponding answer: {corresponding_answer}")
                        break
                if not corresponding_answer:    
                    # Get the answer for the security question
                    corresponding_answer = input(
                        f"Enter the answer for '{security_question_text}': "
                    )

                # Send keys to the answer field
                security_answer_field.send_keys(corresponding_answer)

            # Find the continue button and click it
            continue_button = self.driver.find_element(By.ID, "continue")
            continue_button.click()

            # Check if the error message is displayed
            try:
                # Wait for the error message to be displayed
                error_message = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.ID, "claimVerificationServerError")
                    )
                )

                # Check the style attribute to see if the error is displayed
                if error_message.get_attribute("style") == "display: block;":
                    print("Security question answer is incorrect. Please try again.")

                    # Iterate through the security questions and answer fields
                    for i in range(len(security_question_labels)):
                        security_question_label = security_question_labels[i]
                        security_answer_field = security_answer_fields[i]

                        security_answer_field.clear()

                        # Get the security question text
                        security_question_text = security_question_label.find_element(
                            By.XPATH, "./following-sibling::p"
                        ).text
                        print(f"Security Question: {security_question_text}")

                        corresponding_answer = None
                        # Find the corresponding answer based on the security question text
                        for i in range(1, 4):
                            if security_question_text == security_questionsanswers[f"question_{i}"]:
                                corresponding_answer = security_questionsanswers[f"answer_{i}"]
                                print(f"Corresponding answer: {corresponding_answer}")
                                break
                        
                        if not corresponding_answer:
                            # Wait for the user to input the correct answer
                            corresponding_answer = input("Please enter the correct answer: ")

                        # Enter the correct answer
                        security_answer_field.send_keys(corresponding_answer)

                # Find the continue button and click it
                continue_button = self.driver.find_element(By.ID, "continue")
                continue_button.click()

            except:
                print("The Security Question CheckIn Was successfull.")

            # Wait for 3 seconds before quitting the browser
            time.sleep(10)

            # Check if the desired element is available after login
            try:
                continue_application_link = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "continue_application"))
                )
                # If the element is found, redirect to the specified URL
                redirect_url = continue_application_link.get_attribute("href")
                print("Redirecting to:", redirect_url)
                self.driver.get(redirect_url)

                # Wait for the page to load
                time.sleep(5)

                # Check if the desired element is available after login
                # gm_select FIND THE GIVEN ID

                gm_select = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "gm_select"))
                )
                print(gm_select)

            except NoSuchElementException:
                print(
                    "The LINK 'Schedule Appointment' is not available after login. Make Sure , You have the Finished the application process on the website !"
                )

        except NoSuchElementException:
            # Delete all cookies
            self.driver.delete_all_cookies()
            print("Retrying After Sometimes : Cooldown 10s")

        # Close the browser
        self.driver.quit()


# # Create an instance of the SlotFinder class
# slot_finder = SlotFinder()
# # Call the find_my_slots method
# slot_finder.find_my_slots("mdmazheruddin20117@gmail.com", "mazher@1234")
