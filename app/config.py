import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv(
    "APP_NAME",
    "Restaurant WhatsApp AI Order Agent"
)

RESTAURANT_NAME = os.getenv(
    "RESTAURANT_NAME",
    "Burger O'Clock"
)

PORT = int(
    os.getenv("PORT", "8000")
)

WHATSAPP_VERIFY_TOKEN = os.getenv(
    "WHATSAPP_VERIFY_TOKEN",
    "burger_oclock_verify_123"
)

WHATSAPP_ACCESS_TOKEN = os.getenv(
    "WHATSAPP_ACCESS_TOKEN",
    ""
)

WHATSAPP_PHONE_NUMBER_ID = os.getenv(
    "WHATSAPP_PHONE_NUMBER_ID",
    ""
)
