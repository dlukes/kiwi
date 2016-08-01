#!/usr/bin/env python3

import sys
import csv
import json
import argparse as ap
import fileinput as finp

from datetime import timedelta, datetime as dt
from operator import itemgetter

DFMT = "%Y-%m-%dT%H:%M:%S"
MINT = timedelta(hours=1)
MAXT = timedelta(hours=4)


def parse_dates(flight):
    for key in ("departure", "arrival"):
        flight[key] = dt.strptime(flight[key], DFMT)
    return flight


def jsonify(x):
    if isinstance(x, dt):
        return dt.strftime(x, DFMT)
    else:
        raise RuntimeError("Unable to jsonify {!r}.".format(x))


def is_abab(itin, flight):
    """Will appending ``flight`` to ``itin`` result in (A->B), (_->_), (A->B)?

    """
    itin = itin["itin"]
    if len(itin) < 2:
        return False
    penult = itin[-2]
    return (penult["source"] == flight["source"]
            and penult["destination"] == flight["destination"])


def find_itins(flights, mint, maxt, cleanup_cycles=False):
    """Connect flights into multi-flight itineraries.

    :param flights: Iterable of flight records.
    :param mint: Minimum flight transfer time.
    :param maxt: Maximum flight transfer time.
    :param cleanup_cycles: Whether to remove cyclic references (for JSON
        output).

    """
    itins = []
    earlier_flights = []
    # sorting the flights by arrival times simplifies subsequent code quite a
    # bit because itineraries can then only grow by appending new flights, and
    # never by prepending
    for flight in sorted(flights, key=itemgetter("arrival")):
        parse_dates(flight)
        itin = dict(itin=[flight], valid=False, maximal=True)
        flight["ends"] = [itin]
        itins.append(itin)
        earlier_flights.append(flight)
        rsrc, rdep = flight["source"], flight["departure"]
        for arrival in earlier_flights:
            diff = rdep - arrival["arrival"]
            if not (arrival["destination"] == rsrc and MINT <= diff <= MAXT):
                continue
            for itin in arrival["ends"]:
                if not is_abab(itin, flight):
                    new = dict(itin=itin["itin"][:] + [flight], valid=True, maximal=True)
                    itins.append(new)
                    flight["ends"].append(new)
                    itin["maximal"] = False
    if cleanup_cycles:
        for flight in earlier_flights:
            del flight["ends"]
    return itins


def output(itins, sub_itins=False, fmt="debug"):
    if fmt == "debug":
        print(json.dumps(itins, indent=2, default=jsonify))
        return

    def should_output(itin):
        if sub_itins:
            return itin["valid"]
        else:
            return itin["valid"] and itin["maximal"]

    filtered_itins = enumerate(i for i in itins if should_output(i))

    for i, itin in filtered_itins:
        if fmt == "human":
            print("ITINERARY #{}".format(i + 1))
            for rec in itin["itin"]:
                print("  Flight {}: From {} (at {}) to {} (at {})".format(
                    rec["flight_number"], rec["source"], rec["departure"],
                    rec["destination"], rec["arrival"]))
        elif fmt == "flights":
            print(",".join(rec["flight_number"] for rec in itin["itin"]))
        elif fmt == "airports":
            print(",".join(rec["source"] for rec in itin["itin"]), end=",")
            print(itin["itin"][-1]["destination"])
        else:
            raise RuntimeError("Unknown output format {!r}.".format(fmt))


def parse_argv(argv):
    prs = ap.ArgumentParser(description="Find itineraries in flight list.",
                            formatter_class=ap.ArgumentDefaultsHelpFormatter)
    prs.add_argument("files", metavar="FILE", nargs="?", default="-",
                     help="Input file; '-' for STDIN.")
    prs.add_argument("-s", "--sub-itins", action="store_true",
                     help="Output sub-itineraries as separate entries.")
    prs.add_argument("-f", "--fmt", help="Output format.", default="flights",
                     choices="debug human flights airports".split())
    return prs.parse_args(argv)


def main(argv):
    args = parse_argv(argv)
    # NOTE: data will get corrupted if CSV fields contain newlines; to avoid
    # this, only accept input from a file and ``open(..., newline="")``
    rdr = csv.DictReader(finp.input(args.files))
    itins = find_itins(rdr, MINT, MAXT, args.fmt == "debug")
    output(itins, args.sub_itins, args.fmt)


if __name__ == "__main__":
    main(sys.argv[1:])
