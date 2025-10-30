#****************************************************************************
#    Application:   Annerkennung Ai Cockpit
#    Module:        utils.validators         
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

# It’s a security and validation layer to prevent:
# - Invalid or malicious filenames
# - Unsafe directory paths
# - Unexpected upload types
# - Broken email input

#=== Imports

import re

#=== Regular Expressions for Validation

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
NAME_RE = re.compile(r"^[^\\\\/:*?\\\"<>|]{1,100}$")  # forbid path separators and control chars

#=== Validation Functions

def valid_email(v: str) -> bool:
    return bool(EMAIL_RE.match(v or ""))

def valid_name(v: str) -> bool:
    return bool(NAME_RE.match((v or "").strip()))

def ext_allowed(filename: str, allowed_exts: set) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_exts