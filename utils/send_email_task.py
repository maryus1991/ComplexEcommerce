from config import settings
from config.celery import shared_task
from django.core.mail import send_mail
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

@shared_task(queue='email')
def send_email_task(subject, message, recipient_list):

    smtp_server = '185.97.116.199'
    smtp_port = 587
    from_addr = 'admin@amvajsarmad.com'
    to_addr = recipient_list
    password = 'VeryStrongPassword123J#JqE[wC%baJJ#JqE[wC%baJpostalpasswordamvajsarmadcom'

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = datetime.today().strftime('%m/%d/%Y %I:%M:%S %p')

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()
    print("Email sent!")

# send_email_task('سلامممممممممممممممم', 'سلاممممممممممممممممسلاممممممممممممممممسلاممممممممممممممممسلاممممممممممممممممسلاممممممممممممممممسلاممممممممممممممممسلاممممممممممممممممسلاممممممممممممممممسلامممممممممممممممم', 'test-swwgymmk1@srv1.mail-tester.com')