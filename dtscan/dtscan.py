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

import importlib.resources
import logging
from .dtconvert import DTConvert
from .dtrange import DTRange
from .dtsplit import DTsplit
from .dtposition import DTposition
from .dtformats import datetime_formats

_log = logging.getLogger('dtscan')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

class DTScanner(object):
#   {{{
    #   class vars:
    #   {{{
    dtconvert = DTConvert()
    dtrange = DTRange()

    _scan_regexfile = [ 'dtscan', 'dt-regex-items.txt' ]
    _scan_regexlist = []

    #   substitute: _scan_column_delim
    _IFS = ""
    #   substitute: _printdebug_warn_assume_tz
    _warn_substitute = False

    _OFS = ""
    _assume_LocalTz = True
    _warn_LocalTz = True

    #   If True, pass function inputs to _log.debug()
    _printdebug_func_inputs = True
    #   If True, pass function results to _log.debug
    _printdebug_func_outputs = True

    #   variables: _scan_(.*), filled by Interface_Scan(), if not None, used by 
    _scan_column = None

    #   TODO: 2020-12-14T23:06:44AEDT Allow specifying of custom regex format/file-containing formats
    #   substitue: default_scanstream_regexlist
    #_scan_regexlist = None
    #_scan_regex_file = None

    #   After filtering/sorting input stream, each value in list describes origional position in input of resulting stream
    _input_linenum_map = []

    #   Used in name of tempfiles, itterated every time tempfile is created
    _tempfile_counter = 0

    #   TODO: 2020-11-28T20:31:23AEDT Only create _path_temp_dir when needed
    _path_temp_dir = tempfile.mkdtemp()

    #   }}}

    def __init__(self):
        self.Read_RegexList()

    #   TODO: 2020-12-15T18:00:41AEDT set arg_regexfile (from parser value, where?)
    #   About: Read _scan_regexfile and arg_regexfile to _scan_regexlist as re.compile() instances
    def Read_RegexList(self, arg_regexfile=None):
    #   {{{
        try:
            _scan_regexlist_stream = importlib.resources.open_text(*self._scan_regexfile)
            for loop_line in _scan_regexlist_stream:
                loop_regex_item = re.compile(loop_line.strip())
                self._scan_regexlist.append(loop_regex_item)
            _scan_regexlist_stream.close()
        except Exception as e:
            _log.error("%s, %s, failed to read dt-regex-items.txt" % (type(e), str(e)))
            sys.exit(2)
        if (arg_regexfile is not None):
            try:
                f = open(arg_regexfile, "r")
                for loop_line in f:
                    loop_regex_item = re.compile(loop_line.strip())
                    self._scan_regexlist.append(loop_regex_item)
                f.close()
            except Exception as e:
                _log.error("%s, %s, failed to read arg_regexfile=(%s)" % (type(e), str(e), str(arg_regexfile)))
        if (self._printdebug_func_outputs):
            _log.debug("_scan_regexlist=(%s)" % str(self._scan_regexlist))
    #   }}}

    #   About: Update class variables from _args
    def Update_Vars(self, _args):
    #   {{{
        self._IFS = _args.IFS
        self._OFS = _args.OFS
        self._assumeLocalTz = not _args.noassumetz
        self._warn_LocalTz = _args.warnings
        self._warn_substitute = _args.warnings
        self._printdebug_func_outputs = _args.debug
        self._printdebug_func_inputs = _args.debug
        self.dtrange.Update_Vars(_args)
        self.dtconvert.Update_Vars(_args)
    #   }}}

    #   flags:
    #   {{{
    #   If True, destructor __del__() logs actions it performs (deleting tempfile/dir)
    _printdebug_destructor = True

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

    #   Functions: Interface_(.*)
    #   {{{
    def Interface_Scan(self, _args):
        _infile = _args.infile
        _infile = self._util_CombineStreamList(_infile)
        _infile = self._util_MakeStreamSeekable(_infile)
        if (_args.col is not None):
            self._scan_column = _args.col
        if (_args.sortdt):
            _infile = self.Scan_SortChrono(_infile)
        if (_args.qfstart is not None) or (_args.qfend is not None):
            _infile = self.Scan_QuickFilter(_infile, _args.qfstart, _args.qfend, _args.qfinterval)
        if (_args.rfstart is not None) or (_args.rfend is not None):
            _infile = self.Scan_RangeFilter(_infile, _args.rfstart, _args.rfend)
        if (_args.outfmt is not None):
            _infile = self.Scan_ReplaceDTs(_infile, _args.outfmt)
        return _infile

    def Interface_Matches(self, _args):
        pass

    def Interface_Count(self, _args):
        pass

    def Interface_Deltas(self, _args):
        pass

    def Interface_Splits(self, _args):
        pass

    def Interface_SplitSum(self, _args):
        pass
    #   }}}

    #   Functions: 
    def Scan_SortChrono(self, arg_input_file, arg_reverse=False):
    #   {{{
        #   if there are multiple datetimes on a given line, we consider the first (or n-th) for the purpouses of sorting
        if (self._printdebug_func_inputs):
            _log.debug("sortdt")
        input_lines = []
        #   Continue: 2020-12-02T21:26:21AEDT implement sortdt - read lines, sort lines chronologically, write to new stream, and return
        for loop_line in arg_input_file:
            input_lines.append(loop_line.strip())
        arg_input_file.seek(0)
        scanresults_list = self.ScanStream_DateTimeItems(arg_input_file)
        scanmatch_output_text, scanmatch_datetimes, scanmatch_text, scanmatch_positions, scanmatch_delta_s = scanresults_list
        #result_lines = self._Sort_LineRange_DateTimes(input_lines, scanmatch_positions, scanmatch_datetimes, arg_reverse)
        result_lines = self._Sort_LineRange_DateTimes(input_lines, scanmatch_positions, scanmatch_output_text, arg_reverse)
        #_log.debug("result_lines=(%s)" % str(result_lines))
        _stream_tempfile = self._util_ListAsStream(result_lines)
        arg_input_file.close()
        return _stream_tempfile
    #   }}}

    #   TODO: 2020-12-15T18:31:59AEDT sort is not stable?
    def _Sort_LineRange_DateTimes(self, input_lines, match_positions, match_datetimes, arg_reverse=False, arg_incNonDTLines=True):
    #   {{{
        #   line numbers, sorted first by line number, second by position in line
        lines_order = [ x[2] for x in sorted(match_positions, key=operator.itemgetter(2,3)) ]
        #lines_order = [ x[2] for x in match_positions ]
        if (self._printdebug_func_inputs):
            _log.debug("lines_order=(%s)" % str(lines_order))
        #   Bug: 2020-12-04T01:53:23AEDT sort is not stable for datetimes with same value?
        dtzipped = zip(match_datetimes, lines_order)
        #dtzipped = sorted(dtzipped, key = operator.itemgetter(0), reverse=arg_reverse)
        dtzipped = sorted(dtzipped, reverse=arg_reverse)
        match_datetimes, lines_order= zip(*dtzipped)
        #   Add lines (containing datetimes) in chronological order
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
                if loop_i not in linenums_included:
                    linenums_included.append(loop_i)
                    results_lines.append(input_lines[loop_i])
                loop_i += 1
        if (self._printdebug_func_outputs):
            _log.debug("lines_order=(%s)" % str(lines_order))
        return results_lines
    #   }}}


    def Scan_ReplaceDTs(self, arg_infile, arg_outfmt):
        _log.error("unimplemented")
        return arg_infile

    def Scan_QuickFilter(self, arg_input_stream, arg_date_start, arg_date_end, arg_interval):
    #   {{{
    #   TODO: 2020-12-07T18:42:28AEDT Replace datetime range generation code with call to DTRange_FromDates()
    #   TODO: 2020-11-25T16:14:04AEDT code to write stream to temp file -> used (duplicatate) by both FilterDateTimes_FastFilter() and FilterDateTimes_ScanStream(), place in dedicated function
    #   TODO: 2020-11-29T14:24:40AEDT get date range without using pandas
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

        if (arg_date_start is None):
            arg_date_start = date_now
        if (arg_date_end is None):
            arg_date_end = date_now

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
            raise Exception("_path_tempfile=(%s) exists, (this file is meant to be unique, name contains epoch in ms, if conflicts are encountered - new method of naming tempfiles is needed, (or use sleep() as a standin)" % _path_tempfile)
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
        _output_lines = 0
        for loop_line in arg_input_stream:
            if any(x in loop_line for x in filter_dates_list):
                tempfile_stream_write.write(loop_line)
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

    def Scan_RangeFilter(self, arg_input_stream, arg_start, arg_end, arg_invert=False, arg_includeNonDTs=False):
    #   {{{
    #   TODO: 2020-10-19T13:46:43AEDT Create _path_temp_dir on dtscan start, (delete anything inside older than 24h upon dtscan exit)
    #   Note: 2020-10-19T13:26:34AEDT arg_input_stream must be a seekable stream -> if input has been recieved from stdin, it (must/should?) be written to a temp file, and the stream of that file passed to function.
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
            loop_linenum = loop_match[2]
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
        loop_i = 0
        for loop_line in arg_input_stream:
            if (_linenums_copy[loop_i] == 1):
                tempfile_stream_write.write(loop_line)
                _output_lines += 1
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
        #global self_printdebug
        global self_name
        func_name = inspect.currentframe().f_code.co_name

        #   TODO: 2020-10-12T18:38:58AEDT removing (possible) duplicates from results -> do not allow item to be added to scanstream_regexlist if it is (partially/completely?) contained within a prior result.

        if len(self._scan_regexlist) == 0:
            raise Exception("self._scan_regexlist_len=(%s)" % len(self._scan_regexlist))
        if (self._scan_regexlist):
            _log.debug("self._scan_regexlist_len=(%s)" % len(self._scan_regexlist))

        #   TODO: 2020-11-27T18:16:59AEDT write stream to tempfile if it is not seekable

        #   Attempt 1) Search for regex matches in arg_stream - itterate over each line, for each regex given in file qvar_scanstream_regexlist. 
        scanmatch_text = []
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
            if (self._scan_column is not None) and (self._scan_column_delim is not None):
                loop_split_columns = [pos for pos, char in enumerate(stream_line) if char == self._scan_column_delim]
                loop_split_columns.append(len(stream_line))
                #for loop_col_item in loop_cols:
                    #loop_split_columns.append(loop_col_item)

            #_log.debug("stream_line: %s" % str(stream_line.strip()))
            #_log.debug("cols: %s" % str(loop_split_columns))
            #   item is in a column-a, start > col[a], end <= col[a+1]

            for loop_regex_item in self._scan_regexlist:

                for loop_regex_match in loop_regex_item.finditer(stream_line):

                    loop_match_col_start = -1
                    if (self._scan_column is not None) and (self._scan_column_delim is not None):
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

                    match_item_list = [ loop_match_num, loop_regex_item_num, loop_line_num, loop_regex_match.start(), loop_regex_match.end(), len(loop_regex_match.group()) ]
                    match_item_datetime = self.dtconvert.Convert_string2DateTime(loop_regex_match.group())

                    if not (match_item_datetime is None):
                        #match_item_datetime_outformat = match_item_datetime.strftime(outformat_strftime)
                        match_item_datetime_outformat = self.dtconvert.Convert_DateTime2String(match_item_datetime)
                        #match_item_datetime_epoch = float(match_item_datetime.strftime("%s"))
                        #match_item_datetime_epoch = match_item_datetime.strftime("%s"))
                    else:
                        raise Exception("Failed to decipher match_item_datetime, loop_regex_match_group=(%s)" % str(loop_regex_match.group()))

                    #   Add result match_item to list matches_scan
                    #if (self._scan_column is not None) and (self._scan_column_delim is not None) and (loop_match_col_start == self._scan_column):
                    #   Ongoing: 2020-11-30T23:06:33AEDT is our if condition here correct?
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


    def Split_DeltaList(self, arg_datetimes, arg_deltas, arg_split_s):
        _log.error("unimplemented")
        return arg_infile

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

    #   Destructor, delete _path_temp_dir if it exists
    def __del__(self):
    #   {{{
        if (os.path.exists(self._path_temp_dir)):
            if (self._printdebug_destructor):
                _log.debug("delete _path_temp_dir=(%s)" % str(self._path_temp_dir))
            shutil.rmtree(self._path_temp_dir)
    #   }}}

#   }}}

#   }}}1

