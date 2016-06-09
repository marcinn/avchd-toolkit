import os
import mimetypes


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

