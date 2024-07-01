import unittest

from video_tools.video_transcode import CodecType, Codecs, Codec

class CodecsTestCase(unittest.TestCase):

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
