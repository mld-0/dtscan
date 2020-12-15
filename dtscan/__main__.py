#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   {{{1

self_name="dtscan"
__version__ = "0.2.0"

import sys
import argparse
import logging
import traceback
from .dtscan import DTScanner

#   debug logging
_log = logging.getLogger(self_name)
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

#   these functions must call 'self.Update_Vars(_args)'
def _Parsers_AssignFunc(arg_dtscanner):
    _subparser_scan.set_defaults(func = arg_dtscanner.Interface_Scan)
    _subparser_matches.set_defaults(func = arg_dtscanner.Interface_Matches)
    _subparser_count.set_defaults(func = arg_dtscanner.Interface_Count)
    _subparser_deltas.set_defaults(func = arg_dtscanner.Interface_Deltas)
    _subparser_splits.set_defaults(func = arg_dtscanner.Interface_Splits)
    _subparser_splitsum.set_defaults(func = arg_dtscanner.Interface_SplitSum)

def _SetupParser_Main(arg_parser):
    #   TODO: 2020-12-15T13:29:22AEDT give multiple input files?
    arg_parser.add_argument('-I', '--infile', type=argparse.FileType('r'), default=sys.stdin, help="Input file")
    arg_parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    arg_parser.add_argument('-v', '--debug', action='store_true', default=False, help="Use debug level logging")
    arg_parser.add_argument('-w', '--warnings', default=False, action='store_true', help="Include warnings")
    arg_parser.add_argument('--noassumetz', action='store_true', default=False, help="Do not assume local timezone for datetimes without timezones")
    arg_parser.add_argument('--IFS', nargs=1, default="\t", type=str, help="Input field seperator")
    arg_parser.add_argument('--OFS', nargs=1, default="\t", type=str, help="Output field seperator")
    arg_parser.add_argument('--nodhms', action='store_true', default=False, help="Use seconds (instead of dHMS)")

def _SetupParser_Scan(arg_parser):
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

def _SetupParser_Matches(arg_parser):
    _SetupParser_Scan(arg_parser)
    arg_parser.add_argument('--pos', action='store_true', default=False, help="Include positions of matches <headings?>")

def _SetupParser_Count(arg_parser):
    _SetupParser_Matches(arg_parser)
    arg_parser.add_argument('--interval', nargs=1, default="d", choices=['y', 'm', 'w', 'd', 'H', 'M', 'S'], help="Interval (ymwdHMS) for count")


def _SetupParser_Deltas(arg_parser):
    _SetupParser_Matches(arg_parser)
    #   TODO: 2020-12-14T22:40:23AEDT treatment/behaviour fornegative deltas (--negativedelta?)

def _SetupParser_Splits(arg_parser):
    _SetupParser_Deltas(arg_parser)
    arg_parser.add_argument('--splitlen', nargs=1, default=300, help="Maximum delta (seconds) to consider datetimes adjacent")
    #   TODO: 2020-12-14T22:37:22AEDT splits - rule, considering whether lines are adjacent or not when deciding whether datetimes they contain are also adjacent

def _SetupParser_SplitSum(arg_parser):
    _SetupParser_Splits(arg_parser)
    arg_parser.add_argument('--interval', nargs=1, default="d", choices=['y', 'm', 'w', 'd', 'H', 'M', 'S'], help="Interval (ymwdHMS) for which to sum")

def cliscan():
    #   {{{
    dtscanner = DTScanner()
    _Parsers_AssignFunc(dtscanner)
    _args = _parser.parse_args()

    if not hasattr(_args, 'func'):
        _log.error("No command given")
        _parser.print_help()
        sys.exit(2)

    result_stream = None
    try:
        result_stream = _args.func(_args)
    except Exception as e:
        _log.error("%s\n%s, %s, for '_args.func(_args)' (%s)" % (str(traceback.format_exc()), str(type(e)), str(e), str(_args.func.__name__)))
        try:
            _args.print_help()
        except Exception as e:
            _log.error("%s, %s, failed to call print_help() after initial exception processing '_args.func(_args)'" % (str(type(e)), str(e)))
        sys.exit(2)

    if (result_stream is None):
        _log.debug("None result, exit")
        sys.exit(0)
    for loop_line in result_stream:
        #   remove trailing newline:
        loop_line = loop_line.rstrip()
        print(loop_line)

    ##   shtab
    #   {{{
    #try:
    #    if args.print_zsh_completion:
    #        print(shtab.complete(parser, shell="zsh"))
    #        sys.exit(0)
    #except Exception as e:
    #    pass
    #   }}}

    #   }}}

_parser = argparse.ArgumentParser(prog=self_name, formatter_class 
    = argparse.ArgumentDefaultsHelpFormatter)
_subparsers = _parser.add_subparsers(dest="subparsers")

#   TODO: 2020-12-14T21:29:49AEDT in 'help', rename 'positional arguments' to 'commands'
_subparser_scan = _subparsers.add_parser('scan', description="filter input, divide per column unique item")
_subparser_matches = _subparsers.add_parser('matches', description="")
_subparser_count = _subparsers.add_parser('count', description="")
_subparser_deltas = _subparsers.add_parser('deltas', description="")
_subparser_splits = _subparsers.add_parser('splits', description="")
_subparser_splitsum = _subparsers.add_parser('splitsum', description="")

_SetupParser_Main(_parser)
_SetupParser_Scan(_subparser_scan)
_SetupParser_Matches(_subparser_matches)
_SetupParser_Count(_subparser_count)
_SetupParser_Deltas(_subparser_deltas)
_SetupParser_Splits(_subparser_splits)
_SetupParser_SplitSum(_subparser_splitsum)

##   shtab:
#   {{{
#shtab.add_argument_to(_parser, "--print-completion", help="Output bash/zsh completion script for parser")
#   }}}

#   }}}1

