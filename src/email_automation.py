import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Sender Email Credentials
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "steja2251@gmail.com"
APP_PASSWORD = "jtwn ygws xwwh skej"  # Use App Password instead of real password

# List of student emails (Add all student emails here)
students_emails = [
    "enpotheles@gmail.com",
   
]

# Email Content
subject = "Lecture Notes PDF"
body = "Dear Students,\n\nPlease find attached the lecture notes in PDF format.\n\nBest Regards,\nYour Instructor"

# Path to the PDF file
pdf_filename = "lecture_notes.pdf"

# Function to send emails
def send_email(to_emails):
    try:
        # Set up the MIME
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = ", ".join(to_emails)  # Join all emails in a single string
        msg["Subject"] = subject

        # Attach the body
        msg.attach(MIMEText(body, "plain"))

        # Attach the PDF
        with open(pdf_filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={pdf_filename}")
            msg.attach(part)

        # Establish a secure session with the server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, APP_PASSWORD)  # Login to the email account

        # Send email
        server.sendmail(SENDER_EMAIL, to_emails, msg.as_string())
        server.quit()

        print("✅ Email sent successfully to all students!")

    except Exception as e:
        print(f"❌ Error: {e}")

# Send the email to all students in the list
send_email(students_emails)
