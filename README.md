# auto-config-backup

A Python automation tool that connects to Cisco network devices via SSH and automatically backs up their running configurations.

## What it does

- Connects to Cisco devices using SSH via Netmiko
- Pulls the running configuration automatically
- Saves each backup to a dated file — no manual work needed
- Loops through multiple devices in one run
- Generates a summary report showing success and failed backups

## Why this matters

Network engineers manually backup configs before every change — one missed backup can mean hours of downtime with no way to roll back. This script automates the entire process and saves results with timestamps so you always have a clean backup history.

## Project structure