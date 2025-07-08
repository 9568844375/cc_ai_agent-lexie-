# chat_agent.py

from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
from prompts import get_system_prompt
from typing import List, Dict  # <-- ✅ Add here

# ✅ Load .env
load_dotenv()

# ✅ Initialize async client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ Async function to generate GPT-4 response with context and role
async def generate_response(user_message: str, context_data: dict, role: str) -> str:
    context_text = f"User Role: {role}\nContext Data: {context_data}"

    # ✅ Typed message list to avoid red underline
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": get_system_prompt(role)},
        {"role": "user", "content": f"{user_message}\n\n{context_text}"}
    ]

    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Lexi error: {str(e)}"
