import os
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def groq_chat(messages, system_prompt):
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return "⚠️ GROQ_API_KEY missing hai."

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                "temperature": 0.7,
                "max_tokens": 512,
            },
            timeout=15,
        )

        if response.status_code != 200:
            return "❌ Groq API error."

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Error: {str(e)}"
