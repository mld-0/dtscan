#	dtscan (Date-Time Scanner)

UPDATE: 2023-07-29T22:15:07AEST consider this an example of how not to write something. See 'mld-0/datetimescan' for a much better (less offensive code, running at a less offensive speed) re-write of this utility.

Python cli utility, identify/convert/analyse datetimes in text. 

##	Getting Started
###	Prerequisites
Requires pip packages:
	pandas
	dateutil
	pytz
	tzlocal

For tests:
	freezegun
	pytest

For tab completion
	shtab

Linting
	flake8

###	Installation
Run 'pip install .' in project directory

##	Commands (subparsers)
Some commands begin where another function finishes, i.e: 'deltas/count' process results of 'matches'

scan - read text, perform updates available by all our subsiquent commands, and outputs result

matches - outputs list of strings identified as datetimes, optionally including their locations in input

count - count the number of datetimes which fall in each given interval (ymwdHMS) between first and last datetime in input

deltas - output difference in (s/dHMS) between subsiquent datetimes

splits - group subsiqent datetimes together if the delta between them is less than a given value, both counting and summing all such deltas

splitsum - output sum of splits identified for each given interval (ymwdHMS) between first and last datetime in input

previous command, (to be implemented) 'uniques' (how? caller of dtscan? perl/xargs? don't tell me there isn't a tool for just such a thing), perform the given command once for each line containing a common value in a given column

###	common arguments

	Do not assume timezone of datetimes
		--noassumetz
	Input column delimitor
		--IFS
	Output column delimitor
		--OFS

	Limit dt scan to given column
		--col

	quickfilter date start/end 
	Generate datetime range from start/end values, and only include lines containing date-as-string within range.
		--qfstart 	<filter-start> 			Defaults to now. If integer <value>, subtract 									
		--qfend 	<filter-end>	 		<value> qfintervals {y|m|d} from now. If string,
											parse to datetime
	quickfilter interval
		--qfinterval {y|m|d}

	Range filter start/end
	Parse datetimes on each line, and only include lines which fall between start/end datetimes.
		--rfstart 
		--rfend

	Range Filter Invert 
		--rfinvert

	Sort lines chronologically
		--sortdt

	Replace datetimes with given format
		--outfmt

	only match historical (before now) datetimes 
		--historic

# unused:
quickfilter range, intervals before now
	--qfnum

TODO: 2020-12-14T19:22:24AEDT qfstart/qfend - support for epochs, (various) seperators between '%F' and '%H/%M/%S'

### scan


### matches (continues 'scan')

	include position of matches
		--pos

### count (continues 'matches')

	Interval to count by (ymwdHMS)
		--interval

### deltas (continues 'matches')

	negative delta behaviour (Unimplemented)
		--negativedelta
	Use seconds for outputs
		--nodhms

### splits (continues 'deltas')

	negative delta behaviour (Unimplemented)
		--negativedelta
	Use seconds for outputs
		--nodhms
	Split by length in seconds
		--splitlen

### splitsum (continues 'splits')

	negative delta behaviour (Unimplemented)
		--negativedelta
	Use seconds for outputs
		--nodhms
	Split by length in seconds
		--splitlen
	Interval to sum by (ymwdHMS)	
		--interval

