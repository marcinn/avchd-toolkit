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



def extract_timecode(path, quiet=False):
    tc = timecode.extract_timecode(path)
    if not quiet:
        sys.stdout.write('%s=%s\n' % (os.path.basename(path), tc))
        sys.stdout.flush()
    return path, tc


def extract_timecodes(directory, parallel=False, quiet=False):
    asyncs = []
    timecodes = []

    files = finder.find_video_files(directory)

    if parallel:
        with futures.ProcessPoolExecutor() as ex:
            for infile in files:
                asyncs.append(ex.submit(extract_timecode, infile, quiet=quiet))

            for obj in asyncs:
                timecodes.append(obj.result()) # raise exception if failed
    else:
        for infile in files:
            timecodes.append(extract_timecode(infile, quiet=quiet))

    return timecodes


@command
def main():

    parser = make_parser()
    args = parser.parse_args()

    kwargs = vars(args)
    directory = kwargs.pop('directory')
    parallel = kwargs.pop('parallel', None)

    extract_timecodes(directory, parallel=parallel, quiet=False)


