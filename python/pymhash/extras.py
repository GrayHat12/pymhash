from typing import List
from pathlib import Path
from .lib import PymHash, ImageFileMetadata

try:
    from tqdm import tqdm # type: ignore
except ImportError:
    tqdm = lambda x: x

IMAGE_EXTENSIONS = ['.bmp', '.dib', '.jpeg', '.jpg', '.jp2', '.png', '.pbm', '.pgm', '.ppm', '.sr', '.ras', '.tiff', '.tif', '.exr', '.jxr', '.pfm', '.pds', '.pfm', '.viff', '.xbm', '.xpm', '.dds', '.eis', '.mng', '.web', '.hei', '.hei', '.av']

def drilldown(targeted_directory: str, extensions: List[str] = IMAGE_EXTENSIONS):
    image_files:list[str]= []
    folder_path:Path = Path(targeted_directory)
    if not folder_path.exists():
        raise ValueError(f"Folder path {targeted_directory} does not exist.")
    for file_path in folder_path.glob('**/*'):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            raw_filename = u'{}'.format(file_path)
            image_files.append(raw_filename)
    return image_files

def get_duplicates(folder_path: str):
    image_paths = drilldown(folder_path)

    # List of similarity groups
    similarity_groups: List[List[PymHash[ImageFileMetadata]]] = []

    for image_path in tqdm(image_paths):
        metadata = PymHash.from_image(image_path)
        
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