# chat_agent.py

import os
from dotenv import load_dotenv
import openai  # OpenAI client
from prompts import get_system_prompt  # Lexi's system prompt helper

# ✅ Load environment variables
load_dotenv()

# ✅ Set OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to generate GPT-4 response with context and role
async def generate_response(user_message: str, context_data: dict, role: str) -> str:
    # Convert context into a readable string
    context_text = f"User Role: {role}\nContext Data: {context_data}"

    # Prepare message list for ChatGPT
    messages = [
        {"role": "system", "content": get_system_prompt(role)},
        {"role": "user", "content": f"{user_message}\n\n{context_text}"}
    ]

    try:
        # Call GPT-4 API with the constructed message
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3,
            max_tokens=300
        )
        return response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"⚠️ Lexi error: {str(e)}"
