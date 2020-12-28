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
from dtscan.__main__ import _Parsers_AssignFunc_cliscan, _parser_cliscan

#   debug logging
_log = logging.getLogger('dtscan')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
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
    _pkg_testdata = "data.test_input"
    _pkg_checkdata = "data.test_check"

    dtscan_instance = DTScanner()
    dtscan_instance._assume_LocalTz = True
    dtscan_instance._warn_LocalTz = True
    dtscan_instance._printdebug_func_inputs = True
    dtscan_instance._printdebug_func_outputs = True

    _arg_debug = '-v'

    def _util_assertExists(self, path_file):
        self.assertTrue(os.path.isfile(path_file), "file path_file=(%s) not found" % str(path_file))

    #   About: Compare (result stream or list of streams) with (path check of list of paths)
    def runtest_CompareStreamListAndCheckFileList(self, stream_test, path_check):
    #   {{{
    #   Ongoing: 2020-11-29T13:46:41AEDT using filecmp.cmp() for comparison, does not permit traililing newline in checkfile if not present in stream (as the custom line-by-line check from test-methods.py does)
    #   Ongoing: 2020-11-30T22:53:06AEDT This is a comparision of a stream to a file, not of two streams (and the stream must be a file)
    #   Ongoing: 2020-12-02T13:44:53AEDT require that stream_test is either a stream, or a list of streams of length 1 -> (or, stream-test/path_check are lists of the same length)
        sys.stderr.write("path_check=(%s)\n" % str(path_check))
        flag_print_diff = False
        flag_print_actualResults = True
        func_caller = inspect.stack()[1][3]
        #   Ongoing: 2020-11-29T12:19:09AEDT If stream is not a file we can locate, instead compare stream_test and path_check line-by-line
        #   If given multiple streams, and one checkfile, compare combined stream to checkfile. If streams list and check list are the same lenght, compare indervidually. 
        #if not isinstance(path_check, list):
        #    path_check = [ path_check ]
        #if not isinstance(stream_test, list):
        #    stream_test = [ stream_test ]
        #if len(stream_test) != len(path_check) and len(path_check) == 1:
        #    stream_test = self._util_CombineStreams(stream_test)
        #if not len(path_check) == 1 and not len(stream_test) == len(path_check):
        #    raise Exception("invalid input, stream_test=(%s), path_check=(%s), len(stream_test)=(%s), len(path_check)=(%s)" % (str(sream_test), str(path_check), str(len(stream_test)), str(len(path_check))))
        #for loop_stream_test, loop_path_check in zip(stream_test, path_check):
        self._util_assertExists(path_check)
        result_compare = None
        path_stream_test = os.path.realpath(stream_test.name)
        sys.stderr.write("path_stream_test=(%s)\n" % str(path_stream_test))
        count_lines_test = 0
        count_lines_check = 0
        with open(path_check, "r") as f:
            for line in f:
                count_lines_check += 1
        with open(path_stream_test, "r") as f:
            for line in f:
                count_lines_test += 1
        if (os.path.isfile(path_stream_test)):
            filecmp.clear_cache()
            result_compare = filecmp.cmp(path_stream_test, path_check, shallow=False)
            message_compare = "expected files to match, %s v %s lines, Set 'flag_print_diff' to see differences, or 'flag_print_actualResults' to see actual result, %s, %s" % (str(count_lines_test), str(count_lines_check), str(path_stream_test), str(path_check))
            #   {{{
            if not (result_compare):
            #   Prevent resource warnings by closing stream if test is about to fail
                stream_test.close()
            if not (result_compare) and (flag_print_diff):
            #   if given flag, print differing lines between test/check
                for line_diff in difflib.unified_diff(open(path_check).readlines(), open(path_stream_test).readlines()):
                    print(line_diff.strip())
            if not (result_compare) and (flag_print_actualResults):
                sys.stderr.write("begin actualResults\n")
                with open(path_stream_test, "r") as f:
                    for loop_line in f:
                        sys.stderr.write(loop_line.strip())
                        sys.stderr.write("\n")
                sys.stderr.write("end actualResults\n")
            #   }}}
            self.assertTrue(result_compare, message_compare)
        else:
            raise Exception("Unable to determine stream_test filepath %s" % str(path_stream_test))
        stream_test.close()
    #   }}}

    #   TODO: 2020-12-12T19:46:37AEDT test method does not account for newlines between streams, unique item headings - which are in the output from (actual) cli dtscan usage (see __main__.py)
    #   About: Simulate cli usage with args_list 
    def runtest_parseargs(self, args_list, arg_flag_expectStreamList=True):
    #   {{{
        print("%s" % str(self._printdebug_tests_leading))
        _Parsers_AssignFunc_cliscan(self.dtscan_instance)
        if (len(self._arg_debug) > 0):
            args_list.insert(0, self._arg_debug)
        args = _parser_cliscan.parse_args(args_list)
        _test_result = None
        #if (args.debug):
        #    #logging.basicConfig(level=logging.DEBUG)
        #    _log.debug("Enable debugging")
        #    self.dtscan_instance._printdebug_func_inputs = True
        #    self.dtscan_instance._printdebug_func_outputs = True
        #    if (_flag_printargs):
        #        self.dtscan_instance._PrintArgs(args, _parser_cliscan)
        if not hasattr(args, 'func'):
            raise Exception("No subparser command given\n")
        try:
            _test_result = args.func(args)
        except Exception as e:
            _log.error("%s\n%s, %s, for 'args.func(args)' (%s)" % (str(traceback.format_exc()), str(type(e)), str(e), str(args.func.__name__)))
        #   Verify that _test_result is a list containing TextIOWrapper instances
        #   {{{
        self.assertTrue(isinstance(_test_result, io.TextIOWrapper), "Expect TextIOWrapper_test_result=(%s)" % str(type(_test_result)))
            #for loop_result in _test_result:
            #    self.assertTrue(isinstance(loop_result, io.TextIOWrapper), "Expect TextIOWrapper loop_result=(%s)" % str(type(loop_result)))
        #   }}}
        return _test_result
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

    #   {{{
    #   test cases: 
    #   scan (hello world)
    #       scan
    #   scan, current month: 
    #       scan --qfinterval m --qfnum 0 
    #   scan, current and previous month: 
    #       scan --qfinterval m --qfnum 1
    #   scan, Nov
    #       scan --qfstart 2020-11 --qfend 2020-11
    #   scan, May-Aug
    #       scan --qfstart 2020-05 --qfend 2020-08
    #   scan dayrange, Oct-Nov
    #       scan --qfinterval d --qfstart 2020-10 --qfend 2020-11
    #       <more qfstart/qfend>
    #   scan range
    #       scan --rfstart 2020-11-27T22:24:10 --rfend 2020-11-27T22:26:00AEDT
    #       <more rfstart/rfend>
    #   scan, chronological sort
    #       scan --sortdt
    #   matches, only first column
    #       matches --col 1
    #   matches, 
    #   count <interval>
    #   splits
    #   deltas
    #   splitsum
    #   }}}

    def test_matches_sortdt_order(self):
        path_test = self._getPath_TestData("mixed-text-datetimes.txt")
        path_check = self._getPath_CheckData("mixed-text-datetimes-sorted-pos.txt")
        args_list = [ '-I', path_test, 'matches', '--sortdt', '--pos' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)

    #   compare input to itself - given no arguments, scan should output same stream as input
    def test_scan_helloworld(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_TestData("vimh-samples.txt")
        args_list = [  '-I', path_test, 'scan' ]
        _test_result = None
        self._util_assertExists(path_test)
        with freeze_time("2020-11-01"):
            _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   splitsum by days
    def test_splitsum_d(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-splitsum-d-dhms.txt")
        args_list = [ '-I', path_test, 'splitsum', '--interval', 'd']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   splitsum by months
    def test_splitsum_m(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-splitsum-m-dhms.txt")
        args_list = [ '-I', path_test, 'splitsum', '--interval', 'm']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   splitsum by years
    def test_splitsum_y(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-splitsum-y-dhms.txt")
        args_list = [ '-I', path_test, 'splitsum', '--interval', 'y']
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   splitsum with seconds output
    def test_splitsum_nodhms(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-splitsum-s.txt")
        args_list = [ '-I', path_test, '--nodhms', 'splitsum' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   deltas
    def test_deltas(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-deltas-dhms.txt")
        args_list = [ '-I', path_test, 'deltas' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   deltas with seconds output
    def test_deltas_nodhms(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-deltas-s.txt")
        args_list = [ '-I', path_test, '--nodhms', 'deltas' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   count by days
    def test_count_d(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-count-d.txt")
        args_list = [ '-I', path_test, 'count', '--interval', 'd' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   count by months
    def test_count_m(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-count-m.txt")
        args_list = [ '-I', path_test, 'count', '--interval', 'm' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   count by years
    def test_count_y(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-count-y.txt")
        args_list = [ '-I', path_test, 'count', '--interval', 'y' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   count by hours
    def test_count_H(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-count-H.txt")
        args_list = [ '-I', path_test, 'count', '--interval', 'H' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   split by 300s
    def test_splits300(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-split300-dhms.txt")
        args_list = [ '-I', path_test, 'splits', '--splitlen', '300' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   split by 60s
    def test_splits60(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-split60-dhms.txt")
        args_list = [ '-I', path_test, 'splits', '--splitlen', '60' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   split by 60s, seconds output
    def test_splits60_nodhms(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-split60-s.txt")
        args_list = [ '-I', path_test, '--nodhms', 'splits', '--splitlen', '60' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   matches in column 2 
    def test_matches_col2(self):
    #   {{{
        path_test = self._getPath_TestData("column-datetime.txt")
        path_check = self._getPath_CheckData("column-datetimes-col2.txt")
        args_list = [  '-I', path_test, 'matches', '--col', '2' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   matches in column 1
    def test_matches_col1(self):
    #   {{{
        path_test = self._getPath_TestData("column-datetime.txt")
        path_check = self._getPath_CheckData("column-datetimes-col1.txt")
        args_list = [  '-I', path_test, 'matches', '--col', '1' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   matches in column 0
    def test_matches_col0(self):
    #   {{{
        path_test = self._getPath_TestData("column-datetime.txt")
        path_check = self._getPath_CheckData("column-datetimes-col0.txt")
        args_list = [  '-I', path_test, 'matches', '--col', '0' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   matches in column 3
    def test_matches_col3(self):
    #   {{{
        path_test = self._getPath_TestData("column-datetime.txt")
        path_check = self._getPath_CheckData("column-datetimes-col3.txt")
        args_list = [  '-I', path_test, 'matches', '--col', '3' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   get specific items within ~27M interval
    def test_scan_rfNov27Minutes(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-Nov27Minutes.txt")
        args_list = [  '-I', path_test, 'scan', "--rfstart", "2020-11-27T22:24:10", "--rfend", "2020-11-27T22:25:55AEDT" ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   get specific items within ~27M interval
    def test_scan_rfMar(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-Mar.txt")
        args_list = [  '-I', path_test, 'scan', "--rfstart", "2020-03-01", "--rfend", "2020-04-01" ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   Backwards range-filter date range
    def test_scan_rfNovBackward27Minutes(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-Nov27Minutes.txt")
        args_list = [  '-I', path_test, 'scan', "--rfstart", "2020-11-27T22:25:55AEDT", "--rfend", "2020-11-27T22:24:10" ]
        with self.assertRaises(Exception) as context:
            _test_result = self.runtest_parseargs(args_list)
    #   }}}

    #   quick-filter for current (Novemeber) month
    def test_scan_qfMonthqfStart0(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-Nov.txt")
        args_list = [  '-I', path_test, 'scan', '--qfinterval', 'm', '--qfstart', '0' ]
        _test_result = None
        self._util_assertExists(path_test)
        with freeze_time("2020-11-01"):
            _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   quick-filter, same start and end date
    def test_scan_qfMonthqfStartEndNov(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-Nov.txt")
        args_list = [  '-I', path_test, 'scan', '--qfinterval', 'm', '--qfstart', '2020-11', '--qfend', '2020-11' ]
        _test_result = None
        self._util_assertExists(path_test)
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   quick-filter, backwards date range
    def test_scan_qfMonthqfStartNovEndOct(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples.txt")
        path_check = self._getPath_CheckData("vimh-samples-Nov.txt")
        args_list = [  '-I', path_test, 'scan', '--qfinterval', 'm', '--qfstart', '2020-11', '--qfend', '2020-10' ]
        _test_result = None
        self._util_assertExists(path_test)
        with self.assertRaises(Exception) as context:
            _test_result = self.runtest_parseargs(args_list)
    #   }}}

    #   scan with chronological sort
    def test_scan_sortdt(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples-scrambled.txt")
        path_check = self._getPath_TestData("vimh-samples.txt")
        args_list = [   '-I', path_test, 'scan', '--sortdt' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}

    #   matches with chronological sort
    def test_matches_sortdt_linenums(self):
    #   {{{
        path_test = self._getPath_TestData("vimh-samples-scrambled.txt")
        path_check = self._getPath_CheckData("vimh-samples-scrambled-sortdt-pos.txt")
        args_list = [ '-I', path_test, 'matches', '--pos', '--sortdt' ]
        _test_result = self.runtest_parseargs(args_list)
        self.runtest_CompareStreamListAndCheckFileList(_test_result, path_check)
    #   }}}


#   }}}

#   }}}1

