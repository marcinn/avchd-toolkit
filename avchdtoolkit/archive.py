import os
import csv
from . import finder


class Archive(object):
    def __init__(self, path, reel_name=None, timecodes=None):
        self.path = os.path.realpath(path)
        self.reel_name = reel_name
        self.timecodes = timecodes
        self.name = os.path.basename(self.path)

    def get_timecode(self, name):
        if self.timecodes is None:
            return None
        return self.timecodes.get(name)

    def set_timecode(self, name, value):
        if self.timecodes is None:
            self.timecodes={}
        self.timecodes[name]=value

    def remove_timecode(self, name):
        self.timecodes.pop(name)

    def get_timecodes(self):
        return dict(self.timecodes)

    def set_reel(self, reel_name):
        self.reel_name = reel_name.strip()

    def set(self, attr, value):
        return getattr(self, 'set_%s' % attr)(value)

    def replace_timecodes(self, timecodes):
        self.timecodes = timecodes

    def update_timecodes(self, timecodes):
        self.timecodes.update(timecodes)

    def clear_timecodes(self):
        self.timecodes = {}

    def save(self):
        ArchiveManager(self.path).save(self)

    def video_files(self):
        return finder.find_files(self.path)


class ArchiveManager(object):
    def __init__(self, path):
        self.path = path
        self._dbpath = os.path.join(path, '.avchdtoolkit')

    def load(self):
        reel_name = self._read_reel()
        timecodes = self._read_timecodes()
        return Archive(self.path, reel_name=reel_name, timecodes=timecodes)

    def save(self, archive):
        if archive.reel_name is not None:
            self._save_reel(archive.reel_name)
        if archive.timecodes is not None:
            self._save_timecodes(archive.timecodes)

    def _read_reel(self):
        try:
            with open(os.path.join(self.path, '.reel_name')) as fh:
                return fh.readline().strip()
        except IOError:
            return

    def _read_timecodes(self):
        try:
            with open(os.path.join(self.path, '.timecodes')) as fh:
                csvreader = csv.reader(fh)
                timecodes = {}
                for name, tc in csvreader:
                    timecodes[name]=tc
                return timecodes
        except IOError:
            return

    def _save_reel(self, reel_name):
        with open(os.path.join(self.path, '.reel_name'), 'w') as fh:
            fh.write(reel_name)

    def _save_timecodes(self, timecodes):
        with open(os.path.join(self.path, '.timecodes'), 'w') as fh:
            tcwriter = csv.writer(fh)
            for path,tc in timecodes.items():
                tcwriter.writerow([os.path.basename(path),tc])


def read(path):
    return ArchiveManager(path).load()


def save(archive):
    return ArchiveManager(archive.path).save(archive)


