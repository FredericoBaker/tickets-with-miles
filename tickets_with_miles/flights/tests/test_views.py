from django.contrib.messages import get_messages
from django.test.testcases import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from flights.models import Airport


class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('search_flights')
    
    def test_search_flights_page_status_code(self):
        """
        Tests if the flight search page is loading successfully.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flights/search.html')

    def test_search_flights_form_displayed(self):
        """
        Verifies if the form is displayed correctly on the page.
        """
        response = self.client.get(self.url)
        self.assertContains(response, '<form', 1)
        self.assertContains(response, 'Origem')
        self.assertContains(response, 'Destino')
        self.assertContains(response, 'Data')
        self.assertContains(response, 'Flexibilidade')

    @patch('flights.services.FlightService.get_flights')
    @patch('flights.models.Airport.objects.filter')
    def test_search_flights_successful_search(self, mock_filter, mock_get_flights):
        """
        Tests if the flight search works when the form is valid.
        """
        mock_filter.return_value.exists.return_value = True

        mock_get_flights.return_value = [{
                'airline': 'GOL (G3)', 
                'miles_cost': 55200, 
                'duration_hours': 1, 
                'duration_minutes': 15, 
                'departure_time': '2024-12-18T10:20:00', 
                'departure_airport': 'CNF', 
                'number_of_stops': 1, 
                'arrival_time': '2024-12-18T11:35:00', 
                'arrival_airport': 'GRU', 
                'smiles_url': 'https://www.smiles.com.br/mfe/emissao-passagem/?cabin=ALL&adults=1&children=0&infants=0&searchType=g3&segments=1&tripType=2&originAirport=CNF&destinationAirport=GRU&departureDate=1734534000000'
            }]
        
        data = {
            'origin': 'CNF',
            'destination': 'GRU',
            'date': '10/03/2025',
            'flexibility': 0
        }

        response = self.client.post(self.url, data)
        self.assertIn('flights', self.client.session)
        self.assertRedirects(response, self.url)
        self.assertEqual(response.status_code, 302)

    @patch('flights.services.FlightService.get_flights')
    @patch('flights.models.Airport.objects.filter')
    def test_search_flights_error_occurred(self, mock_filter, mock_get_flights):
        """
        Tests the behavior when an error occurs while fetching the flights.
        """
        mock_filter.return_value.exists.return_value = True
        mock_get_flights.side_effect = Exception("Erro ao buscar os voos")
        data = {
            'origin': 'ABC',
            'destination': 'GRU',
            'date': '10/03/2025',
            'flexibility': 0
        }
        response = self.client.post(self.url, data)
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Ocorreu um erro ao pesquisar pelos voos.', messages)

    @patch('flights.services.FlightService.get_flights')
    def test_search_flights_no_session_data(self, mock_get_flights):
        """
        Tests the behavior when there is no flight data in the session.
        """
        mock_get_flights.return_value = []
        response = self.client.get(self.url)
        self.assertEqual(response.context['flights'], [])