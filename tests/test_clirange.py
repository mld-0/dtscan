#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   {{{3
import importlib
import unittest
import os
import sys
import datetime
import dateutil
import logging
import io
import filecmp
from subprocess import Popen, PIPE
from unittest.mock import patch
from freezegun import freeze_time
import difflib
#   pandas must be imported *before* any freezegun fake times are used
import pandas
import inspect
import sys
import argparse
import logging
import traceback
#   }}}1
#   {{{1
from dtscan.dtscan import DTScanner
from dtscan.dtrange import DTRange
from dtscan.__main__ import _Parsers_AssignFunc_clirange, _parser_clirange

#   debug logging
_log = logging.getLogger('dtscan')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

class Test_CliRange(unittest.TestCase):
    _printdebug_tests_leading = "\n"

    _arg_debug = "-v"

    def runtest_parseargs(self, args_list):
        dtrange = DTRange()
        print("%s" % str(self._printdebug_tests_leading))
        _Parsers_AssignFunc_clirange(dtrange)
        _args = _parser_clirange.parse_args(args_list)

        if not hasattr(_args, 'func'):
            _log.error("No command given")
            _parser_clirange.print_help()
            sys.exit(2)
        result_list = None
        try:
            result_list = _args.func(_args)
        except Exception as e:
            _log.error("%s\n%s, %s, for '_args.func(_args)' (%s)" % (str(traceback.format_exc()), str(type(e)), str(e), str(_args.func.__name__)))
            try:
                _args.print_help()
            except Exception as e:
                _log.error("%s, %s, failed to call print_help() after initial exception processing '_args.func(_args)'" % (str(type(e)), str(e)))
            #sys.exit(2)
        if (result_list is None):
            _log.debug("None result, exit")
            #sys.exit(0)

        #for loop_line in result_list:
        #    #   remove trailing newline:
        #    loop_line = loop_line.rstrip()
        #    print(loop_line)
        #    pass

    def test_helloworld(self):
        args_list = [ 'range', '--qfinterval', 'm', '--qfstart', '0' ]
        _test_result = self.runtest_parseargs(args_list)



#   }}}1

