
from .interfaces import ITranscoder, ICodecs
import asyncio
import sys
import tempfile
import json
import subprocess
import logging
from asyncio import Future
import shlex
import os
import re
from ffmpeg import FFmpeg

from typing import Dict, Final, Sequence
from .types import Codec, CodecType, TranscodingParameters

def ffprobe(input_file: str) -> Dict:
    ffprobe_args = "-v quiet -show_format -show_streams -print_format json".split()

    ffprobe_exec = "ffprobe"

    result = subprocess.run(
        [ffprobe_exec] + ffprobe_args + [input_file], stdout=subprocess.PIPE)    

    return json.loads(result.stdout)

class Codecs(ICodecs):
    """
    Used to list codecs installed on the platform
    """

    DECODING_POS: Final[int] = 0
    ENCODING_POS: Final[int] = 1
    # Type pos is V, A, S, D
    TYPE_POS: Final[int] = 2
    INTRA_FRAME_POS: Final[int] = 3
    LOSSY_POS: Final[int] = 4
    LOSSLESS_POS: Final[int] = 5

    CAP_FIELD: Final[int] = 1
    NAME_FIELD: Final[int] = 2
    DESC_FIELD: Final[int] = 3

    _instance = None

    def __init__(self):
        raise RuntimeError("Call instance() instead")

    @classmethod
    def instance(cls: type["Codecs"]) -> "Codecs":
        if cls._instance is None:
            cls._instance = cls.__new__(cls)

        return cls._instance


    @staticmethod
    def parse_codec_line(line: str) -> Codec:
        fields = re.search("([^\\s]+)\\s([^\\s]+)\\s*(.+)",line.lstrip().rstrip())

        if fields:

            codec = Codec()

            codec.name = fields[Codecs.NAME_FIELD]
            codec.description = fields[Codecs.DESC_FIELD]

            # Parse the capabilities lines
            if fields[Codecs.CAP_FIELD][Codecs.DECODING_POS] == "D":
                codec.decoding = True

            if fields[Codecs.CAP_FIELD][Codecs.ENCODING_POS] == "E":
                codec.encoding = True

            if fields[Codecs.CAP_FIELD][Codecs.TYPE_POS] == "V":
                codec.type = CodecType.VIDEO
            elif fields[Codecs.CAP_FIELD][Codecs.TYPE_POS] == "A":
                codec.type = CodecType.AUDIO
            elif fields[Codecs.CAP_FIELD][Codecs.TYPE_POS] == "S":
                codec.type = CodecType.SUBTITLE
            elif fields[Codecs.CAP_FIELD][Codecs.TYPE_POS] == "D":
                codec.type = CodecType.DATA
            elif fields[Codecs.CAP_FIELD][Codecs.TYPE_POS] == "T":
                codec.type = CodecType.ATTACHMENT

            if fields[Codecs.CAP_FIELD][Codecs.INTRA_FRAME_POS] == "I":
                codec.intra_frame_only = True

            if fields[Codecs.CAP_FIELD][Codecs.LOSSY_POS] == "L":
                codec.lossy = True

            if fields[Codecs.CAP_FIELD][Codecs.LOSSLESS_POS] == "S":
                codec.lossless = True

            return codec
        else:
            raise TypeError("invalid line")

    def list_codecs(self) -> Sequence[Codec]:
        """Lists the codecs installed

        :returns: a list of installed codecs
        :raises CalledProcessError if something goes wrong
         """
        result = subprocess.run(["ffmpeg", "-codecs"], capture_output=True, check=True)

        codecs = []

        for line in result.stdout.decode("utf-8").split("\n"):
            try:
                codecs.append(Codecs.parse_codec_line(line))
            except:
                pass

        return codecs

class Transcoder(ITranscoder):

    parameters: TranscodingParameters = TranscodingParameters()

    def __init__(self) -> None:
        pass

    def transcode(self, input_file: str, output_file: str) -> Future:
        return asyncio.create_task(self.__do_transcode(input_file, output_file))

    def __apply_rotation(self, input_file: str, output_file: str, info: Dict) -> None:

        if "side_data_list" in info["streams"][0]:
            rotation = info["streams"][0]["side_data_list"][0]["rotation"]

            tmp_output_file = tempfile.NamedTemporaryFile(
                suffix=".mp4", dir=".", delete=False).name

            logging.debug(f"Applying rotation of {rotation} deg")

            ffmpeg_args = "ffmpeg -y -display_rotation {}  -i {} -map_metadata 0 -codec copy {}".format(
                rotation, input_file, tmp_output_file)

            logging.debug("ffmpeg command: {}", ffmpeg_args)

            result = subprocess.run(shlex.split(
                ffmpeg_args), stdout=sys.stdout, stderr=sys.stderr)

            # Rename the file
            os.rename(tmp_output_file, output_file)

    async def __do_transcode(self, input_file: str, output_file: str) -> None:

        # Get the info from the file
        info = ffprobe(input_file)
        stream_info = info["streams"][0]
        format_name = info["format"]["format_name"]

        if ("mp4" in format_name):
            ffmpeg_args = "ffmpeg -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -i '{}' -map_metadata 0 -movflags use_metadata_tags -c:a aac -c:v hevc_nvenc -b:v {}k '{}'"
        else:
            ffmpeg_args = "ffmpeg -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -i '{}' -c:a aac -c:v hevc_nvenc -b:v {}k '{}'"

        h265_bpp = 0.09375

        bitrate = int((stream_info["width"] * stream_info["height"]
                      * eval(stream_info["avg_frame_rate"]) * h265_bpp)/1000)

        ffmpeg_args = ffmpeg_args.format(input_file, bitrate, output_file)

        if 'bit_rate' in stream_info:
            logging.debug(f"original bitrate: {stream_info['bit_rate']}")
        logging.debug(f"bitrate for {stream_info['width']}x{stream_info['height']}@{eval(stream_info['r_frame_rate'])}: {bitrate}kbps")

        logging.debug(f"ffmpeg command: {ffmpeg_args}")

        logging.debug(f"args split: {shlex.split(ffmpeg_args)}")

        result = subprocess.run(shlex.split(ffmpeg_args),
                                stdout=sys.stdout, stderr=sys.stderr)

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to transcode, command used: {ffmpeg_args}, stream info {stream_info}")

        self.__apply_rotation(output_file, output_file, info)


