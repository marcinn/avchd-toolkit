import csv
import os
from . import exiftool


class NoTimecodeFound(Exception):
    pass


NON_NATIVE_TC_MIMETYPES = (
        'video/m2ts',
        'video/mp2t',
        'video/mp4',
        'video/m4v',
        )


def read_timecode_from_database(infile):
    dbfile = os.path.join(os.path.dirname(infile), '.timecodes')
    basename = os.path.basename(infile)

    try:
        fh = open(dbfile)
    except IOError:
        raise NoTimecodeFound

    tcreader=csv.reader(fh)
    for fname,tc in tcreader:
        if fname==basename:
            fh.close()
            return tc

    fh.close()
    raise NoTimecodeFound


def write_timecodes_to_database(directory, timecodes):
    with open(os.path.join(directory, '.timecodes'), 'w') as fh:
        tcwriter = csv.writer(fh)
        for path,tc in timecodes:
            tcwriter.writerow([os.path.basename(path),tc])


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


