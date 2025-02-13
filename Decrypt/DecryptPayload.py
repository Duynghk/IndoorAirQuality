import json
import struct
import numpy as np
from Decrypt.AES128_Encrypt import encrypt_payload

def decode_node_data(data,ptr,application_session_key,group_identifier,timestamp=0, direction = 0x00, frame_counter = 0):
    # Bước 8: Giải mã dữ liệu của các nodes
    nodes = []
    while ptr < len(data):
        node_id = data[ptr]
        device_address = group_identifier + bytearray([node_id])
        payload = data[ptr + 1:ptr + 5]  
        node_decoded_data = encrypt_payload(bytearray(payload), len(payload), application_session_key, 
                                            device_address, direction, frame_counter)
        # Unpack dữ liệu sau khi giải mã
        node_data = struct.unpack('>HH', node_decoded_data)
        ptr += 5          
        if node_data[1]>1000 or node_data[1]==0 or node_data[0]==0 or node_data[0]>1000:
            continue
        nodes.append({
            "node_id": node_id,
            "timestamp": timestamp,
            "temperature": node_data[0]/10,
            "humidity": node_data[1]/10
        })
    return nodes


def decode_payload(data_hex,application_session_key,group_identifier):
    # Loại bỏ dấu cách và chuyển chuỗi HEX thành chuỗi byte
    data = bytes.fromhex(data_hex.replace(" ", ""))
    
    ptr = 0

    # Bước 2: Giải mã dữ liệu từ SCD4x
    scd4x_format = '<HHff'  # uint16, float, float
    scd4x_size = struct.calcsize(scd4x_format)
    # print(f"SCD4x raw data: {data[ptr:ptr + scd4x_size].hex()}")
    scd4x_data = struct.unpack(scd4x_format, data[ptr:ptr + scd4x_size])
    scd4x = {
        "co2": scd4x_data[0],
        "temperature": scd4x_data[2],
        "humidity": scd4x_data[3]
    }
    # print(f"SCD4x Data: {scd4x}")
    ptr += scd4x_size
    # Bước 3: Giải mã dữ liệu từ BME680
    bme680_format = '<ffff'  # 4 floats
    bme680_size = struct.calcsize(bme680_format)
    # print(f"BME680 raw data: {data[ptr:ptr + bme680_size].hex()}")
    bme680_data = struct.unpack(bme680_format, data[ptr:ptr + bme680_size])
    bme680 = {
        "temperature": bme680_data[0],
        "humidity": bme680_data[1],
        "pressure": bme680_data[2],
        "gas_resistance": bme680_data[3]
    }
    # print(f"BME680 Data: {bme680}")
    ptr += bme680_size

    # Bước 4: Giải mã dữ liệu từ SGP41
    sgp41_format = '<HH'  # 2 uint16
    sgp41_size = struct.calcsize(sgp41_format)
    # print(f"SGP41 raw data: {data[ptr:ptr + sgp41_size].hex()}")
    sgp41_data = struct.unpack(sgp41_format, data[ptr:ptr + sgp41_size])
    sgp41 = {
        "TVOC": sgp41_data[0],
        "nox": sgp41_data[1]
    }
    # print(f"SGP41 Data: {sgp41}")
    ptr += sgp41_size

    # Bước 5: Giải mã dữ liệu từ KXTJ3
    kxtj3_format = '<fff'  # 3 floats
    kxtj3_size = struct.calcsize(kxtj3_format)
    # print(f"KXTJ3 raw data: {data[ptr:ptr + kxtj3_size].hex()}")
    kxtj3_data = struct.unpack(kxtj3_format, data[ptr:ptr + kxtj3_size])
    kxtj3 = {
        "x": kxtj3_data[0],
        "y": kxtj3_data[1],
        "z": kxtj3_data[2]
    }
    # print(f"KXTJ3 Data: {kxtj3}")
    ptr += kxtj3_size

    # Bước 6: Giải mã dữ liệu từ LTR
    ltr_format = '<HH'  # 2 uint16
    ltr_size = struct.calcsize(ltr_format)
    # print(f"LTR raw data: {data[ptr:ptr + ltr_size].hex()}")
    ltr_data = struct.unpack(ltr_format, data[ptr:ptr + ltr_size])
    ltr = {
        "visible_plus_ir": ltr_data[0],
        "infrared": ltr_data[1]
    }
    # print(f"LTR Data: {ltr}")
    ptr += ltr_size

    # Bước 7: Giải mã điện áp pin và trạng thái nguồn
    battery_voltage_format = '<I'  # int
    battery_voltage_size = struct.calcsize(battery_voltage_format)
    # print(f"Battery voltage raw data: {data[ptr:ptr + battery_voltage_size].hex()}")
    battery_voltage = (struct.unpack(battery_voltage_format, data[ptr:ptr + battery_voltage_size])[0])/1000
    # battery_voltage = {"battery_voltage": battery_voltage_data[0]}

    # print(f"Battery Voltage: {battery_voltage}")
    ptr += battery_voltage_size
    
    # power_status11=[]
    # print(f"Power status raw data: {data[ptr:ptr + 1].hex()}")
    power_status = struct.unpack('<?', data[ptr:ptr + 1])[0]  # bool
    # power_status11.append({"power_status": power_status11[0]})
    # print(f"Power Status: {power_status11}")
    ptr += 1

    # Bước 8: Giải mã dữ liệu của các nodes
    nodes = decode_node_data(data,ptr,application_session_key,group_identifier) 
    # Tạo dictionary chứa toàn bộ dữ liệu
    decoded_data = {
        "scd4x": scd4x,
        "bme680": bme680,
        "sgp41": sgp41,
        "kxtj3": kxtj3,
        "ltr": ltr,
        "battery_voltage": battery_voltage,
        "power_status": power_status,
        "nodes": nodes
    }

    return decoded_data