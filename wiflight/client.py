#!/usr/bin/python

import urllib
import contextlib
# We insist on using cURL, not urllib2 because the former
# does not check certificates!
import pycurl
import cStringIO as StringIO

class HTTPError(Exception):
    def __init__(self, url, code, message):
        if message:
            Exception.__init__(self, "%d %s" % (code, message))
        else:
            Exception.__init__(self, str(code))
        self.url = url
        self.code = code
        self.message = message

AnyEtag = object()

class APISession(object):
    """Wi-Flight HTTP API session

    Usage:

    anonymous_session = wiflight.APISession()
    r1 = ananymous_session.request("some/public/object", "GET")
    with anonymous_session.login("foo", "bar") as authenticated_session:
        r2 = authenticated_session.request(
            "can/only/be/accessed/when/logged/in", "GET"
        )

    # Override the URL to access the Wi-Flight REST API:
    another_session = wiflight.APISession("https://other-server/")
    """

    def __init__(self, baseurl='https://www.wi-flight.net/'):
        self.baseurl = baseurl
        self.curl_handle = pycurl.Curl()

    def extra_setup(self):
        """A derived class can override this method in order to set
        additional options on the cURL handle just before the transfer
        is performed. An example of this would be to set a proxy server
        or cURL hostname resolution options."""

    def request(self, url, method, data=None, content_type="text/xml", etag=AnyEtag):
        """Make an HTTP request to the API.

        Supported methods are GET, PUT, DELETE, POST, and MOVE.
        :param data: is only used for PUT and POST.
        :param content_type: is only used for PUT.
        :param etag: is only used for PUT and DELETE.

        If etag is supplied, it must match the existing document
        before it can be modified. To force the existing document
        to not exist yet, use None.

        Returns a tuple (content_type, etag, body_string)
        """
        req = self.curl_handle
        req.setopt(pycurl.URL, self.baseurl + url)
        outbody = StringIO.StringIO()
        req.setopt(pycurl.WRITEFUNCTION, outbody.write)
        header = []
        req.setopt(pycurl.HEADERFUNCTION, header.append)
        out_header = []
        if method in ("PUT", "POST"):
            body = StringIO.StringIO(data)
            req.setopt(pycurl.READFUNCTION, body.read)
            req.setopt(pycurl.INFILESIZE, len(data))
            if method == "POST":
                out_header.append('Content-Length: %d' % (len(data),))
                req.setopt(pycurl.POST, 1)
            else:
                req.setopt(pycurl.UPLOAD, 1)
                out_header.append('Content-Type: text/xml')
        elif method != 'GET':
            req.setopt(pycurl.CUSTOMREQUEST, method)
        if etag is not AnyEtag:
            if etag is None:
                out_header.append('If-None-Match: *')
            else:
                out_header.append('If-Match: %d' % (etag,))
        req.setopt(pycurl.HTTPHEADER, out_header)
        req.setopt(pycurl.SSL_VERIFYPEER, 1)
        self.extra_setup()
        req.perform()
        code = req.getinfo(pycurl.RESPONSE_CODE)
        if code >= 200 and code < 300:
            content_type = req.getinfo(pycurl.CONTENT_TYPE)
            req.reset()
            etag = None
            for line in header:
                if line.lower().startswith('etag:'):
                    etag = line[5:].strip()
            return content_type, etag, outbody.getvalue()
        req.reset()
        status_line = None
        while True:
            tok = header[0].split(None, 2)
            if tok[0].startswith('HTTP/') and not ':' in tok[0] and tok[1] == '100':
                header.pop(0)
                if header[0] == '\r\n' or header[0] == '\n':
                    header.pop(0)
            else:
                break
        tok = header[0].split(None, 2)
        if tok[0].startswith('HTTP/') and not ':' in tok[0]:
            status_line = tok[2]
        if status_line.endswith('\r\n'):
            status_line = status_line[:-2]
        elif status.endswith('\n'):
            status_line = status_line[:-1]
        raise HTTPError(self.baseurl + url, code, status_line)

    @contextlib.contextmanager
    def login(self, username, password, expiration=60):
        """A context manager for upgrading a Wi-Flight API
        session from an anonymous session to an authenticated
        session.

        :param username: Wi-Flight username for logging in to server
        :param password: Password for logging in using this username
        :param expiration: Length of time in seconds for which the
          login should be valid. Defaults to 1 minute.

        Usage:

        flight = wiflight.APIFlight(12345)
        anonymous_session = wiflight.APISession()

        # This would not work because permission is not granted
        # to anonymously access this flight
        #flight.load(anonymous_session)

        with anonymous_session.login("foo", "bar") as session:
            # But this will work
            flight.load(session)
        """
        s = APISession(self.baseurl)
        s.curl_handle.setopt(pycurl.COOKIEJAR, "-")
        s.request('auth/login', 'POST', urllib.urlencode({
            'expires': expiration,
            'username': username,
            'password': password
        }))
        successful = False
        try:
            yield s
            successful = True
        finally: 
            if successful:
                s.request('auth/logout', 'POST', '')
            else:
                # If an exception occurred, we still try to log
                # out, but we suppress any exceptions
                try:
                    s.request('auth/logout', 'POST', '')
                except Exception:
                    pass
