import argparse
import requests
import sys
from datetime import datetime, timedelta

API_URL = "http://127.0.0.1:9999"

def get_alerts(since: str):
    try:
        response = requests.get(f"{API_URL}/alerts")
        if response.status_code == 200:
            alerts = response.json()
            print(f"Found {len(alerts)} alerts.")
            for alert in alerts:
                print(alert)
        else:
            print(f"Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to service. Is it running?")

def get_status():
    try:
        response = requests.get(f"{API_URL}/status")
        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to service. Is it running?")

def main():
    parser = argparse.ArgumentParser(description="Threat Hunting Assistant CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Alerts command
    alerts_parser = subparsers.add_parser("alerts", help="List alerts")
    alerts_parser.add_argument("--since", help="Time range (e.g., 24h)", default="24h")

    # Status command
    subparsers.add_parser("status", help="Show system status")

    args = parser.parse_args()

    if args.command == "alerts":
        get_alerts(args.since)
    elif args.command == "status":
        get_status()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
