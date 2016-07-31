#!/usr/bin/env python3

import csv
import json
import fileinput as finp

from datetime import datetime as dt

DFMT = "%Y-%m-%dT%H:%M:%S"
MINT = 60*60  # seconds
MAXT = 4*60*60  # seconds


def parse_dates(record):
    for key in ("departure", "arrival"):
        record[key] = dt.strptime(record[key], DFMT)
    return record


def main(files=None):
    """Entry point.

    :param files: Files to process.
    :type files: iterable or None. If None, STDIN and/or files in
                 ``sys.argv[1:]`` are processed.
    """
    itins = []
    # NOTE: data will get corrupted if CSV fields contain newlines; to avoid
    # this, only accept input from a file and ``open(..., newline="")``
    rdr = csv.DictReader(finp.input(files))
    for record in rdr:
        parse_dates(record)
        rsrc, rdst = record["source"], record["destination"]
        rdep, rarr = record["departure"], record["arrival"]
        for itin in itins:
            isrc, idst = itin[0]["source"], itin[-1]["destination"]
            idep, iarr = itin[0]["departure"], itin[-1]["arrival"]
            start_diff = (idep - rarr).total_seconds()
            end_diff = (rdep - iarr).total_seconds()
            if rdst == isrc and start_diff >= MINT and start_diff <= MAXT:
                itin.insert(0, record)
            elif idst == rsrc and end_diff >= MINT and end_diff <= MAXT:
                itin.append(record)
        itins.append([record])
    itins = [itin for itin in itins if len(itin) > 1]
    print(json.dumps(itins, indent=2, default=lambda x: dt.strftime(x, DFMT)))


if __name__ == "__main__":
    main()
