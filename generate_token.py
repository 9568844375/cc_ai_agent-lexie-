import jwt

SECRET_KEY = "my_super_secret_key_123"

# Payload for admin role
payload = {"role": "admin"}

# Generate token
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

print("✅ Valid token:")
print(token)
