import asyncio
import json
import logging
import os
import re
import subprocess
import tempfile
from asyncio import Future
from typing import Dict, Final, Optional, Sequence

from ffmpeg.asyncio import FFmpeg
from ffmpeg.ffmpeg import types

from .constants import H265_BPP
from .interfaces import ICodecs, ITranscoder
from .types import Codec, CodecType, TranscodingParameters


def ffprobe(input_file: str) -> Dict:
    """Runs ffprobe on a file an returns

    :param input_file: the file to probe.

    :return: a dictionary containing the different properties of the file.
    """
    ffprobe_args = "-v quiet -show_format -show_streams -print_format json".split()

    ffprobe_exec = "ffprobe"

    result = subprocess.run(
        [ffprobe_exec] + ffprobe_args + [input_file], stdout=subprocess.PIPE
    )

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
        fields = re.search("([^\\s]+)\\s([^\\s]+)\\s*(.+)", line.lstrip().rstrip())

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

            if codec.decoding:
                # Try to match encoders and decoders
                m = re.search(r"decoders:([^\)]*)\)", line.lstrip().rstrip())

                if m is not None:
                    codec.decoders = m.group(1).split()

            if codec.encoding:
                m = re.search(r"encoders:([^\)]*)\)", line.lstrip().rstrip())

                if m is not None:
                    codec.encoders = m.group(1).split()

            if codec.encoding and len(codec.encoders) == 0:
                codec.encoders.append(codec.name)

            if codec.decoding and len(codec.decoders) == 0:
                codec.decoders.append(codec.name)

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
            except Exception:
                pass

        return codecs


class Transcoder(ITranscoder):
    """The FFmpeg implementation of interface ITranscoder."""

    def __init__(self) -> None:
        self.parameters = TranscodingParameters()

    async def transcode(self, input_file: str, output_file: str) -> None:
        await asyncio.create_task(self.__do_transcode(input_file, output_file))

    async def __apply_rotation(
        self, input_file: str, output_file: str, info: Dict
    ) -> None:
        if "side_data_list" in info["streams"][0]:
            rotation = info["streams"][0]["side_data_list"][0]["rotation"]

            tmp_output_file = tempfile.NamedTemporaryFile(
                suffix=".mp4", dir=".", delete=False
            ).name

            logging.debug(f"Applying rotation of {rotation} deg")

            ffmpeg_cmd = FFmpeg()

            ffmpeg_cmd.option("y").option("display_rotation", rotation).input(
                input_file
            ).output(tmp_output_file, {"map_metadata": 0, "codec": "copy"})

            await ffmpeg_cmd.execute()

            os.rename(tmp_output_file, output_file)

    async def __do_transcode(self, input_file: str, output_file: str) -> None:
        # Get the info from the file
        info = ffprobe(input_file)
        stream_info = info["streams"][0]
        format_name = info["format"]["format_name"]

        ffmpeg_cmd = FFmpeg()

        if self.parameters.auto_bitrate:
            bitrate = int(
                (
                    stream_info["width"]
                    * stream_info["height"]
                    * eval(stream_info["avg_frame_rate"])
                    * H265_BPP
                )
                / 1000
            )
        else:
            bitrate = self.parameters.bitrate // 1000

        # Default output options
        output_options: dict[str, Optional[types.Option]] = {}
        if self.parameters.try_gpu:
            output_options["c:v"] = "hevc_nvenc"
        else:
            output_options["c:v"] = "libx265"
        #            output_options["c:v"] = "libx264"
        #            output_options["profile:v"] = "high"
        #            output_options["level:v"] = 4.0

        logging.debug(f"format name: {format_name}")

        if "mp4" in format_name:
            output_options["map_metadata"] = 0
            output_options["movflags"] = "use_metadata_tags"

        if self.parameters.only_video:
            output_options["an"] = None
        else:
            output_options["c:a"] = "aac"

        output_options["b:v"] = "{}k".format(bitrate)

        logging.debug(f"output_options: {output_options}")

        ffmpeg_cmd.option("y").option("vsync", 0).input(input_file).output(
            output_file, options=output_options
        )

        if self.parameters.try_gpu:
            ffmpeg_cmd.option("hwaccel", "cuda").option("hwaccel_output_format", "cuda")

        await ffmpeg_cmd.execute()

        if "bit_rate" in stream_info:
            logging.debug(f"original bitrate: {stream_info['bit_rate']}")
        logging.debug(
            f"bitrate for {stream_info['width']}x{stream_info['height']}@{eval(stream_info['r_frame_rate'])}: {bitrate}kbps"
        )

        await self.__apply_rotation(output_file, output_file, info)
