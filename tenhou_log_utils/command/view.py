"""Define `view` command"""
from __future__ import absolute_import

from tenhou_log_utils.parser import parse_node
from tenhou_log_utils.viewer import print_node


def main(args):
    """Entry point for `view` command."""
    from tenhou_log_utils.io import load_mjlog
    n_init = 0
    round_to_view = args.round
    for node in load_mjlog(args.input):
        result = parse_node(node.tag, node.attrib)
        if result['tag'] == 'INIT':
            n_init += 1
        if (
                round_to_view is None or  # view all rounds
                round_to_view == n_init or  # view only current round
                result['tag'] in ['SHUFFLE', 'GO', 'UN', 'TAIKYOKU']
        ):
            print_node(result['tag'], result['data'])
