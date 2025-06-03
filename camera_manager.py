#!/usr/bin/env python3
import toml
import keyring
from tabulate import tabulate

camera_settings_path = "cameras.toml"

def load_cameras(toml_file):
    with open(toml_file, 'r') as f:
        settings = toml.load(f)
    return settings

def check_credentials_saved(cam_id):
    password = keyring.get_password("camera_pass", cam_id)
    return "Yes" if password else "No"

def list_cameras(toml_file=camera_settings_path):
    try:
        cameras = load_cameras(toml_file)
        
        camera_list = []
        for cam_id, camera_config in cameras.items():
            # Skip nested configurations (like highres, lowres, etc.)
            if isinstance(camera_config, dict) and 'ip' in camera_config:
                ip = camera_config['ip']
                credentials_saved = check_credentials_saved(cam_id)
                camera_list.append([cam_id, ip, credentials_saved])
        
        headers = ["Camera Name", "IP Address", "Credentials Saved"]
        print(tabulate(camera_list, headers=headers, tablefmt="grid"))
        
    except FileNotFoundError:
        print(f"Error: {toml_file} not found")
    except Exception as e:
        print(f"Error reading configuration: {e}")

def save_credentials(cam_id):
    import getpass
    
    try:
        print(f"Enter credentials for {cam_id}:")
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        
        if username and password:
            keyring.set_password("camera_pass", cam_id, password)
            keyring.set_password("camera_usernames", cam_id, username)
            print(f"Credentials saved for {cam_id}")
        else:
            print("Username or password cannot be empty")
    except KeyboardInterrupt:
        print("\nCancelled by user")
    except Exception as e:
        print(f"Error saving credentials: {e}")

def get_credentials(cam_id):
    try:
        username = keyring.get_password("camera_usernames", cam_id)
        password = keyring.get_password("camera_pass", cam_id)
        return username, password
    except Exception as e:
        print(f"Error retrieving credentials: {e}")
        return None, None

def delete_credentials(cam_id):
    try:
        keyring.delete_password("camera_usernames", cam_id)
        keyring.delete_password("camera_pass", cam_id)
        print(f"Credentials deleted for {cam_id}")
    except Exception as e:
        print(f"Error deleting credentials: {e}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  camera_manager.py list [toml_file]")
        print("  camera_manager.py save <camera_id>")
        print("  camera_manager.py delete <camera_id>")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        toml_file = sys.argv[2] if len(sys.argv) > 2 else camera_settings_path
        list_cameras(toml_file)
    
    elif command == "save" and len(sys.argv) == 3:
        cam_id = sys.argv[2]
        save_credentials(cam_id)
    
    elif command == "delete" and len(sys.argv) == 3:
        cam_id = sys.argv[2]
        delete_credentials(cam_id)
    
    else:
        print("Invalid command or arguments")

if __name__ == "__main__":
    main()