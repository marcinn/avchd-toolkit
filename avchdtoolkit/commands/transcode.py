import os
import sys
import argparse
from .. import profiles
from . import command, CommandError, load_config

try:
    from concurrent import futures
except ImportError:
    futures = None


def assignment(x):
    return x.split('=')



def make_parser():

    class HelpAction(argparse._HelpAction):
        def __call__(self, parser, *args, **kw):
            print parser.format_help()
            print "\nAvailable profiles:\n"

            for profile in profiles.registry.registered_keys():
                desc = profiles.registry.description(profile) or 'no description'
                print("{:<20} {}".format(profile, desc))

            sys.exit(0)

    parser = argparse.ArgumentParser(
            description='Transcode wrapper for FFMPEG', add_help=False)
    parser.add_argument('-h', '--help', action=HelpAction,
            help='show this help message and exit')

    parser.add_argument('inputs', type=str, nargs='+',
        help='Input files or directories', metavar='INPUT')

    parser.add_argument('output', type=str,
        help='Output directory', metavar='OUTPUT')

    add_parser_options(parser)
    return parser


def add_parser_options(parser):
    #parser.add_argument(
    #    '-d', '--deshake', dest='deshake', action='store', type=int,
    #    help='enable extra deshaking pass (requires shakiness value)',
    #    metavar='SHAKINESS',
    #)

    try:
        default_profile = profiles.registry.default_key()
    except TypeError:
        default_profile=None

    parser.add_argument(
        '-r', '--rename', dest='rename', action='store_true',
        help='enable automagical renaming files based on original shot time',
    )

    parser.add_argument(
        '-p', '--profile', dest='profile', action='store',
        help='output profile name (default: "%(default)s")',
        default=default_profile,
    )

    parser.add_argument(
        '-m', '--meta', dest='meta', action='append', type=assignment,
        help='add meta tag (use multiple options for setting more tags at once)',
        default=[],
        )

    parser.add_argument(
        '-t', '--timecode', dest='timecode', type=str, default=None,
        help='set explicit timecode (by default timecode is extracted from source)',
        )

    parser.add_argument(
        '--force', dest='force_overwrite', action='store_true', default=False,
        help='force output files overwriting without confirmation',
        )

    parser.add_argument(
        '--parallel', dest='parallel', action='store_true', default=False,
        help='Use experimental multiprocessing (default: %(default)s)',
    )

    parser.add_argument(
        '--pix_fmt', dest='pix_fmt', action='store', type=str,
        help='pix fmt (default: auto)',
    )

    return parser



def transcode_command(**userargs):

    from ..conversion import execute
    from ..finder import find_files

    inputs = userargs.pop('inputs')
    parallel = userargs.pop('parallel')
    usermeta = dict(userargs.pop('meta'))

    batch = []

    for path in inputs:
        if os.path.isdir(path):
            files = find_files(path)

            meta = {}

            # read reel_name for batch processing
            try:
                with open(os.path.join(path, '.reel_name')) as fh:
                    reel_name = fh.readline().strip()
            except IOError:
                pass
            else:
                meta['reel'] = reel_name

            meta.update(usermeta)

            for filename in files:
                data = {'infile': filename, 'meta': meta}
                data.update(userargs)
                batch.append(data)
        else:
            data = {'infile': path, 'meta': usermeta}
            data.update(userargs)
            batch.append(data)


    if parallel:
        if not futures:
            raise CommandError('Please install `futures` packate to enable parallel transcoding')

        if not userargs.get('force_overwrite'):
            raise CommandError('Parallel processing requires enabling of --force flag')

        asyncs = []

        with futures.ProcessPoolExecutor() as ex:
            for cmdargs in batch:
                asyncs.append(ex.submit(execute, **cmdargs))

        for obj in asyncs:
            obj.result() # raise exception if failed

    else:
        for cmdargs in batch:
            execute(**cmdargs)



@command
def main():
    load_config()
    parser = make_parser()
    args = parser.parse_args()
    userargs = dict(vars(args)) # copy
    transcode_command(**userargs)

