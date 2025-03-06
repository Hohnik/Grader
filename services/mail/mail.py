import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail_to(receiver_email, subject, message):
    sender_email = "haw@mail.edu"

    mail = MIMEMultipart()
    mail["From"] = sender_email
    mail["To"] = receiver_email
    mail["Subject"] = subject
    mail.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP("localhost", 1025) as server:
            # TODO: Activate if using real server
            # server.starttls()
            # server.login(username, password)
            server.sendmail(sender_email, receiver_email, mail.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

