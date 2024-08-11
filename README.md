# Video Tools

A collection of helper functions for processing videos. Currently, only transcoding is supported.

The initial use case was reducing the size of the videos acquired using a cell phone which normally have an overkill bitrate. This was driven by the need to save space on my Google Photos account.

Currently only one tool is available ```video-transcode```, please type ```video-transcode --help``` for details.

## Installation

```bash
pip install video-tools
```

Also, make sure ```ffmpeg``` is installed and in your path. For gpu support, make sure to install [FFmpeg NVIDIA GPU Hardware Acceleation](https://docs.nvidia.com/video-technologies/video-codec-sdk/11.1/ffmpeg-with-nvidia-gpu/index.html)

