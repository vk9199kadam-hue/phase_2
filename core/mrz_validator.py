"""
ICAO Doc 9303 Machine Readable Zone (MRZ) Checksum Validator
Uses repeating weights [7, 3, 1] Modulo 10.
"""

WEIGHTS = [7, 3, 1]

def mrz_char_value(c: str) -> int:
    if c.isdigit():
        return int(c)
    if 'A' <= c.upper() <= 'Z':
        return ord(c.upper()) - ord('A') + 10
    if c == '<':
        return 0
    return 0

def calculate_mrz_check_digit(data_str: str) -> int:
    total = 0
    for idx, char in enumerate(data_str):
        val = mrz_char_value(char)
        weight = WEIGHTS[idx % 3]
        total += val * weight
    return total % 10

def validate_mrz_field(data_str: str, check_digit_char: str) -> bool:
    if not check_digit_char.isdigit():
        return False
    expected = calculate_mrz_check_digit(data_str)
    return int(check_digit_char) == expected

def parse_and_validate_td3_mrz(line1: str, line2: str) -> dict:
    """
    Parses and checks standard 2-line 44-character TD3 Passport MRZ.
    """
    line1 = line1.strip().upper().ljust(44, '<')[:44]
    line2 = line2.strip().upper().ljust(44, '<')[:44]
    
    if len(line1) != 44 or len(line2) != 44:
        return {
            "valid": False,
            "error": f"Invalid line lengths (Line1: {len(line1)}, Line2: {len(line2)})",
            "passport_number": "",
            "nationality": "",
            "dob": "",
            "expiry": "",
            "overall_valid": False
        }
        
    doc_type = line1[0:2]
    issuing_country = line1[2:5]
    names = line1[5:].split("<<")
    surname = names[0].replace("<", " ").strip()
    given_names = names[1].replace("<", " ").strip() if len(names) > 1 else ""
    
    doc_num = line2[0:9]
    doc_num_cd = line2[9]
    doc_num_valid = validate_mrz_field(doc_num, doc_num_cd)
    
    nationality = line2[10:13]
    dob = line2[13:19]
    dob_cd = line2[19]
    dob_valid = validate_mrz_field(dob, dob_cd)
    
    gender = line2[20]
    expiry = line2[21:27]
    expiry_cd = line2[27]
    expiry_valid = validate_mrz_field(expiry, expiry_cd)
    
    overall_valid = doc_num_valid and dob_valid and expiry_valid
    
    return {
        "valid": True,
        "doc_type": doc_type,
        "issuing_country": issuing_country,
        "surname": surname,
        "given_names": given_names,
        "full_name": f"{given_names} {surname}".strip(),
        "passport_number": doc_num.replace("<", ""),
        "passport_num_checksum_valid": doc_num_valid,
        "nationality": nationality,
        "dob": dob,
        "dob_checksum_valid": dob_valid,
        "gender": gender,
        "expiry": expiry,
        "expiry_checksum_valid": expiry_valid,
        "overall_valid": overall_valid
    }
