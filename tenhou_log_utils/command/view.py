"""Define `view` command"""
from __future__ import absolute_import

import logging

from tenhou_log_utils.io import load_mjlog
from tenhou_log_utils.parser import parse_mjlog
from tenhou_log_utils.viewer import print_node

_LG = logging.getLogger(__name__)


def _print_meta(meta_data):
    for tag in ['SHUFFLE', 'GO', 'UN', 'TAIKYOKU']:
        if tag in meta_data:
            print_node(tag, meta_data[tag])


def _print_round(round_data):
    _LG.info('=' * 40)
    for node in round_data:
        print_node(node['tag'], node['data'])


def main(args):
    """Entry point for `view` command."""
    data = parse_mjlog(load_mjlog(args.input))
    _print_meta(data['meta'])

    if args.round:
        rounds = [data['rounds'][args.round]]
    else:
        rounds = data['rounds']

    for round_data in rounds:
        _print_round(round_data)
