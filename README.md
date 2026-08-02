# Network Configuration Backup

A Python network automation tool that connects to Cisco network devices through SSH, retrieves their running configurations, and saves timestamped backups with a CSV summary report.

Built as part of my networking and network automation learning path.

## Features

- Connects to network devices through SSH using Netmiko
- Supports multiple devices from a JSON inventory
- Retrieves running configurations automatically
- Stores credentials securely in a local `.env` file
- Creates timestamped configuration backups
- Generates a CSV report for every backup operation
- Handles authentication failures and connection timeouts
- Disconnects safely from each device
- Supports custom commands, ports, and timeout values
- Returns a failure exit code when one or more backups fail
- Keeps credentials and generated backup files out of Git

## Project Structure

```text
auto-config-backup/
├── backup.py
├── devices.example.json
├── devices.json
├── .env.example
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── backups/
```

The following files and directories are private or generated automatically and are excluded from Git:

```text
.env
devices.json
.venv/
backups/
```

## Requirements

- Python 3.10 or newer
- SSH access to the target network devices
- Valid device credentials
- Network connectivity to each management IP address

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/netbyme/auto-config-backup.git
cd auto-config-backup
```

Create a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

The project uses:

- `netmiko` for SSH connections to network devices
- `python-dotenv` for loading credentials from `.env`

## Environment Configuration

Create a private `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add the SSH credentials used by your network devices:

```env
NETWORK_USERNAME=your_ssh_username
NETWORK_PASSWORD=your_ssh_password
```

Do not commit `.env` to GitHub.

The Wi-Fi SSID and Wi-Fi password are not used. The script requires the SSH username and password configured on the router or switch.

## Device Inventory

Create your private inventory from the example:

```bash
cp devices.example.json devices.json
```

Example `devices.json`:

```json
[
  {
    "name": "core-router-1",
    "device_type": "cisco_ios",
    "host": "192.168.1.1",
    "port": 22,
    "command": "show running-config"
  },
  {
    "name": "branch-router-1",
    "device_type": "cisco_ios",
    "host": "192.168.1.2",
    "port": 22,
    "command": "show running-config"
  }
]
```

Required fields:

| Field | Purpose |
|---|---|
| `name` | Friendly name used in reports and backup filenames |
| `device_type` | Netmiko platform identifier |
| `host` | Device management IP address or hostname |

Optional fields:

| Field | Default |
|---|---:|
| `port` | `22` |
| `command` | `show running-config` |
| `conn_timeout` | `15` seconds |
| `auth_timeout` | `20` seconds |
| `banner_timeout` | `20` seconds |
| `read_timeout` | `60` seconds |

Common Netmiko device types include:

```text
cisco_ios
cisco_xe
cisco_xr
cisco_nxos
```

The correct value depends on the target device platform.

## Usage

Run the backup using the default inventory and output directory:

```bash
python backup.py
```

Use a custom inventory file:

```bash
python backup.py --inventory lab-devices.json
```

Use a custom backup directory:

```bash
python backup.py --output-dir network-backups
```

Use both options:

```bash
python backup.py \
  --inventory lab-devices.json \
  --output-dir network-backups
```

## Example Successful Output

```text
=== Network Configuration Backup ===
Devices: 2
Inventory: devices.json
Output directory: backups

Connecting to core-router-1 (192.168.1.1)...
[CONNECTED] core-router-1
[SUCCESS] Backup saved: backups/core-router-1_192.168.1.1_2026-08-02_20-05-23.txt

Connecting to branch-router-1 (192.168.1.2)...
[CONNECTED] branch-router-1
[SUCCESS] Backup saved: backups/branch-router-1_192.168.1.2_2026-08-02_20-05-23.txt

=== Backup Complete ===
Successful: 2
Failed: 0
Summary report: backups/backup-summary_2026-08-02_20-05-23.csv
```

## Example Failed Connection

```text
Connecting to test-router (192.168.1.1)...
[FAILED] test-router: SSH connection timed out.

=== Backup Complete ===
Successful: 0
Failed: 1
Summary report: backups/backup-summary_2026-08-02_20-05-23.csv
```

A failed connection is recorded in the CSV report without causing the entire program to crash.

## Backup Files

Successful device backups are saved using this filename format:

```text
device-name_host_timestamp.txt
```

Example:

```text
core-router-1_192.168.1.1_2026-08-02_20-05-23.txt
```

Each file contains the output returned by the configured backup command.

## CSV Summary Report

Every run creates a CSV report:

```text
backups/backup-summary_2026-08-02_20-05-23.csv
```

Example:

```csv
device_name,host,status,backup_file,message
core-router-1,192.168.1.1,SUCCESS,backups/core-router-1_192.168.1.1_2026-08-02_20-05-23.txt,Configuration backed up successfully.
branch-router-1,192.168.1.2,FAILED,,SSH connection timed out.
```

The report records:

- Device name
- Management address
- Backup status
- Generated backup file
- Success or failure message

## How It Works

The script:

1. Loads SSH credentials from `.env`
2. Reads the device inventory from JSON
3. Validates the required inventory fields
4. Creates the backup directory when necessary
5. Connects to each device through SSH
6. Executes the configured backup command
7. Saves successful configuration outputs
8. Records failed connections without stopping the full operation
9. Disconnects from every established session
10. Generates a CSV summary report
11. Returns exit code `0` when all backups succeed
12. Returns exit code `1` when one or more backups fail

## Troubleshooting

### Missing credentials

```text
Error: NETWORK_USERNAME and NETWORK_PASSWORD must be configured in the .env file.
```

Confirm that `.env` exists and contains both required variables.

### Missing inventory

```text
Error: Inventory file not found: devices.json
```

Create it from the example:

```bash
cp devices.example.json devices.json
```

### Authentication failure

Confirm that:

- The username and password are correct
- SSH authentication is enabled
- The account is permitted to access the device

### Connection timeout

Confirm that:

- The management IP address is correct
- The device is reachable
- SSH is enabled
- TCP port 22 is not blocked
- The device supports the configured Netmiko platform type

A normal home ISP router may not provide Cisco-compatible SSH access.

## Security

- Never place real passwords directly inside `backup.py`
- Never commit `.env`
- Never publish private device inventories
- Use a dedicated automation account where possible
- Apply least-privilege access
- Protect generated configuration backups because they may contain sensitive information
- Rotate any credential that has previously been exposed publicly

## Responsible Use

Only connect to and back up devices that you own or are explicitly authorized to manage.

## Author

Mohammed Hammouch  
Casablanca, Morocco
