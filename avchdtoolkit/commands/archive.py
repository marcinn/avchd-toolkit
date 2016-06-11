from __future__ import print_function

import os
import sys
import argparse

from .extract_timecodes import extract_timecodes
from .transcode import add_parser_options as add_transcode_parser_options
from .transcode import transcode_command
from . import CommandError, command, load_config
from .. import archive, finder, renamer


def directory(x):
    if not os.path.isdir(x):
        raise CommandError('%s is not a directory' % x)
    return x


def variable_assignment(x):
    try:
        key,value=x.split('=',1)
    except IndexError:
        raise CommandError('Invalid variable assignment format')
    else:
        return key.strip(), value.strip()


def make_parser():

    parser = argparse.ArgumentParser(
        description='AVCHD archive management tool')

    parser.add_argument(
            'directory', type=directory, default=os.getcwd(),
            help='Path to the archive directory',
            metavar='DIRECTORY')

    subparsers = parser.add_subparsers(
            title='available commands', dest='command')

    tag_parser =  subparsers.add_parser(
            'tag', help='Change information of the archive')
    tag_parser.add_argument(
            'variables', type=variable_assignment, nargs='+',
            help='Variable assignment (example: reel=REEL_NAME)',
            action='store', default=None, metavar='VAR',
    )

    init_parser = subparsers.add_parser(
            'initialize', help='Initialize the archive')

    init_parser.add_argument(
            'reel', type=str, metavar='REEL',
            help='Reel name')

    info_parser =  subparsers.add_parser(
            'info', help='Show information about archive')

    dumptc_parser =  subparsers.add_parser(
            'extract-timecodes',
            help='Read timecodes from H264 files and save in the archive')

    tc_parser =  subparsers.add_parser(
            'timecodes', help='Show saved timecodes')

    fixnames_parser =  subparsers.add_parser(
            'fix-names', help='Magically fix video filenames in the archive')

    fixnames_parser.add_argument(
            '-p', '--prefix', type=str, dest='prefix',
            help='Name prefix', default='', action='store')

    fixnames_parser.add_argument(
            '-s', '--suffix', type=str, dest='suffix',
            help='Name suffix', default='', action='store')

    fixnames_parser.add_argument(
            '-f', '--date-format', type=str, dest='date_fmt',
            help='Date format (default: %(default)s)', metavar='FORMAT',
            default='%Y%m%d%H%M%S')

    transcode_parser = subparsers.add_parser('transcode',
            help='Transcode archive into proxy/intermediate')

    transcode_parser.add_argument('output', type=directory,
            help='Output directory', metavar='OUTPUT')

    add_transcode_parser_options(transcode_parser)

    return parser


def tag(directory, variables):
    arc = archive.read(directory)
    for key, value in variables:
        try:
            arc.set(key,value)
        except (AttributeError, TypeError):
            raise CommandError('Unsupported variable `%s`' % key)
    arc.save()
    info(directory)


def dumptimecodes(directory, parallel=False):
    arc = archive.read(directory)
    timecodes = extract_timecodes(directory, parallel=parallel, quiet=False)
    arc.replace_timecodes(dict(timecodes))
    arc.save()


def timecodes(directory, parallel=False):
    arc = archive.read(directory)
    for row in arc.timecodes.items():
        print("%s=%s" % row)


def fixnames(directory, prefix=None, suffix=None, date_fmt=None):
    arc = archive.read(directory)
    files = finder.find_files(directory)

    ops = []

    for path in files:
        basename = os.path.basename(path)
        tc = arc.get_timecode(basename)

        print('Generating new name for file `%s`...' % basename)

        try:
            renamed_path = renamer.prettify_filename(
                path, prefix=prefix, suffix=suffix, date_fmt=date_fmt)
        except renamer.RenameError, ex:
            print('Can\'t generate new name for `%s`: %s' % (basename, ex))
            continue

        if os.path.exists(renamed_path):
            print('Can\'t rename `%s` because the target exists' % (path, renamed_path))
            continue

        ops.append((path, renamed_path, tc))

    try:
        for original, renamed, tc in ops:
            baseorg = os.path.basename(original)
            baserenamed = os.path.basename(renamed)

            print('Renaming %s -> %s' % (baseorg, baserenamed))

            if tc:
                arc.set_timecode(baserenamed, tc)
                arc.remove_timecode(baseorg)
            os.rename(original, renamed)
    finally:
        print('Updating archive database')
        arc.save()

    print('Done.')


def info(directory):
    arc = archive.read(directory)

    print('Directory:', arc.path)
    print('Name     :', arc.name)
    print('Timecodes:', 'available' if arc.timecodes else '(not set)')
    print('Reel name:', arc.reel_name or '(not set)')


def transcode(directory, **kw):
    arc = archive.read(directory)
    inputs = arc.video_files()

    meta = dict(kw.pop('meta', []))
    meta['reel']=arc.reel_name

    args = {}
    args.update(kw)
    args.update({
        'inputs': inputs,
        'meta': meta.items(),
        })

    transcode_command(**args)


def initialize(directory, reel):

    arc = archive.read(directory)

    if arc.reel_name:
        raise CommandError('The archive was already initialized')

    print('Initializing archive...')
    print('Setting reel name:', reel)
    tag(directory, variables=[('reel', reel)])

    print('Extracting timecodes')
    dumptimecodes(directory)

    print('Fixing names')
    fixnames(directory)

    print('Initialization complete.\n')
    info(directory)


@command
def main():
    load_config()

    parser = make_parser()
    args = parser.parse_args()

    kwargs = dict(vars(args))
    cmd = kwargs.pop('command')

    subcommands = {
            'tag': tag,
            'info': info,
            'extract-timecodes': dumptimecodes,
            'timecodes': timecodes,
            'fix-names': fixnames,
            'transcode': transcode,
            'initialize': initialize,
            }

    subcommands[cmd](**kwargs)

