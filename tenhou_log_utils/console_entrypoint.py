"""Define console entrypoint"""
import logging

_LG = logging.getLogger(__name__)


def _parse_command_line_args():
    import argparse
    parser = argparse.ArgumentParser(
        description='Utility for tenhou.net log files.'
    )
    subparsers = parser.add_subparsers(dest='sub_command')
    subparsers.required = True
    _add_subparsers(subparsers)
    return parser.parse_args()


def _add_subparsers(subparsers):
    parser = subparsers.add_parser('view')
    _populate_view_options(parser)
    parser = subparsers.add_parser('download')
    _populate_download_options(parser)


###############################################################################
def _parse_mjlog(args):
    from tenhou_log_utils.viewer import parse_mjlog
    parse_mjlog(args.input)


def _populate_view_options(parser):
    parser.add_argument(
        'input', help='Input mjlog file.'
    )
    parser.set_defaults(func=_parse_mjlog)
    parser.add_argument('--debug', help='Enable debug log', action='store_true')


###############################################################################
def _download_mjlog(args):
    import sys
    import requests
    from .download import download_mjlog
    try:
        download_mjlog(args.log_id, args.output)
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 404:
            _LG.error('Log file (%s) not found.', args.log_id)
            sys.exit(1)
        raise


def _populate_download_options(parser):
    parser.add_argument(
        'log_id', help='Play log ID'
    )
    parser.add_argument(
        'output', help='Output file path.'
    )
    parser.set_defaults(func=_download_mjlog)
    parser.add_argument('--debug', help='Enable debug log', action='store_true')


###############################################################################
def _init_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    format_ = (
        '%(asctime)s: %(levelname)5s: %(message)s' if not debug else
        '%(asctime)s: %(levelname)5s: %(funcName)10s: %(message)s'
    )
    logging.basicConfig(level=level, format=format_)


def main():
    """Main entry point for Tenhou log utils CLI."""
    args = _parse_command_line_args()
    _init_logging(args.debug)
    args.func(args)


if __name__ == '__main__':
    main()
