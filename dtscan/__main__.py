#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   {{{2

self_name="dtscan"
self_name_dtrange="dtrange"
__version__ = "0.2.0"

import sys
import argparse
import logging
import traceback
from .dtscan import DTScanner
from .dtrange import DTRange

#   debug logging
_log = logging.getLogger(self_name)
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

#   these functions must call 'self.ParserUpdate_Vars_Paramaters(_args)'
def _Parsers_AssignFunc_cliscan(arg_dtscanner):
#   {{{
    _subparser_cliscan_scan.set_defaults(func = arg_dtscanner.ParserInterface_Scan)
    _subparser_cliscan_matches.set_defaults(func = arg_dtscanner.ParserInterface_Matches)
    _subparser_cliscan_count.set_defaults(func = arg_dtscanner.ParserInterface_Count)
    _subparser_cliscan_deltas.set_defaults(func = arg_dtscanner.ParserInterface_Deltas)
    _subparser_cliscan_splits.set_defaults(func = arg_dtscanner.ParserInterface_Splits)
    _subparser_cliscan_splitsum.set_defaults(func = arg_dtscanner.ParserInterface_SplitSum)
#   }}}

def _SetupParser_cliscan_Main(arg_parser):
#   {{{
    #   TODO: 2020-12-15T13:29:22AEDT give multiple input files?
    arg_parser.add_argument('-I', '--infile', type=argparse.FileType('r'), default=sys.stdin, help="Input file")
    arg_parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    arg_parser.add_argument('-v', '--debug', action='store_true', default=False, help="Use debug level logging")
    arg_parser.add_argument('-w', '--warnings', default=False, action='store_true', help="Include warnings")
    arg_parser.add_argument('--noassumetz', action='store_true', default=False, help="Do not assume local timezone for datetimes without timezones")
    arg_parser.add_argument('--IFS', nargs=1, default="\t", type=str, help="Input field seperator")
    arg_parser.add_argument('--OFS', nargs=1, default="\t", type=str, help="Output field seperator")
    arg_parser.add_argument('--nodhms', action='store_true', default=False, help="Use seconds (instead of dHMS)")
#   }}}

def _SetupParser_clirange_Main(arg_parser):
    arg_parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    arg_parser.add_argument('-v', '--debug', action='store_true', default=False, help="Use debug level logging")
    arg_parser.add_argument('-w', '--warnings', default=False, action='store_true', help="Include warnings")

def _SetupParser_cliscan_Scan(arg_parser):
#   {{{
    arg_parser.add_argument('-C', '--col', nargs=1, default=None, type=int, help="Limit scan to given column (0-indexed)")
    arg_parser.add_argument('--qfstart', nargs=1, default=None, type=str, help="Quick-Filter start date")
    arg_parser.add_argument('--qfend', nargs=1, default=None, type=str, help="Quick-Filter end date")
    arg_parser.add_argument('--qfinterval', nargs=1, default='m', type=str, help="Quick-Filter interval (ymd)")
    arg_parser.add_argument('--qfnum', nargs=1, default=None, type=int, help="filter using %%y(-%%m)(-%%d) from current date to given number of qfinterval before current date")
    arg_parser.add_argument('--rfstart', nargs=1, default=None, type=str, help="Range-Filter start datetime")
    arg_parser.add_argument('--rfend', nargs=1, default=None, type=str, help="Range-Filter end datetime")
    arg_parser.add_argument('--rfinvert', action='store_true', default=False, help="Output datetimes outside given Range-Filter interval")
    arg_parser.add_argument('--sortdt', action='store_true', default=None, help="Sort lines chronologically")
    arg_parser.add_argument('--outfmt', nargs=1, default=None, type=str, help="Replace datetimes with given format")
#   }}}

def _SetupParser_cliscan_Matches(arg_parser):
#   {{{
    _SetupParser_cliscan_Scan(arg_parser)
    #   TODO: 2020-12-17T00:02:31AEDT dtscan, implement '--historic'
    arg_parser.add_argument('--historic', action='store_true', default=False, help="Only include datetimes before the present time")
    arg_parser.add_argument('--pos', action='store_true', default=False, help="Include positions of matches <headings?>")
#   }}}

def _SetupParser_cliscan_Count(arg_parser):
#   {{{
    _SetupParser_cliscan_Matches(arg_parser)
    arg_parser.add_argument('--interval', nargs=1, default="d", choices=['y', 'm', 'w', 'd', 'H', 'M', 'S'], help="Interval (ymwdHMS) for count")
#   }}}


def _SetupParser_cliscan_Deltas(arg_parser):
#   {{{
    _SetupParser_cliscan_Matches(arg_parser)
    #   TODO: 2020-12-14T22:40:23AEDT treatment/behaviour fornegative deltas (--negativedelta?)
#   }}}

def _SetupParser_cliscan_Splits(arg_parser):
#   {{{
    _SetupParser_cliscan_Deltas(arg_parser)
    arg_parser.add_argument('--splitlen', nargs=1, default=300, help="Maximum delta (seconds) to consider datetimes adjacent")
    #   TODO: 2020-12-14T22:37:22AEDT splits - rule, considering whether lines are adjacent or not when deciding whether datetimes they contain are also adjacent
#   }}}

