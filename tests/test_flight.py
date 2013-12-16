#!/usr/bin/python

import unittest
import wiflight
import datetime
import decimal
import re

import server

class WiFlightAPIFlightTestCase(unittest.TestCase):
    def setUp(self):
        self.client = server.MockClient()

    def test_flight(self):
        flight = wiflight.APIFlight(3189)
        flight.load(self.client)
        self.assertEqual(
            flight.start, datetime.datetime(2010,6,26,23,36,33)
        )

    def test_flight_attr(self):
        flight = wiflight.APIFlight(3189)
        flight.load(self.client)
        self.assertEqual(flight.length, decimal.Decimal('7205.25'))
        self.assertEqual(flight.master_ontime, decimal.Decimal('7204.0'))
        self.assertEqual(flight.engine_ontime, decimal.Decimal('7139.5'))
        self.assertEqual(flight.airtime, decimal.Decimal('6606.75'))
        self.assertEqual(flight.alt_min, decimal.Decimal('134.072'))
        self.assertEqual(flight.alt_max, decimal.Decimal('887.285'))
        self.assertEqual(flight.agl_min, decimal.Decimal('-0.182'))
        self.assertEqual(flight.agl_max, decimal.Decimal('880.297'))
        self.assertEqual(flight.groundlevel_min, decimal.Decimal('-17.427'))
        self.assertEqual(flight.groundlevel_max, decimal.Decimal('412.881'))
        self.assertEqual(flight.gs_max, decimal.Decimal('61.218'))
        self.assertEqual(flight.vs_min, decimal.Decimal('-5.697'))
        self.assertEqual(flight.vs_max, decimal.Decimal('6.343'))
        self.assertEqual(flight.az_min, decimal.Decimal('0.0509114583333'))
        self.assertEqual(flight.az_max, decimal.Decimal('1.62018229167'))
        self.assertEqual(flight.headline, 'local at SWF')

    def test_flight_aircraft(self):
        flight = wiflight.APIFlight(3189)
        flight.load(self.client)
        self.assertEqual(flight.aircraft.url, 'a/aircraft/5/')
        flight.aircraft = wiflight.APIAircraft(6)
        self.assertEqual(flight.aircraft.url, 'a/aircraft/6/')
        del flight.aircraft
        self.assertIsNone(flight.aircraft)

    def test_flight_groups(self):
        flight = wiflight.APIFlight(3189)
        flight.load(self.client)
        self.assertItemsEqual(flight.groups, ['Demo flights', 'Featured flights'])
        flight.groups.add('xxx')
        self.assertItemsEqual(flight.groups, ['Demo flights', 'Featured flights', 'xxx'])
        flight.groups.remove('Demo flights')
        self.assertItemsEqual(flight.groups, ['Featured flights', 'xxx'])

    def test_flight_crew(self):
        flight = wiflight.APIFlight(62)
        flight.load(self.client)
        self.assertItemsEqual(flight.crew, ['foo'])
        flight.crew.add('bar')
        self.assertItemsEqual(flight.crew, ['foo', 'bar'])
        flight.crew.remove('foo')
        self.assertItemsEqual(flight.crew, ['bar'])
        # Not possible to save modified crew to the server

    def test_change_aircraft(self, _matchre=re.compile(
        r'.*<flight id="63">.*<aircraft id="7"\s*/>.*</flight>\s*', re.DOTALL
    )):
        flight = wiflight.APIFlight(63)
        flight.load(self.client)
        flight.aircraft = wiflight.APIAircraft(7)
        flight.save(self.client)
        d = self.client.contents['a/flight/63/']
        self.assertRegexpMatches(d[2], _matchre)
        self.assertEqual(d[0], 1)

    def test_flight_blank(self, _matchre=re.compile(
        r'.*<flight id="64">.*</flight>\s*', re.DOTALL
    )):
        # New flights cannot be created through the real API
        # but this is just to test what the blank generated
        # object looks like
        flight = wiflight.APIFlight(64)
        flight.headline = 'anything'
        flight.save(self.client)
        self.assertRegexpMatches(self.client.contents['a/flight/64/'][2], _matchre)

if __name__ == '__main__':
    unittest.main()
