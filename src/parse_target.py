def parse_target(raw: str):
    """
    Extract host and optional port from a raw target string.

    Returns:
        (host: str, port: Optional[str], meta: dict)
    """
    raw = raw.strip().replace("\ufeff", "")
    meta = {}

    if not raw:
        return None, None, {"error": "empty"}

    host = raw
    port = None

    # IPv6 with port: [::1]:443
    if raw.startswith("[") and "]" in raw:
        try:
            host_part, port_part = raw.split("]:", 1)
            host = host_part.strip("[]")
            if port_part.isdigit():
                port = port_part
                meta["port_source"] = "explicit"
        except ValueError:
            host = raw.strip("[]")

    # IPv4 / domain with port
    elif ":" in raw:
        left, right = raw.rsplit(":", 1)
        if right.isdigit():
            host = left
            port = right
            meta["port_source"] = "explicit"

    return host.strip(), port, meta
