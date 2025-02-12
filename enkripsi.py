from cryptography.fernet import Fernet

# Baca kunci
with open("secret.key", "rb") as key_file:
    key = key_file.read()

cipher = Fernet(key)

# Baca kode asli
with open("po-data-processing.py", "rb") as file:
    original_code = file.read()

# Enkripsi kode
encrypted_code = cipher.encrypt(original_code)

# Simpan hasil enkripsi
with open("script.enc", "wb") as file:
    file.write(encrypted_code)

print("Kode berhasil dienkripsi!")
