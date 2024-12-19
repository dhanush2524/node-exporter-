import os
import subprocess
import sys

def check_python_version():
    correct_version = (3, 10)  # Define your required Python version here
    current_version = sys.version_info[:2]
    print(f"Current Python version: {'.'.join(map(str, current_version))}")

    if current_version < correct_version:
        print(f"Python version is below {'.'.join(map(str, correct_version))}. Please upgrade.")
        print("Visit https://www.python.org/downloads/ to download the latest Python version.")
    else:
        print("Python version is correct.")

def install_node_exporter():
    print("Installing Node Exporter...")
    try:
        # Check if the user already exists
        user_check = subprocess.run(["id", "-u", "node_exporter"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if user_check.returncode != 0:
            subprocess.run(["sudo", "useradd", "--no-create-home", "--shell", "/usr/sbin/nologin", "node_exporter"], check=True)

        subprocess.run(["sudo", "mkdir", "-p", "/etc/node_exporter", "/var/lib/node_exporter"], check=True)
        subprocess.run(["sudo", "chown", "node_exporter:node_exporter", "/etc/node_exporter", "/var/lib/node_exporter"], check=True)

        # Correct URL for downloading Node Exporter
        print("Downloading Node Exporter...")
        try:
            subprocess.run(["wget", "https://github.com/prometheus/node_exporter/releases/download/v1.8.1/node_exporter-1.8.1.linux-amd64.tar.gz"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading Node Exporter: {e}")
            return

        subprocess.run(["tar", "-xvf", "node_exporter-1.8.1.linux-amd64.tar.gz"], check=True)
        
        print("Moving Node Exporter binaries and configuration files...")
        subprocess.run(["sudo", "mv", "node_exporter-1.8.1.linux-amd64/node_exporter", "/usr/local/bin/"], check=True)
        subprocess.run(["sudo", "chown", "-R", "node_exporter:node_exporter", "/usr/local/bin/"], check=True)

        # Create systemd service
        create_systemd_service()

        print("Node Exporter installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Node Exporter: {e}")

def create_systemd_service():
    service_file = """
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
ExecStart=/usr/local/bin/node_exporter
Restart=always
LimitNOFILE=4096

[Install]
WantedBy=multi-user.target
"""
    try:
        print("Creating systemd service file for Node Exporter...")
        # Ask for sudo permission to write the service file
        subprocess.run(["sudo", "sh", "-c", f'echo "{service_file}" > /etc/systemd/system/node_exporter.service'], check=True)

        print("Systemd service file created for Node Exporter.")

        # Reload systemd, enable, and start the service
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "node_exporter"], check=True)
        subprocess.run(["sudo", "systemctl", "start", "node_exporter"], check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error creating systemd service for Node Exporter: {e}")

def edit_node_exporter_configuration():
    config_path = "/etc/node_exporter/node_exporter.yml"
    try:
        if os.path.exists(config_path):
            print(f"Editing Node Exporter configuration at {config_path}...")
            subprocess.run(["sudo", "nano", config_path])
        else:
            print(f"Configuration file not found at {config_path}. Please ensure Node Exporter is installed.")
    except Exception as e:
        print(f"Error editing Node Exporter configuration: {e}")

def remove_node_exporter():
    print("Removing Node Exporter and related files...")
    try:
        # Stop the Node Exporter service if it is running
        service_check = subprocess.run(["systemctl", "is-active", "--quiet", "node_exporter"])
        if service_check.returncode == 0:
            subprocess.run(["sudo", "systemctl", "stop", "node_exporter"], check=True)

        # Remove Node Exporter related files
        subprocess.run(["sudo", "userdel", "node_exporter"], check=True)
        
        # Removing Node Exporter directories and binaries
        subprocess.run(["sudo", "rm", "-rf", "/etc/node_exporter", "/var/lib/node_exporter", "/usr/local/bin/node_exporter"], check=True)

        # Remove Node Exporter tarballs and extracted directories
        subprocess.run(["sudo", "rm", "-rf", "node_exporter-1.8.1.linux-amd64", "node_exporter-1.8.1.linux-amd64.tar.gz"], check=True)
        
        # If there's any .1 file (from multiple downloads), remove it
        subprocess.run(["sudo", "rm", "-f", "node_exporter-1.8.1.linux-amd64.tar.gz.1"], check=True)

        # Remove systemd service
        subprocess.run(["sudo", "rm", "-f", "/etc/systemd/system/node_exporter.service"], check=True)

        print("Node Exporter and related files removed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error removing Node Exporter: {e}")

def check_node_exporter_status():
    try:
        print("Checking Node Exporter service status...")
        # Reload systemd if the service file has changed
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        
        # Check Node Exporter service status
        service_status = subprocess.run(["sudo", "systemctl", "status", "node_exporter"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if service_status.returncode != 0:
            print(f"Node Exporter service is not active. Attempting to start it...")
            subprocess.run(["sudo", "systemctl", "start", "node_exporter"], check=True)
            print("Node Exporter service started successfully.")
        else:
            print("Node Exporter service is already running.")

        # Check for logs if Node Exporter is still not running
        service_logs = subprocess.run(
            ["sudo", "journalctl", "-u", "node_exporter", "--since", "10 minutes ago"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if service_logs.stdout:
            print(service_logs.stdout.decode())

    except subprocess.CalledProcessError as e:
        print(f"Error checking Node Exporter service: {e}")

def main():
    while True:
        print("\nChoose an option:")
        print("1. Check Python Version")
        print("2. Install Node Exporter")
        print("3. Edit Node Exporter Configuration")
        print("4. Remove Node Exporter")
        print("5. Check Node Exporter Service Status")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            check_python_version()
        elif choice == "2":
            install_node_exporter()
        elif choice == "3":
            edit_node_exporter_configuration()
        elif choice == "4":
            remove_node_exporter()
        elif choice == "5":
            check_node_exporter_status()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
