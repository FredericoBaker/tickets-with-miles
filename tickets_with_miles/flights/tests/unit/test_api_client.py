from django.test import TestCase
from unittest.mock import patch, AsyncMock, ANY
from datetime import date
from flights.api_client import FlightAPIClient
import asyncio


class FlightAPIClientTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.origin = 'CNF'
        cls.destination = 'GRU'
        cls.departure_date = date(2025, 3, 25)
        cls.return_date = date(2025, 6, 10)

    def setUp(self):
        self.client = FlightAPIClient(api_key='fake-api-key', telemetry='fake-telemetry')

    @patch('flights.api_client.FlightAPIClient.fetch', new_callable=AsyncMock)
    def test_search_flights(self, mock_fetch):
        """
        Test the method test_search_flights.
        """
        adults = 2
        children = 1
        infants = 0

        # Mocking API response
        mock_fetch.return_value = {
            'flights': [
                {
                    'origin': self.origin,
                    'destination': self.destination,
                    'departure': self.departure_date.strftime('%Y-%m-%d'),
                    'return': self.return_date.strftime('%Y-%m-%d'),
                    'adults': adults,
                    'children': children,
                }
            ]
        }

        result = asyncio.run(self.client.search_flights(
            origin=self.origin,
            destination=self.destination,
            departure_date=self.departure_date,
            return_date=self.return_date,
            adults=adults,
            children=children,
            infants=infants,
        ))

        self.assertEqual(result['flights'][0]['origin'], self.origin)
        self.assertEqual(result['flights'][0]['destination'], self.destination)
        self.assertEqual(result['flights'][0]['departure'], self.departure_date.strftime('%Y-%m-%d'))
        self.assertEqual(result['flights'][0]['return'], self.return_date.strftime('%Y-%m-%d'))

    @patch('flights.api_client.FlightAPIClient.fetch', new_callable=AsyncMock)
    def test_search_flights_bulk(self, mock_fetch):
        """
        Test the method test_search_flights_bulk.
        """
        searches = [
            {
                'origin': self.origin,
                'destination': self.destination,
                'departure_date': self.departure_date,
                'return_date': self.return_date,
                'adults': 2,
                'children': 1,
                'infants': 0
            },
            {
                'origin': 'RIO',
                'destination': 'NYC',
                'departure_date': self.departure_date,
                'return_date': self.return_date,
                'adults': 1,
                'children': 0,
                'infants': 1
            }
        ]

        # Mocking API response
        mock_fetch.side_effect = [
            {'flights': [{'origin': self.origin, 'destination': self.destination, 'departure': self.departure_date.strftime('%Y-%m-%d')}]},
            {'flights': [{'origin': 'RIO'      , 'destination': 'NYC'           , 'departure': self.departure_date.strftime('%Y-%m-%d')}]}
        ]

        result = asyncio.run(self.client.search_flights_bulk(searches))
        self.assertEqual(mock_fetch.call_count, 2)

        self.assertEqual(result[0]['flights'][0]['origin'], self.origin)
        self.assertEqual(result[1]['flights'][0]['origin'], 'RIO')

    @patch('flights.api_client.FlightAPIClient.fetch', new_callable=AsyncMock)
    def test_fetch_error_handling(self, mock_fetch):
        # Mocking an error in an API request
        mock_fetch.return_value = {'error': 'Network error'}

        result = asyncio.run(self.client.search_flights(
            origin=self.origin,
            destination=self.destination,
            departure_date=self.departure_date,
        ))

        self.assertEqual(result['error'], 'Network error')
