#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   {{{3
import operator
import shutil
import logging
import argparse
import subprocess
import io
import os
import argcomplete
import inspect
import sys
import os
import importlib
import importlib.resources
import math
import csv
import time
import glob
import platform
import inspect
import re
import time
import pytz
import pprint
import textwrap
import dateutil.parser
import dateutil.tz
import dateutil.relativedelta 
import time
import tempfile
import decimal
import logging
from subprocess import Popen, PIPE, STDOUT
from os.path import expanduser
from pathlib import Path
from datetime import datetime, timedelta, date
from subprocess import Popen, PIPE, STDOUT
from io import StringIO
from tzlocal import get_localzone
from dateutil.relativedelta import relativedelta
#   }}}1
#   {{{1
from .dtconvert import DTConvert
from .dtrange import DTRange
from .dtsplit import DTsplit
from .dtposition import DTposition
from .dtformats import datetime_formats

_log = logging.getLogger('dtscan')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

#   Continue: 2021-01-19T17:42:37AEDT menu item, splitsum for global vimh for today

class DTScanner(object):
#   {{{
    #   class vars:
    dtconvert = DTConvert()
    dtrange = DTRange()

    _splitlen_default = 300

    #   substitute: _scan_column_delim
    _IFS = ""
    #   substitute: _printdebug_warn_assume_tz
    _warn_substitute = False
    _OFS = ""
    _assume_LocalTz = True
    _warn_LocalTz = True
    #   If True, pass function inputs to _log.debug()
    _printdebug_func_inputs = False
    #   If True, pass function results to _log.debug
    _printdebug_func_outputs = False
    #   If True, destructor __del__() logs actions it performs (deleting tempfile/dir)
    _printdebug_destructor = False

    #   Ongoing: 2020-12-17T18:13:28AEDT two locations - where 'dtscan' (vs dtscan.dtscan) points to depends on what is our entry point to the application
    #   default file, containing regexes to be used by scan 
    _scan_regexfile = [ 'dtscan', 'datetimeregexes.txt' ]
    #[ 'dtscan/data', 'dtregexitems.txt' ]
    #_scan_regexfile_second = [ 'dtscan.dtscan', 'dt-regex-items.txt' ]
    _scan_regexlist = []

    #   variables: _scan_(.*), filled by Interface_Scan(), if not None, used by ScanStream_DateTimeItems to limit search location of datetimes
    _scan_column = None

    #   TODO: 2020-12-14T23:06:44AEDT Allow specifying of custom regex format/file-containing formats
    #   substitue: default_scanstream_regexlist
    #_scan_regexlist = None
    #_scan_regex_file = None

    #   After filtering/sorting input stream, each value in list describes origional position in input of resulting stream
    _input_linenum_map = []

    #   Used in name of tempfiles, itterated every time tempfile is created
    _tempfile_counter = 0

    #   temp dir, deleted by destructor, created when needed
    _path_temp_dir = tempfile.mkdtemp()

    _sorted_match_positions = None
    _sorted_match_output_datetimes = None
    _sorted_match_datetimes = None

    #   TODO: 2021-01-29T22:06:35AEDT That these variables should be set before call to (method that calls) Interface_Scan needs to be better documented
    #   _scan_(.*) variables, used during call to _Interface_Scan()
    _scan_sortdt = None
    _scan_qfstart = None
    _scan_qfend = None
    _scan_qfinterval = 'd'
    _scan_rfstart = None
    _scan_rfend = None
    _scan_outfmt = None

    #   flags: (currently?) unused
    #   {{{
    #   If True, Convert_string2DateTime() assigns the system local timezone to any datetimes that do not have a timezone
    #flag_assume_local_timezone = True
    #   If True, Convert_DateTime2String() uses 'isoformat()' instead of strftime
    flag_dt2str_prefer_tz_Z = True
    #   If False, disable function _PrintArgs()
    _printdebug_printargs = False
    #   If True, _PrintArgs() only outputs arguments not equal to their argparse default value 
    _printdebug_args_only_nondefault = True
    #   If True, include convert functions in debug output
    _printdebug_func_includeConvert = False
    #   If True, pass 'failures to pass input' to _log.debug(), for functions that attempt multiple methods to parse given input
    _printdebug_func_failures = False
    #   If True, warn when substituting characters in input
    _printdebug_warn_substitute = False
    #   Warn about multiple regex matches 
    _printdebug_warn_strict_parse = False
    #   }}}

    def __init__(self):
        self._Read_RegexList()

    #   Destructor, delete _path_temp_dir if it exists
    def __del__(self):
    #   {{{
        if (os.path.exists(self._path_temp_dir)):
            if (self._printdebug_destructor):
                _log.debug("delete _path_temp_dir=(%s)" % str(self._path_temp_dir))
            shutil.rmtree(self._path_temp_dir)
    #   }}}

    def _Interface_ScanDir_Matches(self, arg_dir):
        """Get list of lines from files in dir containing datetimes within 'Scan' range, and corresponding filenames and linenums"""
        results_filepaths = []
        results_linenums = []
        results_linecontents = []
        results_datetimes = []

        #   For each (text) file in arg_dir:
        search_files = [ x for x in glob.iglob(arg_dir+ '**/**', recursive=True) ]
        _log.debug("search_files=(%s)" % pprint.pformat(search_files))

        import mimetypes

        for loop_file in search_files:
            _log.debug("loop_file=(%s)" % str(loop_file))

            if (os.path.isdir(loop_file)):
                _log.debug("skip, isdir for loop_file=(%s)" % str(loop_file))
                continue

            mime = mimetypes.guess_type(loop_file)
            if (mime[0] != 'text/plain'):
                _log.debug("skip, mime=(%s) for loop_file=(%s)" % (str(mime), str(loop_file)))
                continue

            f = open(loop_file, 'r')
            loop_results_matches = self._Interface_Matches(f, True, False)
            _log.debug("loop_results_matches=(%s)" % str(loop_results_matches))
            f.close()

            _index_match = 0
            _index_linenum = 3

            for loop_match in loop_results_matches:
                loop_match_item = loop_match[_index_match]
                loop_match_linenum = int(loop_match[_index_linenum])
                loop_match_linestr = ""

                #   Continue: 2021-01-29T23:40:55AEDT get line loop_match_linenum from loop_file as loop_match_linestr 

                results_filepaths.append(loop_file)
                results_datetimes.append(loop_match_item)
                results_linenums.append(loop_match_linenum)
                results_linecontents.append(loop_match_linestr)

        _log.debug("len(results_datetimes)=(%s)" % len(results_datetimes))

        return [ results_datetimes, results_filepaths, results_linenums, results_linecontents ]

    def _Interface_ScanDir_MatchToString(arg_datetimes, arg_filepaths, arg_linenums, arg_linecontents, flag_include_path=True, flag_include_linenum=True, flag_include_contents=True):
        _delim = "\t"
        pass
        #   Continue: 2021-01-29T23:51:52AEDT return as string, filepath, linenum, (content or datetime), using _delim, and flag_include_(.*) args



    def Update_Vars_Scan(self, _args):
        return self._Update_Vars_Scan(_args.sortdt, _args.qfstart, _args.qfend, _args.qfinterval, _args.rfstart, _args.rfend, _args.outfmt)

    def _Update_Vars_Scan(self, arg_sortdt, arg_qfstart, arg_qfend, arg_qfinterval, arg_rfstart, arg_rfend, arg_outfmt):
    #   {{{
        self._scan_sortdt = arg_sortdt
        self._scan_qfstart = arg_qfstart
        self._scan_qfend = arg_qfend
        self._scan_qfinterval = arg_qfinterval
        self._scan_rfstart = arg_rfstart
        self._scan_rfend = arg_rfend
        self._scan_outfmt = arg_outfmt
    #   }}}

    #   TODO: 2020-12-15T18:00:41AEDT set arg_regexfile (from parser value, where?)
    #   About: Read _scan_regexfile and arg_regexfile to _scan_regexlist as re.compile() instances
    def _Read_RegexList(self, arg_regexfile=None):
    #   {{{
        """Read resource self._scan_regexfile, list of regex-as-strings to append to list self._scan_regexlist"""
        self._scan_regexlist = []

        try:
            #_scan_regexlist_stream = importlib.resources.open_text(*self._scan_regexfile)
            #import pkgutil
            #_scan_regexlist_stream = pkgutil.get_data(*self._scan_regexfile)
            #_log.debug("_scan_regexlist_stream=(%s)" % str(_scan_regexlist_stream))

            from importlib import resources
            #for loop_line in _scan_regexlist_stream:

            with resources.open_text(*self._scan_regexfile) as fid:
                regexdata_str = fid.readlines()

            for loop_line in regexdata_str:
                loop_regex_item = re.compile(loop_line.strip())
                self._scan_regexlist.append(loop_regex_item)
            #_scan_regexlist_stream.close()
        except Exception as e:
            #_log.warning("%s, %s, failed to read dt-regex-items.txt" % (type(e), str(e)))
            #pass
            raise Exception("%s, %s, failed to read <dtregexitems.txt>" % (type(e), str(e)))
        #try:
        #    _scan_regexlist_stream = importlib.resources.open_text(*self._scan_regexfile_second)
        #    for loop_line in _scan_regexlist_stream:
        #        loop_regex_item = re.compile(loop_line.strip())
        #        self._scan_regexlist.append(loop_regex_item)
        #    _scan_regexlist_stream.close()
        #except Exception as e:
        #    _log.warning("%s, %s, failed to read dt-regex-items.txt" % (type(e), str(e)))
        #    pass

        if (arg_regexfile is not None):
            try:
                f = open(arg_regexfile, "r")
                for loop_line in f:
                    loop_regex_item = re.compile(loop_line.strip())
                    self._scan_regexlist.append(loop_regex_item)
                f.close()
            except Exception as e:
                raise Exception("%s, %s, failed to read arg_regexfile=(%s)" % (type(e), str(e), str(arg_regexfile)))
                #_log.error("%s, %s, failed to read arg_regexfile=(%s)" % (type(e), str(e), str(arg_regexfile)))

        if (len(self._scan_regexlist) == 0):
            raise Exception("Failed to read _scan_regexlist")
            #_log.error("Failed to read _scan_regexlist")
            #sys.exit(2)

        if (self._printdebug_func_outputs):
            _log.debug("_scan_regexlist=(%s)" % str(self._scan_regexlist))
    #   }}}

    #   About: Update class variables from _args
    def Update_Vars_Parameters(self, _args):
        return self._Update_Vars_Parameters(_args.noassumetz, _args.col, _args.IFS, _args.OFS, _args.warnings, _args.debug)

    def _Update_Vars_Parameters(self, arg_noassumetz, arg_col, arg_IFS, arg_OFS, arg_warnings, arg_debug):
    #   {{{
        self._IFS = arg_IFS
        self._OFS = arg_OFS
        self._assumeLocalTz = not arg_noassumetz
        self._warn_LocalTz = arg_warnings
        self._warn_substitute = arg_warnings
        self._printdebug_func_outputs = arg_debug
        self._printdebug_func_inputs = arg_debug
        self._printdebug_destructor = arg_debug
        self.dtrange._Update_Vars_Parameters(arg_warnings, arg_debug)
        self.dtconvert._Update_Vars_Parameters(arg_noassumetz, arg_IFS, arg_OFS, arg_warnings, arg_debug)
        if isinstance(arg_col, list):
            self._scan_column = arg_col[0]
        else:
            self._scan_column = arg_col
    #   }}}

    #   TODO: 2021-01-24T21:23:13AEDT neated arguments-for/usage-of Interface_Scan(), being the first step of most function present in DTScanner

    #   Common 'scan' arguments are: arg_sortdt, arg_qfstart, arg_qfend, arg_qfinterval, arg_rfstart, arg_rfend, arg_outfmt, arg_noassumetz, arg_col, arg_IFS, arg_OFS, arg_warnings, arg_debug) <- (note that) when used these are placed at the end of args list in said order.

    def Interface_Scan(self, _args):
        return self._Interface_Scan(_args.infile)

    def Interface_Matches(self, _args):
        return self._Interface_Matches(_args.infile, _args.pos)

    def Interface_Count(self, _args):
        return self._Interface_Count(_args.infile, _args.interval)

    def Interface_Splits(self, _args):
        return self._Interface_Splits(_args.infile, _args.splitlen, _args.nodhms)

    def Interface_SplitSum(self, _args):
        return self._Interface_SplitSum(_args.infile, _args.nodhms, _args.interval, _args.splitlen)

    def Interface_Deltas(self, _args):
        return self._Interface_Deltas(_args.infile, _args.nodhms)

    #   About: Replace datetime instances with those of arg_outfmt
    def Scan_ReplaceDTs(self, arg_infile, arg_outfmt):
        raise Exception("ReplaceDTs unimplemented")

    def _Interface_Scan(self, arg_infile):
    #   {{{
        """Read stream, and optionally (as per self._scan_(.*) vars) sort, quickfilter (filter dates without parsing), rangefilter (filter dates with parsing), and/or replace with given format (unimplemented)"""
        self._sorted_match_positions = None
        self._sorted_match_datetimes = None
        self._sorted_match_output_datetimes = None

        _infile = arg_infile
        _infile = self._util_CombineStreamList(_infile)
        _infile = self._util_MakeStreamSeekable(_infile)

        self._input_linenum_map = []
        for loop_i, loop_line in enumerate(_infile):
            self._input_linenum_map.append(loop_i + 1)
        _infile.seek(0)

        #self._Update_Vars_Parameters(arg_noassumetz, arg_col, arg_IFS, arg_OFS, arg_warnings, arg_debug)

        #self.Update_Vars_Parameters(_args)
        #self.dtrange.Update_Vars_Parameters(_args)
        #self.dtconvert.Update_Vars_Parameters(_args)

        if (self._scan_sortdt):
            _infile = self.Scan_SortChrono(_infile)
        if (self._scan_qfstart is not None) or (self._scan_qfend is not None):
            _infile = self.Scan_QuickFilter(_infile, self._scan_qfstart, self._scan_qfend, self._scan_qfinterval)
        if (self._scan_rfstart is not None) or (self._scan_rfend is not None):
            _infile = self.Scan_RangeFilter(_infile, self._scan_rfstart, self._scan_rfend)
        if (self._scan_outfmt is not None):
            _infile = self.Scan_ReplaceDTs(_infile, self._scan_outfmt)
        return _infile
    #   }}}

    #	TODO: 2020-12-08T23:38:04AEDT argument to print results in given dt format
    #   TODO: 2020-12-13T18:31:51AEDT Implement argument _args.matchtext, if given use scanmatch_text instead of scanmatch_output_text
    #   TODO: 2020-12-13T18:32:26AEDT preserve line numbers from input (so that ScanStream_DateTimeItems is able to return line numbers corresponding to input, not those from filtered stream it processes)
    def _Interface_Matches(self, arg_infile, arg_pos, arg_output_as_Stream=True):
    #   {{{
        """Scan input, get list of matches, and output, optionally with position of said matches. Output either as stream, or list of matches (and positions). Output columns: {0,1,2,3,4,5,6} = {match, """
        #_input_file = self.Interface_Scan(_args)
        _input_file = self._Interface_Scan(arg_infile)

        scanmatch_output_stream_list = []
        scanmatch_output_stream = None
        scanmatch_output_text = None
        scanmatch_datetimes = None

        #   If we have sorted our input stream, use the sorted position and datetime lists, (as opposed to results of scanstream, run on sorted stream)
        if (self._sorted_match_positions is not None) and (self._sorted_match_output_datetimes is not None) and (self._sorted_match_datetimes is not None):
            scanmatch_positions = self._sorted_match_positions
            scanmatch_output_text = self._sorted_match_output_datetimes
            scanmatch_datetimes = self._sorted_match_datetimes
        else:
            results_list = self.ScanStream_DateTimeItems(_input_file)
            scanmatch_output_text, scanmatch_datetimes, scanmatch_text, scanmatch_positions, scanmatch_delta_s = results_list

        #_args.infile.close()
        arg_infile.close()
        _input_file.close()

        if not (arg_pos):
            if not (arg_output_as_Stream):
                return scanmatch_output_text
            scanmatch_output_stream = self._util_ListAsStream(scanmatch_output_text)
        else:
            _delim = "\t"
            scanmatch_outputTextAndPosition = []

            if (len(scanmatch_output_text) != len(scanmatch_positions)):
                raise Exception("mismatch, len(scanmatch_output_text)=(%i), len(scanmatch_positions)=(%i)" % (len(scanmatch_output_text), len(scanmatch_positions)))

            #for loop_output_text, loop_position in zip(scanmatch_output_text, scanmatch_positions):
            #    loop_list_item = loop_output_text + _delim
            #    for loop_position_item in loop_position:
            #        loop_list_item += str(loop_position_item) + _delim
            #    scanmatch_outputTextAndPosition.append(loop_list_item[0:-1])

            for loop_output_text, loop_position in zip(scanmatch_output_text, scanmatch_positions):
                loop_list_item = loop_output_text + _delim
                for loop_position_item in loop_position:
                    loop_list_item += str(loop_position_item) + _delim
                scanmatch_outputTextAndPosition.append(loop_list_item[0:-1])

            if not (arg_output_as_Stream):
                return [ x.split('\t') for x in scanmatch_outputTextAndPosition ]
            scanmatch_output_stream = self._util_ListAsStream(scanmatch_outputTextAndPosition)

        return scanmatch_output_stream
    #   }}}

    def _Interface_Count(self, arg_infile, arg_interval, arg_output_as_Stream=True):
    #   {{{
        """Scan, and Count datetime instances by interval."""
        _input_file = self._Interface_Scan(arg_infile)

        results_list = self.ScanStream_DateTimeItems(_input_file)
        scanmatch_output_text, scanmatch_datetimes, scanmatch_text, scanmatch_positions, scanmatch_delta_s = results_list
        arg_infile.close()

        count_results = self.dtrange.DTRange_CountBy(scanmatch_datetimes, arg_interval)

        #count_results = self.dtrange.DTRange_CountBy(_input_file, _args.interval)
        count_results = list(zip(*count_results))
        count_results_stream = self._util_ListOfListsAsStream(count_results)
        if not (arg_output_as_Stream):
            return count_results
        return count_results_stream
    #   }}}

    #   TODO: 2021-01-29T23:53:24AEDT where a list is returned in place of a stream -> use list of lists, with an element for each value from a given result <- should be only thing returned, conversion to string/stream handled by non '_' function
    #   TODO: 2021-01-29T22:23:25AEDT Output list-of-dicts -> conversion of each item to stream being handled (by call to a utility function) in Interface_Splits
    #   TODO: 2021-01-29T22:03:21AEDT return List from _Interface Methods -> Interface methods perform conversion to stream
    def _Interface_Splits(self, arg_infile, arg_splitlen, arg_nodhms, arg_output_as_Stream=True):
    #   {{{
        """Scan, Identify deltas, and sum adjacent deltas of length < arg_splitlen."""
        _input_file = self._Interface_Scan(arg_infile)

        if (arg_splitlen is None):
            arg_splitlen = self._splitlen_default
            _log.debug("default arg_splitlen=(%s)" % str(arg_splitlen))

        results_list = self.ScanStream_DateTimeItems(_input_file)
        scanmatch_output_text, scanmatch_datetimes, scanmatch_text, scanmatch_positions, scanmatch_delta_s = results_list
        result_splits_elapsed, result_splits = self.Split_DeltasList(scanmatch_datetimes, scanmatch_delta_s, arg_splitlen)
        #result_splits_elapsed, result_splits = self.Split_DeltasList(scanmatch_delta_s, _args.splitlen, scanmatch_datetimes)
        if (result_splits is None):
            raise Exception("result_splits is None")
        _delim = self._OFS
        result_output = []
        for loop_split in result_splits:
            loop_output = self.dtconvert.Convert_SplitListItem2String(loop_split, arg_nodhms)
            result_output.append(loop_output)
        _input_file.close()
        if not (arg_output_as_Stream):
            return result_output
        scanmatch_splits_stream = self._util_ListAsStream(result_output)
        return scanmatch_splits_stream
    #   }}}

    #   TODO: 2020-11-30T21:09:09AEDT avoid scanning same stream twice - keep results of scan, along with corresponding line numbers (later useable for whichever lines haven't been removed) 
    def _Interface_Deltas(self, arg_infile, arg_nodhms, arg_output_as_Stream=True):
    #   {{{
        """Scan, Identify deltas, and output."""
        #_input_file = self.Interface_Scan(_args)
        _input_file = self._Interface_Scan(arg_infile)
        scanmatch_deltas_stream = None
        results_list = self.ScanStream_DateTimeItems(_input_file)
        scanmatch_output_text, scanmatch_datetimes, scanmatch_text, scanmatch_positions, scanmatch_delta_s = results_list
        _input_file.close()
        if (arg_nodhms):
            if not (arg_output_as_Stream):
                return scanmatch_delta_s
            scanmatch_deltas_stream = self._util_ListAsStream(scanmatch_delta_s)
        else:
            scanmatch_delta_dhms = [ self.dtconvert.Convert_seconds2Dhms(x) for x in scanmatch_delta_s ] 
            if not (arg_output_as_Stream):
                return scanmatch_delta_dhms
            scanmatch_deltas_stream = self._util_ListAsStream(scanmatch_delta_dhms)
        return scanmatch_deltas_stream
    #   }}}

    #   TODO: 2021-01-25T21:19:09AEDT arg_interval has a default value of 'd'
    #   TODO: 2021-01-25T21:05:23AEDT arg_nodhms should be a class option
    def _Interface_SplitSum(self, arg_infile, arg_nodhms, arg_interval, arg_splitlen, arg_output_as_Stream=True):
    #   {{{
        """Scan, Identify adjacent deltas of length < arg_splitlen, and sum results by arg_interval"""
        #   list of streams from scan,
        #   for each stream, 
        #       if stream belongs to 'unique', label result with column item
        #       sum matches for each given range interval (or entire stream if none given)
        #   result is a sum, for each unique item, for each interval in range
        _input_file = self._Interface_Scan(arg_infile)

        results_list = self.ScanStream_DateTimeItems(_input_file)
        scanmatch_output_text, scanmatch_datetimes, scanmatch_text, scanmatch_positions, scanmatch_delta_s = results_list
        result_splits_elapsed, result_splits = self.Split_DeltasList(scanmatch_datetimes, scanmatch_delta_s, arg_splitlen)
        _log.debug("len(result_splits)=(%s)" % str(len(result_splits)))
        splits_sum = self.dtrange.DTRange_SumSplits(result_splits, arg_interval, arg_nodhms)
        _log.debug("splits_sum=(%s)" % str(splits_sum))
        splits_sum = list(zip(*splits_sum))
        _input_file.close()

        if not (arg_output_as_Stream):
            return splits_sum
        splits_sum_stream = self._util_ListOfListsAsStream(splits_sum)

        return splits_sum_stream

    #   }}}

    #   TODO: 2020-12-23T19:17:35AEDT 2020-12-07T18:42:28AEDT Replace datetime range generation code with call to DTRange_FromDates()
    #   TODO: 2020-11-25T16:14:04AEDT code to write stream to temp file -> used (duplicatate) by both FilterDateTimes_FastFilter() and FilterDateTimes_ScanStream(), place in dedicated function
    #   TODO: 2020-11-29T14:24:40AEDT get date range without using pandas
    def Scan_QuickFilter(self, arg_input_stream, arg_date_start, arg_date_end, arg_interval):
    #   {{{
        """Copy input stream, keeping only lines with datetimes (identified as text %Y, %Y-%m, %Y-%m-%d) which fall inside given date range, for start/end and interval [ymd]."""
        #   Get list of all year-and-month-s that fall between arg_date_start and arg_date_end
        import pandas
        func_name = inspect.currentframe().f_code.co_name

        date_now = datetime.now()
        dateformat_str = ""
        datefrequency = ''

        #   arguments from argparser (may?) come in the form of lists, if so, replace argument with first list element
        if isinstance(arg_interval, list):
            arg_interval = arg_interval[0]
        if isinstance(arg_date_start, list):
            arg_date_start = arg_date_start[0]
        if isinstance(arg_date_end, list):
            arg_date_end = arg_date_end[0]

        if (arg_interval == 'm'):
            dateformat_str = "%Y-%m"
            datefrequency = 'MS'
        elif (arg_interval == 'y'):
            dateformat_str = "%Y"
            datefrequency = 'YS'
        elif (arg_interval == 'd'):
            dateformat_str = "%Y-%m-%d"
            datefrequency = 'D'
        else:
            raise Exception("Invalid arg_interval=(%s), must be one of [y, m, d]" % str(arg_interval))

        #   If arg_date_(start|end) are integers, (or integers in string format) set them to the current date offset by that number of intervals (days,months,years) prior to now
        try:
            if (arg_date_start is not None):
                arg_date_start = int(arg_date_start)
        except Exception as e:
            pass
        try:
            if (arg_date_end is not None):
                arg_date_end = int(arg_date_end)
        except Exception as e:
            pass

        if (arg_date_start is None):
            arg_date_start = date_now
        if (arg_date_end is None):
            arg_date_end = date_now

        if (isinstance(arg_date_end, int)):
            pass
            offset_list = [0] * 7
            if not (arg_interval == 'd'):
                offset_list[3] = arg_date_end
            elif (arg_interval == 'm'):
                offset_list[1] = arg_date_end
            elif (arg_interval == 'y'):
                offset_list[0] = arg_date_end
            arg_date_end = self.dtconvert.OffsetDateTime_DeltaYMWDhms(date_now, offset_list)
        if (isinstance(arg_date_start, int)):
            pass
            offset_list = [0] * 7
            if not (arg_interval == 'd'):
                offset_list[3] = arg_date_start
            elif (arg_interval == 'm'):
                offset_list[1] = arg_date_start
            elif (arg_interval == 'y'):
                offset_list[0] = arg_date_start
            arg_date_start = self.dtconvert.OffsetDateTime_DeltaYMWDhms(date_now, offset_list)

        #   If arg_date_(start|end) are strings, convert them to datetimes
        if (isinstance(arg_date_start, str)):
            arg_date_start = self.dtconvert.Convert_string2DateTime(arg_date_start)
            if arg_date_start is None:
                raise Exception("Got None for arg_date_start")
        if (isinstance(arg_date_end, str)):
            arg_date_end = self.dtconvert.Convert_string2DateTime(arg_date_end)
            if arg_date_end is None:
                raise Exception("Got None for arg_date_end")

        if (arg_date_start > arg_date_end):
            raise Exception("arg_date_start=(%s) > arg_date_end=(%s)" % (str(arg_date_start), str(arg_date_end)))

        #   About Pandas date range:
        #   LINK: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.date_range.html
        #   LINK: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
        filter_dates_list = [ x.strftime(dateformat_str) for x in pandas.date_range(start=arg_date_start.strftime(dateformat_str), end=arg_date_end.strftime(dateformat_str), freq=datefrequency) ]

        if (self._printdebug_func_inputs):
            _log.debug("arg_date_start=(%s)" % (str(arg_date_start)))
            _log.debug("arg_date_end=(%s)" % (str(arg_date_end)))
            _log.debug("arg_interval=(%s)" % str(arg_interval))

        if (self._printdebug_func_outputs):
            _log.debug("filter_dates_list=(%s)" % str(filter_dates_list))

        #   TODO: 2020-11-19T19:05:04AEDT if arg_input_stream is a string, consisting of a valid filepath, create stream from said file
        _input_path = None
        if isinstance(arg_input_stream, str):
            _input_path = arg_input_stream
            arg_input_stream = open(_input_path, "r")

        if not (os.path.exists(self._path_temp_dir)):
            os.mkdir(self._path_temp_dir)

        #   _path_tempfile, temp file we write filtered output to
        #   {{{
        _now = str(time.time())
        _path_tempfile = os.path.join(self._path_temp_dir, "%s.output.%s" % (func_name, self._tempfile_counter))
        self._tempfile_counter += 1
        if (os.path.exists(_path_tempfile)):
            raise Exception("_path_tempfile=(%s) exists, (this file is meant to be unique, name contains counter, if conflicts are encountered - new method of naming tempfiles is needed, (or use sleep() as a standin)" % _path_tempfile)
        tempfile_stream_write = open(_path_tempfile, "w")
        #   }}}

        #   count _input_lines
        #   {{{
        _input_lines = 0
        arg_input_stream = self._util_MakeStreamSeekable(arg_input_stream)
        for loop_line in arg_input_stream:
            _input_lines += 1
        arg_input_stream.seek(0)
        #   }}}

        #   validate _input_lines > 0
        #   {{{
        if not (_input_lines > 0):
            raise Exception("_input_lines=(%s)" % str(_input_lines))
        #   }}}
        #   printdebug:
        #   {{{
        if (self._printdebug_func_outputs):
            _log.debug("_input_lines=(%s)" % str(_input_lines))
        #   }}}

        #   Copy lines from arg_input_stream to tempfile_stream_write if they contain a string in filter_dates_list
        #   {{{
        previous_input_linenums_map = self._input_linenum_map
        self._input_linenum_map = []
        _output_lines = 0
        for loop_i, loop_line in enumerate(arg_input_stream):
            if any(x in loop_line for x in filter_dates_list):
                tempfile_stream_write.write(loop_line)
                self._input_linenum_map.append(previous_input_linenums_map[loop_i])
                _output_lines += 1
        #   }}}

        #   printdebug, output
        #   {{{
        if (self._printdebug_func_outputs):
            _log.debug("_output_lines=(%s)" % str(_output_lines))
        #   }}}

        #   If arg_input_stream is a stream opened within function, close it
        #   {{{
        if (_input_path is None):
            arg_input_stream.close()
        #   }}}

        tempfile_stream_write.close()
        tempfile_stream_result = open(_path_tempfile, "r")
        return tempfile_stream_result
    #   }}}

    #   TODO: 2020-10-19T13:46:43AEDT Create _path_temp_dir on dtscan start, (delete anything inside older than 24h upon dtscan exit)
    #   Note: 2020-10-19T13:26:34AEDT arg_input_stream must be a seekable stream -> if input has been recieved from stdin, it (must/should?) be written to a temp file, and the stream of that file passed to function.
    def Scan_RangeFilter(self, arg_input_stream, arg_start, arg_end, arg_invert=False, arg_includeNonDTs=False):
    #   {{{
        """Copy input stream, parsing datetimes and keeping only lines containing datetimes falling between given start/end."""
        global self_name
        func_name = inspect.currentframe().f_code.co_name

        if isinstance(arg_start, list):
            arg_start = arg_start[0]
        if isinstance(arg_end, list):
            arg_end = arg_end[0]

        if isinstance(arg_start, str):
            arg_start = self.dtconvert.Convert_string2DateTime(arg_start)
        if isinstance(arg_end, str):
            arg_end = self.dtconvert.Convert_string2DateTime(arg_end)

        if (arg_start is not None) and (arg_end is not None) and (arg_start > arg_end):
            raise Exception("arg_date_start=(%s) > arg_date_end=(%s)" % (str(arg_start), str(arg_end)))

        #   if arg_input_stream is a string, consisting of a valid filepath, create stream from said file
        _input_path = None
        if isinstance(arg_input_stream, str):
            _input_path = arg_input_stream
            arg_input_stream = open(_input_path, "r")

        #if not (os.path.exists(self._path_temp_dir)):
        #    os.mkdir(self._path_temp_dir)

        if (arg_start is None) and (arg_end is None):
            _log.error("both arg_start and arg_end are None")
            return None

        if not (os.path.exists(self._path_temp_dir)):
            os.mkdir(self._path_temp_dir)

        #   Create _path_tempfile
        #   {{{
        #   Ongoing: 2020-10-19T11:01:08AEDT Do we want a singular, temp file which is reused, or do we want a new tempfile (epoch + ms in filename) for each new call? Name is such anyway and delete when done (delete when done how? - this function will have returned, but file will still be in use?) 
        _now = str(time.time())
        _path_tempfile = os.path.join(self._path_temp_dir, "%s.output.%s" % (func_name, str(self._tempfile_counter)))
        self._tempfile_counter += 1
        if (os.path.exists(_path_tempfile)):
            raise Exception("_path_tempfile=(%s) exists, (this file is meant to be unique, name contains epoch in ms, if conflicts are encountered - new method of naming tempfiles is needed, (or use sleep() as a standin)" % _path_tempfile)
        tempfile_stream_write = open(_path_tempfile, "w")
        #   }}}

        #   printdebug, input
        #   {{{
        if (self._printdebug_func_inputs):
            _log.debug("start=(%s), end=(%s), invert=(%s), includeNonDTs=(%s)" % (str(arg_start), str(arg_end), str(arg_invert), str(arg_includeNonDTs)))
        #   }}}

        #   TODO: 2020-11-27T18:21:08AEDT (duplication being bad), 'make-seekable' (use in multiple functions) should be se singular function
        _input_lines = 0
        _output_lines = 0
        #   Count lines in arg_input_stream as _input_lines. If input is not a seekable stream, write it to a file, and use that file as our stream (stdin is not seekable)
        #   {{{
        arg_input_stream = self._util_MakeStreamSeekable(arg_input_stream)

        for loop_line in arg_input_stream:
            _input_lines += 1
        arg_input_stream.seek(0)
        #   }}}

        #   validate _input_lines > 0
        #   {{{
        if not (_input_lines > 0):
            raise Exception("_input_lines=(%s)" % str(_input_lines))
        #   }}}
        #   printdebug:
        #   {{{
        if (self._printdebug_func_inputs):
            _log.debug("_input_lines=(%s)" % str(_input_lines))
        #   }}}

        #   Ongoing: 2020-11-29T16:34:50AEDT performing ScanStream_DateTimeItems() earlier, storing the results (and not performing it again later), or, intentionally perform it again, presuming the results will change as a result of performing filtering
        #   Ongoing: 2020-10-19T10:38:29AEDT Do we make a temp file, or do we keep the result in memory?
        #try:
        scanresults_list = self.ScanStream_DateTimeItems(arg_input_stream)
        scanmatch_output_text, scanmatch_datetimes, scanmatch_text, scanmatch_positions, scanmatch_delta_s = scanresults_list
        arg_input_stream.seek(0)
        #except Exception as e:
            #_log.error("exception: %s, %s, ScanStream_DateTimeItems() failed to read stream" % (str(type(e)), str(e)))
            #return None

        #   _linenums_copy: for each line in _input_lines, do we copy it to output
        _linenums_copy = []
        #_linenums_copy = [0] * _input_lines
        #   {{{
        if (arg_includeNonDTs):
            _linenums_copy = [1] * _input_lines
        else:
            _linenums_copy = [0] * _input_lines
        #   }}}

        #   check mismatch len(scanmatch_positions) != len(scanmatch_datetimes)
        #   {{{
        if (len(scanmatch_positions) != len(scanmatch_datetimes)):
            raise Exception("mismatch, len(scanmatch_positions)=(%s) != len(scanmatch_datetimes)=(%s)" % (len(scanmatch_positions)))
        #   }}}

        #   debug: _lineranges_copy, list of start/end-of-range(s) of lines copied from input->output stream
        #   {{{
        _lineranges_copy = []
        _lineranges_copy_start = None
        _lineranges_copy_end = None
        #   }}}
        #   Identify lines containing datetimes (inside/outside) range, [arg_start, arg_end], and denote them to be copied: _linenums_copy[i] = 1
        for loop_i, (loop_datetime, loop_match) in enumerate(zip(scanmatch_datetimes, scanmatch_positions)):

            loop_linenum = loop_match[2]-1

            if (not arg_invert and ((loop_datetime >= arg_start) and (loop_datetime <= arg_end or arg_end is None))) or (arg_invert and ((loop_datetime < arg_start or arg_start is None) or (loop_datetime > arg_end or arg_end is None))):
                _linenums_copy[loop_linenum] = 1
                #   {{{
                if (_lineranges_copy_start is None):
                    _lineranges_copy_start = loop_i
                    _lineranges_copy_end = None
                #   }}}
            else:
                _linenums_copy[loop_linenum] = 0
                #   {{{
                if (_lineranges_copy_end is None) and (not _lineranges_copy_start is None):
                    _lineranges_copy_end = loop_i
                    _lineranges_copy.append( [ _lineranges_copy_start, _lineranges_copy_end ] )
                    _lineranges_copy_start = None
                #   }}}

        #   debug:
        #   {{{
        if (self._printdebug_func_outputs):
            #_log.debug("_linenums_copy=(%s)" % str(_linenums_copy))
            _log.debug("_lineranges_copy=(%s)" % str(_lineranges_copy))
        #   }}}

        #   copy lines where _linenums_copy[<>] = 1
        #   {{{
        #loop_i = 0
        previous_input_linenums_map = self._input_linenum_map
        self._input_linenum_map = []
        for loop_i, loop_line in enumerate(arg_input_stream):
            if (_linenums_copy[loop_i] == 1):
                tempfile_stream_write.write(loop_line)
                _output_lines += 1
                #self._input_linenum_map.append(loop_i + 1)
                self._input_linenum_map.append(previous_input_linenums_map[loop_i])

            loop_i += 1
        arg_input_stream.seek(0)
        #   }}}

        #   printdebug, output
        #   {{{
        if (self._printdebug_func_outputs):
            _log.debug("_output_lines=(%s)" % str(_output_lines))
        #   }}}

        tempfile_stream_write.close()

        if (_input_path is None):
            arg_input_stream.close()

        tempfile_stream_result = open(_path_tempfile, "r")
        return tempfile_stream_result
    #   }}}

    #   Rename: Scan_DateTimes()
    def ScanStream_DateTimeItems(self, arg_stream):
    #   {{{ 
        """Scan stream, identifying items matching regex-for-datetime, and returning list of lists [ scanmatch_output_text, scanmatch_datetimes, scanmatch_text, scanmatch_positions, scanmatch_delta_s ]."""
        #global self_printdebug
        global self_name
        func_name = inspect.currentframe().f_code.co_name

        #   TODO: 2020-10-12T18:38:58AEDT removing (possible) duplicates from results -> do not allow item to be added to scanstream_regexlist if it is (partially/completely?) contained within a prior result.

        if len(self._scan_regexlist) == 0:
            raise Exception("self._scan_regexlist_len=(%s)" % len(self._scan_regexlist))
        if (self._printdebug_func_outputs) and (self._scan_regexlist):
            _log.debug("self._scan_regexlist_len=(%s)" % len(self._scan_regexlist))

        #   TODO: 2020-11-27T18:16:59AEDT write stream to tempfile if it is not seekable

        scanmatch_text = []
        #   positions: [ match_num, regex_num, line_num, start_index, end_index, len ]
        scanmatch_positions = []
        scanmatch_datetimes = []
        scanmatch_output_text = []
        scanmatch_delta_s = []
        scanmatch_epoch_previous = 0
        scanmatch_datetime_previous = None
        _input_lines = 0
        _output_lines = 0

        if (arg_stream is None):
            raise Exception("arg_stream is none")

        #   TODO: 2020-11-19T19:05:04AEDT if arg_stream is a string, consisting of a valid filepath, create stream from said file
        _input_path = None
        if isinstance(arg_stream, str):
            _input_path = arg_stream
            arg_stream = open(_input_path, "r")

        if not (os.path.exists(self._path_temp_dir)):
            os.mkdir(self._path_temp_dir)

        #   Count lines in arg_stream as _input_lines. If input is not a seekable stream, write it to a file, and use that file as our stream (stdin is not seekable)
        #   {{{
        arg_stream = self._util_MakeStreamSeekable(arg_stream)
        for loop_line in arg_stream:
            _input_lines += 1
        arg_stream.seek(0)
        #   }}}

        #   Continue: 2020-11-24T19:06:13AEDT fix ScanStream_DateTimeItems() deltas calculation

        #   TODO: 2020-11-30T21:29:57AEDT how (best) to limit search to given column (create new stream, of only that column), or (check for each item, whether it is in the specified column)

        loop_match_num = 0
        loop_line_num = 0
        for stream_line in arg_stream:
            loop_regex_item_num = 0

            #   Ongoing: 2020-11-30T21:44:54AEDT behaviour if self._scan_column > len(loop_split_columns)?
            loop_split_columns = []
            if (self._scan_column is not None) and (self._IFS is not None):
                loop_split_columns = [pos for pos, char in enumerate(stream_line) if char == self._IFS]
                loop_split_columns.append(len(stream_line))
                #for loop_col_item in loop_cols:
                    #loop_split_columns.append(loop_col_item)

            #_log.debug("stream_line: %s" % str(stream_line.strip()))
            #_log.debug("cols: %s" % str(loop_split_columns))
            #   item is in a column-a, start > col[a], end <= col[a+1]

            for loop_regex_item in self._scan_regexlist:

                for loop_regex_match in loop_regex_item.finditer(stream_line):

                    loop_match_col_start = -1
                    if (self._scan_column is not None) and (self._IFS is not None):
                        #_log.debug("match start/end: %i, %i" % (loop_regex_match.start(), loop_regex_match.end()))
                        loop_match_col_start = 0
                        loop_match_col_end = 0
                        for loop_col_i, loop_col_x in enumerate(loop_split_columns):
                            if (loop_col_x > loop_regex_match.start()):
                                loop_match_col_start = loop_col_i
                            if (loop_col_x >= loop_regex_match.end()):
                                loop_match_col_end = loop_col_i
                                break
                        #if (loop_match_col_start != loop_match_col_end):
                        #    _log.warning("col before/after: %i, %i" % (loop_match_col_start, loop_match_col_end))
                        #else:
                        #    _log.debug("item col: %i" % loop_match_col_start)

                    #   Ongoing: 2020-12-17T18:11:13AEDT (I don't like it) - either use _input_linenum_map or dont? Why are we even making this exception anyway? (out-of-bounds exception when calling DTRange_GetFirstAndLast() directly from python code)
                    linenum_lookup = None
                    if (len(self._input_linenum_map) > loop_line_num):
                        linenum_lookup = self._input_linenum_map[loop_line_num]
                    else:
                        linenum_lookup = loop_line_num

                    match_item_list = [ loop_match_num, loop_regex_item_num, linenum_lookup, loop_regex_match.start(), loop_regex_match.end(), len(loop_regex_match.group()) ]

                    #_log.debug("linenum_lookup=(%s)" % str(linenum_lookup))
                    #match_item_list = [ loop_match_num, loop_regex_item_num, loop_line_num, loop_regex_match.start(), loop_regex_match.end(), len(loop_regex_match.group()) ]

                    match_item_datetime = self.dtconvert.Convert_string2DateTime(loop_regex_match.group())

                    if not (match_item_datetime is None):
                        #match_item_datetime_outformat = match_item_datetime.strftime(outformat_strftime)
                        match_item_datetime_outformat = self.dtconvert.Convert_DateTime2String(match_item_datetime)
                        #match_item_datetime_epoch = float(match_item_datetime.strftime("%s"))
                        #match_item_datetime_epoch = match_item_datetime.strftime("%s"))
                    else:
                        raise Exception("Failed to decipher match_item_datetime, loop_regex_match_group=(%s)" % str(loop_regex_match.group()))

                    #   Add result match_item to list matches_scan
                    #if (self._scan_column is not None) and (self._IFS is not None) and (loop_match_col_start == self._scan_column):
                    #   Ongoing: 2020-11-30T23:06:33AEDT is our if condition here correct?
                    #_log.error("loop_match_col_start=(%s)" % str(loop_match_col_start))
                    if (self._scan_column is None)  or (loop_match_col_start == self._scan_column):
                        scanmatch_text.append(loop_regex_match.group())
                        scanmatch_positions.append(match_item_list)
                        scanmatch_datetimes.append(match_item_datetime)
                        scanmatch_output_text.append(match_item_datetime_outformat)

                        loop_delta_s = 0
                        if (loop_match_num >= 1):
                            loop_timedelta = match_item_datetime - scanmatch_datetime_previous 
                            #loop_delta_s = loop_timedelta.total_seconds()
                            loop_delta_s = decimal.Decimal(str(loop_timedelta.total_seconds()))
                        else:
                            loop_delta_s = 0
                        scanmatch_datetime_previous = match_item_datetime
                        scanmatch_delta_s.append(loop_delta_s)
                        loop_match_num += 1

                    #else:
                    #    _log.debug("Skip item")

                    #scanmatch_epoch_previous = match_item_datetime_epoch

                loop_regex_item_num += 1
            loop_line_num += 1

        #_log.debug("1/2, scanmatch_positions=(%s)" % str(scanmatch_positions))
        #_log.debug("1/2, scanmatch_datetimes=(%s)" % str(scanmatch_datetimes))
        #   Remove any matches already in text? (or), remove said matches from text, before searching with dateparser
        #_log.debug("2/2, scanmatch_positions=(%s)" % str(scanmatch_positions))
        #_log.debug("2/2, scanmatch_datetimes=(%s)" % str(scanmatch_datetimes))

        #   Ongoing: 2020-11-24T01:27:14AEDT is dateparser faster vis-a-vis extracting a list of datetimes from text?
        #   TODO: 2020-10-19T09:09:24AEDT dtscan, ScanStream_DateTimeItems(), (optionally) examine text with dateparser
        #   Attempt 2) Using dateparser, search arg_stream

        arg_stream.seek(0)

        if (len(scanmatch_text) != len(scanmatch_positions)) or (len(scanmatch_positions) != len(scanmatch_datetimes)) or (len(scanmatch_datetimes) != len(scanmatch_output_text)) or (len(scanmatch_output_text) != len(scanmatch_delta_s)):
            raise Exception("mismatch, matches_ lists lengths, scanmatch_text, scanmatch_positions, scanmatch_datetimes, scanmatch_output_text, scanmatch_delta_s: %i, %i, %i, %i, %i" %  (len(scanmatch_text), len(scanmatch_positions), len(scanmatch_datetimes), len(scanmatch_output_text), len(scanmatch_delta_s)))
        if (self._printdebug_func_outputs):
            _log.debug("len(matches)=(%i)" % len(scanmatch_positions))
        return [ scanmatch_output_text, scanmatch_datetimes, scanmatch_text, scanmatch_positions, scanmatch_delta_s ]
    #   }}}

    #   Ongoing: 2020-12-16T14:14:59AEDT start/end in splittable refer to split number, *not* line number
    #   TODO: 2020-12-09T22:23:19AEDT Replace split_table (list) with dictionary, indexes 0-7 with descriptive keys
    #   TODO: 2020-11-25T18:22:27AEDT flag -> output delta quantities as Dhms instead of seconds
    #   Ongoing: 2020-11-24T21:28:36AEDT use Decimal anywhere (currently) float is being used to store seconds
    #   Ongoing: 2020-11-24T21:26:30AEDT (do we want to be) returning decimals instead of floats for elapsed/before/after -> (better solution presumedly being to) store as integer in microseconds, or using Python's builtin <datetime.delta> 
    def Split_DeltasList(self, arg_datetime_list, arg_deltalist, arg_split):
    #   {{{
        """Given a list of deltas (elapsed times between datetimes), identify those which are sepereated by less than arg_split, returning [ result_split_elapsed, result_splits ]."""
        if isinstance(arg_split, list):
            arg_split = arg_split[0]
        if isinstance(arg_split, str):
            arg_split = decimal.Decimal(arg_split)
        result_splits = []
        result_split_elapsed = []
        #result_singles = []
        if (len(arg_deltalist) != len(arg_datetime_list)):
            raise Exception("mismatch, len(arg_deltalist)=(%i), len(arg_datetime_list)=(%i), arg_split=(%s)" % (len(arg_deltalist), len(arg_datetime_list), str(arg_split)))

        try:
            if (self._printdebug_func_inputs):
                _log.debug("len(arg_deltalist)=(%i), len(arg_datetime_list)=(%i), arg_split=(%s)" % (len(arg_deltalist), len(arg_datetime_list), str(arg_split)))
                _log.debug("arg_deltalist=(%s)" % str(arg_deltalist))
            loop_i=0
            #   split_table:
            #       0:      start
            #       1:      end
            #       2:      count
            #       3:      elapsed
            #       4:      starttime
            #       5:      endtime
            #       6:      before
            #       7:      after
            _index_start = 0
            _index_end = 1
            _index_count = 2
            _index_elapsed = 3
            _index_starttime = 4
            _index_endtime = 5
            _index_before = 6
            _index_after = 7
            split_table = [0] * 8
            split_table[_index_starttime] = arg_datetime_list[0]
            split_table[_index_endtime] = '-'
            split_table[_index_elapsed] = decimal.Decimal(0)
            split_table[_index_before] = decimal.Decimal(0)
            split_table[_index_after] = decimal.Decimal(0)
            split_table[_index_start] = 1
            loop_elapsed = 0

            for loop_delta_decimal in arg_deltalist:
                #_log.debug("loop_i=(%i), loop_delta_decimal=(%s)" % (loop_i, str(loop_delta_decimal)))
                #loop_delta_decimal = decimal.Decimal(str(loop_delta))
                if (loop_delta_decimal > arg_split) and (loop_delta_decimal > 0):
                    split_table[_index_end] = loop_i + 1
                    split_table[_index_after] = loop_delta_decimal
                    split_table[_index_count] = split_table[_index_end] - split_table[_index_start]
                    split_table[_index_endtime] = arg_datetime_list[loop_i-1]
                    split_table[_index_elapsed] = loop_elapsed
                    result_splits.append(split_table)
                    result_split_elapsed.append(loop_elapsed)
                    #if (split_details['elapsed'] > 0):
                    #    result_splits.append(split_details)
                    #else:
                    #    result_singles.append(split_details)
                    #split_table = []
                    split_table = [0] * 8
                    split_table[_index_start] = loop_i + 1
                    split_table[_index_starttime] = arg_datetime_list[loop_i]
                    split_table[_index_before] = loop_delta_decimal
                    loop_elapsed = 0
                elif (loop_delta_decimal >= 0):
                    #_log.debug("add loop_delta_decimal=(%s)" % str(loop_delta_decimal))
                    #split_details['elapsed'] += loop_delta_decimal
                    #   Ongoing: 2020-11-24T20:04:36AEDT dealing with rounding errors?
                    loop_elapsed += loop_delta_decimal
                    #_log.debug("loop_delta_decimal=(%s)" % str(loop_delta_decimal))
                    #_log.debug("loop_elapsed=(%s)" % str(loop_elapsed))
                else:
                    split_table[_index_end] = loop_i + 1
                    split_table[_index_after] = loop_delta_decimal
                    split_table[_index_count] = split_table[_index_end] - split_table[_index_start]
                    split_table[_index_endtime] = arg_datetime_list[loop_i-1]
                    split_table[_index_elapsed] = loop_elapsed
                    result_splits.append(split_table)
                    result_split_elapsed.append(loop_elapsed)
                    #if (split_details['elapsed'] > 0):
                    #    result_splits.append(split_details)
                    #else:
                    #    result_singles.append(split_details)
                    split_table = [0] * 8
                    split_table[_index_start] = loop_i + 1
                    split_table[_index_starttime] = arg_datetime_list[loop_i]
                    split_table[_index_before] = loop_delta_decimal
                    loop_elapsed = 0
                    _log.warning("negative loop_delta_decimal=(%s)" % str(loop_delta_decimal))
                loop_i += 1

            split_table[_index_end] = (loop_i-1)+1
            split_table[_index_after] = arg_deltalist[loop_i-1]
            split_table[_index_count] = split_table[_index_end] - split_table[_index_start]
            split_table[_index_endtime] = arg_datetime_list[loop_i-1]
            split_table[_index_elapsed] = loop_elapsed
            result_splits.append(split_table)
            result_split_elapsed.append(loop_elapsed)
        except Exception as e:
            _log.error("exception: %s %s" % (type(e), str(e)))
            return [ None, None ]
        if (self._printdebug_func_outputs):
            _log.debug("len(result_splits)=(%i)" % len(result_splits))
        #_log.debug("len(result_singles)=(%i)" % len(result_singles))

        return [ result_split_elapsed, result_splits ]
    #   }}}

    #   TODO: 2020-12-15T19:12:03AEDT Sort functions need rewriting
    def Scan_SortChrono(self, arg_input_file, arg_reverse=False):
    #   {{{
        if (self._printdebug_func_inputs):
            _log.debug("sortdt")
        input_lines = []
        for loop_line in arg_input_file:
            input_lines.append(loop_line.strip())
        arg_input_file.seek(0)
        scanresults_list = self.ScanStream_DateTimeItems(arg_input_file)
        scanmatch_output_text, scanmatch_datetimes, scanmatch_text, scanmatch_positions, scanmatch_delta_s = scanresults_list
        result_lines = self._Sort_LineRange_DateTimes(input_lines, scanmatch_datetimes, scanmatch_positions, scanmatch_output_text, arg_reverse)
        _stream_tempfile = self._util_ListAsStream(result_lines)
        arg_input_file.close()
        return _stream_tempfile
    #   }}}

    #   Ongoing: 2020-12-17T17:05:51AEDT here we 1) sort stream chronologically, with each line being positioned according to the earliest datetime it contains. Also, match_positions and match_output_datetimes
    def _Sort_LineRange_DateTimes(self, input_lines, match_datetimes, match_positions, match_output_datetimes, arg_reverse=False, arg_incNonDTLines=True):
    #   {{{
        #   line numbers, sorted first by line number, second by position in line. Convert from 1-indexed to 0-indexed
        lines_order = [ x[2]-1 for x in sorted(match_positions, key=operator.itemgetter(2,3)) ]
        #lines_order = [ x[2] for x in match_positions ]
        if (self._printdebug_func_inputs):
            _log.debug("lines_order=(%s)" % str(lines_order))
        #   Bug: 2020-12-04T01:53:23AEDT sort is not stable for datetimes with same value?
        dtzipped = zip(match_datetimes, match_output_datetimes, lines_order, match_positions)
        #dtzipped = sorted(dtzipped, key = operator.itemgetter(0), reverse=arg_reverse)
        dtzipped = sorted(dtzipped, reverse=arg_reverse)
        match_datetimes, match_output_datetimes, lines_order, match_positions = zip(*dtzipped)

        #   Once we have sorted datetimes (by calling this function), store sorted lists (for use by 'matches', <others?>)
        self._sorted_match_positions = match_positions
        self._sorted_match_output_datetimes = match_output_datetimes
        self._sorted_match_datetimes = match_datetimes

        #   Add lines (containing datetimes) in chronological order to (what will become) our new stream
        results_lines = []
        linenums_included = []
        for loop_line in lines_order:
            if loop_line not in linenums_included:
                linenums_included.append(loop_line)
                try:
                    results_lines.append(input_lines[loop_line])
                except Exception as e:
                    _log.error("%s, %s, Out of bounds line" % (str(type(e)), str(e)))
        #   Add any lines (not containing datetimes)
        if (arg_incNonDTLines):
            loop_i=0
            while (loop_i < len(input_lines)):
                if (loop_i) not in linenums_included:
                    linenums_included.append(loop_i)
                    results_lines.append(input_lines[loop_i])
                loop_i += 1
        if (self._printdebug_func_outputs):
            _log.debug("lines_order=(%s)" % str(lines_order))
        return results_lines
    #   }}}

    #   Ongoing: 2020-12-15T20:28:46AEDT not useable without (access to) dtscan
    #   Return tuple containing first and last datetimes from arg_stream
    def DTRange_GetFirstAndLast(self, arg_stream):
    #   {{{
        arg_stream = self._util_MakeStreamSeekable(arg_stream)
        scanresults_list = None
        try:
            #   Ongoing: 2020-12-15T12:32:16AEDT 
            scanresults_list = self.ScanStream_DateTimeItems(arg_stream)
            arg_stream.seek(0)
        except Exception as e:
            raise Exception("%s, %s, ScanStream_DateTimeItems() failed to read stream" % (str(type(e)), str(e)))
        scanmatch_output_text, scanmatch_datetimes, scanmatch_text, scanmatch_positions, scanmatch_delta_s = scanresults_list
        scanmatch_datetimes.sort()
        result_dt_first = scanmatch_datetimes[0]
        result_dt_last = scanmatch_datetimes[-1]
        result_list = [ result_dt_first, result_dt_last ]
        if (self._printdebug_func_outputs):
            _log.debug("result_list=(%s)" % str(result_list))
        return result_list
    #   }}}

    #   Functions: _util_(.*)
    #   {{{

    #   Copy a given stream to a tempfile and return stream of tempfile. Closes arg_stream. If arg_force is False, return input stream if it is seekable, if True, create new stream regardless
    def _util_MakeStreamSeekable(self, arg_stream, arg_force=False):
    #   {{{
        func_name = inspect.currentframe().f_code.co_name
        if (arg_stream.seekable()) and not (arg_force):
            return arg_stream
        #   if arg_stream is a string, consisting of a valid filepath, create stream from said file
        _input_path = None
        if isinstance(arg_stream, str):
            _input_path = arg_stream
            arg_stream = open(_input_path, "r")
        _now = str(time.time())
        _path_tempfile = os.path.join(self._path_temp_dir, "%s.input.%s.%s" % (func_name, _now, str(self._tempfile_counter)))
        self._tempfile_counter += 1
        if not (arg_stream.seekable()) or (arg_force):
            if not (os.path.exists(self._path_temp_dir)):
                os.mkdir(self._path_temp_dir)
            if (os.path.exists(_path_tempfile)):
                raise Exception("_path_tempfile=(%s) exists, (this file is meant to be unique, name contains epoch in ms, if conflicts are encountered - new method of naming tempfiles is needed, (or use sleep() as a standin)" % _path_tempfile)
            with open(_path_tempfile, "w") as f:
                for loop_line in arg_stream:
                    f.write(loop_line)
            arg_stream.close()
            arg_stream = open(_path_tempfile, "r")
        #if (self._printdebug_func_outputs):
        #    _tempfile_basename = os.path.basename(_path_tempfile)
        #    _log.debug("tempfile_basename=(%s)" % str(_tempfile_basename))
        return arg_stream
    #   }}}

    #   About: Given a list of streams, create and return single stream containing combined data from all streams
    def _util_CombineStreamList(self, arg_stream_list, flag_keepOpen=False):
    #   {{{
        if (arg_stream_list is None):
            return None
        if isinstance(arg_stream_list, io.TextIOWrapper):
            return arg_stream_list
        result_list = []
        for loop_stream in arg_stream_list:
            for loop_line in loop_stream:
                result_list.append(loop_line.strip())
            if not (flag_keepOpen):
                loop_stream.close()
        result_stream = self._util_ListAsStream(result_list)
        return result_stream
    #   }}}

    #   About: Create and return a (tempfile based) stream from a list
    def _util_ListAsStream(self, arg_list):
    #   {{{
        result_string = ""
        if (arg_list is None):
            return None
        for loop_str in arg_list:
            result_string += str(loop_str) + "\n"
        result_stream = io.StringIO(result_string)
        return self._util_MakeStreamSeekable(result_stream, True)
    #   }}}

    def _util_ListOfListsAsStream(self, arg_list):
    #   {{{
    #   TODO: 2020-12-09T19:47:36AEDT use delim from <>?
        result_string = ""
        _delim= "\t"
        if (arg_list is None):
            return None
        for loop_list in arg_list:
            for loop_item in loop_list:
                result_string += str(loop_item) + _delim
            result_string = result_string[0:-1] + "\n"
        result_stream = io.StringIO(result_string)
        return self._util_MakeStreamSeekable(result_stream, True)
    #   }}}

    #   }}}

#   }}}

#   }}}1

