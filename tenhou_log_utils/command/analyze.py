"""Define `analyze` command behavior"""
from __future__ import absolute_import

import logging

from tenhou_log_utils.io import load_mjlog
from tenhou_log_utils.parser import parse_mjlog
from tenhou_log_utils.analyzer import analyze_mjlog

_LG = logging.getLogger(__name__)


def main(args):
    """Entry potin for `analyze` command."""
    logging.getLogger('tenhou_log_utils.parser').setLevel(logging.WARN)
    analyze_mjlog(parse_mjlog(load_mjlog(args.input)))
