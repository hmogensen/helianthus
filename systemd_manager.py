import subprocess
import sys
import glob
import re
from pathlib import Path

class SystemdManager:
    def __init__(self):
        self.service_pattern = "timelapse-*.service"
        self.service_dir = "/etc/systemd/system/"
    
    def get_timelapse_services(self):
        try:
            services = glob.glob(f"{self.service_dir}{self.service_pattern}")
            if not services:
                user_service_dir = Path.home() / ".config/systemd/user/"
                services = glob.glob(f"{user_service_dir}{self.service_pattern}")
            
            return [Path(service).stem for service in services]
        except Exception as e:
            print(f"Error finding services: {e}")
            return []
    
    def get_service_status(self, service_name):
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service_name],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"
    
    def start_service(self, service_name):
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "start", service_name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"Started {service_name}")
            else:
                print(f"Failed to start {service_name}: {result.stderr}")
        except Exception as e:
            print(f"Error starting service: {e}")
    
    def stop_service(self, service_name):
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "stop", service_name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"Stopped {service_name}")
            else:
                print(f"Failed to stop {service_name}: {result.stderr}")
        except Exception as e:
            print(f"Error stopping service: {e}")
    
    def parse_service_file(self, service_name):
        service_file = f"{self.service_dir}{service_name}"
        
        if not Path(service_file).exists():
            user_service_dir = Path.home() / ".config/systemd/user/"
            service_file = f"{user_service_dir}{service_name}"
        
        try:
            with open(service_file, 'r') as f:
                content = f.read()
            
            exec_start_match = re.search(r'ExecStart=(.+)', content)
            if not exec_start_match:
                print(f"Could not find ExecStart in {service_name}")
                return
            
            exec_start = exec_start_match.group(1)
            
            parts = exec_start.split()
            if len(parts) < 4:
                print(f"Invalid ExecStart format in {service_name}")
                return
            
            python_path = parts[0]
            script_path = parts[1]
            camera_config = parts[2] if len(parts) > 2 else ""
            output_name = parts[3] if len(parts) > 3 else ""
            additional_args = parts[4:] if len(parts) > 4 else []
            
            print(f"Service: {service_name}")
            print(f"Python: {python_path}")
            print(f"Script: {script_path}")
            print(f"Camera Config: {camera_config}")
            print(f"Output Name: {output_name}")
            if additional_args:
                print(f"Additional Args: {' '.join(additional_args)}")
            
            desc_match = re.search(r'Description=(.+)', content)
            if desc_match:
                print(f"Description: {desc_match.group(1)}")
            
            user_match = re.search(r'User=(.+)', content)
            if user_match:
                print(f"User: {user_match.group(1)}")
            
            workdir_match = re.search(r'WorkingDirectory=(.+)', content)
            if workdir_match:
                print(f"Working Directory: {workdir_match.group(1)}")
                
        except FileNotFoundError:
            print(f"Service file not found: {service_file}")
        except Exception as e:
            print(f"Error parsing service file: {e}")
    
    def list_services_status(self):
        services = self.get_timelapse_services()
        
        if not services:
            print("No timelapse services found")
            return
        
        print("Timelapse Services Status:")
        print("-" * 40)
        
        for service in services:
            status = self.get_service_status(service)
            service_id = service.replace("timelapse-", "").replace(".service", "")
            print(f"{service_id:<20} {status}")

def main():
    if len(sys.argv) < 2:
        print("Usage: systemd_manager.py <command> [service-id]")
        print("Commands:")
        print("  status                    - List all services and their status")
        print("  start <service-id>        - Start service (e.g., reolink-lowres)")
        print("  stop <service-id>         - Stop service")
        print("  parse <service-id>        - Parse service file and show config")
        sys.exit(1)
    
    manager = SystemdManager()
    command = sys.argv[1]
    
    if command != "status":
        service_name = f"timelapse-{sys.argv[2]}.service"
    if command == "status":
        manager.list_services_status()
    elif command == "start":
        manager.start_service(service_name)
    elif command == "stop":
        manager.stop_service(service_name)
    elif command == "parse":
        manager.parse_service_file(service_name)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()