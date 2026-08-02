#!/usr/bin/env python3

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Back up running configurations from network devices."
    )

    parser.add_argument(
        "--inventory",
        default="devices.json",
        help="Path to the JSON device inventory. Default: devices.json",
    )

    parser.add_argument(
        "--output-dir",
        default="backups",
        help="Directory where backup files are stored. Default: backups",
    )

    return parser.parse_args()


def load_inventory(inventory_path: Path) -> list[dict[str, Any]]:
    if not inventory_path.exists():
        raise FileNotFoundError(f"Inventory file not found: {inventory_path}")

    try:
        with inventory_path.open("r", encoding="utf-8") as file:
            devices = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in inventory file: {error}"
        ) from error

    if not isinstance(devices, list):
        raise ValueError("Inventory must contain a JSON list of devices.")

    if not devices:
        raise ValueError("Inventory does not contain any devices.")

    required_fields = {"name", "device_type", "host"}

    for index, device in enumerate(devices, start=1):
        if not isinstance(device, dict):
            raise ValueError(f"Device {index} must be a JSON object.")

        missing_fields = required_fields - device.keys()

        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(
                f"Device {index} is missing required fields: {missing}"
            )

    return devices


def safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", value)


def build_connection_parameters(
    device: dict[str, Any],
    username: str,
    password: str,
) -> dict[str, Any]:
    return {
        "device_type": device["device_type"],
        "host": device["host"],
        "username": username,
        "password": password,
        "port": device.get("port", 22),
        "conn_timeout": device.get("conn_timeout", 15),
        "auth_timeout": device.get("auth_timeout", 20),
        "banner_timeout": device.get("banner_timeout", 20),
    }


def save_configuration(
    output_directory: Path,
    device: dict[str, Any],
    configuration: str,
    timestamp: str,
) -> Path:
    device_name = safe_filename(device["name"])
    host = safe_filename(device["host"])

    filename = f"{device_name}_{host}_{timestamp}.txt"
    backup_path = output_directory / filename

    backup_path.write_text(configuration, encoding="utf-8")

    return backup_path


def write_summary_report(
    output_directory: Path,
    results: list[dict[str, str]],
    timestamp: str,
) -> Path:
    summary_path = output_directory / f"backup-summary_{timestamp}.csv"

    with summary_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "device_name",
                "host",
                "status",
                "backup_file",
                "message",
            ],
        )

        writer.writeheader()
        writer.writerows(results)

    return summary_path


def backup_device(
    device: dict[str, Any],
    username: str,
    password: str,
    output_directory: Path,
    timestamp: str,
) -> dict[str, str]:
    device_name = device["name"]
    host = device["host"]
    command = device.get("command", "show running-config")

    connection = None

    print(f"\nConnecting to {device_name} ({host})...")

    try:
        connection_parameters = build_connection_parameters(
            device,
            username,
            password,
        )

        connection = ConnectHandler(**connection_parameters)

        print(f"[CONNECTED] {device_name}")

        configuration = connection.send_command(
            command,
            read_timeout=device.get("read_timeout", 60),
        )

        if not configuration.strip():
            raise RuntimeError("The device returned an empty configuration.")

        backup_path = save_configuration(
            output_directory,
            device,
            configuration,
            timestamp,
        )

        print(f"[SUCCESS] Backup saved: {backup_path}")

        return {
            "device_name": device_name,
            "host": host,
            "status": "SUCCESS",
            "backup_file": str(backup_path),
            "message": "Configuration backed up successfully.",
        }

    except NetmikoAuthenticationException:
        message = "SSH authentication failed."
        print(f"[FAILED] {device_name}: {message}")

    except NetmikoTimeoutException:
        message = "SSH connection timed out."
        print(f"[FAILED] {device_name}: {message}")

    except Exception as error:
        message = str(error)
        print(f"[FAILED] {device_name}: {message}")

    finally:
        if connection is not None:
            connection.disconnect()

    return {
        "device_name": device_name,
        "host": host,
        "status": "FAILED",
        "backup_file": "",
        "message": message,
    }


def main() -> int:
    load_dotenv()

    arguments = parse_arguments()

    username = os.getenv("NETWORK_USERNAME")
    password = os.getenv("NETWORK_PASSWORD")

    if not username or not password:
        print(
            "Error: NETWORK_USERNAME and NETWORK_PASSWORD "
            "must be configured in the .env file.",
            file=sys.stderr,
        )
        return 1

    inventory_path = Path(arguments.inventory)
    output_directory = Path(arguments.output_dir)

    try:
        devices = load_inventory(inventory_path)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    output_directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results: list[dict[str, str]] = []

    print("=== Network Configuration Backup ===")
    print(f"Devices: {len(devices)}")
    print(f"Inventory: {inventory_path}")
    print(f"Output directory: {output_directory}")

    for device in devices:
        result = backup_device(
            device,
            username,
            password,
            output_directory,
            timestamp,
        )

        results.append(result)

    summary_path = write_summary_report(
        output_directory,
        results,
        timestamp,
    )

    successful = sum(
        result["status"] == "SUCCESS" for result in results
    )
    failed = len(results) - successful

    print("\n=== Backup Complete ===")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Summary report: {summary_path}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())