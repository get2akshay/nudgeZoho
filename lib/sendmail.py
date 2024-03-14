
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(dic):
    # dic = {'subject': subject, 'body': body, 'sender_email': sender_email, 'recipient_email': recipient_email, 'password': password}
    try:
        # Create a MIMEText object for the email body
        msg = MIMEMultipart()
        msg['From'] = dic.get('sender_email')
        msg['To'] = dic.get('recipient_email')
        msg['Subject'] = dic.get('subject')
        msg.attach(MIMEText(dic.get('body'), 'plain'))

          # Connect to Gmail's SMTP server using SSL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(dic.get('sender_email'), dic.get('password'))
            server.sendmail(dic.get('sender_email'), dic.get('recipient_email'), msg.as_string())
            print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")
