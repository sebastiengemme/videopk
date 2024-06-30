#!/usr/bin/env python3

import subprocess
import json
import argparse
import sys
import os.path
import logging
import shlex

from typing import Dict
import tempfile

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
