import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")

def send_otp_email(to_email: str, otp: str):
    if not MAIL_USERNAME or not APP_PASSWORD:
        print("WARNING: Email credentials missing in .env. OTP email skipped.")
        return
        
    msg = EmailMessage()
    msg.set_content(f"Hello,\n\nYour OTP for the OBE Tracking System signup is: {otp}\n\nIt is valid for 10 minutes.\n\nRegards,\nOBE System")
    msg["Subject"] = "Your Signup OTP"
    msg["From"] = MAIL_USERNAME
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(MAIL_USERNAME, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"OTP email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_credentials_email(to_email: str, role: str, raw_password: str):
    if not MAIL_USERNAME or not APP_PASSWORD:
        print("WARNING: Email credentials missing in .env. Credentials email skipped.")
        return
        
    msg = EmailMessage()
    msg.set_content(
        f"Hello,\n\n"
        f"An account has been created for you in the OBE Tracking System.\n"
        f"Role: {role}\n"
        f"Username / Email: {to_email}\n"
        f"Password: {raw_password}\n\n"
        f"Please log in and change your password as soon as possible.\n\n"
        f"Regards,\n"
        f"OBE System"
    )
    msg["Subject"] = "Your OBE System Credentials"
    msg["From"] = MAIL_USERNAME
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(MAIL_USERNAME, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Credentials email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send credentials email to {to_email}: {e}")
