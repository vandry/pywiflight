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
        self.assertEqual(resv.name, 'resv1')
        resv.load(self.client)
        self.assertEqual(resv.name, 'resv1')
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

    def test_reservation_crew_by_uuid(self):
        resv = wiflight.APIReservation('resv1')
        resv.load(self.client)
        self.assertItemsEqual(resv.crew_by_uuid, ['uuid1', 'uuid2'])
        resv.crew_by_uuid.add('uuid3')
        self.assertItemsEqual(resv.crew_by_uuid, ['uuid1', 'uuid2', 'uuid3'])
        resv.crew_by_uuid.remove('uuid1')
        self.assertItemsEqual(resv.crew_by_uuid, ['uuid2', 'uuid3'])

    def test_reservation_aircraft(self):
        resv = wiflight.APIReservation('resv1')
        resv.load(self.client)
        self.assertEqual(resv.aircraft.url, 'a/aircraft/5')
        resv.aircraft = wiflight.APIAircraft(6)
        self.assertEqual(resv.aircraft.url, 'a/aircraft/6')

    def test_add_crew_to_new(self):
        resv = wiflight.APIReservation('placeholder')
        self.assertEqual(len(resv.crew), 0)
        self.assertItemsEqual(resv.crew, [])
        resv.crew.add('another placeholder')
        self.assertItemsEqual(resv.crew, ['another placeholder'])
        self.assertEqual(len(resv.crew), 1)

if __name__ == '__main__':
    unittest.main()
