import datetime
import os
import re

from avchdtrans import exiftool


DATE_PATTERNS = (
        (re.compile('^([0-9]{4}-[0-9]{2}-[0-9]{2}\s+[0-9]{2}:[0-9]{2}:[0-9]{2}).*'), '%Y-%m-%d %H:%M:%S'),
        (re.compile('^([0-9]{4}:[0-9]{2}:[0-9]{2}\s+[0-9]{2}:[0-9]{2}:[0-9]{2}).*'), '%Y:%m:%d %H:%M:%S'),
        )


def prettify_filename(infile, prefix='', suffix='', date_fmt='%Y%m%d%H%M%S',
        exiftool_tag='DateTimeOriginal'):

    with exiftool.ExifTool() as et:
        dt_str = et.get_tag(exiftool_tag, infile)

    if not dt_str:
        raise RuntimeError('Can\'t read datetime from file using tag=%s' % exiftool_tag)

    for pattern, re_fmt in DATE_PATTERNS:
        match = pattern.match(dt_str)
        if match:
            dt = datetime.datetime.strptime(match.groups()[0], re_fmt)
            break

    directory = os.path.dirname(infile)
    filename = os.path.basename(infile)
    filename,ext = os.path.splitext(filename)

    pretty_filename = u'%s%s%s%s' % (prefix, dt.strftime(date_fmt), suffix, ext)
    return os.path.join(directory, pretty_filename)


def pretty_rename(filename, **prettify_args):
    new_filename = prettify_filename(filename, **prettify_args)
    os.rename(filename, new_filename)


def pretty_batch_rename(files, **prettify_args):
    for filename in files:
        pretty_rename(filename, **prettify_args)


