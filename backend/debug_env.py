import os
from dotenv import load_dotenv

load_dotenv()
print(f"DATABASE_URL present: {bool(os.getenv('DATABASE_URL'))}")
print(f"GROQ_API_KEY present: {bool(os.getenv('GROQ_API_KEY'))}")
print(f"GROQ_API_KEY value start: {os.getenv('GROQ_API_KEY')[:10] if os.getenv('GROQ_API_KEY') else 'None'}")
