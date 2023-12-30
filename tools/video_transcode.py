#!/usr/bin/env python3

import subprocess
import json
import argparse
import sys
import os.path
import shlex

from typing import Dict


def transcode(input_file: str, output_file: str):

    # Get the info from the file
    info = ffprobe(input_file)
    stream_info = info["streams"][0]
    format_name = info["format"]["format_name"]
    
    if ( "mp4" in format_name):
        ffmpeg_args = "ffmpeg -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -i '{}' -map_metadata 0 -c:a copy -c:v hevc_nvenc -b:v {}k '{}'"
    else:
        ffmpeg_args = "ffmpeg -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -i '{}' -c:a aac -c:v hevc_nvenc -b:v {}k '{}'"             
        
    h265_bpp=0.09375
    
    bitrate = int((stream_info["width"] * stream_info["height"] * eval(stream_info["r_frame_rate"]) * h265_bpp)/1000)
    
    ffmpeg_args = ffmpeg_args.format(input_file, bitrate, output_file)
    
    # print(f"original bitrate: {stream_info['bit_rate']}")
    # print(f"bitrate for {stream_info['width']}x{stream_info['height']}@{eval(stream_info['r_frame_rate'])}: {bitrate}kbps")    
    
    print(f"ffmpeg command: {ffmpeg_args}")
    
    print(f"args split: {shlex.split(ffmpeg_args)}")
    
    result = subprocess.run(shlex.split(ffmpeg_args), stdout=sys.stdout, stderr=sys.stderr)    
    
def ffprobe(input_file: str) -> Dict:
    ffprobe_args = "-v quiet -show_format -show_streams -print_format json".split()

    ffprobe_exec = "ffprobe"

    result = subprocess.run(
        [ffprobe_exec] + ffprobe_args + [input_file], stdout=subprocess.PIPE)

    # print(f"Return code {result.returncode}")

    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser("video transcoding")
    parser.add_argument("input_file", help="Input file")
    parser.add_argument("output_dir", help="Outout directory")

    args = parser.parse_args()

    info = ffprobe(args.input_file)
    
    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)        
    
    output_file = os.path.join(args.output_dir, os.path.splitext(os.path.basename(args.input_file))[0] + ".mp4")
    
    # print(f"Output file {output_file}")
    
    transcode(args.input_file, output_file)
    
    # print(info)

    print(
        f'Size: {info["streams"][0]["width"]} x {info["streams"][0]["height"]}')
    print(f'fps: {eval(info["streams"][0]["r_frame_rate"])}')
    
    print(f"Output written to {output_file}")


if __name__ == "__main__":
    main()
