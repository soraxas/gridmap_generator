#!/usr/bin/env python
"""Gridmap Generator

Usage:
  main.py <IMAGE> [options] [-v|-vv|-vvv]
  main.py <IMAGE> <OUTPUT_FILE> [options] [-v|-vv|-vvv]
  main.py (-h | --help)
  main.py --version

Arguments:
  <IMAGE>                An image that represent the map.
                          [default: "./maps/simple.map"]
  <OUTPUT_FILE>          A filename that represent the output map.
                          [default: "./generated_map.map"]

General Options:
  -b --block-size=SIZE   Grid block size.
                          [default: 25]

  -h --help              Show this screen.
  --version              Show version.
  -v --verbose           Display debug message.

Display Options:
  -s --scaling=SCALING   Set scaling for display (ratio will be maintained).
                         [default: 1.0]
"""
from docopt import docopt
import logging
import sys
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '' # hide pygame prompt

from map_generator import MAPD

LOGGER = logging.getLogger()
def main():
    args = docopt(__doc__, version='MAPD Research v1.0')
    if args['<OUTPUT_FILE>'] is None:
        args['<OUTPUT_FILE>'] = "./generated_map.map"

    if args['--verbose'] > 2:
        LOGGER.setLevel(logging.DEBUG)
    elif args['--verbose'] > 1:
        LOGGER.setLevel(logging.INFO)
    elif args['--verbose'] > 0:
        LOGGER.setLevel(logging.WARNING)
    else:
        LOGGER.setLevel(logging.ERROR)
    # INFO includes only loading
    # DEBUG includes all outputs
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    LOGGER.addHandler(ch)

    LOGGER.debug("commandline args: {}".format(args))

    mapd = MAPD(args)
    return mapd


if __name__ == '__main__':
    # run if run from commandline
    mapd = main()
    mapd.run()
