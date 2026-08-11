import os

from google import genai
from app.config import settings

client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)

def generate_answer(prompt:str):

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text