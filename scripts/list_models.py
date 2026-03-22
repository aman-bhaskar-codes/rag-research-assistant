import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY is not set.")
    exit(1)

genai.configure(api_key=api_key)

print("🔍 Listing supported Embedding Models:")
try:
    for m in genai.list_models():
        if 'embedContent' in m.supported_generation_methods:
            print(f"   🔹 {m.name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")
