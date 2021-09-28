"""
This is a fake package for testing.
"""

__version__ = '1.2.3'

from pathlib import Path
from pprint import pprint
THIS_FILE_DIR = Path(__file__).resolve().parent


def call_and_return(to_call, what='__file__', **kwargs):
    if what == '__file__':
        args = [Path(__file__)]
        kwargs = {'use_output_numbering': True, 'use_rule_seperator': True, 'rule_seperator_char': ',', 'use_prefix': True, 'use_extra_newline_pre': True, 'use_extra_newline_post': True}
    return to_call(*args, **kwargs)
