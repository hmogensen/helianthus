#!/usr/bin/env python3
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import subprocess
import glob
import re
from pathlib import Path

app = Flask(__name__)

filter_services = ["reolink-lowres", "tapo-lowres"]
service_ext = "service"


class SystemdManager:
    def __init__(self):
        self.service_pattern = f"timelapse-*.{service_ext}"
        self.service_dir = "/etc/systemd/system/"

    def get_timelapse_services(self):
        try:
            services = glob.glob(f"{self.service_dir}{self.service_pattern}")
            return [
                Path(service).stem
                for service in services
                if any([s in service for s in filter_services])
            ]
        except Exception as e:
            print(f"Error finding services: {e}")
            return []

    def get_service_status(self, service_name):
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service_name], capture_output=True, text=True
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def start_service(self, service_name):
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "start", service_name],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return True, f"Started {service_name}"
            else:
                return False, f"Failed to start {service_name}: {result.stderr}"
        except Exception as e:
            return False, f"Error starting service: {e}"

    def stop_service(self, service_name):
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "stop", service_name],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return True, f"Stopped {service_name}"
            else:
                return False, f"Failed to stop {service_name}: {result.stderr}"
        except Exception as e:
            return False, f"Error stopping service: {e}"

    def parse_service_file(self, service_name):
        service_file = f"{self.service_dir}{service_name}.{service_ext}"

        try:
            with open(service_file, "r") as f:
                content = f.read()

            info = {"service": service_name}

            exec_start_match = re.search(r"ExecStart=(.+)", content)
            if not exec_start_match:
                return {"error": f"Could not find ExecStart in {service_name}"}

            exec_start = exec_start_match.group(1)
            parts = exec_start.split()
            if len(parts) < 4:
                return {"error": f"Invalid ExecStart format in {service_name}"}

            info.update(
                {
                    "python_path": parts[0],
                    "script_path": parts[1],
                    "camera_config": parts[2] if len(parts) > 2 else "",
                    "output_name": parts[3] if len(parts) > 3 else "",
                    "additional_args": parts[4:] if len(parts) > 4 else [],
                }
            )

            # Extract other info
            for pattern, key in [
                (r"Description=(.+)", "description"),
                (r"User=(.+)", "user"),
                (r"WorkingDirectory=(.+)", "working_directory"),
            ]:
                match = re.search(pattern, content)
                if match:
                    info[key] = match.group(1)

            return info
        except FileNotFoundError:
            return {"error": f"Service file not found: {service_file}"}
        except Exception as e:
            return {"error": f"Error parsing service file: {e}"}

    def get_all_services_info(self):
        services = self.get_timelapse_services()
        services_info = []

        for service in services:
            service_id = service.replace("timelapse-", "").replace(
                f".{service_ext}", ""
            )
            status = self.get_service_status(service)
            info = self.parse_service_file(service)

            services_info.append(
                {
                    "service_id": service_id,
                    "service_name": service,
                    "status": status,
                    "info": info,
                }
            )

        return services_info


