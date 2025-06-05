# Configuring Passwordless Sudo for Timelapse Services

## Overview

To allow the Timelapse SystemD Manager web interface to start and stop services without password prompts, you need to configure passwordless sudo access for specific systemctl commands.

## Why This Is Needed

The web application runs systemctl commands to manage timelapse services:
```bash
sudo systemctl start timelapse-camera-name.service
sudo systemctl stop timelapse-camera-name.service
```

By default, these commands require password authentication, which fails in a web environment. This guide shows how to grant passwordless sudo access for only these specific commands.

## Setup Instructions

### Step 1: Open the Sudoers File

⚠️ **Important**: Always use `visudo` to edit sudoers files. This command validates syntax before saving, preventing you from accidentally locking yourself out of sudo access.

```bash
sudo visudo
```

### Step 2: Add the Passwordless Rule

Add the following line at the end of the file (replace `your_username` with your actual username):

```
your_username ALL=(ALL) NOPASSWD: /usr/bin/systemctl start timelapse-*, /usr/bin/systemctl stop timelapse-*
```

**For Raspberry Pi users**, the default username is typically `pi`:
```
pi ALL=(ALL) NOPASSWD: /usr/bin/systemctl start timelapse-*, /usr/bin/systemctl stop timelapse-*
```

### Step 3: Save and Exit

- In nano (default editor): Press `Ctrl+X`, then `Y`, then `Enter`
- In vim: Press `Esc`, type `:wq`, then `Enter`

### Step 4: Test the Configuration

Test that the passwordless sudo is working:

```bash
# These commands should now work without prompting for a password
sudo systemctl status timelapse-your-camera-name.service
sudo systemctl start timelapse-your-camera-name.service
sudo systemctl stop timelapse-your-camera-name.service
```

## What This Rule Does

The sudoers rule breaks down as follows:

- `your_username` - The user account that can run these commands
- `ALL=(ALL)` - Can run on any host as any user (standard for single-user systems)
- `NOPASSWD:` - Don't require password authentication
- `/usr/bin/systemctl start timelapse-*` - Allow starting any service with name matching `timelapse-*`
- `/usr/bin/systemctl stop timelapse-*` - Allow stopping any service with name matching `timelapse-*`

## Security Considerations

✅ **Secure**: This configuration only grants access to start/stop timelapse services
✅ **Limited scope**: Uses wildcards to match only `timelapse-*` services
✅ **Specific commands**: Only allows `start` and `stop` operations

❌ **Avoid**: Don't use broad rules like `ALL ALL=(ALL) NOPASSWD: ALL` which would grant passwordless access to everything

## Troubleshooting

### "Command not found" errors
If you get command not found errors, verify the full path to systemctl:
```bash
which systemctl
```
The output should be `/usr/bin/systemctl`. If different, update the sudoers rule accordingly.

### Permission still denied
1. Verify your username is correct:
   ```bash
   whoami
   ```
2. Check the sudoers file syntax:
   ```bash
   sudo visudo -c
   ```
3. Ensure there are no conflicting rules earlier in the file

### Web interface still shows password errors
1. Restart the web application after making sudoers changes
2. Check that your service names match the pattern `timelapse-*`
3. Verify the web app is running under the same user account you configured

## Alternative: User Services

If you prefer not to modify sudoers, consider running your timelapse services as user services instead of system services:

```bash
# Install as user service (no sudo required)
systemctl --user enable timelapse-camera.service
systemctl --user start timelapse-camera.service
systemctl --user stop timelapse-camera.service
```

Then modify the web application to use `systemctl --user` commands instead of `sudo systemctl`.