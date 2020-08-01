import functools
from math import inf
import os

from blessings import Terminal

import bini


FREELANCER_ROOT = None  # To be set by user of module
cached = functools.lru_cache(maxsize=None)


def print_universe_map():
    # Read map data
    universe = load_ini("DATA/UNIVERSE/universe.ini")
    position_to_nickname = {}
    for section, entries in universe:
        if section != "system":
            continue
        system = section_dict(entries)
        position_to_nickname[system["pos"]] = system["nickname"]

    # Calculate coordinate bounding box
    x_min, x_max = inf, -inf
    y_min, y_max = inf, -inf
    for x, y in position_to_nickname.keys():
        x_min = min(x_min, x)
        x_max = max(x_max, x)
        y_min = min(y_min, y)
        y_max = max(y_max, y)

    # Print map
    t = Terminal()
    colors = {
        "Li": t.blue,
        "Br": t.red,
        "Ku": t.magenta,
        "Rh": t.green,
        "Bw": t.white,
        "Iw": t.yellow,
        "Ew": t.cyan,
        "":   t.white,
    }
    other = t.black_on_white
    for y in range(y_min, y_max + 1):
        for x in range(x_min, x_max + 1):
            nickname = position_to_nickname.get((x, y), "")
            color_fn = colors.get(nickname[:2], other)
            cell = color_fn(nickname)
            if len(nickname) < 5:
                cell += (5 - len(nickname)) * " "
            print(cell, end="")
        print()
        print()


@cached
def load_ini(path):
    rooted_path = os.path.join(FREELANCER_ROOT, path)
    with open(rooted_path, "rb") as f:
        return bini.load(f)


def section_dict(entries):
    """Convert a section with unique keys to a dictionary

    For section entries that have mutliple values the values are put in a
    tuple. For section entries with only one value, the value is used
    directly without a wrapping tuple.

    Example input:

    [section]
    foo = bar
    baz = 1, 2, 3

    Example output:
    {
        "foo": "bar",
        "baz": (1, 2, 3),
    }
    """
    result = {}
    for key, values in entries:
        assert key not in result
        if len(values) == 1:
            result[key] = values[0]
        else:
            result[key] = tuple(values)
    return result


if __name__ == "__main__":
    import sys
    if "FREELANCER_ROOT" not in os.environ:
        print("Environment variable FREELANCER_ROOT not set")
        sys.exit(1)
    FREELANCER_ROOT = os.environ["FREELANCER_ROOT"]
    print_universe_map()
