from src.vms_engine import calculate_vms

def run_bulk_vms(inventory):
    """
    Runs authoritative VMS scoring per node.
    Does NOT infer environment-level security.
    """
    results = []

    for node in inventory:
        score, findings, edge_opacity = calculate_vms({
            "ports": node["technical_details"]["ports"],
            "services": node["technical_details"]["services"],
            "banners": node["technical_details"]["os"],
            "is_edge_protected": False,  # IMPORTANT: node-local only
            "defensive_density": None
        })

        node["vms"] = {
            "score": score,
            "edge_opacity": edge_opacity,
            "findings": findings
        }

        results.append(node)

    return results
