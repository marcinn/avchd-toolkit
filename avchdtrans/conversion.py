import os
import sys

from .profiles import registry
from .ffmpeg import execute_ffmpeg
from .metadata import metadatahandler_factory
from .timecode import extract_timecode


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
    def __init__(self, profile, quality, pix_fmt=None, **kw):
        super(Video, self).__init__(**kw)

        self.profile = profile
        self.quality = quality
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
    def __init__(self, profile, quality, **kw):
        super(Audio, self).__init__(**kw)

        self.profile = profile
        self.quality = quality
        self.stream = 0

    def _metadata_argname(self):
        return '-metadata:s:a:%s' % self.stream


CONTAINERS = {
        'prores': {
            'fileext': 'MOV',
            'ffmpeg_args': [
                ('-f', 'mov'),
            ],
            },
        'mpeg': {
            'fileext': 'MXF',
            'ffmpeg_args': [
                ('-f','mxf'),
            ],
            },
        'dnxhd': {
            'fileext': 'MXF',
            'ffmpeg_args': [
                ('-f','mxf'),
            ],
        }
    }


def video_factory(profile, quality='high', pix_fmt=None, meta=None):

    try:
        profile_args = registry.get_ffmpeg_args(profile, quality, 'video')
    except KeyError:
        raise KeyError('Unsupported profile/quality pair: `%s:%s`' % (profile, quality))

    return Video(profile=profile, quality=quality, pix_fmt=pix_fmt,
            meta=meta, ffmpeg_args=profile_args)


def audio_factory(profile, quality='high', meta=None):

    try:
        profile_args = registry.get_ffmpeg_args(profile, quality, 'audio')
    except KeyError:
        raise KeyError('Unsupported profile/quality pair: `%s:%s`' % (profile, quality))

    return Audio(
            profile=profile, quality=quality, meta=meta, ffmpeg_args=profile_args)


def container_factory(profile, meta=None):
    try:
        args = CONTAINERS[profile]
    except KeyError:
        raise KeyError('Profile `%s` has no container defined' % profile)

    return Container(**args)



def execute(infile, profile, quality, deshake=None, pix_fmt=None, meta=None,
        timecode=None, outfile=None, force_overwrite=False, export_dir=None,
        rename=False):

    import avchdrenamer

    c = container_factory(profile=profile)
    v = video_factory(profile=profile, quality=quality, pix_fmt=pix_fmt)
    a = audio_factory(profile=profile, quality=quality)

    c.add_audio(a)
    c.add_video(v)

    if timecode is not None:
        tc = timecode
    else:
        sys.stdout.write('Extracting timecode data from "%s"\n' % infile)
        sys.stdout.flush()
        tc = extract_timecode(infile)

    if tc:
        c.add_args('-timecode', tc)

    if force_overwrite:
        c.add_args('-y')

    if meta:
        metahandler = metadatahandler_factory(profile)
        metahandler.set_tags(c, dict(meta))

    if not outfile:
        if rename:
            outfile = avchdrenamer.fix_name(infile)
        else:
            outfile = infile

        base,ext = os.path.splitext(outfile)

        if export_dir:
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            base = os.path.join(export_dir, os.path.basename(base))
        outfile = u'%s.%s' % (base, c.fileext)

    sys.stdout.write('Transcoding "%s"->"%s" using %s@%s\n' % (infile, outfile, profile, quality))
    sys.stdout.flush()
    execute_ffmpeg(infile, c, outfile)
    sys.stdout.write('Finished transcoding "%s"\n' % infile)
    sys.stdout.flush()

