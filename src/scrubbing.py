import re
import json
from pathlib import Path

class PrivacyScrubber:
    def __init__(self, config_path: Path):
        self.config = self._load_config(config_path)
        self.rules = self.config.get("scrubbing_rules", {})
        self.mapping = {}
        self.counter = 1
        
        # FIX: Move TLDs to config or use expanded set for future-proofing
        tlds = "|".join(self.config.get("privacy_tlds", ["com", "net", "org", "edu", "gov", "io", "co", "uk", "de", "in"]))
        
        self.patterns = {
            "ipv4": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
            "ipv6": r"(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:)",
            "mac": r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})",
            "domain": r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:" + tlds + r")\b"
        }
        
        self.custom_patterns = self.rules.get("sensitive_patterns", {})

    def _load_config(self, path: Path):
        with open(path, 'r') as f:
            return json.load(f)

    def _is_valid_ipv4(self, ip: str) -> bool:
        try:
            parts = ip.split(".")
            return len(parts) == 4 and all(0 <= int(p) <= 255 for p in parts)
        except ValueError:
            return False

    def _get_replacement(self, original_val: str, category: str) -> str:
        if self.rules.get("replacement_strategy") == "mask":
            return self.rules.get("mask_character", "*") * 8
        
        if original_val not in self.mapping:
            self.mapping[original_val] = f"[{category}_{self.counter}]"
            self.counter += 1
        return self.mapping[original_val]

    def scrub(self, content: str) -> str:
        scrubbed = content
        target_keys = self.rules.get("targets_to_scrub", [])

        # --- IPv4 SCRUBBING ---
        if "ipv4_addresses" in target_keys:
            # FIX: Sort by length (Longest first) to prevent partial replacement
            potential_ips = sorted(set(re.findall(self.patterns["ipv4"], scrubbed)), key=len, reverse=True)
            for ip in potential_ips:
                if self._is_valid_ipv4(ip):
                    scrubbed = scrubbed.replace(ip, self._get_replacement(ip, "IP"))

        # --- IPv6 SCRUBBING ---
        if "ipv6_addresses" in target_keys:
            ipv6s = sorted(set(re.findall(self.patterns["ipv6"], scrubbed)), key=len, reverse=True)
            for ipv6 in ipv6s:
                val = ipv6[0] if isinstance(ipv6, tuple) else ipv6
                scrubbed = scrubbed.replace(val, self._get_replacement(val, "IPv6"))

        # --- DOMAIN SCRUBBING ---
        if "domain_names" in target_keys:
            domains = sorted(set(re.findall(self.patterns["domain"], scrubbed)), key=len, reverse=True)
            for d in domains:
                if any(provider in d.lower() for provider in ["google", "cloudflare", "nmap", "github"]):
                    continue
                scrubbed = scrubbed.replace(d, self._get_replacement(d, "DOMAIN"))

        # --- CUSTOM SENSITIVE PATTERNS ---
        for label, pattern in self.custom_patterns.items():
            matches = sorted(set(re.findall(pattern, scrubbed, re.IGNORECASE)), key=len, reverse=True)
            for match in matches:
                val = match[0] if isinstance(match, tuple) else match
                scrubbed = scrubbed.replace(val, self._get_replacement(val, label.upper()))

        return scrubbed

# Global entry point
def run_scrubbing_phase(raw_file: Path, output_file: Path, config_path: Path):
    if not raw_file.exists(): return False
    scrubber = PrivacyScrubber(config_path)
    with open(raw_file, 'r', encoding='utf-8') as f:
        clean_content = scrubber.scrub(f.read())
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(clean_content)
    return True