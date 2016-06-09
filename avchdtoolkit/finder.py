import glob
import os


def find_files(directory, extensions):
    results = []
    for ext in extensions:
        pattern = os.path.join(directory, '*.%s' % ext)
        results += glob.glob(pattern)
    return sorted(results)

