"""Module for searching/parsing mjinfo file"""
import re
import sys
import glob
import os.path
import logging

from tenhou_log_utils.io import ensure_unicode, unquote

_LG = logging.getLogger(__name__)


def _fetch_subdir_paths(path):
    subdirs = [os.path.join(path, subdir) for subdir in os.listdir(path)]
    return [subdir for subdir in subdirs if os.path.isdir(subdir)]


def _get_flash_root_mac():
    home = os.path.expanduser('~')
    platform_dirs = [
        # Default (Firefox)
        ('Library', 'Preferences', 'Macromedia', 'Flash Player',),
        # Chrome
        (
            'Library', 'Application Support', 'Google', 'Chrome',
            'Default', 'Pepper Data', 'Shockwave Flash', 'WritableRoot',
        ),
    ]
    return [os.path.join(home, *platform) for platform in platform_dirs]


def _get_sol_files(root_dirs):
    path = ('#SharedObjects', '*', 'mjv.jp', 'mjinfo.sol')
    ret = []
    for root_dir in root_dirs:
        ret.extend(glob.glob(os.path.join(root_dir, *path)))
    return ret


def _parse_sol_file_line(line):
    ret = {}
    for component in unquote(ensure_unicode(line)).split('&'):
        match = re.match('(.*)=(.*)', component)
        key, value = match.group(1, 2)
        if key.startswith('un'):
            value = value
        ret[key] = value
    return ret


def parse_sol_file(filepath):
    """Parse SOL file to extract game infomation.

    Parameters
    ----------
    filepath : str
        Path to SOL file

    Returns
    -------
    list of dict
        Information found in the SOL file, such as ID, player names, scores.
    """
    with open(filepath, 'rb') as file_:
        ret = []
        for line in file_:
            if line.startswith(b'file='):
                ret.append(_parse_sol_file_line(line))
        return ret


def _parse_flash_dirs(root_dirs):
    logs = {}
    for sol_file in _get_sol_files(root_dirs):
        logs[sol_file] = parse_sol_file(sol_file)
    return logs


def parse_mjinfo():
    """List up game history stored in Flash cache directory

    Returns
    -------
    dict
        Key : str
            File name in which data are stored
        Value : list of dict
            Information of logs. See :func:`parse_sol`.
    """
    if sys.platform == 'darwin':
        root_dirs = _get_flash_root_mac()
    else:
        raise NotImplementedError(
            '`list` function is not implemented for %s' % sys.platform)
    return _parse_flash_dirs(root_dirs)
