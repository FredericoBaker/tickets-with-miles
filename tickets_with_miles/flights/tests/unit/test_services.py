from datetime import date, datetime
from django.test.testcases import TestCase
from flights.services import FlightService
from unittest.mock import MagicMock
from flights.api_client import FlightAPIClient

class FlightServiceTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.mock_client = MagicMock(FlightAPIClient)
        cls.flight_service = FlightService(client=cls.mock_client)

    def test_generate_smiles_url(self):
        """
        Test the generate_smiles_url function.
        """
        origin = "GIG"
        destination = "MIL"
        departure_date = date(2025, 3, 26)

        url = self.flight_service.generate_smiles_url(origin, destination, departure_date)

        self.assertIn("originAirport=GIG", url)
        self.assertIn("destinationAirport=MIL", url)
        self.assertIn("departureDate=1743001200000", url)

    def test_date_to_timestamp(self):
        """
        Test the method date_to_timestamp.
        """
        departure_date = date(2024, 12, 15)
        timestamp = self.flight_service.date_to_timestamp(departure_date)
        
        expected_timestamp = int(datetime(2024, 12, 15, 15, 0).timestamp() * 1000)
        self.assertEqual(timestamp, expected_timestamp)

    def test_get_miles_cost(self):
        """
        Test the method get_miles_cost.
        """
        flight = {'fareList': [{'type': 'SMILES', 'miles': 1000}, 
                               {'type': 'SMILES_CLUB', 'miles': 1500},
                               {'type': 'SMILES_CLUB', 'miles': 500}
                               ]}
        miles_cost = self.flight_service.get_miles_cost(flight)
        
        self.assertEqual(miles_cost, 500)

    def test_extract_flights(self):
        """
        Test the method extract_flights.
        """
        airline = 'GOL (G3)'
        miles_1 = 55200
        miles_2 = 555200
        hours = 1
        minutes = 15
        derparture_airport = 'CNF'
        derparture_time = '2024-12-18T10:20:00'
        arrival_airport = 'GRU'
        arrival_time = '2024-12-18T11:35:00'
        number_stops = 1
        smiles_url = 'https://www.smiles.com.br/mfe/emissao-passagem/?cabin=ALL&adults=1&children=0&infants=0&searchType=g3&segments=1&tripType=2&originAirport=CNF&destinationAirport=GRU&departureDate=1734534000000'
        
        raw_data = {
            'requestedFlightSegmentList' : [{'flightList' : [{
                'airline' : { 'name': airline },
                'fareList' : [{ 'type' : 'SMILES', 'miles' : miles_1 },
                              { 'type' : 'SMILES', 'miles' : miles_2 }],
                'duration' : { 'hours' : hours, 'minutes' : minutes },
                'departure' : { 'airport' : { 'code' : derparture_airport }, 'date' : derparture_time },
                'stops' : number_stops,
                'arrival' : { 'airport' : { 'code' : arrival_airport }, 'date': arrival_time }
                }]
            }]
        }

        flights = self.flight_service.extract_flights(raw_data, smiles_url)
    
        self.assertEqual(flights[0]['airline'], airline)
        self.assertEqual(flights[0]['miles_cost'], miles_1)
        self.assertEqual(flights[0]['duration_hours'], hours)
        self.assertEqual(flights[0]['duration_minutes'], minutes)
        self.assertEqual(flights[0]['departure_time'], derparture_time)
        self.assertEqual(flights[0]['departure_airport'], derparture_airport)
        self.assertEqual(flights[0]['number_of_stops'], number_stops)
        self.assertEqual(flights[0]['arrival_time'], arrival_time)
        self.assertEqual(flights[0]['arrival_airport'], arrival_airport)
        self.assertEqual(flights[0]['smiles_url'], smiles_url)