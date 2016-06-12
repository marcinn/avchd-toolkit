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
    if x:
        if not os.path.isdir(x):
            raise CommandError('%s is not a directory' % x)
    else:
        x = os.getcwd()
    return x


def variable_assignment(x):
    try:
        key,value=x.split('=',1)
    except IndexError:
        raise CommandError('Invalid variable assignment format')
    else:
        return key.strip(), value.strip()


def _add_directory_arg(parser):
    parser.add_argument(
            'directory', type=directory, default='',
            help='Path to the archive directory',
            metavar='ARCHIVE_DIR', nargs='?')

def make_parser():

    parser = argparse.ArgumentParser(
        description='AVCHD archive management tool')

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
    init_parser.add_argument(
            '-r', '--rename', dest='fix_names',
            default=False, action='store_true',
            help='Auto fix names during initialization')
    init_parser.add_argument(
            '-t', '--extract-timecodes', dest='dump_timecodes',
            default=False, action='store_true',
            help='Extract timecodes during initialization')

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

    _add_directory_arg(transcode_parser)
    transcode_parser.add_argument('output', type=directory,
            help='Output directory', metavar='OUTPUT')

    add_transcode_parser_options(transcode_parser)


    finder_parser = subparsers.add_parser(
            'find', help='Find archives matching query')
    finder_parser.add_argument(
            'directory', metavar='DIRECTORY', nargs='?', type=directory,
            default=os.getcwd(), help='Search directory')
    finder_parser.add_argument(
            'terms', metavar='TERM', nargs='*', type=variable_assignment,
            help='Query terms in key=value format')
    finder_parser.add_argument(
            '-v', '--invert-match', action='store_true',
            dest='invert_match', help='Show non matching archives')
    finder_parser.add_argument(
            '-l', '--only-filenames', action='store_true',
            dest='filenames_only', help='Show only filenames')

    list_parser = subparsers.add_parser(
            'list', help='List archive contents (video files)',
            )

    _add_directory_arg(tag_parser)
    _add_directory_arg(init_parser)
    _add_directory_arg(info_parser)
    _add_directory_arg(dumptc_parser)
    _add_directory_arg(tc_parser)
    _add_directory_arg(fixnames_parser)
    _add_directory_arg(list_parser)

    return parser


def tag(directory, variables, show_info=True):
    arc = archive.read(directory)
    for key, value in variables:
        try:
            arc.set(key,value)
        except (AttributeError, TypeError):
            raise CommandError('Unsupported variable `%s`' % key)
    arc.save()
    if show_info:
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
    files = finder.find_video_files(directory)

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


def initialize(directory, reel, fix_names=False, dump_timecodes=False):

    arc = archive.read(directory)

    if arc.reel_name:
        raise CommandError('The archive was already initialized')

    print('Initializing archive...')
    print('Setting reel name:', reel)
    tag(directory, variables=[('reel', reel)], show_info=False)

    if dump_timecodes:
        print('Extracting timecodes')
        dumptimecodes(directory)

    if fix_names:
        print('Fixing names')
        fixnames(directory)

    print('Initialization complete.\n')
    info(directory)


def find_archives(directory, terms, fullpath=False, filenames_only=False,
        invert_match=False):
    kwargs = dict(terms)

    #print('Searching for archives in `%s`' % directory)

    try:
        results = finder.find_archives(directory, invert_match=invert_match, **kwargs)
    except TypeError:
        raise CommandError('Unsopported terms in query')

    if fullpath:
        path_func = lambda x: os.path.abspath(x)
    else:
        path_func = lambda x: os.path.relpath(x, directory)

    if filenames_only:
        for result in results:
            print(path_func(result.path))
    else:
        for result in results:
            path = path_func(result.path)
            print('%s:\t(reel=%s)' % (path, result.reel_name)) 


def list_video_files(directory):
    results = finder.find_video_files(directory)
    for result in results:
        print(os.path.relpath(result, directory))


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
            'find': find_archives,
            'list': list_video_files,
            }

    subcommands[cmd](**kwargs)

