from config import settings
from config.celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from sitesetting.models import SiteSetting
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@shared_task(queue='email', bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, recipient_email, link):
    try:
        # آماده سازی context
        context = {
            'site': SiteSetting.objects.first(),
            'link': link,
        }

        # رندر HTML و متن fallback
        html_content = render_to_string('utils/emails/send_mail_verify.html', context)
        text_content = f"لطفاً ایمیل خود را تایید کنید: {link}"

        # ساخت پیام ایمیل
        msg = EmailMultiAlternatives(
            subject='ایمیل خود را تایید کنید',
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[recipient_email],
        )
        msg.attach_alternative(html_content, "text/html")

        # ارسال ایمیل
        msg.send(fail_silently=False)

        print(f"Email sent to {recipient_email} at {datetime.now()}")
        return f"Email sent to {recipient_email} at {datetime.now()}"

    except Exception as e:
        logger.error(f"Email sending failed to {recipient_email}: {str(e)}")
 
        raise self.retry(exc=e)

