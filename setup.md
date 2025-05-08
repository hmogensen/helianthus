# Setting up timelapse on a remote Ubuntu device

## Install and Enable SSH Server
   ```bash
   sudo apt install openssh-server
   sudo systemctl enable ssh
   sudo systemctl start ssh
   ```

## Setting Up SSH Key Authentication

1. Check available keys on your local machine
   ```bash
   ls -la ~/.ssh
   ```

2. If they do not exist: generate SSH key pair on your local machine:
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
## Running Python Scripts Daily with Systemd

You can use systemd timers to run your Python script daily, even after system reboots. This approach provides better logging, more control, and is the modern way to schedule tasks on Ubuntu.

### 1. Create your Python script

First, create your Python script in a location where it can be easily accessed:

```bash
mkdir -p ~/repos/timelapse
touch ~/repos/timelapse/download_data.py
chmod +x ~/repos/timelapse/download_data.py
```

Your script should have a proper shebang:

```python
#!/usr/bin/env python3

# Your script code here
```

### 2. Create a systemd service file

Create a service file that will run your script:

```bash
sudo nano /etc/systemd/system/timelapse-download.service
```

Add the following content:

```
[Unit]
Description=Daily Python Task
After=network.target

[Service]
Type=oneshot
User=username
ExecStart=/usr/bin/python3 /home/username/repos/timelapse/timelapse-download.py
WorkingDirectory=/home/username/repos/timelapse

[Install]
WantedBy=multi-user.target
```

### 3. Create a systemd timer file

Create a timer file that will trigger the service:

```bash
sudo nano /etc/systemd/system/timelapse-download.timer
```

Add the following content:

```
[Unit]
Description=Run timelapse-download service daily

[Timer]
OnCalendar=*-*-* 00:00:00
Persistent=true
RandomizedDelaySec=10min

[Install]
WantedBy=timers.target
```

The key settings here:
- `OnCalendar=*-*-* 00:00:00` runs the script daily at midnight
- `Persistent=true` ensures the timer will trigger even if the system was off at the scheduled time
- `RandomizedDelaySec=10min` adds a small random delay to avoid all timers running at exactly the same time

### 4. Enable and start the timer

```bash
sudo systemctl daemon-reload
sudo systemctl enable timelapse-download.timer
sudo systemctl start timelapse-download.timer
```

### 5. Verify the timer is working

```bash
sudo systemctl list-timers
```

This will show all active timers, including when they'll next run.

### 6. Check logs

To check if your script ran successfully, you can use:

```bash
sudo journalctl -u timelapse-download.service
```

### 7. Testing

You can manually trigger the service to test it:

```bash
sudo systemctl start timelapse-download.service
```

To check the status of your service after running it:

```bash
sudo systemctl status timelapse-download.service
```

For more detailed logs:

```bash
sudo journalctl -u timelapse-download.service
```

### Additional Tips

- If your script needs specific environment variables or dependencies, you can add them to the service file:

```
[Service]
Type=oneshot
User=your_username
Environment="PATH=/home/your_username/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/username/repos/timelapse/download_data.py
WorkingDirectory=/home/username/repos/timelapse
```

- You can also set up email notifications for failures by adding:

```
[Service]
...
OnFailure=status-email-user@%n.service
```
