use pyo3::pyfunction;

pub fn bin_to_dec(arr: &[bool]) -> i32 {
    let mut solution: i32 = 0;
    for item in arr.iter().rev().enumerate() {
        let (index, value) = item;
        if *value {
            solution += i32::pow(2, index.try_into().unwrap());
        }
    }
    return solution;
}

#[pyfunction()]
pub fn bin_to_hex(arr: Vec<bool>) -> String {
    let mut solution = String::new();
    for item in arr.chunks(4) {
        solution.push_str(&format!("{:x}", bin_to_dec(item)));
    }
    return solution;
}

#[pyfunction()]
pub fn hex_char_to_bin(character: char) -> Vec<bool> {
    match character.to_ascii_lowercase() {
        '0' => vec![false, false, false, false],
        '1' => vec![false, false, false, true],
        '2' => vec![false, false, true, false],
        '3' => vec![false, false, true, true],
        '4' => vec![false, true, false, false],
        '5' => vec![false, true, false, true],
        '6' => vec![false, true, true, false],
        '7' => vec![false, true, true, true],
        '8' => vec![true, false, false, false],
        '9' => vec![true, false, false, true],
        'a' => vec![true, false, true, false],
        'b' => vec![true, false, true, true],
        'c' => vec![true, true, false, false],
        'd' => vec![true, true, false, true],
        'e' => vec![true, true, true, false],
        'f' => vec![true, true, true, true],
        _ => panic!("Invalid Hex Char"),
    }
}
