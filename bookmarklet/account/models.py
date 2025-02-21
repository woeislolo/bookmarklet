from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True, verbose_name='Фото')
    
    def __str__(self):
        return f'Профиль {self.user.username}'
    
    class Meta:
        verbose_name = 'Профили пользователей'
        verbose_name_plural = 'Профили пользователей'


class Contact(models.Model):
    user_from = models.ForeignKey(to='auth.User',
                                  related_name='rel_from_set',
                                  on_delete=models.CASCADE) # подписывающийся
    user_to = models.ForeignKey(to='auth.User',
                                related_name='rel_to_set',
                                on_delete=models.CASCADE) # на кого подписываются
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'
    
    class Meta:
        indexes = [models.Index(fields=['-created']),]
        ordering = ['-created']

    
user_model = get_user_model()
user_model.add_to_class('following',
                        models.ManyToManyField('self',
                                               through=Contact,
                                               related_name='followers',
                                               symmetrical=False))
