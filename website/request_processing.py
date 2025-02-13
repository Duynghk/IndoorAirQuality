from website.fetch_data import fetch_data,fetch_device_data
from datetime import datetime
from Decrypt.DecryptPayload import decode_payload
import json


def get_device_keys(device_id):
    """
    Lấy application_session_key và group_identifier từ Firebase,
    sau đó chuyển đổi về dạng bytearray.
    """
    data = fetch_device_data(device_id)
    if not data:
        return None, None

    try:
        # Chuyển đổi chuỗi hex thành bytearray
        app_session_key = bytearray.fromhex(data["application_session_key"])
        group_id = bytearray.fromhex(data["group_identifier"])
        return app_session_key, group_id

    except KeyError as e:
        print(f"Missing key in response: {e}")
    except ValueError as ve:
        print(f"Invalid hex data: {ve}")

    return None, None  # Trả về None nếu có lỗi

def filter_sensor_data(device_id,raw_data,application_session_key, group_identifier):
    print("Start filter data")
    all_data = []
    timestamps = []
    node_time_data = {}
    for date, daily_data in raw_data.items():
        print(type(daily_data))
        for timestamp, json_string in daily_data.items():
            try:
                # Chuyển đổi chuỗi JSON thành dictionary
                json_data = json.loads(json_string)
                # Kiểm tra nếu device ID khớp với yêu cầu
                if json_data.get("device ID") == device_id:
                    data_hex = json_data["data"]
                    decoded_data = decode_payload(data_hex,application_session_key,group_identifier)
                    all_data.append(decoded_data)
                    timestamps.append(timestamp)
                    if 'nodes' in decoded_data:
                        for node in decoded_data['nodes']:
                            node_id = node['node_id']
                            node_timestamp = node.get('timestamp', timestamp)  # Lấy thời gian của node nếu có
                            if node_id not in node_time_data:
                                node_time_data[node_id] = []
                            node_time_data[node_id].append(node_timestamp)  
            except json.JSONDecodeError as e:
                print(f"Lỗi khi phân tích JSON tại {timestamp}: {e}")

    # Chọn các thông số cảm biến cần vẽ từ all_data
    co2_data = [entry['scd4x']['co2'] for entry in all_data if 'scd4x' in entry]
    temperature_data_scd4x = [entry['scd4x']['temperature'] for entry in all_data if 'scd4x' in entry]
    humidity_data_scd4x = [entry['scd4x']['humidity'] for entry in all_data if 'scd4x' in entry]

    temperature_data_bme680 = [entry['bme680']['temperature'] for entry in all_data if 'bme680' in entry]
    humidity_data_bme680 = [entry['bme680']['humidity'] for entry in all_data if 'bme680' in entry]
    pressure_data_bme680 = [entry['bme680']['pressure'] for entry in all_data if 'bme680' in entry]

    tvoc_data_sgp41 = [entry['sgp41']['TVOC'] for entry in all_data if 'sgp41' in entry]
    nox_data_sgp41 = [entry['sgp41']['nox'] for entry in all_data if 'sgp41' in entry]

    x_data_kxtj3 = [entry['kxtj3']['x'] for entry in all_data if 'kxtj3' in entry]
    y_data_kxtj3 = [entry['kxtj3']['y'] for entry in all_data if 'kxtj3' in entry]
    z_data_kxtj3 = [entry['kxtj3']['z'] for entry in all_data if 'kxtj3' in entry]

    visible_data_ltr = [entry['ltr']['visible_plus_ir'] for entry in all_data if 'ltr' in entry]
    infrared_data_ltr = [entry['ltr']['infrared'] for entry in all_data if 'ltr' in entry]

    battery_voltage_data = [entry['battery_voltage'] for entry in all_data]
    # Dữ liệu từ các node
    node_temperature_data = {}
    node_humidity_data = {}

    # Lấy thông tin nhiệt độ, độ ẩm và thời gian của từng node
    for entry in all_data:
        if 'nodes' in entry:
            for node in entry['nodes']:
                node_id = node['node_id']
                node_timestamp = node.get('timestamp', timestamp)  # Lấy thời gian của node
                if node_id not in node_temperature_data:
                    node_temperature_data[node_id] = {'timestamps': [], 'temperature': [], 'humidity': []}
                if node_id not in node_humidity_data:
                    node_humidity_data[node_id] = {'timestamps': [], 'temperature': [], 'humidity': []}
                node_temperature_data[node_id]['timestamps'].append(node_timestamp)
                node_temperature_data[node_id]['temperature'].append(node['temperature'])
                node_humidity_data[node_id]['timestamps'].append(node_timestamp)
                node_humidity_data[node_id]['humidity'].append(node['humidity'])

    co2_data = [entry['scd4x']['co2'] for entry in all_data if 'scd4x' in entry]
    temperature_data_scd4x = [entry['scd4x']['temperature'] for entry in all_data if 'scd4x' in entry]
    humidity_data_scd4x = [entry['scd4x']['humidity'] for entry in all_data if 'scd4x' in entry]

    temperature_data_bme680 = [entry['bme680']['temperature'] for entry in all_data if 'bme680' in entry]
    humidity_data_bme680 = [entry['bme680']['humidity'] for entry in all_data if 'bme680' in entry]
    pressure_data_bme680 = [entry['bme680']['pressure'] for entry in all_data if 'bme680' in entry]

    tvoc_data_sgp41 = [entry['sgp41']['TVOC'] for entry in all_data if 'sgp41' in entry]
    nox_data_sgp41 = [entry['sgp41']['nox'] for entry in all_data if 'sgp41' in entry]

    x_data_kxtj3 = [entry['kxtj3']['x'] for entry in all_data if 'kxtj3' in entry]
    y_data_kxtj3 = [entry['kxtj3']['y'] for entry in all_data if 'kxtj3' in entry]
    z_data_kxtj3 = [entry['kxtj3']['z'] for entry in all_data if 'kxtj3' in entry]

    visible_data_ltr = [entry['ltr']['visible_plus_ir'] for entry in all_data if 'ltr' in entry]
    infrared_data_ltr = [entry['ltr']['infrared'] for entry in all_data if 'ltr' in entry]

    battery_voltage_data = [entry['battery_voltage'] for entry in all_data]
    # Dữ liệu từ các node
    node_temperature_data = {}
    node_humidity_data = {}

    # # Lấy thông tin nhiệt độ, độ ẩm và thời gian của từng node
    # for entry in all_data:
    #     if 'nodes' in entry:
    #         for node in entry['nodes']:
    #             node_id = node['node_id']
    #             node_timestamp = node.get('timestamp', timestamp)  # Lấy thời gian của node
    #             if node_id not in node_temperature_data:
    #                 node_temperature_data[node_id] = {'timestamps': [], 'temperature': [], 'humidity': []}
    #             if node_id not in node_humidity_data:
    #                 node_humidity_data[node_id] = {'timestamps': [], 'temperature': [], 'humidity': []}
    #             node_temperature_data[node_id]['timestamps'].append(node_timestamp)
    #             node_temperature_data[node_id]['temperature'].append(node['temperature'])
    #             node_humidity_data[node_id]['timestamps'].append(node_timestamp)
    #             node_humidity_data[node_id]['humidity'].append(node['humidity'])

    return {
            "timestamps": timestamps,
            "co2_data": co2_data,
            "temperature_data_scd4x": temperature_data_scd4x,
            "humidity_data_scd4x": humidity_data_scd4x,
            "temperature_data_bme680": temperature_data_bme680,
            "humidity_data_bme680": humidity_data_bme680,
            "pressure_data_bme680": pressure_data_bme680,
            "tvoc_data_sgp41": tvoc_data_sgp41,
            "nox_data_sgp41": nox_data_sgp41,
            "x_data_kxtj3": x_data_kxtj3,
            "y_data_kxtj3": y_data_kxtj3,
            "z_data_kxtj3": z_data_kxtj3,
            "visible_data_ltr": visible_data_ltr,
            "infrared_data_ltr": infrared_data_ltr,
            "battery_voltage_data": battery_voltage_data,
            "node_temperature_data": node_temperature_data,
            "node_humidity_data": node_humidity_data
        }

