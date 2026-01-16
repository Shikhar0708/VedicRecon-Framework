def calculate_vms(analysis: dict) -> int:
    """
    Deterministic Infrastructure Maturity Score (VMS v1.1).
    Engine-owned. Hardened against NoneType errors.
    """
    # 1. Initialize safe defaults
    score = 100
    if not analysis:
        return 0

    edge = analysis.get("is_edge_protected", False)

    # --- Base Maturity Deductions ---

    if not edge:
        score -= 25

    # FIX: Ensure density is a float and handle missing keys safely
    density_raw = analysis.get("defensive_density") or "0%"
    try:
        density_val = float(str(density_raw).replace("%", ""))
    except (ValueError, TypeError):
        density_val = 0.0

    if density_val == 0:
        score -= 20
    elif density_val < 50:
        score -= 10

    # Logic: Absence of OS info is common in hardened/edge-protected setups
    if analysis.get("os") == "DETECTION_FAILED" and not edge:
        score -= 5 # Minor penalty only if no edge is shielding it

    if not analysis.get("detected_vendors") and not edge:
        score -= 10

    services = str(analysis.get("services") or "").lower()
    if "tcpwrapped" in services and not edge:
        score -= 10

    # --- Expanded Critical Risk Flags ---

    critical_flags = {
        "unauth_database": False,
        "rce_surface": False,
        "exposed_cloud_metadata": False,
        "insecure_docker_socket": False
    }

    ports = str(analysis.get("ports") or "")
    banners = str(analysis.get("banners") or "").lower()

    # 1. Database Check
    if "mongodb" in services or "27017" in ports:
        critical_flags["unauth_database"] = True

    # 2. RCE Surface Check (Common dev ports)
    if any(p in ports for p in ["3000", "8080", "8081"]) and "http" in services:
        critical_flags["rce_surface"] = True

    # 3. Cloud Metadata (IMDSv1/v2)
    if "metadata" in banners or "instance-id" in banners:
        critical_flags["exposed_cloud_metadata"] = True

    # 4. Insecure Docker Socket (Remote API)
    if "2375" in ports or "docker" in services:
        critical_flags["insecure_docker_socket"] = True

    # --- Updated Risk-Based Score Caps ---

    score_cap = 100

    if critical_flags["unauth_database"]:
        score_cap = min(score_cap, 40)
    if critical_flags["rce_surface"]:
        score_cap = min(score_cap, 35)
    if critical_flags["exposed_cloud_metadata"]:
        score_cap = min(score_cap, 20) # High severity
    if critical_flags["insecure_docker_socket"]:
        score_cap = min(score_cap, 15) # Critical severity

    # Multi-factor Failure (The 'Meltdown' Cap)
    if sum(critical_flags.values()) >= 2:
        score_cap = min(score_cap, 10)

    # Final Calculation
    score = min(score, score_cap)
    
    # Final safety: Ensure return is an int and within 0-100 range
    return max(0, min(100, int(score)))