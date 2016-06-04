import os
import sys
import argparse

try:
    from concurrent import futures
except ImportError:
    futures = None


def assignment(x):
    return x.split('=')


class CommandError(Exception):
    pass


def make_parser():

    parser = argparse.ArgumentParser(description='Transcode wrapper for FFMPEG')


    parser.add_argument('inputs', type=str, nargs='*',
        help='Input file paths', metavar='FILE')

    parser.add_argument('-o', '--outfile', type=str,
        help='Output file path (default: basename of input with changed extension)',
    )

    parser.add_argument(
        '-d', '--deshake', dest='deshake', action='store', type=int,
        help='enable extra deshaking pass (requires shakiness value)',
        metavar='SHAKINESS',
    )

    parser.add_argument(
        '-r', '--rename', dest='rename', action='store_true',
        help='enable automagical renaming files based on original shot time',
    )

    parser.add_argument(
        '-s', '--source-dir', dest='source_dir', action='store', type=str,
        help='source directory for batch processing',
    )
    
    parser.add_argument(
        '--ext', dest='source_extensions', action='append', type=str,
        help='add source file extension for batch processing (default: %(default)s)',
        default=['MTS', 'mts'],
    )

    parser.add_argument(
        '-x', '--export-dir', dest='export_dir', action='store', type=str,
        help='export/output directory (default: same as original file)',
    )

    parser.add_argument(
        '-q', '--quality', dest='quality', action='store',
        help='transcoding quality (default: %(default)s)', default='high',
        choices=['proxy', 'low', 'standard', 'high'],
    )

    parser.add_argument(
        '--pix_fmt', dest='pix_fmt', action='store', type=str,
        help='pix fmt (default: auto)',
    )

    parser.add_argument(
        '-f', '--profile', dest='profile', action='store',
        help='output profile name (default: %(default)s)', default='prores',
        choices=['prores', 'dnxhd', 'mpeg'],
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

    return parser


def main():

    import pkg_resources
    from .profiles import load_profiles_config
    from .conversion import execute
    from .finder import find_files

    configs = (
            os.path.join(os.path.expanduser('~'), '.config', 'avchdtranscode', 'codecs.ini'),
            os.path.sep+os.path.join('etc', 'avchdtrans', 'codecs.ini'),
            os.environ.get('AVCHDTRANSCODE_CODECS', None),
            pkg_resources.resource_filename('avchdtrans', 'codecs.ini'),
        )

    load_profiles_config(paths=configs)

    parser = make_parser()
    args = parser.parse_args()

    kwargs = vars(args)
    files = kwargs.pop('inputs')
    source_dir = kwargs.pop('source_dir')
    source_extensions = kwargs.pop('source_extensions')
    parallel = kwargs.pop('parallel')

    if files and source_dir:
        raise CommandError('You can\'t use batch mode together with processing individual files')

    if source_dir:
        files = find_files(source_dir, source_extensions)

        # read reel_name for batch processing
        if not args.meta or not 'reel' in dict(args.meta):
            try:
                with open(os.path.join(source_dir, '.reel_name')) as fh:
                    reel_name = fh.readline()
            except IOError:
                pass
            else:
                kwargs['meta'].append(('reel', reel_name))

    if len(files)>1:
        if not args.export_dir:
            raise CommandError('You must set export dir (-x) for multiple inputs')

        if args.outfile:
            raise CommandError('You can\'t use output filename for multiple inputs')

    if parallel:
        if not futures:
            raise CommandError('Please install `futures` packate to enable parallel transcoding')

        if not args.force_overwrite:
            raise CommandError('Parallel processing requires enabling of --force flag')

        asyncs = []

        with futures.ProcessPoolExecutor() as ex:
            for infile in files:
                asyncs.append(ex.submit(execute, infile, **vars(args)))

        for obj in asyncs:
            obj.result() # raise exception if failed

    else:
        for infile in files:
            execute(infile, **kwargs)
