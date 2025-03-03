from flask import Blueprint, render_template, request, jsonify, redirect
from website.request_processing import *
from flask_socketio import SocketIO

views = Blueprint('view', __name__)

@views.route('/')
def home():
    return redirect("/live-monitoring")

# Route để lấy dữ liệu từ Firebase và hiển thị trên web
@views.route('/get-history', methods=['POST','GET'])
def get_history():
    if request.method == 'POST':
        form_data = request.json
        print(form_data)
        try:
            sensors_data = process_history_data(form_data)
            print("Get history")
            print(type(sensors_data))
            data = {
                "status": "success",
                "message": "Data received successfully",
                "sensors_data": sensors_data,
                "author": "nguyenhoangkhanhduy030903@gmail.com",
                }
            return data
        except:
            data = {
                "status": "error",
                "message": "Data Error",
                "data": {"steps": [],"result": {},},
                "author": "nguyenhoangkhanhduy030903@gmail.com",
                }
            return data
    else:
        return render_template("history.html")

@views.route('/live-monitoring', methods=["POST","GET"])
def live_monitoring_page():
    return render_template("live_monitoring.html")

@views.route('/api/live-monitoring-data', methods=["POST","GET"])
def load_live_monitoring():
    try:
        device_id = request.args.get("device_id", None)
        if not device_id or device_id.lower() == "null":
            return jsonify({"status": "error", "message": "Device ID is required"}), 400
        app_session_key, group_id = get_device_keys(device_id)
        sensors_data = process_live_monitoring(device_id,app_session_key,group_id)
        return sensors_data

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
