import smtplib
from email.message import EmailMessage

# Email configuration

def send_email(subject, body, to_email, EMAIL_ADDRESS, EMAIL_PASSWORD):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(body)

    # Gmail SMTP server
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

