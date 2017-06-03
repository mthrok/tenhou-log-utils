"""Download Tenhou.net mahjong log"""
import logging

import requests

_ARCHIVE_URL = 'http://tenhou.net/0/log/?'
_LG = logging.getLogger(__name__)


def _download(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.content


def _save(data, filepath):
    with open(filepath, 'wb') as file_:
        file_.write(data)


def download_mjlog(log_id, outpath):
    """Download mjlog file on local file"""
    url = '{}{}'.format(_ARCHIVE_URL, log_id)
    _LG.info('Downloading %s', log_id)
    data = _download(url)
    _LG.info('Saving data on %s', outpath)
    _save(data, outpath)
