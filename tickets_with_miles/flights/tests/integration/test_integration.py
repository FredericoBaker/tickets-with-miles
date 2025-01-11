from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from flights.models import Airport
from datetime import date
import time


class FlightSearchIntegrationTest(TestCase):
    """
    Integration tests for the Flight Search feature.
    Tests the interaction between forms, views, services, and models without mocking.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up initial data for all tests.
        """
        # Create valid airports
        cls.origin_airport = Airport.objects.create(
            name="São Paulo–Guarulhos",
            iata_code="GRU",
            state_code="SP",
            country_code="BR",
            country_name="Brazil"
        )
        cls.destination_airport = Airport.objects.create(
            name="Lisbon Airport",
            iata_code="LIS",
            state_code="",
            country_code="PT",
            country_name="Portugal"
        )
        # Create an airport that does not have flights for certain tests
        cls.no_flight_airport = Airport.objects.create(
            name="Aeropuerto Carlos Hott Siebert",
            iata_code="ZOS",
            state_code="OS",
            country_code="CL",
            country_name="Chile"
        )

    def test_valid_flight_search_and_result_display(self):
        """
        Test submitting the flight search form with valid data
        and verify that flights are fetched and displayed correctly.
        """
        url = reverse('search_flights')
        form_data = {
            'origin': 'GRU',
            'destination': 'LIS',
            'date': '2025-04-10',
            'flexibility': '3'
        }

        response = self.client.post(url, data=form_data, follow=True)

        # Check for redirect after successful form submission
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flights/search.html')

        # Check that flights are stored in the session
        session = self.client.session
        self.assertIn('flights', session)
        self.assertGreater(len(session['flights']), 0, "Flights should be present in the session.")

        # Check that flights are displayed in the response
        self.assertContains(response, 'flight-card', msg_prefix="Flights should be displayed on the page.")

    def test_flight_search_with_flexibility_multiple_dates(self):
        """
        Test submitting the flight search form with flexibility greater than 0,
        ensuring that multiple dates are searched and combined flight results are processed.
        """
        url = reverse('search_flights')
        form_data = {
            'origin': 'GRU',
            'destination': 'LIS',
            'date': '2025-04-10',
            'flexibility': '7'
        }

        response = self.client.post(url, data=form_data, follow=True)

        # Check for redirect after successful form submission
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flights/search.html')

        # Check that flights are stored in the session
        session = self.client.session
        self.assertIn('flights', session)
        self.assertGreater(len(session['flights']), 0, "Flights should be present in the session.")

        # Check that flights are displayed in the response
        self.assertContains(response, 'flight-card', msg_prefix="Flights should be displayed on the page.")

    def test_flight_search_no_flights_found(self):
        """
        Test submitting the flight search form with parameters that yield no flights,
        ensuring that the appropriate warning message is displayed.
        """
        url = reverse('search_flights')
        form_data = {
            'origin': 'ZOS',  # Assuming ZOS has no flights to LIS on the given date
            'destination': 'LIS',
            'date': '2025-06-31',  # Invalid date to ensure no flights
            'flexibility': '1'
        }

        response = self.client.post(url, data=form_data)

        # Since no flights are expected, the view should render the template again
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flights/search.html')

        # Check that no flights are stored in the session
        session = self.client.session
        self.assertNotIn('flights', session)

        # Check for the warning message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any('Nenhum voo encontrado.' in str(message) for message in messages),
            "A warning message should be displayed when no flights are found."
        )

    def test_session_flight_data_cleared_after_retrieval(self):
        """
        Test that flight data stored in the session is cleared after being retrieved.
        """
        url = reverse('search_flights')
        form_data = {
            'origin': 'GRU',
            'destination': 'LIS',
            'date': '2025-04-10',
            'flexibility': '3'
        }

        # Submit the form to store flights in the session
        response = self.client.post(url, data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertIn('flights', session)

        # Perform a GET request to retrieve and pop 'flights' from the session
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn('flights', context)
        self.assertGreater(len(context['flights']), 0, "Flights should be present in the context.")

        # Check that 'flights' are removed from the session
        session = self.client.session
        self.assertNotIn('flights', session, "Flights should be cleared from the session after retrieval.")

    def test_invalid_flight_search_inputs_display_errors(self):
        """
        Test submitting the flight search form with invalid origin and destination codes,
        ensuring that the form is invalid and appropriate error messages are displayed.
        """
        url = reverse('search_flights')
        form_data = {
            'origin': 'XYZ',  # Invalid airport code
            'destination': 'ABC',  # Invalid airport code
            'date': '2025-04-10',
            'flexibility': '3'
        }

        response = self.client.post(url, data=form_data)

        # The form is invalid, so the same template should be rendered
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flights/search.html')

        # Check that no flights are stored in the session
        session = self.client.session
        self.assertNotIn('flights', session)

        # Check for form error messages
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Origin: O código da origem não é válido." in str(message) for message in messages),
            "An error message should be displayed for invalid origin."
        )
        self.assertTrue(
            any("Destination: O código do destino não é válido." in str(message) for message in messages),
            "An error message should be displayed for invalid destination."
        )
