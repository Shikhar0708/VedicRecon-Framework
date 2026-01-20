import json
import time
import sys
from pathlib import Path

# Move up to root and then into config
BASE_DIR = Path(__file__).resolve().parent.parent
LEGAL_JSON = BASE_DIR / "config" / "legal_status.json"

def check_status():
    """Independent check for the legal flag."""
    if LEGAL_JSON.exists():
        try:
            with open(LEGAL_JSON, "r") as f:
                data = json.load(f)
                if data.get("status") == "verified":
                    return True
        except:
            pass
    
    # If file doesn't exist or isn't verified, run the prompt
    return run_legal_prompt()

def run_legal_prompt():

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
    
    try:
        confirm = input("[?] Type 'ACCEPT' to continue: ").strip().upper()
        if confirm == "ACCEPT":
            # Create the NEW separate JSON file
            with open(LEGAL_JSON, "w") as f:
                json.dump({"status": "verified", "accepted_at": time.time()}, f, indent=2)
            
            print("\n[+] Status recorded. Accessing Framework...")
            return True
        else:
            print("[!] Agreement rejected.")
            sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)