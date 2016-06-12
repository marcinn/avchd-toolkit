import os
import mimetypes
import archive


def is_video_file(fullpath):
    mimetype,enc=mimetypes.guess_type('file://%s' % fullpath)
    if mimetype:
        category = mimetype.split('/')[0]
        return category=='video'
    return False


def find_video_files(directory, recursive=False):
    results = []

    if recursive:
        for dirpath, dirnames, filenames in os.walk(directory, topdown=False):
            for name in filenames:
                fullpath = os.path.join(dirpath, name)
                if is_video_file(fullpath):
                    results.append(fullpath)
    else:
        for entry in os.listdir(directory):
            fullpath = os.path.join(directory, entry)
            if os.path.isfile(fullpath) and is_video_file(fullpath):
                results.append(fullpath)

    return sorted(results)


def find_archives(directory, reel=None, invert_match=False):
    results = []
    if reel:
        reel_lower = reel.lower()

    matching_rules = (
            lambda arc: reel=='*' and arc.reel_name is not None,
            lambda arc: reel and arc.reel_name and reel_lower in arc.reel_name.lower(),
            lambda arc: not reel and not arc.reel_name,
            lambda arc: reel is None,
            )

    for dirpath, dirnames, filenames in os.walk(directory):
        for dirname in dirnames:
            try:
                arc = archive.read(os.path.join(dirpath,dirname))
            except IOError:
                pass
            else:
                test = any(map(lambda x: x(arc), matching_rules))
                if invert_match:
                    test = not test
                if test:
                    results.append(arc)

    return results

