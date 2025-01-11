from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from django.core.management import call_command
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
        Load airport data from the CSV into the test database.
        """
        call_command('load_airports')

    def test_valid_flight_search_and_result(self):
        """
        Test submitting the flight search form with valid data
        and verify that flights are fetched.
        """
        url = reverse('search_flights')
        form_data = {
            'origin': 'GRU',
            'destination': 'LIS',
            'date': '2025-04-10',
            'flexibility': '0'
        }

        response = self.client.post(url, data=form_data, follow=False)
        self.assertEqual(response.status_code, 302)

        session = self.client.session
        self.assertIn('flights', session)
        self.assertGreater(len(session['flights']), 0)


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

        response = self.client.post(url, data=form_data, follow=False)
        self.assertEqual(response.status_code, 302)

        session = self.client.session
        self.assertIn('flights', session)
        self.assertGreater(len(session['flights']), 0)

    def test_flight_search_no_flights_found(self):
        """
        Test submitting the flight search form with parameters that yield no flights,
        ensuring that the appropriate warning message is displayed.
        """
        url = reverse('search_flights')
        form_data = {
            'origin': 'GVR',
            'destination': 'BOS',
            'date': '2025-04-10',
            'flexibility': '3'
        }

        response = self.client.post(url, data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flights/search.html')

        session = self.client.session
        self.assertNotIn('flights', session)

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

        response = self.client.post(url, data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertNotIn('flights', session)

    def test_invalid_flight_search_inputs_display_errors(self):
        """
        Test submitting the flight search form with invalid origin and destination codes,
        ensuring that the form is invalid and appropriate error messages are displayed.
        """
        url = reverse('search_flights')
        form_data = {
            'origin': 'QQQ',  # Invalid airport code
            'destination': 'XXX',  # Invalid airport code
            'date': '2025-04-10',
            'flexibility': '3'
        }

        response = self.client.post(url, data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flights/search.html')

        session = self.client.session
        self.assertNotIn('flights', session)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Origin: O código da origem não é válido." in str(message) for message in messages),
            "An error message should be displayed for invalid origin."
        )
        self.assertTrue(
            any("Destination: O código do destino não é válido." in str(message) for message in messages),
            "An error message should be displayed for invalid destination."
        )
