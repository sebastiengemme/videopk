import asyncio

from videopk.ffmpeg import Transcoder


async def main():
    transcoder = Transcoder()

    # Try using the gpu for encoding, will throw an exception if no gpu codec is found
    # Currently, this will throw an FFmpegUnsupportedCodec exception.
    transcoder.parameters.try_gpu = True

    # Will compute the nominal bitrate using average framerate of the file and its resolution
    transcoder.parameters.auto_bitrate = True

    # Output file will be in H.265 (HEVC) format
    await transcoder.transcode("input.mp4", "output.mp4")


if __name__ == "__main__":
    asyncio.run(main())
