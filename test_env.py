import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
print("🔍 Looking for .env at:", env_path)

loaded = load_dotenv(dotenv_path=env_path)
print("📦 .env loaded:", loaded)

key = os.getenv("OPENAI_API_KEY")
print("🔑 API Key:", key)
