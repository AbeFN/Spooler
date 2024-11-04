from flask import Flask, request, jsonify
import subprocess
from vcenter_logic import connect_to_vcenter, create_server
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow CORS for all routes

@app.route('/')
def home():
    return "Welcome to the Spooler2 API!"

@app.route('/api/create_server/windows', methods=['POST'])
def create_windows_server():
    # your existing windows server creation code here
    pass

@app.route('/api/create_server/linux', methods=['POST'])
def create_linux_server():
    # your existing linux server creation code here
    pass

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/api/create_server/windows', methods=['POST'])
def create_windows_server():
    data = request.json
    powershell_command = [
        "powershell.exe",
        "-ExecutionPolicy", "Bypass",
        "-File", "backend/powershell_script.ps1",
        "-vCenter", data["vcenter_ip"],
        "-Username", data["username"],
        "-Password", data["password"],
        "-TemplateName", data["template_name"],
        "-NewVMName", data["vm_name"]
    ]
    result = subprocess.run(powershell_command, capture_output=True, text=True)
    if result.returncode == 0:
        return jsonify({"status": "success", "message": "Windows server created"})
    else:
        return jsonify({"status": "error", "message": result.stderr}), 500

@app.route('/api/create_server/linux', methods=['POST'])
def create_linux_server():
    data = request.json
    si = connect_to_vcenter(data["vcenter_ip"], data["username"], data["password"])
    if si:
        try:
            create_server(si, data["vm_name"], data["datacenter_name"], data["cluster_name"],
                          data["datastore_name"], data["template_name"], data["num_cpus"],
                          data["ram_mb"], data["network_name"])
            return jsonify({"status": "success", "message": "Linux server created"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Failed to connect to vCenter"}), 500

if __name__ == '__main__':
    app.run(debug=True)
