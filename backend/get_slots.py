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
from datetime import datetime

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

    async def find_my_slots(self, username, password , security_questionsanswers , start_date , end_date , cities_list=None ,  city=None):
        try:
            await self.tab.sleep(10)
            await self.tab.wait_for("#signInName" , timeout=120)

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
            wait = await self.tab.wait_for("[id^='kbq']" , timeout=120)

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
                await self.tab.wait_for("#post_select" , timeout=120)

                if cities_list:
                    for city in cities_list:
                        try:
                            await self.schedule_appointment(city, start_date, end_date)
                            return  # Exit if appointment is scheduled successfully
                        except Exception as e:
                            print(f"Could not schedule appointment for {city}. Error: {e}")
                elif city:
                    await self.schedule_appointment(city, start_date, end_date)

            except asyncio.TimeoutError: 
                print("Timeout occurred while looking for reschedule appointment or continue application elements.")
            except Exception as e:
                print(f"An error occurred: {e}")
                            
        except Exception as e:
            # Delete all cookies
            print("Retrying after some time, cooldown 10s due to the error:", e)

        # Close the browser
        self.driver.stop()

    # span_of_cities : list = [] , based_on_range : bool = False ,
    async def schedule_appointment(self , city : str = None ,  start_date : str = None , end_date : str = None):
        # book an appointment based on the range of cities or cities from the first date available between the range of dates start_date and end_date
        try:
            # Wait for the page to load
            await self.tab.wait_for("#post_select" , timeout=120)

            # Find the element by id
            select_element = await self.tab.query_selector('#post_select')
            print(select_element)

            # Get all option elements within the select
            options = await select_element.query_selector_all('option')
            print(options)

            # Iterate through the options and select the option or range of options as specified
            if city:
                for option in options:
                    if city.lower() in (option.text).lower():
                        selected_option = option
                        print(f"Selected option: {selected_option}")
                        await selected_option.select_option()
                        break

                # call the JavaScript function to dispatch a change event
                await self.dispatch_change_event(self.tab , select_element)

                # Check if the datepicker element was found
                has_date_appointment  = await self.tab.select(".hasDatepicker")
                print(has_date_appointment)

                # If the datepicker element was found, select the date
                if has_date_appointment:
                    datepicker = await self.tab.select("#datepicker")
                    print("Slot found for the selected city. Selecting the date...")

                    # was usefull for earlier version of the website
                    await datepicker.click()
                    await self.tab.sleep(2)
                    await datepicker.mouse_click()
                    await self.tab.sleep(2)

                    # make sure the start date is greater than the current date and less than the end date
                    current_date = datetime.now().date()

                    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                    print(type(start_date))
                    print(type(end_date))

                    if start_date > current_date and start_date < end_date:
                        print("Date range is valid")

                        #Find the first group div
                        select_element_group = await self.tab.query_selector('.ui-datepicker-group-first')
                        print("Selected the First Group")

                        select_element_header = await select_element_group.query_selector('.ui-datepicker-header')
                        print("Selected the Header of the First Group")

                        # Find the month and year elements
                        select_element_title = await select_element_header.query_selector('.ui-datepicker-title')
                        print("Selected the Title of the First Group")

                        # Find the year element
                        select_element_year = await select_element_title.query_selector('.ui-datepicker-year')
                        print("Selected the Year of the First Group")

                        select_element_month = await select_element_title.query_selector('.ui-datepicker-month')
                        print("selected the Month of the First Group")

                        # Get the year options
                        year_options = await select_element_year.query_selector_all('option')
                        print("Selected the Year Options")

                        # Extract the start year from the provided start date
                        start_year = start_date.year

                        # Extract the end year from the provided end date
                        end_year = end_date.year

                        # Display the options to the user
                        year_index = -1
                        for index, option in enumerate(year_options):
                            try:
                                # Extract the year value from the option text
                                year_value = int(option.text)
                                print(f"{index}. {year_value}")

                                # Select the option corresponding to the start year
                                if year_value == start_year:
                                    try:
                                        await option.select_option()
                                        print(f"Selected year: {year_value}")
                                        year_index = index
                                        print(type(year_index))
                                        await self.dispatch_change_event(self.tab , select_element_year)
                                        break
                                    except Exception as e:
                                        print(e)
                                        await option.click()
                            except Exception as e:
                                print(e)
                                continue
                        
                        # Loop through the months and years until a green day is found or the range is exhausted
                        current_month = start_date.month
                        current_year = start_year
                        
                        
                        while current_year <= end_year:
            
                            # Find the datepicker element for the month
                            select_element_month = await self.tab.select('.ui-datepicker-month')

                            # Get the month options
                            month_options = await select_element_month.query_selector_all('option')

                            # Extract the end month from the provided end date
                            end_month = end_date.month

                            js_function = """
                            function (select) {
                                let optionsList = [];
                                select.querySelectorAll('option').forEach(option => {
                                    let optionText = option.textContent;
                                    let optionValue = option.value;
                                    optionsList.push({text: optionText, value: optionValue});
                                });
                                return optionsList;
                            }
                            """

                            # Use the apply function to execute the JavaScript on the select element
                            month_option_values = await select_element_month.apply(js_function, return_by_value=True)

                            # option_values now contains the values of all option elements
                            print(month_option_values)

                            # Display the options to the user
                            month_index = -1
                            for index, option in enumerate(month_options):
                                try:
                                    # Extract the month value from the option text
                                    for moption in month_option_values:
                                        if moption['text'] == option.text:
                                            month_value = int(option['value'])
                                    print(f"{index}. {option.text}")

                                    # Select the option corresponding to the start month
                                    if month_value == current_month - 1:
                                        await option.select_option()
                                        print(f"Selected month: {option.text}")
                                        month_index = index
                                        await self.dispatch_change_event(self.tab , select_element_month)
                                        break
                                except Exception as e:
                                    print(e)
                                    continue
                            
                            first_available_date = None
                            try:
                                green_dates_elements = await self.tab.select_all('.greenday')

                                for element in green_dates_elements:

                                    day = element.text
                                    day = datetime.strptime(day, "%d").day
                                    print(day)

                                    date = datetime(current_year, current_month, day).date()

                                    if date >= start_date and date <= end_date:
                                        first_available_date = element
                                        break
                                    else:
                                        print("so condition is not met")
                            except asyncio.exceptions.TimeoutError:
                                    print("No greenday available. Increasing the month.")
                                    
                            except Exception as e:
                                print(e)

                            # If a matching date element is found, interact with it
                            if first_available_date:
                                # For example, click on the date if it's a link
                                await first_available_date.click()
                                await self.tab.sleep(5)
                                print("Selected the first available date.")
                                # await first_available_date.mouse_click()
                                # await tab.sleep(5)
                                break

                            # Increment the month and year
                            current_month = current_month + 1
                            await self.tab.sleep(5)
                            if current_month > 11:
                                current_month = 1
                                current_year = current_year + 1
                                print("Current Year:", current_year)
                                print("year_index:", year_options)
                                for index, option in enumerate(year_options):
                                    try:
                                        # Extract the year value from the option text
                                        year_value = int(option.text)
                                        print(f"{index}. {year_value}")

                                        # Select the option corresponding to the start year
                                        if year_value == current_year:
                                            try:
                                                await option.select_option()
                                                print(f"Selected year: {year_value}")
                                                year_index = index
                                                print(type(year_index))
                                                await self.dispatch_change_event(self.tab , select_element_year)
                                                await self.tab.sleep(5)
                                                break
                                            except Exception as e:
                                                print(e)
                                                await option.click()
                                    except Exception as e:
                                        print(e)

                            # Check if the end year is reached
                            if current_year > end_year or current_month > end_month:
                                print("No available dates in the specified range")
                                break

                        await self.submit_form()
                        print("Submitted the appointment.")

                    else:
                        print("No valid selection criteria provided.")
                        raise ValueError("No valid selection criteria provided.")
                else:
                    print("No datepicker element found.")
                    raise ValueError("No datepicker element found.")
            else:
                print("No valid city provided.")
                raise ValueError("No valid city provided.")

        except asyncio.TimeoutError: 
            print("Timeout occurred while looking for reschedule appointment or continue application elements.")
        except Exception as e:
            print(f"An error occurred: {e}")

    # JavaScript function to dispatch a change event
    async def dispatch_change_event(self, tab , select_element):
        try:
            js_dispatch_event = """
            function dispatchChangeEvent(element) {
                var event = new Event('change', { bubbles: true });
                element.dispatchEvent(event);
            }
            """
            # Dispatch the change event on the select element
            await select_element.apply(js_dispatch_event, return_by_value=False)

            # Find the schedule button and click it
            await tab.sleep(5)         
        except Exception as e:
            print(f"An error occurred: {e}")
    
    # Time and submit the form
    async def submit_form(self):
        try:
            # select the timing available
            time_slots = await self.tab.query_selector_all('#time_select')

            # Check if there are any available time slots
            if time_slots:
                # Select the first available time slot by clicking on the radio input
                first_available_slot = await time_slots[0].query_selector('input[type="radio"]')
                if first_available_slot:
                    await first_available_slot.click()
                    await self.tab.sleep(5)
                    print(first_available_slot)
                    print("selected the first available slot w/o dispatch event")

                    await self.dispatch_change_event(self.tab , first_available_slot)
                    print("Selected the first available time slot with dispatch event")

                    submit_button = await self.tab.query_selector('#submitbtn')
                    print(submit_button)

                    # Check if the submit button is available and not disabled
                    if submit_button:
                            await submit_button.click()
                            await self.tab.sleep(30)
                            print("Submitted the appointment.")
                    else:
                        print("Submit button not found.")
            else:
                print("No available time slots.")
        except Exception as e:
            print(f"An error occurred: {e}")

# # Create an instance of the SlotFinder class
# slot_finder = SlotFinder()
# # Call the find_my_slots method
# slot_finder.find_my_slots("mdmazheruddin20117@gmail.com", "mazher@1234")
#selenium grid concept