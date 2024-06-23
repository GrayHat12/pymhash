from pymhash import ImageHash, OrientationHash

# Will write proper pytests later

a = OrientationHash.from_str("a5b4a3425cd72ccd")

assert isinstance(a, OrientationHash) == True
assert isinstance(a.to_str(), str)
assert isinstance(a.unique_hash(), int)
assert a.to_str() == "a5b4a3425cd72ccd"
assert a.unique_hash() == 997