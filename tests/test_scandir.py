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
from freezegun import freeze_time
#   pandas must be imported *before* any freezegun fake times are used
import pandas
#   }}}1
#   {{{1
from dtscan.dtscan import DTScanner
# from dtscan.__main__ import _Parsers_AssignFunc_cliscan, _parser_cliscan
from dtscan.__main__ import _parser_cliscan, dtscanner

#   debug logging
_log = logging.getLogger('dtscan')
_logging_format = "%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime = "%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)


class Test_CliScan(unittest.TestCase):
    #   {{{

    #   flags
    #   {{{
    _printdebug_tests = True
    _printdebug_tests_inputs = True
    _printdebug_tests_intermediate = True
    _printdebug_tests_leading = "\n"
    #   }}}
    _pkg_testdata = "tests.data.test_input"
    _pkg_checkdata = "tests.data.test_check"

    dtscan_instance = DTScanner()
    dtscan_instance._assume_LocalTz = True
    dtscan_instance._warn_LocalTz = True
    dtscan_instance._printdebug_func_inputs = True
    dtscan_instance._printdebug_func_outputs = True

    _arg_debug = '-v'

    def _util_assertExists(self, path_file):
        self.assertTrue(os.path.isfile(path_file), "file path_file=(%s) not found" % str(path_file))

    #   TODO: 2020-12-12T19:46:37AEDT test method does not account for newlines between streams, unique item headings - which are in the output from (actual) cli dtscan usage (see __main__.py)
    #   About: Simulate cli usage with args_list
    def runtest_parseargs(self, args_list, arg_flag_expectStreamList=True):
        #   {{{
        print("%s" % self._printdebug_tests_leading, end='')

        if (len(self._arg_debug) > 0):
            args_list.insert(0, self._arg_debug)
        _args = _parser_cliscan.parse_args(args_list)

        capturedOutput = io.StringIO()

        if not hasattr(_args, 'func'):
            raise Exception("No subparser command given\n")
        sys.stdout = capturedOutput
        _args.func(_args)
        sys.stdout = sys.__stdout__

        print("%s" % self._printdebug_tests_trailing, end='')

        return capturedOutput
        #   }}}

    #   About: Compare (result stream or list of streams) with (path check of list of paths)
    def runtest_CompareStreamListAndCheckFileList(self, stream_test, path_check):
        #   {{{
        sys.stderr.write("path_check:\n%s\n" % str(path_check))

        stream_test_text = stream_test.getvalue()
        stream_check_text = None
        with open(path_check, "r") as f:
            stream_check_text = f.read()

        if (self._printdebug_include_test_check_vals):
            print("test results:")
            print(stream_test_text)
            print("check:")
            print(stream_check_text)

        self.maxDiff = None
        self.assertEqual(stream_test_text, stream_check_text)
        #   }}}

    def _getPath_CheckData(self, arg_fname):
        path_check = None
        with importlib.resources.path(self._pkg_checkdata, arg_fname) as p:
            path_check = str(p)
        return path_check

    def _getPath_TestData(self, arg_fname):
        path_test = None
        with importlib.resources.path(self._pkg_testdata, arg_fname) as p:
            path_test = str(p)
        return path_test

    def _getPath_ScanDir(self):
        """Get path to directory 'scandir' inside tests.data.test_input"""
        import os
        import tests.data.test_input.scandir
        path_scandir = None
        try:
            path_lookup = tests.data.test_input.__file__
            path_testinput = os.path.dirname(path_lookup)
            path_scandir = os.path.join(path_testinput, "scandir")
        except Exception as e:
            _log.debug("%s, %s" % (type(e), str(e)))
        self.assertTrue(os.path.isdir(path_scandir), "Failed to find scandir path=(%s)" % str(path_scandir))
        return path_scandir

    #def test_Interface_ScanDir_Matches(self):
    #    path_scandir = self._getPath_ScanDir()
    #    _log.debug("path_scandir=(%s)" % str(path_scandir))
    #    results_test = self.dtscan_instance._ScanDir_ScanFileMatches(path_scandir)
    #    print(results_test)

    def test_Interface_ScanDir_ScanFileMatches(self):
        import pprint
        path_scandir = self._getPath_ScanDir()
        _log.debug("path_scandir=(%s)" % str(path_scandir))
        results_test = self.dtscan_instance.Interface_ScanDir_ScanFileMatches(path_scandir, True, True, True)
        pprint.pprint(results_test)

    #   }}}

#   }}}1
