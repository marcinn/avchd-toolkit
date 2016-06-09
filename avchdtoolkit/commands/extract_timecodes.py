import os
import sys
import argparse
import csv
from .. import timecode, finder
from . import CommandError

try:
    from concurrent import futures
except ImportError:
    futures = None





def make_parser():
    parser = argparse.ArgumentParser(
            description='Extract timecodes from AVC/H264 files')

    parser.add_argument('directory', type=str, help='Media directory')

    parser.add_argument(
        '-r', '--recursive', dest='recursive', action='store_true',
        help='Walk into subdirectories',
    )

    parser.add_argument(
        '--ext', dest='extensions', action='append', type=str,
        help='add source file extension for batch processing (default: %(default)s)',
        default=['MTS', 'mts'],
    )
    return parser


def main():
    try:
        handle_main()
    except CommandError, ex:
        RESET_SEQ = "\033[0m"
        COLOR_SEQ = "\033[91m"
        sys.stdout.write(COLOR_SEQ+unicode(ex)+RESET_SEQ+'\n')
        sys.stdout.flush()


def extract_timecode(path):
    tc = timecode.extract_timecode(path)
    sys.stdout.write('%s: %s\n' % (path, tc))
    sys.stdout.flush()
    return path, tc


def handle_main():

    parser = make_parser()
    args = parser.parse_args()

    kwargs = vars(args)
    directory = kwargs.pop('directory')
    extensions = kwargs.pop('extensions')
    parallel = kwargs.pop('parallel', None)


    asyncs = []
    timecodes = []

    files = finder.find_files(directory, extensions)

    if parallel:
        with futures.ProcessPoolExecutor() as ex:
            for infile in files:
                asyncs.append(ex.submit(extract_timecode, infile))

            for obj in asyncs:
                timecodes.append(obj.result()) # raise exception if failed
    else:
        for infile in files:
            timecodes.append(extract_timecode(infile))

    timecode.write_timecodes_to_database(directory, timecodes)

