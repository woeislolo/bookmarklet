from django.core.mail import send_mail
from django.utils import timezone

from celery import shared_task
from celery.utils.log import get_task_logger

from account.models import *
from images.models import *


logger = get_task_logger(__name__)


@shared_task
def task_send_email(user_pk, subject):
    logger.info("Running task...")
    try:
        user = User.objects.get(pk=user_pk)
        email = user.email
        name = user.first_name
        if subject == "Profile's update":
            message = f"""Кто-то изменил информацию Вашего профиля.\n
            Если это были не вы, рекомендуется зайти в свой аккаунт и изменить пароль.\n
            Если это были вы, проигнорируйте это письмо."""
        else:
            message = 'Регистрация прошла успешно.'

        result = send_mail(
            subject=f"{subject} of {name}",
            message=message,
            from_email="support@example.com",
            recipient_list=[email],
            fail_silently=False,
        )
        if result == 0:
            logger.error(f"Email failed to send")
        else:
            logger.info(f"Email sent successfully")
    except:
        logger.error("Could not fetch the result")
        # raise SystemExit(1)


@shared_task
def task_send_birthday_email():
    logger.info("Running task...")
    try:
        today = timezone.now().date()
        birthday_profile_ids = Profile.objects \
            .filter(date_of_birth__day=today.day, date_of_birth__month=today.month) \
            .values_list('user_id', flat=True)
        birthday_emails = User.objects.filter(id__in=birthday_profile_ids) \
            .values_list('username', 'email')
        for name, email in birthday_emails:
            result = send_mail(
                subject=f"Birthday wishes for {name}",
                message='Happy birthday!',
                from_email="support@example.com",
                recipient_list=[email],
                fail_silently=False,
            )
            if result == 0:
                logger.error(f"Email failed to send for email {email}")
            else:
                logger.info(f"Email sent successfully for email {email}")
    except:
        logger.error("Could not fetch the result")
        # raise SystemExit(1)
