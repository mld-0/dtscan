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
#   {{{2
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
    dtrange = DTRange()

    _arg_debug = "-v"

    #   About: simplified clirange(), calls parser function for given args_list
    def runtest_parseargs(self, args_list):
    #   {{{
        print("%s" % str(self._printdebug_tests_leading))
        _Parsers_AssignFunc_clirange(self.dtrange)
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

        self.assertTrue((result_list is not None), "None result")
        return result_list
        #   }}}

    #   About: start/end=0 should be the current date only for a given interval
    def test_qfintervalStartEndZero(self):
    #   {{{
        test_intervals = [ "y", "m", "d" ]
        expected_strftime_format = [ "%Y", "%Y-%m", "%Y-%m-%d" ]
        for arg_interval, expected_format in zip(test_intervals, expected_strftime_format):
            args_list = [ 'range', '--qfinterval', arg_interval, '--qfstart', '0', '--qfend', '0' ]
            expected_result = [ datetime.datetime.now().strftime(expected_format) ]
            test_result = self.runtest_parseargs(args_list)
            self.assertEqual(test_result, expected_result)
    #   }}}

    #   About: test _DTRange_Date_From_Integer() - value of 1 should produce date 1 interval before test_freezetime
    def test_dateFromInteger_One(self):
    #   {{{
        test_freezetime = "2020-11-01"
        test_intervals = [ 'y', 'm', 'w', 'd', 'H', 'M', 'S' ]
        test_datetimes = [ 1, 1, 1, 1, 1, 1, 1 ]
        test_expectedresults  = [ "2019-11-01", "2020-10-01", "2020-10-25", "2020-10-31", "2020-10-31T23:00:00", "2020-10-31T23:59:00", "2020-10-31T23:59:59" ]
        for arg_interval, arg_datetime, expected_result_str in zip(test_intervals, test_datetimes, test_expectedresults):
            expected_result = dateutil.parser.parse(expected_result_str)
            with freeze_time(test_freezetime):
                test_result = self.dtrange._DTRange_Date_From_Integer(arg_datetime, arg_interval)
            message_str = "result=(%s), expected=(%s)" % (str(test_result), str(expected_result))
            self.assertEqual(test_result, expected_result, message_str)
    #   }}}

    def test_dtrangeFromDates_yearly(self):
    #   {{{
        test_freezetime = "2020-11-01"
        arg_interval = 'y'
        args_list = [ 'range', '--qfinterval', arg_interval, '--qfstart', '5', '--qfend', '0' ]
        test_result = None
        expected_result = [ '2015', '2016', '2017', '2018', '2019', '2020' ]
        with freeze_time(test_freezetime):
            test_result = self.runtest_parseargs(args_list)
        self.assertEqual(test_result, expected_result)
    #   }}}

    def test_dtrangeFromDates_monthly(self):
    #   {{{
        test_freezetime = "2020-11-01"
        arg_interval = 'm'
        args_list = [ 'range', '--qfinterval', arg_interval, '--qfstart', '5', '--qfend', '0' ]
        test_result = None
        expected_result = ['2020-06', '2020-07', '2020-08', '2020-09', '2020-10', '2020-11']
        with freeze_time(test_freezetime):
            test_result = self.runtest_parseargs(args_list)
        self.assertEqual(test_result, expected_result)
    #   }}}

    def test_dtrangeFromDates_daily(self):
    #   {{{
        test_freezetime = "2020-11-01"
        arg_interval = 'd'
        args_list = [ 'range', '--qfinterval', arg_interval, '--qfstart', '5', '--qfend', '0' ]
        test_result = None
        expected_result = ['2020-10-27', '2020-10-28', '2020-10-29', '2020-10-30', '2020-10-31', '2020-11-01' ]
        with freeze_time(test_freezetime):
            test_result = self.runtest_parseargs(args_list)
        self.assertEqual(test_result, expected_result)
    #   }}}


#   }}}1

