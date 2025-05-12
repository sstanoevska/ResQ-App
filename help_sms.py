from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()  # Make sure this is called once, at the top of your app

def send_sms(to, message):
    try:
        account_sid = os.getenv("TWILIO_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_NUMBER")

        if not all([account_sid, auth_token, from_number]):
            print("❌ Missing Twilio credentials from environment variables.")
            return "Missing credentials"

        client = Client(account_sid, auth_token)
        sent = client.messages.create(
            body=message,
            from_=from_number,
            to=to
        )
        print("✅ SMS sent successfully. SID:", sent.sid)
        return "SMS sent"

    except Exception as e:
        print("❌ Failed to send SMS:", e)
        return "Failed to send SMS"