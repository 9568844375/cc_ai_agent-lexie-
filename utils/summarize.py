from openai import OpenAI
import os
from dotenv import load_dotenv


client = OpenAI(api_key="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")



client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # ✅ Use env variable safely
async def summarize_data(data_list: list, topic: str):
    if not data_list:
        return f"No {topic} found."

    prompt = f"Summarize the following {topic}:\n\n" + "\n".join(data_list)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an admin assistant that summarizes structured data clearly."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Summarization failed: {str(e)}"
