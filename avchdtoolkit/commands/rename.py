
import os
import sys
import argparse

from . import CommandError, command


def make_parser():

    parser = argparse.ArgumentParser(
        description='Rename files based on shoot time extracted from video metadata')


    parser.add_argument(
            'inputs', type=str, nargs='+',
            help='Input file paths', metavar='FILE'
    )

    parser.add_argument(
            '-p', '--prefix', type=str, dest='prefix',
            help='Name prefix', default='', action='store',
    )

    parser.add_argument(
            '-s', '--suffix', type=str, dest='suffix',
            help='Name suffix', default='', action='store',
    )

    parser.add_argument(
            '-f', '--date-format', type=str, dest='date_fmt',
            help='Date format (default: %(default)s)', metavar='FORMAT',
            default='%Y%m%d%H%M%S',
    )

    return parser


@command
def main():
    from .. import renamer

    parser = make_parser()
    args = parser.parse_args()

    kwargs = vars(args)
    inputs= kwargs.pop('inputs')

    renamer.pretty_batch_rename(inputs, **kwargs)

