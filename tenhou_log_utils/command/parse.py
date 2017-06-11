"""Define `parse` command"""
from __future__ import absolute_import

import json
import logging

from tenhou_log_utils.io import load_mjlog
from tenhou_log_utils.parser import parse_mjlog

_LG = logging.getLogger(__name__)


def main(args):
    """Entry point for `parse` command."""
    data = parse_mjlog(load_mjlog(args.input), tags=args.tags)
    _LG.info(json.dumps(data, indent=2))
