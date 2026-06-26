# auto-config-backup
# Connects to a real Cisco IOS XR device via SSH
# Backs up running config and saves to a dated file

from netmiko import ConnectHandler
from datetime import datetime
import os

# create backups folder if it doesn't exist
if not os.path.exists("backups"):
    os.makedirs("backups")

# DevNet sandbox device credentials
devices = [
    {
        "device_type": "cisco_xr",
        "host": "sandbox-iosxr-1.cisco.com",
        "username": "admin",
        "password": "QAWSedrf1234!",
        "port": 22,
        "timeout": 60,
        "auth_timeout": 60,
        "banner_timeout": 60,
        "global_delay_factor": 2,
        "conn_timeout": 60,
    }
]

def backup_all_devices(devices):
    success = []
    failed = []

    print("=== Starting Backup ===\n")

    for device in devices:
        try:
            print(f"Connecting to {device['host']}...")
            connection = ConnectHandler(**device)
            print("Connected!")

            # get running config
            config = connection.send_command("show running-config")

            # save to dated file
            date = datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = f"backups/{device['host']}_{date}.txt"

            with open(filename, "w") as f:
                f.write(config)

            print(f"[OK] Config saved to {filename}")
            success.append(device['host'])
            connection.disconnect()

        except Exception as e:
            print(f"[FAILED] {device['host']} — {e}")
            failed.append(device['host'])

    # summary report
    print(f"\n=== Backup Complete ===")
    print(f"Success: {len(success)} | Failed: {len(failed)}")

backup_all_devices(devices)