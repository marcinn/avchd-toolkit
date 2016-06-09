"""
Codecs database mgmt
"""

import collections
import os


class ProfilesRegistry(object):
    def __init__(self):
        self.clear()

    def register(self, name, quality, medium, ffmpeg_args):
        if not (name,quality) in self._codecs_list:
            self._codecs_list.append((name, quality))
        self._codecs[name][quality][medium]=list(ffmpeg_args)

    def register_description(self, name, quality, description):
        self._descriptions['%s:%s' % (name,quality)]=description

    def get(self, name, quality):
        return self._codecs[name][quality]

    def registered_keys(self):
        return self._codecs_list[:]

    def get_default(self):
        if self._default:
            return self.get(*self.default_key())

    def default_key(self):
        return self._codecs_list[0]

    def description(self, name, quality):
        return self._descriptions.get('%s:%s' % (name, quality)) or ''

    def get_ffmpeg_args(self, name, quality, medium):
        return self.get(name, quality)[medium]

    def clear(self):
        self._codecs = collections.defaultdict(lambda: collections.defaultdict(dict))
        self._codecs_list = []
        self._descriptions = {}


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
            if medium in ('audio', 'video'):
                ffmpeg_args = map(
                    lambda x: filter(None, map(lambda y: y.strip(), x.split(' '))),
                    args.split('\n')
                )
                registry.register(profile, quality, medium, filter(None, ffmpeg_args))
        try:
            desc = cp.get(section, 'description')
        except ConfigParser.NoOptionError:
            pass
        else:
            registry.register_description(profile, quality, desc)


