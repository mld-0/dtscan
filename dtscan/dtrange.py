#   VIM SETTINGS: {{{3
#   VIM: let g:mldvp_filecmd_open_tagbar=0 g:mldvp_filecmd_NavHeadings="" g:mldvp_filecmd_NavSubHeadings="" g:mldvp_filecmd_NavDTS=0 g:mldvp_filecmd_vimgpgSave_gotoRecent=0
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   {{{3
import dateutil
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
import dtscan

from .dtconvert import DTConvert
from .dtformats import datetime_formats

_log = logging.getLogger('dtscan')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

class DTRange(object):
#   {{{
    dtconvert = DTConvert()

    #   If True, pass function inputs to _log.debug()
    _printdebug_func_inputs = True
    #   If True, pass function results to _log.debug
    _printdebug_func_outputs = True
    _warn_substitute = True

    def Interface_Range(self, _args):
        return self._Interface_Range(_args.qfstart, _args.qfend, _args.qfinterval)

    def _Interface_Range(self, arg_qfstart, arg_qfend, arg_qfinterval):
        #result_range = self.DTRange_FromDates(_args.qfstart, _args.qfend, _args.qfinterval)
        result_range = self.DTRange_FromDates(arg_qfstart, arg_qfend, arg_qfinterval)
        return result_range

    def Update_Vars_Parameters(self, _args):
    #   {{{
        #self._warn_substitute = _args.warnings
        #self._printdebug_func_outputs = _args.debug
        #self._printdebug_func_inputs = _args.debug
        _log.debug("_args=(%s)" % str(_args))
        return self._Update_Vars_Parameters(_args.warnings, _args.debug)
    #   }}}

    def _Update_Vars_Parameters(self, arg_warnings, arg_debug):
    #   {{{
        self._warn_substitute = arg_warnings
        self._printdebug_func_outputs = arg_debug
        self._printdebug_func_inputs = arg_debug
    #   }}}

    #   About: Given an integer, and an interval [ymwdHMS], subtract given number of intervals from current datetime
    def _DTRange_Date_From_Integer(self, arg_datetime_offset, arg_interval):
    #   {{{
        date_now = datetime.now()
        arg_datetime_offset =  -1 * arg_datetime_offset
        offset_list = [0] * 7
        if (arg_interval == 'y'):
            offset_list[0] = arg_datetime_offset
        elif (arg_interval == 'm'):
            offset_list[1] = arg_datetime_offset
        elif (arg_interval == 'w'):
            offset_list[2] = arg_datetime_offset
        elif (arg_interval == 'd'):
            offset_list[3] = arg_datetime_offset
        elif (arg_interval == 'H'):
            offset_list[4] = arg_datetime_offset
        elif (arg_interval == 'M'):
            offset_list[5] = arg_datetime_offset
        elif (arg_interval == 'S'):
            offset_list[6] = arg_datetime_offset
        else:
            #raise Exception("Invalid arg_interval=(%s), must be one of [ymwdHMS]" % str(arg_interval))
            offset_list[3] = arg_datetime_offset
            _log.warning("Use default 'd' arg_interval=(%s)" % str(arg_interval))
        #if (self._printdebug_func_inputs):
        #    _log.debug("arg_datetime_offset=(%s)" % str(arg_datetime_offset))
        #    _log.debug("offset_list=(%s)" % str(offset_list))
        arg_datetime = self.dtconvert.OffsetDateTime_DeltaYMWDhms(date_now, offset_list)
        return arg_datetime
    #   }}}

    #   All unique datetimes for given arg_interval (YMWDhms) (as strings if arg_type_datetime is False, as python datetimes if True), (assume local timezone as per flag_assume_local_timezone). (More advanced rules for interval i.e: start/end?) 
    #   last datetime in resulting list is *after* arg_datetime_end
    def DTRange_FromDates(self, arg_datetime_start, arg_datetime_end, arg_interval="d", arg_type_datetime=False):
    #   {{{
    #   TODO: 2020-12-23T19:19:06AEDT if arg_datetime_(start|end) are integers, set them to the current date, offset by that number of intervals prior (same behaviour as Scan_QuickFilter -> code in which is to be replaced by call to this function)
    #   TODO: 2020-12-07T19:16:18AEDT begining of week is by default Sunday -> flag to use monday by default, parameter to specify start-day of week
    #   TODO: 2020-12-07T19:14:18AEDT unimplemented hourly/minutly/secondly (HMS of ymwdHMS)

        if isinstance(arg_interval, list):
            arg_interval = arg_interval[0]
        if isinstance(arg_datetime_start, list):
            arg_datetime_start = arg_datetime_start[0]
        if isinstance(arg_datetime_end, list):
            arg_datetime_end = arg_datetime_end[0]

        try:
            if (arg_datetime_start is not None):
                arg_datetime_start = int(arg_datetime_start)
        except Exception as e:
            pass
        try:
            if (arg_datetime_end is not None):
                arg_datetime_end = int(arg_datetime_end)
        except Exception as e:
            pass
        if (arg_datetime_start is None):
            arg_datetime_start = 0
        if (arg_datetime_end is None):
            arg_datetime_end = 0

        delim_date = "-"
        delim_time = ":"
        delim_seperate = "T"

        dateformat_str = ""
        datefrequency = ""
        #   set datefrequency / dateformat_str as per arg_interval, (see below)
        #   LINK: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html
        if (arg_interval == "y"):
            dateformat_str = "%Y"
            datefrequency = "YS"
        elif (arg_interval == "m"):
            dateformat_str = "%Y" + delim_date + "%m"
            datefrequency = "MS"
        elif (arg_interval == "w"):
            dateformat_str = "%Y" + delim_date + "%m" + delim_date + "%d"
            datefrequency = "W"
        elif (arg_interval == "d"):
            dateformat_str = "%Y"+ delim_date +"%m"+ delim_date +"%d"
            datefrequency = "D"
        elif (arg_interval == "H"):
            dateformat_str = "%Y"+ delim_date +"%m"+ delim_date +"%d" + delim_seperate + "%H"
            datefrequency = "H"
        elif (arg_interval == "M"):
            dateformat_str = "%Y"+ delim_date +"%m"+ delim_date +"%d"+ delim_seperate + "%H" + delim_time + "%M"
            datefrequency = "T"
        elif (arg_interval == "S"):
            dateformat_str = "%Y"+ delim_date +"%m"+ delim_date +"%d"+ delim_seperate +"%H"+ delim_time + "%M" + delim_time + "%S"
            datefrequency = "S"
        else:
            raise Exception("Invalid arg_interval=(%s)" % str(arg_interval))

        #   If arg_datetime_(start|end) are strings, convert them to datetimes
        if (isinstance(arg_datetime_start, str)):
            arg_datetime_start = self.dtconvert.Convert_string2DateTime(arg_datetime_start)
        if (isinstance(arg_datetime_end, str)):
            arg_datetime_end = self.dtconvert.Convert_string2DateTime(arg_datetime_end)

        #   Ongoing: 2020-12-07T18:40:38AEDT treatment of negative numbers '-' as arguments (dtscan, python argparse)
        #   If arg_datetime_(start|end) are integers, subtract that many intervals from current date to get value for argument
        if (isinstance(arg_datetime_start, int)):
            arg_datetime_start = self._DTRange_Date_From_Integer(arg_datetime_start, arg_interval)
        if (isinstance(arg_datetime_end, int)):
            arg_datetime_end = self._DTRange_Date_From_Integer(arg_datetime_end, arg_interval)

        #   Require arg_datetime_start to not be after arg_datetime_end
        if (arg_datetime_start.replace(tzinfo=None) > arg_datetime_end.replace(tzinfo=None)):
            raise Exception("backward interval, arg_datetime_start=(%s), arg_datetime_end=(%s)" % (str(arg_datetime_start), str(arg_datetime_end)))

        if (self._printdebug_func_inputs):
            _log.debug("arg_datetime_start=(%s)" % str(arg_datetime_start))
            _log.debug("arg_datetime_end=(%s)" % str(arg_datetime_end))
            _log.debug("arg_interval=(%s)" % str(arg_interval))
            _log.debug("arg_type_datetime=(%s)" % str(arg_type_datetime))

        #   About Pandas date range:
        #   {{{
        #   LINK: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.date_range.html
        #   LINK: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
        #   }}}

        #   pandas not imported until needed (due to ~1s loadtime)
        import pandas
        dtRange_list = [ x for x in pandas.date_range(start=arg_datetime_start.strftime(dateformat_str), end=arg_datetime_end.strftime(dateformat_str), freq=datefrequency) ]

        if not (arg_type_datetime):
            dtRange_list = [ x.strftime(dateformat_str) for x in dtRange_list ]

        if (self._printdebug_func_outputs):
            _log.debug("dtRange_list=(%s)" % str(dtRange_list))
            _log.debug("len(dtRange_list)=(%i)" % len(dtRange_list))

        return dtRange_list
        #   }}}

    def DTRange_FromDateAndDelta(self, arg_datetime_start, arg_delta, arg_interval):
        pass
        #   Adjust arg_datetime_start by arg_delta, and return DTRange_FromDates()

    #   Given a stream of datetimes (as strings), newline seperated, combine entries from the same 'group interval' (YMWDhms) onto the same line 
    def DTRange_GroupInterval(self, arg_DTRange, arg_groupinterval):
        pass

    def _DTRange_Convert_SortedDTList2Range(self, arg_datetimes_sorted, arg_interval, arg_type_datetime):
    #   {{{
        intervalEnd = None
        if isinstance(arg_interval, list):
            arg_interval = arg_interval[0]
        _log.debug("arg_interval=(%s)" % str(arg_interval))
        #   (when) last item is '2020-11', this is actually 2020-11-01T00:00:00 - excluding items actually in month 2020-11. Therefore, find intervalEnd as last datetime + 1 interval
        #   {{{
        if (arg_interval == "y"):
            intervalEnd = arg_datetimes_sorted[-1] + relativedelta(years=1)
        elif (arg_interval == "m"):
            intervalEnd = arg_datetimes_sorted[-1] + relativedelta(months=1)
        elif (arg_interval == "w"):
            intervalEnd = arg_datetimes_sorted[-1] + relativedelta(weeks=1)
        elif (arg_interval == "d"):
            intervalEnd = arg_datetimes_sorted[-1] + relativedelta(days=1)
        elif (arg_interval == "H"):
            intervalEnd = arg_datetimes_sorted[-1] + relativedelta(hours=1)
        elif (arg_interval == "M"):
            intervalEnd = arg_datetimes_sorted[-1] + relativedelta(minutes=1)
        elif (arg_interval == "S"):
            intervalEnd = arg_datetimes_sorted[-1] + relativedelta(seconds=1)
        #   }}}
        if (intervalEnd is None):
            #raise Exception("intervalEnd is None")
            intervalEnd = arg_datetimes_sorted[-1] + relativedelta(days=1)
            _log.warning("use default 'd' intervalEnd=(%s)" % str(intervalEnd))

        firstAndLast = [ arg_datetimes_sorted[0], intervalEnd ]
        if (arg_datetimes_sorted[0] > intervalEnd):
            raise Exception("arg_datetimes_sorted[0] > intervalEnd")
        if (self._printdebug_func_inputs):
            _log.debug("first=(%s), last=(%s)" % (str(firstAndLast[0]), str(firstAndLast[1])))
        #   Get datetime range for first/last datetimes and arg_interval
        result_range = self.DTRange_FromDates(firstAndLast[0], firstAndLast[1], arg_interval, arg_type_datetime)
        return result_range
    #   }}}

    ##   About: Given a stream, determine first and last datetimes, get range list, and datetimes in stream corresponding to each range. Return list [ list_counts, list_intervals ]. Intervals with count 0 are excluded 
    #def DTRange_CountBy(self, arg_infile, arg_interval):
    ##   {{{
    #    #arg_infile = self._util_MakeStreamSeekable(arg_infile)
    #    #   ScanStream_DateTimeItems() handles is-datetime-in-column, provided self._scan_column has been specified
    #    scanresults_list = self.ScanStream_DateTimeItems(arg_infile)
    #    scanmatch_output_text, scanmatch_datetimes, scanmatch_text, scanmatch_positions, scanmatch_delta_s = scanresults_list
    #   }}}

    def DTRange_CountBy(self, arg_scanmatch_datetimes, arg_interval):
    #   {{{
        #   TODO: 2020-12-08T15:15:45AEDT handle cases of (only) 0/1 datetimes 
        #   Get first and last datetime in input
        scanmatch_datetimes_sorted = sorted(arg_scanmatch_datetimes)
        #_log.error("scanmatch_datetimes_sorted=(%s)" % str(scanmatch_datetimes_sorted))
        #   for item in range list, create list of datetimes which are after item, but before next item
        datetime_range = self._DTRange_Convert_SortedDTList2Range(scanmatch_datetimes_sorted, arg_interval, True)
        datetime_range_str = self._DTRange_Convert_SortedDTList2Range(scanmatch_datetimes_sorted, arg_interval, False)
        count_range = []
        #   for items in list datetime_range, get count of datetimes in scanmatch_datetimes which are before item, but after following item
        loop_i = 0
        while (loop_i < len(datetime_range)-1):
            count_range.append(0)
            for loop_datetime in arg_scanmatch_datetimes:
                loop_tz = loop_datetime.tzinfo
                if (loop_datetime >= datetime_range[loop_i].replace(tzinfo=loop_tz) and loop_datetime < datetime_range[loop_i+1].replace(tzinfo=loop_tz)):
                    count_range[loop_i] += 1
            loop_i += 1
        #   result_list, 0=count, 1=datetime-str
        result_list = [ [], [] ]
        #   datetime_range_str will be 1 element longer than count_range, last element discarded by zip
        for loop_count, loop_dtStr in zip(count_range, datetime_range_str):
            if (not isinstance(loop_count, str) and (loop_count > 0)) or (isinstance(loop_count, str) and loop_count != "0s"):
                result_list[0].append(loop_count)
                result_list[1].append(loop_dtStr)
        if (len(result_list[0]) != len(result_list[1])):
            raise Exception("mismatch lengths, len(result_list[0])=(%i) != len(result_list[1])=(%i), result_list=(%s)" % (len(result_list[0]), len(result_list[1]), str(result_list)))
        if (self._printdebug_func_outputs):
            _log.debug("result_list=(%s)" % str(result_list))
        return result_list
        #   }}}

    def DTRange_SumSplits(self, arg_splitlist, arg_interval, arg_nodhms=False):
    #   TODO: 2020-12-09T22:38:21AEDT finding firstAndLast from sorted list, duplication being bad, dedicated function, (currently) located in DTRange_CountBy(), DTRange_SumSplits
    #   {{{
        #   splitlist: [ start, end, count, elapsed, starttime, endtime, before, after ]
        #   Get first and last datetime in arg_splitlist
        if (self._printdebug_func_inputs):
            _log.debug("len(arg_splitlist)=(%s)" % str(len(arg_splitlist)))
            _log.debug("arg_interval=(%s)" % str(arg_interval))
        #   Get datetime range for first/last datetimes and arg_interval
        splitlist_datetimes = list(zip(*arg_splitlist))[4]
        splitlist_elapseds = list(zip(*arg_splitlist))[3]
        scanmatch_datetimes_sorted = sorted(splitlist_datetimes)
        datetime_range = self._DTRange_Convert_SortedDTList2Range(scanmatch_datetimes_sorted, arg_interval, True)
        datetime_range_str = self._DTRange_Convert_SortedDTList2Range(scanmatch_datetimes_sorted, arg_interval, False)
        interval_split_sum = []
        #   for item in list datetime_range, get sum of splits for each datetime in scanmatch_datetimes which are before item, but after following item
        loop_i = 0
        while (loop_i < len(datetime_range)-1):
            interval_split_sum.append(0)
            for loop_datetime, loop_elapsed in zip(splitlist_datetimes, splitlist_elapseds):
                loop_tz = loop_datetime.tzinfo
                if (loop_datetime >= datetime_range[loop_i].replace(tzinfo=loop_tz) and loop_datetime < datetime_range[loop_i+1].replace(tzinfo=loop_tz)):
                    interval_split_sum[loop_i] += loop_elapsed
                pass
            loop_i += 1
        if not (arg_nodhms):
            interval_split_sum_temp = interval_split_sum
            interval_split_sum = [ self.dtconvert.Convert_seconds2Dhms(x) for x in interval_split_sum_temp ]
            #_log.debug("interval_split_sum=(%s)" % str(interval_split_sum))
        result_list = [ [], [] ]
        for loop_count, loop_dtStr in zip(interval_split_sum, datetime_range_str):
            #if (loop_count > 0):
            if (not isinstance(loop_count, str) and (loop_count > 0)) or (isinstance(loop_count, str) and loop_count != "0s"):
                result_list[0].append(loop_count)
                result_list[1].append(loop_dtStr)
        if (self._printdebug_func_outputs):
            _log.debug("interval_split_sum=(%s)" % str(interval_split_sum))
        #   datetime_range_str has last interval, which is after values in text, removed, to give lists of matching length. 
        if (len(result_list[0]) != len(result_list[1])):
            raise Exception("mismatch lengths, len(result_list[0])=(%i) != len(result_list[1])=(%i), result_list=(%s)" % (len(result_list[0]), len(result_list[1]), str(result_list)))
        if (self._printdebug_func_outputs):
            _log.debug("result_list=(%s)" % str(result_list))
        return result_list
    #   }}}

#   }}}

#   }}}1

