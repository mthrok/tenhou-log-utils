"""Utility functions for I/O"""
from __future__ import absolute_import

import sys
import gzip
import xml.etree.ElementTree as ET


def _load_gzipped(filepath):
    with gzip.open(filepath) as file_:
        return ET.parse(file_).getroot()


def load_mjlog(filepath):
    """Load [gzipped] mjlog file

    Parameters
    ----------
    filepath : str
        Path to the mjlog file to load

    Returns
    -------
    xml.etree.ElementTree.Element
        Element object which represents the root node.
    """
    if '.gz' in filepath:
        return _load_gzipped(filepath)
    return ET.parse(filepath).getroot()


if sys.version_info[0] < 3:
    def ensure_unicode(string):
        """Convert string into unicode."""
        if not isinstance(string, unicode):
            return string.decode('utf-8')
        return string


    def ensure_str(string):
        """Convert string into str (bytes) object."""
        if not isinstance(string, str):
            return string.encode('utf-8')
        return string


    from urllib2 import unquote as _unquote
    def unquote(string):
        unquoted = _unquote(ensure_str(string))
        if isinstance(string, unicode):
            return unquoted.decode('utf-8')
        return unquoted


else:
    def ensure_unicode(string):
        """Convert string into unicode."""
        if not isinstance(string, str):
            return string.decode('utf-8')
        return string

    def ensure_str(string):
        """Convert string into str (bytes) object."""
        if not isinstance(string, str):
            return string.decode('utf-8')
        return string


    from urllib.parse import unquote as _unquote
    def unquote(string):
        return _unquote(string)
