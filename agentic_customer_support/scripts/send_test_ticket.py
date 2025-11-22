#!/usr/bin/env python3
"""Script to send test tickets to either Asya or Ray Serve implementation."""

import argparse
import json
import sys
from pathlib import Path
import httpx


def send_to_ray_serve(ticket_data: dict, endpoint: str = "http://localhost:8000/support"):
    """Send ticket to Ray Serve endpoint."""
    try:
        response = httpx.post(endpoint, json=ticket_data, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        print(f"Error connecting to Ray Serve: {e}", file=sys.stderr)
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        print(f"HTTP error from Ray Serve: {e.response.status_code}", file=sys.stderr)
        print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)


def send_to_asya(ticket_data: dict, endpoint: str = None):
    """Send ticket to Asya (via gateway or queue)."""
    # TODO: Implement Asya gateway/MCP client
    # For now, this is a placeholder
    print("Asya integration not yet implemented")
    print(f"Ticket data: {json.dumps(ticket_data, indent=2)}")
    return {"status": "not_implemented"}


def main():
    parser = argparse.ArgumentParser(description="Send test ticket to customer support system")
    parser.add_argument(
        "--framework",
        choices=["asya", "ray"],
        required=True,
        help="Framework to send ticket to"
    )
    parser.add_argument(
        "--ticket",
        type=Path,
        required=True,
        help="Path to JSON file containing ticket data"
    )
    parser.add_argument(
        "--endpoint",
        help="Endpoint URL (default: http://localhost:8000/support for Ray)"
    )
    
    args = parser.parse_args()
    
    # Load ticket data
    if not args.ticket.exists():
        print(f"Error: Ticket file not found: {args.ticket}", file=sys.stderr)
        sys.exit(1)
    
    with open(args.ticket) as f:
        ticket_data = json.load(f)
    
    # Send to appropriate framework
    if args.framework == "ray":
        endpoint = args.endpoint or "http://localhost:8000/support"
        result = send_to_ray_serve(ticket_data, endpoint)
        print(json.dumps(result, indent=2))
    elif args.framework == "asya":
        result = send_to_asya(ticket_data, args.endpoint)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

