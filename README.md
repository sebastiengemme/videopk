# Video Pocket Knife (videopk)

A collection of helper functions for processing videos. Currently, only transcoding is supported.

The initial use case was reducing the size of the videos acquired using a cell phone which normally have an overkill bitrate. This was driven by the need to save space on my Google Photos account.

Currently only one tool is available ```video-transcode```, please type ```video-transcode --help``` for details. The resulting transcoded file will contain all the metadata of the initial file including the rotation. The resulting file is in ```mp4``` file format where the video stream is encoded using [High Efficiency Video Coding (HEVC), also known as H.265](https://fr.wikipedia.org/wiki/H.265).

## Installation

```bash
pip install videopk
```

The code relies on [FFmpeg](https://www.ffmpeg.org/) to perform the conversion. Make sure ```ffmpeg``` is installed and in your path. This code has not been tested on windows, only under Linux.

* For gpu support, make sure to install [FFmpeg NVIDIA GPU Hardware Acceleation](https://docs.nvidia.com/video-technologies/video-codec-sdk/11.1/ffmpeg-with-nvidia-gpu/index.html). 
* Also make sure the ```ffmpeg``` installation has ```libx265``` support if you want to perform software encoding.

## How to use

To transcode a video file, use ```video-transcode```:
```
usage: video transcoding [-h] [-v] [-n] [--version] [-b BITRATE] input_file output_dir

positional arguments:
  input_file            Input file
  output_dir            Outout directory

options:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose output
  -n, --no_gpu          Do not use gpu
  --version             show program's version number and exit
  -b BITRATE, --bitrate BITRATE
                        Bitrate, in bps, if not specified, nominal bitrate is calculated (preferred option)
```

To transcode a file using nominal bitrate. Note that the nominal bitrate is conservately high, suitable for scenes that are noisy such as scenes that contain trees, clouds and bushes. This bitrate has been determined using [this calculator](https://www.dr-lex.be/info-stuff/videocalc.html).

```bash
video-transcode input.mp4 output_dir
```

The resulting file will be located under ```output_dir/input.mp4```. 

## API Usage

Sample. Currenty, the API is meant to be asynchronous, synchronous version of the API will be added in the future.

```python
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
```
