#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3:
#   }}}1
#   {{{2
import sys
import argparse
import logging
import traceback
import dateparser
from .dtscan import DTScanner
from .dtrange import DTRange

self_name = "dtscan"
self_name_dtrange = "dtrange"
__version__ = "0.2.1"

#   debug logging
_log = logging.getLogger(self_name)
_logging_format = "%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime = "%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

dtscanner = DTScanner()


def cliscan():
    #   {{{
    _args = _parser_cliscan.parse_args()

    if not hasattr(_args, 'func'):
        _log.error("No command given")
        _parser_cliscan.print_help()
        sys.exit(2)

    if (_args.regexfile):
        dtscanner._resource_read_regexlist(_args.regexfile)

    try:
        _args.func(_args)
    except Exception as e:
        _log.error("%s\n%s, %s, for '_args.func(_args)' (%s)" % (str(traceback.format_exc()), str(type(e)), str(e), str(_args.func.__name__)))
        try:
            _args.print_help()
        except Exception as e:
            _log.error("%s, %s, failed to call print_help() after initial exception processing '_args.func(_args)'" % (str(type(e)), str(e)))
        sys.exit(2)
    #   }}}


#   TODO: 2020-12-14T21:29:49AEDT in 'help', rename 'positional arguments' to 'commands'
_parser_cliscan = argparse.ArgumentParser(prog=self_name, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

#   dtscan common arguments
_parser_cliscan.add_argument('--version', action='version', version='%(prog)s ' + __version__)
_parser_cliscan.add_argument('-v', '--debug', action='store_true', default=False, help="Use debug level logging")
_parser_cliscan.add_argument('-w', '--warnings', default=False, action='store_true', help="Include warnings")
_parser_cliscan.add_argument('-I', '--infile', type=argparse.FileType('r', encoding='utf-8', errors='ignore'), default=sys.stdin, help="Input file")
_parser_cliscan.add_argument('--regexfile', type=argparse.FileType('r', encoding='utf-8', errors='ignore'), help="File containing (extra) regex strings for matching datetimes")
_parser_cliscan.add_argument('--noassumetz', action='store_true', default=False, help="Do not assume local timezone for datetimes without timezones")
_parser_cliscan.add_argument('-C', '--col', nargs=1, default=None, type=int, help="Limit scan to given column (0-indexed)")
_parser_cliscan.add_argument('--IFS', nargs=1, default="\t", type=str, help="Input field seperator")
_parser_cliscan.add_argument('--OFS', nargs=1, default="\t", type=str, help="Output field seperator")
_parser_cliscan.add_argument('--nodhms', action='store_true', default=False, help="Use seconds (instead of dHMS)")
_parser_cliscan.add_argument('--qfstart', nargs=1, default=None, type=str, help="Quick-Filter start date")
_parser_cliscan.add_argument('--qfend', nargs=1, default=None, type=str, help="Quick-Filter end date")
_parser_cliscan.add_argument('--qfinterval', nargs=1, default='m', type=str, help="Quick-Filter interval (ymd)")
#   qfnum: not used
# _parser_cliscan.add_argument('--qfnum', nargs=1, default=None, type=int, help="filter using %%y(-%%m)(-%%d) (as per interval) from current date to given number of qfinterval before current date")
_parser_cliscan.add_argument('--rfstart', nargs=1, default=None, type=str, help="Range-Filter start datetime")
_parser_cliscan.add_argument('--rfend', nargs=1, default=None, type=str, help="Range-Filter end datetime")
_parser_cliscan.add_argument('--rfinvert', action='store_true', default=False, help="Output datetimes outside given Range-Filter interval")
#   historic: role filled by rangefilter?
# _parser_cliscan.add_argument('--historic', action='store_true', default=False, help="Only include datetimes before the present time")
_parser_cliscan.add_argument('--sortdt', action='store_true', default=None, help="Sort lines chronologically")
_parser_cliscan.add_argument('--outfmt', nargs=1, default=None, type=str, help="Replace datetimes with given format")

_subparsers_cliscan = _parser_cliscan.add_subparsers(dest="subparsers")

#   subparser scan
_subparser_cliscan_scan = _subparsers_cliscan.add_parser('scan', description="filter input, divide per column unique item")
_subparser_cliscan_scan.set_defaults(func=dtscanner.ParserInterface_Scan)

#   subparser matches
_subparser_cliscan_matches = _subparsers_cliscan.add_parser('matches', description="")
_subparser_cliscan_matches.add_argument('--pos', action='store_true', default=False, help="Include positions of matches <headings?>")
_subparser_cliscan_matches.set_defaults(func=dtscanner.ParserInterface_Matches)

#   subparser count
_subparser_cliscan_count = _subparsers_cliscan.add_parser('count', description="")
_subparser_cliscan_count.add_argument('--interval', nargs=1, default="d", choices=['y', 'm', 'w', 'd', 'H', 'M', 'S'], help="Interval (ymwdHMS) for count")
_subparser_cliscan_count.set_defaults(func=dtscanner.ParserInterface_Count)

#   subparser deltas
_subparser_cliscan_deltas = _subparsers_cliscan.add_parser('deltas', description="")
_subparser_cliscan_deltas.set_defaults(func=dtscanner.ParserInterface_Deltas)

#   subparser splits
_subparser_cliscan_splits = _subparsers_cliscan.add_parser('splits', description="")
_subparser_cliscan_splits.add_argument('--splitlen', nargs=1, default=300, help="Maximum delta (seconds) to consider datetimes adjacent")
_subparser_cliscan_splits.set_defaults(func=dtscanner.ParserInterface_Splits)

#   subparser splitsum
_subparser_cliscan_splitsum = _subparsers_cliscan.add_parser('splitsum', description="")
_subparser_cliscan_splitsum.add_argument('--splitlen', nargs=1, default=300, help="Maximum delta (seconds) to consider datetimes adjacent")
_subparser_cliscan_splitsum.add_argument('--interval', nargs=1, default="d", choices=['y', 'm', 'w', 'd', 'H', 'M', 'S'], help="Interval (ymwdHMS) for which to sum")
_subparser_cliscan_splitsum.set_defaults(func=dtscanner.ParserInterface_SplitSum)

#   subparser scandir
#   Continue: 2021-02-14T19:56:47AEDT subparser scandir




#   clirange:
def _SetupParser_clirange_Main(arg_parser):
    arg_parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    arg_parser.add_argument('-v', '--debug', action='store_true', default=False, help="Use debug level logging")
    arg_parser.add_argument('-w', '--warnings', default=False, action='store_true', help="Include warnings")


def _Parsers_AssignFunc_clirange(arg_dtrange):
    _subparser_clirange_range.set_defaults(func=arg_dtrange.ParserInterface_Range)


def _SetupParser_clirange_range(arg_parser):
    arg_parser.add_argument('--qfstart', nargs=1, default=None, type=str, help="Quick-Filter start date")
    arg_parser.add_argument('--qfend', nargs=1, default=None, type=str, help="Quick-Filter end date")
    arg_parser.add_argument('--qfinterval', nargs=1, default='m', type=str, help="Quick-Filter interval (ymd)")
    # arg_parser.add_argument('--qfnum', nargs=1, default=None, type=int, help="filter using %%y(-%%m)(-%%d) from current date to given number of qfinterval before current date")


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
_parser_clirange = argparse.ArgumentParser(prog=self_name_dtrange, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
_subparsers_clirange = _parser_clirange.add_subparsers(dest="subparsers")
_subparser_clirange_range = _subparsers_clirange.add_parser('range', description="")
_SetupParser_clirange_Main(_parser_clirange)
_SetupParser_clirange_range(_subparser_clirange_range)

#   }}}1