def _SetupParser_cliscan_SplitSum(arg_parser):
#   {{{
    _SetupParser_cliscan_Splits(arg_parser)
    arg_parser.add_argument('--interval', nargs=1, default="d", choices=['y', 'm', 'w', 'd', 'H', 'M', 'S'], help="Interval (ymwdHMS) for which to sum")
#   }}}

def cliscan():
#   {{{
    dtscanner = DTScanner()
    _Parsers_AssignFunc_cliscan(dtscanner)
    _args = _parser_cliscan.parse_args()

    if not hasattr(_args, 'func'):
        _log.error("No command given")
        _parser_cliscan.print_help()
        sys.exit(2)

    result_stream = None
    try:
        dtscanner.ParserUpdate_Vars_Paramaters(_args)
        dtscanner.ParserUpdate_Vars_Scan(_args)
        result_stream = _args.func(_args)
    except Exception as e:
        _log.error("%s\n%s, %s, for '_args.func(_args)' (%s)" % (str(traceback.format_exc()), str(type(e)), str(e), str(_args.func.__name__)))
        try:
            _args.print_help()
        except Exception as e:
            _log.error("%s, %s, failed to call print_help() after initial exception processing '_args.func(_args)'" % (str(type(e)), str(e)))
        sys.exit(2)

    if (result_stream is None):
        _log.error("None result, exit")
        sys.exit(0)
    for loop_line in result_stream:
        #   remove trailing newline:
        loop_line = loop_line.rstrip()
        print(loop_line)

#   }}}


def _Parsers_AssignFunc_clirange(arg_dtrange):
    _subparser_clirange_range.set_defaults(func = arg_dtrange.ParserInterface_Range)

def _SetupParser_clirange_range(arg_parser):
    arg_parser.add_argument('--qfstart', nargs=1, default=None, type=str, help="Quick-Filter start date")
    arg_parser.add_argument('--qfend', nargs=1, default=None, type=str, help="Quick-Filter end date")
    arg_parser.add_argument('--qfinterval', nargs=1, default='m', type=str, help="Quick-Filter interval (ymd)")
    arg_parser.add_argument('--qfnum', nargs=1, default=None, type=int, help="filter using %%y(-%%m)(-%%d) from current date to given number of qfinterval before current date")


def clirange():
#   {{{
    dtrange = DTRange()
    _Parsers_AssignFunc_clirange(dtrange)
    _args = _parser_clirange.parse_args()
    if not hasattr(_args, 'func'):
        _log.error("No command given")
        _parser_cliscan.print_help()
        sys.exit(2)
    result_list = None
    try:
        dtrange.ParserUpdate_Vars_Paramaters(_args)
        result_list = _args.func(_args)
    except Exception as e:
        _log.error("%s\n%s, %s, for '_args.func(_args)' (%s)" % (str(traceback.format_exc()), str(type(e)), str(e), str(_args.func.__name__)))
        try:
            _args.print_help()
        except Exception as e:
            _log.error("%s, %s, failed to call print_help() after initial exception processing '_args.func(_args)'" % (str(type(e)), str(e)))
        sys.exit(2)
    if (result_list is None):
        _log.error("None result, exit")
        sys.exit(0)
    for loop_line in result_list:
        #   remove trailing newline:
        loop_line = loop_line.rstrip()
        print(loop_line)
#   }}}


#   Ongoing: 2020-12-23T18:50:29AEDT Do we need subparser(s) for dtrange?
_parser_clirange = argparse.ArgumentParser(prog=self_name_dtrange, formatter_class = argparse.ArgumentDefaultsHelpFormatter)
_subparsers_clirange = _parser_clirange.add_subparsers(dest="subparsers")
_subparser_clirange_range = _subparsers_clirange.add_parser('range', description="")

_SetupParser_clirange_Main(_parser_clirange)
_SetupParser_clirange_range(_subparser_clirange_range)


_parser_cliscan = argparse.ArgumentParser(prog=self_name, formatter_class = argparse.ArgumentDefaultsHelpFormatter)
_subparsers_cliscan = _parser_cliscan.add_subparsers(dest="subparsers")
#   TODO: 2020-12-14T21:29:49AEDT in 'help', rename 'positional arguments' to 'commands'

_subparser_cliscan_scan = _subparsers_cliscan.add_parser('scan', description="filter input, divide per column unique item")
_subparser_cliscan_matches = _subparsers_cliscan.add_parser('matches', description="")
_subparser_cliscan_count = _subparsers_cliscan.add_parser('count', description="")
_subparser_cliscan_deltas = _subparsers_cliscan.add_parser('deltas', description="")
_subparser_cliscan_splits = _subparsers_cliscan.add_parser('splits', description="")
_subparser_cliscan_splitsum = _subparsers_cliscan.add_parser('splitsum', description="")

_SetupParser_cliscan_Main(_parser_cliscan)
_SetupParser_cliscan_Scan(_subparser_cliscan_scan)
_SetupParser_cliscan_Matches(_subparser_cliscan_matches)
_SetupParser_cliscan_Count(_subparser_cliscan_count)
_SetupParser_cliscan_Deltas(_subparser_cliscan_deltas)
_SetupParser_cliscan_Splits(_subparser_cliscan_splits)
_SetupParser_cliscan_SplitSum(_subparser_cliscan_splitsum)

##   shtab:
#   {{{
#shtab.add_argument_to(_parser_cliscan, "--print-completion", help="Output bash/zsh completion script for parser")
#   }}}

#   }}}1

