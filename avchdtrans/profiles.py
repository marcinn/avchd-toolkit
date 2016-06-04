"""
Codecs database mgmt
"""

import collections
import os


class ProfilesRegistry(object):
    def __init__(self):
        self.clear()

    def register(self, name, quality, medium, ffmpeg_args):
        self._codecs[name][quality][medium]=ffmpeg_args

    def get(self, name, quality):
        return self._codecs[name][quality]

    def get_ffmpeg_args(self, name, quality, medium):
        return self.get(name, quality)[medium]

    def clear(self):
        self._codecs = collections.defaultdict(lambda: collections.defaultdict(dict))


registry = ProfilesRegistry()


def load_profiles_config(paths):
    paths = list(filter(None, paths))
    paths.append(os.path.join(os.path.dirname(__file__), 'codecs.ini'))

    try:
        import ConfigParser
    except ImportError:
        import configparser as ConfigParser

    cp = ConfigParser.ConfigParser()
    cp.read(paths)

    registry.clear()

    for section in cp.sections():
        profile, quality = section.split(':')
        for medium, args in cp.items(section):
            ffmpeg_args = map(
                lambda x: filter(None, map(lambda y: y.strip(), x.split(' '))),
                args.split('\n')
            )
            registry.register(profile, quality, medium, filter(None, ffmpeg_args))