def process_history_data(form_data):
    device_id = form_data["device_name"]
    start_date, start_time = form_data["start_date"].split("T")
    end_date, end_time = form_data["end_date"].split("T")           
    start_time += ":00"
    end_time += ":59"
    print(end_time)
    raw_data = fetch_data(date1=start_date,time1=start_time,date2=end_date,time2=end_time,device_name=device_id)
    print(type(raw_data))
    app_session_key, group_id = get_device_keys(device_id)
    sensors_data = filter_sensor_data(device_id,raw_data,app_session_key, group_id)
    return sensors_data

def find_latest_device_data(firebase_response, device_id):
    """
    Tìm dữ liệu mới nhất của một thiết bị dựa trên device_id.
    Duyệt từ cuối lên để tối ưu tốc độ.
    """
    for key, value in reversed(firebase_response.items()):
        value_dict = json.loads(value)
        if value_dict.get("device ID") == device_id:
            return key, value  # Trả về key và dữ liệu tương ứng

    return None, None  # Nếu không tìm thấy

def process_live_monitoring(device_id,application_session_key,group_identifier):
    date = datetime.today().date()  # Lấy ngày hiện tại dưới dạng YYYY-MM-DD
    firebase_response = fetch_data(date1=date,device_name=device_id)
    # Lọc dữ liệu theo device_id
    last_key,last_value = find_latest_device_data(firebase_response, device_id)

    # last_key, last_value = next(reversed(firebase_response.items()))
    last_value = json.loads(last_value)
    sensors_data = decode_payload(last_value["data"],application_session_key,group_identifier)
    return sensors_data
