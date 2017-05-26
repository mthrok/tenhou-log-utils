import re
import os
import gzip
import requests

_ARCHIVE_URL = 'http://e.mjv.jp/0/log/archived.cgi'


def _parse_command_line_args():
    import argparse
    parser = argparse.ArgumentParser(
        description='Download log from tenhou.net'
    )
    parser.add_argument(
        'log_id', default='2017042101gm-00c1-0000-4b052ac7',
        help='Log ID',
    )
    return parser.parse_args()


def _download(url):
    resp = requests.get(url)
    return resp.content


def _save(data, filepath):
    with open(filepath, 'wb') as file_:
        file_.write(data)


def _main():
    args = _parse_command_line_args()
    url = '{}?{}'.format(_ARCHIVE_URL, args.log_id)
    data = _download(url)
    filepath = '{}.mjlog'.format(args.log_id)
    _save(data, filepath)


if __name__ == '__main__':
    _main()
