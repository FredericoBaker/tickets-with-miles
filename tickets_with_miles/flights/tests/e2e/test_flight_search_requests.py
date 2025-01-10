from django.test import TestCase
from flights.models import Airport
from django.urls import reverse
from django.contrib.messages import get_messages

class FlightSearchRequestsTest(TestCase):
    """
    Using Django's test client to test the search_flights view 
    and inspect session data directly.
    """

    def setUp(self):
        self.url = reverse('search_flights')

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

        Airport.objects.create(
            name="Aeropuerto Carlos Hott Siebert",
            iata_code="ZOS",
            state_code="OS",
            country_code="CL",
            country_name="Chile"
        )

    def test_request_with_valid_data_return_flights(self):

        response = self.client.post(
            self.url,
            data={
                'origin': 'GRU',
                'destination': 'LIS',
                'date': '2025-04-10',
                'flexibility': 3,
            },
            follow=False
        )

        # Check status -> Redirect (status 302)
        self.assertEqual(response.status_code, 302)
        
        # Check if 'flights' were returned
        session = self.client.session
        self.assertIn('flights', session)
        self.assertGreater(len(session['flights']), 0)

    def test_valid_request_no_flights_shows_no_flights_message(self):

        response = self.client.post(
            self.url,
            data={
                'origin': 'ZOS',
                'destination': 'LIS',
                'date': '2025-06-31',
                'flexibility': 1,
            }
        )

        # No flights -> the view re-renders
        self.assertEqual(response.status_code, 200)

        session = self.client.session

        # The session might not have 'flights' at all, or might be an empty list
        flights_in_session = session.get('flights', [])
        self.assertEqual(len(flights_in_session), 0)

    def test_invalid_form(self):
        response = self.client.post(
            self.url,
            data={
                'origin': 'XYZ',
                'destination': 'LIS',
                'date': '',
                'flexibility': 1,
            }
        )

        # The form is invalid -> no redirect -> status 200
        self.assertEqual(response.status_code, 200)

        # The view uses messages to show validation errors
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Origin: O código da origem não é válido." in str(msg) for msg in messages)
        )

        # Session should NOT contain flights
        session = self.client.session
        self.assertNotIn('flights', session)