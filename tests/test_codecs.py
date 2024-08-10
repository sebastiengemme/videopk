import unittest

from video_tools.types import CodecType,  Codec
from video_tools.ffmpeg import *

class CodecsTestCase(unittest.TestCase):

    def test_list_codecs(self):
        codecs = Codecs.instance().list_codecs()

        self.assertTrue(len(codecs) > 0)

        # Find the hevc codec
        hevc = [x for x in codecs if x.name == "hevc"]

        self.assertTrue(len(hevc) == 1)

    def test_parse_line(self):

        hevc = Codecs.parse_codec_line(" DEV.L. hevc                 H.265 / HEVC (High Efficiency Video Coding) (decoders: hevc hevc_v4l2m2m hevc_cuvid) (encoders: hevc_nvenc hevc_v4l2m2m)")
        
        self.assertTrue(hevc.encoding)
        self.assertEqual(hevc.type, CodecType.VIDEO)
        self.assertTrue(hevc.lossy)
        self.assertFalse(hevc.lossless)
        self.assertFalse(hevc.intra_frame_only)
        self.assertEqual(hevc.name, "hevc")
        self.assertEqual(hevc.description, "H.265 / HEVC (High Efficiency Video Coding) (decoders: hevc hevc_v4l2m2m hevc_cuvid) (encoders: hevc_nvenc hevc_v4l2m2m)")

        hevc = Codecs.parse_codec_line("DEV.L. hevc                 H.265 / HEVC (High Efficiency Video Coding) (decoders: hevc hevc_v4l2m2m hevc_cuvid) (encoders: hevc_nvenc hevc_v4l2m2m)")
        self.assertTrue(hevc.encoding)
        self.assertEqual(hevc.type, CodecType.VIDEO)
        self.assertTrue(hevc.lossy)
        self.assertFalse(hevc.lossless)
        self.assertFalse(hevc.intra_frame_only)
        self.assertEqual(hevc.name, "hevc")
        self.assertEqual(hevc.description, "H.265 / HEVC (High Efficiency Video Coding) (decoders: hevc hevc_v4l2m2m hevc_cuvid) (encoders: hevc_nvenc hevc_v4l2m2m)")

        with self.assertRaises(TypeError):
            hevc = Codecs.parse_codec_line("test 2")
       
    def test_codec(self):
        codec = Codec()
        self.assertFalse(codec.decoding)
        self.assertFalse(codec.encoding)
        self.assertFalse(codec.intra_frame_only)
        self.assertEqual(codec.type, CodecType.VIDEO)
        self.assertFalse(codec.lossy)
        self.assertFalse(codec.lossless)
        self.assertEqual(codec.name,"")
        self.assertEqual(codec.description,"")

        codec.name = "test"
        self.assertEqual(codec.name,"test")

        codec.description = "un test"
        self.assertEqual(codec.description,"un test")

        codec.type = CodecType.AUDIO
        self.assertEqual(codec.type, CodecType.AUDIO)

        codec.type = CodecType.SUBTITLE
        self.assertEqual(codec.type, CodecType.SUBTITLE)

        codec.type = CodecType.DATA
        self.assertEqual(codec.type, CodecType.DATA)

        codec = Codec()
        codec.decoding = True
        self.assertTrue(codec.decoding)

        codec = Codec()
        codec.encoding = True
        self.assertTrue(codec.encoding)

        codec.intra_frame_only = True
        self.assertTrue(codec.intra_frame_only)

        codec = Codec()
        codec.lossy = True
        self.assertTrue(codec.lossy)

        codec = Codec()
        codec.lossless = True
        self.assertTrue(codec.lossless)

if __name__ == "__main__":
    unittest.main()
