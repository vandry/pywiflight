#!/usr/bin/python

import unittest
import wiflight
import decimal
import re

import server

class WiFlightAPIAircraftTestCase(unittest.TestCase):
    def setUp(self):
        self.client = server.MockClient()

    def test_aircraft(self):
        ac = wiflight.APIAircraft(5)
        ac.load(self.client)
        self.assertEqual(ac.tail, 'C-FFSK')

    def test_aircraft_attr(self):
        ac = wiflight.APIAircraft(5)
        ac.load(self.client)
        self.assertEqual(ac.id, 5)
        self.assertEqual(ac.model, 'Cessna 172N')
        self.assertEqual(ac.cockpit_height, decimal.Decimal('1.5'))
        self.assertEqual(ac.prop_blades, 2)
        self.assertEqual(ac.model_url, 'http://www.wi-flight.net/Cessna_172.kmz')

    def test_aircraft_delete(self):
        self.assertIn('a/aircraft/62', self.client.contents)
        ac = wiflight.APIAircraft(62)
        ac.load(self.client)
        ac.delete(self.client)
        self.assertNotIn('aircraft/62', self.client.contents)

    def test_aircraft_nonascii(self, _matchre=re.compile(
        ur'.*<aircraft id="63">.*<model>(?:\u30bb|&#12475;)(?:\u30b9|&#12473;)(?:\u30ca|&#12490;)</model>.*</aircraft>', re.DOTALL
    )):
        ac = wiflight.APIAircraft(63)
        ac.load(self.client)
        ac.model = u'\u30bb\u30b9\u30ca'
        ac.save(self.client)
        self.assertRegexpMatches(self.client.contents['a/aircraft/63'][2], _matchre)
        ac.load(self.client)
        self.assertEqual(ac.model, u'\u30bb\u30b9\u30ca')

    def test_aircraft_new(self, _matchre=re.compile(
        r'.*<aircraft>.*<model>Brand new</model>.*</aircraft>', re.DOTALL
    )):
        ac = wiflight.APIAircraft('C-ZZZZ')
        ac.tail = 'C-ZZZZ'
        ac.model = 'Brand new'
        ac.prop_blades = 2
        ac.save(self.client)
        self.assertRegexpMatches(self.client.contents['a/aircraft/tail/C-ZZZZ'][2], _matchre)

class WiFlightAPIAircraftSearchTestCase(unittest.TestCase):
    def setUp(self):
        self.client = server.MockClient()

    def test_ac_search(self):
        s = wiflight.APIAircraftSearch("filter words n&&d encoding")
        self.assertEqual(s.url, 'a/aircraft/?search=filter+words+n%26%26d+encoding')
        s.load(self.client)
        self.assertEqual(len(s), 2)
        it = iter(s)
        first = it.next()
        second = it.next()
        self.assertEqual(first.url, 'a/aircraft/5')
        self.assertEqual(second.url, 'a/aircraft/6')

class WiFlightAPIAircraftImageTestCase(unittest.TestCase):
    def setUp(self):
        self.client = server.MockClient()

    def test_ac_image_get(self):
        image = wiflight.APIAircraft(65).image
        image.load(self.client)
        self.assertEqual(image.content_type, "image/png")
        self.assertEqual(image.body, self.client.contents['a/aircraft/65/image'][2])

    def test_ac_image_put(self):
        black_1x1 = '\x89PNG\r\n\x1a\n\0\0\0\rIHDR\0\0\0\1\0\0\0\1\1\0\0\0\x007n\xf9$\0\0\0\nIDAT\x08\x99c`\0\0\0\2\0\1\xf4qd\xa6\0\0\0\0IEND\xaeB`\x82'
        image = wiflight.APIAircraft(66).image
        image.content_type = "image/png"
        image.body = black_1x1
        image.save(self.client)
        self.assertEqual(image.content_type, "image/png")
        self.assertEqual(
            self.client.contents['a/aircraft/66/image'],
            (0, "image/png", black_1x1)
        )

if __name__ == '__main__':
    unittest.main()
