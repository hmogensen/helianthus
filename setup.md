# Timelapse Application Setup

## System Boot Configuration

Before setting up the timelapse application, ensure your system is configured to automatically provide SSH access and network connectivity at boot:

1. **Install and Enable SSH Server**
   ```bash
   sudo apt install openssh-server
   sudo systemctl enable ssh
   sudo systemctl start ssh
   ```

2. **Configure Network to Connect at Boot**
   Ensure your connection is set to auto-connect:
  
3. **Set Up Static IP or DHCP Reservation** (Recommended)
   - Configure your router to assign a consistent IP to your device, or set up a static IP on your device

## Automatic Restart with Systemd

To ensure the timelapse application restarts automatically after a device reboot and to enable easy management via SSH, follow these steps:

### 1. Create a systemd Service File

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

### 2. Enable and Start the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable timelapse-camera.service
sudo systemctl start timelapse-camera.service
```

### 3. Managing via SSH

You can manage the application remotely with these commands:

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

### 4. Multiple Camera Setup

If you need to run the application for multiple cameras, create separate service files for each:

```bash
sudo nano /etc/systemd/system/timelapse-garden.service
sudo nano /etc/systemd/system/timelapse-frontdoor.service
```

Each service file should have appropriate camera parameters:

```
ExecStart=/usr/bin/python3 /path/to/timelapse/directory/timelapse.py axis-cam1 garden --interval 300
```

### 5. System Startup Security Considerations

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

### 6. Prerequisites and Troubleshooting

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
# Stream data over PoE injector from network camera to Raspbery Pi with Ubuntu OS

## Enabling SSH on Ubuntu

To enable SSH on Ubuntu, you'll need to install the OpenSSH server and then configure it. Here's how to do it:

1. First, update your package lists:
```bash
sudo apt update
```

2. Install the OpenSSH server:
```bash
sudo apt install openssh-server -y
```

3. Verify that SSH is running:
```bash
sudo systemctl status ssh
```

4. If it's not running, start the SSH service:
```bash
sudo systemctl start ssh
```

5. Enable SSH to start on boot:
```bash
sudo systemctl enable ssh
```

6. Configure the firewall to allow SSH connections:
```bash
sudo ufw allow ssh
```

7. If you need to configure SSH further, edit the SSH configuration file:
```bash
sudo nano /etc/ssh/sshd_config
```

8. After making any changes to the configuration, restart the SSH service:
```bash
sudo systemctl restart ssh
```

That's it! SSH should now be enabled on your Ubuntu system. You can connect to it from another machine using:
```bash
ssh username@your_ubuntu_ip
```

Replace "username" with your actual username and "your_ubuntu_ip" with the IP address of your Ubuntu machine.

## Switch to static Wifi IP

# Setting Static IP on Raspberry Pi 4 Ubuntu (Headless)

This guide provides instructions for setting a static IP address on a Raspberry Pi 4 running Ubuntu in headless mode (without GUI).

## Using NetworkManager CLI (nmcli)

NetworkManager is the default network management tool on Ubuntu. Here's how to configure a static IP address using the command line:

### 1. List Available Network Connections

First, identify your WiFi connection name:

```bash
nmcli connection show
```

Look for your WiFi connection in the output. It will typically have a "wifi" type.

### 2. Set Static IP Configuration

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

### 3. Apply the Changes

Restart the network connection to apply the changes:
(Not if connected via SSH, as you will lose the connection!)

```bash
sudo nmcli connection down "Your-WiFi-Connection-Name"
sudo nmcli connection up "Your-WiFi-Connection-Name"
```

### 4. Verify the Configuration

Check that your new IP address has been applied:

```bash
ip addr show
```

You should see your static IP address assigned to your WiFi interface (usually wlan0).

## Additional Information

### Finding Your Router's IP Address

If you don't know your router's IP address, you can usually find it with:

```bash
ip route | grep default
```

### Troubleshooting

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

### Making the Configuration Persistent

The configuration set with nmcli will persist across reboots. If you need to make additional changes, simply repeat the modification commands.

# Dual Network Setup: PoE Camera + WiFi Internet
## For Headless Ubuntu with Network Manager

This guide explains how to configure a headless Ubuntu system to simultaneously:
- Connect to a PoE network camera via Ethernet
- Maintain WiFi connectivity for internet access

## Hardware Setup

1. Connect your network camera to the PoE injector's "Data+Power" port
2. Connect the "Data In" port of the PoE injector to your computer's Ethernet port
3. Keep your computer's WiFi connection active for internet access

## Software Configuration with Network Manager

### 1. Identify Network Interfaces

First, identify your network interfaces:

```bash
nmcli device status
```

Note your Ethernet interface name (typically `eth0` or `enp3s0`) and WiFi interface name (typically `wlan0` or `wlp2s0`).

### 2. Configure Ethernet with Static IP

Create a new connection profile for your Ethernet interface:

```bash
sudo nmcli connection add \
  type ethernet \
  con-name "POE-Camera" \
  ifname YOUR_ETHERNET_INTERFACE \
  ipv4.method manual \
  ipv4.addresses 192.168.1.XXX0/24 \
  ipv4.gateway "" \
  ipv4.dns ""
```

*Note: Replace `YOUR_ETHERNET_INTERFACE` with your actual interface name (e.g., `eth0` or `enp3s0`).*

### 3. Prevent Ethernet from Taking Over Default Route

To ensure your WiFi remains the default internet connection:

```bash
sudo nmcli connection modify "POE-Camera" ipv4.never-default true
```

### 4. Enable Auto-Connect for Persistence

Make the configuration persistent across reboots:

```bash
sudo nmcli connection modify "POE-Camera" connection.autoconnect yes
```

### 5. Activate the Connection

Apply and activate the new connection:

```bash
sudo nmcli connection up "POE-Camera"
```

### 6. Verify WiFi Connectivity

Check that your WiFi connection is still active:

```bash
nmcli connection show --active
```

### 7. Connect WiFi (if needed)

If your WiFi isn't connected:

```bash
# List available WiFi networks
nmcli device wifi list

# Connect to your WiFi
sudo nmcli device wifi connect YOUR_SSID password YOUR_PASSWORD
```

*Note: Replace `YOUR_SSID` and `YOUR_PASSWORD` with your actual WiFi credentials.*

## Verification

### 1. Check Network Interfaces

```bash
ip addr
```

You should see both interfaces with their respective IP addresses.

### 2. Verify Routing Table

```bash
ip route
```

Confirm that your WiFi interface is used for the default route.

### 3. Test Camera Connection

```bash
ping 192.168.1.XXX8  # Replace with your camera's IP
```

### 4. Test Internet Connectivity

```bash
ping 8.8.8.8
```

## Troubleshooting

If you encounter issues:

1. **Cannot connect to camera**: Verify the camera's IP address and ensure it's in the same subnet as your Ethernet interface.

2. **No internet access**: Check that your WiFi is still connected and that the Ethernet connection hasn't taken over as the default route.

3. **Connection drops after reboot**: Verify both connections are set to auto-connect.

4. **Interface names changed**: If your interface names change after a reboot, consider setting up persistent interface names in Ubuntu.
