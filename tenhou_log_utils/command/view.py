"""Define `view` command"""
from __future__ import absolute_import

from tenhou_log_utils.parser import parse_node
from tenhou_log_utils.viewer import print_node


def view_mjlog(args):
    """Entry point for `view` command."""
    from tenhou_log_utils.io import load_mjlog
    for node in load_mjlog(args.input):
        result = parse_node(node.tag, node.attrib)
        print_node(result['tag'], result['data'])
