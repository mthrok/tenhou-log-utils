"""Define console entrypoint"""
from __future__ import absolute_import

import sys
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
    parser = subparsers.add_parser('parse')
    _populate_parse_options(parser)
    parser = subparsers.add_parser('view')
    _populate_view_options(parser)
    parser = subparsers.add_parser('list')
    _populate_list_options(parser)
    parser = subparsers.add_parser('download')
    _populate_download_options(parser)


###############################################################################
def _populate_parse_options(parser):
    from .parse import main as _main
    parser.add_argument(
        'input', help='Input mjlog file.'
    )
    parser.set_defaults(func=_main)
    parser.add_argument('--tags', help='Display only given tags', nargs='*')
    parser.add_argument('--debug', help='Enable debug log', action='store_true')


###############################################################################
def _populate_view_options(parser):
    from .view import main as _main
    parser.add_argument(
        'input', help='Input mjlog file.'
    )
    parser.set_defaults(func=_main)
    parser.add_argument('--round', help='Round number to view', type=int)
    parser.add_argument('--debug', help='Enable debug log', action='store_true')


###############################################################################
def _populate_list_options(parser):
    from .list_mjlog import main as _main
    parser.add_argument(
        '--id-only', help='Print log IDs only.', action='store_true')
    parser.add_argument(
        '--debug', help='Enable debug log', action='store_true')
    parser.set_defaults(func=_main)


###############################################################################
def _populate_download_options(parser):
    from .download import main as _main
    parser.add_argument(
        'log_id', help='Play log ID'
    )
    parser.add_argument(
        'output', help='Output file path.'
    )
    parser.set_defaults(func=_main)
    parser.add_argument('--debug', help='Enable debug log', action='store_true')


###############################################################################
def _init_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    format_ = (
        '%(message)s' if not debug else
        '%(asctime)s: %(levelname)5s: %(funcName)10s: %(message)s'
    )
    logging.basicConfig(level=level, format=format_, stream=sys.stdout)


def main():
    """Main entry point for Tenhou log utils CLI."""
    args = _parse_command_line_args()
    _init_logging(args.debug)
    args.func(args)
