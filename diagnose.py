"""Review recorded DNS and domain-controller discovery results. No live probes."""
import argparse
import json
from pathlib import Path

FIELDS = {"client_dns_matches_lab", "dc_srv_resolves", "domain_controller_discovery"}


def diagnose(record):
    if not isinstance(record, dict) or set(record) != FIELDS:
        raise ValueError("Expected exactly the three documented check results")
    if any(type(record[key]) is not bool for key in FIELDS):
        raise ValueError("Check results must be JSON booleans")
    dns, srv, dc = (record[key] for key in (
        "client_dns_matches_lab", "dc_srv_resolves", "domain_controller_discovery"
    ))
    if srv and dc:
        return ("discovery_restored", "Domain controller discovery succeeded; verify user sign-in separately.")
    if not dns and not srv:
        return ("check_client_dns", "Verify the configured DNS resolver against the lab baseline, then repeat the checks.")
    if not srv:
        return ("check_srv_resolution", "Check access to the lab DNS resolver and confirm the domain SRV record.")
    return ("check_dc_discovery", "SRV lookup succeeded; review domain controller reachability and client logs.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checks", type=Path)
    args = parser.parse_args()
    try:
        result = diagnose(json.loads(args.checks.read_text(encoding="utf-8")))
    except (OSError, ValueError) as error:
        parser.exit(2, f"Input error: {error}\n")
    print(f"{result[0]}: {result[1]}")


if __name__ == "__main__":
    main()
