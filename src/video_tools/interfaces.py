from typing import Sequence
from .types import Codec, TranscodingParameters
from asyncio import Future
from typing import Protocol

class ICodecs(Protocol):

    def list_codecs(self) -> Sequence[Codec]:
        """
        """
        ...

class ITranscoder(Protocol):

    parameters: TranscodingParameters

    def transcode(self, input_file: str, output_file: str) -> Future:
        """
        """
        ...