manager = SystemdManager()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Timelapse SystemD Manager</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .service-card {
            border: 1px solid #ddd;
            margin: 10px 0;
            padding: 15px;
            border-radius: 5px;
            background: #fafafa;
        }
        .service-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .status {
            padding: 5px 10px;
            border-radius: 3px;
            color: white;
            font-weight: bold;
        }
        .status.active { background-color: #28a745; }
        .status.inactive { background-color: #dc3545; }
        .status.unknown { background-color: #6c757d; }
        .buttons {
            margin: 10px 0;
        }
        .btn {
            padding: 8px 16px;
            margin: 2px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .btn-start { background-color: #28a745; color: white; }
        .btn-stop { background-color: #dc3545; color: white; }
        .btn-info { background-color: #17a2b8; color: white; }
        .btn:hover { opacity: 0.8; }
        .service-info {
            background: #e9ecef;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            font-size: 0.9em;
        }
        .refresh-btn {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .message {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .message.success { background-color: #d4edda; color: #155724; }
        .message.error { background-color: #f8d7da; color: #721c24; }
        @media (max-width: 768px) {
            .service-header { flex-direction: column; align-items: flex-start; }
            .buttons { margin-top: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎥 Timelapse SystemD Manager</h1>
        
        {% if message %}
        <div class="message {{ message_type }}">{{ message }}</div>
        {% endif %}
        
        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Status</button>
        
        {% for service in services %}
        <div class="service-card">
            <div class="service-header">
                <h3>📹 {{ service.service_id }}</h3>
                <span class="status {{ service.status }}">{{ service.status.upper() }}</span>
            </div>
            
            <div class="buttons">
                {% if service.status != 'active' %}
                <a href="/start/{{ service.service_id }}" class="btn btn-start">▶️ Start</a>
                {% endif %}
                {% if service.status == 'active' %}
                <a href="/stop/{{ service.service_id }}" class="btn btn-stop">⏹️ Stop</a>
                {% endif %}
                <button class="btn btn-info" onclick="toggleInfo('{{ service.service_id }}')">ℹ️ Info</button>
            </div>
            
            <div id="info-{{ service.service_id }}" class="service-info" style="display: none;">
                {% if service.info.error %}
                    <strong>Error:</strong> {{ service.info.error }}
                {% else %}
                    <strong>Service:</strong> {{ service.info.service }}<br>
                    {% if service.info.description %}
                    <strong>Description:</strong> {{ service.info.description }}<br>
                    {% endif %}
                    {% if service.info.camera_config %}
                    <strong>Camera Config:</strong> {{ service.info.camera_config }}<br>
                    {% endif %}
                    {% if service.info.output_name %}
                    <strong>Output Name:</strong> {{ service.info.output_name }}<br>
                    {% endif %}
                    {% if service.info.additional_args %}
                    <strong>Additional Args:</strong> {{ service.info.additional_args | join(' ') }}<br>
                    {% endif %}
                    {% if service.info.user %}
                    <strong>User:</strong> {{ service.info.user }}<br>
                    {% endif %}
                    {% if service.info.working_directory %}
                    <strong>Working Directory:</strong> {{ service.info.working_directory }}
                    {% endif %}
                {% endif %}
            </div>
        </div>
        {% endfor %}
        
        {% if not services %}
        <p>No timelapse services found.</p>
        {% endif %}
    </div>
    
    <script>
        function toggleInfo(serviceId) {
            const info = document.getElementById('info-' + serviceId);
            info.style.display = info.style.display === 'none' ? 'block' : 'none';
        }
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    services = manager.get_all_services_info()
    message = request.args.get("message")
    message_type = request.args.get("type", "success")

    return render_template_string(
        HTML_TEMPLATE, services=services, message=message, message_type=message_type
    )


@app.route("/start/<service_id>")
def start_service(service_id):
    service_name = f"timelapse-{service_id}.{service_ext}"
    success, message = manager.start_service(service_name)
    message_type = "success" if success else "error"
    return redirect(url_for("index", message=message, type=message_type))


@app.route("/stop/<service_id>")
def stop_service(service_id):
    service_name = f"timelapse-{service_id}.{service_ext}"
    success, message = manager.stop_service(service_name)
    message_type = "success" if success else "error"
    return redirect(url_for("index", message=message, type=message_type))


@app.route("/api/status")
def api_status():
    """JSON API endpoint for status"""
    services = manager.get_all_services_info()
    return jsonify(services)


if __name__ == "__main__":
    print("Starting Timelapse SystemD Manager Web Interface")
    print("Access from any device on your network at:")
    print("http://YOUR_RASPBERRY_PI_IP:5000")
    print("\nTo find your IP address, run: hostname -I")

    # Run on all interfaces so it's accessible from other devices
    app.run(host="0.0.0.0", port=5000, debug=False)
