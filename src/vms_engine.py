def calculate_vms(analysis: dict) -> tuple:
    """
    Deterministic Infrastructure Maturity Score (VMS v1.2).
    Returns: (int score, list findings)
    """

    # --- Initialization ---
    score = 100
    findings = []

    if not analysis:
        return 0, ["No analysis data available"]

    # Normalize core inputs
    edge = bool(analysis.get("is_edge_protected", False))

    ports = str(analysis.get("Open_Ports") or analysis.get("ports") or "")
    services = str(analysis.get("Services") or analysis.get("services") or "").lower()
    banners = str(analysis.get("OS_Tech") or analysis.get("banners") or "").lower()

    # --- Base Architecture Assessment ---
    if edge:
        findings.append("Edge / Reverse-Proxy Abstraction Detected")
    else:
        score -= 25
        findings.append("Direct Exposure: No Edge Protection (-25)")

    # Defensive Density (internal layers, not perimeter)
    density_raw = analysis.get("defensive_density") or "0%"
    try:
        density_val = float(str(density_raw).replace("%", "").split()[0])
    except (ValueError, TypeError, IndexError):
        density_val = 0.0

    if density_val == 0:
        score -= 15
        findings.append("Zero Internal Defensive Density (-15)")
    elif density_val < 50:
        score -= 8
        findings.append("Low Internal Defensive Density (-8)")

    # --- Critical Exposure Flags (Evidence-Gated) ---
    critical_flags = {
        "exposed_database": False,
        "probable_rce_surface": False,
        "exposed_cloud_metadata": False,
        "insecure_docker_socket": False
    }

    # 1. Exposed Database (presence ≠ unauth, handled carefully)
    if "mongodb" in services or "27017" in ports:
        critical_flags["exposed_database"] = True
        findings.append("CRITICAL: Database Service Directly Exposed")

    # 2. Probable RCE / Dev Surface (context-aware)
    if any(p in ports for p in ["3000", "8080", "8081"]) and not edge:
        critical_flags["probable_rce_surface"] = True
        findings.append("HIGH: Unprotected Development / Application Surface")

    # 3. Cloud Metadata Indicators (low-noise signals only)
    if any(k in banners for k in ["metadata", "instance-id", "169.254.169.254"]):
        critical_flags["exposed_cloud_metadata"] = True
        findings.append("CRITICAL: Potential Cloud Metadata Exposure")

    # 4. Docker Remote API
    if "2375" in ports or ("docker" in services and not edge):
        critical_flags["insecure_docker_socket"] = True
        findings.append("CRITICAL: Docker Remote API Exposed")

    # --- Risk-Based Score Capping (Non-Linear Impact) ---
    score_cap = 100

    if critical_flags["exposed_database"]:
        score_cap = min(score_cap, 45)

    if critical_flags["probable_rce_surface"]:
        score_cap = min(score_cap, 35)

    if critical_flags["exposed_cloud_metadata"]:
        score_cap = min(score_cap, 20)

    if critical_flags["insecure_docker_socket"]:
        score_cap = min(score_cap, 15)

    # --- Multi-Failure Meltdown Logic ---
    active_criticals = [k for k, v in critical_flags.items() if v]

    if len(active_criticals) >= 2:
        score_cap = min(score_cap, 10)
        findings.append(
            f"MELTDOWN: Multiple Critical Exposures ({', '.join(active_criticals)})"
        )

    # --- Final Score Resolution ---
    final_score = min(score, score_cap)

    return max(0, min(100, int(final_score))), findings
