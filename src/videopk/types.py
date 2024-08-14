from enum import Enum
from typing import MutableSequence


class CodecType(Enum):
    AUDIO = 0
    VIDEO = 1
    SUBTITLE = 2
    ATTACHMENT = 3
    DATA = 4


class TranscodingParameters(object):
    """Transcoding parameter"""

    def __init__(self) -> None:
        self.try_gpu = True
        self.auto_bitrate = True
        self.only_video = False
        self.bitrate = 0
        self.auto_bitrate = True


class Codec(object):
    def __init__(self) -> None:
        self.encoders: MutableSequence[str] = []
        self.decoders: MutableSequence[str] = []
        self.__decoding = False
        self.__encoding = False
        self.__type = CodecType.VIDEO
        self.__intra_frame_only = False
        self.__lossy = False
        self.__lossless = False
        self.__name = ""
        self.__description = ""

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        """
        Sets the name

        :param value: the new value that property name should take
        """
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
    def type(self) -> CodecType:
        return self.__type

    @type.setter
    def type(self, value: CodecType) -> None:
        self.__type = value

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
