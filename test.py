from pymhash import ImageHash, OrientationHash, PymHash

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