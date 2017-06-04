from __future__ import absolute_import

import gzip
import xml.etree.ElementTree as ET


def _load_gzipped(filepath):
    with gzip.open(filepath) as file_:
        return ET.parse(file_)


def load_mjlog(filepath):
    """Load [gzipped] mjlog file

    Parameters
    ----------
    filepath : str
        Path to the mjlog file to load

    Returns
    -------
    xml.etree.ElementTree.ElementTree
        ElementTree object representing the log data.
    """
    if '.gz' in filepath:
        return _load_gzipped(filepath)
    return ET.parse(filepath)
