from cryptography.fernet import Fernet

# Generate a key
key = Fernet.generate_key()
print(f"Generated key: {key}")

# Create a Fernet object
f = Fernet(key)
print("Fernet object created successfully.")
cipher_suite = Fernet(key)
token = cipher_suite.encrypt(b"THis is a secret message.")
print(token)

decrypted = cipher_suite.decrypt(token)
print("Decrypted token=", decrypted)
print(decrypted.decode(utf-8))

from cryptography.fernet import Fernet
