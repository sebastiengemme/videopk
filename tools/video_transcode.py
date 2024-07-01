#!/usr/bin/env python3

import subprocess
import json
import argparse
import sys
import os.path
import logging
import shlex

from typing import Dict, Sequence, Final
import tempfile

class Codec(object):

    __decoding = False
    __encoding = False
    __video = False
    __audio = False
    __subtitle = False
    __data = False
    __attachment = False
    __intra_frame_only = False
    __lossy = False
    __lossless = False
    __name = ""
    __description = ""

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, value: str) -> None:
        self.__description = value

    @property
    def decoding(self) -> bool:
        return self.__decoding

    @decoding.setter
    def decoding(self, value: bool) -> None:
        self.__decoding = value

    @property
    def encoding(self) -> bool:
        return self.__encoding

    @encoding.setter
    def encoding(self, value: bool) -> None:
        self.__encoding = value

    @property
    def video(self) -> bool:
        return self.__video

    @video.setter
    def video(self, value: bool) -> None:
        self.__video = value

    @property
    def audio(self) -> bool:
        return self.__audio

    @audio.setter
    def audio(self, value: bool) -> None:
        self.__audio = value

    @property
    def subtitle(self) -> bool:
        return self.__subtitle

    @subtitle.setter
    def subtitle(self, value: bool) -> None:
        self.__subtitle = value

    @property
    def data(self) -> bool:
        return self.__data

    @data.setter
    def data(self, value: bool) -> None:
        self.__data = value

    @property
    def attachment(self) -> bool:
        return self.__attachment

    @attachment.setter
    def attachment(self, value: bool) -> None:
        self.__attachment = value

    @property
    def intra_frame_only(self) -> bool:
        return self.__intra_frame_only

    @intra_frame_only.setter
    def intra_frame_only(self, value: bool) -> None:
        self.__intra_frame_only = value

    @property
    def lossy(self) -> bool:
        return self.__lossy

    @lossy.setter
    def lossy(self, value: bool) -> None:
        self.__lossy = value

    @property
    def lossless(self) -> bool:
        return self.__lossless

    @lossless.setter
    def lossless(self, value: bool) -> None:
        self.__lossless = value

class Codecs(object):

    DECODING_POS: Final[int] = 0
    ENCODING_POS: Final[int] = 1
    # Type pos is V, A, S, D
    TYPE_POS: Final[int] = 2
    INTRA_FRAME_POS: Final[int] = 3
    LOSSY_POS: Final[int] = 4
    LOSSLESS_POS: Final[int] = 5

    CAP_FIELD: Final[int] = 0
    NAME_FIELD: Final[int] = 1
    DESC_FIELD: Final[int] = 2

    @staticmethod
    def parse_codec_line(line: str) -> Codec:
        fields = line.split()

        codec = Codec()

        codec.name = fields[Codecs.NAME_FIELD]
        codec.description = fields[Codecs.DESC_FIELD]

        # Parse the capabilities lines
        if line[Codecs.CAP_FIELD][Codecs.DECODING_POS] == "D":
            codec.decoding = True

        if line[Codecs.CAP_FIELD][Codecs.ENCODING_POS] == "E":
            codec.decoding = True

        if line[Codecs.CAP_FIELD][Codecs.CAP_FIELD] == "V":
            codec.video = True
        elif line[Codecs.CAP_FIELD][Codecs.CAP_FIELD] == "A":
            codec.audio = True
        elif line[Codecs.CAP_FIELD][Codecs.CAP_FIELD] == "S":
            codec.subtitle = True
        elif line[Codecs.CAP_FIELD][Codecs.CAP_FIELD] == "D":
            codec.data = True
        elif line[Codecs.CAP_FIELD][Codecs.CAP_FIELD] == "T":
            codec.attachment = True

        if line[Codecs.CAP_FIELD][Codecs.INTRA_FRAME_POS] == "I":
            codec.intra_frame_only = True

        if line[Codecs.CAP_FIELD][Codecs.LOSSY_POS] == "L":
            codec.lossy = True

        if line[Codecs.CAP_FIELD][Codecs.LOSSLESS_POS] == "S":
            codec.lossless = True

        return codec

    @staticmethod
    def list_codecs() -> Sequence[Codec]:
        result = subprocess.run(["ffmpeg", "-codecs"], capture_output=True, check=True)

        codecs = []

        for line in result.stdout.decode("utf-8").split("\n"):
            try:
                codecs.append(Codecs.parse_codec_line(line))
            except:
                pass

        return codecs

def apply_rotation(input_file: str, output_file: str, info: Dict):

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


def transcode(input_file: str, output_file: str) -> None:

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


def ffprobe(input_file: str) -> Dict:
    ffprobe_args = "-v quiet -show_format -show_streams -print_format json".split()

    ffprobe_exec = "ffprobe"

    result = subprocess.run(
        [ffprobe_exec] + ffprobe_args + [input_file], stdout=subprocess.PIPE)    

    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser("video transcoding")
    parser.add_argument("input_file", help="Input file")
    parser.add_argument("output_dir", help="Outout directory")

    args = parser.parse_args()

    info = ffprobe(args.input_file)

    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)

    output_file = os.path.join(args.output_dir, os.path.splitext(
        os.path.basename(args.input_file))[0] + ".mp4")

    logging.debug(f"Output file {output_file}")

    try:
        transcode(args.input_file, output_file)

        logging.debug(info)

        print(
            f'Size: {info["streams"][0]["width"]} x {info["streams"][0]["height"]}')
        print(f'fps: {eval(info["streams"][0]["avg_frame_rate"])}')

        # Apply rotation if needed
        apply_rotation(output_file, output_file, info)

        logging.info(f"Output written to {output_file}")
    except Exception as e:
        logging.critical(f"Failed to run: {e}")


if __name__ == "__main__":
    main()
