from . import exiftool


NON_NATIVE_TC_MIMETYPES = (
        'video/m2ts',
        'video/mp2t',
        'video/mp4',
        'video/m4v',
        )



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



