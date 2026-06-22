from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from core.models import EmailLog


def send_html_email(subject, text_message, html_message, recipient):

    email_log = EmailLog.objects.create(
        email=recipient,
        subject=subject,
        message=text_message,
        html_message=html_message,
        status='pending'
    )

    try:
        msg = EmailMultiAlternatives(
            subject,
            text_message,
            settings.EMAIL_HOST_USER,
            [recipient]
        )

        msg.attach_alternative(html_message, "text/html")
        msg.send()

        email_log.status = 'sent'
        email_log.save()

    except Exception as e:
        email_log.status = 'failed'
        email_log.error_message = str(e)
        email_log.retry_count += 1
        email_log.save()

    return email_log


def retry_failed_emails():

    failed_emails = EmailLog.objects.filter(
        status='failed',
        retry_count__lt=3
    )

    for email in failed_emails:

        try:
            msg = EmailMultiAlternatives(
                email.subject,
                email.message,
                settings.EMAIL_HOST_USER,
                [email.email]
            )

            # if HTML exists, send it too
            if email.html_message:
                msg.attach_alternative(email.html_message, "text/html")

            msg.send()

            email.status = 'sent'
            email.error_message = None
            email.save()

        except Exception as e:
            email.retry_count += 1
            email.error_message = str(e)
            email.save()

            