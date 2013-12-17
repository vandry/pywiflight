#!/usr/bin/python

import unittest
import wiflight
import datetime

import server

class WiFlightAPIReservationTestCase(unittest.TestCase):
    def setUp(self):
        self.client = server.MockClient()

    def test_reservation(self):
        resv = wiflight.APIReservation('resv1')
        resv.load(self.client)
        self.assertEqual(resv.domain, 'dom1')

    def test_reservation_attr(self):
        resv = wiflight.APIReservation('resv1')
        resv.load(self.client)
        self.assertEqual(resv.start, datetime.datetime(2013,12,1,12,0,0))
        self.assertEqual(resv.end, datetime.datetime(2013,12,1,13,0,0))
        self.assertEqual(resv.notify_profile, "placeholder")

    def test_reservation_crew(self):
        resv = wiflight.APIReservation('resv1')
        resv.load(self.client)
        self.assertItemsEqual(resv.crew, ['crew1', 'crew2'])
        resv.crew.add('crew3')
        self.assertItemsEqual(resv.crew, ['crew1', 'crew2', 'crew3'])
        resv.crew.remove('crew1')
        self.assertItemsEqual(resv.crew, ['crew2', 'crew3'])

    def test_reservation_aircraft(self):
        resv = wiflight.APIReservation('resv1')
        resv.load(self.client)
        self.assertEqual(resv.aircraft.url, 'a/aircraft/5')
        resv.aircraft = wiflight.APIAircraft(6)
        self.assertEqual(resv.aircraft.url, 'a/aircraft/6')

if __name__ == '__main__':
    unittest.main()
