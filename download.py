"""Download Tenhou.net mahjong log"""
import requests

_ARCHIVE_URL = 'http://tenhou.net/0/log/?'


def _parse_command_line_args():
    import argparse
    parser = argparse.ArgumentParser(
        description='Download log from tenhou.net'
    )
    parser.add_argument(
        'log_id', help='Log ID, such as 2017042101gm-00c1-0000-4b052ac7',
    )
    return parser.parse_args()


def _download(url):
    resp = requests.get(url)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 404:
            raise RuntimeError('Archived log file not found.')
        raise
    return resp.content


def _save(data, filepath):
    with open(filepath, 'wb') as file_:
        file_.write(data)


def _main():
    args = _parse_command_line_args()
    url = '{}{}'.format(_ARCHIVE_URL, args.log_id)
    data = _download(url)
    filepath = '{}.mjlog'.format(args.log_id)
    _save(data, filepath)


if __name__ == '__main__':
    _main()
