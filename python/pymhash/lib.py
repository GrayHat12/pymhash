"""
Core PyHash Module: Hash your images

Easily hash and compare images
"""

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
    """Dataclass representing base Image metadata"""

    width: int
    """width of the image"""

    height: int
    """height of the image"""

    channels: int
    """channels in the image"""

    hash: ImageHash
    """hash of the image"""

@dataclass
class ImageBufferMetadata(Metadata):
    """Dataclass representing Image metadata for images loaded through a binary stream"""

    exiftags: dict
    """exif tags of the image"""

@dataclass
class ImageFileMetadata(ImageBufferMetadata):
    """Dataclass representing Image metadata for images loaded through filepath"""

    size: int
    """size of the image reported by `os.path.getsize()`"""

    extension: str
    """Image extension"""

    filename: str
    """Image File name"""

    filepath: str
    """Image file path"""

T = TypeVar("T", bound=Metadata)

def get_image_hash(image: cv2.typing.MatLike, hash_size: int, highfreq_factor: int) -> ImageHash: # type: ignore
    """
    Get image hash

    Calculate image hash

    :param image: Matrix Like cv2 image
    :param hash_size: hash size
    :param highfreq_factor: factor to amplify higher frequencies with
    :return: ImageHash
    """

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
    """
    Get exif tags

    Get exiftags from image

    :param buffer: Image buffer
    :return: dictionary containg exiftags
    """
    exif_tags = {}
    try:
        for tag, value in exifread.process_file(buffer).items():
            exif_tags[tag] = value
    except:
        # TODO: Decide on what to do in exiftags parsing failure. Currently doing nothing
        print(traceback.format_exc())
    return exif_tags

def _metadata_from_image_buffer(buffer: BinaryIO, hash_size: int, highfreq_factor: int):
    """
    Metadata from image buffer

    Get ImageBufferMetadata from image buffer

    :param buffer: Image buffer
    :param hash_size: hash size
    :param highfreq_factor: factor to amplify higher frequencies with
    :return: ImageBufferMetadata
    """
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
    """
    Metadata from image filepath

    Get ImageFileMetadata from image path

    :param path: Image path
    :param hash_size: hash size
    :param highfreq_factor: factor to amplify higher frequencies with
    :return: ImageFileMetadata
    """
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
    """Class representing a parsed Image"""

    def __init__(self, metadata: T) -> None:
        """
        :param metadata: metadata that is parsed
        """
        self.metadata = metadata
    
    @overload
    @classmethod
    def from_image(cls, image: PathLike, hash_size: int =  ..., highfreq_factor: int =  ...) -> 'PymHash[ImageFileMetadata]': 
        """
        Instantiate PymHash using an image path
        
        :param image: Image path
        :param hash_size: hash size
        :param highfreq_factor: factor to amplify higher frequencies with
        :return: PymHash[ImageFileMetadata]
        """
        ...

    @overload
    @classmethod
    def from_image(cls, image: BinaryIO, hash_size: int =  ..., highfreq_factor: int =  ...) -> 'PymHash[ImageBufferMetadata]': 
        """
        Instantiate PymHash using an image buffer
        
        :param image: Image buffer
        :param hash_size: hash size
        :param highfreq_factor: factor to amplify higher frequencies with
        :return: PymHash[ImageBufferMetadata]
        """
        ...

    @overload
    @classmethod
    def from_image(cls, image: cv2.typing.MatLike, hash_size: int = ..., highfreq_factor: int = ...) -> 'PymHash[Metadata]': 
        """
        Instantiate PymHash using an image cv2 matrix
        
        :param image: Image matrix
        :param hash_size: hash size
        :param highfreq_factor: factor to amplify higher frequencies with
        :return: PymHash[Metadata]
        """
        ...

    @classmethod
    def from_image(cls, image: Union[PathLike, BinaryIO, cv2.typing.MatLike], hash_size: int = 8, highfreq_factor: int = 4):
        """
        Instantiate PymHash using an image path/buffer/matrix
        
        :param image: Image path/buffer/matrix
        :param hash_size: hash size
        :param highfreq_factor: factor to amplify higher frequencies with
        :return: PymHash
        """
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
        """
        Compare PymHash objects

        Two PymHash objects are equal if their respective ImageHash(es) satisfy equality
        
        :param other: PymHash
        :return: bool
        """
        if not isinstance(other, PymHash):
            return False
        return self.metadata.hash == other.metadata.hash
    
    def similar(self, other: 'PymHash[Metadata]', threshold: float = 0.01):
        """
        Compare PymHash objects

        Two PymHash objects are similar if the difference between their respective ImageHash(es) is less than the provided threshold
        
        :param other: PymHash
        :param threshold: float
        :return: bool
        """
        return (self.metadata.hash - other.metadata.hash) <= threshold

    def to_dict(self):
        """
        Convert PymHash to dict

        :return: serializable json
        """
        dictionary = {}
        for field in fields(self.metadata):
            value = getattr(self.metadata, field.name)
            if isinstance(value, ImageHash):
                dictionary.update({field.name: value.to_str()})
            else:
                dictionary.update({field.name: value})
        return dictionary