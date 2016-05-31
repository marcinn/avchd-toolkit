
import argparse

parser = argparse.ArgumentParser(description='Transcode with ffmpeg')

parser.add_argument(
    '-d', '--deshake', dest='deshake', action='store_true',
    help='enable deshaking'
)

parser.add_argument(
    '-s', '--shakiness', dest='shakiness', action='store',
    help='shakiness level (default=5)', default=5, type=int,
)

parser.add_argument(
    '-p', '--profile', dest='profile', action='store',
    help='transcoding profile (default=high)', default='high',
    choices=['proxy', 'low', 'standard', 'hq'],
)

parser.add_argument(
    '-b', '--bits', dest='bits', action='store', type=int,
    help='bit depth (default=8)', default=8,
    choices=[8, 10, 12],
)

parser.add_argument(
    '-f', '--format', dest='format', action='store',
    help='output format (default=prores)', default='prores',
    choices=['prores', 'dnxhd'],
)

args = parser.parse_args()
print args
