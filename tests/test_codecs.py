import pytest

from videopk.ffmpeg import *
from videopk.types import Codec, CodecType


def list_codecs():
    codecs = Codecs.instance().list_codecs()

    assert len(codecs) > 0

    # Find the hevc codec
    hevc = [x for x in codecs if x.name == "hevc"]

    assert len(hevc) == 1


def parse_line():
    hevc = Codecs.parse_codec_line(
        " DEV.L. hevc                 H.265 / HEVC (High Efficiency Video Coding) (decoders: hevc hevc_v4l2m2m hevc_cuvid) (encoders: hevc_nvenc hevc_v4l2m2m)"
    )

    assert hevc.encoding
    assert hevc.type == CodecType.VIDEO
    assert hevc.lossy
    assert not hevc.lossless
    assert not hevc.intra_frame_only
    assert hevc.name == "hevc"
    assert (
        hevc.description
        == "H.265 / HEVC (High Efficiency Video Coding) (decoders: hevc hevc_v4l2m2m hevc_cuvid) (encoders: hevc_nvenc hevc_v4l2m2m)"
    )

    hevc = Codecs.parse_codec_line(
        "DEV.L. hevc                 H.265 / HEVC (High Efficiency Video Coding) (decoders: hevc hevc_v4l2m2m hevc_cuvid) (encoders: hevc_nvenc hevc_v4l2m2m)"
    )
    assert hevc.encoding
    assert hevc.type == CodecType.VIDEO
    assert hevc.lossy
    assert not hevc.lossless
    assert not hevc.intra_frame_only
    assert hevc.name == "hevc"
    assert (
        hevc.description
        == "H.265 / HEVC (High Efficiency Video Coding) (decoders: hevc hevc_v4l2m2m hevc_cuvid) (encoders: hevc_nvenc hevc_v4l2m2m)"
    )

    with pytest.raises(TypeError):
        hevc = Codecs.parse_codec_line("test 2")


def codec():
    codec = Codec()
    assert not codec.decoding
    assert not codec.encoding
    assert not codec.intra_frame_only
    assert codec.type == CodecType.VIDEO
    assert not codec.lossy
    assert not codec.lossless
    assert codec.name == ""
    assert codec.description == ""

    codec.name = "test"
    assert codec.name == "test"

    codec.description = "un test"
    assert codec.description == "un test"

    codec.type = CodecType.AUDIO
    assert codec.type == CodecType.AUDIO

    codec.type = CodecType.SUBTITLE
    assert codec.type == CodecType.SUBTITLE

    codec.type = CodecType.DATA
    assert codec.type == CodecType.DATA

    codec = Codec()
    codec.decoding = True
    assert codec.decoding

    codec = Codec()
    codec.encoding = True
    assert codec.encoding

    codec.intra_frame_only = True
    assert codec.intra_frame_only

    codec = Codec()
    codec.lossy = True
    assert codec.lossy

    codec = Codec()
    codec.lossless = True
    assert codec.lossless
