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