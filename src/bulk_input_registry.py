import ipaddress
import sys
from pathlib import Path
import re
from . import registry

base_dir=Path(__file__).resolve().parent
#domain_validation
DOMAIN_REGEX = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))+$"
)

def is_valid_domain(value: str) -> bool:
    return bool(DOMAIN_REGEX.fullmatch(value))

#ipv4-look-alike issue resolved

def looks_like_ipv4(value: str) -> bool:
    parts = value.split(".")
    if len(parts) != 4:
        return False
    return all(p.isdigit() for p in parts)

def bulk_input_file(filename: Path):
    if not filename.exists():
        print("[!] File does not exist")
        sys.exit(1)

    if filename.stat().st_size == 0:
        print("[!] Empty file provided")
        sys.exit(0)

    with open(filename, "r") as file:
        targets = [line.strip() for line in file if line.strip()]

    for raw_val in targets:
        try:
            ipaddress.ip_address(raw_val)
            target_type = "IP"

        except ValueError:
            try:
                ipaddress.ip_network(raw_val, strict=False)
                target_type = "CIDR"

            except ValueError:
                if looks_like_ipv4(raw_val):
                    print(f"[-] Invalid IPv4 address: {raw_val}")
                    continue

                if is_valid_domain(raw_val):
                    target_type = "DOMAIN"
                else:
                    print(f"[-] Invalid target format: {raw_val}")
                    continue

        target_entry = {
            "Target_Name": raw_val,
            "Input_Value": raw_val,
            "Notes": f"Declared as {target_type}"
        }

        registry.add_targets_to_registry([target_entry])


