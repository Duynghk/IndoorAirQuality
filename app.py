from website import create_app
from flask_mqtt import Mqtt
import json
import csv

app = create_app()


app.config['MQTT_BROKER_URL'] = "eu1.cloud.thethings.network"  # URL của MQTT broker
app.config['MQTT_BROKER_PORT'] = 1883  # Cổng của MQTT broker
app.config['MQTT_USERNAME'] = "rfthing-smart-building@ttn" # Tên đăng nhập, nếu có
app.config['MQTT_PASSWORD'] = "NNSXS.DUSSDAT62FDL3XOZN7CU2SDRDR43OGNPODFBEKA.P2KSQYYNHDZGWFFEJTMCLQRCPDV5VZTUWRWX6TD4B6774CRVPPMA"  # Mật khẩu, nếu có
app.config['MQTT_KEEPALIVE'] = 60  # Thời gian giữ kết nối
app.config['MQTT_TLS_ENABLED'] = False  # Kích hoạt TLS nếu cần
mqtt = Mqtt(app)

# Đăng ký topic và xử lý tin nhắn
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('#')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    json_data = json.loads(message.payload.decode('utf-8'))
    try:
        payload = json_data["uplink_message"]["frm_payload"]
        time = json_data["uplink_message"]["rx_metadata"][0]["time"]

        # Ghi dữ liệu vào file CSV
        with open("LoraButtonBatteryLife.csv", "a", newline='') as csvfile:
            fieldnames = ["time", "payload"]  # Các trường dữ liệu
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Nếu file chưa có dữ liệu, ghi tiêu đề vào
            csvfile.seek(0, 2)  # Di chuyển con trỏ đến cuối file
            if csvfile.tell() == 0:
                writer.writeheader()

            # Ghi dữ liệu vào file
            writer.writerow({"time": time, "payload": payload})
    except:
        print("Payload error")


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port='5000')