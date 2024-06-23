use std::hash::Hasher;
use std::{cmp, hash::{self, Hash}, ops};
use std::collections::hash_map::DefaultHasher;

use pyo3::PyTypeInfo;
use pyo3::{pyclass, pymethods, types::PyType, Bound, PyResult};

use super::orientation::OrientationHash;

// static VERSION: u8 = 0x0001;

#[pyclass]
#[derive(Clone)]
pub struct ImageHash {
    pub hashes: Vec<OrientationHash>,
}

impl ops::Sub<ImageHash> for ImageHash {
    type Output = i32;

    fn sub(self, rhs: ImageHash) -> Self::Output {
        let mut min_value = i32::MAX;
        for lhs_hash in self.hashes {
            for rhs_hash in rhs.hashes.clone() {
                let val = (lhs_hash.clone() - rhs_hash).unwrap();
                if val < min_value {
                    min_value = val;
                }
            }
        }
        if min_value == i32::MAX {
            panic!("No hashes to subtract");
        }
        return min_value;
    }
}

impl cmp::PartialEq for ImageHash {
    fn eq(&self, other: &Self) -> bool {
        for lhs_hash in self.hashes.clone() {
            for rhs_hash in other.hashes.clone() {
                if lhs_hash == rhs_hash {
                    return true;
                }
            }
        }
        return false;
    }
}

impl hash::Hash for ImageHash {
    fn hash<H: hash::Hasher>(&self, state: &mut H) {
        self.unique_hash().hash(state);
    }

    fn hash_slice<H: hash::Hasher>(data: &[Self], state: &mut H)
    where
        Self: Sized,
    {
        for piece in data {
            piece.hash(state)
        }
    }
}

#[pymethods]
impl ImageHash {

    #[classattr]
    const VERSION: u8 = 0x0001;

    #[new]
    pub fn new() -> Self {
        ImageHash { hashes: Vec::new() }
    }

    pub fn add_hash(&mut self, hash: OrientationHash) {
        if self.hashes.len() > 0 && self.hashes[0].hash_size() != hash.hash_size() {
            panic!(
                "Cannot add different length hashes to same image hash Expecting {x}, Recieved {y}",
                x = self.hashes[0].hash_size(),
                y = hash.hash_size()
            );
        }
        self.hashes.push(hash);
    }

    pub fn to_str(&self) -> String {
        let mut hash = String::from(format!("{:#06x}", ImageHash::VERSION));
        let mut length_set = false;
        for individual_hash in self.hashes.iter().map(|h| h.to_str()) {
            if !length_set {
                hash.push_str(&format!("{:#06x}", individual_hash.len()));
                length_set = true;
            }
            hash.push_str(&individual_hash);
        }
        return hash;
    }

    #[classmethod]
    pub fn from_str(cls: &Bound<'_, PyType>, hash_str: &str) -> Self {
        let mut hashes: Vec<OrientationHash> = Vec::new();
        let version = u8::from_str_radix(&hash_str[0..6], 16).unwrap();
        if version != ImageHash::VERSION {
            panic!("Incorrect version");
        }
        let individual_hash_str_length = usize::from_str_radix(&hash_str[6..12], 16).unwrap();
        for index in (12..=hash_str.len() - 1).step_by(individual_hash_str_length) {
            hashes.push(OrientationHash::from_str(&OrientationHash::type_object_bound(cls.py()), &hash_str[index..index + individual_hash_str_length]))
        }
        return ImageHash { hashes };
    }

    pub fn unique_hash(&self) -> i32 {
        let mut computed_hash = 0;
        for item in self.hashes.iter().map(|h| h.unique_hash()).enumerate() {
            let (index, value) = item;
            computed_hash += value * i32::pow(2, (index % 4).try_into().unwrap());
        }
        return computed_hash;
    }

    fn __eq__(&self, other: &Self) -> PyResult<bool> {
        for lhs in self.hashes.iter() {
            for rhs in other.hashes.iter() {
                if lhs == rhs {
                    return Ok(true);
                }
            }
        }
        return Ok(false);
    }

    fn __str__(&self) -> String {
        return self.to_str();
    }

    fn __hash__(&self) -> u64 {
        let mut hasher = DefaultHasher::new();
        self.hash(&mut hasher);
        hasher.finish()
    }

}
