import logging
import datetime
import re
from xml.etree.cElementTree import Element, SubElement, ElementTree

module_logger = logging.getLogger('application.XmlCreator')


class XmlCreator(object):

    def __init__(self):
        self.logger = logging.getLogger('application.XmlCreator')
        self.logger.debug('creating an instance of XmlCreator')
        self.root = None
        self.child = None
        self.tree = None

    def create_root(self, value):
        self.root = Element(value)

    def create_child(self, value):
        self.child = SubElement(self.root, value)

    def create_element(self, field, name, value):
        SubElement(self.child, field, name=name).text = value

    def compose_tree(self):
        self.tree = ElementTree(self.root)

    def save_xml(self):
        filename = str(datetime.datetime.now())
        filename = re.sub(":", "", filename) + '.xml'
        self.tree.write(filename)



