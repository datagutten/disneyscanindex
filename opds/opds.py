# https://github.com/c4software/pyopds-server/blob/main/controllers/opds.py
import datetime
import hashlib
import heapq
import os
import time
from xml.etree import ElementTree as etree

from xml.sax.saxutils import escape as xml_escape
import zipfile
from urllib.parse import parse_qs, quote, unquote, urlparse


class OPDSEntry:
    def __init__(self, feed: etree.Element, title, identifier):
        self.feed = feed
        self.entry = etree.SubElement(self.feed, 'entry')
        etree.SubElement(self.entry, 'title').text = title
        etree.SubElement(self.entry, 'id').text = identifier
        etree.SubElement(self.entry, 'updated').text = datetime.datetime.now().isoformat()

    def author(self, name: str):
        author = etree.SubElement(self.entry, 'author')
        etree.SubElement(author, 'name').text = name

    def link(self, link_type: str, href: str, rel):
        etree.SubElement(self.entry, 'link', {'rel': rel, 'href': href, 'type': link_type})

    def navigation(self, target: str, kind='navigation'):
        return self.link('application/atom+xml; profile=opds-catalog; kind=%s' % kind, target, 'subsection')

    def content_link(self, target: str, content_type: str, rel: str):
        return self.link(content_type, target, rel)

    def content(self, data, content_type='html'):
        element = etree.SubElement(self.entry, 'content', {'type': content_type})
        element.text = data
        return element


class OPDS:
    def __init__(self, title: str, feed_id: str):
        self.feed = etree.Element(
            'feed',
            {
                'xmlns': 'http://www.w3.org/2005/Atom',
                'xmlns:opds': 'http://opds-spec.org/2010/catalog',
            }
        )

        etree.SubElement(self.feed, 'id').text = feed_id
        etree.SubElement(self.feed, 'title').text = title
        etree.SubElement(self.feed, 'updated').text = datetime.datetime.now().isoformat()

    def entry(self, title, identifier, author=None, links=None):
        return OPDSEntry(self.feed, title, identifier)

    # entry = etree.SubElement(self.feed, 'entry')
    # etree.SubElement(entry, 'title').text = title
    # etree.SubElement(entry, 'id').text = identifier

    # if author:
    #     author = ET.SubElement(entry, 'author')
    #     ET.SubElement(author, 'name').text = entry_data['author']
    #
    # for rel, href, type_ in links or []:
    #     ET.SubElement(entry, 'link', {'rel': rel, 'href': href, 'type': type_})

    def render(self) -> str:
        xml_string = etree.tostring(self.feed, encoding='unicode', method='xml')
        processing_instruction = (
            '<?xml-stylesheet type="text/xsl" href="/opds_to_html.xslt"?>\n'
        )
        # return processing_instruction + xml_string
        return xml_string


class OPDSFeedGenerator:
    @staticmethod
    def generate_feed(title, feed_id, links, entries):
        feed = ET.Element(
            'feed',
            {
                'xmlns': 'http://www.w3.org/2005/Atom',
                'xmlns:opds': 'http://opds-spec.org/2010/catalog',
            },
        )

        ET.SubElement(feed, 'title').text = title
        ET.SubElement(feed, 'id').text = feed_id
        ET.SubElement(feed, 'updated').text = (
                datetime.datetime.now(datetime.timezone.utc).isoformat() + 'Z'
        )

        for rel, href, type_ in links:
            ET.SubElement(feed, 'link', {'rel': rel, 'href': href, 'type': type_})

        for entry_data in entries:
            entry = ET.SubElement(feed, 'entry')
            ET.SubElement(entry, 'title').text = entry_data['title']
            ET.SubElement(entry, 'id').text = entry_data['id']

            if 'author' in entry_data:
                author = ET.SubElement(entry, 'author')
                ET.SubElement(author, 'name').text = entry_data['author']

            for rel, href, type_ in entry_data['links']:
                ET.SubElement(entry, 'link', {'rel': rel, 'href': href, 'type': type_})

        xml_string = ET.tostring(feed, encoding='unicode', method='xml', pretty_print=True)
        processing_instruction = (
            '<?xml-stylesheet type="text/xsl" href="/opds_to_html.xslt"?>\n'
        )
        return processing_instruction + xml_string
