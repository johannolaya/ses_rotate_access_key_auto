import smtplib  
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

HOST = "email-smtp.us-east-1.amazonaws.com"
PORT = 587
SENDERNAME = 'Test Team'

def ses_send_email(user_smtp, password_smtp, recipient, sender):

    SUBJECT = "[TEST] - SES Rotation Key"

    BODY_TEXT = ("This email was sent to test the new access-key.")  

    BODY_HTML = """<html>
    <head></head>
    <body>
    <p>This email was sent to test the new access-key.</p>
    </body>
    </html>
                """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    msg['From'] = email.utils.formataddr((SENDERNAME, sender))
    msg['To'] = recipient

    part1 = MIMEText(BODY_TEXT, 'plain')
    part2 = MIMEText(BODY_HTML, 'html')

    msg.attach(part1)
    msg.attach(part2)

    try:  
        server = smtplib.SMTP(HOST, PORT)
        server.ehlo()
        server.starttls()
        #stmplib docs recommend calling ehlo() before & after starttls()
        server.ehlo()
        server.login(user_smtp, password_smtp)
        server.sendmail(sender, recipient, msg.as_string())
        server.close()
    except Exception as e:
        return (False, e)
    else:
        return (True, "Email sent!")