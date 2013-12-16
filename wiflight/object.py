#!/usr/bin/python

import lxml.etree
import datetime
import decimal

def _decode_iso8601(d):
    return datetime.datetime.strptime(d, "%Y%m%dT%H%M%SZ")
def _encode_iso8601(d):
    return "%d%02d%02dT%02d%02d%02dZ" % (d.year, d.month, d.day, d.hour, d.minute, d.second)

class _GroupMembershipSet(object):
    __slots__ = ('doc', 'xpath')

    def __init__(self, doc, xpath):
        self.doc = doc
        self.xpath = xpath

    def __iter__(self):
        return iter(self.doc.xpath(self.xpath + "/member_of/@group_name"))

    def __repr__(self):
        return repr(set(self))

    def add(self, groupname):
        if groupname not in self:
            toptag = self.doc.xpath(self.xpath)[0]
            tag = lxml.etree.Element('member_of')
            tag.set('group_name', groupname)
            toptag.append(tag)

    def remove(self, groupname):
        for tag in self.doc.xpath(self.xpath + "/member_of"):
            if tag.get('group_name') == groupname:
                tag.getparent().remove(tag)

class APIObject(object):
    """Represents an arbitrary Wi-Flight API object

    Each object is instantiated as an empty container. Most objects
    have required fields and cannot be saved to the server while still
    empty.

    To manipulate existing objects, the load method should be used
    to populate the object. To create new objects, required attributes
    should be set and then the object saved to the server using the
    save method.
    """
    __slots__ = ('url', 'etag', 'body', 'content_type')

    def __init__(self, url):
        self.url = url
        self.etag = None
        if hasattr(self, '_toptag'):
            self.body = lxml.etree.Element(self._toptag)
            self.content_type = 'text/xml'
        else:
            self.body = None
            self.content_type = None

    def load(self, client):
        """Load the contents of the object from the server.

        This replaces the old contents of the local copy of the object.
        """
        content_type, etag, body = client.request(self.url, "GET")
        self.etag = etag
        self.content_type = content_type
        if content_type == 'text/xml':
            self.body = lxml.etree.fromstring(body)
        else:
            self.body = body

    def save(self, client):
        """Save the object to the server.

        A guard is used to make sure the object has not changed through
        other means since it was last loaded (or for new objects, to
        make sure it does not already exist on the server.
        """
        content_type = self.content_type
        if content_type == 'text/xml':
            body = lxml.etree.tostring(
                self.body, pretty_print=False, xml_declaration=True
            )
        else:
            body = self.body
        client.request(
            self.url, "PUT", body,
            content_type=content_type, etag=self.etag
        )

    def save_noguard(self, client):
        """Same as save, but without a guard.

        The object will be saved to the server no matter what version
        the server has.
        """
        content_type = self.content_type
        if content_type == 'text/xml':
            body = lxml.etree.tostring(
                self.body, pretty_print=False, xml_declaration=True
            )
        else:
            body = self.body
        client.request(self.url, "PUT", body, content_type=content_type)

    def delete(self, client):
        """Delete the object from the server.

        A guard is used. See save for details.
        """
        client.request(self.url, "DELETE", etag=self.etag)

    def delete_noguard(self, client):
        """Same as delete, but without a guard.

        The object will be deleted from the server no matter what
        version the server has.
        """
        client.request(self.url, "DELETE")

    @property
    def groups(self):
        """Set of group names which the object is a member of

        These group memberships influence permissions for the object and
        only superusers can modify the list."""
        return _GroupMembershipSet(self.body, "/" + self._toptag)

    def __get_attr(self, name, decoder):
        taglist = self.body.xpath("/" + self._toptag + "/" + name + "/text()")
        if not taglist:
            return None
        return decoder(''.join(taglist))

    def __have_attr(self, name):
        p = self.body.xpath("/" + self._toptag + "/" + name)
        return bool(p)

    def __set_attr(self, name, value, encoder):
        taglist = self.body.xpath("/" + self._toptag + "/" + name)
        if len(taglist) == 0:
            toptag = self.body.xpath("/" + self._toptag)[0]
            tag = lxml.etree.Element(name)
            toptag.append(tag)
        else:
            tag = taglist[0]
            for x in taglist[1:]:
                x.getparent().remove(x)
        tag.clear()
        if value is not None:
            tag.text = encoder(value)

    def __set_bool_attr(self, name, value):
        if value:
            taglist = self.body.xpath("/" + self._toptag + "/" + name)
            if len(taglist) == 0:
                toptag = self.body.xpath("/" + self._toptag)[0]
                tag = lxml.etree.Element(name)
                toptag.append(tag)
        else:
            self.__del_attr(name)

    def __del_attr(self, name):
        taglist = self.body.xpath("/" + self._toptag + "/" + name)
        for x in taglist:
            x.getparent().remove(x)

    @classmethod
    def _add_simple_property(cls, decoder, encoder, name, doc):
        setattr(cls, name, property(
            lambda self: self.__get_attr(name, decoder),
            lambda self, value: self.__set_attr(name, value, encoder),
            lambda self: self.__del_attr(name), doc=doc
        ))

    @classmethod
    def _add_simple_text_property(cls, name, doc):
        cls._add_simple_property(unicode, unicode, name, doc)

    @classmethod
    def _add_simple_float_property(cls, name, doc):
        cls._add_simple_property(decimal.Decimal, str, name, doc)

    @classmethod
    def _add_simple_date_property(cls, name, doc):
        cls._add_simple_property(_decode_iso8601, _encode_iso8601, name, doc)

    @classmethod
    def _add_simple_bool_property(cls, name, doc):
        setattr(cls, name, property(
            lambda self: self.__have_attr(name),
            lambda self, value: self.__set_bool_attr(name, value),
            lambda self: self.__del_attr(name), doc=doc
        ))
