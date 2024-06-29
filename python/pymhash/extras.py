"""
Pyhash extras

Extra functionality for Image Comparisons
"""

from typing import Any, Generator, List
from pathlib import Path
from .lib import PymHash, ImageFileMetadata, PathLike

try:
    from tqdm import tqdm # type: ignore
except ImportError:
    tqdm = lambda x: x

IMAGE_EXTENSIONS = ['.bmp', '.dib', '.jpeg', '.jpg', '.jp2', '.png', '.pbm', '.pgm', '.ppm', '.sr', '.ras', '.tiff', '.tif', '.exr', '.jxr', '.pfm', '.pds', '.pfm', '.viff', '.xbm', '.xpm', '.dds', '.eis', '.mng', '.web', '.hei', '.hei', '.av']
"""Common image extensions that can be parsed by cv2"""

def drilldown(targeted_directory: PathLike, extensions: List[str] = IMAGE_EXTENSIONS) -> Generator[str, Any, None]:
    """
    Generator Function

    Yields all valid image paths inside target directory and it's subdirectories

    :param targeted_directory: Path of a root folder
    :param extensions: Acceptable image extensions
    :return: Generator over all valid image paths inside the target and it's subdirectories
    """
    folder_path:Path = Path(targeted_directory)
    if not folder_path.exists():
        raise ValueError(f"Folder path {targeted_directory} does not exist.")
    for file_path in folder_path.glob('**/*'):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            raw_filename = u'{}'.format(file_path)
            yield raw_filename
    return None

def get_duplicates(
        folder_path: str, 
        valid_image_extensions: List[str] = IMAGE_EXTENSIONS, 
        hash_size: int = 8, 
        highfreq_factor: int = 4
    ) -> List[List[PymHash[ImageFileMetadata]]]:
    """
    Find Duplicate Image Groups

    Return all duplicate image groups inside target directory and it's subdirectories

    :param targeted_directory: Path of a root folder
    :param valid_image_extensions: List of valid image extensions to consider
    :param hash_size: hash size
    :param highfreq_factor: factor to amplify higher frequencies with
    :return: Groups of all duplicate PymHash images
    """
    image_paths = drilldown(folder_path, extensions=valid_image_extensions)

    # List of similarity groups
    similarity_groups: List[List[PymHash[ImageFileMetadata]]] = []

    for image_path in tqdm(image_paths):
        metadata = PymHash.from_image(image_path, hash_size=hash_size, highfreq_factor=highfreq_factor)
        
        inserted = False

        for group in similarity_groups:
            for meta in group:
                if meta == metadata:
                    group.append(metadata)
                    inserted = True
                    break
            if inserted:
                break
        
        if not inserted:
            similarity_groups.append([metadata])
    # Return duplicates -> similarity groups where there are more than a single item
    return [group for group in similarity_groups if len(group) > 1]