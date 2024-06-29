import os
import cv2
import exifread
import traceback
import numpy as np
from pathlib import Path
from scipy import fftpack
from dataclasses import dataclass, fields
from . import ImageHash, OrientationHash
from typing import TypeVar, Union, Generic, BinaryIO, overload

PathLike = TypeVar("PathLike", str, Path)

@dataclass
class Metadata:
    width: int
    height: int
    channels: int
    hash: ImageHash

@dataclass
class ImageBufferMetadata(Metadata):
    exiftags: dict

@dataclass
class ImageFileMetadata(ImageBufferMetadata):
    size: int
    extension: str
    filename: str
    filepath: str

T = TypeVar("T", bound=Metadata)

def get_image_hash(image: cv2.typing.MatLike, hash_size: int, highfreq_factor: int) -> ImageHash: # type: ignore
    img_size = hash_size * highfreq_factor

    sample = cv2.resize(image, (img_size, img_size))
    sample = cv2.cvtColor(sample, cv2.COLOR_BGR2GRAY)

    image_hash = ImageHash() # type: ignore

    for _ in range(4):

        dct = fftpack.dct(fftpack.dct(np.asarray(sample), axis=0), axis=1)

        dctlowfreq = dct[:hash_size, :hash_size]

        med = np.median(dctlowfreq)
        
        diff = dctlowfreq > med

        image_hash.add_hash(OrientationHash(diff.tolist()))

        sample = cv2.rotate(sample, cv2.ROTATE_90_CLOCKWISE)
    
    return image_hash

def _get_exiftags(buffer: BinaryIO):
    exif_tags = {}
    try:
        for tag, value in exifread.process_file(buffer).items():
            exif_tags[tag] = value
    except:
        # TODO: Decide on what to do in exiftags parsing failure. Currently doing nothing
        print(traceback.format_exc())
    return exif_tags

def _metadata_from_image_buffer(buffer: BinaryIO, hash_size: int, highfreq_factor: int):
    file_bytes = np.asarray(bytearray(buffer.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    buffer.seek(0)
    return ImageBufferMetadata(
        width=image.shape[0],
        height=image.shape[1],
        channels=image.shape[2],
        exiftags=_get_exiftags(buffer),
        hash=get_image_hash(image, hash_size=hash_size, highfreq_factor=highfreq_factor)
    )

def _metadata_from_image_path(path: Union[str, Path], hash_size: int, highfreq_factor: int):
    if not os.path.exists(path) or not os.path.isfile(path):
        raise ValueError(f"No file at {path=}")
    filename, extension = os.path.splitext(path)
    _, filename = os.path.split(filename)
    with open(path, "rb") as f:
        buffer_meta = _metadata_from_image_buffer(f, hash_size=hash_size, highfreq_factor=highfreq_factor)
        return ImageFileMetadata(
            width=buffer_meta.width,
            height=buffer_meta.height,
            channels=buffer_meta.channels,
            size=os.path.getsize(path),
            extension=extension,
            filename=filename,
            filepath=str(path),
            exiftags=buffer_meta.exiftags,
            hash=buffer_meta.hash
        )

class PymHash(Generic[T]):
    def __init__(self, metadata: T) -> None:
        self.metadata = metadata
    
    @overload
    @classmethod
    def from_image(cls, image: PathLike, hash_size: int =  ..., highfreq_factor: int =  ...) -> 'PymHash[ImageFileMetadata]': ...

    @overload
    @classmethod
    def from_image(cls, image: BinaryIO, hash_size: int =  ..., highfreq_factor: int =  ...) -> 'PymHash[ImageBufferMetadata]': ...

    @overload
    @classmethod
    def from_image(cls, image: cv2.typing.MatLike, hash_size: int = ..., highfreq_factor: int = ...) -> 'PymHash[Metadata]': ...

    @classmethod
    def from_image(cls, image: Union[PathLike, BinaryIO, cv2.typing.MatLike], hash_size: int = 8, highfreq_factor: int = 4):
        if isinstance(image, (str, Path)):
            return cls(_metadata_from_image_path(image, hash_size=hash_size, highfreq_factor=highfreq_factor))
        elif isinstance(cls, BinaryIO):
            return cls(_metadata_from_image_buffer(image, hash_size=hash_size, highfreq_factor=highfreq_factor))
        elif type(image) == cv2.typing.MatLike:
            return cls(Metadata(
                width=image.size[0],
                height=image.size[1],
                channels=image.size[2],
                hash=get_image_hash(image, hash_size=hash_size, highfreq_factor=highfreq_factor)
            ))
        else:
            raise ValueError("Invalid image")
    
    def __eq__(self, other: 'PymHash[Metadata]'):
        if not isinstance(other, PymHash):
            return False
        return self.metadata.hash == other.metadata.hash
    
    def similar(self, other: 'PymHash[Metadata]', threshold: float = 0.01):
        return (self.metadata.hash - other.metadata.hash) <= threshold

    def to_dict(self):
        dictionary = {}
        for field in fields(self.metadata):
            value = getattr(self.metadata, field.name)
            if isinstance(value, ImageHash):
                dictionary.update({field.name: value.to_str()})
            else:
                dictionary.update({field.name: value})
        return dictionary
    
    @staticmethod
    def asdict(data):
        if isinstance(data, PymHash):
            return data.to_dict()
        else:
            return data