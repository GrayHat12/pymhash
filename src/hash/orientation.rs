use pyo3::pyclass;
use pyo3::pymethods;
use pyo3::types::PyType;
use pyo3::Bound;
use pyo3::PyResult;

use crate::utils::bin_to_hex;
use crate::utils::hex_char_to_bin;
use std::hash::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::ops::Sub;
use std::{cmp, hash, ops};

#[pyclass]
#[derive(Clone)]
pub struct OrientationHash {
    pub hash: Vec<Vec<bool>>,
}

impl ops::Sub<OrientationHash> for OrientationHash {
    type Output = Result<i32, &'static str>;

    fn sub(self, rhs: OrientationHash) -> Self::Output {
        if self.hash.len() != rhs.hash.len() {
            Err("hash length should be same for both operands")
        } else {
            let mut fallacies = 0;
            for item in self.hash.iter().flatten().zip(rhs.hash.iter().flatten()) {
                let (lhs, rhs) = item;
                fallacies += match lhs == rhs {
                    false => 1,
                    _ => 0,
                };
            }
            Ok(fallacies)
        }
    }
}

impl cmp::PartialEq<OrientationHash> for OrientationHash {
    fn eq(&self, other: &OrientationHash) -> bool {
        if self.hash.len() != other.hash.len() {
            false
        } else {
            let mut fallacies = 0;
            for item in self.hash.iter().flatten().zip(other.hash.iter().flatten()) {
                let (lhs, rhs) = item;
                fallacies += match lhs == rhs {
                    false => 1,
                    _ => 0,
                };
            }
            fallacies == 0
        }
    }
}

impl hash::Hash for OrientationHash {
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
impl OrientationHash {

    #[new]
    pub fn new(hash_value: Vec<Vec<bool>>) -> Self {
        return OrientationHash {hash: hash_value};
    }

    fn __str__(&self) -> String {
        return self.to_str();
    }

    fn __hash__(&self) -> u64 {
        let mut hasher = DefaultHasher::new();
        self.hash(&mut hasher);
        hasher.finish()
    }

    fn __eq__(&self, other: &Self) -> PyResult<bool> {
        let diff = OrientationHash::sub(<OrientationHash as Clone>::clone(&*self), other.clone());
        return Ok(diff.unwrap() == 0);
    }

    #[classmethod]
    pub fn from_str(_cls: &Bound<'_, PyType>, hash_str: &str) -> Self {
        let hash_size = ((hash_str.len() as f32) * 4.0).sqrt() as i32;
        let mut hash_vector: Vec<Vec<bool>> = Vec::new();
        let mut hash_index = 0;
        for _ in 0..=hash_size - 1 {
            let mut row_vector: Vec<bool> = Vec::new();
            while (row_vector.len() as i32) < hash_size && hash_index < hash_str.len() {
                let char = hash_str.chars().nth(hash_index).unwrap();
                hash_index += 1;
                row_vector.append(&mut hex_char_to_bin(char));
            }
            hash_vector.push(row_vector);
        }
        OrientationHash { hash: hash_vector }
    }

    pub fn to_str(&self) -> String {
        return bin_to_hex(self.hash.iter().flatten().map(|bin| *bin).collect());
    }

    pub fn hash_size(&self) -> i32 {
        let mut count = 0;
        for _ in self.hash.iter().flatten() {
            count += 1;
        }
        return count;
    }

    pub fn unique_hash(&self) -> i32 {
        let mut computed_hash = 0;
        for item in self.hash.iter().flatten().enumerate() {
            let (index, value) = item;
            if *value {
                computed_hash += i32::pow(2, (index % 8).try_into().unwrap());
            };
        }
        return computed_hash;
    }
}
