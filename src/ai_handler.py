import json
import time
import sys
import threading
import re
from pathlib import Path
from datetime import datetime
from google import genai
from google.genai import types
import random

class ProgressDisplay:
    """Handles foreground animation and time estimation."""
    def __init__(self, estimate=20):
        self.estimate = estimate
        self.stop_event = threading.Event()
        self.start_time = time.time()

    def animate(self):
        chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        idx = 0
        while not self.stop_event.is_set():
            elapsed = int(time.time() - self.start_time)
            percent = min(99, int((elapsed / self.estimate) * 100))
            bar_size = 20
            pos = elapsed % bar_size
            bar = ["-"] * bar_size
            bar[pos] = "#"
            bar_str = "".join(bar)
            
            sys.stdout.write(
                f"\r  {chars[idx % len(chars)]} [ {bar_str} ] {percent}% | ETC: {max(0, self.estimate - elapsed)}s remaining... "
            )
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)

    def stop(self):
        self.stop_event.set()
        sys.stdout.write("\r" + " " * 85 + "\r")
        sys.stdout.flush()

class AIHandler:
    def __init__(self, profile_path: Path):
        """The missing constructor that was causing the TypeError."""
        self.profile_path = profile_path
        self.config = self._load_profile()
        self.client = None
        
    def _load_profile(self):
        with open(self.profile_path, 'r') as f:
            return json.load(f)

    def _save_profile(self):
        with open(self.profile_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def verify_api_key(self):
        """Ensures API key is present and initializes the GenAI Client."""
        api_key = self.config["api_configuration"].get("api_key", "").strip()
        if not api_key:
            print("\n[!] AI Reporting: No Google Gemini API Key found.")
            api_key = input("[?] Please enter your Gemini API Key: ").strip()
            self.config["api_configuration"]["api_key"] = api_key
            self._save_profile()
            print("[+] API Key saved to config.")
        self.client = genai.Client(api_key=api_key)

    def generate_report(self, scrubbed_data: str):
        active_p = self.config["active_profile"]
        profile_data = self.config["profiles"][active_p]
        constraints = self.config.get("ai_constraints", {})
        evidence = self.config.get("evidence_policy", {})

        constraint_text = "\n".join([f"- {k.replace('_', ' ').upper()}: {v}" for k, v in constraints.items()])
        evidence_text = f"- ALLOWED LEVELS: {', '.join(evidence.get('allowed_levels', []))}"
        
        system_instruction = (
            f"ROLE: {profile_data['role']}\n"
            f"FOCUS: {profile_data['focus']}\n"
            f"FORMAT: {profile_data['format']}\n\n"
            "GOVERNANCE CONSTRAINTS:\n"
            f"{constraint_text}\n\n"
            "TABLE FORMATTING RULES:\n"
            "1. When generating Markdown tables, ensure every row ends with a pipe '|'.\n"
            "2. Keep Table Rationales concise (max 2 sentences) to prevent layout breaking.\n"
            "3. Do NOT use multiple spaces to align columns; use single spaces and standard Markdown pipes.\n\n"
            "CONTEXTUAL SEMANTICS: If is_edge_protected is True, interpret the absence of services or OS data as 'SUCCESSFUL ABSTRACTION' and 'HIGH DEFENSIVE MATURITY.' Do not label this as a visibility gap; label it as intentional perimeter hardening.\n\n"
            "STRICT PRIVACY: Node IDs (e.g., [IP_1]) are tokens. Do NOT attempt to resolve them.\n\n"
            "STRATEGIC METRIC: Use the provided 'Maturity Score' to set the tone.\n"
                "- 80-100: Praise the 'Defensive Excellence' and focus on minor optimizations.\n"
                "- 50-79: Label as 'Developing Posture' and suggest hardening steps.\n"
                "- 0-49: Label as 'Critical Exposure' and prioritize foundational security."
        )

        # ... [Keep your system_instruction logic] ...

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.config["api_configuration"]["model_name"],
                    contents=f"ANONYMIZED INFRASTRUCTURE DATA:\n{scrubbed_data}",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=self.config["api_configuration"]["temperature"],
                        top_p=self.config["api_configuration"]["top_p"]
                    )
                )
                return response.text

            except Exception as e:
                # If it's a 503/Overloaded error and we have retries left
                if "503" in str(e) or "overloaded" in str(e).lower():
                    if attempt < max_retries - 1:
                        wait_time = ((attempt + 1) * 5) + random.uniform(1, 3)
                        # The progress bar thread is still running, so we just sleep
                        time.sleep(wait_time)
                        continue 
                return f"[!] AI Engine Error: {str(e)}"

def run_ai_reporting(scrubbed_file: Path, report_dir: Path, profile_path: Path):
    handler = AIHandler(profile_path)
    handler.verify_api_key()
    
    with open(scrubbed_file, 'r') as f:
        data = f.read()

    line_count = len(data.splitlines())
    etc_seconds = max(20, 15 + (line_count // 5))

    print(f"[*] Analyzing infrastructure and drafting report...")
    progress = ProgressDisplay(estimate=etc_seconds)
    anim_thread = threading.Thread(target=progress.animate)
    anim_thread.start()

    try:
        raw_report = handler.generate_report(data)
        progress.stop()
        anim_thread.join()

        # Build Footer
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer = (
            "\n\n---\n"
            f"*Generated by VedicRecon 1.0.0-alpha | {timestamp}*\n"
            "> **NOTICE:** Findings are advisory and require manual validation."
        )

        # AGGRESSIVE CLEANUP: Merge AI output and footer, rstrip all, then add one final newline
        final_md = (raw_report.strip() + footer).rstrip()
        final_md = re.sub(r' {5,}', ' ', final_md)
        final_md = re.sub(r'\s+$', '\n', final_md)

        # Archive Report
        report_path = report_dir / f"VedicRecon_Report_{int(time.time())}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(final_md)
        
        print(f"[+] Intelligence report successfully lodged at: {report_path}")

    except Exception as e:
        if 'progress' in locals(): progress.stop()
        print(f"[!] Critical reporting failure: {e}")