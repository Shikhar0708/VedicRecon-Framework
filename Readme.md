🕉️ VedicRecon Framework v1.0-alpha
Autonomous AI-Augmented Infrastructure Reconnaissance & Risk Intelligence

VedicRecon is a next-generation security framework that merges high-performance network discovery with strategic AI reasoning. By utilizing a Go-based execution engine (the "Muscle") and a Python-based analytical core (the "Brain"), VedicRecon automates the transition from raw packet data to executive-level intelligence reports.

🏗️ The Hybrid Architecture
Unlike traditional scanners, VedicRecon separates "Doing" from "Thinking":

The Muscle (Go Engine): Engineered for concurrency. Handles multi-threaded Nmap execution, HTTP banner grabbing, and high-speed directory fuzzing.

The Brain (Python Orchestrator): Manages the stateful registry, enforces the "Scrub Last" privacy boundary, and performs cross-phase data correlation.

🚀 Key Features
Stateful Target Registry: Persistent tracking with automated integrity sealing and session management.

VMS (Vedic Maturity Score): A proprietary 1-100 scoring system that evaluates infrastructure based on exposure, defensive density, and information leakage.

Privacy-Native (Scrub Last): Anonymizes all PII (IPs, Domains, MACs) using JSON-recursive scrubbing before any data leaves your machine for AI analysis.

Defensive Fingerprinting: Automated detection of WAFs (Cloudflare/Akamai) and security barriers (TCPWrapped) without attempting a bypass.

Phase 6 Consent Gate: Strict manual control over "noisy" enumeration (Fuzzing) to prevent accidental IDS/IPS triggers.

🚦 The 11-Phase Operational Workflow
VedicRecon follows a rigorous, legally-defensible reconnaissance methodology:

Phase 0-1: Environment Verification & Target Ingestion.

Phase 2-5: Baseline Recon, Service Mapping, & Defensive Fingerprinting.

Phase 6: Consent Gate for Active Directory Enumeration.

Phase 7-8: Data Correlation & Immutable Master JSON Generation.

Phase 9: Privacy Scrubbing (The Anonymization Layer).

Phase 10-11: AI-Assisted Intelligence Drafting & Professional Handoff.

🛠️ Installation & Quick Start
🐧 Linux
Bash

chmod +x setup.sh
sudo ./setup.sh
sudo python3 main.py
🪟 Windows
Run setup.bat as Administrator.

DOS

venv\Scripts\activate
python main.py
🔑 Configuration
Create a .env file in the root directory:

Code snippet

GEMINI_API_KEY=your_api_key_here
🛡️ Ethical Guardrails
Non-Exploitative: VedicRecon is a reconnaissance tool. It does not contain exploit payloads or bypass logic.

Data Sovereignty: Raw scan data never leaves the local environment.

Attribution: All AI-generated findings are labeled as "[AI ANALYSIS – ADVISORY ONLY]" and require manual validation.

Developed for Security Architects and Red Teams | © 2026 VedicRecon

This project is licensed under the GNU GPL v3.0 to ensure transparency, user freedom, and prevent proprietary misuse of privacy-sensitive security tooling.