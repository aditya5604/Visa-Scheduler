import undetected_chromedriver as uc
import time
from PIL import Image
import shutil
import io
import os.path
import nodriver as uc
import logging
import time
import io
from PIL import Image
import asyncio

logging.basicConfig(level=30)
captcha_input = None

def receive_captcha_input(input_data):
    global captcha_input
    captcha_input = input_data

def get_captcha_input():
    global captcha_input
    return captcha_input

class SlotFinder:

    @classmethod
    async def create(cls):
        self = SlotFinder()
        
        # Initialize the WebDriver instance
        self.driver = await uc.start()
        
        # Navigate to the URL and initialize the browser tab
        self.tab = await self.driver.get("https://www.usvisascheduling.com/")
        
        return self


    async def save_captcha_image(self):

        # Get the bounding box of the image
        captcha_image_node_id = await self.tab.query_selector("#captchaImage")
        attributes = await captcha_image_node_id.get_js_attributes()
        style_attribute = attributes.get("style", "")
        height = int((style_attribute.get("height")).replace("px", ""))
        width = int(style_attribute.get("width").replace("px", ""))
        location_x = attributes.get("x")
        location_y = attributes.get("y")
        image_bounding_box = (
            location_x,
            location_y,
            location_x + width,
            location_y + height,
        )

        # Take a screenshot of the specific area
        screenshot = await self.tab.save_screenshot(filename="../Image/Full_image.png")
        with open(screenshot, 'rb') as f:
            screenshot = f.read()
        captcha_image = Image.open(io.BytesIO(screenshot)).crop(image_bounding_box)


        # Save the cropped captcha image
        captcha_image.save("../Image/captcha_image.png")
        # shutil.rmtree("../Image/Full_image.png")

    async def get_capcha_text(self , counter):
        try: 
                captcha_text = None
                
                if counter > 1:
                    # Clear the stored captcha input
                    receive_captcha_input(None)
                
                # Save the CAPTCHA image
                await self.save_captcha_image()

                while not captcha_text:
                    print("Waiting for CAPTCHA input...")
                    try:

                        await self.tab.sleep(1)
                        captcha_text = get_captcha_input()
                        print("CAPTCHA input received successfully" , captcha_text)

                    except asyncio.exceptions.TimeoutError:
                        print("CAPTCHA input not received yet. Waiting...")

                if not captcha_text:
                    # Get the captcha image and extract text using pytesseract
                    await self.tab.sleep(10)
                    print("Extracting CAPTCHA text...")

                # Find the captcha input field and enter the extracted text
                captcha_field = await self.tab.select("#extension_atlasCaptchaResponse")
                
                await captcha_field.clear_input()
                await captcha_field.send_keys(captcha_text)

        except Exception as e:
            print("Error:", str(e))

    async def find_my_slots(self, username, password , security_questionsanswers):
        try:
            await self.tab.sleep(10)

            # Find the username and password fields and enter the user-provided values
            username_field = await self.tab.select("#signInName")
            await username_field.send_keys(username)

            password_field = await self.tab.select("#password")
            await password_field.send_keys(password)
            counter = 0 

            await self.get_capcha_text(counter)

            await self.tab.sleep(5)

            # Find the sign-in button and click it
            sign_in_button = await self.tab.select("#continue")
            await sign_in_button.click()

            try:

                while(True):
                    # Check if the captcha verification was successful
                    captcha_reverification_required = await self.tab.select("#claimVerificationServerError")

                    # If the captcha verification was not successful, refresh the captcha
                    if captcha_reverification_required:
                        # Use JavaScript to click the captcha refresh button
                        captcha_refresh_button = await self.tab.select("#captchaRefreshImage")
                        await captcha_refresh_button.click()

                        # Wait for the new captcha image to load
                        await self.tab.sleep(3)

                        captcha_field = await self.tab.select("#extension_atlasCaptchaResponse")
            
                        await captcha_field.clear_input()

                        counter += 1
                        await self.get_capcha_text(counter)

                        await self.tab.sleep(10)
                        
                        # Find the sign-in button and click it
                        sign_in_button = await self.tab.select("#continue")
                        await sign_in_button.click()
                    else:
                        break
            except asyncio.exceptions.TimeoutError:
                print("Captcha verification successful")

            # Wait for the security questions to appear
            wait = await self.tab.wait_for("[id^='kbq']")

            # Find the security question labels and answer fields
            security_question_labels = await self.tab.select_all("p[id^='kbq']")
            security_answer_fields = await self.tab.select_all("input[id^='kba']")

            # Iterate through the security questions and answer fields
            for i in range(len(security_question_labels)):
                security_question_label = security_question_labels[i]
                security_answer_field = security_answer_fields[i]

                await security_answer_field.clear_input()

                # Get the security question text
                security_question_text = security_question_label.text
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
                    print("Please re-enter and submit the answer for the security question on the extension page.")
                    corresponding_answer = input(
                        f"Enter the answer for '{security_question_text}': "
                    )

                # Send keys to the answer field
                await security_answer_field.send_keys(corresponding_answer)

            # Find the continue button and click it
            continue_button = await self.tab.select("#continue")
            await continue_button.click()

            # Check if the error message is displayed
            try:
                # Wait for the error message to be displayed
                error_message = await self.tab.wait_for("#claimVerificationServerError", timeout=10)

                # Check the style attribute to see if the error is displayed
                if error_message.text:
                    print(error_message.text)
                    # Iterate through the security questions and answer fields
                    for i in range(len(security_question_labels)):
                        security_question_label = security_question_labels[i]
                        security_answer_field = security_answer_fields[i]

                        await security_answer_field.clear_input()

                        # Get the security question text
                        security_question_text = security_question_label.text
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
                            print("Please re-enter and submit the answer for the security question on the extension page.")
                            corresponding_answer = input("Please enter the correct answer: ")

                        # Enter the correct answer
                        await security_answer_field.send_keys(corresponding_answer)

                # Find the continue button and click it
                continue_button = await self.tab.select("#continue")
                await continue_button.click()

            except asyncio.exceptions.TimeoutError:
                print("The Security Question CheckIn Was successfull.")

            # Wait for 3 seconds before quitting the browser
            time.sleep(10)

            # Check for 'reschedule_appointment' or 'continue_application' elements
            try:
                schedule_appointment = await self.tab.query_selector("#reschedule_appointment")
                if schedule_appointment:
                    print("Found reschedule appointment element.")
                    # If the element is found, click it
                    await schedule_appointment.click()
                else:
                    continue_application = await self.tab.query_selector("#continue_application")
                    if continue_application:
                        print("Found continue application element.")
                        # If the element is found, click it
                        await continue_application.click()
                    else:
                        print("Neither reschedule appointment nor continue application elements were found.")
                
                # Randomly scroll page down 
                await self.tab.scroll_down()
                # Randomly scroll page up
                await self.tab.scroll_up()
                
                # Wait for the page to load
                await asyncio.sleep(10)

            except asyncio.TimeoutError: 
                print("Timeout occurred while looking for reschedule appointment or continue application elements.")
            except Exception as e:
                print(f"An error occurred: {e}")

        except Exception as e:
            # Delete all cookies
            print("Retrying after some time, cooldown 10s due to the error:", e)

        # Close the browser
        self.driver.stop()

# # Create an instance of the SlotFinder class
# slot_finder = SlotFinder()
# # Call the find_my_slots method
# slot_finder.find_my_slots("mdmazheruddin20117@gmail.com", "mazher@1234")
