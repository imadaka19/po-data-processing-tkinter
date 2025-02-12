from cryptography.fernet import Fernet
import tkinter as tk

# Baca kunci
with open("secret.key", "rb") as key_file:
    key = key_file.read()

cipher = Fernet(key)

# Baca kode terenkripsi
with open("script.enc", "rb") as file:
    encrypted_code = file.read()

# Dekripsi
decrypted_code = cipher.decrypt(encrypted_code).decode()

# Eksekusi kode
exec(decrypted_code)
