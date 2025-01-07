import sys
from calendarfns import *

if __name__ == "__main__":
    cal_name = str(sys.argv[1])
    month = int(sys.argv[2])
    year = int(sys.argv[3])
    file_name = str(sys.argv[4])

X = parse_calendar(cal_name)
generate_printable_calendar(X, month, year, file_name)
