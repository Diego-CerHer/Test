import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("MicrosoftAppId", "")
APP_PASSWORD = os.getenv("MicrosoftAppPassword", "")
PORT = int(os.getenv("PORT", 3978))
