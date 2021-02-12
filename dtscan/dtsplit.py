
class DTSplit(object):
    #   {{{
    #   split start time
    starttime = None
    #   split end time
    endtime = None
    #   split line number, start
    start_index = None
    #   split line number, end
    end_index = None
    #   number of datetimes in split
    count = None
    #   delta before previous split
    delta_before = None
    #   delta before next split
    delta_after = None
    #   elapsed
    elapsed = None

    #delim = "\t"
    #_str_fixed_width = False

    #def __str__(self):
    #    result_str = None
    #    if (self._str_fixed_width):
    #        result_str = "%26s%26s%-8s%16s%-6s%16s" % (str(self.starttime), str(self.endtime), str(self.start_index), str(self.elapsed), str(self.count), str(self.delta_before))
    #    else:
    #        result_str = str(self.starttime) + self.delim + str(self.endtime) + self.delim + str(self.start_index) + self.delim + str(self.elapsed) + self.delim + str(self.count) + self.delim + str(self.delta_before))
    #    return result_str
        



    #   }}}
