# auto-config-backup
# Part 1 - Connect to a Cisco device and run a show command
# Uses Netmiko for SSH connection to network devices

from netmiko import ConnectHandler

# device connection details
device = {
    "device_type": "cisco_ios",
    "host": "192.168.1.1",
    "username": "admin",
    "password": "cisco",
    "port": 22,
}

def connect_and_show(device):
    print(f"Connecting to {device['host']}...")
    
    try:
        # establish SSH connection
        connection = ConnectHandler(**device)
        print(f"Connected successfully!")
        
        # run show command
        output = connection.send_command("show ip interface brief")
        print("\n=== Interface Status ===")
        print(output)
        
        # close connection
        connection.disconnect()
        print("\nConnection closed.")
    
    except Exception as e:
        print(f"Connection failed: {e}")

connect_and_show(device)
# Part 2 - Save device config to a dated backup file

from netmiko import ConnectHandler
from datetime import datetime
import os

# create backups folder if it doesn't exist
if not os.path.exists("backups"):
    os.makedirs("backups")

def backup_config(device):
    print(f"Connecting to {device['host']}...")
    
    try:
        connection = ConnectHandler(**device)
        print("Connected!")
        
        # get the running config
        config = connection.send_command("show running-config")
        
        # create filename with date and device IP
        date = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"backups/{device['host']}_{date}.txt"
        
        # save config to file
        with open(filename, "w") as f:
            f.write(config)
        
        print(f"Config saved to {filename}")
        connection.disconnect()
    
    except Exception as e:
        print(f"Backup failed: {e}")

# device to backup
device = {
    "device_type": "cisco_ios",
    "host": "192.168.1.1",
    "username": "admin",
    "password": "cisco",
    "port": 22,
}

backup_config(device)
# Part 3 - Loop through multiple devices and backup all configs

devices = [
    {
        "device_type": "cisco_ios",
        "host": "192.168.1.1",
        "username": "admin",
        "password": "cisco",
        "port": 22,
    },
    {
        "device_type": "cisco_ios",
        "host": "192.168.1.2",
        "username": "admin",
        "password": "cisco",
        "port": 22,
    },
    {
        "device_type": "cisco_ios",
        "host": "192.168.1.3",
        "username": "admin",
        "password": "cisco",
        "port": 22,
    },
]

print("=== Starting Backup for All Devices ===")

# loop through each device and backup
for device in devices:
    backup_config(device)

print("\n=== All Backups Complete ===")
# Part 4 - Add error handling and generate a summary report

from datetime import datetime

def backup_all_devices(devices):
    success = []
    failed = []
    
    print("=== Starting Backup for All Devices ===\n")
    
    for device in devices:
        try:
            connection = ConnectHandler(**device)
            config = connection.send_command("show running-config")
            
            # save config to dated file
            date = datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = f"backups/{device['host']}_{date}.txt"
            
            with open(filename, "w") as f:
                f.write(config)
            
            print(f"[OK]    {device['host']} — saved to {filename}")
            success.append(device['host'])
            connection.disconnect()
        
        except Exception as e:
            print(f"[FAILED] {device['host']} — {e}")
            failed.append(device['host'])
    
    # save summary report
    report_date = datetime.now().strftime("%Y-%m-%d_%H-%M")
    with open(f"backups/summary_{report_date}.txt", "w") as f:
        f.write("=== Backup Summary Report ===\n\n")
        f.write(f"Total devices : {len(devices)}\n")
        f.write(f"Successful    : {len(success)}\n")
        f.write(f"Failed        : {len(failed)}\n\n")
        
        f.write("--- Successful ---\n")
        for ip in success:
            f.write(f"[OK]    {ip}\n")
        
        f.write("\n--- Failed ---\n")
        for ip in failed:
            f.write(f"[FAILED] {ip}\n")
    
    print(f"\n=== Backup Complete ===")
    print(f"Success: {len(success)} | Failed: {len(failed)}")
    print(f"Summary saved to backups/summary_{report_date}.txt")

# run the full backup
backup_all_devices(devices)