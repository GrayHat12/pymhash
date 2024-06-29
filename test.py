from pymhash import ImageHash, OrientationHash, PymHash
from pymhash.extras import get_duplicates

# Will write proper pytests later

a = OrientationHash.from_str("a5b4a3425cd72ccd")

p = PymHash.from_image("./docs/pymhash.png")

print(p.metadata)
print(p.metadata.hash.to_str())
print(p.metadata.hash.to_str() == str(ImageHash.from_str(p.metadata.hash.to_str())))
print(p.metadata.hash == ImageHash.from_str(p.metadata.hash.to_str()))
hashes_str = [str(hash) for hash in p.metadata.hash.hashes]
print(hashes_str)

n = ImageHash()
for v in hashes_str:
    n.add_hash(OrientationHash.from_str(v))

print(n == p.metadata.hash)

assert isinstance(a, OrientationHash)
assert isinstance(a.to_str(), str)
assert isinstance(a.unique_hash(), int)
assert a.to_str() == "a5b4a3425cd72ccd"
assert a.unique_hash() == 997

import json

imagea = ImageHash.from_str("0x00010x0010d8daeae9a1b4320ea9a56b92ae5a264d8970bf41f81e6ba4fc0e3e30f16063c7")
imageb = ImageHash.from_str("0x00010x0010dcdaeaeb81b4320aa9a46b92aeda264d8970bf41f81e6ba4fc0e3e20f36073c3")
imagec = ImageHash.from_str("0x00010x0010cfdb22701c8cd7389387640a98dbb7939a7177da4927829ac62d31a4cd71e23d")

print(imagea-imageb, imagea-imagec, imageb-imagec)
print(imageb-imagea, imagec-imagea, imagec-imageb)

# Find all duplicate image groups inside this parent folder
duplicates = get_duplicates("/home/grayhat/desktop/github/PyCompare/_sample_data")

# Convert the duplicate image groups information into a json serializable object
duplicates_dict = [[item.to_dict() for item in group] for group in duplicates]

with open("./duplicates.json", "w+") as f:
    json.dump(duplicates_dict, f, default=str)

from pathlib import Path
import os
import uuid
from pymhash.extras import tqdm

# Create a duplicates folder to copy duplicate images in groups for human verification
for group_index, duplicate_group in tqdm(enumerate(duplicates)):
    for duplicate_item in duplicate_group:
        new_path = Path(f"./duplicates/group-{group_index}")
        new_path.mkdir(parents=True, exist_ok=True)
        with open(duplicate_item.metadata.filepath, "rb") as srcf:
            target_file_path = os.path.join(new_path, f"{duplicate_item.metadata.filename}.{duplicate_item.metadata.extension}")
            if os.path.isfile(target_file_path):
                target_file_path = os.path.join(new_path, f"{duplicate_item.metadata.filename}-{uuid.uuid4().hex}.{duplicate_item.metadata.extension}")
            with open(target_file_path, "wb+") as trgtf:
                trgtf.write(srcf.read())