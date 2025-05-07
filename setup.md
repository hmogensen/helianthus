# Setting up timelapse on a remote Ubuntu device

## Install and Enable SSH Server
   ```bash
   sudo apt install openssh-server
   sudo systemctl enable ssh
   sudo systemctl start ssh
   ```

## Setting Up SSH Key Authentication

1. Generate SSH key pair on your local machine:
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. Copy your public key to the remote server:
   ```bash
   ssh-copy-id username@remote_host
   ```

## Setting Static IP using NetworkManager CLI (nmcli)

First, identify your WiFi connection name:

```bash
nmcli connection show
```

Use the following command to modify your connection, replacing the placeholders with your network information:

```bash
sudo nmcli connection modify "Your-WiFi-Connection-Name" \
    ipv4.method manual \
    ipv4.addresses 192.168.1.XXX0/24 \
    ipv4.gateway 192.168.1.1 \
    ipv4.dns "8.8.8.8,8.8.4.4"
```

- Replace `"Your-WiFi-Connection-Name"` with your actual WiFi connection name from step 1
- Replace `192.168.1.XXX0/24` with your desired static IP address and subnet mask
- Replace `192.168.1.1` with your router's IP address (gateway)
- You can keep the Google DNS servers (`8.8.8.8,8.8.4.4`) or replace them with your preferred DNS

## Automatic Restart with Systemd

Create a new service file:

```bash
sudo nano /etc/systemd/system/timelapse-camera.service
```

Add the following content (adjust paths and parameters as needed):

```
[Unit]
Description=Timelapse Recording Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/timelapse/directory
ExecStart=/usr/bin/python3 /path/to/timelapse/directory/timelapse.py camera_id location --interval 300
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and Start the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable timelapse-camera.service
sudo systemctl start timelapse-camera.service
```

You can manage the application via SSH with these commands:

```bash
# Check status
sudo systemctl status timelapse-camera.service

# Stop application
sudo systemctl stop timelapse-camera.service

# Start application
sudo systemctl start timelapse-camera.service

# Restart application
sudo systemctl restart timelapse-camera.service

# View logs
sudo journalctl -u timelapse-camera.service
```

If you need to run the application for multiple cameras, create separate service files for each:

```bash
sudo nano /etc/systemd/system/timelapse-garden.service
sudo nano /etc/systemd/system/timelapse-frontdoor.service
```

Each service file should have appropriate camera parameters:

```
ExecStart=/usr/bin/python3 /path/to/timelapse/directory/timelapse.py axis-cam1 garden --interval 300
```

## System Startup Security Considerations

When running services at system boot:

- **Service User Permissions**: 
  - The user specified in the service file doesn't need to be logged in
  - This user should have minimal permissions (principle of least privilege)
  - Consider creating a dedicated user for the timelapse application:
    ```bash
    sudo adduser --system --no-create-home timelapse
    ```
  
- **File Permissions**:
  - Make sure the credentials file is only readable by the service user:
    ```bash
    sudo chown timelapse:timelapse /path/to/credentials.txt
    sudo chmod 600 /path/to/credentials.txt
    ```
  
- **SSH Security**:
  - Consider disabling password authentication and using key-based authentication
  - Edit `/etc/ssh/sshd_config`:
    ```
    PasswordAuthentication no
    ```
  - Add your public key to authorized keys

## Prerequisites and Troubleshooting

Before setting up the service:

- Ensure `credentials.txt` exists in the working directory with the correct camera information
- Verify the user specified in the service file has permissions to:
  - Read the credentials file
  - Connect to the network cameras
  - Write to the output directory where images are saved
- Test the script manually first:
  ```bash
  cd /path/to/timelapse/directory
  python3 timelapse.py camera_id location --interval 300
  ```

If the service fails to start, check the logs:
```bash
sudo journalctl -u timelapse-camera.service -n 50
```

If you lose network connectivity after applying changes:

1. Try to reconnect manually:
   ```bash
   sudo nmcli device wifi connect "Your-WiFi-SSID" password "Your-WiFi-Password"
   ```

2. If still having issues, revert to DHCP:
   ```bash
   sudo nmcli connection modify "Your-WiFi-Connection-Name" ipv4.method auto
   sudo nmcli connection down "Your-WiFi-Connection-Name"
   sudo nmcli connection up "Your-WiFi-Connection-Name"
   ```
