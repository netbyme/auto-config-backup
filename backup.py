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