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
# ==================== PART 2 ====================
# Backup running-config to a timestamped file

def backup_config(device, backup_dir="backups"):
    """
    Connects to the device, retrieves the running-config,
    and saves it to a timestamped file in the backup directory.
    """
    print(f"\n[Part 2] Starting backup for {device['host']}...")
    
    # create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Created backup directory: {backup_dir}")
    
    try:
        # establish SSH connection
        connection = ConnectHandler(**device)
        print(f"Connected to {device['host']} for backup.")
        
        # retrieve running-config
        print("Retrieving running-config...")
        config = connection.send_command("show running-config")
        
        # generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hostname = device['host'].replace(".", "_")
        filename = f"{backup_dir}/{hostname}_running-config_{timestamp}.txt"
        
        # write config to file
        with open(filename, "w") as f:
            f.write(config)
        
        print(f"Config saved to: {filename}")
        
        # close connection
        connection.disconnect()
        print("Backup complete. Connection closed.")
        
        return filename
    
    except Exception as e:
        print(f"Backup failed: {e}")
        return None

# run both parts
if __name__ == "__main__":
    # Part 1
    connect_and_show(device)
    
    # Part 2
    backup_config(device)