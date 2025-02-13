from datetime import datetime, timedelta
from models.communicate_database import firebase_request

def fetch_data(date1,time1='00:00:00',date2=None,time2="23:59:59",device_name="RF-SB1"):
    try:
        if not date2:  # Nếu chỉ có một ngày
            return firebase_request(f'/{date1}')
        
        date_format = "%Y-%m-%d"
        start_date = datetime.strptime(date1, date_format)
        end_date = datetime.strptime(date2, date_format)
        
        data = {}  # Lưu dữ liệu các ngày
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime(date_format)
            try:
                if (current_date == start_date):
                    time1 = datetime.strptime(time1, "%H:%M:%S")
                    temp_data = firebase_request(f'/{date_str}')
                    data[date_str] = {time: value for time, value in temp_data.items() if datetime.strptime(time, "%H:%M:%S") >= time1}
                    # print(data[date_str])
                elif(current_date == end_date): 
                    time2 = datetime.strptime(time2, "%H:%M:%S")
                    temp_data = firebase_request(f'/{date_str}')
                    data[date_str] = {time: value for time, value in temp_data.items() if datetime.strptime(time, "%H:%M:%S") <= time2}
                else:
                    data[date_str] = firebase_request(f'/{date_str}')
            except Exception as e:
                print(f"Bỏ qua lỗi ngày {date_str}: {e}")
            
            print(current_date)
            current_date += timedelta(days=1)
        
        return data  # Trả về dictionary chứa dữ liệu từng ngày

    except Exception as e:
        print(f"Lỗi: {e}")
        return None
    
def fetch_device_data(device_id):
    """
    Lấy dữ liệu thiết bị từ Firebase theo device_id.
    Trả về dictionary chứa thông tin thiết bị hoặc None nếu không tìm thấy.
    """
    data = firebase_request(f"/devices_information/{device_id}", method="GET")
    if not data:
        print("Device not found or no data available")
        return None
    return data