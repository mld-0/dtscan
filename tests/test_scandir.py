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
import pprint
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

    _printdebug_tests_leading = ""
    _printdebug_tests_trailing = "\n"
    _pkg_testdata = "tests.data.test_input"
    _pkg_checkdata = "tests.data.test_check"
    _printdebug_include_test_check_vals = True

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
#    def runtest_parseargs(self, args_list, arg_flag_expectStreamList=True):
#        #   {{{
#        print("%s" % self._printdebug_tests_leading, end='')
#
#        if (len(self._arg_debug) > 0):
#            args_list.insert(0, self._arg_debug)
#        _args = _parser_cliscan.parse_args(args_list)
#
#        capturedOutput = io.StringIO()
#
#        if not hasattr(_args, 'func'):
#            raise Exception("No subparser command given\n")
#        sys.stdout = capturedOutput
#        _args.func(_args)
#        sys.stdout = sys.__stdout__
#
#        print("%s" % self._printdebug_tests_trailing, end='')
#
#        return capturedOutput
#        #   }}}

    def runtest_parseargs(self, args_list, arg_flag_expectStreamList=True):
        #   {{{
        print("%s" % self._printdebug_tests_leading, end='')

        if (len(self._arg_debug) > 0):
            args_list.insert(0, self._arg_debug)
        _args = _parser_cliscan.parse_args(args_list)

        capturedOutput = io.StringIO()

        if not hasattr(_args, 'func'):
            raise Exception("No subparser command given\n")
        # try:
        sys.stdout = capturedOutput
        _args.func(_args)
        sys.stdout = sys.__stdout__
        # except Exception as e:
        #    _log.error("%s\n%s, %s, for '_args.func(_args)' (%s)" % (str(traceback.format_exc()), str(type(e)), str(e), str(_args.func.__name__)))

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

    def read_scandir_datetimeitems_transposedlist_file(self, path_checkfile):
        """Read results of scandir_datetimeitems_results_to_transposedlist() (with surrounding '()' removed) into list-of-lists matching origional output of scandir_datetimeitems()"""
        #   {{{
        check_list = []
        _delim = '\t'
        f = open(path_checkfile, "r")
        for loop_line in f:
            loop_line = loop_line[:-1]  # remove last character - newline
            loop_line_split = loop_line.split(_delim)
            check_list.append([])
            check_list[-1].append(loop_line_split[0])
            check_list[-1].append(loop_line_split[1])
            check_list[-1].append(int(loop_line_split[2]))
            loop_fileline = ""
            for loop_join in loop_line_split[3:]:
                loop_fileline += loop_join + _delim
            loop_fileline = loop_fileline[:-1]
            check_list[-1].append(loop_fileline)
        check_list = list(map(list, zip(*check_list)))
        f.close()
        return check_list
        #   }}}

    def scandir_datetimeitems_results_to_transposedlist(self, results_test):
        """Output results of scandir_datetimeitems in such a way that (with surrounding '()' removed), read_scandir_datetimeitems_transposedlist_file() can read them into an identical list of lists"""
        #   {{{
        results_test = list(zip(*results_test))
        for loop_result in results_test:
            loop_line = ""
            _delim = "\t"
            for loop_item in loop_result:
                loop_line += str(loop_item) + _delim
            loop_line = loop_line[:-1]
            #print(loop_line, end="")
            print(f"({loop_line})")  # using () to preserve any trailign whitespace when copying result into 'check' file (without it -> Pipe results directly to file)
        #   }}}

    def test_cli_scandir_matches(self):
        path_scandir = self._getPath_ScanDir()
        path_check = self._getPath_CheckData("scandir-cli-results.txt")
        test_args = ['scandir', '--dir', path_scandir]
        test_results = self.runtest_parseargs(test_args)
        self.runtest_CompareStreamListAndCheckFileList(test_results, path_check)

    def test_cli_scandir_matches_sortdt(self):
        path_scandir = self._getPath_ScanDir()
        path_check = self._getPath_CheckData("scandir-cli-sorted-results.txt")
        test_args = ['--sortdt', 'scandir', '--dir', path_scandir]
        test_results = self.runtest_parseargs(test_args)
        self.runtest_CompareStreamListAndCheckFileList(test_results, path_check)

    def test_scandir_matches(self):
        path_scandir = self._getPath_ScanDir()
        path_check = self._getPath_CheckData("scandir-results.txt")
        results_check = self.read_scandir_datetimeitems_transposedlist_file(path_check)
        _log.debug("path_scandir=(%s)" % str(path_scandir))
        results_test = self.dtscan_instance.scandir_datetimeitems(path_scandir)
        self.assertEqual(results_test, results_check)
        #   {{{
        #   print test results in 'check' format
        #self.scandir_datetimeitems_results_to_transposedlist(results_test)
        #   compare test, check lists line-by-line
        #print(results_test == results_check)
        #results_test_transpose = list(map(list, zip(*results_test)))
        #results_check_transpose = list(map(list, zip(*results_check)))
        #for loop_test, loop_check in zip(results_test_transpose, results_check_transpose):
        #    print(loop_test == loop_check)
        #    print(f"loop_test=({loop_test})")
        #    print(f"loop_check=({loop_check})")
        #   }}}


    #   }}}

#   }}}1
