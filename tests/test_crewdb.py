#!/usr/bin/python

import unittest
import wiflight

import server

class WiFlightAPICrewDbTestCase(unittest.TestCase):
    def setUp(self):
        self.client = server.MockClient()

    def test_crewdb(self):
        fleetname = 'fleet1'
        username = 'user@example.com'
        u = wiflight.APICrewDbEntry(fleetname, username)
        u.load(self.client)
        self.assertEqual(u.username, username)
        self.assertEqual(u.email, username)
        self.assertEqual(u.name, 'Kim Vandry')
        self.assertEqual(u.phone, '+1 514 907-0802')
        self.assertEqual(u.dbdomain, 'fleet1-domain.example.com')
        self.assertEqual(u.fleet, fleetname)
        self.assertTrue(u.signup_done)

    def test_empty_crewdb(self):
        fleetname = 'yar'
        username = 'yas'
        u = wiflight.APICrewDbEntry(fleetname, username)
        self.assertEqual(u.username, username)
        self.assertEqual(u.fleet, fleetname)

    def test_crewdb_search(self):
        s = wiflight.APICrewDbSearch("example")
        s.load(self.client)
        self.assertEqual(len(s), 2)
        for item in s:
            if isinstance(item, wiflight.APICrewDbEntry):
                self.assertEqual(item.name, 'Kim Vandry')
            else:
                self.assertEqual(
                    item.temporary_username_domain, 'fleet1-domain.example.com'
                )
                self.assertEqual(item.name, 'fleet1')
                # This property is supposed to get removed by
                # canonicalization
                self.assertIsNone(item.body.get('dbdomain'))

    def test_crewdb_search_anyfleet(self):
        s = wiflight.APICrewDbAnyFleet("user@example.com")
        s.load(self.client)
        self.assertEqual(len(s), 1)
        first = iter(s).next()
        self.assertEqual(first.name, 'Kim Vandry')

if __name__ == '__main__':
    unittest.main()
