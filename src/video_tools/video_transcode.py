#!/usr/bin/env python3

import argparse
import os.path
import logging

from .ffmpeg import Transcoder

import asyncio

async def run():
    parser = argparse.ArgumentParser("video transcoding")
    parser.add_argument("input_file", help="Input file")
    parser.add_argument("output_dir", help="Outout directory")

    args = parser.parse_args()

    transcoder = Transcoder()
    try:
        if not os.path.isdir(args.output_dir):
            os.makedirs(args.output_dir)

        output_file = os.path.join(args.output_dir, os.path.splitext(os.path.basename(args.input_file))[0] + ".mp4")

        await transcoder.transcode(args.input_file, output_file)

    except Exception as e:
        logging.critical(f"Failed to run: {e}")


def main():
    asyncio.run(run())

