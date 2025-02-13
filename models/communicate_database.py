import requests
import json
# Thông tin Firebase
FIREBASE_URL = 'https://indoor-air-quality-monit-8d27a-default-rtdb.firebaseio.com/'  # Thay bằng URL Realtime Database của bạn
DATABASE_SECRET = 'xn3T4KhAApilHKlOQh1i6AqV4jayFX4RUDSOZm07'  # Thay bằng Database Secret của bạn

# FIREBASE_URL = 'https://test-7afff-default-rtdb.firebaseio.com/'  # Thay bằng URL Realtime Database của bạn
# DATABASE_SECRET = 'lsl32v2J5ZlvaF8YG7TKj548EoC8A7Zc9bPUAjix'  # Thay bằng Database Secret của bạn
# Hàm gửi request đến Firebase
def firebase_request(path, method='GET', data=None):
    url = f'{FIREBASE_URL}{path}.json?auth={DATABASE_SECRET}'
    headers = {'Content-Type': 'application/json'}
    if method == 'GET':
        response = requests.get(url)
    elif method == 'POST':
        response = requests.post(url, data=json.dumps(data), headers=headers)
    elif method == 'PUT':
        response = requests.put(url, data=json.dumps(data), headers=headers)
    elif method == 'DELETE':
        response = requests.delete(url)
    else:
        return None
    return response.json()