import os
import subprocess


def execute_ffmpeg(infile, container, outfile, ffmpeg='ffmpeg'):
    args = [
            '-hide_banner',
            '-i', infile,
            '-loglevel', 'quiet',
            ]
    args += container.video_args()
    args += container.audio_args()
    args += container.args()
    args += [outfile]

    p = subprocess.Popen(
            [ffmpeg]+args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return p.communicate()


