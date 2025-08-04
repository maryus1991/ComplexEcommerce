from config import settings
from config.celery import shared_task
from django.core.mail import send_mail
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from sitesetting.models import  SiteSetting
from django.template.loader import render_to_string

@shared_task(queue='email')
def send_email_task(recipient_list, link):
    try:
        context = {
            'site': SiteSetting.objects.first(),
            'link': link,
        }
        html_message = render_to_string(f'utils/emails/send_mail_verify.html', context)
        # smtp_server = settings.EMAIL_HOST
        smtp_server = '185.97.116.199'
        smtp_port = 587
        from_addr = settings.EMAIL_HOST_USER
        to_addr = recipient_list
        password = settings.EMAIL_HOST_PASSWORD
        msg = MIMEText(html_message, 'html')
        msg['Subject'] = 'ایمیل خود را تایید کنید'
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Date'] = datetime.today().strftime('%m/%d/%Y %I:%M:%S %p')
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()

        return f"Email sent to {recipient_list} at {datetime.now()}"

    except Exception as e:
        return f"Email sending failed: {str(e)}"
