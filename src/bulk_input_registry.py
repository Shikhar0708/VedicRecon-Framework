from pathlib import Path
import re
from . import registry,parse_target

# domain validation
DOMAIN_REGEX = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))+$"
)

def is_valid_domain(value: str) -> bool:
    return bool(DOMAIN_REGEX.fullmatch(value))


def looks_like_ipv4(value: str) -> bool:
    parts = value.split(".")
    return len(parts) == 4 and all(p.isdigit() for p in parts)


def bulk_input_file(filename: Path):
    if not filename.exists():
        print("[!] File does not exist")
        return

    with open(filename, "r", encoding="utf-8", errors="ignore") as file:
        lines = [
            line.strip().replace("\ufeff", "")
            for line in file
            if line.strip() and not line.lstrip().startswith("#")
        ]

    final_registry_list = []

    for raw in lines:
        host = raw
        port = None

        # --- PORT EXTRACTION (NO VALIDATION) ---
        if ":" in raw:
            left, right = raw.rsplit(":", 1)
            if right.isdigit():
                host = left.strip()
                port = right.strip()

        final_registry_list.append({
            "Target_Name": raw,
            "Input_Value": host,
            "Assigned_Port": port,
            "Notes": "Bulk imported"
        })

    if not final_registry_list:
        print("[!] No targets extracted from file.")
        return

    registry.add_targets_to_registry(final_registry_list)

