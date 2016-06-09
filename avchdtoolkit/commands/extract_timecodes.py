import os
import sys
import argparse
import csv
from .. import timecode, finder
from . import CommandError, command

try:
    from concurrent import futures
except ImportError:
    futures = None


def make_parser():
    parser = argparse.ArgumentParser(
            description='Extract timecodes from AVC/H264 files')

    parser.add_argument('directory', type=str, help='Media directory')

    #parser.add_argument(
    #    '-r', '--recursive', dest='recursive', action='store_true',
    #    help='Walk into subdirectories',
    #)

    return parser



def extract_timecode(path):
    tc = timecode.extract_timecode(path)
    sys.stdout.write('%s: %s\n' % (path, tc))
    sys.stdout.flush()
    return path, tc


@command
def main():

    parser = make_parser()
    args = parser.parse_args()

    kwargs = vars(args)
    directory = kwargs.pop('directory')
    parallel = kwargs.pop('parallel', None)

    asyncs = []
    timecodes = []

    files = finder.find_files(directory)

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

