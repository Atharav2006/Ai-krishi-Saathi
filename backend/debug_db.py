import os
from dotenv import load_dotenv

# Try to find .env file
load_dotenv()

from app.core.config import settings
print(f"DATABASE_URL_FROM_CONFIG: {settings.DATABASE_URL}")
