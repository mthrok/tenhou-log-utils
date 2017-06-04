"""Entrypoint for `list` command"""
from __future__ import absolute_import

import logging

from tenhou_log_utils.mjinfo_parser import parse_mjinfo

_LG = logging.getLogger(__name__)


def _print_ids(logs):
    for data in logs.values():
        for datum in data:
            _LG.info(datum['file'])


def _print_info(logs):
    for filepath, data in logs.items():
        _LG.info('%s:', filepath)
        for datum in data:
            for key, value in datum.items():
                _LG.info('  %s: %s', key, value)
            _LG.info('')


def main(args):
    """Entrypoint for `list` sub command. List up game logs and print info"""
    logs = parse_mjinfo()
    if args.id_only:
        _print_ids(logs)
    else:
        _print_info(logs)
