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
  ipv4.addresses 192.168.1.XXX/24 \
  ipv4.gateway "" \
  ipv4.dns ""
```

*Note: Replace `YOUR_ETHERNET_INTERFACE` with your actual interface name (e.g., `eth0` or `enp3s0`)., and 192.168.1.XXX with the static IP address of device*

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
ping 192.168.1.XXX  # Replace with your camera's IP
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
