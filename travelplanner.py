#! /usr/bin/python

# stdlib
from datetime import datetime, timedelta
from urllib.parse import urlencode
from urllib.request import urlopen
from subprocess import call
from tempfile import NamedTemporaryFile
from sys import stderr
from os import getenv

# 3rd party
from bs4 import BeautifulSoup
from dateutil.parser import parse as parsedate


_DEFAULT_ORIGIN =  # Fill in yourself
_DEFAULT_DESTINATION =  # Fill in yourself
_DEFAULT_DEPARTURE_TIME = lambda: [datetime.now()]
_DEFAULT_ARRIVAL_TIME = lambda: [datetime.now() + timedelta(hours=1,
                                                            minutes=30)]

_FORM_BASE = "http://www.octranspo1.com/travelplanner/travelplanner"


def query(src, dst, city, constraint, datetime):
    raise NotImplementedError()


def _matchdt(parser, *args):
    try:
        return parsedate(' '.join(args))
    except:
        parser.error("unparseable date")


def _matchloc(parser,
              *args,
              _map={"Cantley": "CANT",
                    "Chelsea": "CHEL",
                    "Gatineau": "GATI",
                    "Ottawa": "OTTA",
                    "Val-des-monts": "VALD"},
              _city="Ottawa"):
    """
    Convert location phrase to (address, travel planner city mnemonic) tuple.

    ["1337", "Foo", "drive"] → ("1337 Foo drive", "OTTA")
    ["DEADBEEF station, Gatineau"] → ("DEADBEEF station", "GATI")
    """
    *address, city = args
    if city in _map:
        code = _map[city]
    elif city in _map.values():
        code = city
    elif len(address) > 0 and address[-1].endswith(','):
        parser.error("Unknown city")
    else:
        code = _map[_city]
        address.append(city)

    return ' '.join(address).rstrip(', '), code


def _isolate_results(soup):
    """
    Scrape directions header, route summary, and route details"
    """
    summary = soup.find(lambda tag: tag.name == "table" and
                        "TripPlanDetailsTable" in tag.attrs.get("class",
                                                                set()))

    details = summary.find_next_sibling("ul")
    details.name = "ol"
    last = details.find_all("li")[-1]
    if last.text.strip().startswith("Thank you for using"):
        last.extract()

    header = summary.find_previous_sibling(lambda tag: tag.name == "p" and
                                           "header" in tag.attrs.get("class",
                                                                     set()))

    return header, summary, details


def _print_results(header, summary, details):
    """
    Print route information as plain text
    """
    with NamedTemporaryFile(mode="w") as tmp:
        for element in summary, details:
            tmp.write(str(element))
        tmp.flush()
        call(["links", "-dump", "-html-numbered-links", "0", tmp.name])


# TODO: Cache results
def _interact(page):
    """
    Display and recursively prompt user to page results.
    """
    soup = BeautifulSoup(page)
    # flake8 is wrong in saying that this was overindented. I don't care what
    # it thinks. The expression part of the lambda should not be *under* the
    # argument list, but to the *right*…
    earlier = soup.find(lambda tag: tag.name == "a" and
                        tag.string == "Earlier")
    later = soup.find(lambda tag: tag.name == "a" and
                      tag.string == "Later")
    walking = soup.find(lambda tag: tag.name == "a" and
                        (tag.string or "").startswith("Walking"))
    if not all([earlier, later, walking]):
        tabs = soup.find(lambda tag: tag.name == "ul" and
                         tag.attrs.get("id", None) == "tabs")
        # Yet here I must break my principle above to keep the line under
        # eighty characters wide.
        font = tabs.find_previous_sibling(lambda tag: tag.name == "font" and
                                          tag.attrs.get("color",
                                                        None) == "red")
        print("Error:", font.string, file=stderr)
        prompt = "View page in (b)rowser, (q)uit: "
        try:
            response = None
            while response not in {"b", "q"}:
                response = input(prompt).lower()
        except EOFError:
            pass
        else:
            if response == "b":
                browser = getenv("BROWSER")
                if browser is None:
                    print("$BROWSER not set")
                else:
                    with NamedTemporaryFile() as tmp:
                        tmp.write(page)
                        tmp.flush()
                        call([browser, tmp.name])

    else:
        _print_results(*_isolate_results(soup))
        prompt = "(E)arlier, (l)ater, (w)alking instructions, (q)uit: "
        try:
            response = None
            while response not in {"e", "l", "w", "q"}:
                response = input(prompt).lower()
        except EOFError:
            pass
        else:
            if response == "w":
                soup = BeautifulSoup(urlopen(walking["href"]))
                _print_results(*_isolate_results(soup))
            elif response != "q":
                _interact(urlopen({"e": earlier,
                                   "l": later}[response]["href"]))


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Query optimal bus route with"
                                        " OC Transpo travel planner")
    for name, desc, default in [("--src", "Departing from…",
                                 _DEFAULT_ORIGIN),
                                ("--dst", "Arriving at…",
                                 _DEFAULT_DESTINATION)]:
        parser.add_argument(name,
                            help=desc,
                            default=default,
                            nargs="*",
                            metavar="address part")

    # Must add roughly five-ten minutes or form complains that departure time
    # is in the past.
    parser.add_argument("--skew",
                        help="OC Transpo system time skew relative to us",
                        default=10,
                        nargs=1,
                        type=int)

    group = parser.add_mutually_exclusive_group(required=True)
    for flag, desc, default in [("--departure",
                                 "Departing at…",
                                 _DEFAULT_DEPARTURE_TIME()),
                                ("--arrival",
                                 "Arriving at…",
                                 _DEFAULT_ARRIVAL_TIME())]:
        group.add_argument(flag,
                           help=desc,
                           default=default,
                           nargs="*",
                           metavar="datetime part")

    args = parser.parse_args()

    origin, originRegion = _matchloc(parser, *args.src)
    destination, destinationRegion = _matchloc(parser, *args.dst)
    constraint = _matchdt(parser, *map(str, (args.arrival or args.departure)))
    constraint += timedelta(minutes=args.skew)
    qs = urlencode({"origin": origin,
                    "originRegion": originRegion,
                    "destination": destination,
                    "destinationRegion": destinationRegion,
                    "timeType": 4 if args.arrival else 3,
                    "hour": constraint.strftime("%I").lstrip('0'),
                    "minute": constraint.minute,
                    "pm": constraint.strftime("%p") == "PM",
                    "day": constraint.strftime("%Y%m%d")})
    response = urlopen('?'.join([_FORM_BASE, qs]))
    _interact(response.read())
