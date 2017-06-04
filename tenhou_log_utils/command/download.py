"""Download Tenhou.net mahjong log"""
from __future__ import absolute_import

import sys
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


def _download_mjlog(log_id, outpath):
    url = '{}{}'.format(_ARCHIVE_URL, log_id)
    _LG.info('Downloading %s', log_id)
    data = _download(url)
    _LG.info('Saving data on %s', outpath)
    _save(data, outpath)


def main(args):
    """Download mjlog file on local file"""
    try:
        _download_mjlog(args.log_id, args.output)
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 404:
            _LG.error('Log file (%s) not found.', args.log_id)
        else:
            _LG.exception('Unexpected error.')
        sys.exit(1)
