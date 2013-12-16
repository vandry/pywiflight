#!/usr/bin/python

import unittest
import wiflight

import server

class WiFlightAPIObjectTestCase(unittest.TestCase):
    """Most of APIObject is implicitly tested in the
    testing of its derived classes."""
    def setUp(self):
        self.client = server.MockClient()

    def test_not_found(self):
        o = wiflight.APIObject('test/foo1')
        with self.assertRaises(wiflight.HTTPError) as cm:
            o.load(self.client)
        self.assertEqual(cm.exception.code, 404)

    def test_new_object_conflict(self):
        o = wiflight.APIObject('test/foo2')
        o.body = "yyy"
        o.content_type = "text/plain"
        with self.assertRaises(wiflight.HTTPError) as cm:
            o.save(self.client)
        self.assertEqual(cm.exception.code, 412)

    def test_change_conflict(self):
        # First we create an object
        o1 = wiflight.APIObject('test/foo3')
        o1.body = "zzz"
        o1.content_type = "text/plain"
        o1.save(self.client)
        # Then the object is modified out of band
        o2 = wiflight.APIObject('test/foo3')
        o2.load(self.client)
        o2.body = "aaa"
        o2.save(self.client)
        # Now we try to save the original again
        o1.body = "bbb"
        with self.assertRaises(wiflight.HTTPError) as cm:
            o1.save(self.client)
        self.assertEqual(cm.exception.code, 412)

    def test_new_object_force(self):
        o = wiflight.APIObject('test/foo4')
        o.body = "yyy"
        o.content_type = "text/plain"
        o.save_noguard(self.client)

    def test_del_object_conflict(self):
        o1 = wiflight.APIObject('test/foo5')
        o1.load(self.client)
        # In the meantime...
        o2 = wiflight.APIObject('test/foo5')
        o2.load(self.client)
        o2.body = "eee"
        o2.save(self.client)
        with self.assertRaises(wiflight.HTTPError) as cm:
            o1.delete(self.client)
        self.assertEqual(cm.exception.code, 412)

    def test_del_object_force(self):
        o1 = wiflight.APIObject('test/foo5')
        o1.load(self.client)
        # In the meantime...
        o2 = wiflight.APIObject('test/foo5')
        o2.load(self.client)
        o2.body = "eee"
        o2.save(self.client)
        o1.delete_noguard(self.client)

if __name__ == '__main__':
    unittest.main()
