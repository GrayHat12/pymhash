use hash::{image::ImageHash, orientation::OrientationHash};
use pyo3::prelude::*;
// use utils::{bin_to_hex, hex_char_to_bin};

pub mod hash;
pub mod utils;

/// A Python module implemented in Rust.
#[pymodule]
fn _pymhash(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OrientationHash>()?;
    m.add_class::<ImageHash>()?;
    Ok(())
}
