import os
import sys

from .profiles import registry
from .ffmpeg import execute_ffmpeg
from .metadata import metadatahandler_factory
from . import timecode as timecode_mod


class Medium(object):
    def __init__(self, meta=None, ffmpeg_args=None):
        self.meta = {}
        self.ffmpeg_args = list(ffmpeg_args or []) # copy

    def _metadata_argname(self):
        return '-metadata'

    def add_args(self, *args):
        self.ffmpeg_args.append(args)

    def meta_args(self):
        args = []

        for key, value in self.meta.items():
            args.append(self._metadata_argname())
            args.append('%s=%s' % (key,value))

        return args

    def args(self):
        args = self.meta_args()
        for arg in self.ffmpeg_args:
            args += arg
        return args


class Container(Medium):
    def __init__(self, fileext, video=None, audio=None, **kw):
        super(Container, self).__init__(**kw)
        self.videos = []
        self.audios = []
        self.fileext = fileext

        if video:
            self.add_video(video)

        if audio:
            self.add_audio(audio)

    def add_video(self, video):
        self.videos.append(video)

    def add_audio(self, audio):
        self.audios.append(audio)

    def audio_args(self):
        if len(self.audios)>1:
            raise NotImplementedError('Multiple audio streams are not supported yet')

        if self.audios:
            return self.audios[0].args()
        else:
            return []

    def video_args(self):
        if len(self.videos)>1:
            raise NotImplementedError('Multiple video streams are not supported yet')

        if self.videos:
            return self.videos[0].args()
        else:
            return []


class Video(Medium):
    def __init__(self, profile, pix_fmt=None, **kw):
        super(Video, self).__init__(**kw)

        self.profile = profile
        self.pix_fmt = pix_fmt
        self.stream = 0

    def _metadata_argname(self):
        return '-metadata:s:v:%s' % self.stream

    def args(self):
        args = super(Video, self).args()
        if self.pix_fmt:
            args.append('-pix_fmt')
            args.append(self.pix_fmt)
        return args


class Audio(Medium):
    def __init__(self, profile, **kw):
        super(Audio, self).__init__(**kw)

        self.profile = profile
        self.stream = 0

    def _metadata_argname(self):
        return '-metadata:s:a:%s' % self.stream


CONTAINERS = {
        'mov': {
            'fileext': 'MOV',
            'ffmpeg_args': [
                ('-f', 'mov'),
            ],
            },
        'mxf': {
            'fileext': 'MXF',
            'ffmpeg_args': [
                ('-f','mxf'),
            ],
            },
        }


def video_factory(profile, pix_fmt=None, meta=None):

    try:
        profile_args = registry.get_ffmpeg_args(profile, 'video')
    except KeyError:
        raise KeyError('Profile is not defined: `%s:%s`' % profile)

    return Video(profile=profile, pix_fmt=pix_fmt,
            meta=meta, ffmpeg_args=profile_args)


def audio_factory(profile, meta=None):

    try:
        profile_args = registry.get_ffmpeg_args(profile, 'audio')
    except KeyError:
        raise KeyError('Profile is not defined: `%s:%s`' % profile)

    return Audio(
            profile=profile, meta=meta, ffmpeg_args=profile_args)


def container_factory(profile_name, meta=None):
    profile = registry.get(profile_name)
    try:
        args = CONTAINERS[profile.container]
    except KeyError:
        raise KeyError('Profile `%s` has no container defined' % profile)

    return Container(**args)



def execute(infile, output, profile, deshake=None, meta=None,
        timecode=None, force_overwrite=False, export_dir=None,
        rename=False, pix_fmt=None):

    import renamer

    c = container_factory(profile_name=profile)
    v = video_factory(profile=profile, pix_fmt=pix_fmt)
    a = audio_factory(profile=profile)

    c.add_audio(a)
    c.add_video(v)

    if timecode is not None:
        tc = timecode
    else:
        try:
            tc = timecode_mod.read_timecode_from_database(infile)
        except timecode_mod.NoTimecodeFound:
            tc = timecode_mod.extract_timecode(infile)

    if tc:
        c.add_args('-timecode', tc)

    if force_overwrite:
        c.add_args('-y')

    if meta:
        metahandler = metadatahandler_factory(profile)
        metahandler.set_tags(c, dict(meta))

    if rename:
        outfile = renamer.prettify_filename(infile)
    else:
        outfile = infile

    base,ext = os.path.splitext(outfile)

    if not os.path.exists(output):
        os.makedirs(output)
    base = os.path.join(output, os.path.basename(base))
    outfile = u'%s.%s' % (base, c.fileext)

    print(80*'-')
    print('Transcoding %s' % infile)
    print('  to %s' % outfile)
    print('  using REEL=%s, TIMECODE=%s, PROFILE=%s' % (
        meta.get('reel') or '(not set)',
        tc or '(not set)',
        profile))

    if os.path.exists(outfile) and not force_overwrite:
        answer = raw_input('File exists. Overwrite? (y/N)')
        if not answer.lower()=='y':
            return

    execute_ffmpeg(infile, c, outfile)

