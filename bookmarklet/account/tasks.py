from django.core.mail import send_mail

from celery import shared_task
from celery.utils.log import get_task_logger

from .models import User


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
