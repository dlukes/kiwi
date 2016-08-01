#!/usr/bin/env python3

# Generate some more test data. Useful for comparing performance of version
# with indexing (on branch ``master``) and without (on branch ``naive``).
#
# Usage: ./more_data.py <data.csv> <times>
#
# <data.csv> is the original data; <times> is an integer indicating how much
# more data you want.

import sys
import csv

from datetime import datetime as dt, timedelta
from find_combinations import DFMT


def parse_date(date):
    return dt.strptime(date, DFMT)


def add_days(date, days):
    return dt.strftime(date + timedelta(days=days), DFMT)


def main():
    data, times = sys.argv[1], int(sys.argv[2])
    with open(data) as fh:
        for i, row in enumerate(csv.reader(fh)):
            if i == 0:
                print(",".join(row))
                continue
            dpt, arr, fnum = parse_date(row[2]), parse_date(row[3]), row[4]
            for j in range(times):
                row[2] = add_days(dpt, j)
                row[3] = add_days(arr, j)
                row[4] = "{}_{}".format(fnum, j)
                print(",".join(row))


if __name__ == "__main__":
    main()
