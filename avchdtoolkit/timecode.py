import csv
import os
from . import exiftool, archive


class NoTimecodeFound(Exception):
    pass


NON_NATIVE_TC_MIMETYPES = (
        'video/m2ts',
        'video/mp2t',
        'video/mp4',
        'video/m4v',
        )


def read_timecode_from_database(infile):
    basename = os.path.basename(infile)

    arc = archive.read(os.path.dirname(infile))
    tc = arc.get_timecode(basename)

    if not tc:
        raise NoTimecodeFound

    return tc


def write_timecodes_to_database(directory, timecodes):
    arc = archive.read(directory)
    arc.replace_timecodes(dict(timecodes))
    archive.save(arc)


def extract_timecode(infile):
    with exiftool.ExifTool() as et:
        mime = et.get_tag('MIMEType', infile)

        if mime in NON_NATIVE_TC_MIMETYPES:
            out = et.execute('-TimeCode', '-ee', '-s3', infile)
            try:
                return sorted(filter(None, map(lambda x: x[-11:], out.split('\n'))))[0]
            except IndexError:
                return
        else:
            return et.get_tag('TimeCode', infile)


