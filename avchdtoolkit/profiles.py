"""
Codecs database mgmt
"""

import os


class Profile(object):
    def __init__(self,
            container, description=None, audio_args=None, video_args=None):
        self.container = container
        self.description = description
        self.ffmpeg_args = {
                'audio': list(audio_args or []),
                'video': list(video_args or []),
                }


class ProfilesRegistry(object):
    def __init__(self):
        self.clear()

    def register(self, name, profile):

        if not name in self._codecs_list:
            self._codecs_list.append(name)

        self._codecs[name]=profile

    def get(self, name):
        return self._codecs[name]

    def registered_keys(self):
        return self._codecs_list[:]

    def get_default(self):
        if self._default:
            return self.get(*self.default_key())

    def default_key(self):
        return self._codecs_list[0]

    def description(self, name):
        return self.get(name).description or ''

    def get_ffmpeg_args(self, name, medium):
        return self.get(name).ffmpeg_args[medium]

    def clear(self):
        self._codecs = {}
        self._codecs_list = []


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

    def parse_args(args):
        return filter(None, map(
            lambda x: filter(None, map(lambda y: y.strip(), x.split(' '))),
            args.split('\n')
        ))

    def getopt(section, name):
        try:
            return cp.get(section, name)
        except ConfigParser.NoOptionError:
            return

    for profile_name in cp.sections():
        video_args = parse_args(cp.get(profile_name, 'video'))
        audio_args = parse_args(cp.get(profile_name, 'audio'))
        container = cp.get(profile_name, 'container')
        description = getopt(profile_name, 'description')

        profile = Profile(
                container=container, description=description,
                audio_args=audio_args, video_args=video_args)

        registry.register(profile_name, profile)


