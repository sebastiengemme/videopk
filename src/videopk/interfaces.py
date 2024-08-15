from asyncio import Future
from typing import Protocol, Sequence

from .types import Codec, TranscodingParameters


class ICodecs(Protocol):
    """Defines a codec repository where the available codecs can be queried."""

    def list_codecs(self) -> Sequence[Codec]:
        """Lists the codecs available on the platform.

        :raises RuntimeError: if an error occurs while querying the codecs.

        :return: the codecs available on the platform
        """
        ...


class ITranscoder(Protocol):
    """Represents a transcoder, used to convert a video."""

    parameters: TranscodingParameters
    """Transcoding parameters
    """

    async def transcode(self, input_file: str, output_file: str) -> None:
        """Transcodes a file using the specified transcoding parameter. This method is meant to be run asynchronously by
        return a Future object.

        :param input_file: the file to transcode
        :param output_file: the target file.

        :raises RuntimeError: if an error occurs (will have more granular exceptions in the future)

        """
        ...
