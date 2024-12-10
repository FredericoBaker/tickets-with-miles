from django.test.testcases import TestCase
from flights.forms import FlightSearchForm
from unittest.mock import patch
from datetime import date

class FlightSearchFormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.form_data = {
            'origin' : 'CNF',
            'destination' : 'GRU',
            'date' : '01/10/2025',
            'flexibility' : 0
        }

    @patch('flights.models.Airport.objects.filter')
    def test_valid_form(self, mock_filter):
        """
        Test all valid inputs in the FlightSearchForm with mocked airports.
        """
        # Mocking the filter method to simulate that both airports exist in the database
        mock_filter.return_value.exists.return_value = True
        
        flight_search_form = FlightSearchForm(data=self.form_data)

        self.assertTrue(flight_search_form.is_valid())
        self.assertEqual(flight_search_form.clean_origin(), 'CNF')
        self.assertEqual(flight_search_form.clean_destination(), 'GRU')
        self.assertEqual(flight_search_form.clean_date(), date(2025, 10, 1))

    @patch('flights.models.Airport.objects.filter')
    def test_invalid_airport_form(self, mock_filter):
        """
        Test an invalid airport input in the FlightSearchForm with mocked airports.
        """
        # Mocking filter to simulate the absence of some airports
        mock_filter.return_value.exists.return_value = False
        
        self.form_data['origin'] = 'ABC'
        flight_search_form = FlightSearchForm(data=self.form_data)
        self.assertFalse(flight_search_form.is_valid())

        self.form_data['destination'] = 'XYZ'
        flight_search_form = FlightSearchForm(data=self.form_data)
        self.assertFalse(flight_search_form.is_valid())        

    @patch('flights.models.Airport.objects.filter')
    def test_invalid_date_form(self, mock_filter):
        """
        Test an invalid date input in the FlightSearchForm with mocked airports.
        """
        # Mocking the filter to return airports as existing
        mock_filter.return_value.exists.return_value = True
        
        # Test with a date in the past
        self.form_data['date'] = '01/10/2023'
        flight_search_form = FlightSearchForm(data=self.form_data)
        self.assertFalse(flight_search_form.is_valid())

        # Test with a date too far in the future
        self.form_data['date'] = '01/10/2030'
        flight_search_form = FlightSearchForm(data=self.form_data)
        self.assertFalse(flight_search_form.is_valid())

        # Test with a valid future date within the allowed range
        self.form_data['date'] = '01/10/2025'
        flight_search_form = FlightSearchForm(data=self.form_data)
        self.assertTrue(flight_search_form.is_valid())
