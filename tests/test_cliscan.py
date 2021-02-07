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
import inspect
import logging
import traceback
#   }}}1
#   {{{1
from dtscan.dtscan import DTScanner
from dtscan.__main__ import _parser_cliscan, dtscanner

#   debug logging
_log = logging.getLogger('dtscan')
_logging_format = "%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime = "%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)


class Test_CliScan(unittest.TestCase):
    #   {{{

    _printdebug_tests_leading = ""
    _printdebug_tests_trailing = "\n"
    _pkg_testdata = "tests.data.test_input"
    _pkg_checkdata = "tests.data.test_check"

    _printdebug_include_test_check_vals = True

    _arg_debug = '-v'

    def _getPath_CheckData(self, arg_fname):
        #   {{{
        path_check = None
        with importlib.resources.path(self._pkg_checkdata, arg_fname) as p:
            path_check = str(p)
        return path_check
        #   }}}

    def _getPath_TestData(self, arg_fname):
        #   {{{
        path_test = None
        with importlib.resources.path(self._pkg_testdata, arg_fname) as p:
            path_test = str(p)
        return path_test
        #   }}}

    def _util_assertExists(self, path_file):
        #   {{{
        self.assertTrue(os.path.isfile(path_file), "file path_file=(%s) not found" % str(path_file))
        #   }}}

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

    #   Continue: 2021-02-06T19:34:56AEDT qffilter tests
    #   Continue: 2021-02-06T19:35:05AEDT rfilter test, historic datetimes, (others)
    #   Continue: 2021-02-06T21:07:33AEDT tests, scandir

    def test_matches(self):
        path_test = self._getPath_TestData("column-datetime.txt")
        path_check = self._getPath_CheckData("column-datetime.txt")
        args_list = ['-I', path_test, 'matches']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    def test_matches_sortdt_pos(self):
        path_test = self._getPath_TestData("vimh-samples-scrambled.txt")
        path_check = self._getPath_CheckData("vimh-samples-scrambled-sortdt-pos.txt")
        args_list = ['--sortdt', '-I', path_test, 'matches', '--pos']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    def test_matches_sortdt(self):
        path_test = self._getPath_TestData("vimh-samples-scrambled.txt")
        path_check = self._getPath_CheckData("vimh-samples-scrambled-sortdt.txt")
        args_list = ['--sortdt', '-I', path_test, 'matches']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    def test_matches_col0(self):
        path_test = self._getPath_TestData("column-datetime.txt")
        path_check = self._getPath_CheckData("column-datetimes-col0.txt")
        args_list = ['-I', path_test, '--col', '0', 'matches']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    def test_matches_col1(self):
        path_test = self._getPath_TestData("column-datetime.txt")
        path_check = self._getPath_CheckData("column-datetimes-col1.txt")
        args_list = ['-I', path_test, '--col', '1', 'matches']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    def test_matches_col2(self):
        path_test = self._getPath_TestData("column-datetime.txt")
        path_check = self._getPath_CheckData("column-datetimes-col2.txt")
        args_list = ['-I', path_test, '--col', '2', 'matches']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    def test_matches_col3(self):
        path_test = self._getPath_TestData("column-datetime.txt")
        path_check = self._getPath_CheckData("column-datetimes-col3.txt")
        args_list = ['-I', path_test, '--col', '3', 'matches']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    def test_matches_noassumetz(self):
        path_test = self._getPath_TestData("mixed-text-datetimes.txt")
        path_check = self._getPath_CheckData("mixed-text-datetimes-matches-noassumetz.txt")
        args_list = ['-I', path_test, '--noassumetz', 'matches']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   scan with chronological sort
    def test_scan_sortdt(self):
        path_test = self._getPath_TestData("vimh-samples-scrambled.txt")
        path_check = self._getPath_TestData("vimh-samples.txt")
        args_list = ['-I', path_test, '--sortdt', 'scan']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   matches with chronological sort
    def test_matches_sortdt_linenums(self):
        path_test = self._getPath_TestData("vimh-samples-scrambled.txt")
        path_check = self._getPath_CheckData("vimh-samples-scrambled-sortdt-pos.txt")
        args_list = ['-I', path_test, '--sortdt', 'matches', '--pos']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    def test_matches_sortdt_order(self):
        path_test = self._getPath_TestData("mixed-text-datetimes.txt")
        path_check = self._getPath_CheckData("mixed-text-datetimes-sorted-pos.txt")
        args_list = ['-I', path_test, '--sortdt', 'matches', '--pos']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   compare input to itself - given no arguments, scan should output same stream as input
    def test_scan_helloworld(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_TestData("vimh-samples.txt")
        args_list = ['-I', path_test, 'scan']
        _test_result = None
        self._util_assertExists(path_test)
        with freeze_time("2020-11-01"):
            _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   splitsum by days
    def test_splitsum_d(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-splitsum-d-dhms.txt")
        args_list = ['-I', path_test, 'splitsum', '--interval', 'd']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   splitsum by months
    def test_splitsum_m(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-splitsum-m-dhms.txt")
        args_list = ['-I', path_test, 'splitsum', '--interval', 'm']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   splitsum by years
    def test_splitsum_y(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-splitsum-y-dhms.txt")
        args_list = ['-I', path_test, 'splitsum', '--interval', 'y']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   splitsum with seconds output
    def test_splitsum_nodhms(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-splitsum-s.txt")
        args_list = ['-I', path_test, '--nodhms', 'splitsum']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   deltas
    def test_deltas(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-deltas-dhms.txt")
        args_list = ['-I', path_test, 'deltas']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   deltas with seconds output
    def test_deltas_nodhms(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-deltas-s.txt")
        args_list = ['-I', path_test, '--nodhms', 'deltas']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   count by days
    def test_count_d(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-count-d.txt")
        args_list = ['-I', path_test, 'count', '--interval', 'd']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   count by months
    def test_count_m(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-count-m.txt")
        args_list = ['-I', path_test, 'count', '--interval', 'm']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   count by years
    def test_count_y(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-count-y.txt")
        args_list = ['-I', path_test, 'count', '--interval', 'y']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   count by hours
    def test_count_H(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-count-H.txt")
        args_list = ['-I', path_test, 'count', '--interval', 'H']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   split by 300s
    def test_splits300(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-split300-dhms.txt")
        args_list = ['-I', path_test, 'splits', '--splitlen', '300']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   split by 60s
    def test_splits60(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-split60-dhms.txt")
        args_list = ['-I', path_test, 'splits', '--splitlen', '60']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   split by 60s, seconds output
    def test_splits60_nodhms(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-split60-s.txt")
        args_list = ['-I', path_test, '--nodhms', 'splits', '--splitlen', '60']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   get specific items within ~27M interval
    def test_scan_rfNov27Minutes(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-Nov27Minutes.txt")
        args_list = ['-I', path_test, "--rfstart", "2020-11-27T22:24:10AEDT", "--rfend", "2020-11-27T22:25:55AEDT", 'scan']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   Get entries from March
    def test_scan_rfMar(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-Mar.txt")
        args_list = ['-I', path_test, "--rfstart", "2020-03-01", "--rfend", "2020-04-01", 'scan']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   Backwards range-filter date range
    def test_scan_rfNovBackward27Minutes(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-Nov27Minutes.txt")
        args_list = ['-I', path_test, "--rfstart", "2020-11-27T22:25:55AEDT", "--rfend", "2020-11-27T22:24:10AEDT", 'scan']
        with self.assertRaises(Exception) as context:
            _test_result = self.runtest_parseargs(args_list)
            self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   quick-filter for current (November) month
    def test_scan_qfMonthqfStart0(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-Nov.txt")
        args_list = ['-I', path_test, '--qfinterval', 'm', '--qfstart', '0', 'scan']
        _test_result = None
        self._util_assertExists(path_test)
        with freeze_time("2020-11-01"):
            _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   quick-filter, same start and end date
    def test_scan_qfMonthqfStartEndNov(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-Nov.txt")
        args_list = ['-I', path_test, '--qfinterval', 'm', '--qfstart', '2020-11', '--qfend', '2020-11', 'scan']
        _test_result = None
        self._util_assertExists(path_test)
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   quick-filter, backwards date range
    def test_scan_qfMonthqfStartNovEndOct(self):
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-Nov.txt")
        args_list = ['-I', path_test, '--qfinterval', 'm', '--qfstart', '2020-11', '--qfend', '2020-10', 'scan']
        _test_result = None
        self._util_assertExists(path_test)
        with self.assertRaises(Exception) as context:
            _test_result = self.runtest_parseargs(args_list)

#   def test_matches_historic(self):
#       pass
#   #   Other was of specifying qf/rf date ranges
#   def test_scan_qfstartend(self):
#       pass
#   def test_scan_rfstartend(self):
#       pass
#       {{{
#       test cases:
#       scan (hello world)
#           scan
#       scan, current month:
#           scan --qfinterval m --qfnum 0
#       scan, current and previous month:
#           scan --qfinterval m --qfnum 1
#       scan, Nov
#           scan --qfstart 2020-11 --qfend 2020-11
#       scan, May-Aug
#           scan --qfstart 2020-05 --qfend 2020-08
#       scan dayrange, Oct-Nov
#           scan --qfinterval d --qfstart 2020-10 --qfend 2020-11
#           <more qfstart/qfend>
#       scan range
#           scan --rfstart 2020-11-27T22:24:10 --rfend 2020-11-27T22:26:00AEDT
#           <more rfstart/rfend>
#       scan, chronological sort
#           scan --sortdt
#       matches, only first column
#           matches --col 1
#       matches,
#       count <interval>
#       splits
#       deltas
#       splitsum
#       }}}

    #   }}}

#   }}}1
