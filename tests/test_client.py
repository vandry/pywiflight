#!/usr/bin/python

import unittest
import wiflight
import threading
import time
import BaseHTTPServer

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def log_request(self, *args, **kwargs):
        pass

    def send_body(self, content_type, body):
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_error(self, code, message):
        self.send_response(code)
        return self.send_body("text/plain", message)

    def wrong_method(self, allowed):
        self.send_response(405)
        self.send_header("Allow", allowed)
        return self.send_body("text/plain", "method not allowed")

    def get_document(self):
        path = self.path
        if path == '/auth/login' or path == '/auth/logout':
            self.wrong_method("POST")
            return None
        if path.startswith('/private/'):
            session = self.server.session
            try:
                cookie = self.headers['Cookie']
            except KeyError:
                self.send_error(403, "no session")
                return None
            if session not in cookie:
                self.send_error(403, "no session")
                return None
        if path in self.server.documents:
            d = self.server.documents[path]
        else:
            d = None, None
        try:
            v = self.headers['If-None-Match']
        except KeyError:
            pass
        else:
            if v == '*':
                if d[0] is not None:
                    self.send_error(412, "If-None-Match")
                    return None
            else:
                for etag in map(int, v.split()):
                    if d[0] == etag:
                        self.send_error(412, "If-None-Match")
                        return None
        try:
            v = self.headers['If-Match']
        except KeyError:
            pass
        else:
            if v == '*':
                if d[0] is None:
                    self.send_error(412, "If-Match")
                    return None
            else:
                found = False
                for etag in map(int, v.split()):
                    if d[0] == etag:
                        found = True
                        break
                if not found:
                    self.send_error(412, "If-Match")
                    return None
        return d

    def do_GET(self):
        d = self.get_document()
        if d is None:
            return
        etag, contents = d
        if etag is None:
            return self.send_error(404, "not found")
        self.send_response(200)
        self.send_header("ETag", str(etag))
        return self.send_body("text/plain", contents)

    def read_body(self):
        try:
            length = int(self.headers['Content-Length'])
        except (KeyError, ValueError), e:
            self.send_error(400, "bad Content-Length")
            return None
        return self.rfile.read(length)

    def do_PUT(self):
        d = self.get_document()
        if d is None:
            return
        etag, contents = d
        contents = self.read_body()
        if contents is None:
            return
        if etag is None:
            etag = 0
            self.send_response(201)
        else:
            etag += 1
            self.send_response(200)
        self.server.documents[self.path] = etag, contents
        self.send_header("ETag", str(etag))
        return self.send_body("text/plain", "")

    def do_DELETE(self):
        d = self.get_document()
        if d is None:
            return
        etag, contents = d
        if etag is None:
            return self.send_error(404, "not found")
        del self.server.documents[self.path]
        self.send_response(200)
        return self.send_body("text/plain", "")

    def do_POST(self):
        if self.path == '/auth/login':
            b = self.read_body()
            if b is None:
                return
            if 'username=foo&password=bar' in b:
                self.server.session = 'MagicstrinG'
                self.send_response(200)
                self.send_header(
                    "Set-Cookie",
                    "gasn-session=MagicstrinG; Path=/; Expires=" +
                        self.date_time_string(time.time() + 9999999)
                )
            else:
                self.send_response(403)
            return self.send_body("text/plain", "")
        elif self.path == '/auth/logout':
            self.server.session = None
            self.send_response(200)
            self.send_header("Set-Cookie", "gasn-session=.; Path=/; Expires=0")
            return self.send_body("text/plain", "")
        else:
            self.wrong_method("GET, PUT, DELETE")

class WiFlightAPIClientTestCase(unittest.TestCase):
    def setUp(self):
        server_address = ('localhost', 0)
        httpd = BaseHTTPServer.HTTPServer(server_address, Handler)
        httpd.documents = {
            '/public/example': (0, "example1"),
            '/public/example3': (11, "example3"),
            '/public/example4': (0, "example4"),
            '/private/example1': (0, "example1"),
        }
        httpd.session = None
        self.httpd = httpd
        self.url = 'http://localhost:%d/' % (httpd.server_port,)
        thread = threading.Thread(target=httpd.serve_forever)
        thread.daemon = True
        thread.start()

    def tearDown(self):
        self.httpd.shutdown()

    def test_get(self):
        session = wiflight.APISession(self.url)
        content_type, etag, body = session.request("public/example", "GET")
        self.assertEqual(content_type, "text/plain")
        self.assertEqual(etag, "0")
        self.assertEqual(body, "example1")

    def test_get_error(self):
        session = wiflight.APISession(self.url)
        with self.assertRaises(wiflight.HTTPError) as cm:
            session.request("public/absent", "GET")
        self.assertEqual(cm.exception.code, 404)

    def test_put_unconditional(self):
        session = wiflight.APISession(self.url)
        session.request(
            "public/example2", "PUT", "new_content",
            content_type="text/plain",
        )
        content_type, etag, body = session.request("public/example2", "GET")
        self.assertEqual(content_type, "text/plain")
        self.assertEqual(etag, "0")
        self.assertEqual(body, "new_content")

    def test_put_conditional(self):
        session = wiflight.APISession(self.url)
        with self.assertRaises(wiflight.HTTPError) as cm:
            session.request(
                "public/example3", "PUT", "new_content",
                content_type="text/plain", etag=1
            )
        self.assertEqual(cm.exception.code, 412)

    def test_delete(self):
        session = wiflight.APISession(self.url)
        session.request("public/example4", "DELETE")
        with self.assertRaises(wiflight.HTTPError) as cm:
            session.request("public/example4", "GET")
        self.assertEqual(cm.exception.code, 404)

    def test_notallowed(self):
        session = wiflight.APISession(self.url)
        with self.assertRaises(wiflight.HTTPError) as cm:
            session.request("private/example1", "GET")
        self.assertEqual(cm.exception.code, 403)

    def test_login(self):
        session = wiflight.APISession(self.url)
        with session.login("foo", "bar") as newsession:
            newsession.request("private/example1", "GET")

if __name__ == '__main__':
    unittest.main()
