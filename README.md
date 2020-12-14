#	dtscan (Date-Time Scanner)

Python cli utility, identify/convert datetimes in text, and provide various information about results.

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

### scan

	Limit dt scan to given column
		--col
	Column delimitor, default="\t"
		--col_delim
	quickfilter start
		--qfstart
		quickfilter end
		--qfend
	Range filter start
		--rfstart
	Range filter end
		--rfend
	Sort lines chronologically
		--sortdt
	Sort lines alphabetically
		--sortalpha
	Replace datetimes with given format
		--replacefmt

TODO: 2020-12-14T19:22:24AEDT qfstart/qfend - support for epochs, (various) seperators between '%F' and '%H/%M/%S'

### matches (continues 'scan')

	include position of matches
		--pos
	
### count (continues 'matches')

	Interval to count by (ymwdHMS)
		--interval

### deltas (continues 'matches')

	<negative delta behaviour>
		--negativedelta
	Use seconds for outputs
		--nodhms

### splits (continues 'deltas')

	Split by length in seconds
		--splitlen

### splitsum (continues 'splits')

	Interval to sum by (ymwdHMS)	
		--interval

