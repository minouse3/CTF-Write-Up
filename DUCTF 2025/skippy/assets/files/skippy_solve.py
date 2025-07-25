from Crypto.Cipher import AES

# Step 1: Raw key and IV before sandwich()
key_bytes = [
    -0x1a, -0x2a, -0x2e, -0x20, -0x20, -0x0e, -0x42, -0x18,
    -0x30, -0x36, -0x42, -0x3c, -0x16, -0x1a, -0x30, -0x42
]

iv_bytes = [
    -0x2a, -0x3e, -0x24, -0x32, -0x3e, -0x1c, -0x22, -0x22,
    -0x22, -0x22, -0x22, -0x22, -0x22, -0x22, -0x22, -0x22
]

def decode_param(arr):
    return bytes([(b & 0xff) >> 1 for b in arr])

key = decode_param(key_bytes)
iv = decode_param(iv_bytes)

# Step 2: Paste your ciphertext here (hex format, no spaces)
ciphertext_hex = """
ae27241b7ffd2c8b3265f22ad1b063f0915b6b95dcc0eec14de2c563f7715594007d2bc75e5d614e5e51190f4ad1fd21c5c4b1ab89a4a725c5b8ed3cb37630727b2d2ab722dc9333264725c6b5ddb00dd3c3da6313f1e2f4df5180d5f3831843
"""
ciphertext_hex = ciphertext_hex.strip().replace("\n", "").replace(" ", "")
ciphertext = bytes.fromhex(ciphertext_hex)

# Step 3: Decrypt
cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted = cipher.decrypt(ciphertext)

# Step 4: stone() is a no-op after decryption, just strip nulls and print
try:
    plaintext = decrypted.rstrip(b"\x00").decode()
except UnicodeDecodeError:
    plaintext = decrypted

print("[+] Flag (raw):", plaintext)
