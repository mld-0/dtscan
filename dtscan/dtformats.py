
#   datetime_formats, strings for strftime/strptime
datetime_formats = {}
#   {{{
datetime_formats['dts'] = "(%Y-%m-%d)-(%H%M-%S)"
datetime_formats['dts2'] = "(%Y-%m-%d)-(%H-%M-%S)"
datetime_formats['iso'] = "%Y-%m-%dT%H:%M:%S"
datetime_formats['isoZ'] = "%Y-%m-%dT%H:%M:%S%Z"
datetime_formats['isoZus'] = "%Y-%m-%dT%H:%M:%S.%f%Z"
datetime_formats['epoch'] = "%s"
datetime_formats['default'] = "%Y-%m-%dT%H:%M:%S.%f%Z"
#   }}}
