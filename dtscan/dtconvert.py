#   VIM SETTINGS: {{{3
#   VIM: let g:mldvp_filecmd_open_tagbar=0 g:mldvp_filecmd_NavHeadings="" g:mldvp_filecmd_NavSubHeadings="" g:mldvp_filecmd_NavDTS=0 g:mldvp_filecmd_vimgpgSave_gotoRecent=0
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3:
#   }}}1
#   imports:
#   {{{2
#   {{{3
import logging
import os
import inspect
import sys
import math
import time
import re
import pytz
import dateutil.parser
import dateutil.tz
import dateutil.relativedelta
import decimal
import dateparser
#   }}}1
#   {{{2
from .dtsplit import DTSplit
from datetime import datetime
from .dtformats import datetime_formats

_log = logging.getLogger('dtscan')
_logging_format = "%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime = "%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.WARNING, format=_logging_format, datefmt=_logging_datetime)


class DTConvert(object):
    flag_dt2str_prefer_tz_Z = True
    _assume_local_Tz = True
    _warn_LocalTz = True

    _printdebug_func_includeConvert = False
    #   If True, pass function inputs to _log.debug()
    _printdebug_func_inputs = True
    #   If True, pass function results to _log.debug
    _printdebug_func_outputs = True
    _warn_substitute = True
    _printdebug_warn_strict_parse = False

    _printdebug_func_failures = False

    _IFS = ""
    _OFS = ""

    def ParserUpdate_Vars_Paramaters(self, _args):
        #   {{{
        return self._Update_Vars_Parameters(_args.noassumetz, _args.IFS, _args.OFS, _args.warnings, _args.debug)
        #   }}}

    def _Update_Vars_Parameters(self, arg_noassumetz, arg_IFS, arg_OFS, arg_warnings, arg_debug):
        #   {{{
        self._IFS = arg_IFS
        self._OFS = arg_OFS
        self._warn_substitute = arg_warnings
        self._warn_LocalTz = arg_warnings
        self._printdebug_warn_strict_parse = arg_warnings
        self._printdebug_func_outputs = arg_debug
        self._printdebug_func_inputs = arg_debug
        # self._printdebug_func_includeConvert = arg_debug
        self._assume_local_Tz = not arg_noassumetz
        #   }}}

    def Convert_DateTimes2Delta_YMWDhms(self, arg_datetime_start, arg_datetime_end):
        #   {{{
        """Given two python datetimes, calculate the difference between them using dateutil.relativedelta, and return as 'YMWDhms' string"""
    #   Continue: 2020-10-09T22:33:52AEDT Conversion between years/months/weeks/ect is more than we want to handle <- ask python('s relativedelta) for <>
        if (self._printdebug_func_inputs) and (self._printdebug_func_includeConvert):
            _log.debug("arg_datetime_start=(%s)" % str(arg_datetime_start))
            _log.debug("arg_datetime_end=(%s)" % str(arg_datetime_end))

        result_delta = dateutil.relativedelta.relativedelta(arg_datetime_end, arg_datetime_start)
        result_YMWDhms = ""

        result_tuple = [result_delta.years, result_delta.months, result_delta.weeks, result_delta.days, result_delta.hours, result_delta.minutes, result_delta.seconds, result_delta.microseconds]

        #   Require the values of result_tuple to be all positive, or all negative (or all zero). Raise exception if not so
        #   {{{
        check_tuple_sign = 0
        for loop_item in result_tuple:
            if (check_tuple_sign > 0):
                if (loop_item < 0):
                    raise Exception("Conflict signs result_tuple=(%s)" % str(result_tuple))
            elif (check_tuple_sign < 0):
                if (loop_item > 0):
                    raise Exception("Conflict signs result_tuple=(%s)" % str(result_tuple))
            else:
                if (loop_item > 0):
                    check_tuple_sign = 1
                elif (loop_item < 0):
                    check_tuple_sign = -1
        #   }}}

        #   seconds/minutes/hours have leading '0's as required. microseconds are included only if non-zero, with only as many decimals as necessary. Include all other values after first non-zero value, even if zero.
        #   {{{
        if (result_delta.years != 0):
            result_YMWDhms += str(abs(result_delta.years)) + "Y"
        if (result_delta.months != 0) or (len(result_YMWDhms) > 0):
            result_YMWDhms += str(abs(result_delta.months)) + "M"
        if (result_delta.weeks != 0) or (len(result_YMWDhms) > 0):
            result_YMWDhms += str(abs(result_delta.weeks)) + "W"
        if (result_delta.days != 0) or (len(result_YMWDhms) > 0):
            result_YMWDhms += str(abs(result_delta.days)) + "D"
        if (result_delta.hours != 0) or (len(result_YMWDhms) > 0):
            if (abs(result_delta.hours) < 10) and not (len(result_YMWDhms) == 0):
                result_YMWDhms += "0"
            result_YMWDhms += str(abs(result_delta.hours)) + "h"
        if (result_delta.minutes != 0) or (len(result_YMWDhms) > 0):
            if (abs(result_delta.minutes) < 10) and not (len(result_YMWDhms) == 0):
                result_YMWDhms += "0"
            result_YMWDhms += str(abs(result_delta.minutes)) + "m"
        if (result_delta.seconds != 0) or (len(result_YMWDhms) > 0):
            if (abs(result_delta.seconds) < 10) and not (len(result_YMWDhms) == 0):
                result_YMWDhms += "0"
            result_YMWDhms += str(abs(result_delta.seconds))
        if (result_delta.microseconds != 0):
            result_YMWDhms += str(abs(result_delta.microseconds) / 1000000)[1:]
        #   }}}

        #   If result_YMWDhms is still empty, set it to zero
        if (len(result_YMWDhms) == 0):
            result_YMWDhms = "0"

        #   Prefix with '-' if negative delta interval, postfix with 's'
        if (check_tuple_sign < 0) and (len(result_YMWDhms) > 0):
            result_YMWDhms = "-" + result_YMWDhms
        result_YMWDhms += "s"

        if (self._printdebug_func_outputs) and (self._printdebug_func_includeConvert):
            _log.debug("result_delta=(%s)" % str(result_delta))
            _log.debug("result_YMWDhms=(%s)" % str(result_YMWDhms))

        return result_YMWDhms
        #   }}}

    def Convert_seconds2WDhms(self, arg_seconds):
        #   {{{
        """Wrapper (for) Convert_seconds2Dhms"""
        return self.Convert_seconds2Dhms(arg_seconds, arg_include_W=True)
        #   }}}

    def Convert_seconds2Dhms(self, arg_seconds, arg_include_W=False):
        #   {{{
        """Convert seconds value to a string %iD%ih%im%ds, (days, hours, minutes, seconds), (optionally including weeks) of equivelent time."""
    #   Status: 2020-10-19T01:03:43AEDT Untested
    #   Created: 2020-10-19T01:03:22AEDT Copied from Convert_seconds2WDhms(), with 'W' list value removed
        if (arg_seconds is not int):
            arg_seconds = float(arg_seconds)
        if (self._printdebug_func_inputs) and (self._printdebug_func_includeConvert):
            _log.debug("arg_seconds=(%s)" % str(arg_seconds))
        scale_vals = (86400, 3600, 60, 1)
        scale_key = ("D", "h", "m", "s")
        if (arg_include_W):
            scale_vals = (86400 * 7, 86400, 3600, 60, 1)
            scale_key = ("W", "D", "h", "m", "s")

        #   Check mismatch len(scale_vals) != len(scale_key)
        #   {{{
        if (len(scale_vals) != len(scale_key)):
            _log.error("mismatch, len(scale_vals)=(%d), len(scale_key)=(%d), scale_vals=(%s), scale_key=(%s)" % (len(scale_vals), len(scale_key), str(scale_vals), str(scale_key)))
            return None
        #   }}}
        result_Dhms = ""
        flag_negative_seconds = False
        if (arg_seconds < 0):
            flag_negative_seconds = True
            arg_seconds = abs(arg_seconds)
        loop_seconds = arg_seconds
        for loop_i, (loop_val, loop_key) in enumerate(zip(scale_vals, scale_key)):
            if (loop_val >= 60):
                loop_quotiant = loop_seconds // loop_val
                loop_seconds = loop_seconds % loop_val
            else:
                loop_quotiant = loop_seconds
            if (loop_quotiant > 0) or ((loop_val < 60) and (len(result_Dhms) == 0)):
                #   set loop_quotiant_str to a string of loop_quotiant, as an integer if there is no decimal component
                loop_quotiant_str = ""
                #   {{{
                if (loop_quotiant == 0):
                    loop_quotiant_str = "0"
                else:
                    loop_quotiant_str = str(float(loop_quotiant))
                try:
                    if (type(loop_quotiant) is int) or (loop_quotiant.is_integer()):
                        loop_quotiant_str = str(int(loop_quotiant))
                except Exception as e:
                    _log.debug("exception: loop_quotiant_str, %s, %s" % (type(e), str(e)))
                    pass
                #   }}}
                if ((loop_key == "s") or (loop_key == "m")) and (len(result_Dhms) > 0) and (len(loop_quotiant_str) == 1):
                    loop_quotiant_str = "0" + loop_quotiant_str
                result_Dhms += loop_quotiant_str + loop_key
        if (flag_negative_seconds):
            result_Dhms = "-" + result_Dhms
        if (self._printdebug_func_outputs) and (self._printdebug_func_includeConvert):
            _log.debug("result_Dhms=(%s)" % str(result_Dhms))
        return result_Dhms
        #   }}}

    def Convert_DateTime2String(self, arg_datetime):
        #   {{{
        """Convert a python datetime to a string representation, using iso-format with %Z timezone. Decimal seconds and timezone only includeded if applicable. If self.flag_dt2str_prefer_tz_Z is False, revert to datetime.isoformat()."""
    #   Ongoing: 2020-11-18T18:40:19AEDT only include as many decimal figures as are non-zero for microseconds?
        flag_strip_trailing_decimalZeros = True
        result_datetime_str = ""
        if (not self.flag_dt2str_prefer_tz_Z) or (isinstance(arg_datetime.tzinfo, dateutil.tz.tzoffset)):
            result_datetime_str = arg_datetime.isoformat()
        else:
            if (arg_datetime.microsecond == 0):
                result_datetime_str = arg_datetime.strftime(datetime_formats['isoZ'])
            else:
                result_datetime_str = arg_datetime.strftime(datetime_formats['iso']) + "." + str(arg_datetime.microsecond)
                if (flag_strip_trailing_decimalZeros):
                    result_datetime_str = result_datetime_str.rstrip('0')
                result_datetime_str += arg_datetime.strftime("%Z")
        return result_datetime_str
        #   }}}

    def Convert_string2DateTime(self, arg_datetime_str):
        #   {{{
        """Handle conversion of string identified-as-datetime to python datetime by attempting conversion with series of assorted parser functions"""
    #   TODO: 2020-12-28T18:43:19AEST dtscan, Convert_string2DateTime -> (test oriented rewrite), focused around correct handeling of datetimes
        parse_result = None
        #   TODO: 2020-10-12T22:22:38AEDT Decimal timestamps?

        try:
            parse_result_int = int(arg_datetime_str)
            parse_result = datetime.fromtimestamp(parse_result_int)
            if (self._assume_local_Tz):
                parse_result = self._Convert_string2DateTime_AssumeTimeZone(parse_result)
            if (self._printdebug_func_outputs) and (self._printdebug_func_includeConvert):
                parse_result_str = self.Convert_DateTime2String(parse_result)
                _log.debug("parse_result_str=(%s)" % str(parse_result_str))
            return parse_result
        except Exception:
            pass

        try:
            parse_result = dateparser.parse(arg_datetime_str, settings={'RETURN_AS_TIMEZONE_AWARE': True})
            parse_result_str = self.Convert_DateTime2String(parse_result)
            if (self._printdebug_func_outputs) and (self._printdebug_func_includeConvert):
                parse_result_str = self.Convert_DateTime2String(parse_result)
                _log.debug("parse_result_str=(%s)" % str(parse_result_str))
            return parse_result
        except Exception:
            pass

        #   Ongoing: 2020-10-12T22:08:30AEDT Decimal epoch?
        try:
            parse_result = dateutil.parser.parse(arg_datetime_str)
            if (self._assume_local_Tz):
                parse_result = self._Convert_string2DateTime_AssumeTimeZone(parse_result)
            if (self._printdebug_func_outputs) and (self._printdebug_func_includeConvert):
                parse_result_str = self.Convert_DateTime2String(parse_result)
                _log.debug("parse_result_str=(%s)" % str(parse_result_str))
            return parse_result
        except Exception:
            pass
        #   TODO: 2020-10-12T16:51:03AEDT If arg_datetime_str can be parsed as an epoch, do so and return said value as datetime

        loop_i = 2
        for k, v in datetime_formats.items():
            try:
                parse_result = datetime.strptime(arg_datetime_str, v)
                if (self._assume_local_Tz):
                    parse_result = self._Convert_string2DateTime_AssumeTimeZone(parse_result)
                if (self._printdebug_func_outputs) and (self._printdebug_func_includeConvert):
                    parse_result_str = self.Convert_DateTime2String(parse_result)
                    _log.debug("parse_result_str=(%s)" % str(parse_result_str))
                return parse_result
            except Exception:
                pass
            loop_i += 1

        try:
            _dateParser_suppliedFormats = []
            for k, v in datetime_formats.items():
                _dateParser_suppliedFormats.append(v)
        except Exception as e:
            _log.error("failed to supply dateparser with custom datetime_formats, %s, %s" % (type(e), str(e)))
            return None
        try:
            parse_result = dateparser.parse(arg_datetime_str, date_formats=_dateParser_suppliedFormats)
            parse_result_str = self.Convert_DateTime2String(parse_result)
            if (self._printdebug_func_outputs) and (self._printdebug_func_includeConvert):
                parse_result_str = self.Convert_DateTime2String(parse_result)
                _log.debug("parse_result_str=(%s)" % str(parse_result_str))
            return parse_result
        except Exception:
            pass

        return None
        #   }}}

    def _Convert_string2DateTime_AssumeTimeZone(self, result_datetime):
        #   {{{
        """If a datetime does not contain timezone information, determine the local timezone as of the given datetime (daylight saving is set according to date), add this timezone information to datetime variable, and return."""
        if not (result_datetime.tzinfo is None) and not isinstance(result_datetime.tzinfo, dateutil.tz.tzoffset):
            if (self._printdebug_func_outputs) and (self._printdebug_func_includeConvert):
                _log.debug("Not None tzinfo/tzoffset, Done" % str(result_datetime.tzinfo))
            return result_datetime
        if (isinstance(result_datetime.tzinfo, dateutil.tz.tzoffset)):
            if (self._printdebug_func_outputs) and (self._printdebug_func_includeConvert):
                _log.debug("result_datetime tzoffset tzinfo=(%s), Done" % str(result_datetime.tzinfo))
            return result_datetime
        result_local_astz = result_datetime.astimezone()
        result_local_tzinfo = result_local_astz.tzinfo
        _tz_input_assumelocal = result_local_tzinfo
        result_datetime = result_datetime.replace(tzinfo=_tz_input_assumelocal)
        if (self._warn_LocalTz) and (self._printdebug_func_includeConvert):
            _log.warning("assign _tz_local=(%s)" % (str(_tz_input_assumelocal)))
        return result_datetime
        #   }}}

    def Convert_DateTimes2Delta_s(self, arg_datetime_start, arg_datetime_end):
        #   {{{
        """Given two python datetimes, determine and return number of seconds (including decimals if applicable) between them."""
        if (self._printdebug_func_inputs) and (self._printdebug_func_includeConvert):
            _log.debug("arg_datetime_start=(%s)" % str(arg_datetime_start))
            _log.debug("arg_datetime_end=(%s)" % str(arg_datetime_end))
        if (arg_datetime_start > arg_datetime_end):
            result_delta = arg_datetime_end - arg_datetime_start
            result_delta_s = result_delta.total_seconds()
        else:
            result_delta = arg_datetime_start - arg_datetime_end
            result_delta_s = -1 * result_delta.total_seconds()
        if (self._printdebug_func_outputs) and (self._printdebug_func_includeConvert):
            _log.debug("result_delta=(%s)" % str(result_delta))
            _log.debug("result_delta_s=(%s)" % str(result_delta_s))
        result_decimal_component, result_int_component = math.modf(result_delta_s)
        #   if decimal component is zero, no zero decimal in output
        result_delta_s = int(result_int_component)
        if not (result_decimal_component == 0):
            result_delta_s += result_decimal_component
        return result_delta_s
        #   }}}

    def Convert_string2Delta_YMWDhms(self, arg_delta_str, arg_delta_setdirection=None, arg_delta_strict_format_parsing=False):
        #   {{{
        """Given a string, 'YMWDhms' delta, parse 7 digits, taken from imediately before coresponding letters. Match performed with regex, if multiple matches are found in input, they are combined (with warning) if they do not contain duplicate values. (Presumedly this approach is overly complication, and better would be to clearly define what is allowable as a ymwdhms string - the reason for which being to allow mismatched use of case for 'ymwdhms' to be deciphered relying on order of values)."""
    #   {{{
    #   Rules for negative values:
    #       '-' at start -> entire delta (each number in YMWDhms) is negative, otherwise they are positive,
    #       '-' at other location in delta string -> invalid (or), (new-delta as if preceded by space?)
    #   Args:
    #       arg_delta_str
    #       arg_delta_setdirection. used to enforce sign of output values, i.e: 1, all outputs positive, -1, all outputs negative, otherwise leave values as parsed. Default=0
    #   Parameters:
    #       _flag_allow_lower_dates,
    #           if True, allow for 'ymwd' in addition to 'YMWD'
    #       _flag_allow_upper_times,
    #           if True, allow for 'HMS' in addition to 'hms'
    #       _flag_allow_whitespace,
    #           if False, do not allow any whitespace characters in arg_delta_str
    #   Valid formats as per 'Delta': -> a period of time, (absolute time, meaning no y m w, and d is (only) 24H)
    #   }}}
    #   Ongoing: 2021-02-06T03:51:06AEDT negative value in delta (anywhere in string) -> all values are negative?
    #   Update: 2020-10-15T22:37:10AEDT add _flag_allow_multi_negation
    #   Update: 2020-10-15T13:04:57AEDT Change how '-' is handled.
    #   Ongoing: 2020-10-09T16:37:52AEDT (what should be) behaviour on failure to parse input -> return all-zero list, or None?
    #   Ongoing: 2020-10-09T12:28:18AEDT Return output in form [ 0, 0, 0, 0, 0, 0, 0.0 ] -> no arg_delta_format required, arg_delta_setdirection -> used to enforce sign of output values, i.e: 1, all outputs positive, -1, all outputs negative, otherwise leave values as parsed?
    #   Status: (2020-08-13)-(2215-46) Skeleton
    #   Created: (2020-08-04)-(1604-26)
        _flag_allow_lower_dates = False
        _flag_allow_upper_times = False
        _flag_allow_whitespace = False
        _flag_swap_exclamation = True
        _flag_allow_multi_negation = True
        if (self._printdebug_func_inputs):
            _log.debug("arg_delta_str=(%s)" % str(arg_delta_str))
        #   replace s/!/-/ if (_flag_swap_exclamation)
        #   {{{
        if (_flag_swap_exclamation):
            if '!' in arg_delta_str:
                arg_delta_str_previous = arg_delta_str
                arg_delta_str = arg_delta_str.replace('!', '-')
                if (self._warn_substitute):
                    _log.warning("substitute '!' for '-' in arg_delta_str=(%s)->(%s) _flag_swap_exclamation=(%s)" % (str(arg_delta_str_previous), str(arg_delta_str), str(_flag_swap_exclamation)))
        #   }}}
        #   printdebug:
        #   {{{
        if (arg_delta_setdirection is not None) and (self._printdebug_func_includeConvert):
            if (self._printdebug_func_inputs):
                _log.debug("arg_delta_setdirection=(%s)" % str(arg_delta_setdirection))
        #   }}}

        result_output = [0, 0, 0, 0, 0, 0, 0.0]
        #   Case 1: Input is (entirely) numeric -> it is a value in seconds, return this value. First of: int(), float()
        try:
            result_output[6] = int(arg_delta_str)
            if (self._printdebug_func_outputs) and (self._printdebug_func_includeConvert):
                _log.debug("result: parse int, result=(%s)" % (str(result_output)))
            return result_output
        except Exception:
            pass
        try:
            result_output[6] = float(arg_delta_str)
            if (self._printdebug_func_outputs) and (self._printdebug_func_includeConvert):
                _log.debug("result: parse float, result=(%s)" % (str(result_output)))
            return result_output
        except Exception:
            pass

        #   Case 2: Parse YMWDhms
        if not (_flag_allow_whitespace):
            re_whitespace = re.compile(r"\S\s")
            _check_split_whitespace = re_whitespace.findall(arg_delta_str)
            if (len(_check_split_whitespace) > 0):
                _log.error("_flag_allow_whitespace=(%s), arg_delta_str=(%s), _check_split_whitespace=(%s)" % (str(_flag_allow_whitespace), str(arg_delta_str), str(_check_split_whitespace)))
                return None

        #   ymwdhms characters: (YMWDhms)
        #   {{{
        _year_char = "Y"
        _month_char = "M"
        _week_char = "W"
        _day_char = "D"
        _hour_char = "h"
        _minute_char = "m"
        _second_char = "s"
        #   _flag_allow_lower_dates, _flag_allow_upper_times:
        if (_flag_allow_lower_dates):
            _year_char += "|y"
            _month_char += "|m"
            _week_char += "|w"
            _day_char += "|d"
        if (_flag_allow_upper_times):
            _hour_char += "|H"
            _minute_char += "|M"
            _second_char += "|S"
        #   }}}

        #   TODO: 2020-10-15T14:55:44AEDT Convert_string2Delta_YMWDhms, check whether input contains items we (by default) disallow in a delta?
        #   TODO: 2020-10-15T17:48:51AEDT _regex_YMWDhms_strict, better validation of input
        _regex_YMWDhms = r"(?P<negation>-?)(?:(?P<year>\d*\.?\d*?)\s*?[%s])?.*?(?:(?P<month>\d*\.?\d*?)\s*?[%s])?.*?(?:(?P<week>\d*\.?\d*?)\s*?[%s])?.*?(?:(?P<day>\d*\.?\d*?)\s*?[%s])?.*?(?:(?P<hour>\d*\.?\d*?)\s*?[%s])?.*?(?:(?P<minute>\d*\.?\d*?)\s*?[%s])?.*?(?:(?P<second>\d*\.?\d*?\.?\d*\.?\d*?)\s*?[%s])?" % (_year_char, _month_char, _week_char, _day_char, _hour_char, _minute_char, _second_char)
        _regex_YMWDhms_strict = r"(?P<negation>-?)(?:(?P<year>\d*\.?\d*?)\s*?[%s])?(?:(?P<month>\d*\.?\d*?)\s*?[%s])?(?:(?P<week>\d*\.?\d*?)\s*?[%s])?(?:(?P<day>\d*\.?\d*?)\s*?[%s])?(?:(?P<hour>\d*\.?\d*?)\s*?[%s])?(?:(?P<minute>\d*\.?\d*?)\s*?[%s])?(?:(?P<second>\d*\.?\d*?\.?\d*\.?\d*?)\s*?[%s])?" % (_year_char, _month_char, _week_char, _day_char, _hour_char, _minute_char, _second_char)

        re_YMWDhms = None
        if not (arg_delta_strict_format_parsing):
            re_YMWDhms = re.compile(_regex_YMWDhms)
        else:
            re_YMWDhms = re.compile(_regex_YMWDhms_strict)

        #   Note: 2020-10-09T17:19:42AEDT We use findall instead of search, and discard any results except the first if there are multiple. We then remove any trailing letters and/or whitespace, and convert each

        #   Ongoing: 2020-10-15T12:48:45AEDT What is responsible for the order of regex results? Are we (apparently) relying on the order being that, WRT: L->R, of those in regex_YMWDhms?
        delta_results_list_temp = re_YMWDhms.findall(arg_delta_str)
        #   Remove all-empty elements from delta_results_list_temp
        #   {{{
        count_delta_results_list_len = 0
        delta_results_list = []
        for delta_result_temp in delta_results_list_temp:
            flag_empty = True
            for element in delta_result_temp:
                if (len(element) > 0):
                    flag_empty = False
            if (not flag_empty):
                delta_results_list.append(delta_result_temp)
                count_delta_results_list_len += 1
        #   }}}
        #   Ongoing: 2020-10-15T14:56:54AEDT If 'len(delta_results_list) == 0', do we return None, or do we return a list of all-zeros?
        if (len(delta_results_list) == 0):
            _log.error("empty delta_results_list, failed to parse arg_delta_str=(%s)" % str(arg_delta_str))
            return None

        #   If there is more than one non-empty regex result, print warning/error, return None for the error, as per arg_delta_strict_format_parsing
        #   {{{
        if (count_delta_results_list_len > 1):
            if not (arg_delta_strict_format_parsing):
                if (self._printdebug_warn_strict_parse):
                    _log.warning("multiple matches, len(delta_results_list)=(%s)>1\n\tis arg_delta_str=(%s) a valid delta?\n\tdelta_results_list=(%s)\n\tto reject use 'arg_delta_strict_format_parsing=True'" % (str(count_delta_results_list_len), str(arg_delta_str), str(delta_results_list)))
            else:
                _log.error("multiple matches, len(delta_results_list)=(%s)>1, is arg_delta_str=(%s) a valid delta? delta_results_list=(%s), to allow use 'arg_delta_strict_format_parsing=False'" % (str(count_delta_results_list_len), str(arg_delta_str), str(delta_results_list)))
                return None
        #   }}}

        #   Combine items from delta_results to result_output, replace empty strings with '0'. Return None if we encounter multiple values for the same regex match group. return None if exception encountered.
        loop_j = 0
        result_sign = 1
        for delta_results in delta_results_list:
            try:
                if (delta_results[0] == "-") and (result_sign != -1):
                    result_sign = -1
                elif (delta_results[0] == "-") and (result_sign != 1):
                    if not (_flag_allow_multi_negation):
                        _log.error("duplicate '-' negation\n\t arg_delta_str=(%s)\n\t delta_results=(%s)\n\tresult_output=(%s)\n\tto allow use '_flag_allow_multi_negation=True'" % (str(arg_delta_str), str(delta_results), str(result_output)))
                        return None
                    else:
                        _log.warning("duplicate '-' negation\n\t arg_delta_str=(%s)\n\tdelta_results=(%s)\n\tresult_output=(%s)\n\tto reject use '_flag_allow_multi_negation=False'" % (str(arg_delta_str), str(delta_results), str(result_output)))

                loop_i = 0
                while (loop_i < 6):
                    if (len(delta_results[loop_i + 1]) > 0) and (delta_results[loop_i + 1] != ""):
                        if (result_output[loop_i] == 0) or (result_output[loop_i] == ""):
                            result_output[loop_i] = None
                            try:
                                result_output[loop_i] = float(delta_results[loop_i + 1])
                                result_output[loop_i] = int(delta_results[loop_i + 1])
                            except Exception:
                                pass
                            if (result_output[loop_i] is None):
                                _log.error("Invalid arg_delta_str=(%s), result_output is None, delta_results=(%s), loop_i=(%s), result_output=(%s)" % (str(arg_delta_str), str(delta_results), str(loop_i), str(result_output)))
                                return None
                        else:
                            _log.error("Invalid arg_delta_str=(%s), duplicate assigned value, delta_results=(%s), loop_i=(%s), result_output=(%s)" % (str(arg_delta_str), str(delta_results), str(loop_i), str(result_output)))
                            return None
                    loop_i += 1

                if (len(delta_results[-1]) > 0) and (delta_results[-1] != ""):
                    result_output[-1] = float(delta_results[-1])
            except Exception as e:
                _log.error("exception, parsing delta_results=(%s), result_output=(%s), %s, %s" % (str(delta_results), str(result_output), str(type(e)), str(e)))
                return None
            loop_j += 1

        loop_i = 0
        while (loop_i < len(result_output)):
            if (result_output[loop_i] == ""):
                result_output[loop_i] = 0
            elif (result_sign == -1):
                result_output[loop_i] = -1 * result_output[loop_i]
            loop_i += 1

        #   Process arg_delta_setdirection, if given set all outputs either negative or postive
        #   {{{
        loop_i = 0
        if (arg_delta_setdirection == -1) or (arg_delta_setdirection == "past"):
            while (loop_i < len(result_output)):
                result_output[loop_i] = -1 * abs(result_output[loop_i])
                loop_i += 1
        elif (arg_delta_setdirection == 1) or (arg_delta_setdirection == "future"):
            while (loop_i < len(result_output)):
                result_output[loop_i] = abs(result_output[loop_i])
                loop_i += 1
        #   }}}

        if (result_output[-1] == 0):
            result_output[-1] = int(0)
        if (self._printdebug_func_outputs) and (self._printdebug_func_includeConvert):
            _log.debug("results=(%s)" % str(result_output))

        return result_output
        #   }}}

    def Convert_WDHMS2seconds(self, arg_WDhms):
        #   {{{
    #   Ongoing: 2021-02-06T03:52:56AEDT Unused?
        if isinstance(arg_WDhms, str):
            arg_WDhms = self.Convert_string2Delta_YMWDhms(arg_WDhms)
        #   Validate len >= 5
        #   {{{
        if (len(arg_WDhms) < 5):
            _log.error("invalid len(arg_WDhms)=(%i), arg_WDhms=(%s)" % (len(arg_WDhms), str(arg_WDhms)))
            return None
        #   }}}
        if (self._printdebug_func_inputs) and (self._printdebug_func_includeConvert):
            _log.debug("arg_WDhms=(%s)" % str(arg_WDhms))
        loop_i = -5
        check_sign = 0
        #   Validate all items in arg_WDhms are the same sign:
        #   {{{
        while (loop_i <= -1):
            if (check_sign == 0):
                if (arg_WDhms[loop_i] < 0):
                    check_sign = -1
                elif (arg_WDhms[loop_i] > 0):
                    check_sign = 1
            elif (check_sign > 0):
                if not (arg_WDhms[loop_i] >= 0):
                    raise Exception("Expect +ive, check_sign=(%s), arg_WDhms=(%s)" % (str(check_sign), str(arg_WDhms)))
            elif (check_sign < 0):
                if not (arg_WDhms[loop_i] <= 0):
                    raise Exception("Expect -ive, check_sign=(%s), arg_WDhms=(%s)" % (str(check_sign), str(arg_WDhms)))
            loop_i += 1
        #   }}}
        try:
            result_seconds = arg_WDhms[-5] * (7 * 24 * 60 * 60) + arg_WDhms[-4] * (24 * 60 * 60) + arg_WDhms[-3] * (60 * 60) + (arg_WDhms[-2] * 60) + arg_WDhms[-1]
        except Exception:
            return None
        if (result_seconds % 1 == 0):
            result_seconds = int(result_seconds)
        if (self._printdebug_func_outputs) and (self._printdebug_func_includeConvert):
            _log.debug("result_seconds=(%d)" % result_seconds)
        return result_seconds
        #   }}}

    def Convert_SplitListItem2String(self, arg_splitlist_item, arg_nodhms=False, arg_fixed_width=False):
        #   {{{
        """Given a split (info on a group of adjacent datetimes) (as a list, [0,1,2,3,4,5,6]=[startindex, endindex, count, elapsed, starttime, endtime, before, after]), convert to a string, either as a fixed width of 98chars, or variable width with self._OFS as delim."""
    #   TODO: 2020-11-30T00:13:20AEDT a split should be an itterable object, storing columns of the split as a dictionary, and this method provided as the 'to-string
        _delim = self._OFS

        split_startindex = arg_splitlist_item.start_index
        split_count = arg_splitlist_item.count
        split_elapsed = arg_splitlist_item.elapsed
        split_before = arg_splitlist_item.delta_before
        split_datetime_start = self.Convert_DateTime2String(arg_splitlist_item.starttime)
        split_datetime_end = self.Convert_DateTime2String(arg_splitlist_item.endtime)

        if not (arg_nodhms):
            split_elapsed = self.Convert_seconds2Dhms(split_elapsed)
            split_before = self.Convert_seconds2Dhms(split_before)
        result_str = None
        if (arg_fixed_width):
            result_str = "%26s%26s%-8s%16s%-6s%16s" % (str(split_datetime_start), str(split_datetime_end), str(split_startindex), str(split_elapsed), str(split_count), str(split_before))
        else:
            result_str = str(split_datetime_start) + _delim + str(split_datetime_end) + _delim + str(split_startindex) + _delim + str(split_elapsed) + _delim + str(split_count) + _delim + str(split_before)
        return result_str
        #   }}}

    def OffsetDateTime_DeltaYMWDhms(self, arg_datetime, arg_YMWDhms):
        #   {{{
        """Given a datetime (either string or python datetime), and 'delta' (as either seconds, or ymwdhms as string/list), add delta to datetime and return resulting datetime."""
        #   Convert arg_YMWDhms to (7 value) list (arg_YMWDhms as last element) if it is a number (presumed to be seconds)
        #   {{{
        if (isinstance(arg_YMWDhms, float)):
            arg_YMWDhms = [0, 0, 0, 0, 0, 0, float(arg_YMWDhms)]
        if (isinstance(arg_YMWDhms, int)):
            arg_YMWDhms = [0, 0, 0, 0, 0, 0, int(arg_YMWDhms)]
        #   }}}
        #   Convert arg_YMWDhms if it is a string
        #   {{{
        if isinstance(arg_YMWDhms, str):
            arg_YMWDhms = self.Convert_string2Delta_YMWDhms(arg_YMWDhms)
        #   }}}
        #   if arg_datetime is a string, convert to datetime, otherwise raise Exception if it isn't a datetime
        #   {{{
        if (isinstance(arg_datetime, str)):
            arg_datetime = self.Convert_string2DateTime(arg_datetime)
        if not (isinstance(arg_datetime, datetime)):
            raise Exception("arg_datetime=(%s), %s, is datetime, (or str convertable to datetime)" % (str(arg_datetime), type(arg_datetime)))
        #   }}}
        #   validate len(arg_YMWDhms) == 7
        #   {{{
        if (len(arg_YMWDhms) != 7):
            raise Exception("invalid len(arg_YMWDhms)=(%s) != 7" % len(arg_YMWDhms))
        #   }}}
        #   printdebug:
        #   {{{
        if (self._printdebug_func_inputs):
            _log.debug("arg_datetime=(%s)" % str(arg_datetime))
            _log.debug("arg_YMWDhms=(%s)" % str(arg_YMWDhms))
        #   }}}
        arg_Y, arg_M, arg_W, arg_D, arg_h, arg_m, arg_s = arg_YMWDhms
        result_datetime = arg_datetime + dateutil.relativedelta.relativedelta(years=arg_Y, months=arg_M, weeks=arg_W, days=arg_D, hours=arg_h, minutes=arg_m, seconds=arg_s)
        #   printdebug:
        #   {{{
        if (self._printdebug_func_outputs):
            _log.debug("result_datetime=(%s)" % str(result_datetime))
        #   }}}
        return result_datetime
        #   }}}


#   }}}1
