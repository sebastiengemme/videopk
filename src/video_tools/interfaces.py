from zope import interface
from typing import Sequence
from .types import Codec
from asyncio import Future

class ICodecs(interface.Interface):

    def list_codecs() -> Sequence[Codec]:
        """
        """

class ITranscoder(interface.Interface):

    def transcode(input_file: str, output_file: str) -> Future
        """
        """
