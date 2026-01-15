import time
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # Move up from src to root
CONFIG_PATH = BASE_DIR / "config" / "profiles.json"

def display_legal_boundary():
    # Use Path for cross-platform reliability

    
    # 1. Persistence Check: Skip if already verified
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r") as f:
                existing_data = json.load(f)
                if existing_data.get("legal_status") == "verified":
                    return True
        except (json.JSONDecodeError, KeyError):
            pass

    notice = f"""
    {"="*60}
    VEDICRECON v1.0 | IMPORTANT NOTICE
    {"="*60}
    
    [NON-BYPASS NOTICE & ETHICAL USE POLICY]
    
    1. SCOPE ENFORCEMENT: VedicRecon is designed to operate strictly 
       within user-defined boundaries. Unauthorized scanning is illegal.
    2. DEFENSIVE AWARENESS: This tool detects WAF/IPS signatures. 
       Attempts to bypass security controls are NOT supported.
    3. DATA PRIVACY: Sensitive data is scrubbed before AI analysis 
       per the defined 'privacy.json' policy.
    4. LIABILITY: The developer assumes no liability for misuse, 
       network disruption, or legal consequences resulting from 
       unauthorized operation.
    
    [!] SYSTEM READY. 
    {"="*60}
    """
    print(notice)
    
    # Industrial "Speed Bump" - makes the user actually read it
    try:
        confirmation = input("[?] Type 'ACCEPT' to acknowledge: ").strip().upper()
        if confirmation == "ACCEPT":
            print("[+] Verifying integrity, please wait...")
            
            # 2. READ: Load the current dictionary
            with open(CONFIG_PATH, "r") as file:
                file_data = json.load(file)
            
            # 3. MODIFY: Update the dictionary
            file_data["legal_status"] = "verified"
            
            # 4. WRITE: Overwrite with the full updated data
            with open(CONFIG_PATH, "w") as final_file:
                # Correct syntax: json.dump(WHAT, WHERE)
                json.dump(file_data, final_file, indent=2)
            
            print("\n[+] Integrity Verified. Unlocking Scope Definition...")
            time.sleep(1)
            print("\n[+] Rerun the program to use.")
            sys.exit(0)
        else:
            print("[!] Agreement not accepted. Exiting.")
            sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)

#creating a function to check status
def check_status():
    with open(CONFIG_PATH, "r") as check:
        status = json.load(check)
        try:
            if status["legal_status"] == "verified":
                return True
        except(KeyError, json.JSONDecodeError):
            display_legal_boundary()
            time.sleep(1)
            return True
