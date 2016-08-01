#!/usr/bin/env python3

# Double check whether found itineraries are actually valid. (Only checks
# the precision of the algorithm though, not its recall.)
#
# Usage:
# $ ./find_combinations.py data.csv -f debug >output.json
# $ ./check.py output.json

import sys
import json

from find_combinations import parse_dates, MINT, MAXT


def main():
    with open(sys.argv[1]) as fh:
        itins = (i for i in json.load(fh) if i["valid"])
    for itin in itins:
        itin = itin["itin"]
        for i, flight in enumerate(itin):
            parse_dates(flight)
            if i == 0:
                continue
            prev = itin[i - 1]
            diff = flight["departure"] - prev["arrival"]
            assert prev["destination"] == flight["source"]
            assert diff >= MINT
            assert diff <= MAXT
    print("All itineraries are valid.")


if __name__ == "__main__":
    main()
