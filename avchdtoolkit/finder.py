import os
import mimetypes
import archive


def find_files(directory):
    results = []
    for dirpath, dirnames, filenames in os.walk(directory, topdown=False):
        for name in filenames:
            fullpath = os.path.join(dirpath, name)
            mimetype,enc=mimetypes.guess_type('file://%s' % fullpath)
            if mimetype:
                category = mimetype.split('/')[0]
                if category=='video':
                    results.append(fullpath)

    return sorted(results)


def find_archives(directory, reel=None, recursive=False):
    results = []
    if reel:
        reel_lower = reel.lower()

    for dirpath, dirnames, filenames in os.walk(directory, topdown=recursive):
        for dirname in dirnames:
            try:
                arc = archive.read(os.path.join(dirpath,dirname))
            except IOError:
                pass
            else:
                if reel:
                    if arc.reel_name and (reel_lower=='*' or reel_lower in arc.reel_name.lower()):
                        results.append(arc)
                else:
                    results.append(arc)

    return results

