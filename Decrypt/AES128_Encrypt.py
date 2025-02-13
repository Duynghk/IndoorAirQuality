from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import numpy as np

# # # Function to perform AES encryption
# def aes_encrypt(data, key):
#     cipher = AES.new(key, AES.MODE_ECB)
#     return cipher.encrypt(pad(data, 16))

# # # Function to XOR two byte arrays
# def xor_arrays(arr1, arr2):
#     return np.bitwise_xor(arr1, arr2).astype(np.uint8)

# Encrypt payload
def xor_arrays(arr1, arr2):
    return bytearray([x ^ y for x, y in zip(arr1, arr2)])

# Hàm mã hóa AES (Sử dụng pycryptodome)
def aes_encrypt(block, key):
    cipher = AES.new(key, AES.MODE_ECB)  # Sử dụng chế độ ECB (cho đơn giản trong ví dụ này)
    return bytearray(cipher.encrypt(bytes(block)))  # Trả về kết quả mã hóa dưới dạng bytearray

# Hàm mã hóa payload
def encrypt_payload(payload, payload_len, key, dev_addr, direction, frame_counter):
    number_of_blocks = payload_len // 16
    incomplete_block_size = payload_len % 16

    if incomplete_block_size != 0:
        number_of_blocks += 1

    for i in range(number_of_blocks):
        # Tạo block 16 byte
        block_a = bytearray(16)  # Khởi tạo bytearray 16 byte
        block_a[0] = 0x01
        block_a[1] = 0x00
        block_a[2] = 0x00
        block_a[3] = 0x00
        block_a[4] = 0x00
        block_a[5] = direction
        block_a[6:10] = dev_addr[::-1]  # Đảo ngược dev_addr (little-endian)
        block_a[10] = frame_counter & 0x00FF
        block_a[11] = (frame_counter >> 8) & 0x00FF
        block_a[12] = 0x00  # Byte trên cùng của frame counter
        block_a[13] = 0x00
        block_a[14] = 0x00
        block_a[15] = i + 1  # Đánh dấu số block (1-based index)

        # Mã hóa block
        encrypted_block = aes_encrypt(block_a, key)

        # XOR với payload
        if i != (number_of_blocks - 1):
            payload[i*16:i*16+16] = xor_arrays(payload[i*16:i*16+16], encrypted_block)
        else:
            if incomplete_block_size == 0:
                incomplete_block_size = 16
            payload[i*16:i*16+incomplete_block_size] = xor_arrays(payload[i*16:i*16+incomplete_block_size], encrypted_block[:incomplete_block_size])

    return payload  # Trả về payload đã được mã hóa

# Function to construct data MIC
def construct_data_mic(payload, payload_len, nwk_skey, dev_addr, direction, frame_counter):
    mic_data = np.zeros(80, dtype=np.uint8)
    block_b = np.zeros(16, dtype=np.uint8)

    block_b[0] = 0x49
    block_b[1] = 0x00
    block_b[2] = 0x00
    block_b[3] = 0x00
    block_b[4] = 0x00
    block_b[5] = direction
    block_b[6:10] = dev_addr[::-1]
    block_b[10] = frame_counter & 0x00FF
    block_b[11] = (frame_counter >> 8) & 0x00FF
    block_b[12] = 0x00  # Frame counter upper bytes
    block_b[13] = 0x00
    block_b[14] = 0x00
    block_b[15] = payload_len

    # Copy Block B into MIC data
    mic_data[:16] = block_b

    # Add payload data
    mic_data[16:16+payload_len] = payload[:payload_len]

    # Calculate the MIC
    return calculate_mic(mic_data, 16 + payload_len, nwk_skey)

# Function to calculate MIC
def calculate_mic(payload, payload_len, key):
    k1 = np.zeros(16, dtype=np.uint8)
    k2 = np.zeros(16, dtype=np.uint8)
    old_data = np.zeros(16, dtype=np.uint8)
    new_data = np.zeros(16, dtype=np.uint8)

    number_of_blocks = payload_len // 16
    incomplete_block_size = payload_len % 16

    if incomplete_block_size != 0:
        number_of_blocks += 1

    generate_keys(key, k1, k2)

    for j in range(number_of_blocks - 1):
        new_data[:] = payload[j*16:(j+1)*16]
        new_data = xor_arrays(new_data, old_data)
        new_data = aes_encrypt(new_data, key)
        old_data[:] = new_data

    if incomplete_block_size == 0:
        new_data[:] = payload[(number_of_blocks - 1)*16:]
        new_data = xor_arrays(new_data, k1)
        new_data = xor_arrays(new_data, old_data)
        new_data = aes_encrypt(new_data, key)
    else:
        new_data[:] = np.zeros(16, dtype=np.uint8)
        new_data[:incomplete_block_size] = payload[(number_of_blocks - 1)*16:(number_of_blocks - 1)*16+incomplete_block_size]
        new_data[incomplete_block_size] = 0x80
        new_data = xor_arrays(new_data, k2)
        new_data = xor_arrays(new_data, old_data)
        new_data = aes_encrypt(new_data, key)

    return new_data[:4]

# Function to generate keys K1 and K2
def generate_keys(key, k1, k2):
    aes_encrypt(np.zeros(16, dtype=np.uint8), key)
    k1[:] = np.array(aes_encrypt(np.zeros(16, dtype=np.uint8), key), dtype=np.uint8)
    shift_left(k1)

    msb_key = 1 if k1[0] & 0x80 else 0
    if msb_key:
        k1[15] ^= 0x87

    k2[:] = k1
    shift_left(k2)

    msb_key = 1 if k2[0] & 0x80 else 0
    if msb_key:
        k2[15] ^= 0x87

# Function to shift bits to the left
def shift_left(data):
    overflow = 0
    for i in range(15):
        if (data[i + 1] & 0x80) == 0x80:
            overflow = 1
        else:
            overflow = 0
        data[i] = (data[i] << 1) + overflow

# Example usage
if __name__ == "__main__":
    payload = np.random.randint(0, 256, 32, dtype=np.uint8)
    key = np.random.randint(0, 256, 16, dtype=np.uint8)
    dev_addr = np.random.randint(0, 256, 4, dtype=np.uint8)
    frame_counter = 1
    direction = 0x00  # uplink

    encrypt_payload(payload, len(payload), key, dev_addr, direction, frame_counter)
    print(f"Encrypted Payload: {payload}")
