import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from flights.models import Airport
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


class FlightSearchSeleniumTest(StaticLiveServerTestCase):
    """
    End-to-End tests for the Flight Search feature. 
    Verifies both valid and invalid submission.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        options = webdriver.ChromeOptions()
        
        # options.add_argument('--headless')

        cls.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options
        )

        cls.driver.maximize_window()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()        

    def test_flight_search_with_valid_data_displays_results(self):

        # Adding valid airports to database
        Airport.objects.create(
            name="São Paulo–Guarulhos",
            iata_code="GRU",
            state_code="SP",
            country_code="BR",
            country_name="Brazil"
        )

        Airport.objects.create(
            name="Lisbon Airport",
            iata_code="LIS",
            state_code="",
            country_code="PT",
            country_name="Portugal"
        )

        # 1. Navigate to the flight search page
        search_flights_url = self.live_server_url + reverse('search_flights')
        self.driver.get(search_flights_url)

        # 2. Fill out the flight search form
        origin_input = self.driver.find_element(By.ID, "id_origin")
        destination_input = self.driver.find_element(By.ID, "id_destination")
        date_input = self.driver.find_element(By.ID, "id_date")
        flexibility_input = self.driver.find_element(By.ID, "id_flexibility")

        origin_input.send_keys("GRU")
        time.sleep(0.5)
        destination_input.send_keys("LIS")
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].value = '2025-04-10';", date_input)
        time.sleep(0.5)
        flexibility_input.send_keys("3")
        time.sleep(0.5)

        # 3. Submit the form
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        time.sleep(2)

        # 4. Check if flight results are displayed
        flight_cards = self.driver.find_elements(By.CLASS_NAME, "flight-card")
        self.assertGreater(
            len(flight_cards),
            0,
            "No flights were displayed, but some were expected."
        )

    def test_flight_search_with_invalid_airport_data_shows_error_messages(self):

        # 1. Navigate to the flight search page
        search_flights_url = self.live_server_url + reverse('search_flights')
        self.driver.get(search_flights_url)

        # 2. Fill out the form with invalid data
        origin_input = self.driver.find_element(By.ID, "id_origin")
        destination_input = self.driver.find_element(By.ID, "id_destination")
        date_input = self.driver.find_element(By.ID, "id_date")
        flexibility_input = self.driver.find_element(By.ID, "id_flexibility")

        origin_input.send_keys("GRU")
        time.sleep(0.5)
        destination_input.send_keys("LIS")
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].value = '2025-04-10';", date_input)
        time.sleep(0.5)
        flexibility_input.send_keys("3")
        time.sleep(0.5)

        # 3. Submit the form
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # 4. Wait for any error messages to be displayed
        time.sleep(1)

        # 5. Check if error messages appear
        page_content = self.driver.page_source
        self.assertIn(
            "Origin: O código da origem não é válido.",
            page_content
        )
        self.assertIn(
            "Destination: O código do destino não é válido.",
            page_content
        )
